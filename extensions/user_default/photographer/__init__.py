bl_info = {
    "name": "Photographer",
    "description": "Adds Physical Camera and Physical Light controls, LightMixer and Render Queue",
    "author": "Fabien 'chafouin' Christin, @fabienchristin",
    "version": (5, 5, 3),
    "blender": (3, 0, 0),
    "location": "View3D > Side Panel > Photographer",
    "support": "COMMUNITY",
    "category": "Camera"}

addon_version = (5, 5, 3)

import bpy
from bpy.props import PointerProperty, CollectionProperty

from . import (
    prefs,
    camera,
    camera_presets,
    presets_install,
    view_layer,
    light_presets,
    handler,
    render_queue,
    driver_functions,
)
from .ui import (
    camera_panel,
    bookmarks,
    post_effects_panel,
    lens_panel,
    light_panel,
    physical_light_add,
    physical_camera_add,
    library,
    focus_plane,
    composition_guides_menu,
    resolution_panel,
    scene_panel,
    sticky_menu,
    pie_camera,
)
from .ui import bokeh as bokeh_ui
from .ui.panel_classes import photographer_panel_classes, lightmixer_panel_classes
from .properties import light, scene, material, node, object, post_effects
from .properties import world as world_props
from .operators import (
    auto_exposure,
    autofocus,
    bokeh,
    camera_ops,
    lens,
    light_material,
    sampling_threshold,
    select,
    target,
    stop_adj,
    expand_ui,
    emissive,
    updater,
    exposure,
    ui,
    resolution,
    white_balance,
    world,
    lightgroup,
)

from .icons import icons
from .operators import lightmixer as lightmixer_ops
from .rigs import build_rigs

