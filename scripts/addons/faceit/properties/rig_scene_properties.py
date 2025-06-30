import bpy
from bpy.props import (PointerProperty, StringProperty, BoolProperty, EnumProperty, FloatVectorProperty)
from bpy.types import Bone, Object, Scene
from mathutils import Vector


from ..rigging.pivot_manager import PivotManager, copy_pivot_from_bone, get_eye_pivot_from_landmarks, get_eye_pivot_from_vertex_group
from ..core.vgroup_utils import get_vertex_groups_from_objects
from ..core.modifier_utils import populate_bake_modifier_items
from ..core.faceit_utils import get_rig_type, is_faceit_original_armature, get_faceit_objects_list
from ..core.faceit_data import FACEIT_CTRL_BONES


def faceit_armature_poll(self, obj):
    '''Return True if the object is a valid faceit rig (armature).'''
    if obj.type == 'ARMATURE' and obj.name in self.objects:
        return True


def update_faceit_armature(self, context):
    if self.faceit_armature is not None:
        self.faceit_armature_missing = False


def body_armature_poll(self, obj):
    '''Return True if the object is a valid body rig (armature).'''
    if obj.type == 'ARMATURE' and obj.name in self.objects:
        if not is_faceit_original_armature(obj):
            return True


def update_body_armature(self, context):
    rig = self.faceit_body_armature
    self.faceit_use_rigify_armature = False
    self.faceit_is_rigify_armature = False
    if rig is None:
        return
    if get_rig_type(rig) in ('RIGIFY', 'RIGIFY_NEW'):
        self.faceit_use_rigify_armature = True
        self.faceit_is_rigify_armature = True
    # try to find head bone name
    for b in rig.data.bones:
        if b.use_deform:
            b_name = b.name.lower()
            if "head" in b_name:
                self.faceit_body_armature_head_bone = b.name
                break


def update_use_as_rigify_armature(self, context):
    if self.faceit_use_rigify_armature:
        if not self.faceit_armature:
            self.faceit_armature = self.faceit_body_armature
        self.faceit_show_warnings = False
        objects = get_faceit_objects_list()
        populate_bake_modifier_items(objects)
    else:
        if self.faceit_armature == self.faceit_body_armature:
            self.faceit_armature = None


def update_eye_bone_pivots(self, context):
    rig = self.faceit_pivot_ref_armature
    if not rig:
        return
    # Find the eye bones
    left_eye_bones = []
    right_eye_bones = []
    for b in rig.data.bones:
        if not b.use_deform:
            continue
        b_name = b.name.lower()
        if "eye" in b_name:
            if "left" in b_name or b_name.endswith("_l") or b_name.endswith(".l") or "_l_" in b_name:
                left_eye_bones.append(b.name)
            elif "right" in b_name or b_name.endswith("_r") or b_name.endswith(".r") or "_r_" in b_name:
                right_eye_bones.append(b.name)
    if left_eye_bones and right_eye_bones:
        self.faceit_eye_pivot_bone_L = min(left_eye_bones, key=len)
        self.faceit_eye_pivot_bone_R = min(right_eye_bones, key=len)
        update_eye_pivot_from_bone(self, context)


def update_eye_pivot_from_bone(self, context):
    if self.faceit_eye_pivot_bone_L:
        self.faceit_eye_pivot_point_L = copy_pivot_from_bone(
            self.faceit_pivot_ref_armature, self.faceit_eye_pivot_bone_L)
    else:
        self.faceit_eye_pivot_point_L = get_eye_pivot_from_landmarks(context)
    if self.faceit_eye_pivot_bone_R:
        self.faceit_eye_pivot_point_R = copy_pivot_from_bone(
            self.faceit_pivot_ref_armature, self.faceit_eye_pivot_bone_R)
    else:
        self.faceit_eye_pivot_point_R = get_eye_pivot_from_landmarks(context)


def update_eye_pivot_options(self, context):
    pass


def update_pivot_geo_type(self, context):
    if self.faceit_eye_geometry_type == 'SPHERE':
        update_right_pivot_from_vertex_group(self, context)
        update_left_pivot_from_vertex_group(self, context)
    else:
        if not self.faceit_pivot_ref_armature:
            self.faceit_pivot_ref_armature = self.faceit_body_armature
        update_eye_pivot_from_bone(self, context)


def update_left_pivot_from_vertex_group(self, context):
    if self.faceit_eye_pivot_group_L:
        self.faceit_eye_pivot_point_L = PivotManager.get_eye_pivot_from_vertex_group(vgroup_name=self.faceit_eye_pivot_group_L)


def update_right_pivot_from_vertex_group(self, context):
    if self.faceit_eye_pivot_group_R:
        self.faceit_eye_pivot_point_R = PivotManager.get_eye_pivot_from_vertex_group(vgroup_name=self.faceit_eye_pivot_group_R)


def update_pivot_placement_method(self, context):
    if self.faceit_eye_pivot_placement == 'AUTO':
        if self.faceit_eye_geometry_type == 'SPHERE':
            update_right_pivot_from_vertex_group(self, context)
            update_left_pivot_from_vertex_group(self, context)
        else:
            update_eye_pivot_from_bone(self, context)
    # if self.faceit_eye_pivot_placement == 'MANUAL':


def update_draw_pivots(self, context):
    if self.faceit_draw_pivot_locators:
        PivotManager.start_drawing(context)


