bl_info = {
    "name": "Originie",
    "author": "Kursad Karatas / Mechanical Mustache Labs",
    "version": (1, 3, 2),
    "blender": (2, 91, 0),
    "location": "View3D > Originie",
    "description":
    "Lets user to edit/manage the pivot/origin point. Use ';' to invoke, 'insert' for quit pivot edit",
    "warning": "",
    "wiki_url": "",
    "tracker_url":
    "https://blenderartists.org/t/originie-teleport-the-pivot-with-magic-a-feature-packed-pivot-master-add-on",
    "category": "Object"
}

import bpy
import bmesh

import bgl
import blf
import gpu

from gpu_extras.batch import batch_for_shader

from bpy.types import Menu, Operator

from bpy.props import EnumProperty, IntProperty, FloatProperty, BoolProperty, StringProperty, FloatVectorProperty

from bpy_extras import view3d_utils
import mathutils
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
from mathutils.geometry import intersect_line_plane, intersect_point_tri, intersect_ray_tri
from bpy_extras.view3d_utils import (region_2d_to_vector_3d,
                                     region_2d_to_origin_3d)

import copy
import random
import time
import numpy as np
import math

APIVER = str(bpy.app.version[0]) + str(bpy.app.version[1])
FAKE_LOCATION = (('CURSOR', 'CURSOR', ''), ('OBJECT', 'OBJECT', ''),
                 ('SELECTED', 'SELECTED', ''), ('WORLD', 'WORLD', ''))

ORIGINIE_PRECISION = 1

addon_keymaps = []


def defineSceneProps():
    bpy.types.Scene.originie_doneeditpivot = BoolProperty(
        name="IsPivotEditing", default=False)

    bpy.types.Scene.originie_isgizmovisible = BoolProperty(
        name="IsGizmoVisible", default=False)

    bpy.types.Scene.originie_gizmostates = StringProperty(name="GizmoStates",
                                                          default="")


def setCursorLoc(loc=None):

    C = bpy.context

    cursor_prev = C.scene.cursor.location.copy()

    if loc:
        C.scene.cursor.location = loc

    return cursor_prev


def setOrigin2Cursor():

    bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')


def setSelectActiveObject(context, obj):

    if context.mode == 'OBJECT':

        bpy.ops.object.select_all(action='DESELECT')
        context.view_layer.objects.active = obj
        obj.select_set(True)


def deselectAll():
    bpy.ops.object.select_all(action='DESELECT')


def isEditMode():
    """Check to see we are in edit  mode
    """

    try:
        if bpy.context.object.mode == "EDIT":
            return True

        else:
            return False

    except:
        print("No active mesh object")


def isObjectMode():

    if bpy.context.object.mode == "OBJECT":
        return True

    else:
        return False


def getObjectbyName(name=None):
    try:
        ob = [o for o in bpy.data.objects if o.name == name][0]
        return ob

    except:
        return None


def getParentLoc(obj=None):

    if obj:
        if obj.parent:
            return obj.parent.location.copy()

        else:
            return obj.location.copy()


def selectObject(obj):

    obj.select_set(True)


def setActiveObject(context, obj):
    bpy.context.view_layer.objects.active = obj


def setCursor2Selected():

    bpy.ops.view3d.snap_cursor_to_selected()


def objectMode():

    if isEditMode():
        bpy.ops.object.mode_set(mode="OBJECT")

    else:
        return True

    return


def getActiveComponent():

    obj = bpy.context.edit_object
    obj.update_from_editmode()

    me = obj.data

    bm = bmesh.from_edit_mesh(me)

    mode = bm.select_mode

    co = Vector((0.0, 0.0, 0.0))
    if bm.select_mode == {'VERT'}:
        co = bm.select_history.active.co.copy()

    elif bm.select_mode == {'FACE'} or bm.select_mode == {'EDGE'}:

        verts = bm.select_history.active.verts
        for v in verts:
            co += v.co

        co = co / len(verts)

    return co


def isPivotEditMode():

    if hasattr(bpy.context.scene.tool_settings, "use_transform_data_origin"):
        return (bpy.context.scene.tool_settings.use_transform_data_origin)

    else:
        return False


def storeShowGizmo():

    st = ""
    st = str(bpy.context.space_data.show_gizmo_tool)
    st += "," + str(bpy.context.space_data.show_gizmo)
    st += "," + str(bpy.context.space_data.show_gizmo_context)
    st += "," + str(bpy.context.space_data.show_gizmo_object_rotate)
    st += "," + str(bpy.context.space_data.show_gizmo_object_translate)
    st += "," + str(bpy.context.space_data.show_gizmo_object_scale)

    return st


def restoreShowGizmo(st):

    st = st.split(",")

    bpy.context.space_data.show_gizmo_tool = eval(st[0])
    bpy.context.space_data.show_gizmo = eval(st[1])
    bpy.context.space_data.show_gizmo_context = eval(st[2])
    bpy.context.space_data.show_gizmo_object_rotate = eval(st[3])
    bpy.context.space_data.show_gizmo_object_translate = eval(st[4])
    bpy.context.space_data.show_gizmo_object_scale = eval(st[5])


def setManipulator(flag):

    bpy.context.space_data.show_gizmo_tool = flag
    bpy.context.space_data.show_gizmo = flag
    bpy.context.space_data.show_gizmo_context = flag
    bpy.context.space_data.show_gizmo_object_rotate = flag
    bpy.context.space_data.show_gizmo_object_translate = flag


def enableManipulator(context):

    if int(APIVER) >= 280:

        bpy.context.space_data.show_gizmo_tool = True

        bpy.context.space_data.show_gizmo = True
        bpy.context.space_data.show_gizmo_context = True

        context.space_data.show_gizmo_object_rotate = True
        context.space_data.show_gizmo_object_translate = True

        bpy.ops.wm.tool_set_by_id(name="builtin.transform",
                                  space_type='VIEW_3D')


def toggleManipulator(context):

    rot = context.space_data.show_gizmo_object_rotate
    trn = context.space_data.show_gizmo_object_translate
    scl = context.space_data.show_gizmo_object_scale

    gizmo = context.space_data.show_gizmo_tool

    if gizmo:
        bpy.context.space_data.show_gizmo_tool = False

    else:
        bpy.context.space_data.show_gizmo_tool = True


def isFakePivot():

    context = bpy.context
    C = context
    obj = C.object

    name = obj.name
    name = ".PIVOT_" + name

    isfakepivot = [o for o in context.scene.objects if name in o.name]

    return len(isfakepivot) > 0


