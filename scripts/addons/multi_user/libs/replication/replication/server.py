# ##### BEGIN GPL LICENSE BLOCK #####
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####

import argparse
import cmd
import logging
import os
import sys
from pathlib import Path
import traceback
# REFACTOR: remove this in favor of a better env setup
replication_lib = Path(os.path.dirname(os.path.realpath(__file__)))

try:
    import deepdiff
    import zmq
except ImportError:
    sys.path.insert(0, str(replication_lib.parent.parent))

sys.path.insert(0, str(replication_lib.parent))

import copy
import logging

try:
    import _pickle as pickle
except ImportError:
    import pickle

import os
import queue
import subprocess
import sys
import threading
import time
import uuid
from pathlib import Path

import zmq

from replication import __version__
from replication.constants import (CLIENT_PING_FREQUENCY, CONNECTION_TIMEOUT,
                                   RP_COMMON, STATE_ACTIVE, STATE_AUTH,
                                   STATE_INITIAL, STATE_LOBBY, STATE_SRV_SYNC,
                                   STATE_SYNCING, STATE_WAITING, UP)
from replication.objects import (Node, ReplicationObject, Auth,
                                 Delete, Disconnect, Kick,Right,
                                 ServerSnapshot, Snapshot,UpdateClientsState,
                                 UpdateUserMetadata, RequestServerInfo)

from replication.exception import DataError, NetworkFrameError, StateError
from replication.repository import Repository
from replication.utils import current_milli_time

