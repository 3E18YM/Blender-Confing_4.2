# -*- coding:utf-8 -*-
from ..iBlender_flip_fluids_addon import _z

# Blender FLIP Fluids Add-on
# Copyright (C) 2024 Ryan L. Guy
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import bpy, colorsys, os, json

from bpy.props import (
        BoolProperty,
        StringProperty,
        IntProperty,
        FloatProperty,
        FloatVectorProperty,
        CollectionProperty,
        EnumProperty
        )

from .. import __package__ as base_package

from ..objects import flip_fluid_map
from ..ui import helper_ui
from ..utils import installation_utils
from ..utils import color_utils
from ..utils import version_compatibility_utils as vcu
from ..operators import preferences_operators
from ..filesystem import filesystem_protection_layer as fpl
from .. import types


# Due to a bug in Blender 2.93 (https://developer.blender.org/T87629), preferences
# may not be accessible. In this case, a fake set of preferences can be used in 
# it's place with default values. The values will be populated in 
# FLIPFluidAddonPreferences
FAKE_PREFERENCES = flip_fluid_map.Map({})


def get_addon_preferences(context=None):
    if context is None:
        context = bpy.context

    prefs = vcu.get_blender_preferences(context)
    if vcu.is_blender_42():
        id_name = base_package
        return prefs.addons[id_name].preferences
    else:
        id_name = __name__.split(".")[0]
        if id_name not in prefs.addons:
            global FAKE_PREFERENCES
            return FAKE_PREFERENCES
        return prefs.addons[id_name].preferences

           
     

class FLIPFluidGPUDevice(bpy.types.PropertyGroup):
    conv = vcu.convert_attribute_to_28
    name = StringProperty(); exec(conv("name"))
    description = StringProperty(); exec(conv("description"))
    score = FloatProperty(); exec(conv("score"))


class FLIPFluidColorMixbox(bpy.types.PropertyGroup):
    conv = vcu.convert_attribute_to_28
    color = FloatVectorProperty(default=(0, 0, 0), subtype='COLOR', description="Color mix using Mixbox blending"); exec(conv("color"))


class FLIPFluidColorRGB(bpy.types.PropertyGroup):
    conv = vcu.convert_attribute_to_28
    color = FloatVectorProperty(default=(0, 0, 0), subtype='COLOR', description="Color mix using basic RGB blending"); exec(conv("color"))


def update_helper_category_name(self, context):
    panel_ids = ['FLIPFLUID_PT_HelperPanelMain', 'FLIPFLUID_PT_HelperPanelDisplay', 'FLIPFLUID_PT_HelperTechnicalSupport']
    for pid in panel_ids:
        is_panel_registered = hasattr(bpy.types, pid)
        if is_panel_registered:
            try:
                bpy.utils.unregister_class(getattr(bpy.types, pid))
            except:
                pass

    if self.enable_helper:
        for pid in panel_ids:
            panel = getattr(helper_ui, pid)
            panel.bl_category = self.helper_category_name
            bpy.utils.register_class(panel)


