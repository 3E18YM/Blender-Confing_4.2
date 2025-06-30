import bpy, os, json
import rna_keymap_ui

from bpy.props import (BoolProperty,
                       FloatProperty,
                       EnumProperty,
                       FloatVectorProperty,
                       StringProperty,
                       IntProperty,
                       )
from . import camera_sensors
from .constants import photographer_presets_folder,prefs_filepath
from .ui import panel_classes
from .operators.sampling_threshold import update_light_threshold
from .properties.light import(INTENSITY_DESCRIPTION,
                    EXPOSURE_DESCRIPTION,
                    POWER_DESCRIPTION,
                    EFFICACY_DESCRIPTION,
                    LUMEN_DESCRIPTION,
                    CANDELA_DESCRIPTION,
                    NORMALIZEBYCOLOR_DESCRIPTION,
                    PER_SQUARE_METER_DESCRIPTION,
                    SPOTPOWERCONSERVATION_DESCRIPTION,
                    )
from .ui.library import hdri_lib_path_update, gobo_lib_path_update, ies_lib_path_update
from .operators.updater import changelog,latest_msg
from .operators.world import LIGHTMIXER_OT_HDRI_Rotation_Drag
from .ui.sticky_menu import PHOTOGRAPHER_OT_Sticky_Menu
from .ui.pie_camera import PHOTOGRAPHER_MT_Pie_Camera

SHOW_DEFAULT_LIGHT_PANELS_DESC = ( "In case Blender newer version adds a new Light features,"
            "these features might not be visible in the Physical Light panel until Photographer is also updated.\n"
            "This option allows you to show Blender panels back."
)
SHOW_DEFAULT_CAMERA_PANELS_DESC = ( "In case Blender newer version adds a new Camera features,"
            "these features might not be visible in the Camera panel until Photographer is also updated.\n"
            "This option allows you to show Blender panels back."
)
SUN_SKY_GAIN_DESC = (
    "Brightness multiplier. Set to 1 for physically correct sun/sky brightness, "
    "if you also use physically based tonemapper and light settings"
)

ADDON_KEYMAPS = []

def get_hotkey_entry_item(km, kmi_name, kmi_value):
    '''
    returns hotkey of specific type, with specific properties.name (keymap is not a dict, so referencing by keys is not enough
    if there are multiple hotkeys!)
    '''
    for i, km_item in enumerate(km.keymap_items):
        if km.keymap_items.keys()[i] == kmi_name:
            if not kmi_value:
                return km_item
            if km.keymap_items[i].properties.name == kmi_value:
                return km_item
    return None

def add_hotkey(keymap,space,region,identifier,property,event_type,value,ctrl=False,shift=False,alt=False,oskey=False,key_modifier='NONE',active=True):
    global ADDON_KEYMAPS
    if bpy.context.window_manager:
        wm = bpy.context.window_manager
        if wm.keyconfigs.addon:
            kc = wm.keyconfigs.addon
            km = kc.keymaps.new(name=keymap, space_type=space, region_type=region)
            kmi = get_hotkey_entry_item(km, identifier, property)
            if not kmi:
                kmi = km.keymap_items.new(identifier,event_type,value, shift=shift, ctrl=ctrl, alt=alt, oskey=oskey, key_modifier=key_modifier)
                if property:
                    kmi.properties.name = property
                kmi.active = active
                ADDON_KEYMAPS.append((km, kmi))

def remove_hotkey(keymap):
    ''' clears all addon level keymap hotkeys stored in addon_keymaps '''
    global ADDON_KEYMAPS
    if bpy.context.window_manager:
        wm = bpy.context.window_manager
        if wm.keyconfigs.addon:
            kc = wm.keyconfigs.addon
            if kc.keymaps.get(keymap, False):
                km = kc.keymaps[keymap]

                for km, kmi in ADDON_KEYMAPS:
                    try:
                        km.keymap_items.remove(kmi)
                        wm.keyconfigs.addon.keymaps.remove(km)
                    except RuntimeError:
                        print("Photographer Keymap item not found, skipping removal")
                        pass
                ADDON_KEYMAPS.clear()

def get_scene_prefs():
    preferences = bpy.context.preferences.addons[__package__].preferences
    prefs_values = {}
    for key in preferences.__annotations__.keys():
        k = getattr(preferences, key)
        if str(type(k)) == "<class 'bpy_prop_array'>":
            prefs_values[key] = k[:]
        else:
            prefs_values[key] = k
    
    # Save hotkey values
    wm = bpy.context.window_manager
    if wm.keyconfigs.addon:
        kc = wm.keyconfigs.addon
        if kc.keymaps.get('3D View', False):
            km = kc.keymaps['3D View']

            kmi = get_hotkey_entry_item(km,"wm.call_menu_pie","PHOTOGRAPHER_MT_Pie_Camera")
            if kmi:
                prefs_values['hotkey_camera_pie'] = {'event_type': kmi.type,'value': kmi.value,
                                                    'ctrl': kmi.ctrl,'shift': kmi.shift, 'alt': kmi.alt,
                                                    'oskey' : kmi.oskey, 'key_modifier': kmi.key_modifier,
                                                    'active': kmi.active,
                                                    }
                
            kmi = get_hotkey_entry_item(km, PHOTOGRAPHER_OT_Sticky_Menu.bl_idname,None)
            if kmi:
                prefs_values['hotkey_sticky_menu'] = {'event_type': kmi.type,'value': kmi.value,
                                                    'ctrl': kmi.ctrl,'shift': kmi.shift, 'alt': kmi.alt,
                                                    'oskey' : kmi.oskey, 'key_modifier': kmi.key_modifier,
                                                    'active': kmi.active,
                                                    }
            kmi = get_hotkey_entry_item(km, LIGHTMIXER_OT_HDRI_Rotation_Drag.bl_idname,None)
            if kmi:
                prefs_values['hotkey_hdri_rotation'] = {'event_type': kmi.type,'value': kmi.value,
                                                    'ctrl': kmi.ctrl,'shift': kmi.shift, 'alt': kmi.alt,
                                                    'oskey' : kmi.oskey, 'key_modifier': kmi.key_modifier,
                                                    'active': kmi.active,
                                                    }
    return prefs_values

def export_preferences_to_file():
    prefs_values = get_scene_prefs()
    if prefs_values:
        json_data = json.dumps(prefs_values, indent=4)

        # Write the JSON data to a file
        with open(prefs_filepath, 'w') as file:
            file.write(json_data)
    
    print("Exported Photographer preferences to: " + prefs_filepath)

def import_preferences_from_file():
    preferences = bpy.context.preferences.addons[__package__].preferences
    try:
        with open(prefs_filepath, 'r') as file:
            json_data = json.load(file)

        # Update preferences properties with values from the JSON file
        for prop, value in json_data.items():
            if hasattr(preferences, prop):
                setattr(preferences, prop, value)

            if prop == 'hotkey_camera_pie':
                add_hotkey("3D View",'VIEW_3D','WINDOW',
                    "wm.call_menu_pie","PHOTOGRAPHER_MT_Pie_Camera",
                    value['event_type'], value['value'], shift=value['shift'], ctrl=value['ctrl'], alt=value['alt'],
                    oskey=value['oskey'], key_modifier=value['key_modifier'],active=value['active'])
            if prop == 'hotkey_sticky_menu':
                add_hotkey("3D View",'VIEW_3D','WINDOW',
                    PHOTOGRAPHER_OT_Sticky_Menu.bl_idname,None,
                    value['event_type'], value['value'], shift=value['shift'], ctrl=value['ctrl'], alt=value['alt'],
                    oskey=value['oskey'], key_modifier=value['key_modifier'],active=value['active'])
            if prop == 'hotkey_hdri_rotation':
                add_hotkey("3D View",'VIEW_3D','WINDOW',
                    LIGHTMIXER_OT_HDRI_Rotation_Drag.bl_idname,None,
                    value['event_type'], value['value'], shift=value['shift'], ctrl=value['ctrl'], alt=value['alt'],
                    oskey=value['oskey'], key_modifier=value['key_modifier'], active=value['active'])

        print("Photographer preferences imported successfully.")
    except FileNotFoundError:
        print("Photographer preferences file not found. Using add-on defaults.")
    except Exception as e:
        print("An error occurred while importing Photographer preferences:", str(e))