class ServerNetService(threading.Thread):
    def __init__(self):

        # Threading
        threading.Thread.__init__(self)
        self.name = "command"
        self._exit_event = threading.Event()

        # Networking
        self._repository = Repository(bare=True)
        self._context = zmq.Context.instance()
        self._command = None
        self._data = None
        self._state = 0
        self.clients = {}
        self._ttl = None

    def listen(
            self,
            port=5560,
            server_password=None,
            admin_password='admin',
            attached=False,
            timeout=CONNECTION_TIMEOUT):
        self._server_password = server_password
        self._admin_password = admin_password
        self._port = port
        self._attached = attached

        # Update request
        self._command = self._context.socket(zmq.ROUTER)
        self._command.setsockopt(zmq.IDENTITY, b'SERVER_COMMAND')
        self._command.bind(f"tcp://*:{port}")
        self._command.linger = 0
        self._command.setsockopt(zmq.TCP_KEEPALIVE, 1)
        self._command.setsockopt(zmq.TCP_KEEPALIVE_IDLE, 300)
        self._command.setsockopt(zmq.TCP_KEEPALIVE_INTVL, 300)

        # TTL communication
        self._ttl_pipe = self._context.socket(zmq.DEALER)
        self._ttl_pipe.bind("inproc://server_ttl")
        self._ttl_pipe.linger = 0

        self._ttl = ServerTTL(
            port=port+2,
            timeout=timeout
        )

        # Data handling
        self._data = ServerData(
            port=port+1,
            repository=self._repository,
            clients_state=self.clients
        )

        self._client_snapshot_size = 0
        self._client_snapshot_progress = 0

        self.start()

    def disconnect_client(self, client, reason):
        leaving_client = self.clients.get(client)
        if leaving_client:
            client_id = leaving_client.get('id')
            locked_nodes = [n.uuid for n in self._repository.graph.values() if n.owner == client_id]

            if locked_nodes:
                reset_right = Right(
                                owner='server',
                                data={
                                    'uuid': locked_nodes,
                                    'owner': RP_COMMON
                                }
                            )

                logging.debug(f"Changing node {locked_nodes} rights to COMMON")
                
                for cli in self.clients.keys():
                    if cli != client and not self._command._closed:
                        self._command.send(cli, zmq.SNDMORE)
                        self._repository.push(self._command, reset_right)
                        reset_right.execute(self._repository.object_store)

            del self.clients[client]
            logging.info(f"{client_id} disconnected from the server [{reason}]")


    def _update_clients_states(self):
        user_dict = {}
        for user, user_data in self.clients.items():
            user_dict[user_data['id']] = user_data

        clients_states = UpdateClientsState(
            owner='server',
            data=user_dict
        )

        # Push it to every clients
        for client_uid in self.clients:
            self._command.send(client_uid, zmq.SNDMORE)
            self._repository.push(self._command, clients_states)

    def _login_client(self, auth_type, uid, id, server_password, admin_password, version):
        """ Register a client on the server

        return:
        FAILED
        LOBBY
        RUNNING
        """
        logging.debug(f"Processing logging request from {id}")
        for cli in self.clients.values():
            if id == cli['id']:
                logging.debug("client logged in")
                return 'FAILED: client already logged in'

        if auth_type == 'ADMIN' and admin_password != self._admin_password:
            return 'FAILED: wrong admin password'

        if str(server_password) != self._server_password:
            return 'FAILED: wrong server password'

        if version != __version__:
            return f'FAILED: wrong client version ({version} != {__version__})'

        logging.info(f"{id} logged in.")

        self.clients[uid] = {
            'id': id,
            'admin': auth_type == 'ADMIN',
            'latency': 999,
            'status': STATE_LOBBY,
            'metadata': {},
        }
        if self._state in [STATE_WAITING, STATE_SRV_SYNC]:
            return 'LOBBY'
        else:
            return 'RUNNING'

    def kick(self, user):
        """ kick the given user

        :arg user: username of the kicked client
        :type user: str
        """
        for k, v in self.clients.items():
            if v['id'] == user:
                disconnect = Disconnect(
                    owner='server',
                    data={
                        'reason': 'kicked by admin',
                    }
                )
                self._command.send(k, zmq.SNDMORE)
                self._repository.push(self._command, disconnect)

                self._ttl_pipe.send_multipart([b'STOP_WATCHING', k])
                self.disconnect_client(k, 'kicked')

                logging.warning(f"{user} kicked from the session.")
                return

        logging.error(f"Can't kick {user}, user not found.")

    def send_client_snapshot_init(self, client):
        catalog = [str(k) for k in self._repository.object_store.keys()]
        snapshot_state = Snapshot(
            owner='server',
            data={
                'STATE': 'INIT',
                'CATALOG': catalog})
        logging.info(f"{self.clients[client]['id']} - Snapshot : Pushing nodes catalog")
        self._command.send(client, zmq.SNDMORE)
        self._repository.push(self._command, snapshot_state)

    def handle_client_snapshot(self, command):
        """ Handle client snapshot commands """

        snapshot_state = command.data.get('STATE')
        snapshot_client = self.clients.get(command.sender)

        if snapshot_client:
            if snapshot_state == 'REQUEST_INIT':
                self.send_client_snapshot_init(command.sender)
            elif snapshot_state == 'GET':
                node = self._repository.graph.get(command.data['ID'])

                if node:
                    logging.debug(f"{snapshot_client['id']} - Snapshot : pushing node {node.uuid}")
                else:
                    logging.debug(f"{snapshot_client['id']} - Snapshot : node {command.data['ID']} no longer exist, skipping it.")

                node_data = node.as_raw_chunks() if node else b'removed'
                snapshot_cmd = Snapshot(
                        owner='server',
                        data={
                            'STATE': 'SET',
                            'DATA': node_data
                        }
                )
                self._command.send(command.sender, zmq.SNDMORE)
                self._repository.push(self._command, snapshot_cmd)
            elif snapshot_state == 'DONE':
                # Set client ready
                logging.info(f"{snapshot_client['id']} - Snapshot : done.")
                self.clients[command.sender]['status'] = STATE_ACTIVE
                self._update_clients_states()
        else:
            logging.error(f"Snapshot cancelled {command.sender} (client disconnected)")

    def handle_server_repository_init(self, command):
        cli_snapshot_state = command.data.get('STATE')
        cli_snapshot_lenght = command.data.get('SIZE')
        cli_snapshot_dict = command.data.get('NODES')
        cli_snapshot_data = command.data.get('DATA')


        if cli_snapshot_state == 'INIT':
            if self._state == STATE_SRV_SYNC:  # REJECT
                snapshot_status = "REJECTED"
            if self._state == STATE_WAITING:
                snapshot_status = "ACCEPTED"
                self._client_snapshot_size = cli_snapshot_lenght
                self._client_snapshot_dict = cli_snapshot_dict

            snapshot_cmd = ServerSnapshot(
                owner='server',
                data={'STATE': snapshot_status})
            self._command.send(command.sender, zmq.SNDMORE)
            self._repository.push(self._command, snapshot_cmd)
            self._state = STATE_SRV_SYNC

        if cli_snapshot_state == 'SET':
            node = ReplicationObject.from_raw_chunks(cli_snapshot_data)
            node.state = UP

            self._repository.do_commit(node)

            self._client_snapshot_progress += 1
            logging.debug(f"Receiving snapshot {self._client_snapshot_progress}/{self._client_snapshot_size}")
            self._client_snapshot_dict.remove(node.uuid)
            if len(self._client_snapshot_dict) == 0:
                # Launch snapshot for other waiting clients
                snapshot_cmd = ServerSnapshot(
                    owner='server',
                    data={'STATE': 'DONE'})

                self._command.send(command.sender, zmq.SNDMORE)
                self._repository.push(self._command, snapshot_cmd)

                for client in self.clients.keys():
                    if client != command.sender:
                        self.send_client_snapshot_init(client)

                self._state = STATE_ACTIVE

        if cli_snapshot_state == 'END':
            self.clients[command.sender]['status'] = STATE_ACTIVE
            self._update_clients_states()
            logging.info("Done")

    def run(self):
        logging.info(f"Listening on {self._port}.")
        poller = zmq.Poller()

        poller.register(self._command, zmq.POLLIN)
        poller.register(self._ttl_pipe, zmq.POLLIN)

        self._state = STATE_WAITING

        while not self._exit_event.is_set():
            # Non blocking poller
            socks = dict(poller.poll(1))

            # COMMAND HANDLING
            if self._command in socks:
                try:
                    identity, command = self._repository.fetch(self._command)
                    command.sender = identity
                except Exception as e:
                    logging.error(f"Corrupted command frame received, skipping it. Cause:{e}")
                    traceback.print_exc()
                else:
                    # AUHTENTIFICATION
                    if isinstance(command, Auth):
                        auth_type = command.data.get('AUTH_TYPE')
                        auth_origin = command.sender
                        auth_id = command.data.get('AUTH_ID')
                        auth_s_pass = command.data.get('S_PWD', None)
                        auth_a_pass = command.data.get('A_PWD', None)
                        client_version = command.data.get('VERSION')

                        auth_status = self._login_client(auth_type,
                                                        auth_origin,
                                                        auth_id,
                                                        auth_s_pass,
                                                        auth_a_pass,
                                                        client_version)

                        auth_response = Auth(
                            owner="server",
                            data=auth_status)

                        self._update_clients_states()

                        self._command.send(command.sender, zmq.SNDMORE)
                        self._repository.push(self._command, auth_response)

                    # SERVER-> CLIENT SNAPSHOT
                    if isinstance(command, Snapshot):
                        self.handle_client_snapshot(command)

                    # CLIENT-> SERVER SNAPSHOT
                    if isinstance(command, ServerSnapshot):
                        self.handle_server_repository_init(command)

                    # CLIENT METADATA
                    if isinstance(command, UpdateUserMetadata):
                        user = self.clients.get(command.sender)

                        if user:
                            try:
                                user['metadata'].update(command.data)
                            except Exception as e:
                                logging.error(e)
                                traceback.print_exc()
                            else:
                                for client_uid in self.clients:
                                    if client_uid != command.sender:
                                        self._command.send(client_uid, zmq.SNDMORE)
                                        self._repository.push(self._command, command)

                    # KICK
                    if isinstance(command, Kick):
                        self.kick(command.data['user'])

                    if isinstance(command, RequestServerInfo):
                        server_info = RequestServerInfo(
                            owner='server',
                            data={
                                'private': True if self._server_password else False,
                                'version': __version__
                            })
                        self._command.send(command.sender, zmq.SNDMORE)
                        self._command.send_multipart(server_info.as_raw_chunks())

                    # OTHERS
                    if type(command) in [Delete, Right]:
                        try:
                            command.execute(self._repository.object_store)
                        except Exception as e:
                            logging.error(e)
                            traceback.print_exc()
                        else:
                            for client_uid in self.clients:
                                # if client_uid != command.sender:
                                self._command.send(client_uid, zmq.SNDMORE)
                                self._repository.push(self._command, command)

            # TTL HANDLING
            if self._ttl_pipe in socks:
                notification = self._ttl_pipe.recv_multipart()

                if notification[0] == b'STATE':
                    clients_states = pickle.loads(notification[1])

                    # Prepare update
                    for id, state in clients_states.items():
                        cli = self.clients.get(id)
                        if cli:
                            cli.update(state)
                        else:
                            self._ttl_pipe.send_multipart(
                                [b'STOP_WATCHING', id])

                    self._update_clients_states()

                if notification[0] == b'LOST':
                    self.disconnect_client(notification[1], 'connection closed')

        while self._ttl._state != STATE_INITIAL:
            time.sleep(1)

        self._command.close()
        self._data.close()
        self._ttl_pipe.close()

    def stop(self):
        self._ttl.stop()
        self._data.stop()
        self._exit_event.set()
        self._state = 0

