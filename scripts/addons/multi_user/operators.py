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


import asyncio
import copy
import gzip
import logging
from multi_user.preferences import ServerPreset
import os
import queue
import random
import shutil
import string
import sys
import time
import traceback
from uuid import uuid4
from datetime import datetime
from operator import itemgetter
from pathlib import Path
from queue import Queue
from time import gmtime, strftime

from bpy.props import FloatProperty
import bmesh

try:
    import _pickle as pickle
except ImportError:
    import pickle

import bpy
import mathutils
from bpy.app.handlers import persistent
from bpy_extras.io_utils import ExportHelper, ImportHelper
from replication import porcelain
from replication.constants import (COMMITED, FETCHED, RP_COMMON, STATE_ACTIVE,
                                   STATE_INITIAL, STATE_SYNCING, UP)
from replication.exception import ContextError, NonAuthorizedOperationError
from replication.interface import session
from replication.objects import Node
from replication.protocol import DataTranslationProtocol
from replication.repository import Repository

from . import bl_types, environment, shared_data, timers, ui, utils
from .handlers import on_scene_update, sanitize_deps_graph
from .presence import SessionStatusWidget, renderer, view3d_find, refresh_sidebar_view, bbox_from_obj
from .timers import registry

background_execution_queue = Queue()
deleyables = []
stop_modal_executor = False


def draw_user(username, metadata, radius=0.01, intensity=10.0):
    view_corners =  metadata.get('view_corners')
    color =  metadata.get('color', (1,1,1,0))
    objects = metadata.get('selected_objects', None)

    user_collection = bpy.data.collections.new(username)

    # User Color
    user_mat = bpy.data.materials.new(username)
    user_mat.use_nodes = True
    nodes = user_mat.node_tree.nodes
    nodes.remove(nodes['Principled BSDF'])
    emission_node = nodes.new('ShaderNodeEmission')
    emission_node.inputs['Color'].default_value = color
    emission_node.inputs['Strength'].default_value = intensity

    output_node = nodes['Material Output']
    user_mat.node_tree.links.new(
        emission_node.outputs['Emission'], output_node.inputs['Surface'])

    # Generate camera mesh
    camera_vertices = view_corners[:4]
    camera_vertices.append(view_corners[6])
    camera_mesh = bpy.data.meshes.new(f"{username}_camera")
    camera_obj = bpy.data.objects.new(f"{username}_camera", camera_mesh)
    frustum_bm = bmesh.new()
    frustum_bm.from_mesh(camera_mesh)

    for p in camera_vertices:
        frustum_bm.verts.new(p)
    frustum_bm.verts.ensure_lookup_table()

    frustum_bm.edges.new((frustum_bm.verts[0], frustum_bm.verts[2]))
    frustum_bm.edges.new((frustum_bm.verts[2], frustum_bm.verts[1]))
    frustum_bm.edges.new((frustum_bm.verts[1], frustum_bm.verts[3]))
    frustum_bm.edges.new((frustum_bm.verts[3], frustum_bm.verts[0]))

    frustum_bm.edges.new((frustum_bm.verts[0], frustum_bm.verts[4]))
    frustum_bm.edges.new((frustum_bm.verts[2], frustum_bm.verts[4]))
    frustum_bm.edges.new((frustum_bm.verts[1], frustum_bm.verts[4]))
    frustum_bm.edges.new((frustum_bm.verts[3], frustum_bm.verts[4]))
    frustum_bm.edges.ensure_lookup_table()

    frustum_bm.to_mesh(camera_mesh)
    frustum_bm.free()  # free and prevent further access

    camera_obj.modifiers.new("wireframe", "SKIN")
    camera_obj.data.skin_vertices[0].data[0].use_root = True
    for v in camera_mesh.skin_vertices[0].data:
        v.radius = [radius, radius]

    camera_mesh.materials.append(user_mat)
    user_collection.objects.link(camera_obj)

    # Generate sight mesh
    sight_mesh = bpy.data.meshes.new(f"{username}_sight")
    sight_obj = bpy.data.objects.new(f"{username}_sight", sight_mesh)
    sight_verts = view_corners[4:6]
    sight_bm = bmesh.new()
    sight_bm.from_mesh(sight_mesh)

    for p in sight_verts:
        sight_bm.verts.new(p)
    sight_bm.verts.ensure_lookup_table()

    sight_bm.edges.new((sight_bm.verts[0], sight_bm.verts[1]))
    sight_bm.edges.ensure_lookup_table()
    sight_bm.to_mesh(sight_mesh)
    sight_bm.free()

    sight_obj.modifiers.new("wireframe", "SKIN")
    sight_obj.data.skin_vertices[0].data[0].use_root = True
    for v in sight_mesh.skin_vertices[0].data:
        v.radius = [radius, radius]

    sight_mesh.materials.append(user_mat)
    user_collection.objects.link(sight_obj)

    # Draw selected objects
    if objects:
        for o in list(objects):
            instance = bl_types.bl_datablock.get_datablock_from_uuid(o, None)
            if instance:
                bbox_mesh = bpy.data.meshes.new(f"{instance.name}_bbox")
                bbox_obj = bpy.data.objects.new(
                    f"{instance.name}_bbox", bbox_mesh)
                bbox_verts, bbox_ind = bbox_from_obj(instance, index=0)
                bbox_bm = bmesh.new()
                bbox_bm.from_mesh(bbox_mesh)

                for p in bbox_verts:
                    bbox_bm.verts.new(p)
                bbox_bm.verts.ensure_lookup_table()

                for e in bbox_ind:
                    bbox_bm.edges.new(
                        (bbox_bm.verts[e[0]], bbox_bm.verts[e[1]]))

                bbox_bm.to_mesh(bbox_mesh)
                bbox_bm.free()
                bpy.data.collections[username].objects.link(bbox_obj)

                bbox_obj.modifiers.new("wireframe", "SKIN")
                bbox_obj.data.skin_vertices[0].data[0].use_root = True
                for v in bbox_mesh.skin_vertices[0].data:
                    v.radius = [radius, radius]

                bbox_mesh.materials.append(user_mat)

    bpy.context.scene.collection.children.link(user_collection)