class PHOTOGRAPHER_OT_Hotkey_Add_Camera_Pie_Menu(bpy.types.Operator):
    '''Add hotkey to Photographer's Camera Pie menu'''
    bl_idname = "photographer.hotkey_add_camera_pie_menu"
    bl_label = "Photographer Camera Pie Menu hotkey"
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        add_hotkey("3D View",'VIEW_3D','WINDOW',
            "wm.call_menu_pie","PHOTOGRAPHER_MT_Pie_Camera",
            'C', 'PRESS', shift=True, ctrl=True)
    
        self.report({'INFO'}, "Hotkey added in User Preferences -> Keymap -> 3D View -> 3D View (Global)")
        return {'FINISHED'}

class PHOTOGRAPHER_OT_Hotkey_Add_Camera_Sticky_Menu(bpy.types.Operator):
    '''Add hotkey to Photographer's Camera Sticky Menu'''
    bl_idname = "photographer.hotkey_add_camera_sticky_menu"
    bl_label = "Photographer Camera Sticky Menu hotkey"
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        add_hotkey("3D View",'VIEW_3D','WINDOW',
            PHOTOGRAPHER_OT_Sticky_Menu.bl_idname,None,
            'C', 'PRESS', shift=True, ctrl=True, alt=True)

        self.report({'INFO'}, "Hotkey added in User Preferences -> Keymap -> 3D View -> 3D View (Global)")
        return {'FINISHED'}
    
class PHOTOGRAPHER_OT_Hotkey_Add_HDRI_Rotation_Drag(bpy.types.Operator):
    '''Add hotkey to Photographer's HDRI Rotation using the mouse drag'''
    bl_idname = "photographer.hotkey_add_hdri_rotation_drag"
    bl_label = "HDRI Rotation using Mouse Drag hotkey"
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        add_hotkey("3D View",'VIEW_3D','WINDOW',
            LIGHTMIXER_OT_HDRI_Rotation_Drag.bl_idname,None,
            'RIGHTMOUSE', 'PRESS', shift=True, alt=True)

        self.report({'INFO'}, "Hotkey added in User Preferences -> Keymap -> 3D View -> 3D View (Global)")
        return {'FINISHED'}

def update_photographer_category(self,context):
    for cls in panel_classes.photographer_panel_classes:
        try:
            bpy.utils.unregister_class(cls)
        except:
            pass
        cls.bl_category = self.category
        bpy.utils.register_class(cls)

def update_lightmixer_category(self,context):
    for cls in panel_classes.lightmixer_panel_classes:
        try:
            bpy.utils.unregister_class(cls)
        except:
            pass
        cls.bl_category = self.lightmixer_category
        bpy.utils.register_class(cls)

def update_exposure(self,context):
    if context.scene.camera and context.scene.camera.type == 'CAMERA':
        photographer = context.scene.camera.data.photographer
        from . import camera
        if photographer.exposure_enabled:
            camera.update_ev(photographer,context)

class PHOTOGRAPHER_OT_Update_All_Lights_Energy(bpy.types.Operator):
    bl_idname = "photographer.update_all_lights_energy"
    bl_label = "Update all lights energy"
    bl_description = "Recalculates energy for all lights in the scene, after changing the Follow Scene Unit Scale setting"

    def execute(self, context):
        preferences = bpy.context.preferences.addons[__package__].preferences
        from .properties import light
        if preferences.use_physical_lights:
            lights = [o for o in bpy.data.objects if o.type == 'LIGHT']
            for l in lights:
                photographer = l.data.photographer
                light.update_energy(photographer)
        return {'FINISHED'}

# def update_cam_list_sorting(self,context):
#     context.scene.photographer.cam_list_sorting = self.default_cam_list_sorting

# def update_default_rq_incremental(self,context):
#     print (bpy.data.scenes)
#     for scene in bpy.data.scenes:
#         scene.renderqueue.incremental = self.default_rq_incremental


class AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    category : StringProperty(
        description=("Choose a name for the category of the Photographer panel. \n"
        "You can write the name of an existing panel"),
        default="Photographer",
        update=update_photographer_category
    )

    lightmixer_category : StringProperty(
        description=("Choose a name for the category of the Lightmixer panel. \n"
        "You can write the name of an existing panel"),
        default="Photographer",
        update=update_lightmixer_category
    )

    expand_panel_visibility : BoolProperty(
        name = "Panel Visibility",
        description = "Show / Hide Panel visibility properties",
        default = False
    )

    camera_list_panel_enable : BoolProperty(
        name = "Camera List",
        description = "Shows the panel and its settings in the Add-on panel",
        default = True
    )
    camera_panel_enable : BoolProperty(
        name = "Camera",
        description = "Shows the panel and its settings in the Add-on panel",
        default = True
    )
    bookmarks_panel_enable : BoolProperty(
        name = "Position Bookmarks",
        description = "Shows the panel and its settings in the Add-on panel",
        default = True
    )
    lens_panel_enable : BoolProperty(
        name = "Lens",
        description = "Shows the panel and its settings in the Add-on panel",
        default = True
    )
    dof_panel_enable : BoolProperty(
        name = "Depth of Field",
        description = "Shows the panel and its settings in the Add-on panel",
        default = True
    )
    focus_panel_enable : BoolProperty(
        name = "Focus",
        description = "Shows the panel and its settings in the Add-on panel",
        default = True
    )
    postfx_panel_enable : BoolProperty(
        name = "Post FX",
        description = "Shows the panel and its settings in the Add-on panel",
        default = True
    )
    exposure_panel_enable : BoolProperty(
        name = "Exposure",
        description = "Shows the panel and its settings in the Add-on panel",
        default = True
    )
    wb_panel_enable : BoolProperty(
        name = "White Balance",
        description = "Shows the panel and its settings in the Add-on panel",
        default = True
    )
    resolution_panel_enable : BoolProperty(
        name = "Resolution",
        description = "Shows the panel and its settings in the Add-on panel",
        default = True
    )
    viewlayer_panel_enable : BoolProperty(
        name = "View Layer",
        description = "Shows the panel and its settings in the Add-on panel",
        default = True
    )
    renderqueue_panel_enable : BoolProperty(
        name = "Render Queue",
        description = "Shows the panel and its settings in the Add-on panel",
        default = True
    )
    worldmixer_panel_enable : BoolProperty(
        name = "World Mixer",
        description = "Shows the panel and its settings in the Add-on panel",
        default = True
    )
    lightmixer_panel_enable : BoolProperty(
        name = "Light Mixer",
        description = "Shows the panel and its settings in the Add-on panel",
        default = True
    )
    emissivemixer_panel_enable : BoolProperty(
        name = "Emissive Mixer",
        description = "Shows the panel and its settings in the Add-on panel",
        default = True
    )