class FLIPFluidAddonPreferences(bpy.types.AddonPreferences):
    global FAKE_PREFERENCES
    if vcu.is_blender_42():
        bl_idname = base_package
    else:
        bl_idname = __name__.split(".")[0]

    def update_language(self, context):
        try:
            bpy.context.preferences.view.language = self.language
            
            if bpy.context.preferences.view.language != "en_US":
                bpy.context.preferences.view.use_translate_new_dataname = False
        
            bpy.ops.script.reload()
        except Exception as e:
            print("Couldn't parse: {}".format(e))

    if 'zh_CN' in bpy.app.translations.locales:
        language: bpy.props.EnumProperty(
            name = _z("Language"),
            description = _z("Language Description"),
            update = update_language,
            default = bpy.context.preferences.view.language if bpy.context.preferences.view.language in ["zh_CN", "zh_TW"] else "en_US",
            items =  [
                ("en_US", "English", "English"),
                # ("es", "Español", "Spanish"),
                # ("it_IT", "Italiano", "Italian"),
                # ("ja_JP", "日本語", "Japanese"),
                ("zh_CN", "简体中文", "Simplified Chinese"),
                ("zh_TW", "繁體中文", "Traditional Chinese"),
                # ("ru_RU", "русский", "Russian"),
                # ("fr_FR", "Français", "French"),
                # ("de_DE", "Deutsch", "German"),
                # ("ko_KR", "한국어(한국)", "Korean")
                # ('pt_PT', 'Português', 'Portuguese'),
                # ('nl_NL', 'Nederlands', 'Dutch'), 
            ]
        )
    else:
        language: bpy.props.EnumProperty(
            name = _z("Language"),
            description = _z("Language Description"),
            update = update_language,
            default = bpy.context.preferences.view.language if bpy.context.preferences.view.language in ["zh_HANS", "zh_HANT"] else "en_US",
            items =  [
                ("en_US", "English", "English"),
                # ("es", "Español", "Spanish"),
                # ("it_IT", "Italiano", "Italian"),
                # ("ja_JP", "日本語", "Japanese"),
                ("zh_HANS", "简体中文", "Simplified Chinese"),
                ("zh_HANT", "繁體中文", "Traditional Chinese"),
                # ("ru_RU", "русский", "Russian"),
                # ("fr_FR", "Français", "French"),
                # ("de_DE", "Deutsch", "German"),
                # ("ko_KR", "한국어(한국)", "Korean")
                # ('pt_PT', 'Português', 'Portuguese'),
                # ('nl_NL', 'Nederlands', 'Dutch'), 
            ]
        )
    

    preferences_menu_view_mode = EnumProperty(
            name=_z("Preferences Menu View"),
            description="Preferences Menu View\nSelect the preferences category to view",
            items=types.preferences_menu_view_modes,
            default='PREFERENCES_MENU_VIEW_GENERAL',
            options={'HIDDEN'},
            ); exec(vcu.convert_attribute_to_28("preferences_menu_view_mode"))

    enable_helper = BoolProperty(
                name=_z("Enable Helper Sidebar"),
                description="Enable Helper Sidebar\nEnable the FLIP Fluid helper menu in the 3D view sidebar."
                    " This menu contains operators to help with workflow and simulation setup",
                default=True,
                update=lambda self, context: self._update_enable_helper(context),
                options={'HIDDEN'},
                )
    exec(vcu.convert_attribute_to_28("enable_helper"))
    FAKE_PREFERENCES.enable_helper = True

    helper_category_name = StringProperty(
                name=_z("Panel Category"),
                description="Panel Category\nChoose a category for the FLIP Fluids helper panel tab in the sidebar",
                default=_z("FLIP Fluids"),
                update=lambda self, context: self._update_helper_category_name(context),
                )
    exec(vcu.convert_attribute_to_28("helper_category_name"))
    FAKE_PREFERENCES.helper_category_name = _z("FLIP Fluids")

    show_documentation_in_ui = BoolProperty(
                name=_z("Display documentation links in UI"),
                description="Display documentation links in UI\nDisplay relevant documentation links within the UI. Documentation links will open in your browser."
                    " This setting is also available from the FLIP Fluids sidebar menu",
                default=True,
                options={'HIDDEN'},
                )
    exec(vcu.convert_attribute_to_28("show_documentation_in_ui"))
    FAKE_PREFERENCES.show_documentation_in_ui = False

    engine_debug_mode = BoolProperty(
            name=_z("Engine Debug Mode"), 
            description="Engine Debug Mode\nEnable to run simulation engine in debug mode (slower, but is able to"
                " generate crash errors). Disabling can speed up simulation by 10% - 15%, but if"
                " a crash is encountered, no error messages will be generated. If encountering a"
                " persistent simulation crash, switch to debug mode and resume to check for error"
                " messages. Error messages are not guaranteed on a crash and will depend on system and"
                " situation. Running with debug mode on or off will not affect simulation results", 
            default=False,
            ); 
    exec(vcu.convert_attribute_to_28("engine_debug_mode"))
    FAKE_PREFERENCES.engine_debug_mode = False

    enable_blend_file_logging = BoolProperty(
            name=_z("Save Blender Installation and Simulation Info to Blend File"), 
            description="Save Blender Installation and Simulation Info to Blend File\nIf enabled, save info about your Blender installation and simulation set up into the"
                " Blend file. Saving this info into the Blend file helps improve turnaround time when requesting"
                " technical support and improves accuracy when diagnosing issues. To view the type of info that is"
                " saved, use the [Help > FLIP Fluids > Copy System & Blend Info] operator. If disabled, this info"
                " will be cleared upon the next save of your Blend file, but it may be required to provide"
                " additional items and info when requesting support", 
            default=True,
            ); 
    exec(vcu.convert_attribute_to_28("enable_blend_file_logging"))
    FAKE_PREFERENCES.enable_blend_file_logging = True

    enable_experimental_build_warning = BoolProperty(
            name=_z("Show Experimental Build Warning"), 
            description="Show Experimental Build Warning\nDisable to hide the experimental build warning/notification in the Physics menu", 
            default=True,
            ); 
    exec(vcu.convert_attribute_to_28("enable_experimental_build_warning"))
    FAKE_PREFERENCES.enable_experimental_build_warning = True

    enable_developer_tools = BoolProperty(
            name=_z("Enable Developer Tools"), 
            description="Enable Developer Tools\nEnable to unlock developer tools and hidden features. Enable to unlock features"
                " that may be experimental or considered unstable for rendering due to current bugs in Blender."
                " Rendering issues can be completely avoided by rendering from the command line", 
            default=False,
            ); 
    exec(vcu.convert_attribute_to_28("enable_developer_tools"))
    FAKE_PREFERENCES.enable_developer_tools = False

    enable_support_tools = BoolProperty(
            name=_z("Enable Technical Support Tools"), 
            description="Enable Technical Support Tools\nUsed by the developers to assist in technical support requests", 
            default=False,
            ); 
    exec(vcu.convert_attribute_to_28("enable_support_tools"))
    FAKE_PREFERENCES.enable_support_tools = False

    cmd_save_blend_file_before_launch = BoolProperty(
            name=_z("Autosave Blend file before launching command line operators"), 
            description="Autosave Blend file before launching command line operators\nCommand line operators require the Blend file to be saved for changes to take effect when using command"
            " line operators. If enabled, the Blend file will be automatically saved when using command line operators so that"
            " manual saving is not necessary", 
            default=True,
            ); 
    exec(vcu.convert_attribute_to_28("cmd_save_blend_file_before_launch"))
    FAKE_PREFERENCES.cmd_save_blend_file_before_launch = True

    cmd_bake_max_attempts = IntProperty(
            name=_z("Max Attempts"),
            description="Max Attempts\nWhen using the command line baking operator, if a bake fails due to a crash or an error, attempt"
                " to automatically re-launch and resume the baking process. This value is the maximum number of attempts that"
                " the addon will try to resume the baking process. Set a value greater than 0 to activate. Only supported on Windows OS",
            min=0,
            default=5,
            options={'HIDDEN'},
            )
    exec(vcu.convert_attribute_to_28("cmd_bake_max_attempts"))
    FAKE_PREFERENCES.cmd_bake_max_attempts = False

    enable_bake_alarm = BoolProperty(
            name=_z("Play alarm after simulation finishes"), 
            description="Play alarm after simulation finishes\nPlay an alarm sound when the simulation baking process completes. The alarm will sound on both a"
                " successful bake as well as a bake where an error is encountered. This feature may not work correctly if"
                " a crash is encountered", 
            default=False,
            ); 
    exec(vcu.convert_attribute_to_28("enable_bake_alarm"))
    FAKE_PREFERENCES.enable_experimental_build_warning = False

    enable_presets = BoolProperty(
                name=_z("Enable Presets"),
                description="Enable Presets\nPresets are a deprecated feature that will no longer be updated. Enable to use the older preset"
                    " features, but be aware that you may encounter bugs or issues. Use at your own risk. Blender must be"
                    " restarted after enabling this option. See documentation for more info and future plans",
                default=False,
                options={'HIDDEN'},
                )
    exec(vcu.convert_attribute_to_28("enable_presets"))
    FAKE_PREFERENCES.enable_presets = False

    selected_gpu_device = EnumProperty(
                name=_z("GPU Compute Device"),
                description="GPU Compute Device\nDevice that will be used for GPU acceleration features",
                items=lambda self, context=None: self._get_gpu_device_enums(context),
                )
    exec(vcu.convert_attribute_to_28("selected_gpu_device"))
    FAKE_PREFERENCES.selected_gpu_device = None

    gpu_devices = CollectionProperty(type=FLIPFluidGPUDevice)
    exec(vcu.convert_attribute_to_28("gpu_devices"))
    FAKE_PREFERENCES.gpu_devices = []

    is_gpu_devices_initialized = BoolProperty(False)
    exec(vcu.convert_attribute_to_28("is_gpu_devices_initialized"))
    FAKE_PREFERENCES.is_gpu_devices_initialized = False

    show_mixbox_menu = BoolProperty(default=False)
    exec(vcu.convert_attribute_to_28("show_mixbox_menu"))
    FAKE_PREFERENCES.show_mixbox_menu = False

    is_mixbox_installation_error = BoolProperty(default=False)
    exec(vcu.convert_attribute_to_28("is_mixbox_installation_error"))
    FAKE_PREFERENCES.is_mixbox_installation_error = False

    mixbox_installation_error_message = StringProperty(default="")
    exec(vcu.convert_attribute_to_28("mixbox_installation_error_message"))
    FAKE_PREFERENCES.mixbox_installation_error_message = ""

    mixbox_color1 = FloatVectorProperty(  
                name=_z("Color 1"),
                subtype='COLOR',
                default=(0.0, 0.0, 0.24),
                min=0.0, max=1.0,
                description="Color 1\nColor Input 1",
                update=lambda self, context: self._update_mixbox_color_test(context),
                ); exec(vcu.convert_attribute_to_28("mixbox_color1"))

    mixbox_color2 = FloatVectorProperty(  
                name=_z("Color 2"),
                subtype='COLOR',
                default=(0.7, 0.7, 0.0),
                min=0.0, max=1.0,
                description="Color 2\nColor Input 2",
                update=lambda self, context: self._update_mixbox_color_test(context),
                ); exec(vcu.convert_attribute_to_28("mixbox_color2"))

    num_gradient_samples = IntProperty(default=25)
    exec(vcu.convert_attribute_to_28("num_gradient_samples"))
    FAKE_PREFERENCES.num_gradient_samples = 0

    mixbox_gradient_result = CollectionProperty(type=FLIPFluidColorMixbox)
    exec(vcu.convert_attribute_to_28("mixbox_gradient_result"))
    FAKE_PREFERENCES.mixbox_gradient_result = []

    rgb_gradient_result = CollectionProperty(type=FLIPFluidColorRGB)
    exec(vcu.convert_attribute_to_28("rgb_gradient_result"))
    FAKE_PREFERENCES.rgb_gradient_result = []

    test_mixbox_expanded = BoolProperty(
                default=False, 
                update=lambda self, context: self._update_mixbox_color_test(context)
                ); 
    exec(vcu.convert_attribute_to_28("test_mixbox_expanded"))

    preset_library_install_mode = EnumProperty(
            name=_z("Preset Library Install Method"),
            description="Preset Library Install Method\nInstallation Method",
            items=types.preset_library_install_modes,
            default='PRESET_LIBRARY_INSTALL_ZIP',
            options={'HIDDEN'},
            ); exec(vcu.convert_attribute_to_28("preset_library_install_mode"))
    
    addon_filepath = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    
    preset_library_install_location = StringProperty(
            name="",
            description="Select a location to install the Preset Scenes Library."
                " This should be a location on your system where you have read and write file permissions",
            default=os.path.join(addon_filepath, "PresetsLibrary"),
            subtype='DIR_PATH',
            ); 
    exec(vcu.convert_attribute_to_28("preset_library_install_location"))
    FAKE_PREFERENCES.preset_library_install_location = os.path.join(addon_filepath, "PresetsLibrary")

    is_preset_library_installation_error = BoolProperty(default=False)
    exec(vcu.convert_attribute_to_28("is_preset_library_installation_error"))
    FAKE_PREFERENCES.is_preset_library_installation_error = False

    preset_library_installation_error_message = StringProperty(default="")
    exec(vcu.convert_attribute_to_28("preset_library_installation_error_message"))
    FAKE_PREFERENCES.preset_library_installation_error_message = ""

    preset_library_installations_expanded = BoolProperty(default=True); 
    exec(vcu.convert_attribute_to_28("preset_library_installations_expanded"))

    dismiss_T88811_crash_warning = BoolProperty(
            name=_z("Dismiss render crash bug warnings"), 
            description="Dismiss render crash bug warnings\nDismiss warnings in UI when features are enabled that can trigger a"
                " bug in Blender (T88811) that can cause frequent render crashes or incorrect"
                " renders. The workaround to this issue is to render from the command line. See"
                " the FLIP Fluids sidebar helper menu for tools to help automatically launch a"
                " cmd render. This option can be reset in the addon preferences", 
            default=False,
            ); 
    exec(vcu.convert_attribute_to_28("dismiss_T88811_crash_warning"))
    FAKE_PREFERENCES.dismiss_T88811_crash_warning = False

    dismiss_persistent_data_render_warning = BoolProperty(
            name=_z("Dismiss persistent data warnings"), 
            description="Dismiss persistent data warnings\nDismiss warnings in UI when the Cycles Persistent Data option is enabled."
            " This render option is not compatible with the simulation meshes and can cause render"
            " crashes, incorrect renders, or static renders. The workaround to this issue is to"
            " disable the 'Render Properties > Performance > Persistent Data' option or to render"
            " from the command line. See the FLIP Fluids sidebar helper menu for tools to help"
            " automatically launch a cmd render. This option can be reset in the addon preferences", 
            default=False,
            ); 
    exec(vcu.convert_attribute_to_28("dismiss_persistent_data_render_warning"))
    FAKE_PREFERENCES.dismiss_persistent_data_render_warning = False

    dismiss_rtx_driver_warning = BoolProperty(
            name=_z("Dismiss NVIDIA GeForce RTX Driver Warning"), 
            description="Dismiss NVIDIA GeForce RTX Driver Warning\nDismiss warning in the FLIP Fluids preferences menu related to a recent NVIDIA"
                " GeForce RTX 'Game Ready Driver' update that may cause Blender to crash frequently when baking"
                " a simulation. If you are experiencing this issue, the current solution is to update to"
                " the NVIDIA 'Studio Driver' version. Studio drivers are typically more stable for content"
                " creation software",
            default=False,
            ); 
    exec(vcu.convert_attribute_to_28("dismiss_rtx_driver_warning"))
    FAKE_PREFERENCES.dismiss_rtx_driver_warning = False

    dismiss_export_animated_mesh_parented_relation_hint = BoolProperty(
            name=_z("Dismiss 'Export Animated Mesh' parented relation hint"), 
            description="Dismiss 'Export Animated Mesh' parented relation hint\nDismiss hints about enabling 'Export Animated Mesh' in the FLIP object UI"
                " when parented relations are detected. The 'Export Animated Mesh' option is required"
                " for any animation that is more complex than just keyframed loc/rot/scale or F-Curves,"
                " such as parented relations, armatures, animated modifiers, deformable meshes, etc."
                " This option is not needed for static objects",
            default=False,
            ); 
    exec(vcu.convert_attribute_to_28("dismiss_export_animated_mesh_parented_relation_hint"))
    FAKE_PREFERENCES.dismiss_export_animated_mesh_parented_relation_hint = False

    enable_tabbed_domain_settings_view = BoolProperty(
                name=_z("Enable Tabbed Domain Settings"),
                description="Enable Tabbed Domain Settings\nEnable tabbed domain settings view. If enabled, domain panel categories will be displayed"
                    " using a tab header selector. If disabled, the classic view will display all domain panel categories"
                    " in a vertical stack",
                default=True,
                options={'HIDDEN'},
                )
    exec(vcu.convert_attribute_to_28("enable_tabbed_domain_settings_view"))
    FAKE_PREFERENCES.enable_tabbed_domain_settings_view = True


    def is_developer_tools_enabled(self):
        return self.enable_developer_tools or installation_utils.is_experimental_build()


    def _update_enable_helper(self, context):
        update_helper_category_name(self, context)


    def _update_helper_category_name(self, context):
        update_helper_category_name(self, context)


    def _update_mixbox_color_test(self, context):
        c1 = self.mixbox_color1
        c2 = self.mixbox_color2

        if len(self.mixbox_gradient_result) != self.num_gradient_samples:
            self.mixbox_gradient_result.clear()
            for i in range(self.num_gradient_samples):
                self.mixbox_gradient_result.add()

        if len(self.rgb_gradient_result) != self.num_gradient_samples:
            self.rgb_gradient_result.clear()
            for i in range(self.num_gradient_samples):
                self.rgb_gradient_result.add()

        tstep = 1.0 / (self.num_gradient_samples - 1)
        for i in range(self.num_gradient_samples):
            t = i * tstep
            r, g, b = color_utils.mixbox_lerp_srgb32f(c1[0], c1[1], c1[2], c2[0], c2[1], c2[2], t)

            saturation_factor = installation_utils.get_mixbox_boost_factor()
            h, s, v = colorsys.rgb_to_hsv(r, g, b)
            s = min(s * saturation_factor, 1.0)
            r, g, b = colorsys.hsv_to_rgb(h, s, v)

            self.mixbox_gradient_result[i].color = (r, g, b)

            r = (1.0 - t) * c1[0] + t * c2[0]
            g = (1.0 - t) * c1[1] + t * c2[1]
            b = (1.0 - t) * c1[2] + t * c2[2]
            self.rgb_gradient_result[i].color = (r, g, b)


    def draw_mixbox_menu(self, context):
        preferences = vcu.get_addon_preferences()
        preferences.show_mixbox_menu = True
        if not preferences.show_mixbox_menu:
            return

        is_installed = installation_utils.is_mixbox_installation_complete()

        box = self.layout.box()
        column = box.column(align=True)
        column.label(text=_z("Install Mixbox Color Blending Plugin:"))

        if not self.is_developer_tools_enabled():
            if installation_utils.is_mixbox_supported():
                column.label(text=_z("Activate the 'Enable Developer Tools' option to access this feature:"), icon='INFO')

                row = column.row(align=True)
                row.alignment = 'LEFT'
                row.prop(self, "enable_developer_tools")
                row.operator(
                    "wm.url_open", 
                    text=_z("What are the developer tools and hidden features?"), 
                    icon="URL"
                ).url = "https://github.com/rlguy/Blender-FLIP-Fluids/wiki/Preferences-Menu-Settings#developer-tools"

                column.separator()
                column.operator(
                    "wm.url_open", 
                    text=_z("Mixbox Installation Instructions"), 
                    icon="URL"
                ).url = "https://github.com/rlguy/Blender-FLIP-Fluids/wiki/Mixbox-Installation-and-Uninstallation"
                return

        if not installation_utils.is_mixbox_supported():
            column.label(text=_z("Mixbox color blending features are not supported in this version of the FLIP Fluids addon."), icon="ERROR")
            column.label(text=_z("These features are only available in the full version."), icon="ERROR")
            row = column.row(align=True)
            row.alignment = 'LEFT'
            row.label(text=_z("Learn more about the Mixbox pigment mixing technology here: "), icon='INFO')
            row = row.row(align=True)
            row.operator(
                "wm.url_open", 
                text="", 
                icon="URL"
            ).url = "https://scrtwpns.com/mixbox/"
            return
        
        if not vcu.is_blender_293():
            box.label(text=_z("Blender 2.93 or later is required for this feature"), icon='ERROR')

        column = box.column(align=True)
        column.enabled = vcu.is_blender_293()
        if not is_installed:
            subbox = column.box()
            sub_column = subbox.column(align=True)
            sub_column.label(text=_z("Install the FLIP Fluids Mixbox Plugin to enable physically accurate color mixing and blending features."))
            row = sub_column.row(align=True)
            row.alignment = 'LEFT'
            row.label(text=_z("Learn more about the Mixbox pigment mixing technology here: "), icon='INFO')
            row = row.row(align=True)
            row.operator(
                "wm.url_open", 
                text="", 
                icon="URL"
            ).url = "https://scrtwpns.com/mixbox/"

            sub_column.label(text=_z("The Mixbox plugin installation file can be found in FLIP Fluids addon downloads labeled as <Mixbox.plugin>."), icon="INFO")
            sub_column.label(text=_z("Use the operator below to select and install the Mixbox.plugin file."), icon='INFO')

        subbox = column.box()
        sub_column = subbox.column(align=True)
        split = sub_column.split()
        column_left = split.column(align=True)
        column_right = split.column()

        if is_installed:
            column_left.operator("flip_fluid_operators.uninstall_mixbox_plugin", text=_z("Uninstall Mixbox Plugin"))
        else:
            column_left.operator("flip_fluid_operators.install_mixbox_plugin", text=_z("Install Mixbox Plugin"))
            column_left.separator()
            column_left.operator(
                        "wm.url_open", 
                        text=_z("Mixbox Installation Instructions"), 
                        icon="URL"
                    ).url = "https://github.com/rlguy/Blender-FLIP-Fluids/wiki/Mixbox-Installation-and-Uninstallation"

        if is_installed:
            column_right.label(text=_z("Status: Installed"), icon="CHECKMARK")
        else:
            column_right.alert = True
            column_right.label(text=_z("Status: Not Installed"), icon="CANCEL")

        if not is_installed and preferences.is_mixbox_installation_error:
            errmsg = preferences.mixbox_installation_error_message
            sub_column = subbox.column(align=True)
            sub_column.alert = True
            sub_column.label(text=errmsg, icon='ERROR')

        if is_installed:
            enable_mixing_widget = True
            if enable_mixing_widget:
                column.separator()
                subbox = column.box()

                row = subbox.row(align=True)
                row.prop(preferences, "test_mixbox_expanded",
                    icon="TRIA_DOWN" if preferences.test_mixbox_expanded else "TRIA_RIGHT",
                    icon_only=True, 
                    emboss=False
                )
                row.alignment = "LEFT"
                row.label(text=_z("Test Mixbox:"))

                if not preferences.test_mixbox_expanded:
                    row.prop(preferences, "mixbox_color1", text="")
                    row.prop(preferences, "mixbox_color2", text="")
                    row.label(text=_z("(Expand to see gradient)"))

                if preferences.test_mixbox_expanded:
                    sub_column = subbox.column(align=True)

                    split = vcu.ui_split(sub_column, factor=1/8)
                    column1 = split.column(align=True)
                    column2 = split.column(align=True)

                    row = column2.row(align=True)
                    row.label(text=_z("Gradient Color1"))
                    row.label(text=_z("Gradient Color2"))

                    row = column2.row(align=True)
                    row.prop(preferences, "mixbox_color1", text="")
                    row.prop(preferences, "mixbox_color2", text="")

                    sub_column.separator()

                    split = vcu.ui_split(sub_column, factor=1/8)
                    column1 = split.column(align=True)
                    column2 = split.column(align=True)

                    if len(self.mixbox_gradient_result) > 0:
                        column1.label(text="Mixbox:")
                        column1.label(text="RGB:")

                    row = column2.row(align=True)
                    for i in range(len(self.mixbox_gradient_result)):
                        c = self.mixbox_gradient_result[i]
                        row.prop(c, "color", text="")

                    row = column2.row(align=True)
                    for i in range(len(self.rgb_gradient_result)):
                        c = self.rgb_gradient_result[i]
                        row.prop(c, "color", text="")

                    sub_column = subbox.column(align=True)
                    row = sub_column.row(align=True)
                    row.alignment = 'LEFT'
                    row.label(text=_z("Learn more about the Mixbox pigment mixing technology here: "), icon='INFO')
                    row = row.row(align=True)
                    row.operator(
                        "wm.url_open", 
                        text="", 
                        icon="URL"
                    ).url = "https://scrtwpns.com/mixbox/"


    def get_date_string(self, dd, mm, yyyy):
        month_to_str = {}
        month_to_str[1] = "jan"
        month_to_str[2] = "feb"
        month_to_str[3] = "mar"
        month_to_str[4] = "apr"
        month_to_str[5] = "may"
        month_to_str[6] = "jun"
        month_to_str[7] = "jul"
        month_to_str[8] = "aug"
        month_to_str[9] = "sep"
        month_to_str[10] = "oct"
        month_to_str[11] = "nov"
        month_to_str[12] = "dec"

        date_str = "(" + str(dd).zfill(2) + "-" + month_to_str[int(mm)] + "-" + str(yyyy) + ")"
        return date_str


    def draw_preset_library_menu(self, context):
        box = self.layout.box()

        box.operator('flip_fluid_operators.install_asset_library', icon = "ASSET_MANAGER")
        
        box = self.layout.box()
        box.label(text=_z("Install Preset Scenes Library:"))

        if not vcu.is_blender_33():
            box.label(text=_z("Blender 3.3 or later is required for this feature"), icon="ERROR")

        subbox = box.box()
        column = subbox.column(align=True)
        column.label(text=_z("This is an initial test phase for the new Preset Library integration into the"), icon="INFO")
        column.label(text=_z("Blender Asset Browser. Read more about this feature and known limitations here:"), icon="INFO")
        column.operator(
                "wm.url_open", 
                text=_z("Preset Library Installation and Notes"), 
                icon="URL"
                ).url = "https://github.com/rlguy/Blender-FLIP-Fluids/wiki/Preset-Library-Installation-and-Uninstallation"

        column = box.column(align=True)
        column.enabled = vcu.is_blender_33()

        row = column.row()
        row.prop(self, "preset_library_install_mode", expand=True)

        subbox = box.box()
        column = subbox.column(align=True)

        if self.preset_library_install_mode == 'PRESET_LIBRARY_INSTALL_ZIP':
            column.label(text=_z("1. Select an install location"))
            column.prop(self, "preset_library_install_location")

            location_text1 = ""
            location_text2 = ""
            if not self.preset_library_install_location:
                location_text1 = _z("No install location selected")
            else:
                install_path = os.path.join(self.preset_library_install_location, "FLIP_Fluids_Addon_Presets")
                location_text1 = _z("Preset Scenes Library will be installed to:")
                location_text2 = " "*12 + install_path

            column.label(text=location_text1, icon='INFO')
            if location_text2:
                row = column.row(align=True)
                row.enabled = False
                row.label(text=location_text2)
            else:
                column.label(text="")
            column.separator()

            split = column.split(align=True)
            column_left = split.column(align=True)
            column_right = split.column(align=True)

            column_left.label(text=_z("2. Select and install Preset Scenes zip file"))
            column_left.operator("flip_fluid_operators.install_preset_library", text=_z("Install Preset Scenes Library"))

            is_installed = installation_utils.is_preset_library_installation_complete()
            column_right.label(text="")
            if is_installed:
                column_right.label(text=_z("Status: Installed"), icon="CHECKMARK")
            else:
                column_right.alert = True
                column_right.label(text=_z("Status: Not Installed"), icon="CANCEL")

            if self.is_preset_library_installation_error:
                errmsg = self.preset_library_installation_error_message
                sub_column = subbox.column(align=True)
                sub_column.alert = True
                sub_column.label(text=errmsg, icon='ERROR')
        else:
            split = column.split(align=True)
            column_left = split.column(align=True)
            column_right = split.column(align=True)

            column_left.operator("flip_fluid_operators.select_preset_library_folder", text=_z("Select Preset Library Folder"))

            is_installed = installation_utils.is_preset_library_installation_complete()
            if is_installed:
                column_right.label(text=_z("Status: Installed"), icon="CHECKMARK")
            else:
                column_right.alert = True
                column_right.label(text=_z("Status: Not Installed"), icon="CANCEL")

            if self.is_preset_library_installation_error:
                errmsg = self.preset_library_installation_error_message
                sub_column = subbox.column(align=True)
                sub_column.alert = True
                sub_column.label(text=errmsg, icon='ERROR')

        is_installed = installation_utils.is_preset_library_installation_complete()
        if is_installed:
            box.separator()
            subbox = box.box()

            row = subbox.row(align=True)
            row.prop(self, "preset_library_installations_expanded",
                icon="TRIA_DOWN" if self.preset_library_installations_expanded else "TRIA_RIGHT",
                icon_only=True, 
                emboss=False
            )
            row.alignment = "LEFT"

            preset_library_installations = installation_utils.get_preset_library_installations()
            if len(preset_library_installations) > 1:
                box_label = _z("Preset Library Installations:")
            else:
                box_label = _z("Preset Library Installation:")

            row.label(text=box_label)

            if self.preset_library_installations_expanded:
                for install_info in preset_library_installations:
                    name = install_info["name"]
                    path = install_info["path"]
                    metadata = install_info["metadata"]
                    date_string = self.get_date_string(metadata["date_dd"], metadata["date_mm"], metadata["date_yyyy"])

                    install_box = subbox.box()
                    column = install_box.column(align=True)
                    row = column.row(align=True)
                    row.label(text=name + " " + date_string, icon='KEYTYPE_BREAKDOWN_VEC')
                    row = row.row(align=True)
                    row.alignment = 'RIGHT'
                    row.operator("flip_fluid_operators.preset_library_copy_install_location", 
                            text=_z("Copy Install Location"), 
                            icon='COPYDOWN'
                            ).install_location = install_info["install_path"]
                    row = row.row(align=True)
                    row.alignment = 'RIGHT'
                    row.alert = True
                    op = row.operator("flip_fluid_operators.uninstall_preset_library", text=_z("Uninstall"), icon='X')
                    op.install_info_json_string = json.dumps(install_info)

                    row = column.row(align=True)
                    row.operator("wm.path_open", 
                            text="", 
                            icon='FILE_FOLDER'
                            ).filepath = install_info["path"]
                    row = row.row(align=True)
                    row.enabled = False
                    row.label(text=_z("    Path: ") + path)


    def draw_preferences_notifications(self, context):
        is_installation_complete = installation_utils.is_installation_complete()
        column = self.layout.column(align=True)
        if not is_installation_complete:
            box = column.box()
            box.label(text=_z("IMPORTANT: Please Complete Installation"), icon='ERROR')
            row = box.row(align=True)
            row.alignment = 'LEFT'
            row.label(text=_z("To complete installation of the FLIP Fluids addon, click here: "))
            row.operator("flip_fluid_operators.complete_installation", icon='MOD_FLUIDSIM')
            box.label(text=_z("Or you may restart Blender to complete installation"))
            box.label(text=_z("Full preferences menu will become available after the installation is complete"))
            box.operator(
                    "wm.url_open", 
                    text=_z("FLIP Fluids Addon Installation Instructions"), 
                    icon="URL"
                ).url = "https://github.com/rlguy/Blender-FLIP-Fluids/wiki/Addon-Installation-and-Uninstallation"


    def draw_general_preferences_menu(self, context):
        is_installation_complete = installation_utils.is_installation_complete()

        box = self.layout.box()
        box.enabled = is_installation_complete
        helper_column = box.column(align=True)
        helper_column.label(text=_z("UI Options:"))
        helper_column.prop(self, "enable_tabbed_domain_settings_view")
        helper_column.prop(self, "show_documentation_in_ui")

        row = helper_column.row()
        row.alignment = 'LEFT'
        row.prop(self, "enable_helper")
        row = row.row()
        row.alignment = 'LEFT'
        row.enabled = self.enable_helper
        row.prop(self, "helper_category_name")
        helper_column.separator()

        box = self.layout.box()
        box.enabled = is_installation_complete
        helper_column = box.column(align=True)
        helper_column.label(text=_z("Command Line Tools:"))
        row = helper_column.row(align=True)
        row.prop(self, "cmd_save_blend_file_before_launch")
        row = helper_column.row(align=True)
        row.alignment = 'LEFT'
        row.label(text=_z("Re-launch bake after crash:"), icon='FILE_REFRESH')
        row.prop(self, "cmd_bake_max_attempts")
        row.label(text="")
        helper_column.separator()

        if vcu.is_blender_28():
            box = self.layout.box()
            box.enabled = is_installation_complete
            helper_column = box.column(align=True)
            helper_column.label(text=_z("Sounds:"))
            row = helper_column.row(align=True)
            row.alignment = 'LEFT'
            row.prop(self, "enable_bake_alarm")
            row.operator("flip_fluid_operators.test_bake_alarm", icon='PLAY_SOUND')

        box = self.layout.box()
        box.enabled = is_installation_complete
        helper_column = box.column(align=True)
        helper_column.label(text=_z("Experimental and Extra Features:"))

        if installation_utils.is_experimental_build():
            helper_column.prop(self, "enable_experimental_build_warning")

        row = helper_column.row(align=True)
        row.alignment = 'LEFT'
        row.prop(self, "enable_developer_tools")
        row.operator(
            "wm.url_open", 
            text=_z("What are the developer tools and hidden features?"), 
            icon="URL"
        ).url = "https://github.com/rlguy/Blender-FLIP-Fluids/wiki/Preferences-Menu-Settings#developer-tools"

        helper_column.prop(self, "engine_debug_mode")
        helper_column.prop(self, "enable_blend_file_logging")
        helper_column.prop(self, "enable_support_tools")

        box = self.layout.box()
        box.enabled = is_installation_complete
        column = box.column()
        column.label(text=_z("Warnings and Errors:"))

        split = vcu.ui_split(column, factor=0.666, align=True)
        column_left = split.column(align=True)
        column_right = split.column(align=True)

        row = column_left.row(align=True)
        row.alignment = 'LEFT'
        row.prop(self, "dismiss_T88811_crash_warning")

        row = column_left.row(align=True)
        row.alignment = 'LEFT'
        row.prop(self, "dismiss_persistent_data_render_warning")

        row = column_right.row(align=True)
        row.alignment = 'EXPAND'
        row.operator(
                "wm.url_open", 
                text=_z("Bug Report: T88811"), 
            ).url = "https://projects.blender.org/blender/blender/issues/88811"

        row = column_right.row(align=True)
        row.alignment = 'EXPAND'
        row.operator(
                "wm.url_open", 
                text=_z("Related Bug Reports"), 
            ).url = "https://projects.blender.org/blender/blender/issues?type=all&state=open&labels=&milestone=0&project=0&assignee=0&poster=0&q=Persistent+Data"

        row = column_left.row(align=True)
        row.alignment = 'LEFT'
        row.prop(self, "dismiss_export_animated_mesh_parented_relation_hint")

        row = column_right.row(align=True)
        row.alignment = 'EXPAND'
        row.operator(
                "wm.url_open", 
                text=_z("Mesh Export Documentation"), 
            ).url = "https://github.com/rlguy/Blender-FLIP-Fluids/wiki/Obstacle-Object-Settings#mesh-data-export"


    def draw_support_preferences_menu(self, context):
        box = self.layout.box()
        column = box.column(align=True)
        split = column.split(factor=0.7)
        column_left = split.column(align=True)
        column_right = split.column()
        
        column_left.label(text=_z("Help and Support:"))
        column_left.operator(
                "wm.url_open", 
                text=_z("Frequently Asked Questions"), 
                icon="URL"
            ).url = "https://github.com/rlguy/Blender-FLIP-Fluids/wiki/Frequently-Asked-Questions"
        column_left.operator(
                "wm.url_open", 
                text=_z("Scene Troubleshooting Tips"), 
                icon="URL"
            ).url = "https://github.com/rlguy/Blender-FLIP-Fluids/wiki/Scene-Troubleshooting"
        column_left.operator(
                "wm.url_open", 
                text=_z("Example Scenes"), 
                icon="URL"
            ).url = "https://github.com/rlguy/Blender-FLIP-Fluids/wiki/Example-Scene-Descriptions"
        column_left.operator(
                "wm.url_open", 
                text=_z("Tutorials and Learning Resources"), 
                icon="URL"
            ).url = "https://github.com/rlguy/Blender-FLIP-Fluids/wiki/Video-Learning-Series"
        column_left.separator()

        row = column_left.row(align=True)
        row.operator(
                "wm.url_open", 
                text=_z("Support Form"), 
                icon="URL"
            ).url = "https://flipfluids.com/support/"
        row = row.row(align=True)
        row.alignment = 'RIGHT'
        row.operator(
                "wm.url_open", 
                text=_z("Support Tips Guide"), 
                icon="RENDER_ANIMATION"
            ).url = "https://youtu.be/tZegjrdYJts"

        box = self.layout.box()
        column = box.column(align=True)
        split = column.split(factor=0.7)
        column_left = split.column(align=True)
        column_right = split.column()
        column_left.label(text=_z("Report a Bug:"))
        column_left.operator(
                "wm.url_open", 
                text=_z("Bug Report Guidelines"), 
                icon="URL"
            ).url = "https://github.com/rlguy/Blender-FLIP-Fluids/wiki/Guidelines-for-Reporting-Bugs-and-Issues"
        column_left.operator("flip_fluid_operators.report_bug_prefill", icon="URL")
        column_left.operator("flip_fluid_operators.copy_system_info", icon="COPYDOWN")

        column = box.column(align=True)
        column.label(text=_z("Reports can also be sent through official marketplaces or to support@flipfluids.com"))

        box = self.layout.box()
        column = box.column(align=True)
        split = column.split(factor=0.7)
        column_left = split.column(align=True)
        column_right = split.column()

        column_left.label(text=_z("Info and Links:"))
        column_left.operator(
                "wm.url_open", 
                text=_z("Documentation and Wiki"), 
                icon="URL"
            ).url = "https://github.com/rlguy/Blender-FLIP-Fluids/wiki"
        column_left.operator(
                "wm.url_open", 
                text=_z("Recommended Documentation Topics"), 
                icon="URL"
            ).url = "https://github.com/rlguy/Blender-FLIP-Fluids/wiki#the-most-important-documentation-topics"
        column_left.operator(
                "wm.url_open", 
                text=_z("FLIP Fluids Homepage"), 
                icon="URL"
            ).url = "http://flipfluids.com"

        column_left.separator()
        row = column_left.row(align=True)
        row.operator(
                "wm.url_open", 
                text="YouTube", 
            ).url = "https://www.youtube.com/FLIPFluids"
        # row.operator(
        #         "wm.url_open", 
        #         text="Instagram", 
        #     ).url = "https://www.instagram.com/flip.fluids/"
        # row.operator(
        #         "wm.url_open", 
        #         text="Twitter", 
        #     ).url = "https://twitter.com/flipfluids"
        # row.operator(
        #         "wm.url_open", 
        #         text="Facebook", 
        #     ).url = "https://www.facebook.com/FLIPFluids"
        
        # row = column_left.row(align=True)
        # row.operator(
        #         "wm.url_open", 
        #         text=_z("Discord Server"), 
        #     ).url = "https://discord.gg/FLIPFluids"



    def draw(self, context):

        layout = self.layout
        box = layout.box()       

        box.prop(self, "language")

        box.label(text=_z("Translation is in progress. Whole text isn't translated"))

        row = self.layout.row()
        row.operator("wm.url_open", text=_z("Watch online video tutorials")).url = "https://www.bilibili.com/video/BV17k4y1g7PN/"
        row.operator("wm.url_open", text=_z("Chat Room")).url = "http://qm.qq.com/cgi-bin/qm/qr?_wv=1027&k=LOP7dt3N9TrKLQTzU0hO_rgqr_rOl8sb&authKey=iOM7p2Juuj%2BURJffZXBYNhSfdnb9TPjI5mAG1um2h8KSJJj1hsLNxFL%2BiyY%2BjgOu&noverify=0&group_code=242343175"
        row.operator("wm.url_open", text=_z("Buy More")).url = "https://mesh.taobao.com/"

        self.draw_preferences_notifications(context)

        row = self.layout.row(align=True)
        row.prop(self, "preferences_menu_view_mode", expand=True)

        if self.preferences_menu_view_mode == 'PREFERENCES_MENU_VIEW_GENERAL':
            self.draw_general_preferences_menu(context)
        elif self.preferences_menu_view_mode == 'PREFERENCES_MENU_VIEW_MIXBOX':
            self.draw_mixbox_menu(context)
        elif self.preferences_menu_view_mode == 'PREFERENCES_MENU_VIEW_PRESETS':
            self.draw_preset_library_menu(context)
        elif self.preferences_menu_view_mode == 'PREFERENCES_MENU_VIEW_SUPPORT':
            self.draw_support_preferences_menu(context)


    def _get_gpu_device_enums(self, context=None):
        device_enums = []
        for d in self.gpu_devices:
            device_enums.append((d.name, d.name, d.description))
        return device_enums

