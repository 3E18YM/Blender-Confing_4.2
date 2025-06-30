# -*- coding:utf-8 -*-
from .iBlender_perspective_plotter import _z

# from email.policy import default
# import sys
# import traceback

import bpy

from bpy.types import PropertyGroup, CollectionProperty, StringProperty, PointerProperty, BoolProperty
from bpy.props import *
from bpy.utils import register_class, unregister_class
from mathutils import Vector

from . import operators, util


vp_type_items =(('X', 'X', ''),
                ('Y', 'Y', ''),
                ('Z', 'Z', ''),
                ('-X', '-X', ''),
                ('-Y', '-Y', ''),
                ('-Z', '-Z', ''))

class perspective_plotter_object(PropertyGroup):

    running_uuid : StringProperty()

    is_valid : BoolProperty(default=True)

    is_dirty : BoolProperty(default=True)

    def set_dirty(self, context):
        self.is_dirty = True

    vanishing_point_num : bpy.props.EnumProperty(items= (('1', '1', ''),
                                                     ('2', '2', ''),
                                                     ('3', '3', ''),),
                                                     name = _z("Number of Vanishing Points"), default='2', update=set_dirty, description = "Number of Vanishing Points")


    axis_vp1_point_a : FloatVectorProperty(default=[40, 50], size=2, update=set_dirty)
    axis_vp1_point_b : FloatVectorProperty(default=[20, 40], size=2, update=set_dirty)

    axis_vp1_point_c : FloatVectorProperty(default=[70, 35], size=2, update=set_dirty)
    axis_vp1_point_d : FloatVectorProperty(default=[50, 15], size=2, update=set_dirty)

    axis_vp2_point_a : FloatVectorProperty(default=[50, 55], size=2, update=set_dirty)
    axis_vp2_point_b : FloatVectorProperty(default=[30, 75], size=2, update=set_dirty)

    axis_vp2_point_c : FloatVectorProperty(default=[70, 70], size=2, update=set_dirty)
    axis_vp2_point_d : FloatVectorProperty(default=[45, 80], size=2, update=set_dirty)

    axis_vp3_point_a : FloatVectorProperty(default=[37, 29], size=2, update=set_dirty)
    axis_vp3_point_b : FloatVectorProperty(default=[32, 75], size=2, update=set_dirty)

    axis_vp3_point_c : FloatVectorProperty(default=[70, 75], size=2, update=set_dirty)
    axis_vp3_point_d : FloatVectorProperty(default=[65, 30], size=2, update=set_dirty)

    horizon_point_a : FloatVectorProperty(default=[25, 33], size=2, update=set_dirty)
    horizon_point_b : FloatVectorProperty(default=[75, 33], size=2, update=set_dirty)

    ref_distance_mode : bpy.props.EnumProperty(items= (('camera_distance', _z('Default'), "Default\nPosition the camera at a set distance from the origin"),
                                                     ('X', _z('Along X Axis'), "Along X Axis\nTake a reference measure along the X axis"),
                                                     ('Y', _z('Along Y Axis'), "Along Y Axis\nTake a reference measure along the Y axis"),
                                                     ('Z', _z('Along Z Axis'), "Along Z Axis\nTake a reference measure along the Z axis"),),
                                                     name = _z("Reference Distance"), default='camera_distance', update=set_dirty, description = "Reference Distance")
    ref_length : FloatProperty(
        name=_z("Reference Length"), 
        description="Reference Length\nLength used to determine the relative scale of the axis markers",
        default=1, 
        precision=4,
        min=0, 
        subtype='DISTANCE',
        update=set_dirty)

    is_manual_length_point : BoolProperty(
        name=_z("Edit measuring slides"),
        description="Edit measuring slides\nChange the measuring slide parameters from the panel.  Useful in case the measuring slides are outside the viewing border and cannot be grabbed",
        default=False,
        )

    length_point_a : FloatProperty(default=0.0, update=set_dirty, precision=5, step=5, name=_z("Measuring Point A"), description="Measuring Point A")
    length_point_b : FloatProperty(default=0.05, update=set_dirty, precision=5, step=5, name=_z("Measuring Point B"), description="Measuring Point B")

    vp_to_project_to : FloatVectorProperty(size=2)

    principal_point_mode : bpy.props.EnumProperty(items= (('midpoint', _z('Image Midpoint'), "Image Midpoint"),
                                                     ('manual', _z('Manual'), "Manual"),),
                                                     name = _z("Principal Point"), default='midpoint', update=set_dirty, description = "Principal Point")

    principal_point : FloatVectorProperty(default=[50 , 50], size=2, update=set_dirty)

    camera_distance :  FloatProperty(
        name=_z("Camera Distance"),
        description="Camera Distance\nCamera distance from the origin point",
        default=10, 
        min=0, 
        precision=4,
        subtype='DISTANCE',
        update=set_dirty)


    camera_origin_mode : bpy.props.EnumProperty(
        items= (('center', _z('World Center'), "World Center"),('manual', _z('Manual'), "Manual"),),
        name = _z("Camera Origin"), 
        description="Camera Origin\nThe position of the camera's target",
        default='center', 
        update=set_dirty)


    camera_rotation : FloatVectorProperty(
            name=_z("Camera Rotation"),
            description="Camera Rotation\nRotation of the camera from the origin point",
            subtype='EULER', update=set_dirty
            )

    camera_offset : FloatVectorProperty(
            name=_z("Camera Offset"),
            description="Camera Offset\nLocation of the origin point",
            subtype='TRANSLATION',
            default=[0,0,0], update=set_dirty
            )


    one_point_focal_length : FloatProperty(
        default=35.00, 
        name=_z('Focal Length'),
        description="Focal Length\nFocal Length value which is pre-calculated in 2 and 3 point perspective modes. In one-point perspective mode, this will provide further depth information to the camera",
        precision=4, 
        subtype="DISTANCE_CAMERA", 
        min=10,
        max=200, update=set_dirty)

    is_camera_sync : BoolProperty(
        name=_z("Sync Camera"),
        description="Sync Camera\nSynchronise Camera with Guides",
        default=True, update=set_dirty
    )

    disable_control_points : BoolProperty(
        name=_z("Disable Control Points"),
        description="Disable Control Points\nDisable the movement of control points",
        default=False, update=set_dirty
    )

    vp_1_type : bpy.props.EnumProperty(
        items= vp_type_items, 
        name = _z("Vanishing Point 1 Axis"), 
        description="Vanishing Point 1 Axis\nOrientation of first vanishing point. The third vanishing point is calculated based on the first two vanishing points",
        default='X', update=set_dirty)

    vp_2_type : bpy.props.EnumProperty(
        items= vp_type_items, 
        name = _z("Vanishing Point 2 Axis"), 
        description="Vanishing Point 2 Axis\nOrientation of second vanishing point. The third vanishing point is calculated based on the first two vanishing points",
        default='Y', update=set_dirty)

    grid_point : FloatVectorProperty(default=[50 , 53], size=2, update=set_dirty)
    
    def update_redraw(self, context):
        for area in context.screen.areas:
            area.tag_redraw()

    error_message : StringProperty(default="", update=update_redraw)