# Sticky Menu visibility
    menu_store_ui: BoolProperty(
        name = "Store Sticky Menu UI",
        description = "Reopen the Sticky Menu with the previous tab and opened panels",
        default = True
    )
    menu_multi_tab: BoolProperty(
        name = "Multi Tab Sticky Menu",
        description = "Divide Sticky Menu panel into Camera, Lens, Post FX and Render tabs",
        default = True
    )

    camera_list_menu_enable : BoolProperty(
        name = "Camera List",
        description = "Shows the panel and its settings in the Sticky Menu",
        default = True
    )
    camera_menu_enable : BoolProperty(
        name = "Camera",
        description = "Shows the panel and its settings in the Sticky Menu",
        default = True
    )
    bookmarks_menu_enable : BoolProperty(
        name = "Position Bookmarks",
        description = "Shows the panel and its settings in the Sticky Menu",
        default = True
    )
    lens_menu_enable : BoolProperty(
        name = "Lens",
        description = "Shows the panel and its settings in the Sticky Menu",
        default = True
    )
    dof_menu_enable : BoolProperty(
        name = "Depth of Field",
        description = "Shows the panel and its settings in the Sticky Menu",
        default = True
    )
    focus_menu_enable : BoolProperty(
        name = "Focus",
        description = "Shows the panel and its settings in the Sticky Menu",
        default = True
    )
    postfx_menu_enable : BoolProperty(
        name = "Post FX",
        description = "Shows the panel and its settings in the Sticky Menu",
        default = True
    )
    exposure_menu_enable : BoolProperty(
        name = "Exposure",
        description = "Shows the panel and its settings in the Sticky Menu",
        default = True
    )
    wb_menu_enable : BoolProperty(
        name = "White Balance",
        description = "Shows the panel and its settings in the Sticky Menu",
        default = True
    )
    resolution_menu_enable : BoolProperty(
        name = "Resolution",
        description = "Shows the panel and its settings in the Sticky Menu",
        default = True
    )
    viewlayer_menu_enable : BoolProperty(
        name = "View Layer",
        description = "Shows the panel and its settings in the Sticky Menu",
        default = True
    )
    renderqueue_menu_enable : BoolProperty(
        name = "Render Queue",
        description = "Shows the panel and its settings in the Sticky Menu",
        default = True
    )
    worldmixer_menu_enable : BoolProperty(
        name = "World Mixer",
        description = "Shows the panel and its settings in the Sticky Menu",
        default = True
    )
    lightmixer_menu_enable : BoolProperty(
        name = "Light Mixer",
        description = "Shows the panel and its settings in the Sticky Menu",
        default = True
    )
    emissivemixer_menu_enable : BoolProperty(
        name = "Emissive Mixer",
        description = "Shows the panel and its settings in the Sticky Menu",
        default = True
    )