def setFakePivot(self):

    context = bpy.context
    C = context
    obj = C.object

    name = obj.name
    name = ".PIVOT_" + name

    isfakepivot = [o for o in context.scene.objects if name in o.name]

    cur = bpy.context.object

    if len(isfakepivot) < 1:

        curmode = bpy.context.object.mode
        if isEditMode():
            objectMode()

        bpy.ops.object.empty_add(type='ARROWS',
                                 align='WORLD',
                                 location=(0, 0, 0))
        bpy.context.object.empty_display_size = 2

        bpy.ops.view3d.snap_selected_to_cursor()
        bpy.context.object.name = name

        fakepivot = getObjectbyName(name)

        deselectAll()

        setActiveObject(context, cur)
        selectObject(cur)

        bpy.ops.object.mode_set(mode=curmode)

        bpy.ops.object.constraint_add(type='PIVOT')
        bpy.context.object.constraints['Pivot'].name = "FakePivot"
        bpy.context.object.constraints["FakePivot"].target = bpy.data.objects[
            name]
        bpy.context.object.constraints[
            "FakePivot"].rotation_range = 'ALWAYS_ACTIVE'

    else:
        bpy.ops.object.visual_transform_apply()

        cnst = bpy.context.object.constraints["FakePivot"]
        C.object.constraints.remove(cnst)

        fakepivot = getObjectbyName(name)
        bpy.data.objects.remove(fakepivot, do_unlink=True)


def parseGuideLine():

    try:
        gp_data = bpy.context.scene.grease_pencil
        gp_data = bpy.data.grease_pencils["Annotations"]

        for layer in gp_data.layers:
            for frame in layer.frames:
                for stroke in frame.strokes:

                    p = [v.co for v in stroke.points]

        v1 = p[0]
        v2 = p[1]
        v = v2 - v1

    except:
        v = Vector((0, 0, 0))
        v1 = Vector((0, 0, 0))
        v2 = Vector((0, 0, 0))

    return [v, v1, v2]


def isClose(a, b, rel_tol=0.01, abs_tol=0.0):
    return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


def toggleCursor(state=False):
    bpy.context.space_data.overlay.show_cursor = state


def multiplyNumpyWorldMatrix(ob, co):
    """Get vert coords in world space
    Provided by @Richcolburn
    """
    m = np.array(ob.matrix_world, dtype=np.float32)
    mat = m[:3, :3].T
    loc = m[:3, 3]

    return co @ mat + loc


def buildTrnScl_WorldMat(obj):

    loc, rot, scl = obj.matrix_world.decompose()
    mat_trans = Matrix.Translation(loc)

    mat_scale = Matrix.Scale(scl[0], 4, (1, 0, 0))
    mat_scale @= Matrix.Scale(scl[1], 4, (0, 1, 0))
    mat_scale @= Matrix.Scale(scl[2], 4, (0, 0, 1))

    mat_final = mat_trans @ mat_scale

    return mat_final


def findBBoxNumPy(context):

    obj = context.active_object

    m = obj.matrix_world

    count = len(obj.data.vertices)
    shape = (count, 3)

    verts = np.empty(count * 3, dtype=np.float32)

    obj.data.vertices.foreach_get("co", verts)

    verts.shape = shape

    padding = 0.001

    x_min = verts[:, 0].min()

    y_min = verts[:, 1].min()

    z_min = verts[:, 2].min()

    x_max = verts[:, 0].max()

    y_max = verts[:, 1].max()

    z_max = verts[:, 2].max()

    x_avg = verts[:, 0].mean()
    y_avg = verts[:, 1].mean()
    z_avg = verts[:, 2].mean()

    middle = m @ Vector(
        ((x_min + x_max) / 2, (y_min + y_max) / 2, (z_min + z_max) / 2))

    min = m @ Vector((x_min, y_min, z_min))
    max = m @ Vector((x_max, y_max, z_max))
    avg = m @ Vector((x_avg, y_avg, z_avg))

    return min, max, middle, avg


def findBBoxWorldNumPy(context):

    obj = context.active_object

    count = len(obj.data.vertices)
    shape = (count, 3)

    verts = np.empty(count * 3, dtype=np.float32)

    obj.data.vertices.foreach_get("co", verts)

    verts.shape = shape

    co = verts

    del verts

    verts = multiplyNumpyWorldMatrix(obj, co)

    padding = 0.001

    x_min = verts[:, 0].min()

    y_min = verts[:, 1].min()

    z_min = verts[:, 2].min()

    x_max = verts[:, 0].max()

    y_max = verts[:, 1].max()

    z_max = verts[:, 2].max()

    x_avg = verts[:, 0].mean()
    y_avg = verts[:, 1].mean()
    z_avg = verts[:, 2].mean()

    middle = Vector(
        ((x_min + x_max) / 2, (y_min + y_max) / 2, (z_min + z_max) / 2))

    min = Vector((x_min, y_min, z_min))
    max = Vector((x_max, y_max, z_max))
    avg = Vector((x_avg, y_avg, z_avg))

    return min, max, middle, avg


def getBBox():

    C = bpy.context

    ob = C.object

    cursor = C.scene.cursor.location.copy()

    bbox = []

    m = ob.matrix_world

    for b in ob.bound_box:
        bbox.append(m @ Vector((b[0], b[1], b[2])))

    return bbox


def makeBboxMesh():

    C = bpy.context

    name = ".BBOX"

    def vert(x, y, z):
        """ Make a vertex """
        return (x, y, z)

    verts = getBBox()

    faces = [(0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (1, 5, 6, 2),
             (2, 6, 7, 3), (4, 0, 3, 7)]

    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)

    obj = bpy.data.objects.new(name, mesh)

    C.scene.collection.objects.link(obj)

    C.view_layer.objects.active = obj

    obj.select_set(True)

    return obj


class VIEW_OT_Inspector(bpy.types.Operator):
    """Inspects"""
    bl_idname = "view3d.inspector"
    bl_label = "Inspector"

    first_mouse_x: IntProperty()
    first_mouse_y: IntProperty()
    first_value_x: FloatProperty()
    first_value_y: FloatProperty()
    obj_name: StringProperty()
    cursor_loc: FloatVectorProperty()

    def modal(self, context, event):

        scene = context.scene
        region = context.region
        rv3d = context.region_data
        coord = event.mouse_region_x, event.mouse_region_y

        view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
        ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)

        ray_target = view_vector

        if event.type == 'MOUSEMOVE':
            delta = self.first_mouse_x - event.mouse_x

            delta = self.first_mouse_y - event.mouse_y

        elif event.type == 'LEFTMOUSE':

            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            context.object.location.x = self.first_value
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):

        self.cursor_loc = copy.copy(context.scene.cursor.location)
        self.obj_name = context.object.name
        loc = copy.copy(context.object.location)

        if context.object:
            self.first_mouse_x = event.mouse_x
            self.first_mouse_y = event.mouse_y
            self.first_value_x = context.object.location.x
            self.first_value_y = context.object.location.y

            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "No active object, could not finish")
            return {'CANCELLED'}

    def execute(self, context):

        return {'FINISHED'}