def session_callback(name):
    """ Session callback wrapper

    This allow to encapsulate session callbacks to background_execution_queue.
    By doing this way callback are executed from the main thread. 
    """
    def func_wrapper(func):
        @session.register(name)
        def add_background_task(**kwargs):
            background_execution_queue.put((func, kwargs))
        return add_background_task
    return func_wrapper


@session_callback('on_connection')
def initialize_session():
    """Session connection init hander 
    """
    runtime_settings = bpy.context.window_manager.session

    if not runtime_settings.is_host:
        logging.info("Intializing the scene")
        # Step 1: Constrect nodes
        logging.info("Instantiating nodes")
        for node in session.repository.index_sorted:
            node_ref = session.repository.graph.get(node)
            if node_ref is None:
                logging.error(f"Can't construct node {node}")
            elif node_ref.state == FETCHED:
                node_ref.instance = session.repository.rdp.resolve(node_ref.data)
                if node_ref.instance is None:
                    node_ref.instance = session.repository.rdp.construct(node_ref.data)
                    node_ref.instance.uuid = node_ref.uuid

        # Step 2: Load nodes
        logging.info("Applying nodes")
        for node in session.repository.heads:
            porcelain.apply(session.repository, node)

    logging.info("Registering timers")
    # Step 4: Register blender timers
    for d in deleyables:
        d.register()

    # Step 5: Clearing history
    utils.flush_history()

    # Step 6: Launch deps graph update handling
    bpy.app.handlers.depsgraph_update_post.append(on_scene_update)


@session_callback('on_exit')
def on_connection_end(reason="none"):
    """Session connection finished handler 
    """
    global deleyables, stop_modal_executor
    settings = utils.get_preferences()

    # Step 1: Unregister blender timers
    for d in deleyables:
        try:
            d.unregister()
        except:
            continue
    deleyables.clear()

    stop_modal_executor = True

    if on_scene_update in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(on_scene_update)

    # Step 3: remove file handled
    logger = logging.getLogger()
    for handler in logger.handlers:
        if isinstance(handler, logging.FileHandler):
            logger.removeHandler(handler)
    if reason != "user":
        bpy.ops.session.notify('INVOKE_DEFAULT', message=f"Disconnected from session. Reason: {reason}. ") #TODO: change op session.notify to add ui + change reason (in replication->interface)