# UI Preferences

    show_compact_ui : BoolProperty(
        name = "Show Compact UI",
        description = "Adds most important settings into Panel names to keep the UI compact",
        default = True
    )
    screen_resolution: FloatProperty(
        name = 'Screen Resolution',
        description = ('Used to define when extra buttons appear in Light Mixer and Emissive Mixer, '
        'if the panel is large enough'),
        default = 1920
    )

    needs_update : StringProperty()

    changelog_expanded : BoolProperty(
        default= False,
    )

    ui_tab : EnumProperty(
        name = "Preferences Tab",
        items = [('UI','UI', ''),
                ('LIBRARY','Library',''),
                ('CAMERA','Camera',''),
                ('EXPOSURE','Exposure / WB',''),
                ('LIGHT','Light',''),
                ('RENDER','Render',''),
                ],
        default = 'UI',
    )
    exposure_mode_pref : EnumProperty(
        name = "Default Exposure Mode",
        description = "Choose the default Exposure Mode",
        items = [('EV','EV', ''),('AUTO','Auto',''),('MANUAL','Manual','')],
        default = 'EV',
    )
    reset_exposure : BoolProperty(
        name = "Reset Exposure when not overriden",
        description = ("If enabled, cameras with no Exposure override will reset Blender Exposure to 0 (or inherit from the Main Camera).\n"
                    "If disabled, cameras with no Exposure override will not update Blender Exposure, or will inherit it from the Main Camera.\n"
                    "This gives you the possibility to change Blender Exposure in Render > Color Management if Exposure is not overriden and there is no Main Camera in the Scene"),
        default = True
    )
    reset_wb : BoolProperty(
        name = "Reset White Balance when not overriden",
        description = ("If enabled, cameras with no White Balance override will reset White Balance to neutral (or inherit from the Main Camera).\n"
                    "If disabled, cameras with no White Balance override will not update anything, or will inherit it from the Main Camera.\n"
                    "This gives you the possibility to change Blender White Levels in Render > Color Management > Use Curves if WB is not overriden and there is no Main Camera in the Scene"),
        default = True
    )
    shutter_speed_slider_pref : BoolProperty(
        name = "Shutter Speed / Angle",
        description = "Use Slider for Shutter Speed / Angle",
        default = False
    )

    aperture_slider_pref : BoolProperty(
        name = "Aperture",
        description = "Use Slider for Aperture",
        default = False
    )

    iso_slider_pref : BoolProperty(
        name = "ISO",
        description = "Use Slider for ISO setting",
        default = False
    )

    show_af_buttons_pref : BoolProperty(
        name = "Show Autofocus buttons in 3D View header",
        description = "AF buttons will still be available in the Add-on panel",
        default = True
    )

    show_cam_buttons_pref : BoolProperty(
        name = "Show 'Lock Camera to View' and 'Zoom 1:1' buttons in 3D View header",
        description = "'Lock Camera to View' will still be available in the Add-on panel",
        default = True
    )

    show_image_panels : BoolProperty(
        name = "Show Photographer panel in Image and Node editors",
        description = "Photographer will still be accessible in the 3D View panel",
        default = True
    )

    show_drone_camera : BoolProperty(
        name = "Show Drone Camera feature",
        description = "Uncheck if you don't plan to use the Drone Camera feature, for a cleaner UI",
        default = True
    )

    use_physical_lights : BoolProperty(
        name = "Use Physical lights",
        description = ("Replace Light properties with advanced Physical Light properties. \n"
        "It is recommend to disable this feature when using LuxCore, unless you plan to do comparisons with Cycles"),
        default = True,
    )

    follow_unit_scale : BoolProperty(
        name = "Follow Scene Unit Scale",
        description = "Multiplies lighting power according to the scene Unit Scale",
        default = True,
        # update = update_all_lights_energy,
    )

    show_default_light_panels : BoolProperty(
        name = "Keep showing Blender Light panels",
        description = SHOW_DEFAULT_LIGHT_PANELS_DESC,
        default = False
    )
    show_default_camera_panels : BoolProperty(
        name = "Keep showing Blender Camera panels",
        description = SHOW_DEFAULT_CAMERA_PANELS_DESC,
        default = False
    )

    aces_ue_match : BoolProperty(
        name = "Match Blender ACES to Unreal ACES",
        description = ("Unreal ACES tonemapper uses a 1.45 multiplier. "
        "Check this box to fix this discrepancy. \n"
        "This setting is only effective when using ACES in Blender"),
        default = True,
        update = update_exposure,
    )

    lens_attenuation : FloatProperty(
        name = "Lens Attenuation factor",
        description = ("Default value of 0.78 will cancel lens attenuation calculations"
        "and will match Unreal 4.25 camera exposure. \n"
        "ISO standard recommends a lens transmittance of 0.65, which is sometimes"
        " used by other render engines to match real cameras"),
        default = 0.78,
        min = 0.01,
        max = 1,
        precision = 3,
        update = update_exposure,
    )

    default_light_threshold : FloatProperty(
        name = "Default Light Threshold",
        description = "Defines the Light Sampling Threshold that will be multiplied by the Exposure Value",
        default = 0.01,
        min = 0,
        max = 1,
        precision = 5,
        update = update_light_threshold,
    )

    auto_light_threshold : BoolProperty(
        name = "Automatic Light Threshold",
        description = ("Exposure changes will update the Light Sampling threshold automatically. \n"
        "Note: Viewport render will refresh when changing the exposure when Auto is ON"),
        default = False,
    )

    hide_light_threshold_warning: BoolProperty(
        name = "Hide warning",
        description = ("Hides the warning that will appear in the Exposure Panel "
        "if the current Light Sampling threshold is too far from its optimal value"),
        default = False,
    )
    fit_inside_sensor : BoolProperty(
        name = "Fit inside Sensor",
        description = "Automatically adjusts the Camera Sensor fit in order to make the Resolution fit inside the sensor. \n"
        "This is a smarter Auto Fit than the one provided by Blender.\n"
        "FOV calculation will be more accurate when trying to match a photo.\n"
        "This setting defines the default value that will be used when creating a new camera",
        default = True,

    )
    default_sensor_type : EnumProperty(
        name = "Default Sensor Type", description = "Camera Sensor Size used when creating a new camera",
        items = camera_sensors.sensor_type_items,
        default = 8,
    )
    default_clip_start: FloatProperty(
        name = "Clip Start",
        description = "Clip Start for newly created cameras",
        default = 0.1,
        soft_min = 0.001, min = 0.000001,
        precision = 4,
        unit='LENGTH',
    )
    default_clip_end: FloatProperty(
        name = "Clip End",
        description = "Clip End for newly created cameras",
        default = 1000,
        soft_min = 0.001, min = 0.000001,
        precision = 4,
        unit='LENGTH',
    )
    default_show_passepartout: BoolProperty(
        name = "Show Passepartout",
        description = "Show Passepartout value for newly created cameras",
        default = True,
    )
    default_passepartout_alpha: FloatProperty(
        name = "Passepartout Alpha",
        description = "Passepartout opacity for newly created cameras",
        default = 1.0, # Necessary for Viewport compositing
        min = 0,
        max = 1,
    )
    default_focus_plane_color : FloatVectorProperty(
        name="Default Focus Plane Color", description="Set Color and Alpha opacity of the Focus Plane debug",
        subtype='COLOR', min=0.0, max=1.0, size=4, default=(1,0,0,0.2),
        options = {'HIDDEN'},
    )
    default_focus_plane_edge : bpy.props.FloatProperty(
        name = "Default Edge Detection", description = "Creates an outline where the focus plane meets the objects",
        default = 0.5, min = 0, soft_max= 1,
        options = {'HIDDEN'},
    )
    frame_full_viewport: BoolProperty(
        name = "Full Viewport Framing",
        description = "Frame the full Viewport when adding a new Camera, instead of keeping the viewport overscan",
        default = True,
    )
    focus_eyedropper_func : EnumProperty(
        name = "Focus Eyedropper function",
        description = "Defines the function of the Focus Eyedropper in the Compact UI",
        items = [('AFS','AF-Single', ''),('AFT','AF-Track','photographer.focus_tracking'),('BL_PICKER','Blender Focus Picker','')],
        default = 'AFS',
    )
    # Composition Guides Default values
    show_composition_thirds: BoolProperty(
        name = "Show Thirds Composition Guide",
        description = "Displays Thirds composition guide for newly created cameras",
        default = False,
    )
    show_composition_center: BoolProperty(
        name = "Show Center Composition Guide",
        description = "Displays Center composition guide for newly created cameras",
        default = False,
    )
    show_composition_center_diagonal: BoolProperty(
        name = "Show Diagonal Composition Guide",
        description = "Displays Diagonal composition guide for newly created cameras",
        default = False,
    )
    show_composition_golden: BoolProperty(
        name = "Show Golden Ratio Composition Guide",
        description = "Displays Golden Ratio composition guide for newly created cameras",
        default = False,
    )
    show_composition_golden_tria_a: BoolProperty(
        name = "Show Golden Ratio Triangle A Composition Guide",
        description = "Displays Golden Ratio Triangle A composition guide for newly created cameras",
        default = False,
    )
    show_composition_golden_tria_b: BoolProperty(
        name = "Show Golden Ratio Triangle B Composition Guide",
        description = "Displays Golden Ratio Triangle B composition guide for newly created cameras",
        default = False,
    )
    show_composition_harmony_tri_a: BoolProperty(
        name = "Show Harmony Ratio Triangle A Composition Guide",
        description = "Displays Harmony Ratio Triangle A composition guide for newly created cameras",
        default = False,
    )
    show_composition_harmony_tri_b: BoolProperty(
        name = "Show Harmony Ratio Triangle B Composition Guide",
        description = "Displays Harmony Ratio Triangle B composition guide for newly created cameras",
        default = False,
    )
    # default_rq_incremental: bpy.props.BoolProperty(
    #     name = "Default Incremental",
    #     description = "Incremental default value for the Render Queue"
    #                 "Adds number suffix and increments for each re-render",
    #     default = True,
    #     update = update_default_rq_incremental,
    # )

    hide_unlinked_emissive: BoolProperty(
        name = "Ignore Unlinked materials in Emissive Mixer",
        description = "Do not include Emissive Materials that are assigned to Unlinked meshes",
        default = True,
    )

    sunlight_units = [
        ("artistic", "Artistic", "Artist friendly unit using Gain and Exposure",0),
        ("irradiance", "Irradiance (W/m2)", "Irradiance in Watt per square meter",1),
        ("illuminance", "Illuminance (Lux)", "Illuminance in Lux",2),
    ]

    default_sunlight_unit: EnumProperty(
        name="Default Sunlight Unit",
        items=sunlight_units,
        default='irradiance',
    )

    default_irradiance: FloatProperty(
        name="Irradiance W/m2", #description=light.IRRADIANCE_DESCRIPTION,
        default=1, min=0, precision=3,
    )

    default_illuminance: FloatProperty(
        name="Lux", #description=light.ILLUMINANCE_DESCRIPTION,
        default=110000, min=0, precision=2,
    )

    light_units = [
        ("artistic", "Artistic", "Artist friendly unit using Gain and Exposure",0),
        ("power", "Power", "Radiant flux in Watt",1),
        ("lumen", "Lumen", "Luminous flux in Lumen",2),
        ("candela", "Candela", "Luminous intensity in Candela",3),
        ("advanced_power", "Power (Advanced)", "Radiant flux in Watt",4),
    ]

    default_light_unit: EnumProperty(
        name="Default Light Unit",
        items=light_units,
        default='power',
    )

    default_intensity: FloatProperty(
        name="Intensity", description=INTENSITY_DESCRIPTION,
        default=10, soft_min=0,
    )

    default_light_exposure: FloatProperty(
        name="Exposure", description=EXPOSURE_DESCRIPTION,
        default=0, soft_min=-10, soft_max=10, precision=2,
    )

    default_power: FloatProperty(
        name="Power", description=POWER_DESCRIPTION,
        default=10, soft_min=0, precision=5, unit='POWER',
    )

    default_advanced_power: FloatProperty(
        name="Power (Advanced)", description=POWER_DESCRIPTION,
        default=10, soft_min=0, precision=4, unit='POWER',
    )

    default_efficacy: FloatProperty(
        name="Efficacy (lm/W)", description=EFFICACY_DESCRIPTION,
        default=683, min=0,
    )

    default_lumen: FloatProperty(
        name="Lumen", description=LUMEN_DESCRIPTION,
        default=683, soft_min=0, precision=2,
    )

    default_candela: FloatProperty(
        name="Candela", description=CANDELA_DESCRIPTION,
        default=543.514, soft_min=0, precision=3,
    )

    default_normalizebycolor: BoolProperty(
        name="Normalize by Color Luminance",
        description=NORMALIZEBYCOLOR_DESCRIPTION,
        default=True,
    )

    default_spot_power_conservation: BoolProperty(
        name="Conserves Energy with Cone Angle",
        description=SPOTPOWERCONSERVATION_DESCRIPTION,
        default=True,
    )

    default_per_square_meter: BoolProperty(
        name="Per square meter",
        description=PER_SQUARE_METER_DESCRIPTION,
        default=False,
    )

    # EEVEE Light settings
    default_use_custom_distance: BoolProperty(
        name="Custom Distance",
        default=True,
    )
    default_cutoff_distance: FloatProperty(
        name="Distance",
        default=40,
        unit='LENGTH',
    )
    default_shadow_buffer_bias: FloatProperty(
        name="Shadow Bias",
        default=0.01,
    )
    default_use_contact_shadow: BoolProperty(
        name="Contact Shadows",
        default=False,
    )
    default_contact_shadow_distance: FloatProperty(
        name="Distance",
        default=0.2,
        unit='LENGTH',
    )
    default_contact_shadow_bias: FloatProperty(
        name="Contact Shadows Bias",
        default=0.03,
    )
    default_contact_shadow_thickness: FloatProperty(
        name="Contact Shadows Thickness",
        default=0.2,
    )

    # EEVEE NEXT Shadow Default Properties
    default_use_shadow_jitter: BoolProperty(
        name="Jitter",
        default=False,
    )
    default_shadow_jitter_overblur: FloatProperty(
        name="Overblur",
        default=10, min=0, soft_max=20, max=100,
        subtype='PERCENTAGE',
    )
    default_shadow_filter_radius: FloatProperty(
        name="Filter",
        default=1.0, min=0.0, soft_max=5.0,
    )
    default_shadow_maximum_resolution: FloatProperty(
        name="Resolution Limit",
        default=0.001, min=0, soft_min=0.0001, soft_max=0.02,
        unit='LENGTH',
    )

    lc_light_types = [
        ("sun", "Sun", "Physically correct sun that emits parallel light rays and changes color with elevation", 0),
        ("distant", "Distant", "Distant star without atmosphere simulation (emits parallel light)", 1),
        ("hemi", "Hemi", "180 degree constant light source", 2),
    ]
    default_lc_light_type: EnumProperty(
    name="Sun Type",
    items=lc_light_types,
    default="sun"
    )
    lc_light_units = [
        ("artistic", "Artistic", "Artist friendly unit using Gain and Exposure",0),
        ("power", "Power", "Radiant flux in Watt",1),
        ("lumen", "Lumen", "Luminous flux in Lumen",2),
        ("candela", "Candela", "Luminous intensity in Candela",3),
    ]

    default_lc_light_unit: EnumProperty(
        name="Default Light Unit",
        items=lc_light_units,
        default='power',
    )

    default_sun_sky_gain: FloatProperty(
        name="Sun Gain",
        default=0.00002,
        description=SUN_SKY_GAIN_DESC,
    )
    default_gain: FloatProperty(
        name="Gain",
        default=1,
    )
    opt_vignetting_lib_path: StringProperty(
        name="Optical Vignetting Library Path",
        default= os.path.join(os.path.join(photographer_presets_folder,'optical_vignetting'),''),
        description=("Folder where you store your Optical Vignetting textures for Depth of Field. \n"
                    "Default will use Scripts/Presets/photographer/optical_vignetting"),
        subtype="DIR_PATH",
    )
    bokeh_lib_path: StringProperty(
        name="Bokeh Library Path",
        default= os.path.join(os.path.join(photographer_presets_folder,'bokeh'),''),
        description=("Folder where you store your Bokeh textures for Depth of Field. \n"
                    "Default will use Scripts/Presets/photographer/bokeh"),
        subtype="DIR_PATH",
    )
    gobo_lib_path: StringProperty(
        name="Light Gobo Library Path",
        default= os.path.join(os.path.join(photographer_presets_folder,'light_gobos'),''),
        description=("Folder where you store your Light Gobo textures. \n"
                    "Default will use Scripts/Presets/photographer/light_gobos"),
        subtype="DIR_PATH",
        update=gobo_lib_path_update,
    )
    ies_lib_path: StringProperty(
        name="Light Gobo Library Path",
        default= os.path.join(os.path.join(photographer_presets_folder,'ies_profiles'),''),
        description=("Folder where you store your IES Profiles. \n"
                    "Default will use Scripts/Presets/photographer/ies_profiles"),
        subtype="DIR_PATH",
        update=ies_lib_path_update,
    )
    stmap_lib_path: StringProperty(
        name="Distortion STMap Library Path",
        default= os.path.join(os.path.join(photographer_presets_folder,'stmaps'),''),
        description=("Folder where you store your STMap textures for camera distortion. \n"
                    "Default will use Scripts/Presets/photographer/stmaps"),
        subtype="DIR_PATH",
    )
    film_grain_lib_path: StringProperty(
        name="Film Grain textures Library Path",
        default= os.path.join(os.path.join(photographer_presets_folder,'film_grain'),''),
        description=("Folder where you store your Film Grain textures. \n"
                    "Default will use Scripts/Presets/photographer/film_grain"),
        subtype="DIR_PATH",
    )
    hdri_lib_path: StringProperty(
        name="HDRI Library Path",
        default= '',
        description="Folder where you store your HDRI images for the World Environment",
        subtype="DIR_PATH",
        update=hdri_lib_path_update,
    )
    hdri_auto_world_rename: BoolProperty(
        name="Rename World automatically with HDRI texture name",
        description="Automatically rename the World data with the name of the HDRI it is using",
        default=True,
    )
    hdri_auto_load: BoolProperty(
        name="Loads HDRI automatically when changing Category",
        description="Can be disabled to save memory and the imported images cleaner"
            	" by not loading the first image of the folder when changing the HDRI category",
        default=True,
    )
    sun_placement_precision: IntProperty(
        name='Sun Placement Precision',
        description="Higher value will increase direction accuracy When pointing at the sky when creating a sunlight"
            " but will slow down the Operator, especially on low-end machines",
        default=5,
        min=3,
        soft_max=7,
        max=8,
    )
    hide_hdri_meshes: BoolProperty(
        name="Hide HDRI Meshes during Sun Placement",
        description="Helps with pointing at the Sun position on the World Sphere without colliding with HDRI mesh",
        default=True,
    )

    # Widget prefix
    widget_prefix: StringProperty(
        name="Camera Widget prefix",
        description="Prefix for the widget objects",
        default="WGT-",
    )

    # Collection name
    camera_widget_collection_name: StringProperty(
        name="Bone Widget collection name",
        description="Name for the collection the widgets will appear",
        default="Widgets",
    )

    # White Balance Modes
    color_temperature_modes = [
        ("PG_SIMPLE", "Simplified", "Photographer's simplified uses sRGB table and limits Temperature to Red and Blue channels",0),
        ("ALGORITHM", "Algorithm (Experimental)", "Based on Tanner Helland's and McCamy algorithms",1),
        ("BLACKBODY", "Blackbody (Experimental)", "Based on Blender's Blackbody REC.709 table",2),
        ("BLENDER", "Blender 4.3 White Balance", "Using the Color Management > White Balance",3),
    ]

    color_temperature_mode: EnumProperty(
        name="Color Temperature Mode",
        items=color_temperature_modes,
        default='PG_SIMPLE',
    )


    def draw(self, context):
            layout = self.layout
            wm = bpy.context.window_manager

            box = layout.box()
            split = box.split(factor = 0.45)
            row = split.row()
            row.operator("photographer.check_for_update")
            row = split.row(align=True)
            row.operator("wm.url_open", text="Gumroad").url = "https://gumroad.com/library?query=photographer"
            # row.operator("wm.url_open", text="Blender Market").url = "https://blendermarket.com/account/orders"

            # Update Check
            if self.needs_update and self.needs_update != latest_msg:
                row = box.row()
                row.alert = True
                row.label(text=self.needs_update)

                row = box.row()
                row.prop(self, "changelog_expanded",
                    icon="TRIA_DOWN" if self.changelog_expanded else "TRIA_RIGHT",
                    icon_only=True, emboss=False
                )
                row.label(text='Changelog')
                if self.changelog_expanded:
                    for v in changelog:
                        version_box = box.box()
                        row = version_box.row()
                        row.scale_y = 0.6
                        row.label(text=v[0]+":")

                        split_str = v[1].splitlines()
                        for str in split_str:
                            row = version_box.row()
                            row.scale_y = 0.5
                            row.label(text=str)
            elif self.needs_update == latest_msg:
                row = box.row()
                row.label(text=latest_msg)
            else:
                row = box.row()
                row.label(text="Press 'Check for Updates' to verify if you are "
                        "running the latest version of the add-on.")

            percentage_columns = 0.35
            row = layout.row(align=True)
            row.prop(self, "ui_tab", expand=True)

            box = layout.box()
            if self.ui_tab == 'UI':
                # UI options
                row = box.row(align=True)
                row.label(text="Panel Category :")
                row.prop(self, "category", text="")
                row = box.row(align=True)
                row.label(text="Light Mixer Panel Category :")
                row.prop(self, "lightmixer_category", text="")
                col = box.column()
                col.prop(self, 'show_default_light_panels')
                col.prop(self, 'show_default_camera_panels')

                panels_box = box.box()
                row = panels_box.row(align=True)
                row.alignment='LEFT'
                row.prop(self,'expand_panel_visibility',
                         icon='TRIA_DOWN' if self.get('expand_panel_visibility', False) else 'TRIA_RIGHT',
                        emboss=False)
                # row.label(text= 'Panel visibility :')

                if self.expand_panel_visibility:
                    row = panels_box.row(align=True)
                    row.label(text= '3D View Right Panel :')
                    row.label(text= 'Sticky Menu :')

                    row = panels_box.row(align=True)
                    col = row.column(align=True)
                    col.prop(self,"camera_list_panel_enable")
                    col.prop(self,"camera_panel_enable")
                    col.prop(self,"bookmarks_panel_enable")
                    col.prop(self,"lens_panel_enable")
                    col.prop(self,"dof_panel_enable")
                    col.prop(self,"focus_panel_enable")
                    col.prop(self,"exposure_panel_enable")
                    col.prop(self,"wb_panel_enable")
                    col.prop(self,"postfx_panel_enable")
                    col.prop(self,"resolution_panel_enable")
                    col.prop(self,"viewlayer_panel_enable")
                    col.prop(self,"renderqueue_panel_enable")
                    col.prop(self,"worldmixer_panel_enable")
                    col.prop(self,"lightmixer_panel_enable")
                    col.prop(self,"emissivemixer_panel_enable")

                    col = row.column(align=True)
                    col.prop(self,"camera_list_menu_enable")
                    col.prop(self,"camera_menu_enable")
                    col.prop(self,"bookmarks_menu_enable")
                    col.prop(self,"lens_menu_enable")
                    col.prop(self,"dof_menu_enable")
                    col.prop(self,"focus_menu_enable")
                    col.prop(self,"exposure_menu_enable")
                    col.prop(self,"wb_menu_enable")
                    col.prop(self,"postfx_menu_enable")
                    col.prop(self,"resolution_menu_enable")
                    col.prop(self,"viewlayer_menu_enable")
                    col.prop(self,"renderqueue_menu_enable")
                    # col.prop(self,"worldmixer_menu_enable")
                    # col.prop(self,"lightmixer_menu_enable")
                    # col.prop(self,"emissivemixer_menu_enable")

                box.prop(self, 'screen_resolution')
                box.prop(self, 'show_compact_ui')
                box.prop(self, 'show_image_panels')
                box.prop(self, 'show_af_buttons_pref')
                box.prop(self, 'show_cam_buttons_pref')
                box.prop(self, 'show_drone_camera')
                box.separator()
                box.label(text='Scene Camera Sticky Menu :')
                box.prop(self, 'menu_multi_tab')
                box.prop(self, 'menu_store_ui')

                
                # Pie menu Hotkey
                box = layout.box()
                box.label(text="Hotkeys:")
                wm = bpy.context.window_manager
                kc = wm.keyconfigs.addon
                if kc.keymaps.get('3D View', False):
                    km = kc.keymaps['3D View']

                    kmi = get_hotkey_entry_item(km, "wm.call_menu_pie","PHOTOGRAPHER_MT_Pie_Camera")
                    if kmi:
                        box.context_pointer_set("keymap", km)
                        rna_keymap_ui.draw_kmi([], kc, km, kmi, box, 0)
                    else:
                        box.operator('photographer.hotkey_add_camera_pie_menu', text = "Add Scene Camera Pie Menu hotkey")

                    kmi = get_hotkey_entry_item(km, PHOTOGRAPHER_OT_Sticky_Menu.bl_idname,None)
                    if kmi:
                        box.context_pointer_set("keymap", km)
                        rna_keymap_ui.draw_kmi([], kc, km, kmi, box, 0)
                    else:
                        box.operator('photographer.hotkey_add_camera_sticky_menu', text = "Add Scene Camera Sticky Menu hotkey")

                    kmi = get_hotkey_entry_item(km, LIGHTMIXER_OT_HDRI_Rotation_Drag.bl_idname,None)
                    if kmi:
                        box.context_pointer_set("keymap", km)
                        rna_keymap_ui.draw_kmi([], kc, km, kmi, box, 0)
                    else:
                        box.operator('photographer.hotkey_add_hdri_rotation_drag', text = "Add HDRI Rotation hotkey")

            elif self.ui_tab == 'LIBRARY':
                # Library Paths
                row = box.row(align=True)
                split = row.split(factor = percentage_columns)
                split.label(text = "World HDRI folder:")
                split.prop(self, 'hdri_lib_path', text = '')

                row = box.row(align=True)
                split = row.split(factor = percentage_columns)
                split.label(text = "Optical Vignetting folder:")
                split.prop(self, 'opt_vignetting_lib_path', text = '')

                row = box.row(align=True)
                split = row.split(factor = percentage_columns)
                split.label(text = "Bokeh folder :")
                split.prop(self, 'bokeh_lib_path', text = '')
               
                row = box.row(align=True)
                split = row.split(factor = percentage_columns)
                split.label(text = "Light Gobo folder :")
                split.prop(self, 'gobo_lib_path', text = '')

                row = box.row(align=True)
                split = row.split(factor = percentage_columns)
                split.label(text = "IES Profiles folder :")
                split.prop(self, 'ies_lib_path', text = '')

                row = box.row(align=True)
                split = row.split(factor = percentage_columns)
                split.label(text = "STMaps folder:")
                split.prop(self, 'stmap_lib_path', text = '')

                row = box.row(align=True)
                split = row.split(factor = percentage_columns)
                split.label(text = "Film Grain folder:")
                split.prop(self, 'film_grain_lib_path', text = '')

            elif self.ui_tab == 'CAMERA':
                # # Camera List Sorting
                # row = box.row(align=True)
                # split = row.split(factor=percentage_columns)
                # split.label(text="Default Camera List Sorting :")
                # row = split.row(align=True)
                # row.prop(self, 'default_cam_list_sorting', expand=True)

                # Camera Viewport Display options
                row = box.row(align=True)
                split = row.split(factor=percentage_columns)
                split.label(text="Focus Eyedropper :")
                split.prop(self, 'focus_eyedropper_func', text = '')

                row = box.row(align=True)
                split = row.split(factor=percentage_columns)
                split.label(text="Full Viewport Framing :")
                split.prop(self, 'frame_full_viewport', text = '')

                row = box.row(align=True)
                split = row.split(factor=percentage_columns)
                split.label(text="Fit inside Sensor :")
                split.prop(self, 'fit_inside_sensor', text = '')

                box = layout.box()
                row = box.row(align=True)
                split = row.split(factor=percentage_columns)
                split.label(text="Default Sensor Type :")
                split.prop(self, 'default_sensor_type', text = '')

                row = box.row(align=True)
                split = row.split(factor=percentage_columns)
                split.label(text="Default Clip Start/End :")
                split.prop(self, 'default_clip_start', text = '')
                split.prop(self, 'default_clip_end', text = '')

                row = box.row(align=True)
                split = row.split(factor=percentage_columns)
                split.label(text="Default Passepartout :")
                row = split.row(align=True)
                row.prop(self, 'default_show_passepartout')
                row.prop(self, 'default_passepartout_alpha')

                row = box.row(align=True)
                split = row.split(factor=percentage_columns)
                split.label(text="Default Focus Plane Color :")
                split.prop(self, 'default_focus_plane_color', text = '')
                if bpy.app.version >= (4,2,0):
                    split.prop(self, 'default_focus_plane_edge')

                col = box.column(align=True)
                col.label(text= "Default Composition Guides :")
                row = col.row(align=True)
                split = row.split(factor = 1/4 )
                split.label(text="Thirds / Center :")
                split.prop(self, "show_composition_thirds", text="Thirds")
                split.prop(self, "show_composition_center", text="Center")
                split.prop(self, "show_composition_center_diagonal", text="Diagonal")

                row = col.row(align=True)
                split = row.split(factor = 1/4 )
                split.label(text="Golden :")
                split.prop(self, "show_composition_golden", text="Ratio")
                split.prop(self, "show_composition_golden_tria_a", text="Triangle A")
                split.prop(self, "show_composition_golden_tria_b", text="Triangle B")

                row = col.row(align=True)
                split = row.split(factor = 1/4 )
                split.label(text="Harmony :")
                split.prop(self, "show_composition_harmony_tri_a", text="Triangle A")
                split.prop(self, "show_composition_harmony_tri_b", text="Triangle B")
                split.separator()

                box = layout.box()
                row = box.row(align=True)
                split = row.split(factor=percentage_columns)
                split.label(text="Camera Rig Widget Prefix :")
                split.prop(self, 'widget_prefix', text = '')

                row = box.row(align=True)
                split = row.split(factor=percentage_columns)
                split.label(text="Camera Rig Collection name :")
                split.prop(self, 'camera_widget_collection_name', text = '')

            elif self.ui_tab == 'EXPOSURE':
                # Default Exposure mode
                split = box.split(factor=percentage_columns)
                split.label(text = "Default Exposure Mode :" )
                row = split.row(align=True)
                row.prop(self, 'exposure_mode_pref', expand=True)

                # Use camera values presets or sliders
                row = box.row(align=True)
                split = row.split(factor = percentage_columns)
                split.label(text = "Use Sliders instead of Presets :")
                col2 = split.column()
                row = col2.row()
                row.prop(self, 'shutter_speed_slider_pref')
                row.prop(self, 'aperture_slider_pref')
                row.prop(self, 'iso_slider_pref')

                box = layout.box()
                row = box.row(align=True)
                split = row.split(factor=percentage_columns)
                split.label(text="Exposure Calculation :")
                split.prop(self, 'lens_attenuation')

                row = box.row(align=True)
                split = row.split(factor=percentage_columns)
                split.label(text="")
                split.prop(self, 'aces_ue_match')

                row = box.row(align=True)
                split = row.split(factor=percentage_columns)
                split.label(text="Color Temperature Mode :")
                sub = split.split(factor=0.7)
                sub.prop(self, 'color_temperature_mode', text = '')
                sub.operator('photographer.apply_color_temperature_mode')

                # Reset Exposure or WB options if Camera Exposure/WB is disabled
                box = layout.box()

                row = box.row(align=True)
                split = row.split(factor=percentage_columns)
                split.label(text="When changing cameras :")
                split.prop(self, 'reset_exposure')

                row = box.row(align=True)
                split = row.split(factor=percentage_columns)
                split.label(text="")
                split.prop(self, 'reset_wb')

            elif self.ui_tab == 'LIGHT':
            # Physical lights options
                row = box.row(align=True)
                box.prop(self, 'use_physical_lights',
                text='Use Physical Lights (supported by Cycles, EEVEE, Workbench)')
                col = box.column(align=True)
                if self.use_physical_lights:
                    col.enabled = True
                else:
                    col.enabled = False
                col.prop(self, 'follow_unit_scale')
                col.operator('photographer.update_all_lights_energy')
                col.separator()
                box.prop(self, 'hdri_auto_world_rename')
                box.prop(self, 'hdri_auto_load')

                col = box.column(align=True)
                col.prop(self, 'hide_hdri_meshes')
                row = col.row(align=True)
                row.alignment='LEFT'
                row.label(text='Sun Placement Precision')
                row.prop(self, 'sun_placement_precision', text='')

                col = box.column(align=True)
                col.prop(self, 'hide_unlinked_emissive')

                box = layout.box()
                col = box.column(align=True)

                # Sunlight settings
                if self.use_physical_lights:
                    split = col.split(factor=0.35)
                    split.label(text='Default Sunlight Unit:')
                    split.prop(self,"default_sunlight_unit", text='')
                    split = col.split(factor=0.35)
                    split.label(text='')
                    if self.default_sunlight_unit == 'irradiance':
                        split.prop(self,"default_irradiance")
                    elif self.default_sunlight_unit == 'illuminance':
                        split.prop(self,"default_illuminance")
                        split = col.split(factor=0.35)
                        split.label(text='')
                        split.prop(self, "default_normalizebycolor")
                    elif self.default_sunlight_unit == 'artistic':
                        split.prop(self,"default_intensity")
                        split = col.split(factor=0.35)
                        split.label(text='')
                        split.prop(self,"default_light_exposure")

                elif context.scene.render.engine == 'LUXCORE' and not self.use_physical_lights:
                    split = col.split(factor=0.35)
                    split.label(text='Default Sunlight Type:')
                    split.prop(self,"default_lc_light_type", text='')
                    split = col.split(factor=0.35)
                    split.label(text='')
                    if self.default_lc_light_type == 'sun':
                        split.prop(self,"default_sun_sky_gain")
                    else:
                        split.prop(self,"default_gain")
                    split.prop(self,"default_light_exposure")
                else:
                    split = col.split(factor=0.35)
                    split.label(text='Default Sunlight Intensity:')
                    split.prop(self,"default_irradiance", text = 'Strength')

                col.separator()

                # Other light types settings
                if self.use_physical_lights:
                    split = col.split(factor=0.35)
                    split.label(text='Default Light Unit:')
                    split.prop(self, "default_light_unit", text='')
                    split = col.split(factor=0.35)
                    split.label(text='')
                    if self.default_light_unit == 'artistic':
                        split.prop(self,"default_intensity")
                        split = col.split(factor=0.35)
                        split.label(text='')
                        split.prop(self,"default_light_exposure")

                    elif self.default_light_unit == 'power':
                        split.prop(self,"default_power")

                    elif self.default_light_unit == 'advanced_power':
                        split.prop(self,"default_advanced_power")
                        split = col.split(factor=0.35)
                        split.label(text='')
                        split.prop(self,"default_efficacy")
                        split = col.split(factor=0.35)
                        split.label(text='')
                        split.prop(self,"default_spot_power_conservation")

                    elif self.default_light_unit == 'lumen':
                        split.prop(self,"default_lumen")

                    elif self.default_light_unit == 'candela':
                        split.prop(self,"default_candela")

                    if self.default_light_unit in {'lumen','candela'}:
                        split.prop(self,"default_per_square_meter")
                        split = col.split(factor=0.35)
                        split.label(text='')
                        split.prop(self, "default_normalizebycolor")

                elif context.scene.render.engine == 'LUXCORE' and not self.use_physical_lights:
                    split = col.split(factor=0.35)
                    split.label(text='Default Light Unit:')
                    split.prop(self, "default_lc_light_unit", text='')
                    split = col.split(factor=0.35)
                    split.label(text='')
                    if self.default_lc_light_unit == 'artistic':
                        split.prop(self,"default_gain")
                        split = col.split(factor=0.35)
                        split.label(text='')
                        split.prop(self,"default_light_exposure")

                    elif self.default_lc_light_unit == 'power':
                        split.prop(self,"default_power")
                        split = col.split(factor=0.35)
                        split.label(text='')
                        split.prop(self,"default_efficacy")

                    elif self.default_lc_light_unit == 'lumen':
                        split.prop(self,"default_lumen")

                    elif self.default_lc_light_unit == 'candela':
                        split.prop(self,"default_candela")
                        split.prop(self,"default_per_square_meter")

                    if self.default_lc_light_unit in {'lumen','candela'}:
                        split = col.split(factor=0.35)
                        split.label(text='')
                        split.prop(self, "default_normalizebycolor")
                else:
                    split = col.split(factor=0.35)
                    split.label(text='Default Light Intensity:')
                    split.prop(self,"default_power")

                col.separator()
                col.separator()

                split = col.split(factor=0.35)
                split.label(text='Default EEVEE Light settings:')
                row = split.row(align=True)
                row.prop(self,"default_use_custom_distance")
                row.prop(self,"default_cutoff_distance")

                if bpy.app.version >= (4,2,0):
                    col.separator()
                    split = col.split(factor=0.35)
                    split.label(text='')
                    row = split.row(align=True)
                    row.prop(self, "default_use_shadow_jitter")
                    row.prop(self, "default_shadow_jitter_overblur", text="Overblur")

                    split = col.split(factor=0.35)
                    split.label(text='')
                    split.prop(self, "default_shadow_filter_radius", text="Filter")

                    split = col.split(factor=0.35)
                    split.label(text='')
                    split.prop(self, "default_shadow_maximum_resolution", text="Resolution Limit")

                else:
                    split = col.split(factor=0.35)
                    split.label(text='')
                    split.prop(self,"default_shadow_buffer_bias")

                    col.separator()
                    col.separator()

                    split = col.split(factor=0.35)
                    split.label(text='')
                    row = split.row(align=True)
                    row.prop(self,"default_use_contact_shadow")
                    sub = row.row(align=True)
                    sub.enabled = self.default_use_contact_shadow
                    sub.prop(self,"default_contact_shadow_distance")
                    split = col.split(factor=0.35)
                    split.label(text='')
                    split.enabled = self.default_use_contact_shadow
                    split.prop(self,"default_contact_shadow_bias")
                    split = col.split(factor=0.35)
                    split.label(text='')
                    split.enabled = self.default_use_contact_shadow
                    split.prop(self,"default_contact_shadow_thickness")

            elif self.ui_tab == 'RENDER':
                # Render options
                row = box.row(align=True)
                split = row.split(factor = percentage_columns)
                split.label(text = "Light Sampling Threshold :")
                split.prop(self, 'default_light_threshold', text = '')
                split.prop(self, 'auto_light_threshold', text = 'Auto update')
                split.prop(self, 'hide_light_threshold_warning')

            # Useful links
            box = layout.box()
            row = box.row(align=True)
            row.label(text='Useful links : ')
            row.operator("wm.url_open", text="Documentation").url = "https://sites.google.com/view/photographer-5-documentation"
            row.operator("wm.url_open", text="Video Tutorials").url = "https://www.youtube.com/playlist?list=PLDS3IanhbCIXERthzS7cWG1lnGQwQq5vB"
            row.operator("wm.url_open", text="Blender Artists Forum").url = "https://blenderartists.org/t/addon-photographer-camera-exposure-white-balance-and-autofocus/1101721"
            row = box.row(align=True)
            row.label(text='Free Libraries : ')
            row.operator("wm.url_open", text="PolyHaven HDRIs").url = "https://polyhaven.com/hdris"
            row.operator("wm.url_open", text="IES Library").url = "https://ieslibrary.com"
            row.operator("wm.url_open", text="Gobo Textures [Flora]").url = "https://mschumacher.gumroad.com/l/DkHCV"