class Originie_OT_Set2BboxSides(bpy.types.Operator):
    """Sets the pivot to the Bbox edges"""
    bl_idname = "originie.set2bboxsides"
    bl_label = "Bbox sides"
    bl_options = {'REGISTER', 'UNDO'}

    bbox_side: EnumProperty(name="Operation Type",
                            items={("X", "X", ""), ("Y", "Y", ""),
                                   ("Z", "Z", ""), ("-X", "-X", ""),
                                   ("-Y", "-Y", ""), ("-Z", "-Z", "")})

    def execute(self, context):

        C = context

        ob = C.object

        cursor = C.scene.cursor.location.copy()

        bbox = []

        m = ob.matrix_world

        for b in ob.bound_box:

            bbox.append(m @ Vector((b[0], b[1], b[2])))

        plus_x = (bbox[4] + bbox[5] + bbox[6] + bbox[7]) / 4
        plus_y = (bbox[2] + bbox[6] + bbox[3] + bbox[7]) / 4
        plus_z = (bbox[1] + bbox[5] + bbox[2] + bbox[6]) / 4

        minus_x = (bbox[0] + bbox[1] + bbox[2] + bbox[3]) / 4
        minus_y = (bbox[0] + bbox[4] + bbox[1] + bbox[5]) / 4
        minus_z = (bbox[0] + bbox[3] + bbox[4] + bbox[7]) / 4

        if self.bbox_side == "-X":
            setCursorLoc(loc=minus_x)

        elif self.bbox_side == "-Y":
            setCursorLoc(loc=minus_y)

        elif self.bbox_side == "-Z":
            setCursorLoc(loc=minus_z)

        elif self.bbox_side == "X":
            setCursorLoc(loc=plus_x)

        elif self.bbox_side == "Y":
            setCursorLoc(loc=plus_y)

        elif self.bbox_side == "Z":
            setCursorLoc(loc=plus_z)

        setOrigin2Cursor()

        setCursorLoc(cursor)

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager

        return wm.invoke_props_dialog(self)


class Originie_OT_Set2BboxEdges(bpy.types.Operator):
    """Sets the pivot to the Bbox edges"""
    bl_idname = "originie.set2bboxedges"
    bl_label = "Bbox edges"
    bl_options = {'REGISTER', 'UNDO'}

    bbox_edge: IntProperty(name="Bbox Edge",
                           description="",
                           default=0,
                           min=0,
                           max=11,
                           step=1)
    bbox_edge_percent: FloatProperty(name="Bbox Edge Percent",
                                     description="",
                                     default=0.5,
                                     min=0,
                                     max=1,
                                     step=5)

    def execute(self, context):

        C = context

        ob = C.object

        cursor = C.scene.cursor.location.copy()

        bbox = []

        m = ob.matrix_world

        for b in ob.bound_box:

            bbox.append(m @ Vector((b[0], b[1], b[2])))

        zero = bbox[0] + (bbox[3] - bbox[0]) * self.bbox_edge_percent
        one = bbox[0] + (bbox[1] - bbox[0]) * self.bbox_edge_percent
        two = bbox[1] + (bbox[2] - bbox[1]) * self.bbox_edge_percent
        three = bbox[2] + (bbox[3] - bbox[2]) * self.bbox_edge_percent
        four = bbox[3] + (bbox[7] - bbox[3]) * self.bbox_edge_percent
        five = bbox[6] + (bbox[7] - bbox[6]) * self.bbox_edge_percent
        six = bbox[2] + (bbox[6] - bbox[2]) * self.bbox_edge_percent
        seven = bbox[4] + (bbox[7] - bbox[4]) * self.bbox_edge_percent
        eight = bbox[4] + (bbox[5] - bbox[4]) * self.bbox_edge_percent
        nine = bbox[5] + (bbox[6] - bbox[5]) * self.bbox_edge_percent
        ten = bbox[1] + (bbox[5] - bbox[1]) * self.bbox_edge_percent
        eleven = bbox[0] + (bbox[4] - bbox[0]) * self.bbox_edge_percent

        edges = [
            zero, one, two, three, four, five, six, seven, eight, nine, ten,
            eleven
        ]

        setCursorLoc(edges[self.bbox_edge])

        setOrigin2Cursor()

        setCursorLoc(cursor)

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager

        return wm.invoke_props_dialog(self)


class Originie_OT_Set2BboxPoints(bpy.types.Operator):
    """Sets the pivot to the Bbox points"""
    bl_idname = "originie.set2bboxpoints"
    bl_label = "Bbox corners"
    bl_options = {'REGISTER', 'UNDO'}

    bbox_point: IntProperty(name="Bbox Points",
                            description="",
                            default=0,
                            min=0,
                            max=7,
                            step=1)

    def execute(self, context):

        C = context

        ob = C.object

        cursor = C.scene.cursor.location.copy()

        bbox = []

        m = ob.matrix_world

        for b in ob.bound_box:

            bbox.append(m @ Vector((b[0], b[1], b[2])))

        setCursorLoc(bbox[self.bbox_point])

        setOrigin2Cursor()

        setCursorLoc(cursor)

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager

        return wm.invoke_props_dialog(self)


class Originie_OT_Set2Random(bpy.types.Operator):
    """Randomize the pivot location"""
    bl_idname = "originie.set2random"
    bl_label = "Randomize"
    bl_options = {'REGISTER', 'UNDO'}

    range: FloatProperty(name="Range",
                         description="Range control for random location",
                         default=0,
                         min=0,
                         step=1)
    seed: IntProperty(name="Seed",
                      description="Range control for random location",
                      default=1,
                      min=0,
                      step=1)

    iscenter: BoolProperty(name="Center First",
                           description="Center the pivot first",
                           default=False)

    def execute(self, context):

        C = context

        ob = C.object

        cursor = C.scene.cursor.location.copy()

        if self.iscenter:
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')

        loc = ob.location.copy()

        bbox = []

        m = ob.matrix_world

        random.seed(loc.x + time.time() + self.seed)
        x = loc.x + self.range - 2 * random.random() * self.range

        random.seed(loc.y + time.time() + self.seed)
        y = loc.y + self.range - 2 * random.random() * self.range

        random.seed(loc.z + time.time() + self.seed)
        z = loc.z + self.range - 2 * random.random() * self.range

        loc_rand = Vector((x, y, z))

        setCursorLoc(loc_rand)

        setOrigin2Cursor()

        setCursorLoc(cursor)

        return {'FINISHED'}


class Originie_OT_Set2Ruler(bpy.types.Operator):
    """Sets the pivot to the ruler line"""
    bl_idname = "originie.set2ruler"
    bl_label = "To Ruler"
    bl_options = {'REGISTER', 'UNDO'}

    edge_percent: FloatProperty(name="Edge Percent",
                                description="",
                                default=0.5,
                                min=0,
                                max=1,
                                step=5)

    ruler0: FloatVectorProperty(options={'HIDDEN'})
    ruler1: FloatVectorProperty(options={'HIDDEN'})

    def execute(self, context):

        C = context

        ob = C.object

        cursor = C.scene.cursor.location.copy()

        m = ob.matrix_world

        ruler0 = Vector((self.ruler0))
        ruler1 = Vector((self.ruler1))

        loc = ruler1 + ruler0 * self.edge_percent

        setCursorLoc(loc)

        setOrigin2Cursor()

        setCursorLoc(cursor)

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager

        self.ruler0 = copy.copy(parseGuideLine()[0])
        self.ruler1 = copy.copy(parseGuideLine()[1])
        return wm.invoke_props_dialog(self)


class Originie_OT_Set2World(bpy.types.Operator):
    """Sets the pivot to the world origin"""
    bl_idname = "originie.set2world"
    bl_label = "World Origin"
    bl_options = {'REGISTER', 'UNDO'}

    edge_percent: FloatProperty(name="Edge Percent",
                                description="",
                                default=1,
                                min=0,
                                max=1,
                                step=5)

    def execute(self, context):

        C = context

        ob = C.object

        ob_loc = ob.location.copy()

        cursor = C.scene.cursor.location.copy()

        m = ob.matrix_world

        loc = Vector((0, 0, 0))

        loc = ob_loc + (loc - ob_loc) * self.edge_percent

        setCursorLoc(loc)

        setOrigin2Cursor()

        setCursorLoc(cursor)

        return {'FINISHED'}


