import bpy
from . import BAM_MaterialManager_M
from . import BAM_BamAutomat_M
from . import BAM_MatOverlay_M
from .register import register_class, unregister_class

bl_info = {
    "name": "[BAM] AutoMat",
    "description": "Batch creation of materials from textures folder. Thanks KITBASH3D Team for early testing. Special thanks Nikita Kulchitskiy and Anderson Araujo",
    "version": (1, 1, 1),
    "blender": (4, 2, 0),
    "category": "Material",
    "location": "View3D > right-side panel > AutoMat tab",
    "author": "AlexeyHRDesign <alexeyhrdesign@gmail.com>",
    "tracker_url": "https://www.artstation.com/hrdesign",
    "warning": "",
}

panels = [
    BAM_MaterialManager_M.BAMMM_PT_MaterialManager,
    BAM_BamAutomat_M.BAMAM_PT_AutoMat,
]

def show_message_in_status_bar(message):
    bpy.context.window_manager.popup_menu(lambda self, context: self.layout.label(text=message), title="Warning", icon='INFO')

def show_message_in_console(message):
    print(f"[BAM] {message}")

def update_panel(self, context):
    space_to_region = {
        'EMPTY': {'WINDOW'},
        'VIEW_3D': {'WINDOW', 'HEADER', 'TOOLS', 'TOOL_PROPS', 'UI'},
        'IMAGE_EDITOR': {'WINDOW', 'HEADER', 'UI', 'TOOLS'},
        'NODE_EDITOR': {'WINDOW', 'HEADER', 'UI', 'TOOLS'},
        'SEQUENCE_EDITOR': {'WINDOW', 'HEADER', 'PREVIEW', 'TOOLS', 'UI'},
        'CLIP_EDITOR': {'WINDOW', 'HEADER', 'PREVIEW', 'TOOLS', 'UI'},
        'DOPESHEET_EDITOR': {'WINDOW', 'HEADER', 'CHANNELS', 'TEMPORARY', 'UI'},
        'GRAPH_EDITOR': {'WINDOW', 'HEADER', 'CHANNELS', 'TEMPORARY', 'UI'},
        'NLA_EDITOR': {'WINDOW', 'HEADER', 'CHANNELS', 'TEMPORARY', 'UI'},
        'TEXT_EDITOR': {'WINDOW', 'HEADER', 'UI'},
        'CONSOLE': {'WINDOW', 'HEADER'},
        'INFO': {'WINDOW', 'HEADER'},
        'TOPBAR': {'WINDOW'},
        'STATUSBAR': {'WINDOW'},
        'OUTLINER': {'WINDOW', 'HEADER', 'UI'},
        'PROPERTIES': {'WINDOW', 'HEADER'},
        'FILE_BROWSER': {'WINDOW', 'HEADER', 'CHANNELS', 'PREVIEW', 'TOOLS', 'UI'},
        'SPREADSHEET': {'WINDOW', 'HEADER', 'UI'},
        'PREFERENCES': {'WINDOW'}
    }

    for panel in panels:
        try:
            bpy.utils.unregister_class(panel)
        except RuntimeError:
            pass

        try:
            if panel.__name__ == "BAMMM_PT_MaterialManager":
                panel.bl_category = self.bl_category_bam
                panel.bl_region_type = self.bl_region_type_bam
                panel.bl_space_type = self.bl_space_type_bam

                if self.bl_region_type_bam not in space_to_region.get(self.bl_space_type_bam, set()):
                    message = f"[BAM] Region '{self.bl_region_type_bam}' is not supported in Space '{self.bl_space_type_bam}'."
                    show_message_in_console(message)
                    show_message_in_status_bar(message)

            else:
                panel.bl_category = self.bl_category_material
                panel.bl_region_type = self.bl_region_type_material
                panel.bl_space_type = self.bl_space_type_material

                if self.bl_region_type_material not in space_to_region.get(self.bl_space_type_material, set()):
                    message = f"[BAM] Region '{self.bl_region_type_material}' is not supported in Space '{self.bl_space_type_material}'."
                    show_message_in_console(message)
                    show_message_in_status_bar(message)

            bpy.utils.register_class(panel)

        except ValueError as e:
            message = f"[BAM] Error: Registering panel class: '{panel.__name__}' has category '{panel.bl_category}' - {e}"
            show_message_in_console(message)
            show_message_in_status_bar(message)

class ImageFormatItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(
        name="Format Key",
        description="Key of the image format (e.g., EXR, PNG, etc.)",
        update=lambda self, _: self.sync_display_name()
    )
    display_name: bpy.props.StringProperty(name="Display Name", description="Display name of the format")
    is_active: bpy.props.BoolProperty(name="Active", default=True)

    # Juat a Sync Display Name with Key
    def sync_display_name(self):
        self.display_name = self.name.upper()  # Приводим к верхнему регистру для единообразия