def register():
    # Registering Panel classes - Preferences sets bl_category
    context = bpy.context
    addon_prefs = context.preferences.addons[__package__].preferences
    update_photographer_category(addon_prefs,context)
    update_lightmixer_category(addon_prefs,context)
    import_preferences_from_file()

    # Registering hotkey if they haven't been imported from the JSON file
    wm = bpy.context.window_manager
    if wm.keyconfigs.addon:
        kc = wm.keyconfigs.addon

        kmi = None
        if kc.keymaps.get('3D View', False):
            km = kc.keymaps['3D View']
            kmi = get_hotkey_entry_item(km,"wm.call_menu_pie","PHOTOGRAPHER_MT_Pie_Camera")
        if not kmi:
            add_hotkey("3D View",'VIEW_3D','WINDOW',
                "wm.call_menu_pie","PHOTOGRAPHER_MT_Pie_Camera",
                'C', 'PRESS', shift=True, ctrl=True)

        kmi = None
        if kc.keymaps.get('3D View', False):
            km = kc.keymaps['3D View']
            kmi = get_hotkey_entry_item(km, PHOTOGRAPHER_OT_Sticky_Menu.bl_idname,None)
        if not kmi:
            add_hotkey("3D View",'VIEW_3D','WINDOW',
                PHOTOGRAPHER_OT_Sticky_Menu.bl_idname,None,
                'C', 'PRESS', shift=True, ctrl=True, alt=True)
            
        kmi = None
        if kc.keymaps.get('3D View', False):
            km = kc.keymaps['3D View']
            kmi = get_hotkey_entry_item(km, LIGHTMIXER_OT_HDRI_Rotation_Drag.bl_idname, None)
        if not kmi:
            add_hotkey("3D View",'VIEW_3D','WINDOW',
                LIGHTMIXER_OT_HDRI_Rotation_Drag.bl_idname,None,
                'RIGHTMOUSE', 'PRESS', shift=True, alt=True)

def unregister():
    remove_hotkey("3D View")