class ServerData(threading.Thread):
    def __init__(
        self,
        port=5556,
        repository=None,
        clients_state=None):
        threading.Thread.__init__(self)
        self.name = "data"
        self.daemon = False
        self._exit_event = threading.Event()
        self._repository = repository

        self._context = zmq.Context.instance()
        # Update all clients
        self._data = self._context.socket(zmq.ROUTER)
        self._data.setsockopt(zmq.IDENTITY, b'SERVER_PUSH')
        self._data.bind(f"tcp://*:{port}")
        self._data.linger = 0
        self._data.setsockopt(zmq.RATE, 1000000)
        self._data.setsockopt(zmq.SNDBUF, 2000000)
        self._data.setsockopt(zmq.TCP_KEEPALIVE, 1)
        self._data.setsockopt(zmq.TCP_KEEPALIVE_IDLE, 300)
        self._data.setsockopt(zmq.TCP_KEEPALIVE_INTVL, 300)
        self.clients = clients_state

        self.start()
    
    def run(self):
        poller = zmq.Poller()
        poller.register(self._data, zmq.POLLIN)

        while not self._exit_event.is_set():
            # Non blocking poller
            socks = dict(poller.poll(1))
            if self._data in socks:
                # Regular update  routing (Clients / Server / Clients)

                try:
                    identity, update = self._repository.fetch(self._data)

                    self._repository.do_commit(update)
                except Exception as e:
                    logging.error(f"Corrupted data frame received, skipping it. Cause:{e}")
                    traceback.print_exc()
                else:
                    # Update all ready clients
                    for client_uid, client_data in self.clients.items():
                        if client_uid != identity:
                            self._repository.push(self._data,
                                                        update,
                                                        identity=client_uid)

    def stop(self):
        self._exit_event.set()