def get_enum_vgroups(self, context):
    global vg_items
    vg_items = []
    vgroups = get_vertex_groups_from_objects()
    # for a in get_all_shape_key_actions():
    for vg in vgroups:
        vg_items.append((vg,) * 3)

    if not vg_items:
        vg_items.append(("None", "None", "None"))

    return vg_items


def register():
    Scene.faceit_armature = PointerProperty(
        name='Faceit Armature',
        description='The armature to be used in the binding and baking operators. Needs to be a Rigify layout.',
        type=Object,
        poll=faceit_armature_poll,
        update=update_faceit_armature,
    )
    Scene.faceit_armature_missing = BoolProperty(
        name='Missing Armature',
        description='The armature is missing. Did you remove it intentionally?',
    )
    Scene.faceit_body_armature = PointerProperty(
        name='Existing Rig',
        type=Object,
        poll=body_armature_poll,
        update=update_body_armature
    )
    Scene.faceit_body_armature_head_bone = StringProperty(
        name='Bone',
        default='',
    )
    Scene.faceit_use_rigify_armature = BoolProperty(
        name='Use Existing Rigify Face Rig', default=False,
        description='When active, you can choose a Rigify Armature from the active scene. You can either use the Faceit Armature OR a Rigify Armature for creating the expressions.',
        update=update_use_as_rigify_armature)
    Scene.faceit_is_rigify_armature = BoolProperty(
        name="Is Rigify Armature",
        default=False,
    )
    Scene.faceit_pivot_manager_initialized = BoolProperty(
        name='Pivot Manager Initialized',
        default=False,
    )
    Scene.faceit_eye_pivot_placement = EnumProperty(
        name='Eye Pivot Placement Method',
        items=[('AUTO', 'Auto Find',
                'The pivot locator will be placed automatically, based on assigned vertex groups or existing eye bones.'),
               ('MANUAL', 'Manual', 'The pivot locator will be placed manually, using empties.'), ],
        default='AUTO', update=update_pivot_placement_method,)
    Scene.faceit_eye_geometry_type = EnumProperty(
        name='Geometry Type',
        items=[
            ('SPHERE', 'Spherical', 'The eye geometry is a  sphere or half sphere.'),
            ('FLAT', 'Flat', 'The eye geometry is flat. Typical in anime characters.'),
        ],
        default=0,
        update=update_pivot_geo_type,
    )
    Scene.faceit_pivot_vertex_auto_snap = BoolProperty(
        name='Auto Snap',
        default=True,
        description='When enabled, the snap settings will be disabled automatically when selecting the pivot vertex and re-enabled upon selecting other vertices. Currently this setting does not respect user preferences.',
    )
    Scene.faceit_draw_pivot_locators = BoolProperty(
        name='Draw Pivot Locators',
        default=True,
        description='Draw the pivot locators in the viewport.',
        update=update_draw_pivots
    )
    Scene.faceit_pivot_ref_armature = PointerProperty(
        name='Pivot Reference Armature',
        type=Object,
        poll=faceit_armature_poll,
        update=update_eye_bone_pivots
    )
    Scene.faceit_eye_pivot_group_L = StringProperty(
        name='Left Eye Geometry',
        update=update_left_pivot_from_vertex_group
    )
    Scene.faceit_eye_pivot_group_R = StringProperty(
        name='Left Eye Geometry',
        update=update_right_pivot_from_vertex_group
    )
    Scene.faceit_eye_pivot_point_L = FloatVectorProperty(
        name='Eye Pivot Point Left',
        default=(0, 0, 0),
        subtype='XYZ',
        size=3,
        update=update_eye_pivot_options,
    )
    Scene.faceit_eye_pivot_point_R = FloatVectorProperty(
        name='Eye Pivot Point Right',
        default=(0, 0, 0),
        subtype='XYZ',
        size=3,
        update=update_eye_pivot_options,
    )
    Scene.faceit_eye_manual_pivot_point_L = FloatVectorProperty(
        name='Eye Pivot Point Left',
        default=(0, 0, 0),
        subtype='XYZ',
        size=3,
        update=update_eye_pivot_options,
    )
    Scene.faceit_eye_manual_pivot_point_R = FloatVectorProperty(
        name='Eye Pivot Point Right',
        default=(0, 0, 0),
        subtype='XYZ',
        size=3,
        update=update_eye_pivot_options,
    )
    Scene.faceit_eye_pivot_bone_L = StringProperty(
        name="Left Eye Bone",
        description="The left eye bone of the anime character.",
        default="",
        update=update_eye_pivot_from_bone,
    )
    Scene.faceit_eye_pivot_bone_R = StringProperty(
        name="Right Eye Bone",
        description="The right eye bone of the anime character.",
        default="",
        update=update_eye_pivot_from_bone,
    )
    Scene.faceit_jaw_pivot = FloatVectorProperty(
        name='Jaw Pivot',
        default=(0, 0, 0),
        subtype='XYZ',
        size=3,
    )
    Scene.faceit_use_jaw_pivot = BoolProperty(
        name='Use Jaw Pivot',
        default=False,
    )


def unregister():
    del Scene.faceit_armature
    del Scene.faceit_body_armature_head_bone
    del Scene.faceit_eye_pivot_bone_L
    del Scene.faceit_eye_pivot_bone_R
    del Scene.faceit_use_rigify_armature
    del Scene.faceit_is_rigify_armature
