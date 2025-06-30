import bpy
from .. import __package__ as base_package
from ..icons.icons import preview_collections
from ..camera import update_settings
from ..operators import world as wd
from ..constants import DEFAULT_COLOR_TEMPERATURE, DEFAULT_TINT
from ..ui import library
from bpy.types import PropertyGroup
from bpy.props import (BoolProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       IntProperty,
                       StringProperty,
                       PointerProperty,
                       )

# CAMERAS = []
# main_cameraS = [('NONE','','')]

def update_comp_exposure(self,context):
    if self.comp_exposure:
        bpy.ops.photographer.add_exposure_node()
    else:
        bpy.ops.photographer.disable_exposure_node()

def update_comp_wb(self,context):
    if self.comp_wb:
        bpy.ops.photographer.add_wb_node()
    else:
        bpy.ops.photographer.disable_wb_node()

def update_active_camera_index(self, context):
	context.scene.photographer.active_camera_index = -1

# def update_active_light_index(self, context):
# 	context.scene.photographer.active_light_index = -1

def update_main_camera(self,context):
    cam = context.scene.camera
    if cam:
        settings = cam.data.photographer
        update_settings(settings,context)

def update_resize_mode(self,context):
    self.resize_resolution_x = context.scene.render.resolution_x
    self.resize_resolution_y = context.scene.render.resolution_y
    self.resize_offset_x = 0
    self.resize_offset_y = 0
    self.resize_offset_longedge = 0