class Originie_OT_Set2TopBottom(bpy.types.Operator):
    """Sets the pivot to the world origin"""
    bl_idname = "originie.set2topbottom"
    bl_label = "Bottom"
    bl_options = {'REGISTER', 'UNDO'}

    iscenter: BoolProperty(name="Center First",
                           description="Center the pivot first",
                           default=False)
    type: StringProperty(name="Where", default="bottom", options={'HIDDEN'})

    @classmethod
    def poll(cls, context):

        return bpy.context.object.type == "MESH"

    def execute(self, context):

        C = context
        objs = [o for o in C.selected_objects if o.type == "MESH"]

        selection = C.selected_objects.copy()
        for ob in objs:

            setSelectActiveObject(C, ob)
            if self.iscenter:
                bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY',
                                          center='MEDIAN')

            ob_loc = ob.location.copy()

            cursor = C.scene.cursor.location.copy()

            loc = ob_loc

            if self.type == "bottom":

                loc.z = findBBoxWorldNumPy(context)[0][2]

            elif self.type == "top":
                loc.z = findBBoxWorldNumPy(context)[1][2]

            setCursorLoc(loc)

            setOrigin2Cursor()

            setCursorLoc(cursor)

        for ob in selection:
            ob.select_set(True)

        return {'FINISHED'}


class Originie_OT_Set2Selected(bpy.types.Operator):
    """Sets the active object's pivot to the selected object(s)"""
    bl_idname = "originie.set2selected"
    bl_label = "To Selected"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):

        return len(context.selected_objects) > 1 or len(
            [v for v in context.object.data.vertices if v.select]) > 0

    def execute(self, context):

        C = context

        active = C.object
        active_name = active.name

        cursor = C.scene.cursor.location.copy()
        objs = C.selected_objects.copy()

        if isObjectMode() and len(objs) > 1:
            objs.remove(getObjectbyName(active_name))

            middle = Vector((0, 0, 0))

            for ob in objs:
                middle += ob.location

            middle = middle / len(objs)

            deselectAll()

            setSelectActiveObject(context, getObjectbyName(active_name))

            ob_loc = active.location.copy()

            setCursorLoc(middle)

            setOrigin2Cursor()

            setCursorLoc(cursor)

        elif isEditMode() and C.object:
            setCursor2Selected()
            objectMode()
            setOrigin2Cursor()
            bpy.ops.object.editmode_toggle()

            setCursorLoc(cursor)

        return {'FINISHED'}


class Originie_OT_Set2Active(bpy.types.Operator):
    """Sets the selected object's pivot to the active object (the last selected)"""
    bl_idname = "originie.set2active"
    bl_label = "To Active"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):

        return len(context.selected_objects) > 0 and bool(context.object)

    def execute(self, context):

        C = context

        active = C.object
        active_loc = active.location.copy()
        active_name = active.name
        m = active.matrix_world

        if len(C.selected_objects) > 0:
            objs = C.selected_objects.copy()

            objs.remove(getObjectbyName(active_name))

        else:
            objs = C.object

        cursor = C.scene.cursor.location.copy()

        if isObjectMode():

            deselectAll()

            for ob in objs:

                setCursorLoc(active_loc)
                setSelectActiveObject(context, ob)
                setOrigin2Cursor()

            for ob in objs:
                ob.select_set(True)

        elif isEditMode():
            co = m @ getActiveComponent()

            setCursorLoc(co)

            objectMode()
            setOrigin2Cursor()
            bpy.ops.object.editmode_toggle()

        setCursorLoc(cursor)

        return {'FINISHED'}


class Originie_OT_Set2Parent(bpy.types.Operator):
    """Sets the selected obj's pivot to the the parent's location"""
    bl_idname = "originie.set2parent"
    bl_label = "To Parent"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        C = context

        active = C.object
        active_loc = active.location.copy()
        active_name = active.name

        cursor = C.scene.cursor.location.copy()

        parent_loc = getParentLoc(active)

        setCursorLoc(parent_loc)

        setOrigin2Cursor()

        setCursorLoc(cursor)

        return {'FINISHED'}


class Originie_OT_SetFakePivot(bpy.types.Operator):
    """Sets the pivot to the the Parent's location"""
    bl_idname = "originie.setfakepivot"
    bl_label = "Fake Pivot"
    bl_options = {'REGISTER', 'UNDO'}

    fake_loc: EnumProperty(name="Location ", items=FAKE_LOCATION)

    def execute(self, context):

        C = context

        active = C.object
        active_loc = active.location.copy()
        active_name = active.name

        cursor = C.scene.cursor.location.copy()

        if self.fake_loc == "CURSOR":

            setFakePivot(self)

        elif self.fake_loc == "OBJECT":
            setCursorLoc(active_loc)
            setFakePivot(self)

        elif self.fake_loc == "SELECTED":

            bpy.ops.originie.set2selected()
            bpy.ops.view3d.snap_cursor_to_selected()
            setFakePivot(self)
            setCursorLoc(active_loc)
            setSelectActiveObject(context, active)
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')

        elif self.fake_loc == "WORLD":

            bpy.ops.view3d.snap_cursor_to_center()

            setFakePivot(self)

        setCursorLoc(cursor)

        return {'FINISHED'}


def local_offset_update_func(self, context):

    if self.local_offset:
        self.entry_x = 0.0
        self.entry_y = 0.0
        self.entry_z = 0.0

    else:

        self.entry_x = self.loc[0]
        self.entry_y = self.loc[1]
        self.entry_z = self.loc[2]


class Originie_OT_SetNumerical(bpy.types.Operator):
    """Input numerical entries for the 3d coorodinates of the pivot"""
    bl_idname = "originie.setnumerical"
    bl_label = "Numerical Input"
    bl_options = {'REGISTER', 'UNDO'}

    entry_x: FloatProperty(name="X axis",
                           description="Enter X axis value",
                           default=0.0)
    entry_y: FloatProperty(name="Y axis",
                           description="Enter Y axis value",
                           default=0.0)
    entry_z: FloatProperty(name="Z axis",
                           description="Enter Z axis value",
                           default=0.0)

    loc: FloatVectorProperty(name="Original Loc",
                             description="Original Location",
                             options={'HIDDEN'})

    local_offset: BoolProperty(name="Offset",
                               description="Local Values",
                               default=False,
                               update=local_offset_update_func)

    def execute(self, context):

        C = context

        active = C.object
        active_loc = active.location.copy()
        active_loc_world = active.matrix_world.translation.copy()
        active_name = active.name

        cursor = C.scene.cursor.location.copy()

        if self.local_offset:

            entry_final = Vector((0, 0, 0))

            entry = active_loc + Vector(
                (self.entry_x, self.entry_y, self.entry_z))

            entry_final = entry

        else:

            entry_final = Vector((self.entry_x, self.entry_y, self.entry_z))

        setCursorLoc(entry_final)

        setOrigin2Cursor()
        setCursorLoc(cursor)

        return {'FINISHED'}

    def invoke(self, context, event):

        loc = context.object.location.copy()
        self.local_offset = False
        self.entry_x = loc.x
        self.entry_y = loc.y
        self.entry_z = loc.z

        self.loc = Vector((loc))

        wm = context.window_manager

        return wm.invoke_props_dialog(self)