def setup_logging():
    """ Session setup logging (host/connect)
    """
    settings = utils.get_preferences()
    logger = logging.getLogger()
    if len(logger.handlers) == 1:
        formatter = logging.Formatter(
            fmt='%(asctime)s CLIENT %(levelname)-8s %(message)s',
            datefmt='%H:%M:%S'
        )

        start_time = datetime.now().strftime('%Y_%m_%d_%H-%M-%S')
        log_directory = os.path.join(
            settings.cache_directory,
            f"multiuser_{start_time}.log")

        os.makedirs(settings.cache_directory, exist_ok=True)

        handler = logging.FileHandler(log_directory, mode='w')
        logger.addHandler(handler)

        for handler in logger.handlers:
            if isinstance(handler, logging.NullHandler):
                continue

            handler.setFormatter(formatter)

def setup_timer():
    """ Session setup timer (host/connect)
    """
    settings = utils.get_preferences()
    deleyables.append(timers.ClientUpdate())
    deleyables.append(timers.DynamicRightSelectTimer())
    deleyables.append(timers.ApplyTimer(timeout=settings.depsgraph_update_rate))

    session_update = timers.SessionStatusUpdate()
    session_user_sync = timers.SessionUserSync()
    session_background_executor = timers.MainThreadExecutor(execution_queue=background_execution_queue)
    session_listen = timers.SessionListenTimer(timeout=0.001)

    session_listen.register()
    session_update.register()
    session_user_sync.register()
    session_background_executor.register()

    deleyables.append(session_background_executor)
    deleyables.append(session_update)
    deleyables.append(session_user_sync)
    deleyables.append(session_listen)
    deleyables.append(timers.AnnotationUpdates())

def get_active_server_preset(context):
    active_index = context.window_manager.server_index
    server_presets = utils.get_preferences().server_preset

    active_index = active_index if active_index <= len(server_presets)-1 else 0

    return server_presets[active_index]

# OPERATORS
class SessionConnectOperator(bpy.types.Operator):
    bl_idname = "session.connect"
    bl_label = "connect"
    bl_description = "connect to a net server"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        global deleyables

        settings = utils.get_preferences()
        users = bpy.data.window_managers['WinMan'].online_users
        active_server = get_active_server_preset(context)
        admin_pass = active_server.admin_password if active_server.use_admin_password else None
        server_pass = active_server.server_password if active_server.use_server_password else ''

        users.clear()
        deleyables.clear()

        setup_logging()

        bpy_protocol = bl_types.get_data_translation_protocol()

        # Check if supported_datablocks are up to date before starting the
        # the session
        for dcc_type_id in bpy_protocol.implementations.keys():
            if dcc_type_id not in settings.supported_datablocks:
                logging.info(f"{dcc_type_id} not found, \
                             regenerate type settings...")
                settings.generate_supported_types()


        if bpy.app.version >= (2,91,0):
            python_binary_path = sys.executable
        else:
            python_binary_path = bpy.app.binary_path_python

        repo = Repository(
            rdp=bpy_protocol,
            username=settings.username)
        
        # Join a session
        if not active_server.use_admin_password:
            utils.clean_scene()

        try:
            porcelain.remote_add(
                repo,
                'origin',
                active_server.ip,
                active_server.port,
                server_password=server_pass,
                admin_password=admin_pass)
            session.connect(
                repository= repo,
                timeout=settings.connection_timeout,
                server_password=server_pass,
                admin_password=admin_pass
            )
        except Exception as e:
            self.report({'ERROR'}, str(e))
            logging.error(str(e))

        # Background client updates service
        setup_timer()

        return {"FINISHED"}