class SceneSettings(PropertyGroup):
    comp_exposure : BoolProperty(
        name = "Apply at Compositing",
        description = ("Apply Exposure during Compositing. \nExposure won't be "
                        "visible in viewport if Viewport Compositing is disabled, but will be applied to EXR files"),
        default = False,
        options = {'HIDDEN'},
        update = update_comp_exposure,
    )
    comp_wb : BoolProperty(
        name = "Apply at Compositing",
        description = ("Apply White Balance during Compositing. \n"
                       "White Balance won't be visible in viewport if Viewport Compositing is disabled, but will be applied to EXR files. \n"
                       "Currently Not available if using Blender 4.3 White Balance in the Addon Preferences"),
        default = False,
        options = {'HIDDEN'},
        update = update_comp_wb,
    )
    main_camera : PointerProperty(
        name="Photographer Main Camera",
        type=bpy.types.Camera,
        update = update_main_camera,
    )
    active_view_layer_index: IntProperty(
        default=-1,
    )
    cam_list_sorting : EnumProperty(
        name = "Sort by Camera or Collection",
        items = [('ALPHA','Sort Alphabetically','','CAMERA_DATA',0),
                ('COLLECTION','Group by Collection','','OUTLINER_OB_GROUP_INSTANCE',1)],
        options = {'HIDDEN'},
        # default = bpy.context.preferences.addons[base_package].preferences.default_cam_list_sorting,
    )
    cycle_renderable_only : BoolProperty(
        name = "Cycle through Renderable Cameras only",
        description = (""),
        default = True,
        options = {'HIDDEN'},
    )
    active_camera_index: IntProperty(
        default=-1,
        # update=update_active_camera_index,
    )
    active_camera_collection_index: IntProperty(default=-1,
        # update=update_active_light_index,
    )
    # active_scene_camera: EnumProperty(
    #     name="Scene Camera",
    #     items = camera_items,
    #     options = {'HIDDEN'},
    #     get = get_active_scene_camera,
    #     set = set_active_scene_camera,
    #     # update = update_active_scene_camera,
    # )
    list_filter : StringProperty(
        name="Filter",
        description="Filter by name",
    )
    list_filter_reverse : BoolProperty(
        name="Reverse Order",
        description="Reverse Sorting order",
        default = False,
    )
    renderable_only : BoolProperty(
        name="Renderable Only",
        description="Hide Cameras that are not Renderable",
        default = False,
    )
    hide_excluded : BoolProperty(
        name="Hide Excluded",
        description="Hide Cameras and Collections that are excluded from the current View Layer",
        default = False,
    )
    use_filter_invert : BoolProperty(
        name="Invert",
        description="Invert filtering (show hidden items, and vice versa)",
        default = False,
    )   
    scene_collection_expand : BoolProperty(
        default = True
    )
    resize_resolution_x : bpy.props.IntProperty(
        name = "X", description = "New Horizontal Resolution after Resize",
        default = 1920, min = 0, subtype = 'PIXEL',
        options = {'HIDDEN'},
    )
    resize_resolution_y : bpy.props.IntProperty(
        name = "Y", description = "New Vertical Resolution after Resize",
        min = 0, default = 1080, subtype='PIXEL',
        options = {'HIDDEN'},
    )
    resize_longedge : bpy.props.IntProperty(
        name = "Long Edge", description = "New Long Edge Resolution after Resize",
        default = 1920, min = 0, subtype = 'PIXEL',
        options = {'HIDDEN'},
    )
    resize_offset_x : bpy.props.IntProperty(
        name = "Offset X", description = "Resize Offset X added to current Resolution X",
        default = 0, subtype = 'PIXEL',
        options = {'HIDDEN'},
    )
    resize_offset_y : bpy.props.IntProperty(
        name = "Offset Y", description = "Resize Offset Y added to current Resolution Y",
        default = 0, subtype = 'PIXEL',
        options = {'HIDDEN'},
    )
    resize_offset_longedge : bpy.props.IntProperty(
        name = "Offset Long Edge", description = "Resize Offset added to current Resolution Long Edge",
        default = 0, subtype = 'PIXEL',
        options = {'HIDDEN'},
    )
    resize_pixel_percent_x : bpy.props.FloatProperty(
        name = "Pixel Percentage X", description = "Multiplies Resolution X with Pixel Percentage X to define new Resolution",
        default = 100, subtype = 'PERCENTAGE',
        options = {'HIDDEN'},
    )
    resize_pixel_percent_y : bpy.props.FloatProperty(
        name = "Pixel Percentage Y", description = "Multiplies Resolution Y with Pixel Percentage Y to define new Resolution",
        default = 100, subtype = 'PERCENTAGE',
        options = {'HIDDEN'},
    )
    resize_pixel_percent_longedge : bpy.props.FloatProperty(
        name = "Pixel Percentage Long Edge", description = "Multiplies Long Edge Resolution with Pixel Percentage to define new Resolution",
        default = 100, subtype = 'PERCENTAGE',
        options = {'HIDDEN'},
    )
    resize_mode : bpy.props.EnumProperty(
        name = "Resize Mode", description = "Defines what unit to use to Resize Canvas",
        items = [('PIXEL','Pixels','','',0),
                 ('PIXEL_OFFSET','Pixels Offset','','',1),
                #  ('PIXEL_PERCENT','Pixels Percentage','','',2),
                 ],
        options = {'HIDDEN'},
        update = update_resize_mode,
    )
    resize_anchor : bpy.props.EnumProperty(
        name = "Resize Anchor", description = "Anchor used to define in which direction the canvas will be resized",
        items = [('TOP_LEFT','Top Left','','',0),
                 ('LEFT','Left','','',1),
                 ('BOTTOM_LEFT','Bottom Left','','',2),
                 ('TOP','Top','','',3),
                 ('CENTER','Center','','',4),
                 ('BOTTOM','Bottom','','',5),
                 ('TOP_RIGHT','Top Right','','',6),
                 ('RIGHT','Right','','',7),
                 ('BOTTOM_RIGHT','Bottom Right','','',8),
                 ],
        default = 'CENTER',
        options = {'HIDDEN'},
    )
    resize_stored_anchor : bpy.props.StringProperty()
    is_sticky_menu_open : bpy.props.BoolProperty()