class FLIPFluidSetupAssetBrowser(bpy.types.Operator):
    
    bl_idname = "flip_fluid_operators.install_asset_library"
    bl_label = _z("Install Asset Library")
    bl_description = "Love from iBlender@tb"
 

    def tag_redraw(self, context):
        try:
            # Depending on window, area may be None
            context.area.tag_redraw()
        except:
            pass


    def clear_error_message(self, context):
        preferences = vcu.get_addon_preferences()
        preferences.is_preset_library_installation_error = False
        preferences.preset_library_installation_error_message = ""
        self.tag_redraw(context)


    def report_error_message(self, context, error_message, error_type={'ERROR_INVALID_INPUT'}):
        self.report(error_type, error_message)
        print(error_message)
        preferences = vcu.get_addon_preferences()
        preferences.is_preset_library_installation_error = True
        preferences.preset_library_installation_error_message = error_message
        self.tag_redraw(context)


    def is_path_equal(self, p1, p2):
        return os.path.normpath(p1) == os.path.normpath(p2)


    def is_valid_metadata_file(self, filepath):
        try:
            with open(filepath, 'r') as json_file:
                metadata = json.loads(json_file.read())
                if "name" in metadata.keys() and metadata["name"] == "FLIP Fluids Addon Presets":
                    return True, metadata
            return False, None
        except:
            return False, None


    def execute(self, context):

        installation_utils.update_preset_library_installation_status()
        self.clear_error_message(context)

        install_directory = vcu.get_addon_preferences().preset_library_install_location
        
        found_installations = []

        # Check if current directory is a valid preset library folder
        expected_metadata_filepath = os.path.join(install_directory, ".metadata/version.json")
        

        if os.path.isfile(expected_metadata_filepath):
            is_valid, metadata = self.is_valid_metadata_file(expected_metadata_filepath)
            if is_valid:
                metadata["install_path"] = install_directory
                found_installations.append(metadata)

        # check if subdirectories are valid preset library folders
        if not found_installations:
            subdirs = [os.path.join(install_directory, d) for d in os.listdir(install_directory) if os.path.isdir(os.path.join(install_directory, d))]
            for path in subdirs:
                expected_metadata_filepath = os.path.join(path, ".metadata/version.json")
                if os.path.isfile(expected_metadata_filepath):
                    is_valid, metadata = self.is_valid_metadata_file(expected_metadata_filepath)
                    if is_valid:
                        metadata["install_path"] = path
                        found_installations.append(metadata)

        if not found_installations:
            self.report_error_message(context, _z("Error: No valid preset libraries found in selected folder or subfolders <{}>").format(install_directory))
            return {'CANCELLED'}

        
        asset_libraries = bpy.context.preferences.filepaths.asset_libraries
        
        for metadata in found_installations:
            is_library_path_in_asset_browser = False
            preset_library_directory = metadata["install_path"]
            for lib_entry in asset_libraries:
                if self.is_path_equal(lib_entry.path, preset_library_directory):
                    is_library_path_in_asset_browser = True
                    break

            if not is_library_path_in_asset_browser:
                bpy.ops.preferences.asset_library_add(directory=preset_library_directory)

            for lib_entry in asset_libraries:
                if self.is_path_equal(lib_entry.path, preset_library_directory):
                    version = metadata["version"]
                    lib_version_str = "v" + str(version[0]) + "." + str(version[1]) + "." + str(version[2])
                    preset_library_name = "FLIP Fluids Addon Presets " + lib_version_str
                    lib_entry.name = preset_library_name
                    if vcu.is_blender_35():
                        # Only available in Blender >= 3.5
                        lib_entry.import_method = 'APPEND'

        installation_utils.update_preset_library_installation_status()
        success_message = _z("The Preset Scenes Library has been installed successfully into the Blender Asset Browser.")
        print(success_message)
        self.report({'INFO'}, success_message)
        self.clear_error_message(context)
        self.tag_redraw(context)

        return {'FINISHED'}