class perspective_plotter_visualisation(PropertyGroup):
    # these properties are used to handle visualisation and are calculated.
    vp_1 : FloatVectorProperty(size=2)
    vp_2 : FloatVectorProperty(size=2)
    vp_3 : FloatVectorProperty(size=2)
    horizon_vec : FloatVectorProperty(size=2)
    principal_point : FloatVectorProperty(size=2)
    grid_point : FloatVectorProperty(size=2)
    length_point_a : FloatVectorProperty(size=2, default=[-1 , -1])
    length_point_b : FloatVectorProperty(size=2, default=[-1 , -1])
    vp_to_project_to : FloatVectorProperty(size=2)

classes = [
    perspective_plotter_object,perspective_plotter_visualisation]


def register():
    for cls in classes:
        register_class(cls)

    bpy.types.Object.perspective_plotter = PointerProperty(name=_z('Perspective Plotter Object'), type=perspective_plotter_object, description = 'Perspective Plotter Object')
    bpy.types.Object.perspective_plotter_visualisation = PointerProperty(name=_z('Perspective Plotter Visualisation Object'), type=perspective_plotter_visualisation, description = 'Perspective Plotter Visualisation Object')


def unregister():
    del bpy.types.Object.perspective_plotter_visualisation
    del bpy.types.Object.perspective_plotter

    for cls in classes:
        unregister_class(cls)