class LightMixerSceneSettings(PropertyGroup):
    solo_active: BoolProperty(
        name="Solo",
        default=False,
        options = {'HIDDEN'},
    )
    world_show_more: BoolProperty(
        name="Expand World settings",
        default=True,
        options = {'HIDDEN'},
    )
    show_active_light : BoolProperty(
        name="Active Light properties",
        default=True,
    )

    hdri_tex: EnumProperty(
        name="HDRI Texture",
        items=wd.enum_previews_hdri_tex,
        update=wd.update_hdri_tex,
        default=-1,
    )
    hdri_category: EnumProperty(
        name="HDRI Category",
        items=library.hdri_subfolders_return,
        description="HDRI Subfolder category - Only 1 subfolder level is supported",
        update=wd.update_hdri_category,
    )

    ### Moved to World Settings ###
    # hdri_rotation: FloatProperty(
    #     name="Rotation",
    #     default=0, soft_min=-3.141593, soft_max=3.141593, unit='ROTATION',
    #     precision=2,
    #     get=wd.get_hdri_rotation,
    #     set=wd.set_hdri_rotation,
    # )
    # hdri_use_temperature: BoolProperty(
    #     name="Use Color Temperature",
    #     default=True,
    #     options = {'HIDDEN'},
    #     update = wd.update_hdri_use_temperature,
    # )
    # hdri_temperature: FloatProperty(
    #     name="Temperature",
    #     default=DEFAULT_COLOR_TEMPERATURE, min=0, soft_min=1100, soft_max=13000,
    #     get=wd.get_hdri_temperature,
    #     set=wd.set_hdri_temperature,
    # )
    # hdri_tint: FloatProperty(
    #     name="Tint",
    #     default=DEFAULT_TINT, min=-100, max=100,
    #     get=wd.get_hdri_tint,
    #     set=wd.set_hdri_tint,
    # )
    # hdri_color: FloatVectorProperty(
    #     name="Color Multiplier",
    #     subtype='COLOR',
    #     min=0.0, max=1.0, size=4,
    #     default=(1.0,1.0,1.0,1.0),
    #     get=wd.get_hdri_color,
    #     set=wd.set_hdri_color,
    # )
    # hdri_blur: FloatProperty(
    #     name="Blur",
    #     default=0, min=0, soft_max=1,
    #     get=wd.get_hdri_blur,
    #     set=wd.set_hdri_blur,
    # )
    light_list_sorting : EnumProperty(
        name = "Sort by Light, Collection or Light Group",
        items = [('ALPHA','Sort Alphabetically','','LIGHT_DATA',0),
                ('COLLECTION','Group by Collection','','OUTLINER_OB_GROUP_INSTANCE',1),
                ('LIGHTGROUP','Group by Light Group','','OUTLINER_OB_LIGHT',2),
                ],
        options = {'HIDDEN'},
    )
    active_light_index: IntProperty(
        default=-1,
        # update=update_active_light_index,
    )
    active_light_collection_index: IntProperty(default=-1,
        # update=update_active_light_index,
    )
    active_lightgroup_index: IntProperty(default=-1,
        # update=update_active_light_index,
    )
    list_filter : StringProperty(
        name="Filter",
        description="Filter by name",
    )
    list_filter_reverse : BoolProperty(
        name="Reverse Order",
        description="Reverse Sorting order",
        default = False,
    )
    use_filter_invert : BoolProperty(
        name="Invert",
        description="Invert filtering (show hidden items, and vice versa)",
        default = False,
    )
    group_linked_data : BoolProperty(
        name="Group Linked Lights",
        description="Group Lights that are sharing the same Data",
        default = False,
    )
    scene_collection_expand : BoolProperty(
        default = True
    )
    light_name_width : FloatProperty(
        name = "Width",
        default = 9 , min = 0.5
    )    
    emissive_name_width : FloatProperty(
        name = "Width",
        default = 9 , min = 0.5
    )    
    active_emissive_index: IntProperty(default=-1,
        # update=update_active_light_index,
    )
    emissive_list_filter : StringProperty(
        name="Filter",
        description="Filter by name",
    )
    emissive_list_filter_reverse : BoolProperty(
        name="Reverse Order",
        description="Reverse Sorting order",
        default = False,
    )
    emissive_use_filter_invert : BoolProperty(
        name="Invert",
        description="Invert filtering (show hidden items, and vice versa)",
        default = False,
    )
    emissive_list_sorting : EnumProperty(
        name = "Sort by Material, Collection or Light Group",
        items = [('ALPHA','Sort by Materials','','MATERIAL',0),
                ('LIGHTGROUP','Group by Light Group','','OUTLINER_OB_LIGHT',1),
                ],
        options = {'HIDDEN'},
    )   