classes = [
    # Properties
    camera.PhotographerCameraSettings,
    post_effects.PostEffectsSettings,
    light.PhotographerLightSettings,
    bookmarks.PhotographerBookmarksSettings,

    # LightMixer Object
    object.LightMixerObjectSettings,

    # LightMixer Material
    material.LightMixerMaterialSettings,
    node.LightMixerNodeSettings,

    # Scene Properties
    scene.SceneSettings,
    scene.LightMixerSceneSettings,

    # World Properties
    world_props.LightMixerWorldSettings,

    # Preferences
    prefs.AddonPreferences,
    prefs.PHOTOGRAPHER_OT_Hotkey_Add_Camera_Pie_Menu,
    prefs.PHOTOGRAPHER_OT_Hotkey_Add_Camera_Sticky_Menu,
    prefs.PHOTOGRAPHER_OT_Hotkey_Add_HDRI_Rotation_Drag,
    prefs.PHOTOGRAPHER_OT_Update_All_Lights_Energy,

    # Operators
    lens.PHOTOGRAPHER_OT_DollyZoom,
    lens.PHOTOGRAPHER_OT_DollyZoom_Set_Key,
    lens.PHOTOGRAPHER_OT_PostEffects_Add,

    light_material.PHOTOGRAPHER_OT_Light_Textures_Add,
    light_material.PHOTOGRAPHER_OT_Reset_Intensity,
    light_material.PHOTOGRAPHER_OT_Refresh_Gobo_Categories,
    light_material.PHOTOGRAPHER_OT_Refresh_IES_Categories,

    select.PHOTOGRAPHER_OT_Select,
    select.PHOTOGRAPHER_OT_SelectCollection,
    select.PHOTOGRAPHER_OT_SelectEmissive,
    select.PHOTOGRAPHER_OT_SelectLightgroup,
    select.PHOTOGRAPHER_OT_SelectEmissiveLightgroup,

    # stop_adj.PHOTOGRAPHER_OT_LightStop_Adj,
    stop_adj.PHOTOGRAPHER_OT_LightMixerStop_Adj,
    stop_adj.PHOTOGRAPHER_OT_EmissiveStop_Adj,

    target.PHOTOGRAPHER_OT_TargetAdd,
    target.PHOTOGRAPHER_OT_TargetDelete,
    target.PHOTOGRAPHER_OT_TargetRefreshNames,

    expand_ui.PHOTOGRAPHER_OT_CollectionExpand,
    expand_ui.PHOTOGRAPHER_OT_LightgroupExpand,
    expand_ui.LIGHTMIXER_OT_ShowMore,

    ui.PHOTOGRAPHER_OT_ButtonStringClear,
    ui.PHOTOGRAPHER_OT_ButtonEnumClear,

    lightgroup.LIGHTMIXER_OT_AddLightgroup,
    lightgroup.LIGHTMIXER_OT_AddToLightgroup,
    lightgroup.LIGHTMIXER_OT_AddLightgroupsFromCollections,
    lightgroup.LIGHTMIXER_OT_RemoveFromLightgroup,
    lightgroup.LIGHTMIXER_OT_DeleteLightgroup,
    lightgroup.LIGHTMIXER_OT_EnableLightgroup,
    lightgroup.LIGHTMIXER_OT_EnableEmissiveLightgroup,
    lightgroup.LIGHTMIXER_OT_AddLightgroupCompGraph,

    # Camera Operators
    camera.PHOTOGRAPHER_OT_MakeCamActive,
    camera.PHOTOGRAPHER_OT_ApplyPhotographerSettings,
    camera.PHOTOGRAPHER_OT_SelectActiveCam,
    camera.PHOTOGRAPHER_OT_SetShutterAngle,
    camera.PHOTOGRAPHER_OT_SetShutterSpeed,
    camera.PHOTOGRAPHER_OT_RenderMotionBlur,
    lens.PHOTOGRAPHER_OT_AutoLensShift,
    white_balance.PHOTOGRAPHER_OT_WBReset,
    white_balance.PHOTOGRAPHER_OT_WBPicker,
    white_balance.PHOTOGRAPHER_OT_AddWhiteBalanceNode,
    white_balance.PHOTOGRAPHER_OT_DisableWhiteBalanceNode,
    white_balance.PHOTOGRAPHER_OT_ApplyColorTemperatureMode,
    autofocus.PHOTOGRAPHER_OT_FocusSingle,
    autofocus.PHOTOGRAPHER_OT_FocusTracking,
    autofocus.PHOTOGRAPHER_OT_FocusTracking_Cancel,
    autofocus.PHOTOGRAPHER_OT_Bake_Autofocus,
    autofocus.PHOTOGRAPHER_OT_CreateFocusPlane,
    autofocus.PHOTOGRAPHER_OT_DeleteFocusPlane,
    autofocus.PHOTOGRAPHER_OT_LensSim_SetFocusDistanceMode,
    camera_ops.PHOTOGRAPHER_OT_LookThrough,
    camera_ops.PHOTOGRAPHER_OT_SwitchCamera,
    camera_ops.PHOTOGRAPHER_OT_CycleCamera,
    camera_ops.PHOTOGRAPHER_OT_AddDroneCamera,
    camera_ops.PHOTOGRAPHER_OT_AddCamera,
    camera_ops.PHOTOGRAPHER_OT_DeleteCamera,
    camera_ops.PHOTOGRAPHER_OT_DuplicateCamera,
    camera_ops.PHOTOGRAPHER_OT_SetDroneCameraKey,
    camera_ops.PHOTOGRAPHER_OT_SetPassePartout_Full,
    camera_ops.PHOTOGRAPHER_OT_SetMainCamera,
    camera_ops.PHOTOGRAPHER_OT_SetViewportShading,
    camera_ops.PHOTOGRAPHER_OT_ResetCameraScale,

    # Bokeh
    bokeh.PHOTOGRAPHER_OT_Bokeh_Add,
    bokeh.PHOTOGRAPHER_OT_Bokeh_Delete,
    bokeh.PHOTOGRAPHER_OT_OptVignetting_Add,
    bokeh.PHOTOGRAPHER_OT_OptVignetting_Delete,
    bokeh.PHOTOGRAPHER_OT_FixDisplayType,

    # Photographer Presets
    camera_presets.PHOTOGRAPHER_MT_CameraPresets,
    camera_presets.PHOTOGRAPHER_OT_AddCameraPreset,
    camera_presets.PHOTOGRAPHER_PT_CameraPresets,
    camera_presets.PHOTOGRAPHER_MT_LensPresets,
    camera_presets.PHOTOGRAPHER_OT_AddLensPreset,
    camera_presets.PHOTOGRAPHER_PT_LensPresets,
    camera_presets.PHOTOGRAPHER_MT_LensEffectsPresets,
    camera_presets.PHOTOGRAPHER_OT_AddLensEffectsPreset,
    camera_presets.PHOTOGRAPHER_PT_LensEffectsPresets,
    camera_presets.PHOTOGRAPHER_MT_ExposurePresets,
    camera_presets.PHOTOGRAPHER_OT_AddExposurePreset,
    camera_presets.PHOTOGRAPHER_PT_ExposurePresets,
    camera_presets.PHOTOGRAPHER_MT_ResolutionPresets,
    camera_presets.PHOTOGRAPHER_OT_AddResolutionPreset,
    camera_presets.PHOTOGRAPHER_PT_ResolutionPresets,

    # Camera UI
    camera_panel.PHOTOGRAPHER_PT_Panel,
    camera_panel.PHOTOGRAPHER_PT_Panel_Exposure,
    camera_panel.PHOTOGRAPHER_PT_Panel_WhiteBalance,
    camera_panel.PHOTOGRAPHER_PT_Panel_Autofocus,
    post_effects_panel.PHOTOGRAPHER_PT_Panel_LensEffects,
    camera_panel.PHOTOGRAPHER_OT_ChangeLuxCoreDevice,
    camera_panel.PHOTOGRAPHER_OT_EEVEE_DisableSoftShadows,

    # DOF UI
    bokeh_ui.DATA_PT_PG_camera_dof_aperture,
    bokeh_ui.CYCLES_CAMERA_PT_PG_dof_aperture,    

    # Resolution UI
    resolution_panel.PHOTOGRAPHER_PT_Panel_Resolution,
    resolution_panel.PHOTOGRAPHER_PT_Panel_ResizeCanvas,

    # Camera Scene Camera Tools menu
    sticky_menu.PHOTOGRAPHER_OT_Sticky_Menu,

    # Camera PIE
    pie_camera.PHOTOGRAPHER_MT_Pie_Camera,

    # Light Presets
    light_presets.PHOTOGRAPHER_PT_PhysicalLightPointPresets,
    light_presets.PHOTOGRAPHER_PT_PhysicalLightSunPresets,
    light_presets.PHOTOGRAPHER_PT_PhysicalLightSpotPresets,
    light_presets.PHOTOGRAPHER_PT_PhysicalLightAreaPresets,
    light_presets.PHOTOGRAPHER_OT_AddPointPreset,
    light_presets.PHOTOGRAPHER_OT_AddSunPreset,
    light_presets.PHOTOGRAPHER_OT_AddSpotPreset,
    light_presets.PHOTOGRAPHER_OT_AddAreaPreset,
    light_presets.PHOTOGRAPHER_MT_PhysicalLightPointPresets,
    light_presets.PHOTOGRAPHER_MT_PhysicalLightSunPresets,
    light_presets.PHOTOGRAPHER_MT_PhysicalLightSpotPresets,
    light_presets.PHOTOGRAPHER_MT_PhysicalLightAreaPresets,

    # Light UI
    light_panel.PHOTOGRAPHER_PT_Panel_Light,
    light_panel.PHOTOGRAPHER_PT_beam_shape,
    light_panel.PHOTOGRAPHER_PT_EEVEE_light_shadow,
    light_panel.PHOTOGRAPHER_PT_EEVEE_light_influence,
    light_panel.PHOTOGRAPHER_PT_EEVEE_light_distance,
    light_panel.PHOTOGRAPHER_PT_spot,
    light_panel.PHOTOGRAPHER_OT_CalculateLightSize,
    light_panel.PHOTOGRAPHER_OT_CopySpotSize,
    light_panel.PHOTOGRAPHER_OT_SwitchColorMode,
    light_panel.PHOTOGRAPHER_OT_ApplyLightSettings,

    # Exposure
    exposure.PHOTOGRAPHER_OT_AddExposureNode,
    exposure.PHOTOGRAPHER_OT_DisableExposureNode,
    exposure.PHOTOGRAPHER_OT_EVPicker,
    exposure.PHOTOGRAPHER_OT_AddColorChart,

    # Resolution
    resolution.PHOTOGRAPHER_OT_FlipImage,
    resolution.PHOTOGRAPHER_OT_ResizeCanvas,
    resolution.PHOTOGRAPHER_OT_ResetResizeResolution,
    resolution.PHOTOGRAPHER_OT_SetResizeAnchor,
    resolution.PHOTOGRAPHER_OT_SetFixedSensorFit,
    resolution.PHOTOGRAPHER_OT_RevertResizeCanvas,


    # Light Mixer
    lightmixer_ops.LIGHTMIXER_OT_LightModal,
    lightmixer_ops.LIGHTMIXER_OT_Add,
    lightmixer_ops.LIGHTMIXER_OT_TargetAdd,
    lightmixer_ops.LIGHTMIXER_OT_Delete,
    lightmixer_ops.LIGHTMIXER_OT_Enable,
    lightmixer_ops.LIGHTMIXER_OT_RefreshHDRIPreview,

    # Emissive Mixer
    emissive.LIGHTMIXER_OT_ScanEmissive,
    emissive.LIGHTMIXER_OT_CreateEmissive,
    emissive.LIGHTMIXER_OT_AddEmissiveControls,
    emissive.LIGHTMIXER_OT_EmissiveEnable,
    emissive.LIGHTMIXER_OT_MaterialEnable,
    emissive.LIGHTMIXER_OT_AddBackfaceCullingNodes,
    emissive.LIGHTMIXER_OT_AssignEmissive,

    # Render UI
    sampling_threshold.PHOTOGRAPHER_OT_UpdateLightThreshold,

    # World
    world.LIGHTMIXER_OT_World_HDRI_Add,
    world.LIGHTMIXER_OT_Sky_Texture_Add,
    world.LIGHTMIXER_OT_WorldEnable,
    world.LIGHTMIXER_OT_World_AddControls,
    world.LIGHTMIXER_OT_World_AddHDRIGround,
    world.LIGHTMIXER_OT_World_DeleteHDRIGround,
    world.LIGHTMIXER_OT_Refresh_HDR_Categories,
    world.LIGHTMIXER_OT_Cycle_World,
    world.LIGHTMIXER_OT_Background_Color_Exposure_Compensate,
    world.LIGHTMIXER_OT_HDRI_Ground_Picker,
    world.LIGHTMIXER_OT_HDRI_Rotation_Drag,
    world.LIGHTMIXER_OT_World_Add,

    # Updater
    updater.PHOTOGRAPHER_OT_CheckForUpdate,

]