class Originie_OT_DropToGround(bpy.types.Operator):
    """Drop the object to ground level"""
    bl_idname = "originie.drop_to_ground"
    bl_label = "Drop to Ground"
    bl_options = {'REGISTER', 'UNDO'}

    reset_rotation: BoolProperty(
        name="Reset Rotation",
        description="Drops the object to ground level",
        default=False)

    def execute(self, context):

        C = context

        active = C.object
        active_loc = active.location.copy()
        active_rot = active.rotation_euler.copy()
        active_name = active.name

        cursor = C.scene.cursor.location.copy()

        if self.reset_rotation:

            bpy.ops.object.rotation_clear(clear_delta=False)

        bpy.ops.originie.set2topbottom(type="bottom")

        bpy.ops.view3d.snap_cursor_to_selected()

        cursor_temp = C.scene.cursor.location
        cursor_temp.z = 0

        bpy.ops.view3d.snap_selected_to_cursor(use_offset=False)

        setCursorLoc(cursor)

        return {'FINISHED'}

    def invoke(self, context, event):

        wm = context.window_manager

        return wm.invoke_props_dialog(self)


class Originie_OT_Unitfy(bpy.types.Operator):
    """Drop the object to ground level"""
    bl_idname = "originie.unitfy"
    bl_label = "Unify Object Scale"
    bl_options = {'REGISTER', 'UNDO'}

    reset_rotation: BoolProperty(name="Reset Rotation",
                                 description="Reset rotation prior to fitting",
                                 default=False)

    @classmethod
    def poll(cls, context):

        return context.mode == 'OBJECT'

    def execute(self, context):

        C = context

        active = C.object
        selected = [obj for obj in C.selected_objects if obj.type == 'MESH']

        for active in selected:

            setSelectActiveObject(context, active)

            d = active.dimensions

            v = np.array(d)
            active.dimensions = d / v.max() * 2

            if self.reset_rotation:
                bpy.ops.object.rotation_clear(clear_delta=False)

            bpy.ops.object.transform_apply(location=True,
                                           rotation=self.reset_rotation,
                                           scale=True)

            cur = setCursorLoc(findBBoxNumPy(context)[2])

            setOrigin2Cursor()
            bpy.ops.object.location_clear(clear_delta=False)

            bpy.ops.object.location_clear(clear_delta=False)

        return {'FINISHED'}


class Originie_OT_EditPivot_280(bpy.types.Operator):
    """Edit the active object's pivot in ortho views"""
    bl_idname = "originie.editpivot_280"
    bl_label = "Edit Pivot"

    first_mouse_x: IntProperty()
    first_mouse_y: IntProperty()
    first_value_x: FloatProperty()
    first_value_y: FloatProperty()
    obj_name: StringProperty()
    cursor_loc: FloatVectorProperty()

    def __init__(self):
        self.precision = 1.0

    def modal(self, context, event):

        scene = context.scene
        cur_obj_name = copy.copy(context.object.name)

        region = context.region
        rv3d = context.region_data
        coord = event.mouse_region_x, event.mouse_region_y

        view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
        ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)

        ray_target = view_vector

        ortho = rv3d.view_matrix.decompose()[1].to_euler()
        viewport = "NONE"

        viewdistance = (rv3d.view_distance / 15)

        if isClose(ortho.x, -1.5708, 0.1, 0) and ortho.y == 0 and ortho.z == 0:
            viewport = "front"
            signx = 1
            signy = 1

        if isClose(ortho.x, 1.5708, 0.1, 0) and ortho.y == 0 and isClose(
                ortho.z, 3.1416, 0.1, 0):
            viewport = "back"
            signx = -1
            signy = 1

        if isClose(ortho.x, -1.5708, 0.1, 0) and isClose(
                ortho.y, -1.5708, 0.1, 0) and ortho.z == 0:
            viewport = "right"
            signx = 1
            signy = 1

        if isClose(ortho.x, -1.5708, 0.1, 0) and isClose(
                ortho.y, 1.5708, 0.1, 0) and ortho.z == 0:
            viewport = "left"
            signx = -1
            signy = 1

        if ortho.x == 0 and ortho.y == 0 and ortho.z == 0:
            viewport = "top"
            signx = 1
            signy = 1

        if isClose(ortho.x, 3.1416, 0.1, 0) and ortho.y == 0 and ortho.z == 0:
            viewport = "bottom"
            signx = 1
            signy = -1

        if event.type in {
                'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE', 'NUMPAD_1',
                'NUMPAD_2', 'NUMPAD_3', 'NUMPAD_4', 'NUMPAD_6', 'NUMPAD_7',
                'NUMPAD_8', 'NUMPAD_9', 'NUMPAD_5'
        }:
            return {'PASS_THROUGH'}

        if event.type == 'MOUSEMOVE':

            if viewport in {"front", "back"}:
                delta = signx * (self.first_mouse_x -
                                 event.mouse_x) * viewdistance
                context.object.location.x = self.first_value_x - delta * 0.01

                delta = signy * (self.first_mouse_y -
                                 event.mouse_y) * viewdistance
                context.object.location.z = self.first_value_z - delta * 0.01

            if viewport in {"left", "right"}:
                delta = signx * (self.first_mouse_x -
                                 event.mouse_x) * viewdistance
                context.object.location.y = self.first_value_y - delta * 0.01

                delta = signy * (self.first_mouse_y -
                                 event.mouse_y) * viewdistance
                context.object.location.z = self.first_value_z - delta * 0.01

            if viewport in {"top", "bottom"}:
                delta = signx * (self.first_mouse_x -
                                 event.mouse_x) / 2 * viewdistance
                context.object.location.x = self.first_value_x - delta * 0.01

                delta = signy * (self.first_mouse_y -
                                 event.mouse_y) / 2 * viewdistance
                context.object.location.y = self.first_value_y - delta * 0.01

        elif event.type == 'LEFTMOUSE':

            pivot = context.object

            cursor_loc = copy.copy(bpy.context.scene.cursor.location)

            bpy.ops.view3d.snap_cursor_to_selected()

            bpy.ops.object.select_all(action='DESELECT')

            obj = bpy.data.objects[self.obj_name]

            context.view_layer.objects.active = obj
            obj.select_set(True)

            bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')

            bpy.context.scene.cursor.location = self.cursor_loc

            bpy.data.objects.remove(pivot)

            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:

            pivot = context.object
            bpy.data.objects.remove(pivot)
            obj = getObjectbyName(self.obj_name)
            setSelectActiveObject(context, obj)

            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):

        self.cursor_loc = copy.copy(context.scene.cursor.location)
        self.obj_name = context.object.name
        loc = copy.copy(context.object.location)

        d = context.object.dimensions

        self.precision = (d[0] + d[1] + d[2]) / 3

        bpy.ops.object.empty_add(type='PLAIN_AXES',
                                 location=loc,
                                 radius=self.precision / 2)

        if context.object:
            self.first_mouse_x = event.mouse_x
            self.first_mouse_y = event.mouse_y
            self.first_value_x = context.object.location.x
            self.first_value_y = context.object.location.y
            self.first_value_z = context.object.location.z
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "No active object, could not finish")
            return {'CANCELLED'}

    def execute(self, context):

        return {'FINISHED'}