class ServerTTL(threading.Thread):
    def __init__(
            self,
            port=5562,
            timeout=CONNECTION_TIMEOUT):
        # Threading

        threading.Thread.__init__(self)
        self.name = "ttl"
        self.daemon = False
        self._id = id
        self._exit_event = threading.Event()

        # Networking
        self._context = zmq.Context.instance()
        self._heartbeat = self._context.socket(zmq.ROUTER)
        self._heartbeat.bind(f"tcp://*:{port}")
        self._heartbeat.linger = 0
        self._pipe = self._context.socket(zmq.DEALER)
        self._pipe.connect("inproc://server_ttl")
        self._pipe.linger = 0

        self._timeout = timeout
        self._state = STATE_INITIAL
        self._clients_state = {}

        self.start()

    def run(self):
        self._state = STATE_ACTIVE
        poller = zmq.Poller()

        poller.register(self._heartbeat, zmq.POLLIN)
        poller.register(self._pipe, zmq.POLLIN)
        last_update_time = current_milli_time()
        while not self._exit_event.is_set():
            socks = dict(poller.poll(1))
            current_time = current_milli_time()

            if self._heartbeat in socks:
                identity, frame = self._heartbeat.recv_multipart(0)

                if frame == b'INIT':
                    self._clients_state[identity] = {}
                    self._clients_state[identity]['latency'] = 999
                    self._clients_state[identity]['last_received_update'] = current_time
                    self._clients_state[identity]['last_sent_update'] = current_time
                    self._heartbeat.send(identity, zmq.SNDMORE)
                    self._heartbeat.send(b"PING")

                client = self._clients_state.get(identity)

                if client is None:
                    continue

                client['last_received_update'] = current_time

            if self._pipe in socks:
                notification = self._pipe.recv_multipart()

                if notification[0] == b'STOP_WATCHING':
                    self.stop_monitor(notification[1])

            if current_time-last_update_time > 1000:
                last_update_time = current_time
                client_to_remove = []

                # Check clients status
                for client, client_data in self._clients_state.items():
                    client_data['latency'] = abs(
                        (client_data['last_received_update'])-(client_data['last_sent_update']))

                    if client_data['latency'] > self._timeout:
                        client_to_remove.append(client)
                        self._pipe.send_multipart([b'LOST', client])

                for client in client_to_remove:
                    self.stop_monitor(client)

                state_update = {cli:{'latency':val['latency']} for cli, val in self._clients_state.items()}
                self._pipe.send_multipart(
                    [b'STATE', pickle.dumps(state_update, protocol=4)])

            for cli_key, cli_data in self._clients_state.items():
                if (current_time-cli_data['last_received_update']) > CLIENT_PING_FREQUENCY and \
                        current_time-cli_data['last_sent_update'] > CLIENT_PING_FREQUENCY:

                    self._heartbeat.send(cli_key, zmq.SNDMORE)
                    self._heartbeat.send(b"PING")
                    cli_data['last_sent_update'] = current_time

        self._heartbeat.close()
        self._pipe.close()
        self._state = STATE_INITIAL

    def stop_monitor(self, client):
        if client in self._clients_state:
            logging.debug(f"Removing client {client} from watchlist")
            del self._clients_state[client]

    @property
    def state(self):
        return self._state

    @property
    def clients_state(self):
        return copy.copy(self._clients_state)

    def stop(self):
        self._exit_event.set()