# 3D Header Autofocus buttons
af_header_buttons = (
    autofocus.focus_single_button,
    autofocus.focus_continuous_button,
    autofocus.focus_animate_button,
    autofocus.focus_tracking_button,
    autofocus.focus_distance_header,
)
cam_header_buttons = (
    camera.lock_camera_button,
)

def cycles_dof_aperture_poll(cls,context):
    pref = bpy.context.preferences.addons[__package__].preferences
    return (pref.show_default_camera_panels) and (context.camera) and (context.engine in {'CYCLES'})

def dof_aperture_poll(cls,context):
    pref = bpy.context.preferences.addons[__package__].preferences
    return (pref.show_default_camera_panels) and (context.camera) and (context.engine in {'BLENDER_EEVEE', 'BLENDER_EEVEE_NEXT', 'BLENDER_WORKBENCH'})

def eevee_light_panel_poll(cls,context):
    pref = bpy.context.preferences.addons[__package__].preferences
    return (pref.show_default_light_panels or not pref.use_physical_lights) and (context.light) and (context.engine in {'BLENDER_EEVEE','BLENDER_EEVEE_NEXT'})

def eevee_light_distance_poll(cls,context):
    pref = bpy.context.preferences.addons[__package__].preferences
    return (pref.show_default_light_panels or not pref.use_physical_lights) and (context.light and context.light.type != 'SUN')  and (context.engine in {'BLENDER_EEVEE','BLENDER_EEVEE_NEXT'})

