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


import collections.abc
import copy
import datetime
import gzip
import logging
from pathlib import Path
from uuid import uuid4
from datetime import datetime

import zmq
from deepdiff import Delta

from replication.objects import Node, ReplicationObject

from .constants import ADDED, COMMITED, FETCHED, HEAD, RP_COMMON, UP, STATE_INITIAL
from .exception import NetworkFrameError, NonAuthorizedOperationError
from .protocol import DataTranslationProtocol
from .objects import Commit, Node
try:
    import _pickle as pickle
except ImportError:
    import pickle

class GraphObjectStore(collections.abc.MutableMapping):
    """ A basic structure to store object as a graph 
    """
    def __init__(self, *args, **kwargs):
        self.store = dict()
        self.update(dict(*args, **kwargs))  # use the free update to set keys

    def __getitem__(self, key):
        return self.store[key]

    def __setitem__(self, key, value):
        self.store[key] = value

    def __delitem__(self, key):
        del self.store[key]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def __repr__(self):
        str = "\n"
        for key, item in self.store.items():
            str += repr(item)
        return str

    def get_parents(self, target: str):
        """ Retrieve node's parents

           :param node: target node
           :type node: Node
        """
        parents = []
        for node in self.values():
            if node.dependencies and target in node.dependencies:
                parents.append(node)

        return parents

    def rbfs_from(self, node: Node):
        """ Run a reversed Breadth Fist Search from the given nodes

            :param node: 
        """
        visited = []
        queue = node if isinstance(node, list) else [node]

        while queue:
            current = queue.pop(0)

            if current not in visited:
                visited.append(current)
                current_ref = self.store.get(current)
                if current_ref and current_ref.dependencies:
                    queue.extend(current_ref.dependencies)

        return reversed(visited)

class Remote():
    def __init__(self,
                 name='origin',
                 address='127.0.0.1',
                 port=5555,
                 server_password=None,
                 admin_password=None,
                 realtime=False):
        self.name = name
        self.address = address
        self.port = port
        self.realtime = realtime
        self.server_password = server_password
        self.admin_password = admin_password

        self.online_users = {}
        self.connection_status = STATE_INITIAL
        self.uuid = uuid4()
        self._context = zmq.Context()
        self.poller = zmq.Poller()

        self.command = self._context.socket(zmq.DEALER)
        self.command.setsockopt(zmq.IDENTITY, self.uuid.bytes)
        self.command.connect(f"tcp://{address}:{port}")
        self.command.setsockopt(zmq.TCP_KEEPALIVE, 1)
        self.command.setsockopt(zmq.TCP_KEEPALIVE_IDLE, 300)
        self.command.setsockopt(zmq.TCP_KEEPALIVE_INTVL, 300)
        self.command.linger = 0

        self.data = self._context.socket(zmq.DEALER)
        self.data.setsockopt(zmq.IDENTITY, self.uuid.bytes)
        self.data.setsockopt(zmq.TCP_KEEPALIVE, 1)
        self.data.setsockopt(zmq.TCP_KEEPALIVE_IDLE, 300)
        self.data.setsockopt(zmq.TCP_KEEPALIVE_INTVL, 300)
        self.data.connect(f"tcp://{address}:{port+1}")
        self.data.linger = 0
        self.data.setsockopt(zmq.RATE, 1000000)
        self.data.setsockopt(zmq.RCVBUF, 2000000)
        self.poller.register(self.command, zmq.POLLIN)
        self.poller.register(self.data, zmq.POLLIN)

    def is_admin(self):
        return self.admin_password is not None

    def is_private(self):
        return self.server_password is not None

class Repository():
    """
    Structure responsible for replication graph manipulation
    """

    def __init__(self,
                 rdp: DataTranslationProtocol = None,
                 username :str = None,
                 bare = False,
                 *args,
                 **kwargs):
        self.username = username
        self.object_store = GraphObjectStore()
        self.staging = GraphObjectStore()
        self.rdp = rdp
        self.remotes = {}
        self.remote = None
        self._bare = bare

    def dumps(self, filepath: str):
        """Dumps the repository data to a .db file

            :param filepath: target filepath
            :type filepath: str
        """
        nodes = []
        for node in self.graph.values():
            nodes.append(node.as_raw_chunks())

        db = dict()
        db['nodes'] = nodes

        if self.remote:
            db['users'] = copy.copy(self.remote.online_users)

        stime = datetime.now().strftime('%Y_%m_%d_%H-%M-%S')

        filepath = Path(filepath)
        filepath = filepath.with_name(
            f"{filepath.stem}_{stime}{filepath.suffix}")

        with gzip.open(filepath, "wb") as f:
            logging.info(f"Writing session snapshot to {filepath}")
            pickle.dump(db, f, protocol=4)

    def loads(self, filepath: str):
        """Load a repository snapshot

           :param filepath: snapshot filepath
           :type filepath: str
        """
        f = gzip.open(filepath, "rb")
        db = pickle.load(f)

        nodes = db.get("nodes")

        logging.info(f"Loading {len(nodes)} node")
        self.object_store.clear()
        for node_data in nodes:
                instance = Node.from_raw_chunks(node_data)
                self.do_commit(instance)
                instance.state = FETCHED

        logging.info(f"Repository loaded from {filepath}")

    def get_orphans_nodes(self):
        return list(set(self.object_store.keys()).difference(self.index_sorted))

    def get_node_by_datablock(self, datablock, default=None):
        for v in self.object_store.values():
            if not v.instance:
                continue
            if datablock == v.instance:
                return v
        return default

    def do_commit(self, update: ReplicationObject, cache_delta = False):
        node_id = getattr(update, 'uuid', getattr(update, 'node_id', None))
        delta_based = isinstance(update, Commit)
        if node_id:
            existing_node = self.object_store.get(node_id)

            if existing_node:
                if delta_based:
                    existing_node.patch(update)
                else:
                    existing_node.data = update.data
                    existing_node.dependencies = update.dependencies
            elif not delta_based:
                self.object_store[node_id] = update
            else:
                logging.error(f"Skipping update : {update}")
            logging.debug(f"Committed {node_id}")


    def assert_modification_rights(self, node_id):
        if self.graph.get(node_id).owner not in [self.username, RP_COMMON]:
            raise NonAuthorizedOperationError(f"Not authorized to modify the node {node_id}")

    def is_node_readonly(self, node_id: str) -> bool:
        """ Check local user modification rights on a node

        :param node_id: node identifier
        :type node_id: str
        :return: bool
        """
        node = self.graph.get(node_id)
        return node and (node.owner in [self.username, RP_COMMON])

    def push(self, socket, replication_object, identity=None, force=False):
        # Server to specific Client case
        if identity:
            socket.send(identity, zmq.SNDMORE)

        socket.send_multipart(replication_object.as_raw_chunks())

    def fetch(self, socket):
        """
        Here we reeceive data from the wire:
            - read data from the socket
            - reconstruct an instance
        """
        frame = socket.recv_multipart(0)

        # Load node metadata

        if self._bare:
            identity = frame.pop(0)
        else:
            identity = 'server'

        return (identity, ReplicationObject.from_raw_chunks(frame))

    @property
    def heads(self):
        return [n.uuid for n in self.object_store.values() if self.rdp.implementations[n.data['type_id']].is_root]

    @property
    def index_sorted(self):
        """ Return the repository graph node index sorted by dependencies 
            order

            :return: list
        """
        return self.object_store.rbfs_from(self.heads)

    @property
    def graph(self):
        return self.object_store