def load_post():
    id_name = __name__.split(".")[0]
    preferences = vcu.get_addon_preferences()
    if not preferences.enable_helper:
        helper_ui.unregister()

    installation_utils.update_mixbox_installation_status()
    preferences.is_mixbox_installation_error = False
    preferences.mixbox_installation_error_message = ""

    
   
    installation_utils.update_preset_library_installation_status()
    preferences.is_preset_library_installation_error = False
    preferences.preset_library_installation_error_message = ""


def register():
    bpy.utils.register_class(FLIPFluidSetupAssetBrowser)
    bpy.utils.register_class(FLIPFluidGPUDevice)
    bpy.utils.register_class(FLIPFluidColorMixbox)
    bpy.utils.register_class(FLIPFluidColorRGB)
    bpy.utils.register_class(FLIPFluidAddonPreferences)

    id_name = __name__.split(".")[0]
    preferences = vcu.get_addon_preferences()
    update_helper_category_name(preferences, bpy.context)


def unregister():
    bpy.utils.unregister_class(FLIPFluidGPUDevice)
    bpy.utils.unregister_class(FLIPFluidColorMixbox)
    bpy.utils.unregister_class(FLIPFluidColorRGB)
    bpy.utils.unregister_class(FLIPFluidAddonPreferences)
    bpy.utils.unregister_class(FLIPFluidSetupAssetBrowser)