def spot_panel_poll(cls,context):
    pref = bpy.context.preferences.addons[__package__].preferences
    return (pref.show_default_light_panels or not pref.use_physical_lights) and (context.light and context.light.type == 'SPOT')  and (context.engine in {'BLENDER_RENDER', 'BLENDER_EEVEE','BLENDER_EEVEE_NEXT', 'BLENDER_WORKBENCH'})

def area_panel_poll(cls,context):
    pref = bpy.context.preferences.addons[__package__].preferences
    return (pref.show_default_light_panels or not pref.use_physical_lights) and (context.light and context.light.type == 'AREA')  and (context.engine in {'BLENDER_RENDER', 'BLENDER_WORKBENCH'})

def light_panel_poll(cls,context):
    pref = bpy.context.preferences.addons[__package__].preferences
    return (pref.show_default_light_panels or not pref.use_physical_lights) and (context.engine in {'BLENDER_RENDER', 'BLENDER_WORKBENCH'})

def cycles_light_panel_poll(cls,context):
    pref = bpy.context.preferences.addons[__package__].preferences
    return (pref.show_default_light_panels or not pref.use_physical_lights) and (context.light) and (context.engine in {'CYCLES'})

def cycles_spot_panel_poll(cls,context):
    pref = bpy.context.preferences.addons[__package__].preferences
    return (pref.show_default_light_panels or not pref.use_physical_lights) and (context.light and context.light.type == 'SPOT') and (context.engine in {'CYCLES'})