class SessionHostOperator(bpy.types.Operator):
    bl_idname = "session.host"
    bl_label = "host"
    bl_description = "host server"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        global deleyables

        settings = utils.get_preferences()
        runtime_settings = context.window_manager.session
        users = bpy.data.window_managers['WinMan'].online_users
        admin_pass = settings.host_admin_password if settings.host_use_admin_password else None
        server_pass = settings.host_server_password if settings.host_use_server_password else ''

        users.clear()
        deleyables.clear()

        setup_logging()

        bpy_protocol = bl_types.get_data_translation_protocol()

        # Check if supported_datablocks are up to date before starting the
        # the session
        for dcc_type_id in bpy_protocol.implementations.keys():
            if dcc_type_id not in settings.supported_datablocks:
                logging.info(f"{dcc_type_id} not found, \
                             regenerate type settings...")
                settings.generate_supported_types()


        if bpy.app.version >= (2,91,0):
            python_binary_path = sys.executable
        else:
            python_binary_path = bpy.app.binary_path_python

        repo = Repository(
            rdp=bpy_protocol,
            username=settings.username)
    
        # Host a session
        if settings.init_method == 'EMPTY':
            utils.clean_scene()

        try:
            # Init repository
            for scene in bpy.data.scenes:
                porcelain.add(repo, scene)

            porcelain.remote_add(
                repo,
                'origin',
                '127.0.0.1',
                settings.host_port,
                server_password=server_pass,
                admin_password=admin_pass)
            session.host(
                repository= repo,
                remote='origin',
                timeout=settings.connection_timeout,
                server_password=server_pass,
                admin_password=admin_pass,
                cache_directory=settings.cache_directory,
                server_log_level=logging.getLevelName(
                    logging.getLogger().level),
            )
        except Exception as e:
            self.report({'ERROR'}, repr(e))
            logging.error(f"Error: {e}")
            traceback.print_exc()

        # Background client updates service
        setup_timer()

        return {"FINISHED"}


class SessionInitOperator(bpy.types.Operator):
    bl_idname = "session.init"
    bl_label = "Init session repostitory from"
    bl_description = "Init the current session"
    bl_options = {"REGISTER"}

    init_method: bpy.props.EnumProperty(
        name='init_method',
        description='Init repo',
        items={
            ('EMPTY', 'an empty scene', 'start empty'),
            ('BLEND', 'current scenes', 'use current scenes')},
        default='BLEND')

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.prop(self, 'init_method', text="")

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        if self.init_method == 'EMPTY':
            utils.clean_scene()

        for scene in bpy.data.scenes:
            porcelain.add(session.repository, scene)

        session.init()
        context.window_manager.session.is_host = True

        return {"FINISHED"}


class SessionStopOperator(bpy.types.Operator):
    bl_idname = "session.stop"
    bl_label = "close"
    bl_description = "Exit current session"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        global deleyables, stop_modal_executor

        if session:
            try:
                session.disconnect(reason='user')

            except Exception as e:
                self.report({'ERROR'}, repr(e))
        else:
            self.report({'WARNING'}, "No session to quit.")
            return {"FINISHED"}
        return {"FINISHED"}


class SessionKickOperator(bpy.types.Operator):
    bl_idname = "session.kick"
    bl_label = "Kick"
    bl_description = "Kick the target user"
    bl_options = {"REGISTER"}

    user: bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        global deleyables, stop_modal_executor
        assert(session)

        try:
            porcelain.kick(session.repository, self.user)
        except Exception as e:
            self.report({'ERROR'}, repr(e))

        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        row = self.layout
        row.label(text=f" Do you really want to kick {self.user} ? ")


class SessionPropertyRemoveOperator(bpy.types.Operator):
    bl_idname = "session.remove_prop"
    bl_label = "Delete cache"
    bl_description = "Stop tracking modification on the target datablock." + \
        "The datablock will no longer be updated for others client. "
    bl_options = {"REGISTER"}

    property_path: bpy.props.StringProperty(default="None")

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        try:
            porcelain.rm(session.repository, self.property_path)

            return {"FINISHED"}
        except:  # NonAuthorizedOperationError:
            self.report(
                {'ERROR'},
                "Non authorized operation")
            return {"CANCELLED"}


class SessionPropertyRightOperator(bpy.types.Operator):
    bl_idname = "session.right"
    bl_label = "Change modification rights"
    bl_description = "Modify the owner of the target datablock"
    bl_options = {"REGISTER"}

    key: bpy.props.StringProperty(default="None")
    recursive: bpy.props.BoolProperty(default=True)

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        runtime_settings = context.window_manager.session

        row = layout.row()
        row.label(text="Give the owning rights to:")
        row.prop(runtime_settings, "clients", text="")
        row = layout.row()
        row.label(text="Affect dependencies")
        row.prop(self, "recursive", text="")

    def execute(self, context):
        runtime_settings = context.window_manager.session

        if session:
            if runtime_settings.clients == RP_COMMON:
                porcelain.unlock(session.repository,
                                 self.key,
                                 ignore_warnings=True,
                                 affect_dependencies=self.recursive)
            else:
                porcelain.lock(session.repository,
                             self.key,
                             runtime_settings.clients,
                             ignore_warnings=True,
                             affect_dependencies=self.recursive)

        return {"FINISHED"}


