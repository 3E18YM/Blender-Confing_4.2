import bpy
from .. import render_queue, view_layer
from . import (camera_list,
               emissive_mixer,
               post_effects_panel,
               lightmixer_panel,
               world_mixer,
               camera_panel,
               lens_panel,
               bookmarks,
               resolution_panel,
)

photographer_panel_classes = [
    camera_list.PHOTOGRAPHER_PT_ViewPanel_CameraList,
    camera_list.PHOTOGRAPHER_UL_ViewPanel_CameraList,
    camera_list.PHOTOGRAPHER_UL_ViewPanel_CameraCollectionsList,
    camera_panel.PHOTOGRAPHER_PT_ViewPanel_Camera,

    bookmarks.PHOTOGRAPHER_PT_ViewPanel_Bookmarks,

    lens_panel.PHOTOGRAPHER_PT_ViewPanel_Lens,

    camera_panel.PHOTOGRAPHER_PT_ViewPanel_DOF,
    camera_panel.PHOTOGRAPHER_PT_ViewPanel_Focus,
    camera_panel.PHOTOGRAPHER_PT_ViewPanel_Autofocus,

    post_effects_panel.PHOTOGRAPHER_PT_ViewPanel_LensEffects,
    post_effects_panel.PHOTOGRAPHER_PT_ImageEditor_LensEffects,
    post_effects_panel.PHOTOGRAPHER_PT_NodeEditor_LensEffects,

    camera_panel.PHOTOGRAPHER_PT_ViewPanel_Exposure,
    camera_panel.PHOTOGRAPHER_PT_ImageEditor_Exposure,
    camera_panel.PHOTOGRAPHER_PT_NodeEditor_Exposure,
    
    camera_panel.PHOTOGRAPHER_PT_ViewPanel_WhiteBalance,
    camera_panel.PHOTOGRAPHER_PT_ImageEditor_WhiteBalance,
    camera_panel.PHOTOGRAPHER_PT_NodeEditor_WhiteBalance,

    resolution_panel.PHOTOGRAPHER_PT_ViewPanel_Resolution,
    resolution_panel.PHOTOGRAPHER_PT_ImageEditor_Resolution,
    resolution_panel.PHOTOGRAPHER_PT_NodeEditor_Resolution,
    resolution_panel.PHOTOGRAPHER_PT_ViewPanel_ResizeCanvas,

    render_queue.PHOTOGRAPHER_PT_ViewPanel_RenderQueue,
    render_queue.PHOTOGRAPHER_PT_ImageEditor_RenderQueue,
    render_queue.PHOTOGRAPHER_PT_NodeEditor_RenderQueue,

    view_layer.PHOTOGRAPHER_PT_ViewPanel_ViewLayer,
    view_layer.PHOTOGRAPHER_PT_NodeEditor_ViewLayer,
]

lightmixer_panel_classes = [
    lightmixer_panel.LIGHTMIXER_PT_ViewPanel,
    lightmixer_panel.LIGHTMIXER_PT_NodeEditor_ViewPanel,
    lightmixer_panel.LIGHTMIXER_PT_PropertiesSubPanel,
    lightmixer_panel.LIGHTMIXER_PT_PropertiesRaysSubPanel,
    emissive_mixer.LIGHTMIXER_PT_EmissiveViewPanel,
    world_mixer.LIGHTMIXER_PT_WorldViewPanel,
    world_mixer.LIGHTMIXER_PT_WorldProperties,
    lightmixer_panel.PHOTOGRAPHER_UL_ViewPanel_LightList,
    lightmixer_panel.PHOTOGRAPHER_UL_ViewPanel_LightCollectionsList,
    lightmixer_panel.PHOTOGRAPHER_UL_ViewPanel_LightGroupsList,
    emissive_mixer.PHOTOGRAPHER_UL_ViewPanel_EmissiveMaterialsList,
    emissive_mixer.PHOTOGRAPHER_UL_ViewPanel_EmissiveLightGroupsList,
]
if bpy.app.version < (4, 1, 0):
    lightmixer_panel_classes.append(world_mixer.LIGHTMIXER_PT_WorldViewPanel_HDRIGround)
    lightmixer_panel_classes.append(world_mixer.LIGHTMIXER_PT_WorldProperties_HDRIGround)