def cycles_beam_shape_panel_poll(cls,context):
    pref = bpy.context.preferences.addons[__package__].preferences
    return (pref.show_default_light_panels or not pref.use_physical_lights) and (context.light and context.light.type in {'SPOT', 'AREA'}) and (context.engine in {'CYCLES'})

def cycles_check(load=False):
    import addon_utils
    is_enabled,is_loaded = addon_utils.check('cycles')
    if not is_loaded:
        if load:
            print ('Photographer requires Cycles to operate, automatically enabling it...')
            success = addon_utils.enable('cycles', default_set=True)
            if success:
                print ('Cycles is now enabled.')
                return True
        else:
            return False
    else:
        return True

def luxcore_check():
    import addon_utils
    is_enabled,is_loaded = addon_utils.check('BlendLuxCore')
    if is_loaded:
        return True

def register():
    # Load Cycles if not enabled
    if cycles_check(True):
        from bpy.utils import register_class, unregister_class

        # Unregistering some Light panels so we can insert Photographer panels in the right place
        light_panels_class_names = [
            'DATA_PT_EEVEE_shadow',
            'DATA_PT_EEVEE_shadow_cascaded_shadow_map',
            'DATA_PT_EEVEE_shadow_contact',
            'DATA_PT_custom_props_light',
            'CYCLES_LIGHT_PT_nodes',
        ] 
        if bpy.app.version >= (2,93,0):
            light_panels_class_names.append('CYCLES_LIGHT_PT_beam_shape')
        else:
            light_panels_class_names.append('CYCLES_LIGHT_PT_spot')

        # Unregister Light Panels Classes
        light_panels_classes = []
        for class_name in light_panels_class_names:
            class_object = getattr(bpy.types, class_name, None)
            if class_object:
                light_panels_classes.append(class_object)
                unregister_class(class_object)

        # Registering Photographer classes
        for cls in (classes + photographer_panel_classes + lightmixer_panel_classes):
            register_class(cls)

        # Addin Photographer property groups
        bpy.types.Camera.photographer = PointerProperty(type=camera.PhotographerCameraSettings)
        bpy.types.Camera.post_effects = PointerProperty(type=post_effects.PostEffectsSettings)
        bpy.types.Light.photographer = PointerProperty(type=light.PhotographerLightSettings)
        bpy.types.Scene.lightmixer = PointerProperty(type=scene.LightMixerSceneSettings)
        bpy.types.World.lightmixer = PointerProperty(type=world_props.LightMixerWorldSettings)
        bpy.types.Scene.photographer = PointerProperty(type=scene.SceneSettings)
        bpy.types.Object.lightmixer = PointerProperty(type=object.LightMixerObjectSettings)
        bpy.types.Material.lightmixer = PointerProperty(type=material.LightMixerMaterialSettings)
        bpy.types.ShaderNodeBsdfPrincipled.lightmixer = PointerProperty(type=node.LightMixerNodeSettings)
        bpy.types.ShaderNodeEmission.lightmixer = PointerProperty(type=node.LightMixerNodeSettings)
        bpy.types.Camera.bookmarks = CollectionProperty(type=bookmarks.PhotographerBookmarksSettings)

        icons.register()
        handler.register()
        library.register()
        prefs.register()
        scene_panel.register()
        auto_exposure.register()
        presets_install.register()
        render_queue.register()
        driver_functions.register()
        physical_light_add.register()
        physical_camera_add.register()
        composition_guides_menu.register()
        build_rigs.register()
        view_layer.register()
        bookmarks.register()

        # Reset Updater
        bpy.context.preferences.addons[__package__].preferences.needs_update = ""
        # Pass current add-on version to Updater
        updater.addon_version = addon_version

        # Hiding Blender Light Panels using option in Photographer preferences
        class_poll_mapping = {
            'CYCLES_CAMERA_PT_dof_aperture': cycles_dof_aperture_poll,
            'DATA_PT_camera_dof_aperture': dof_aperture_poll,
            'DATA_PT_EEVEE_light': eevee_light_panel_poll,
            'DATA_PT_EEVEE_light_distance': eevee_light_distance_poll,
            'DATA_PT_spot': spot_panel_poll,
            'DATA_PT_area': area_panel_poll if bpy.app.version < (3, 5, 0) else None,
            'DATA_PT_light': light_panel_poll,
            'CYCLES_LIGHT_PT_light': cycles_light_panel_poll,
            'CYCLES_LIGHT_PT_beam_shape': cycles_beam_shape_panel_poll if bpy.app.version >= (2, 93, 0) else None,
            'CYCLES_LIGHT_PT_spot': cycles_spot_panel_poll if bpy.app.version < (2, 93, 0) else None,
        }

        # Set poll methods for each class
        for class_name, poll_func in class_poll_mapping.items():
            class_object = getattr(bpy.types, class_name, None)
            if class_object and poll_func:
                class_object.poll = classmethod(poll_func)

        # Adding Photographer panels to Blender UI
        if bpy.app.version < (4,3,0):
            bpy.types.RENDER_PT_eevee_shadows.append(sampling_threshold.light_threshold_button)
        bpy.types.DATA_PT_camera_dof.append(focus_plane.focus_plane_ui)
        bpy.types.DATA_PT_lens.append(lens_panel.lens_shift_ui)
        if bpy.app.version >= (4,3,0):
            bpy.types.CYCLES_RENDER_PT_sampling_lights.append(sampling_threshold.light_threshold_button)
        else:
            bpy.types.CYCLES_RENDER_PT_sampling_advanced.append(sampling_threshold.light_threshold_button)
        bpy.types.CYCLES_CAMERA_PT_dof.append(focus_plane.focus_plane_ui)

        # bpy.types.CYCLES_CAMERA_PT_dof_aperture.append(bokeh_ui.bokeh_ui)
        # bpy.types.DATA_PT_camera_dof_aperture.append(bokeh_ui.bokeh_ui)

        # Adding 3D view header buttons
        for button in af_header_buttons:
            bpy.types.VIEW3D_HT_header.append(button)

        for button in cam_header_buttons:
            bpy.types.VIEW3D_HT_header.append(button)

        # Re-registrering Blender Light panels after inserting Photographer panels
        for cls in light_panels_classes:
            register_class(cls)

    # Adding Photographer panels to LuxCore UI if enabled
    if luxcore_check():
        bpy.types.LUXCORE_CAMERA_PT_depth_of_field.append(bokeh_ui.bokeh_ui)