class SessionSnapUserOperator(bpy.types.Operator):
    bl_idname = "session.snapview"
    bl_label = "snap to user"
    bl_description = "Snap 3d view to selected user"
    bl_options = {"REGISTER"}

    _timer = None

    target_client: bpy.props.StringProperty(default="None")

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        wm = context.window_manager
        runtime_settings = context.window_manager.session

        if runtime_settings.time_snap_running:
            runtime_settings.time_snap_running = False
            return {'CANCELLED'}
        else:
            runtime_settings.time_snap_running = True

        self._timer = wm.event_timer_add(0.1, window=context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)

    def modal(self, context, event):
        session_sessings = context.window_manager.session
        is_running = session_sessings.time_snap_running

        if event.type in {'RIGHTMOUSE', 'ESC'} or not is_running:
            self.cancel(context)
            return {'CANCELLED'}

        if event.type == 'TIMER':
            area, region, rv3d = view3d_find()

            if session:
                target_ref = session.online_users.get(self.target_client)

                if target_ref:
                    target_scene = target_ref['metadata']['scene_current']

                    # Handle client on other scenes
                    if target_scene != context.scene.name:
                        blender_scene = bpy.data.scenes.get(target_scene, None)
                        if blender_scene is None:
                            self.report(
                                {'ERROR'}, f"Scene {target_scene} doesn't exist on the local client.")
                            session_sessings.time_snap_running = False
                            return {"CANCELLED"}

                        bpy.context.window.scene = blender_scene

                    # Update client viewmatrix
                    client_vmatrix = target_ref['metadata'].get(
                        'view_matrix', None)

                    if client_vmatrix:
                        rv3d.view_matrix = mathutils.Matrix(client_vmatrix)
                    else:
                        self.report({'ERROR'}, f"Client viewport not ready.")
                        session_sessings.time_snap_running = False
                        return {"CANCELLED"}
            else:
                return {"CANCELLED"}

        return {'PASS_THROUGH'}


class SessionSnapTimeOperator(bpy.types.Operator):
    bl_idname = "session.snaptime"
    bl_label = "snap to user time"
    bl_description = "Snap time to selected user time's"
    bl_options = {"REGISTER"}

    _timer = None

    target_client: bpy.props.StringProperty(default="None")

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        runtime_settings = context.window_manager.session

        if runtime_settings.user_snap_running:
            runtime_settings.user_snap_running = False
            return {'CANCELLED'}
        else:
            runtime_settings.user_snap_running = True

        wm = context.window_manager
        self._timer = wm.event_timer_add(0.05, window=context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)

    def modal(self, context, event):
        is_running = context.window_manager.session.user_snap_running
        if not is_running:
            self.cancel(context)
            return {'CANCELLED'}

        if event.type == 'TIMER':
            if session:
                target_ref = session.online_users.get(self.target_client)

                if target_ref:
                    context.scene.frame_current = target_ref['metadata']['frame_current']
            else:
                return {"CANCELLED"}

        return {'PASS_THROUGH'}


class SessionApply(bpy.types.Operator):
    bl_idname = "session.apply"
    bl_label = "Revert"
    bl_description = "Revert the selected datablock from his cached" + \
        " version."
    bl_options = {"REGISTER"}

    target: bpy.props.StringProperty()
    reset_dependencies: bpy.props.BoolProperty(default=False)

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        logging.debug(f"Running apply on {self.target}")
        try:
            node_ref = session.repository.graph.get(self.target)
            porcelain.apply(session.repository,
                            self.target,
                            force=True)
            impl = session.repository.rdp.get_implementation(node_ref.instance)
            # NOTE: find another way to handle child and parent automatic reloading
            if impl.bl_reload_parent:
                for parent in session.repository.graph.get_parents(self.target):
                    logging.debug(f"Refresh parent {parent}")

                    porcelain.apply(session.repository,
                                    parent.uuid,
                                    force=True)
            if hasattr(impl, 'bl_reload_child') and impl.bl_reload_child:
                for dep in node_ref.dependencies:
                    porcelain.apply(session.repository,
                                    dep,
                                    force=True)
        except Exception as e:
            self.report({'ERROR'}, repr(e))
            traceback.print_exc()
            return {"CANCELLED"}    

        return {"FINISHED"}