class Originie_OT_EditPivot(bpy.types.Operator):
    """Edit the active object's pivot in ortho views"""
    bl_idname = "originie.editpivot"
    bl_label = "Edit Pivot"

    first_mouse_x: IntProperty()
    first_mouse_y: IntProperty()
    first_value_x: FloatProperty()
    first_value_y: FloatProperty()
    obj_name: StringProperty()
    cursor_loc: FloatVectorProperty()

    @classmethod
    def poll(cls, context):
        return hasattr(bpy.context.scene.tool_settings,
                       "use_transform_data_origin")

    def invoke(self, context, event):

        if not context.scene.originie_doneeditpivot:
            context.scene.originie_isgizmovisible = context.space_data.show_gizmo_tool
            context.scene.originie_gizmostates = storeShowGizmo()

        return self.execute(context)

    def execute(self, context):

        if (not isPivotEditMode()) and (
                not context.scene.originie_doneeditpivot):
            bpy.context.scene.tool_settings.use_transform_data_origin = True

            enableManipulator(context)

            context.scene.originie_doneeditpivot = True

        else:
            if context.scene.originie_doneeditpivot:

                restoreShowGizmo(context.scene.originie_gizmostates)
                context.scene.originie_doneeditpivot = False

            bpy.context.scene.tool_settings.use_transform_data_origin = False

        return {'FINISHED'}