def revert_cycles_dof_aperture_poll(cls,context):
    return (context.camera) and (context.engine in {'CYCLES'})

def revert_dof_aperture_poll(cls,context):
    return (context.camera) and (context.engine in {'BLENDER_EEVEE', 'BLENDER_EEVEE_NEXT', 'BLENDER_WORKBENCH'})

def revert_eevee_light_panel_poll(cls,context):
    return (context.engine in {'BLENDER_EEVEE','BLENDER_EEVEE_NEXT'})

def revert_eevee_light_distance_poll(cls,context):
    return (context.light and context.light.type != 'SUN')  and (context.engine in {'BLENDER_EEVEE','BLENDER_EEVEE_NEXT'})

def revert_spot_panel_poll(cls,context):
    return (context.light and context.light.type == 'SPOT')  and (context.engine in {'BLENDER_RENDER','BLENDER_EEVEE','BLENDER_EEVEE_NEXT','BLENDER_WORKBENCH'})

def revert_area_panel_poll(cls,context):
    return (context.light and context.light.type == 'AREA')  and (context.engine in {'BLENDER_RENDER', 'BLENDER_WORKBENCH'})

def revert_light_panel_poll(cls,context):
    return (context.engine in {'BLENDER_RENDER', 'BLENDER_WORKBENCH'})

def revert_cycles_light_panel_poll(cls,context):
    return (context.light) and (context.engine in {'CYCLES'})