class SessionCommit(bpy.types.Operator):
    bl_idname = "session.commit"
    bl_label = "Force server update"
    bl_description = "Commit and push the target datablock to server"
    bl_options = {"REGISTER"}

    target: bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        try:
            porcelain.commit(session.repository, self.target)
            porcelain.push(session.repository, 'origin', self.target, force=True)
            return {"FINISHED"}
        except Exception as e:
            self.report({'ERROR'}, repr(e))
            return {"CANCELLED"}


class SessionClearCache(bpy.types.Operator):
    "Clear local session cache"
    bl_idname = "session.clear_cache"
    bl_label = "Modal Executor Operator"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        cache_dir = utils.get_preferences().cache_directory
        try:
            for root, dirs, files in os.walk(cache_dir):
                for name in files:
                    Path(root, name).unlink()

        except Exception as e:
            self.report({'ERROR'}, repr(e))

        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        row = self.layout
        row.label(text=f" Do you really want to remove local cache ? ")


class SessionPurgeOperator(bpy.types.Operator):
    "Remove node with lost references"
    bl_idname = "session.purge"
    bl_label = "Purge session data"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        try:
            porcelain.purge_orphan_nodes(session.repository)
        except Exception as e:
            self.report({'ERROR'}, repr(e))

        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        row = self.layout
        row.label(text=f" Do you really want to remove local cache ? ")