class ORIGINIE_OT_BboxPick(Operator):
    bl_idname = "originie.bboxpick"
    bl_label = "Draw operator"
    bl_description = "Operator for drawing"
    bl_options = {'REGISTER'}

    def __init__(self):
        self.draw_handle_2d = None
        self.draw_handle_3d = None
        self.draw_event = None
        self.mouse_vert = None
        self.offset = 0.02

        self.hit = Vector((0, 0, 0))
        self.normal = Vector((0, 0, 0))

        self.vertices = []
        self.create_batch()

        self.plus_x = Vector((0, 0, 0))
        self.plus_y = Vector((0, 0, 0))
        self.plus_z = Vector((0, 0, 0))

        self.minus_x = Vector((0, 0, 0))
        self.minus_y = Vector((0, 0, 0))
        self.minus_z = Vector((0, 0, 0))
        self.bbox = [Vector((0, 0, 0))] * 6
        self.bbox_sides = []
        self.plus_xindex = ()
        self.cur_center = Vector((0, 0, 0))
        self.bbox_precision = 0.0
        self.is_cursor = None

        self.is_bbox_face = False
        self.is_bbox_edge = False
        self.is_bbox_corner = False

        self.cursor = Vector((0, 0, 0))

        self.temp_box = None
        self.active_obj = None
        self.active_pivot = Vector((0, 0, 0))

        self.kd = None

    @classmethod
    def poll(cls, context):
        return (context.active_object is not None
                and context.active_object.mode == 'OBJECT')

    def invoke(self, context, event):

        self.active_obj = context.object
        self.active_pivot = context.object.location.copy()
        args = (self, context)
        self.register_handlers(args, context)

        context.window_manager.modal_handler_add(self)

        deselectAll()

        self.temp_box = makeBboxMesh()
        setSelectActiveObject(context, self.temp_box)
        bpy.context.object.display_type = 'BOUNDS'

        self.bvhtree = self.bvhtree_from_object(context, self.temp_box)

        self.cursor = context.scene.cursor.location.copy()
        self.is_cursor = bpy.context.space_data.overlay.show_cursor

        context.space_data.overlay.show_cursor = False

        bbox = self.getBBOX()
        self.bbox = bbox

        self.plus_x = [bbox[0], bbox[3], bbox[2], bbox[1]]
        self.plus_xindex = ((0, 3), (2, 1), (3, 2), (1, 0))

        self.plus_y = [bbox[0], bbox[1], bbox[5], bbox[4]]
        self.plus_z = [bbox[1], bbox[2], bbox[6], bbox[5]]
        self.minus_x = [bbox[4], bbox[7], bbox[6], bbox[5]]
        self.minus_y = [bbox[3], bbox[2], bbox[6], bbox[7]]
        self.minus_z = [bbox[0], bbox[3], bbox[7], bbox[4]]

        self.vertices.append(self.bbox[0])
        self.vertices.append(self.bbox[3])
        self.vertices.append(self.bbox[2])

        mesh = context.object.data
        size = len(mesh.vertices)
        self.kd = mathutils.kdtree.KDTree(size)

        for i, v in enumerate(mesh.vertices):
            self.kd.insert(v.co, i)

        self.kd.balance()

        return {"RUNNING_MODAL"}

    def register_handlers(self, args, context):
        self.draw_handle_3d = bpy.types.SpaceView3D.draw_handler_add(
            self.draw_callback_3d, args, "WINDOW", "POST_VIEW")

        self.draw_handle_2d = bpy.types.SpaceView3D.draw_handler_add(
            self.draw_callback_2d, args, "WINDOW", "POST_PIXEL")

        self.draw_event = context.window_manager.event_timer_add(
            0.1, window=context.window)

    def unregister_handlers(self, context):

        context.window_manager.event_timer_remove(self.draw_event)
        bpy.types.SpaceView3D.draw_handler_remove(self.draw_handle_2d,
                                                  "WINDOW")
        bpy.types.SpaceView3D.draw_handler_remove(self.draw_handle_3d,
                                                  "WINDOW")

        self.draw_handle_2d = None
        self.draw_handle_3d = None
        self.draw_event = None
        self.bvhtree = None

    def bvhtree_from_object(self, context, object):
        bm = bmesh.new()

        depsgraph = context.evaluated_depsgraph_get()
        ob_eval = object.evaluated_get(depsgraph)
        mesh = ob_eval.to_mesh()

        bm.from_mesh(mesh)
        bm.transform(object.matrix_world)

        bvhtree = BVHTree.FromBMesh(bm)
        ob_eval.to_mesh_clear()
        return bvhtree

    def findClosestCorner(self, loc, range=0.0):

        co_find = loc

        if range < 0.01:
            range = 0.03

        return self.kd.find_range(loc, range)

    def get_origin_and_direction(self, event, context):
        region = context.region
        region_3d = context.space_data.region_3d

        mouse_coord = (event.mouse_region_x, event.mouse_region_y)

        origin = region_2d_to_origin_3d(region, region_3d, mouse_coord)
        direction = region_2d_to_vector_3d(region, region_3d, mouse_coord)

        return origin, direction

    def get_mouse_3d_on_mesh(self, event, context):

        context = bpy.context

        origin, direction = self.get_origin_and_direction(event, context)

        self.hit, self.normal, *_ = self.bvhtree.ray_cast(
            origin, direction, 100.0)

        if self.hit is not None:
            self.hit = self.hit + (self.normal * self.offset)

        return self.hit

    def get_mouse_3d_on_plane(self, event, context):

        origin, direction = self.get_origin_and_direction(event, context)

        return intersect_line_plane(origin, origin + direction, self.hit,
                                    self.normal)

    def isBboxVertex(self, face=[]):

        for v in face:

            if isClose(v.length_squared, self.hit.length_squared,
                       self.bbox_precision, 0.1):
                return v

        return False

    def isBboxSide(self, event, context):

        origin, direction = self.get_origin_and_direction(event, context)

        hit = self.hit

        side = self.plus_x

        if hit:

            plus_x_t1 = intersect_point_tri(hit, side[0], side[1], side[2])
            plus_x_t2 = intersect_point_tri(hit, side[2], side[3], side[0])
            plus_x_t11 = intersect_ray_tri(side[0], side[1], side[2],
                                           direction, origin)
            plus_x_t22 = intersect_ray_tri(side[2], side[3], side[0],
                                           direction, origin)

            side = self.plus_y
            plus_y_t1 = intersect_point_tri(hit, side[0], side[1], side[2])
            plus_y_t2 = intersect_point_tri(hit, side[2], side[3], side[0])
            plus_y_t11 = intersect_ray_tri(side[0], side[1], side[2],
                                           direction, origin)
            plus_y_t22 = intersect_ray_tri(side[2], side[3], side[0],
                                           direction, origin)

            side = self.plus_z
            plus_z_t1 = intersect_point_tri(hit, side[0], side[1], side[2])
            plus_z_t2 = intersect_point_tri(hit, side[2], side[3], side[0])
            plus_z_t11 = intersect_ray_tri(side[0], side[1], side[2],
                                           direction, origin)
            plus_z_t22 = intersect_ray_tri(side[2], side[3], side[0],
                                           direction, origin)

            side = self.minus_x
            minus_x_t1 = intersect_point_tri(hit, side[0], side[1], side[2])
            minus_x_t2 = intersect_point_tri(hit, side[2], side[3], side[0])
            minus_x_t11 = intersect_ray_tri(side[0], side[1], side[2],
                                            direction, origin)
            minus_x_t22 = intersect_ray_tri(side[2], side[3], side[0],
                                            direction, origin)

            side = self.minus_y
            minus_y_t1 = intersect_point_tri(hit, side[0], side[1], side[2])
            minus_y_t2 = intersect_point_tri(hit, side[2], side[3], side[0])
            minus_y_t11 = intersect_ray_tri(side[0], side[1], side[2],
                                            direction, origin)
            minus_y_t22 = intersect_ray_tri(side[2], side[3], side[0],
                                            direction, origin)

            side = self.minus_z
            minus_z_t1 = intersect_point_tri(hit, side[0], side[1], side[2])
            minus_z_t2 = intersect_point_tri(hit, side[2], side[3], side[0])
            minus_z_t11 = intersect_ray_tri(side[0], side[1], side[2],
                                            direction, origin)
            minus_z_t22 = intersect_ray_tri(side[2], side[3], side[0],
                                            direction, origin)

            if (plus_x_t1 or plus_x_t2) and (plus_x_t11 or plus_x_t22):
                return self.plus_x

            elif (plus_y_t1 or plus_y_t2) and (plus_y_t11 or plus_y_t22):
                return self.plus_y

            elif (plus_z_t1 or plus_z_t2) and (plus_z_t11 or plus_z_t22):
                return self.plus_z

            elif (minus_x_t1 or minus_x_t2) and (minus_x_t11 or minus_x_t22):
                return self.minus_x

            elif (minus_y_t1 or minus_y_t2) and (minus_y_t11 or minus_y_t22):

                return self.minus_y

            elif (minus_z_t1 or minus_z_t2) and (minus_z_t11 or minus_z_t22):
                return self.minus_z

            else:
                return False

        else:
            return False

    def modal(self, context, event):
        if context.area:
            context.area.tag_redraw()

        if event.type in {"ESC"}:

            bpy.data.objects.remove(self.temp_box)

            context.scene.cursor.location = self.active_pivot
            setSelectActiveObject(context, self.active_obj)
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
            context.scene.cursor.location = self.cursor

            toggleCursor(self.is_cursor)

            self.unregister_handlers(context)
            return {'CANCELLED'}

        if event.type == "MOUSEMOVE":

            self.get_mouse_3d_on_mesh(event, context)

            if self.hit:

                hit_side = self.isBboxSide(event, context)

                if hit_side:

                    self.is_bbox_face = True
                    self.is_bbox_edge = False
                    self.is_bbox_corner = False

                    self.vertices = []

                    for v in hit_side:
                        self.vertices.append(v)
                        self.cur_center += v

                    self.cur_center = self.cur_center / 4

                    self.create_batch()

                    for (corner, index, dist) in self.findClosestCorner(
                            self.hit, self.bbox_precision):

                        if corner:
                            self.is_bbox_face = False
                            self.is_bbox_edge = False
                            self.is_bbox_corner = True

                            context.scene.cursor.location = corner
                            self.create_batch_square(corner)

                        else:
                            print("NOOOOO CORNER HIT")

                else:
                    self.vertices = [Vector((0, 0, 0))] * 4
                    self.create_batch()

            return {"RUNNING_MODAL"}

        if event.value == "PRESS":

            if event.type == "LEFTMOUSE":

                if self.is_bbox_face:
                    self.cur_center = Vector((0, 0, 0))
                    hit_side = self.isBboxSide(event, context)

                    if hit_side:

                        for v in hit_side:
                            self.vertices.append(v)
                            self.cur_center += v

                        self.cur_center = self.cur_center / 4

                        context.scene.cursor.location = self.cur_center

                        bpy.ops.object.origin_set(type='ORIGIN_CURSOR',
                                                  center='MEDIAN')

                elif self.is_bbox_corner:
                    bpy.ops.object.origin_set(type='ORIGIN_CURSOR',
                                              center='MEDIAN')

                return {"RUNNING_MODAL"}

            if event.type == "RET":

                self.get_mouse_3d_on_mesh(event, context)

                bpy.data.objects.remove(self.temp_box)

                self.unregister_handlers(context)

                setSelectActiveObject(context, self.active_obj)

                bpy.ops.object.origin_set(type='ORIGIN_CURSOR',
                                          center='MEDIAN')

                context.scene.cursor.location = self.cursor
                toggleCursor(self.is_cursor)

                return {'FINISHED'}

        return {"PASS_THROUGH"}

    def create_object(self):

        mesh = bpy.data.meshes.new("MyMesh")
        obj = bpy.data.objects.new("MyObject", mesh)

        bpy.context.scene.collection.objects.link(obj)
        bpy.context.view_layer.objects.active = obj

        bpy.ops.object.select_all(action='DESELECT')

        obj.select_set(state=True)

        bm = bmesh.new()

        for v in self.vertices:
            bm.verts.new(v)

        bm.to_mesh(mesh)
        bm.free()

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')

        bpy.ops.mesh.edge_face_add()

        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')

    def getBBOX(self):

        C = bpy.context

        ob = C.object

        cursor = C.scene.cursor.location.copy()

        bbox = []

        m = ob.matrix_world

        for b in ob.bound_box:

            bbox.append(m @ Vector((b[0], b[1], b[2])))

        l = Vector(bbox[6]) - Vector(bbox[0])

        d = ob.dimensions

        self.bbox_precision = ((d[0] + d[1] + d[2]) / 3) / 5

        return bbox

    def finish(self):
        self.unregister_handlers(context)
        return {"FINISHED"}

    def drawVertices(self):
        v = self.vertices

        v_pos = []
        for v in v:

            v_pos.append(v.to_tuple())

        fmt = gpu.types.GPUVertFormat()
        fmt.attr_add(id="pos", comp_type='F32', len=3, fetch_mode='FLOAT')

        vbo = gpu.types.GPUVertBuf(len=4, format=fmt)
        vbo.attr_fill(id="pos", data=v_pos)

    def create_batch(self):

        points = self.vertices.copy()

        indices = ((0, 3), (2, 1), (3, 2), (1, 0))

        self.shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
        self.batch = batch_for_shader(self.shader, 'LINE_LOOP',
                                      {"pos": points})

    def create_batch_square(self, loc):

        push = self.bbox_precision / 3
        loc = Vector(loc)
        vertices = ((loc.x - push, loc.y, loc.z + push), (loc.x + push, loc.y,
                                                          loc.z + push),
                    (loc.x + push, loc.y, loc.z - push), (loc.x - push, loc.y,
                                                          loc.z - push),
                    (loc.x, loc.y - push, loc.z + push), (loc.x, loc.y + push,
                                                          loc.z + push),
                    (loc.x, loc.y + push, loc.z - push), (loc.x, loc.y - push,
                                                          loc.z - push),
                    (loc.x - push, loc.y + push, loc.z), (loc.x + push,
                                                          loc.y + push, loc.z),
                    (loc.x + push, loc.y - push, loc.z), (loc.x - push,
                                                          loc.y - push, loc.z))

        indices = ((0, 3), (2, 1), (3, 2), (1, 0), (0 + 4, 3 + 4),
                   (2 + 4, 1 + 4), (3 + 4, 2 + 4), (1 + 4, 0 + 4),
                   (0 + 8, 3 + 8), (2 + 8, 1 + 8), (3 + 8, 2 + 8), (1 + 8,
                                                                    0 + 8))

        self.shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')

        self.batch = batch_for_shader(self.shader,
                                      'LINES', {"pos": vertices},
                                      indices=indices)

    def draw_callback_2d(self, op, context):
        region = context.region
        text = "Pick Pivot Point location"
        subtext = "Esc : Cancel < + > Enter : Finish"

        xt = int(region.width / 2.0)

        blf.size(0, 24, 72)
        blf.position(0, xt - blf.dimensions(0, text)[0] / 2, 60, 0)
        blf.draw(0, text)

        blf.size(1, 20, 72)
        blf.position(1, xt - blf.dimensions(0, subtext)[0] / 2, 30, 1)
        blf.draw(1, subtext)

    def draw_callback_3d(self, op, context):

        bgl.glLineWidth(6)
        self.shader.bind()
        self.shader.uniform_float("color", (0.1, 0.3, 0.7, 1.0))
        self.batch.draw(self.shader)

    def draw_callback_Points(self, op, context):

        bgl.glLineWidth(8)
        self.shader.bind()
        self.shader.uniform_float("color", (0.4, 0.5, 0.7, 1.0))
        self.batch.draw(self.shader)