def revert_cycles_spot_panel_poll(cls,context):
    return (context.light and context.light.type == 'SPOT') and (context.engine in {'CYCLES'})

def revert_cycles_beam_shape_panel_poll(cls,context):
    return (context.light and context.light.type in {'SPOT', 'AREA'}) and (context.engine in {'CYCLES'})

####

def unregister():

    from bpy.utils import unregister_class
    prefs.export_preferences_to_file()

    # Restoring Blender Light panels
    class_poll_mapping = {
        'CYCLES_CAMERA_PT_dof_aperture': revert_cycles_dof_aperture_poll,
        'DATA_PT_camera_dof_aperture': revert_dof_aperture_poll,
        'DATA_PT_EEVEE_light': revert_eevee_light_panel_poll,
        'DATA_PT_EEVEE_light_distance': revert_eevee_light_distance_poll,
        'DATA_PT_spot': revert_spot_panel_poll,
        'DATA_PT_area': revert_area_panel_poll if bpy.app.version < (3, 5, 0) else None,
        'DATA_PT_light': revert_light_panel_poll,
        'CYCLES_LIGHT_PT_light': revert_cycles_light_panel_poll,
        'CYCLES_LIGHT_PT_beam_shape': revert_cycles_beam_shape_panel_poll if bpy.app.version >= (2, 93, 0) else None,
        'CYCLES_LIGHT_PT_spot': revert_cycles_spot_panel_poll if bpy.app.version < (2, 93, 0) else None,
    }

    # Set poll methods for each class
    for class_name, poll_func in class_poll_mapping.items():
        class_object = getattr(bpy.types, class_name, None)
        if class_object and poll_func:
            class_object.poll = classmethod(poll_func)

    # Remove 3D view header buttons
    for button in af_header_buttons:
        bpy.types.VIEW3D_HT_header.remove(button)

    for button in cam_header_buttons:
        bpy.types.VIEW3D_HT_header.remove(button)

    # Remove Photographer panels from Blender UI
    if bpy.app.version < (4,3,0):
        bpy.types.RENDER_PT_eevee_shadows.remove(sampling_threshold.light_threshold_button)
    bpy.types.DATA_PT_camera_dof.remove(focus_plane.focus_plane_ui)
    # bpy.types.DATA_PT_camera_dof_aperture.remove(bokeh_ui.bokeh_ui)
    bpy.types.DATA_PT_lens.remove(lens_panel.lens_shift_ui)

    # Try to unregister Photographer Cycles UI if Cycles is enabled
    if cycles_check():
        bpy.types.CYCLES_RENDER_PT_sampling_advanced.remove(sampling_threshold.light_threshold_button)
        bpy.types.CYCLES_CAMERA_PT_dof.remove(focus_plane.focus_plane_ui)
        # bpy.types.CYCLES_CAMERA_PT_dof_aperture.remove(bokeh_ui.bokeh_ui)

    # Try to unregister Photographer LuxCore UI if LuxCore is enabled
    if luxcore_check():
        try:
            bpy.types.LUXCORE_CAMERA_PT_depth_of_field.remove(bokeh_ui.bokeh_ui)
        except:
            pass

    # Unregister Photographer Classes
    handler.unregister()
    prefs.unregister()
    scene_panel.unregister()
    auto_exposure.unregister()
    render_queue.unregister()
    driver_functions.unregister()
    physical_camera_add.unregister()
    physical_light_add.unregister()
    library.unregister()
    composition_guides_menu.unregister()
    build_rigs.unregister()
    view_layer.unregister()
    bookmarks.unregister()
    icons.unregister()

    for cls in (classes + photographer_panel_classes + lightmixer_panel_classes):
        unregister_class(cls)

    # Unregister Photographer Properties
    del bpy.types.Camera.photographer
    del bpy.types.Camera.post_effects
    del bpy.types.Light.photographer
    del bpy.types.Scene.lightmixer
    del bpy.types.World.lightmixer
    del bpy.types.Scene.photographer
    del bpy.types.Object.lightmixer
    del bpy.types.Material.lightmixer
    del bpy.types.ShaderNodeBsdfPrincipled.lightmixer
    del bpy.types.ShaderNodeEmission.lightmixer
    del bpy.types.Camera.bookmarks

if __name__ == "__main__":
    register()