class SessionNotifyOperator(bpy.types.Operator):
    """Dialog only operator"""
    bl_idname = "session.notify"
    bl_label = "Multi-user"
    bl_description = "multiuser notification"

    message: bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.row().label(text=self.message)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class SessionSaveBackupOperator(bpy.types.Operator, ExportHelper):
    bl_idname = "session.save"
    bl_label = "Save session data"
    bl_description = "Save a snapshot of the collaborative session"

    # ExportHelper mixin class uses this
    filename_ext = ".db"

    filter_glob: bpy.props.StringProperty(
        default="*.db",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    enable_autosave: bpy.props.BoolProperty(
        name="Auto-save",
        description="Enable session auto-save",
        default=True,
    )
    save_interval: bpy.props.FloatProperty(
        name="Auto save interval",
        description="auto-save interval (seconds)",
        default=10,
    )

    def execute(self, context):
        if self.enable_autosave:
            recorder = timers.SessionBackupTimer(
                filepath=self.filepath,
                timeout=self.save_interval)
            recorder.register()
            deleyables.append(recorder)
        else:
            session.repository.dumps(self.filepath)

        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        return session.state == STATE_ACTIVE


class SessionStopAutoSaveOperator(bpy.types.Operator):
    bl_idname = "session.cancel_autosave"
    bl_label = "Cancel auto-save"
    bl_description = "Cancel session auto-save"

    @classmethod
    def poll(cls, context):
        return (session.state == STATE_ACTIVE and 'SessionBackupTimer' in registry)

    def execute(self, context):
        autosave_timer = registry.get('SessionBackupTimer')
        autosave_timer.unregister()

        return {'FINISHED'}

class SessionLoadSaveOperator(bpy.types.Operator, ImportHelper):
    bl_idname = "session.load"
    bl_label = "Load session save"
    bl_description = "Load a Multi-user session save"
    bl_options = {'REGISTER', 'UNDO'}

    # ExportHelper mixin class uses this
    filename_ext = ".db"

    filter_glob: bpy.props.StringProperty(
        default="*.db",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    draw_users: bpy.props.BoolProperty(
        name="Load users",
        description="Draw users in the scene",
        default=False,
    )
    user_skin_radius: bpy.props.FloatProperty(
        name="Wireframe radius",
        description="Wireframe radius",
        default=0.005,
    )
    user_color_intensity: bpy.props.FloatProperty(
        name="Shading intensity",
        description="Shading intensity",
        default=10.0,
    )

    def draw(self, context):
        pass

    def execute(self, context):
        from replication.repository import Repository
    
        # init the factory with supported types
        bpy_protocol = bl_types.get_data_translation_protocol()
        repo = Repository(bpy_protocol)
        repo.loads(self.filepath)
        utils.clean_scene()

        nodes = [repo.graph.get(n) for n in repo.index_sorted]

        # Step 1: Construct nodes
        for node in nodes:
            node.instance = bpy_protocol.resolve(node.data)
            if node.instance is None:
                node.instance = bpy_protocol.construct(node.data)
                node.instance.uuid = node.uuid

        # Step 2: Load nodes
        for node in nodes:
            porcelain.apply(repo, node.uuid)
        
        if self.draw_users:
            f = gzip.open(self.filepath, "rb")
            db = pickle.load(f)

            users = db.get("users")

            for username, user_data in users.items():
                metadata = user_data['metadata']

                if metadata:
                    draw_user(username, metadata, radius=self.user_skin_radius, intensity=self.user_color_intensity)

        return {'FINISHED'}
    
    @classmethod
    def poll(cls, context):
        return True

class SESSION_PT_ImportUser(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Users"
    bl_parent_id = "FILE_PT_operator"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator

        return operator.bl_idname == "SESSION_OT_load"

    def draw_header(self, context):
        sfile = context.space_data
        operator = sfile.active_operator

        self.layout.prop(operator, "draw_users", text="")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        sfile = context.space_data
        operator = sfile.active_operator

        layout.enabled = operator.draw_users

        layout.prop(operator, "user_skin_radius")
        layout.prop(operator, "user_color_intensity")

class SessionPresetServerAdd(bpy.types.Operator):
    """Add a server to the server list preset"""
    bl_idname = "session.preset_server_add"
    bl_label = "Add server preset"
    bl_description = "add a server to the server preset list"
    bl_options = {"REGISTER"}

    server_name: bpy.props.StringProperty(default="")
    ip: bpy.props.StringProperty(default="127.0.0.1")
    port: bpy.props.IntProperty(default=5555)
    use_server_password: bpy.props.BoolProperty(default=False)
    server_password: bpy.props.StringProperty(default="", subtype = "PASSWORD")
    use_admin_password: bpy.props.BoolProperty(default=False)
    admin_password: bpy.props.StringProperty(default="", subtype = "PASSWORD")

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, event):
        self.server_name = ""
        self.ip = "127.0.0.1"
        self.port = 5555
        self.use_server_password = False
        self.server_password = ""
        self.use_admin_password = False
        self.admin_password = ""

        assert(context)
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout

        row = layout.row() 
        row.prop(self, "server_name", text="Server name")
        row = layout.row(align = True)
        row.prop(self, "ip", text="IP+port")
        row.prop(self, "port", text="")
        row = layout.row()
        col = row.column()
        col.prop(self, "use_server_password", text="Server password:")
        col = row.column()
        col.enabled = True if self.use_server_password else False
        col.prop(self, "server_password", text="")
        row = layout.row()
        col = row.column()
        col.prop(self, "use_admin_password", text="Admin password:")
        col = row.column()
        col.enabled = True if self.use_admin_password else False
        col.prop(self, "admin_password", text="")
        
    def execute(self, context):
        assert(context)

        settings = utils.get_preferences()
        existing_preset = settings.get_server_preset(self.server_name)

        new_server = existing_preset if existing_preset else settings.server_preset.add()
        new_server.name = str(uuid4())
        new_server.server_name = self.server_name
        new_server.ip = self.ip
        new_server.port = self.port
        new_server.use_server_password = self.use_server_password
        new_server.server_password = self.server_password
        new_server.use_admin_password = self.use_admin_password
        new_server.admin_password = self.admin_password

        refresh_sidebar_view()

        if new_server == existing_preset :
            self.report({'INFO'}, "Server '" + self.server_name + "' edited")
        else :
            self.report({'INFO'}, "New '" + self.server_name + "' server preset")

        return {'FINISHED'}


class SessionPresetServerEdit(bpy.types.Operator): # TODO : use preset, not settings
    """Edit a server to the server list preset"""
    bl_idname = "session.preset_server_edit"
    bl_label = "Edit server preset"
    bl_description = "Edit a server from the server preset list"
    bl_options = {"REGISTER"}

    target_server_name: bpy.props.StringProperty(default="None")

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, event):
        assert(context)
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        settings = utils.get_preferences()
        settings_active_server = settings.server_preset.get(self.target_server_name)
        
        row = layout.row()
        row.prop(settings_active_server, "server_name", text="Server name")
        row = layout.row(align = True)
        row.prop(settings_active_server, "ip", text="IP+port")
        row.prop(settings_active_server, "port", text="")
        row = layout.row()
        col = row.column()
        col.prop(settings_active_server, "use_server_password", text="Server password:")
        col = row.column()
        col.enabled = True if settings_active_server.use_server_password else False
        col.prop(settings_active_server, "server_password", text="")
        row = layout.row()
        col = row.column()
        col.prop(settings_active_server, "use_admin_password", text="Admin password:")
        col = row.column()
        col.enabled = True if settings_active_server.use_admin_password else False
        col.prop(settings_active_server, "admin_password", text="")
        
    def execute(self, context):
        assert(context)

        settings = utils.get_preferences()
        settings_active_server = settings.server_preset.get(self.target_server_name)

        refresh_sidebar_view()

        self.report({'INFO'}, "Server '" + settings_active_server.server_name + "' edited")

        return {'FINISHED'}

class SessionPresetServerRemove(bpy.types.Operator):
    """Remove a server to the server list preset"""
    bl_idname = "session.preset_server_remove"
    bl_label = "remove server preset"
    bl_description = "remove the current server from the server preset list"
    bl_options = {"REGISTER"}
    
    target_server_name: bpy.props.StringProperty(default="None")

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        assert(context)

        settings = utils.get_preferences()
        settings.server_preset.remove(settings.server_preset.find(self.target_server_name))

        return {'FINISHED'}
        
class RefreshServerStatus(bpy.types.Operator):
    bl_idname = "session.get_info"
    bl_label = "Get session info"
    bl_description = "Get session info"

    target_server: bpy.props.StringProperty(default="127.0.0.1:5555")

    @classmethod
    def poll(cls, context):
        return (session.state != STATE_ACTIVE)

    def execute(self, context):
        settings = utils.get_preferences()

        for server in settings.server_preset:
            infos = porcelain.request_session_info(f"{server.ip}:{server.port}", timeout=settings.ping_timeout)
            server.is_online = True if infos else False
            if server.is_online:
                server.is_private = infos.get("private")

        return {'FINISHED'}

class GetDoc(bpy.types.Operator):
    """Get the documentation of the addon"""
    bl_idname = "doc.get"
    bl_label = "Multi-user's doc"
    bl_description = "Go to the doc of the addon"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        assert(context)
        bpy.ops.wm.url_open(url="https://slumber.gitlab.io/multi-user/index.html")

        return {'FINISHED'}

class FirstLaunch(bpy.types.Operator):
    """First time lauching the addon"""
    bl_idname = "firstlaunch.verify"
    bl_label = "First launch"
    bl_description = "First time lauching the addon"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        assert(context)
        settings = utils.get_preferences()
        settings.is_first_launch = False
        settings.server_preset.clear()
        prefs = bpy.context.preferences.addons[__package__].preferences
        prefs.generate_default_presets()
        return {'FINISHED'}

def menu_func_import(self, context):
    self.layout.operator(SessionLoadSaveOperator.bl_idname, text='Multi-user session snapshot (.db)')

def menu_func_export(self, context):
    self.layout.operator(SessionSaveBackupOperator.bl_idname, text='Multi-user session snapshot (.db)')


classes = (
    SessionConnectOperator,
    SessionHostOperator,
    SessionStopOperator,
    SessionPropertyRemoveOperator,
    SessionSnapUserOperator,
    SessionSnapTimeOperator,
    SessionPropertyRightOperator,
    SessionApply,
    SessionCommit,
    SessionKickOperator,
    SessionInitOperator,
    SessionClearCache,
    SessionNotifyOperator, 
    SessionSaveBackupOperator,
    SessionLoadSaveOperator,
    SESSION_PT_ImportUser,
    SessionStopAutoSaveOperator,
    SessionPurgeOperator,
    SessionPresetServerAdd,
    SessionPresetServerEdit,
    SessionPresetServerRemove,
    RefreshServerStatus,
    GetDoc,
    FirstLaunch,
)


def register():
    from bpy.utils import register_class

    for cls in classes: 
        register_class(cls)


def unregister():
    if session and session.state == STATE_ACTIVE:
        session.disconnect()

    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