def register_interactive_bbox():
    bpy.utils.register_class(ORIGINIE_OT_BboxPick)

    kcfg = bpy.context.window_manager.keyconfigs.addon
    if kcfg:
        km = kcfg.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new("originie.bboxpick",
                                  'B',
                                  'PRESS',
                                  shift=True,
                                  ctrl=True)
        addon_keymaps.append((km, kmi))


def unregister_register_interactive_bbox():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    bpy.utils.unregister_class(ORIGINIE_OT_BboxPick)


class VIEW3D_MT_PIE_Originie(Menu):

    bl_label = "Originie Tools"

    @classmethod
    def poll(cls, context):

        return isObjectMode() or isEditMode()

    def draw(self, context):
        layout = self.layout

        pie = layout.menu_pie()

        box = pie.split().box().column()

        column = box

        if isObjectMode():
            box.operator("originie.set2topbottom", text="Top").type = "top"
            box.operator("originie.set2topbottom",
                         text="Bottom").type = "bottom"
            box.operator("originie.bboxpick", text="Bbox Interactive")
            box.operator("originie.set2bboxsides")
            box.operator("originie.set2bboxedges")
            box.operator("originie.set2bboxpoints")

            box = pie.split().box().column()

            box.operator("originie.setnumerical")
            box.operator("originie.editpivot_280")
            box.operator("originie.editpivot", text="Edit Pivot Beta (2.81)")
            box.operator("originie.set2random")
            box.operator("originie.set2ruler")

            if isFakePivot():
                box.operator("originie.setfakepivot", text="Fake Apply")
            else:
                box.operator("originie.setfakepivot", text="Fake Pivot")

            box.operator("originie.drop_to_ground")
            box.operator("originie.unitfy", text="Unitfy")

            box = pie.split().box().column()

        if isObjectMode():
            box.operator("object.origin_set",
                         text="Geometric center").type = "ORIGIN_GEOMETRY"
            box.operator("object.origin_set",
                         text="Cursor").type = "ORIGIN_CURSOR"

            box.operator("originie.set2selected")
            box.operator("originie.set2active")
            box.operator("originie.set2parent")
            box.operator("originie.set2world")

        if isEditMode():
            box.operator("originie.set2selected")
            box.operator("originie.set2active")


classes = (
    VIEW_OT_Inspector,
    Originie_OT_Set2BboxSides,
    Originie_OT_Set2BboxEdges,
    Originie_OT_Set2BboxPoints,
    Originie_OT_Set2Random,
    Originie_OT_EditPivot,
    Originie_OT_EditPivot_280,
    Originie_OT_Set2Ruler,
    Originie_OT_Set2World,
    Originie_OT_Set2TopBottom,
    Originie_OT_Set2Selected,
    Originie_OT_Set2Active,
    Originie_OT_Set2Parent,
    Originie_OT_SetFakePivot,
    Originie_OT_SetNumerical,
    Originie_OT_DropToGround,
    Originie_OT_Unitfy,
    VIEW3D_MT_PIE_Originie,
)

addon_keymaps = []


def register():

    defineSceneProps()

    for cls in classes:

        bpy.utils.register_class(cls)

    register_interactive_bbox()

    wm = bpy.context.window_manager

    km = wm.keyconfigs.addon.keymaps.new(name="3D View", space_type="VIEW_3D")

    kmi = km.keymap_items.new('wm.call_menu_pie', 'SEMI_COLON', 'PRESS')
    kmi.properties.name = "VIEW3D_MT_PIE_Originie"
    addon_keymaps.append((km, kmi))

    kmi = km.keymap_items.new('originie.editpivot', 'INSERT', 'PRESS')

    addon_keymaps.append((km, kmi))


def unregister():

    for cls in classes:
        bpy.utils.unregister_class(cls)

    unregister_register_interactive_bbox()

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        for km, kmi in addon_keymaps:
            km.keymap_items.remove(kmi)

    addon_keymaps.clear()


if __name__ == "__main__":
    register()