class ServerShell(cmd.Cmd):
    intro = 'Welcome the replication server shell.\n   Type help or ? to list commands.\n'
    prompt = '>> '
    file = None

    def __init__(
            self,
            port=5555,
            timeout=CONNECTION_TIMEOUT,
            server_password=None,
            admin_password=None,
            attached=False):

        cmd.Cmd.__init__(self)
        self._net = ServerNetService()

        self._net.listen(
            port=port,
            server_password=server_password,
            admin_password=admin_password,
            attached=attached,
            timeout=timeout)

    def do_users(self, args):
        """ Print online users """
        print(f"{len(self._net.clients)} user online")
        for cli_id, cli_data in self._net.clients.items():
            role = 'admin' if cli_data['admin'] else ''
            print(f"{cli_data['id']}({role}) - {cli_data['latency']} ms")

    def do_kick(self, args):
        """ Kick the target user """
        self._net.kick(args)

    def do_exit(self, args):
        """ Exit the server """
        self._net.stop()
        return -1

    def do_EOF(self, args):
        print('*** EOF')
        return True


def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', default=5560,
                        help="port to listen")
    parser.add_argument('-l', '--log-level', default='INFO',
                        help="set logging level ")
    parser.add_argument('-lf', '--log-file', default='multi_user_server.log',
                        help="set log file output")
    parser.add_argument('-t', '--timeout', default=CONNECTION_TIMEOUT,
                        help="connection timeout in millisecond")
    parser.add_argument('-apwd', '--admin-password', default='admin',
                        help="session admin password")
    parser.add_argument('-spwd', '--server-password', default=None,
                        help="session server password")

    parser.add_argument('--attached',
                        help="server attached to a blender instance",
                        action='store_true')

    args = parser.parse_args()

    formatter = logging.Formatter(
        fmt='%(asctime)s SERVER %(levelname)-8s %(message)s',
        datefmt='%H:%M:%S'
    )

    logging.basicConfig(level=logging._nameToLevel[args.log_level])
    logger = logging.getLogger()
    handler = logging.FileHandler(args.log_file, mode='w')
    logger.addHandler(handler)

    for handler in logger.handlers:
        if isinstance(handler, logging.NullHandler):
            continue

        handler.setFormatter(formatter)

    shell = ServerShell(
        port=int(args.port),
        timeout=int(args.timeout),
        server_password=str(args.server_password),
        admin_password=str(args.admin_password),
        attached=bool(args.attached))
    try:
        shell.cmdloop()
    except KeyboardInterrupt:
        shell.do_exit(None)


if __name__ == '__main__':
    cli()