class BAM_UL_ImageFormats(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row(align=True)
        row.prop(item, "is_active", text="")  # Чекбокс для активации/деактивации
        row.prop(item, "name", text="")  # Поле для редактирования ключа формата


class BAM_OT_SavePreferences(bpy.types.Operator):
    bl_idname = "bam.save_preferences"
    bl_label = "Save Preferences"
    bl_description = "Save the image formats list and states"

    def execute(self, context):
        bpy.ops.wm.save_userpref()  # Сохраняем пользовательские настройки
        self.report({'INFO'}, "Preferences saved successfully")
        return {'FINISHED'}



class BAMAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    switch_to_cycles: bpy.props.BoolProperty(
        name="Switch to Cycles",
        description="Enable switching to Cycles renderer",
        default=False
    )


    # Параметры для Material Overlay
    overlay_offset_x: bpy.props.IntProperty(
        name="Overlay Offset X",
        description="Horizontal offset of the material overlay",
        default=25,
        min=0,
        max=2000
    )

    overlay_offset_y: bpy.props.IntProperty(
        name="Overlay Offset Y",
        description="Vertical offset of the material overlay",
        default=30,
        min=0,
        max=2000
    )

    overlay_text_size: bpy.props.IntProperty(
        name="Overlay Font Size",
        description="Size of the text in the overlay",
        default=20,
        min=10,
        max=200
    )

    overlay_text_color: bpy.props.FloatVectorProperty(
        name="Overlay Text Color",
        description="Text Font COlor",
        subtype='COLOR',
        size=4,
        default=(1.0, 1.0, 1.0, 1.0),
        min=0.0,
        max=1.0
    )
    
    overlay_text_color_random: bpy.props.BoolProperty(
        name="Random Font Color",
        description="If enabled, override user color with random color per material",
        default=True
    )

    overlay_bg_color: bpy.props.FloatVectorProperty(
        name="Overlay Background Color",
        description="Background color of the overlay",
        subtype='COLOR',
        size=4,
        default=(0.1, 0.1, 0.1, 0.8),
        min=0.0,
        max=1.0
    )

    overlay_border_color: bpy.props.FloatVectorProperty(
        name="Overlay Border Color",
        description="Border color of the overlay",
        subtype='COLOR',
        size=4,
        default=(0.3, 0.3, 0.3, 1.0),
        min=0.0,
        max=1.0
    )

    
    texture_sync_interval: bpy.props.FloatProperty(
        name="Textures Sync Interval",
        description="How frequently to check for texture updates (in seconds).",
        default=8,
        min=0.1,
        max=300.0
    )

    bl_category_bam: bpy.props.StringProperty(
        name="Category",
        description="Choose the category for MaterialManager",
        default="[BAM] AutoMat",
        update=update_panel
    )
    
    bl_category_material: bpy.props.StringProperty(
        name="Category",
        description="Choose the category for AutoMat",
        default="[BAM] AutoMat",
        update=update_panel
    )

    # Новые свойства для управления вкладками
    active_tab: bpy.props.EnumProperty(
        name="Active Tab",
        items=[
            ('GENERAL', "General", "General settings", 'PREFERENCES', 0),
            ('UI Settings', "UI Settings", "Settings for UI panels", 'TOOL_SETTINGS', 1)
        ],
        default='GENERAL'
    )

    # Список форматов изображений
    image_formats: bpy.props.CollectionProperty(type=ImageFormatItem)
    selected_format_index: bpy.props.IntProperty()
    
    

    bl_region_type_bam: bpy.props.EnumProperty(
        name="Region Type",
        description="Choose the region type for MaterialManager",
        items=[
            ('WINDOW', "Window", ""),
            ('HEADER', "Header", ""),
            ('CHANNELS', "Channels", ""),
            ('TEMPORARY', "Temporary", ""),
            ('UI', "UI", ""),
            ('TOOLS', "Tools", ""),
            ('TOOL_PROPS', "Tool Props", ""),
            ('PREVIEW', "Preview", "")
        ],
        default='UI',
        update=update_panel
    )

    bl_space_type_bam: bpy.props.EnumProperty(
        name="Space Type",
        description="Choose the space type for MaterialManager",
        items=[
            ('EMPTY', "Empty", ""),
            ('VIEW_3D', "3D View", ""),
            ('IMAGE_EDITOR', "Image Editor", ""),
            ('NODE_EDITOR', "Node Editor", ""),
            ('SEQUENCE_EDITOR', "Sequencer", ""),
            ('CLIP_EDITOR', "Movie Clip Editor", ""),
            ('DOPESHEET_EDITOR', "Dope Sheet", ""),
            ('GRAPH_EDITOR', "Graph Editor", ""),
            ('NLA_EDITOR', "NLA Editor", ""),
            ('TEXT_EDITOR', "Text Editor", ""),
            #('CONSOLE', "Python Console", ""),
            #('INFO', "Info", ""),
            #('TOPBAR', "Top Bar", ""),
            #('STATUSBAR', "Status Bar", ""),
            ('OUTLINER', "Outliner", ""),
            ('PROPERTIES', "Properties", ""),
            #('FILE_BROWSER', "File Browser", ""),
            ('SPREADSHEET', "Spreadsheet", ""),
            ('PREFERENCES', "Preferences", "")
        ],
        default='VIEW_3D',
        update=update_panel
    )

    bl_region_type_material: bpy.props.EnumProperty(
        name="Region Type",
        description="Choose the region type for AutoMat",
        items=[
            ('WINDOW', "Window", ""),
            ('HEADER', "Header", ""),
            ('CHANNELS', "Channels", ""),
            ('TEMPORARY', "Temporary", ""),
            ('UI', "UI", ""),
            ('TOOLS', "Tools", ""),
            ('TOOL_PROPS', "Tool Props", ""),
            ('PREVIEW', "Preview", "")
        ],
        default='UI',
        update=update_panel
    )

    bl_space_type_material: bpy.props.EnumProperty(
        name="Space Type",
        description="Choose the space type for AutoMat",
        items=[
            ('EMPTY', "Empty", ""),
            ('VIEW_3D', "3D View", ""),
            ('IMAGE_EDITOR', "Image Editor", ""),
            ('NODE_EDITOR', "Node Editor", ""),
            ('SEQUENCE_EDITOR', "Sequencer", ""),
            ('CLIP_EDITOR', "Movie Clip Editor", ""),
            ('DOPESHEET_EDITOR', "Dope Sheet", ""),
            ('GRAPH_EDITOR', "Graph Editor", ""),
            ('NLA_EDITOR', "NLA Editor", ""),
            ('TEXT_EDITOR', "Text Editor", ""),
            #('CONSOLE', "Python Console", ""),
            #('INFO', "Info", ""),
            #('TOPBAR', "Top Bar", ""),
            #('STATUSBAR', "Status Bar", ""),
            ('OUTLINER', "Outliner", ""),
            ('PROPERTIES', "Properties", ""),
            #('FILE_BROWSER', "File Browser", ""),
            ('SPREADSHEET', "Spreadsheet", ""),
            ('PREFERENCES', "Preferences", "")
        ],
        default='VIEW_3D',
        update=update_panel
    )

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.prop(self, "active_tab", expand=True, icon_only=False)
        
        if self.active_tab == 'GENERAL':
            
            # Создаем разметку с двумя колонками
            row = layout.row()
            split = row.split(factor=0.5)  # 50/50
            
            col_left = split.column()
            general_box = col_left.box()
            general_box.label(text="Materials Thumbnails Generation", icon='MATERIAL')
            general_box.prop(self, "switch_to_cycles")
            general_box.label(text="Auto Switch to Cycles for faster")
            general_box.label(text="Material Miniature generation")

            col_left.separator()

            general_box2 = col_left.box()
            general_box2.label(text="Textures Auto Refresh (Sync)", icon='TEXTURE')
            general_box2.prop(self, "texture_sync_interval")
            general_box2.label(text="How frequently to check folder with")
            general_box2.label(text="textures for auto refresh in seconds")
            

            col_right = split.column() # righ side column
            formats_box = col_right.box()
            formats_box.label(text="Image Formats Manager", icon='IMAGE_DATA')

            # Formats list
            row = formats_box.row()
            row.template_list("BAM_UL_ImageFormats", "", self, "image_formats", self, "selected_format_index")

            col = row.column(align=True)
            col.operator("bam.add_image_format", text="", icon='ADD')
            col.operator("bam.remove_image_format", text="", icon='REMOVE')

        elif self.active_tab == 'UI Settings':
            
            # Создаем разметку с двумя колонками
            row = layout.row()  # Строка, содержащая два столбца
            split = row.split(factor=0.5)  # Делим строку на две части 50/50

            
            col_left = split.column()
            panels_box = col_left.box()
            panels_box.label(text="Panels UI Settings", icon='TOOL_SETTINGS')
            panels_box.label(text="-- MaterialManager Panel --")
            panels_box.prop(self, "bl_category_bam")
            panels_box.prop(self, "bl_space_type_bam")
            panels_box.prop(self, "bl_region_type_bam")
            panels_box.separator()
            panels_box.label(text="-- AutoMat Panel --")
            panels_box.prop(self, "bl_category_material")
            panels_box.prop(self, "bl_space_type_material")
            panels_box.prop(self, "bl_region_type_material")
            panels_box.label(text="[NOTE] *Addon panels do not support")
            panels_box.label(text="display in all Region Types and Space Types*")
            panels_box.separator()
            
            col_right = split.column()
            matoverlay_box = col_right.box()
            matoverlay_box.label(text="Material Overlay Settings", icon='META_BALL')

            matoverlay_box.prop(self, "overlay_offset_x")
            matoverlay_box.prop(self, "overlay_offset_y")
            matoverlay_box.prop(self, "overlay_text_size")
            
            row = matoverlay_box.row(align=True)
            row.prop(self, "overlay_text_color")
            row.prop(self, "overlay_text_color_random")
            
            
            matoverlay_box.prop(self, "overlay_bg_color")
            matoverlay_box.prop(self, "overlay_border_color")
            
    
        save_row = layout.row()
        save_row.operator("bam.save_preferences", text="Save Changes", icon='FILE_TICK')

def initialize_image_formats(prefs):
    image_formats = {
        "PNG": "PNG",
        "JPEG": "JPEG",
        "JPG": "JPG",
        "TIFF": "TIFF",
        "EXR": "EXR",
        "HDR": "HDR",
        "BMP": "BMP",
        "TGA": "TGA",
        "RAW": "RAW",
        "PSD": "PSD",
        "WEBP": "WEBP",
        "DDS": "DDS",
        "GIF": "GIF",
    }
    
    # Formats Disabled by default
    inactive_formats = {"PSD", "WEBP", "DDS", "GIF"}

    # Если список уже заполнен, не перезаполняем его
    if prefs.image_formats:
        return

    for key, display_name in image_formats.items():
        item = prefs.image_formats.add()
        item.name = key
        item.display_name = display_name
        item.is_active = key not in inactive_formats  # disabled formats



# Операторы для работы с форматами изображений
class BAM_OT_AddImageFormat(bpy.types.Operator):
    bl_idname = "bam.add_image_format"
    bl_label = "Add Image Format"

    def execute(self, context):
        prefs = context.preferences.addons[__package__].preferences
        new_format = prefs.image_formats.add()
        new_format.name = "NEW_FORMAT"  # Значение по умолчанию
        new_format.is_active = True
        return {'FINISHED'}


class BAM_OT_RemoveImageFormat(bpy.types.Operator):
    bl_idname = "bam.remove_image_format"
    bl_label = "Remove Image Format"

    def execute(self, context):
        prefs = context.preferences.addons[__package__].preferences
        index = prefs.selected_format_index
        if index >= 0 and index < len(prefs.image_formats):
            prefs.image_formats.remove(index)
            prefs.selected_format_index = max(0, index - 1)
        return {'FINISHED'}

        

def register():
    print("[BAM] Addon Registered")
    bpy.utils.register_class(BAM_OT_SavePreferences)
    bpy.utils.register_class(ImageFormatItem)  # Регистрируем PropertyGroup перед его использованием
    bpy.utils.register_class(BAM_UL_ImageFormats)
    bpy.utils.register_class(BAMAddonPreferences)
    bpy.utils.register_class(BAM_OT_AddImageFormat)  # Добавляем в реестр
    bpy.utils.register_class(BAM_OT_RemoveImageFormat)  # Добавляем в реестр

    for panel in panels:
        register_class(panel)
    
    BAM_MatOverlay_M.register()
    BAM_MaterialManager_M.register()
    BAM_BamAutomat_M.register()
    

    # Update panels UI during register
    prefs = bpy.context.preferences.addons[__package__].preferences
    update_panel(prefs, bpy.context)
    
    if prefs and not prefs.image_formats:
        initialize_image_formats(prefs)  # Заполняем список форматами


def unregister():
    print("[BAM] Addon Unregistered")
    bpy.utils.unregister_class(BAM_OT_SavePreferences)
    bpy.utils.unregister_class(BAM_UL_ImageFormats)
    bpy.utils.unregister_class(ImageFormatItem)
    bpy.utils.unregister_class(BAMAddonPreferences)
    bpy.utils.unregister_class(BAM_OT_AddImageFormat)  # Убираем из реестра
    bpy.utils.unregister_class(BAM_OT_RemoveImageFormat)  # Убираем из реестра
    
    for panel in panels:
        unregister_class(panel)
    BAM_MatOverlay_M.unregister()
    BAM_MaterialManager_M.unregister()
    BAM_BamAutomat_M.unregister()
    
    
if __name__ == "__main__":
    register()
