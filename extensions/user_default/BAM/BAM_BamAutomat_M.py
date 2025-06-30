print("[BAM] AutoMat Module Loaded")

'''
Copyright (C) 2025

Created by AlexeyHRDesign

'''

# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####


import bpy
from .register import register_class, unregister_class
import os
import time
import json
import sys

    
# Get the path to the current file (addon script)
addon_dir = os.path.dirname(__file__)
# The path to the preset file
preset_file_path = os.path.join(addon_dir, "material_presets.json")

# Check if the file exists
if not os.path.exists(preset_file_path) or os.stat(preset_file_path).st_size == 0:
    # Если файл не существует или пуст, инициализируем его с пустым объектом
    with open(preset_file_path, 'w') as outfile:
        json.dump({}, outfile)

# Safely download the data from the fileа
with open(preset_file_path, 'r') as infile:
    presets = json.load(infile)


presets_dir = os.path.join(addon_dir, "presets")
if not os.path.exists(presets_dir):
    os.makedirs(presets_dir)


def convert_old_presets():
    old_preset_path = os.path.join(addon_dir, "material_presets.json")
    if os.path.exists(old_preset_path):
        with open(old_preset_path, 'r') as infile:
            old_presets = json.load(infile)
        
        for preset_name, preset_data in old_presets.items():
            preset_file = os.path.join(presets_dir, f"{preset_name}_bpres.json")
            if not os.path.exists(preset_file):  # Создаем файл, если его нет
                with open(preset_file, 'w') as outfile:
                    json.dump(preset_data, outfile, indent=4)
        
        # Старый файл можно удалить после конвертации
        os.remove(old_preset_path)

convert_old_presets()



blender_version = bpy.app.version

# Option to check if the Base Color texture is present
check_basecolor_texture=True

textures_info = {
    "basecolor": {
        "color_space": "sRGB",
        "display_name": "Base Color"
    },
    "normal": {
        "color_space": "Non-Color",
        "display_name": "Normal"
    },
    "roughness": {
        "color_space": "Non-Color",
        "display_name": "Roughness"
    },
    "displacement": {
        "color_space": "Non-Color",
        "display_name": "Displacement"
    },
    "metallic": {
        "color_space": "Non-Color",
        "display_name": "Metallic"
    },
    "emission": {
        "color_space": "sRGB",
        "display_name": "Emission Color" if blender_version >= (3, 5, 0) else "Emission"
    },
    "ao": {
        "color_space": "Non-Color",
        "display_name": "AO"
    },
    "transmission": {
        "color_space": "Non-Color",
        "display_name": "Transmission Weight" if blender_version >= (4, 0, 0) else "Transmission"
    },
    "opacity": {
        "color_space": "Non-Color",
        "display_name": "Alpha"
    },
    "specular": {
        "color_space": "Non-Color",
        "display_name": "Specular IOR Level" if blender_version >= (4, 0, 0) else "Specular"
    },
    "specular_tint": {
        "color_space": "Non-Color",
        "display_name": "Specular Tint" if blender_version >= (3, 4, 0) else "SpecularTint"
    },
    "ior": {
        "color_space": "Non-Color",
        "display_name": "IOR"
    },
    "sheen": {
        "color_space": "Non-Color",
        "display_name": "Sheen Weight" if blender_version >= (4, 0, 0) else "Sheen"
    },
    "sheen_tint": {
        "color_space": "Non-Color",
        "display_name": "Sheen Tint" if blender_version >= (3, 4, 0) else "SheenTint"
    },
    "anisotropic": {
        "color_space": "Non-Color",
        "display_name": "Anisotropy" if blender_version >= (3, 4, 0) else "Anisotropic"
    },
    "clearcoat": {
        "color_space": "Non-Color",
        "display_name": "Coat Weight" if blender_version >= (4, 0, 0) else "Clearcoat"
    },
    "clearcoat_roughness": {
        "color_space": "Non-Color",
        "display_name": "Coat Roughness" if blender_version >= (4, 0, 0) else "Clearcoat Roughness"
    },
    "subsurface": {
        "color_space": "Non-Color",
        "display_name": "Subsurface Weight" if blender_version >= (4, 0, 0) else "Subsurface"
    },
}




# Define available Colorspaces
if blender_version[0] >= 4:
    colorspace_items = [
        ("ACES2065-1", "ACES2065-1", "ACES2065-1"),
        ("ACEScg", "ACEScg", "ACEScg"),
        ("AgX Base Display P3", "AgX Base Display P3", "AgX Base Display P3"),
        ("AgX Base Rec.1886", "AgX Base Rec.1886", "AgX Base Rec.1886"),
        ("AgX Base Rec.2020", "AgX Base Rec.2020", "AgX Base Rec.2020"),
        ("AgX Base sRGB", "AgX Base sRGB", "AgX Base sRGB"),
        ("AgX Log", "AgX Log", "AgX Log"),
        ("Display P3", "Display P3", "Display P3"),
        ("Filmic Log", "Filmic Log", "Filmic Log"),
        ("Filmic sRGB", "Filmic sRGB", "Filmic sRGB"),
        ("Khronos PBR Neutral sRGB", "Khronos PBR Neutral sRGB", "Khronos PBR Neutral sRGB"),
        ("Linear CIE-XYZ D65", "Linear CIE-XYZ D65", "Linear CIE-XYZ D65"),
        ("Linear CIE-XYZ E", "Linear CIE-XYZ E", "Linear CIE-XYZ E"),
        ("Linear DCI-P3 D65", "Linear DCI-P3 D65", "Linear DCI-P3 D65"),
        ("Linear FilmLight E-Gamut", "Linear FilmLight E-Gamut", "Linear FilmLight E-Gamut"),
        ("Linear Rec.2020", "Linear Rec.2020", "Linear Rec.2020"),
        ("Linear Rec.709", "Linear Rec.709", "Linear Rec.709"),
        ("Non-Color", "Non-Color", "Non-Color"),
        ("Rec.1886", "Rec.1886", "Rec.1886"),
        ("Rec.2020", "Rec.2020", "Rec.2020"),
        ("sRGB", "sRGB", "sRGB"),
    ]

elif (3, 6) <= blender_version < (4, 0):
    colorspace_items = [
        ("ACES2065-1", "ACES2065-1", "ACES2065-1"),
        ("ACEScg", "ACEScg", "ACEScg"),
        ("Display P3", "Display P3", "Display P3"),
        ("Filmic Log", "Filmic Log", "Filmic Log"),
        ("Filmic sRGB", "Filmic sRGB", "Filmic sRGB"),
        ("Khronos PBR Neutral sRGB", "Khronos PBR Neutral sRGB", "Khronos PBR Neutral sRGB"),
        ("Linear FilmLight E-Gamut", "Linear FilmLight E-Gamut", "Linear FilmLight E-Gamut"),
        ("Linear Rec.2020", "Linear Rec.2020", "Linear Rec.2020"),
        ("Linear Rec.709", "Linear Rec.709", "Linear Rec.709"),
        ("Non-Color", "Non-Color", "Non-Color"),
        ("sRGB", "sRGB", "sRGB"),
    ]

elif (3, 4) <= blender_version < (3, 6):
    colorspace_items = [
        ("ACEScg", "ACEScg", "ACEScg"),
        ("Filmic Log", "Filmic Log", "Filmic Log"),
        ("Filmic sRGB", "Filmic sRGB", "Filmic sRGB"),
        ("Linear Rec.709", "Linear Rec.709", "Linear Rec.709"),
        ("Linear Rec.2020", "Linear Rec.2020", "Linear Rec.2020"),
        ("Khronos PBR Neutral sRGB", "Khronos PBR Neutral sRGB", "Khronos PBR Neutral sRGB"),
        ("Non-Color", "Non-Color", "Non-Color"),
        ("sRGB", "sRGB", "sRGB"),
    ]

elif (3, 3) <= blender_version < (3, 4):
    colorspace_items = [
        ("ACEScg", "ACEScg", "ACEScg"),
        ("Filmic Log", "Filmic Log", "Filmic Log"),
        ("Filmic sRGB", "Filmic sRGB", "Filmic sRGB"),
        ("Linear Rec.709", "Linear Rec.709", "Linear Rec.709"),
        ("Linear Rec.2020", "Linear Rec.2020", "Linear Rec.2020"),
        ("Non-Color", "Non-Color", "Non-Color"),
        ("sRGB", "sRGB", "sRGB"),
    ]

else:
    colorspace_items = [
        ("Filmic Log", "Filmic Log", "Filmic Log"),
        ("Filmic sRGB", "Filmic sRGB", "Filmic sRGB"),
        ("Linear", "Linear", "Linear"),
        ("Linear ACEScg", "Linear ACEScg", "Linear ACEScg"),
        ("Non-Color", "Non-Color", "Non-Color"),
        ("Raw", "Raw", "Raw"),
        ("sRGB", "sRGB", "sRGB"),
        ("Rec.709", "Rec.709", "Rec.709"),
    ]


def get_active_image_formats():
    # Получаем объект настроек аддона
    preferences = bpy.context.preferences.addons[__package__].preferences

    # Проверяем, что preferences существует
    if not preferences:
        print("[BAM] Preferences not found!")
        return {}

    # Формируем словарь только активных форматов
    active_formats = {item.name: item.display_name for item in preferences.image_formats if item.is_active}
    return active_formats
    
    


active_image_formats = get_active_image_formats()

# Используем активные форматы в логике
for format_name in active_image_formats.keys():
    print(f"[BAM] Using format: {format_name}")


# Definition of blend_modes
blend_modes = [
    ('OPAQUE', "Opaque", "Opaque Blend Mode"),
    ('CLIP', "Alpha Clip", "Alpha Clip Blend Mode"),
    ('HASHED', "Alpha Hashed", "Alpha Hashed Blend Mode"),
    ('BLEND', "Alpha Blend", "Alpha Blend Blend Mode")
]

bpy.types.Scene.my_blend_mode = bpy.props.EnumProperty(
    name="Blend Mode",
    description="Choose a Blend Mode for material with Opacity maps",
    items=blend_modes,
    default='HASHED'
)

# Vocabulary with Displacement
disp_modes=[
    ('BUMP',"Bump Only","Bump Only"),
    ('DISPLACEMENT',"Displacement Only","Displacement Only"),
    ('BOTH',"Displacement and Bump","Displacement and Bump")
]
bpy.types.Scene.my_disp_mode=bpy.props.EnumProperty(
    name="Displacement Mode",
    description="Choose a Surface Displacement Mode for materials with Displacement maps",
    items=disp_modes,
    default='BOTH'
)

# _channel for each texture map
texture_keys=["basecolor","normal","roughness","metallic","opacity",
              "subsurface","specular","specular_tint",
              "anisotropic","sheen","sheen_tint","clearcoat","clearcoat_roughness",
              "ior","transmission","displacement","emission","ao"]

for key in texture_keys:
    setattr(bpy.types.Scene,key+"_channel",bpy.props.EnumProperty(
        name=key.capitalize()+" ",
        description=f"Select the output color channel for {key} map",
        items=[
            ('RGB','Channel','RGB Channel'),
            ('R','->RED','Red Channel'),
            ('G','->GREEN','Green Channel'),
            ('B','->BLUE','Blue Channel'),
        ],
        default='RGB',
    ))



def resolve_path(path):
    # Converting a Blender-specific relative path to an absolute path
    if path.startswith("//"):
        return bpy.path.abspath(path)
    return path



#def update_material_list(self,context):
#    bpy.ops.material.check_all()



def update_material_list(self, context):
    if not context or not context.scene:
        #print("[BAM] Context or scene is not available.")
        return
    path = resolve_path(context.scene.texture_folder_path)
    if not os.path.exists(path):
        print(f"[BAM] [update_material_list] Path not found: {path}")
        return []

    materials = detect_materials_in_folder(context.scene)
    material_list = context.scene.material_list
    material_list.clear()
    
    for material in materials:
        item = material_list.add()
        item.name = material
        item.bamam_checked = material not in bpy.data.materials


def with_temporary_cycles_renderer(func):
    def wrapper(*args, **kwargs):
        context = bpy.context
        if not context or not context.scene:
            print("[BAM] Context or scene is not available.")
            return None

        addon_prefs = None
        try:
            addon_prefs = context.preferences.addons[__package__].preferences
        except KeyError:
            print("[BAM] Addon preferences not found. Using default settings.")

        original_renderer = None
        if addon_prefs and getattr(addon_prefs, 'switch_to_cycles', False):
            original_renderer = context.window.scene.render.engine
            print(f"[BAM] Original renderer: {original_renderer}")
            context.window.scene.render.engine = 'CYCLES'
            print("[BAM] Switched to Cycles")

        try:
            result = func(*args, **kwargs)
        finally:
            if addon_prefs and getattr(addon_prefs, 'switch_to_cycles', False) and original_renderer:
                print(f"[BAM] Switching back to {original_renderer} is Disabled")
                #context.window.scene.render.engine = original_renderer

        return result

    return wrapper


def detect_materials_in_folder(scene):
    path = resolve_path(scene.texture_folder_path)
    if not os.path.exists(path):
        print(f"[BAM] [detect_materials_in_folder] Path not found: {path}")
        return []
    
    materials = set()
    include_subfolders = scene.include_subfolders

    def check_suffixes(file, suffixes, format):
        file_lower = file.lower()
        for suffix in suffixes:
            if file_lower.endswith(f"{suffix.strip().lower()}.{format.lower()}"):
                return True
        return False

    def get_material_name(file, suffixes):
        for suffix in suffixes:
            suffix_with_format = suffix.strip().lower()
            if file.lower().endswith(suffix_with_format):
                return file[: -len(suffix_with_format)]
        return file

    if include_subfolders:
        for root, dirs, files in os.walk(path):
            for file in files:
                for format in get_active_image_formats().keys():
                    suffixes = getattr(scene, 'basecolor_suffix').split(",")
                    if check_suffixes(file, suffixes, format):
                        material_name = get_material_name(file, [f"{suffix.strip().lower()}.{format.lower()}" for suffix in suffixes])
                        materials.add(material_name)
    else:
        for item in os.listdir(path):
            for format in get_active_image_formats().keys():
                suffixes = getattr(scene, 'basecolor_suffix').split(",")
                if check_suffixes(item, suffixes, format):
                    material_name = get_material_name(item, [f"{suffix.strip().lower()}.{format.lower()}" for suffix in suffixes])
                    materials.add(material_name)

    return list(materials)



class MaterialNodeManager:
    def __init__(self, material):
        self.material = material
        self.node_tree = material.node_tree

        self.texture_coordinate_node = self.create_texture_coordinate_node()
        self.mapping_node = self.create_mapping_node()

    def create_texture_coordinate_node(self):
        # Check if Texture Coordinate node exist
        for node in self.node_tree.nodes:
            if node.type == 'TEX_COORD':
                return node  # use existing
        texture_coordinate_node = self.node_tree.nodes.new(type='ShaderNodeTexCoord')
        texture_coordinate_node.location = (-1400, 0)
        return texture_coordinate_node

    def create_mapping_node(self):
        # check if Mapping exist
        for node in self.node_tree.nodes:
            if node.type == 'MAPPING':
                return node 
        mapping_node = self.node_tree.nodes.new(type='ShaderNodeMapping')
        mapping_node.location = (-1200, 0)
        return mapping_node

    def connect_texture_coordinates(self,texture_node):
        # connect Texture Coordinate with textures
        self.node_tree.links.new(
            self.mapping_node.outputs['Vector'], 
            texture_node.inputs['Vector']
        )

    def connect_mapping(self,texture_node):
        # connect Mapping and texture
        self.node_tree.links.new(
            self.texture_coordinate_node.outputs['UV'],
            self.mapping_node.inputs['Vector']
        )


def ensure_principled_bsdf_connection(node_tree, shader, output):
    # Get the Surface input from the Material Output node
    output_surface_input = output.inputs['Surface']
    # Check if the Principled BSDF node is connected to this input
    if not output_surface_input.is_linked or (output_surface_input.links[0].from_node != shader):
        # Remove all existing connections to this input
        while output_surface_input.is_linked:
            node_tree.links.remove(output_surface_input.links[0])
        # Create a new connection from Principled BSDF to Material Output
        node_tree.links.new(output_surface_input, shader.outputs['BSDF'])



class TextureProcessor:
    def __init__(self, scene, material, nodes, node_tree):
        self.texture_node_cache = {}  # Кэш для текстур
        self.scene = scene
        self.material = material
        self.nodes = nodes
        self.node_tree = node_tree
        self.vertical_location = 300

    def create_texture_node(self, full_item_path, info_key):
        """Создаем или возвращаем существующий нод текстуры."""
        if full_item_path in self.texture_node_cache:
            return self.texture_node_cache[full_item_path]
            
        """Создаем ноду текстуры с учетом цветового пространства."""
        image_name = os.path.basename(full_item_path)
        texture_node = self.nodes.new(type="ShaderNodeTexImage")

        if image_name in bpy.data.images:
            image = bpy.data.images[image_name]
            if image.filepath_from_user() != full_item_path:
                image.filepath = full_item_path
        else:
            image = bpy.data.images.load(filepath=full_item_path)

        # Установка цветового пространства
        color_space = getattr(self.scene, f"{info_key}_colorspace", "sRGB")
        image.colorspace_settings.name = color_space

        texture_node.image = image
        texture_node.location = (-800, self.vertical_location)
        self.vertical_location -= 300
        # Добавление в кэш
        self.texture_node_cache[full_item_path] = texture_node
        return texture_node


    def create_separate_rgb_node(self):
        """Создаем ноду для разделения RGB каналов"""
        separate_node = self.nodes.new(type="ShaderNodeSeparateRGB")
        separate_node.location = (-210, self.vertical_location)
        self.vertical_location -= 20
        return separate_node

    def create_normal_map_node(self, texture_node, channel="RGB"):
        """Создаем узел Normal Map и располагаем его параллельно текстурному узлу."""
        normal_map_node = self.nodes.new(type="ShaderNodeNormalMap")
        normal_map_node.location = (texture_node.location.x + 600, texture_node.location.y)

        separate_node = None
        rgb_curves = None

        if channel in ["R", "G", "B"]:
            # Создаем Separate RGB узел для разбиения каналов
            separate_node = self.create_separate_rgb_node()
            separate_node.location.x = texture_node.location.x + 300
            separate_node.location.y = texture_node.location.y

            # Подключаем Separate RGB к текстуре
            self.node_tree.links.new(separate_node.inputs["Image"], texture_node.outputs["Color"])

        if self.scene.invert_normal_map_green_channel:
            # Создаем RGB Curves для инверсии зеленого канала
            rgb_curves = self.nodes.new(type="ShaderNodeRGBCurve")
            rgb_curves.location = (separate_node.location.x + 300 if separate_node else texture_node.location.x + 300,
                                   texture_node.location.y)

            # Настройка кривой для инверсии зеленого канала
            green_curve = rgb_curves.mapping.curves[1]
            green_curve.points[0].location = (0.0, 1.0)
            green_curve.points[1].location = (1.0, 0.0)

            # Подключение к RGB Curves
            if separate_node:
                self.node_tree.links.new(rgb_curves.inputs["Color"], separate_node.outputs[channel])
            else:
                self.node_tree.links.new(rgb_curves.inputs["Color"], texture_node.outputs["Color"])

            self.node_tree.links.new(normal_map_node.inputs["Color"], rgb_curves.outputs["Color"])
        else:
            # Подключаем напрямую к Normal Map
            if separate_node:
                self.node_tree.links.new(normal_map_node.inputs["Color"], separate_node.outputs[channel])
            else:
                self.node_tree.links.new(normal_map_node.inputs["Color"], texture_node.outputs["Color"])

        return rgb_curves, normal_map_node




    def get_output_node(self):
        for node in self.nodes:
            if node.type == "OUTPUT_MATERIAL":
                return node
        output_node = self.nodes.new(type="ShaderNodeOutputMaterial")
        output_node.location = (400, 0)
        return output_node



    def link_texture_to_shader(self, texture_node, separate_node, shader, channel, info_key):
        """Подключаем текстуру к нужному входу шейдера."""
        display_name = textures_info[info_key]["display_name"]


        if info_key == "normal":
            # Создаем узел Normal Map с учетом выбранного канала
            rgb_curves, normal_map_node = self.create_normal_map_node(texture_node, channel=channel)

            # Подключаем результат узла Normal Map к входу Principled BSDF
            self.node_tree.links.new(shader.inputs["Normal"], normal_map_node.outputs["Normal"])
            return




        if info_key == "roughness" and self.scene.invert_roughness:
            # Создаем узел RGB Curves для инверсии Roughness
            rgb_curves = self.nodes.new(type="ShaderNodeRGBCurve")
            rgb_curves.location = (texture_node.location.x + 300, texture_node.location.y)
            
            # Настройка кривой для инверсии всех каналов
            for curve in rgb_curves.mapping.curves:
                curve = rgb_curves.mapping.curves[-1]
                curve.points[0].location = (0.0, 1.0)
                curve.points[1].location = (1.0, 0.0)
            
            # Подключаем Roughness через RGB Curves
            self.node_tree.links.new(rgb_curves.inputs["Color"], texture_node.outputs["Color"])

            # Если выбран определенный канал, добавляем Separate RGB после RGB Curves
            if channel in ["R", "G", "B"]:
                separate_node = self.create_separate_rgb_node()
                separate_node.location = (rgb_curves.location.x + 300, rgb_curves.location.y)
                self.node_tree.links.new(separate_node.inputs["Image"], rgb_curves.outputs["Color"])
                self.node_tree.links.new(shader.inputs["Roughness"], separate_node.outputs[channel])
                print(f"[BAM] Inverted Roughness connected through channel {channel} with Separate RGB.")
            else:
                self.node_tree.links.new(shader.inputs["Roughness"], rgb_curves.outputs["Color"])
                print("[BAM] Inverted Roughness applied directly to shader.")
            
            return


        if info_key == "displacement":
            displacement_node = self.nodes.new(type="ShaderNodeDisplacement")
            displacement_node.inputs["Scale"].default_value = 0.1
            displacement_node.location = (texture_node.location.x + 300, texture_node.location.y)
            self.node_tree.links.new(displacement_node.inputs["Height"], texture_node.outputs["Color"])
            output_node = self.get_output_node()
            if output_node:
                self.node_tree.links.new(output_node.inputs["Displacement"], displacement_node.outputs["Displacement"])
            return

        if channel in ["R", "G", "B"]:
            if not separate_node:
                separate_node = self.create_separate_rgb_node()
            self.node_tree.links.new(separate_node.inputs["Image"], texture_node.outputs["Color"])
            self.node_tree.links.new(shader.inputs[display_name], separate_node.outputs[channel])
        else:
            if info_key != "ao":  # Исключаем попытку подключения AO напрямую
                self.node_tree.links.new(shader.inputs[display_name], texture_node.outputs["Color"])



        # Убедитесь, что BSDF подключен к Material Output
        output_node = self.get_output_node()
        ensure_principled_bsdf_connection(self.node_tree, shader, output_node)


    def get_or_create_basecolor_node(self, shader):
        """Возвращаем узел BaseColor или создаем его."""
        for node in self.nodes:
            if node.type == "TEX_IMAGE" and node.image and "basecolor" in node.image.name.lower():
                return node
        return None


    def apply_custom_values_to_all(self):
        """Применяет кастомные значения ко всем обработанным материалам с учетом фильтра."""
        scene = self.scene
        
        print("\n")
        for material in bpy.data.materials:
            # Пропускаем материалы, которые не используют узлы или не были обработаны
            if not material.use_nodes or not material.get("bamam_processed", False):
                continue

            # Проверяем, был ли материал отмечен в списке фильтра
            material_item = next((item for item in scene.material_list if item.name == material.name), None)
            if not material_item or not material_item.bamam_checked:
                print(f"[BAM] Skip material {material.name}, disabled in filter.")
                continue

            node_tree = material.node_tree
            shader = None

            # Ищем узел Principled BSDF
            for node in node_tree.nodes:
                if node.type == "BSDF_PRINCIPLED":
                    shader = node
                    break

            if not shader:
                continue  # Пропускаем, если нет Principled BSDF

            # Применяем кастомные значения ко всем входам
            for info_key, info_value in textures_info.items():
                if getattr(scene, f"{info_key}_use_value", False):
                    custom_value = getattr(scene, f"{info_key}_custom_value")
                    display_name = info_value["display_name"]

                    if display_name in shader.inputs:
                        input_socket = shader.inputs[display_name]

                        # Разрываем все существующие связи
                        while input_socket.is_linked:
                            node_tree.links.remove(input_socket.links[0])

                        # Устанавливаем кастомное значение
                        if len(custom_value) == 4:
                            input_socket.default_value = custom_value  # RGBA
                        else:
                            input_socket.default_value = custom_value[0]  # Скалярное значение
                        print(f"[BAM] Applied custom value: {custom_value} for {info_key} in material: {material.name}")



    def process_texture(self, full_item_path, info_key, channel):
        """Обработка текстуры по ключу info_key с учетом пользовательских значений."""
        shader = self.get_principled_bsdf()


        # Если текстуры нет, выводим лог и завершаем
        if not full_item_path:
            print(f"[BAM] The texture for {info_key} absent.")
            return

        # Создаем узел текстуры
        texture_node = self.create_texture_node(full_item_path, info_key)

        # Создаем или находим MixRGB узел
        mix_node = next((node for node in self.nodes if node.type == 'MIX_RGB' and node.blend_type == 'MULTIPLY'), None)
        if not mix_node:
            mix_node = self.nodes.new(type="ShaderNodeMixRGB")
            mix_node.blend_type = 'MULTIPLY'
            mix_node.inputs["Fac"].default_value = 1.0
            mix_node.location.x = texture_node.location.x + 500  # Смещение вправо относительно текстуры BaseColor
            mix_node.location.y = texture_node.location.y  # Оставляем тот же уровень по вертикали
            mix_node.inputs["Color2"].default_value = (1.0, 1.0, 1.0, 1.0)

        # Подключение BaseColor
        if info_key == "basecolor":
            if channel in ["R", "G", "B"]:
                separate_node = self.create_separate_rgb_node()
                separate_node.location.x = texture_node.location.x + 300  # Смещаем вправо
                separate_node.location.y = texture_node.location.y
                self.node_tree.links.new(separate_node.inputs["Image"], texture_node.outputs["Color"])
                self.node_tree.links.new(mix_node.inputs["Color1"], separate_node.outputs[channel])
                print(f"[BAM] BaseColor connected via a channel {channel} with Separate RGB.")
            else:
                self.node_tree.links.new(mix_node.inputs["Color1"], texture_node.outputs["Color"])
                print("[BAM] BaseColor connected directly to Mix node.")

            self.node_tree.links.new(shader.inputs["Base Color"], mix_node.outputs["Color"])
            self.node_tree.nodes.active = texture_node
            return

        # Подключение AO
        if info_key == "ao":
            self.texture_node_cache["ao"] = texture_node
            print(f"[BAM] Ao texture added with channel: {channel}")

            ao_texture_node = self.texture_node_cache.get("ao")
            if ao_texture_node:
                if channel in ["R", "G", "B"]:
                    separate_node = self.create_separate_rgb_node()
                    separate_node.location.x = texture_node.location.x + 300  # Смещаем вправо для выравнивания
                    separate_node.location.y = texture_node.location.y  # Оставляем на том же уровне по Y
                    self.node_tree.links.new(separate_node.inputs["Image"], ao_texture_node.outputs["Color"])
                    self.node_tree.links.new(mix_node.inputs["Color2"], separate_node.outputs[channel])
                    print(f"[BAM] AO added through channel {channel} with Separate RGB.")
                else:
                    self.node_tree.links.new(mix_node.inputs["Color2"], ao_texture_node.outputs["Color"])
                    print("[BAM] AO connected directly to Mix node.")
            else:
                mix_node.inputs["Color2"].default_value = (1.0, 1.0, 1.0, 1.0)
                print("[BAM] AO absent. The white color is used.")
            return

        # Подключение других карт
        self.link_texture_to_shader(texture_node, None, shader, channel, info_key)




    def get_principled_bsdf(self):
        """Возвращаем ноду Principled BSDF"""
        for node in self.nodes:
            if node.type == "BSDF_PRINCIPLED":
                return node
        shader = self.nodes.new(type='ShaderNodeBsdfPrincipled')
        shader.location = (0, 0)
        
        # specular tint black by default
        shader.inputs["Specular Tint"].default_value = (0.0, 0.0, 0.0, 1.0) if is_blender_4 else 0.5
        
        return shader


def optimize_material_creation(scene, material_name, textures):
    
    print("\n")
    print(f"[BAM] ------------ >>>> MATERIAL Processing: {material_name} <<<< ------------ ")


    
    material = bpy.data.materials.get(material_name) or bpy.data.materials.new(name=material_name)
    material.use_nodes = True
    material["bamam_processed"] = True  # Метка, что материал был обработан
    node_tree = material.node_tree
    nodes = node_tree.nodes

    texture_processor = TextureProcessor(scene, material, nodes, node_tree)

    # Находим или создаем узел Principled BSDF
    shader = None
    for node in nodes:
        if node.type == "BSDF_PRINCIPLED":
            shader = node
            break
    if not shader:
        shader = nodes.new(type='ShaderNodeBsdfPrincipled')
        shader.location = (0, 0)

    # Устанавливаем Specular Tint по умолчанию
    if bpy.app.version[0] >= 4:
        shader.inputs["Specular Tint"].default_value = (0.0, 0.0, 0.0, 1.0)  # Черный цвет (RGBA)
    else:
        shader.inputs["Specular Tint"].default_value = 0.5  # Скалярное значение для Blender 3.x


    for info_key, channel, full_item_path in textures:
        if os.path.exists(full_item_path):
            texture_processor.process_texture(full_item_path, info_key, channel)

    return material


@with_temporary_cycles_renderer
def create_material_from_textures(path, scene):
    path = bpy.path.abspath(path)
    if not os.path.exists(path):
        print(f"[BAM] [create_material_from_textures(1)] Path not found: {path}")
        return []

    path = resolve_path(path)
    if not os.path.exists(path):
        print(f"[BAM] [create_material_from_textures(3)] Path not found: {path}")
        return []

    materials = []
    materials_textures = {}

    include_subfolders = scene.include_subfolders

    def process_texture_file(full_item_path, item_name, materials_textures):
        for info_key, info_value in textures_info.items():
            suffixes = getattr(scene, info_key + "_suffix").split(",")
            channel = getattr(scene, info_key + "_channel")
            for suffix in suffixes:
                suffix = suffix.strip().lower()
                for format in get_active_image_formats().keys():
                    texture_suffix_with_extension = suffix + "." + format.lower()
                    if item_name.lower().endswith(texture_suffix_with_extension):
                        material_name = item_name[: -len(texture_suffix_with_extension)]
                        if material_name not in materials_textures:
                            materials_textures[material_name] = []
                        materials_textures[material_name].append((info_key, channel, full_item_path))

    if include_subfolders:
        for root, dirs, files in os.walk(path):
            for item in files:
                full_item_path = os.path.join(root, item)
                process_texture_file(full_item_path, item, materials_textures)
    else:
        for item in os.listdir(path):
            full_item_path = os.path.join(path, item)
            process_texture_file(full_item_path, item, materials_textures)

    for material_name, textures in materials_textures.items():
        if not any(material.bamam_checked for material in scene.material_list if material.name == material_name):
            continue

        mat = bpy.data.materials.get(material_name)

        if not mat:
            mat = bpy.data.materials.new(name=material_name)

        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        node_tree = mat.node_tree

        shader = None
        output = None
        rgb_curves = None

        for node in nodes:
            if node.type == "BSDF_PRINCIPLED":
                shader = node
            elif node.type == "OUTPUT_MATERIAL":
                output = node
            elif node.type == "ShaderNodeRGBCurve":
                rgb_curves = node

        if not shader:
            shader = nodes.new(type='ShaderNodeBsdfPrincipled')
            shader.location = (0, 0)

        if not output:
            output = nodes.new(type='ShaderNodeOutputMaterial')
            output.location = (400, 0)

        output_surface_input = output.inputs["Surface"]
        if not output_surface_input.is_linked:
            mat.node_tree.links.new(output_surface_input, shader.outputs["BSDF"])

        for node in nodes:
            if node != shader and node != output and node != rgb_curves:
                nodes.remove(node)

        ensure_principled_bsdf_connection(node_tree, shader, output)

        shader.inputs["Base Color"].default_value = (1.0, 1.0, 1.0, 1.0)


        vertical_location = 300

        # Create a dictionary to track which textures have been replaced
        replaced_textures = {key: False for key in textures_info.keys()}


        material = optimize_material_creation(scene, material_name, textures)


        for material in materials:
            material_node_manager = MaterialNodeManager(material)
            texture_nodes = [node for node in material.node_tree.nodes if node.type == 'TEX_IMAGE']

            for texture_node in texture_nodes:
                material_node_manager.connect_texture_coordinates(texture_node)
                material_node_manager.connect_mapping(texture_node)

        
        #Special event for shaders with alpha maps
        texture_found = False
        print("[BAM] Blend mode check for", material_name)
        #print("[BAM] Opacity suffixes:", getattr(scene, "opacity_suffix"))

        for format in get_active_image_formats().keys():
            suffixes = getattr(scene, "opacity_suffix").split(",")
            #print("Checking format:", format)
            for suffix in suffixes:
                texture_suffix_with_extension = suffix.strip() + "." + format.lower()
                if include_subfolders:
                    for root, _, files in os.walk(path):
                        for file in files:
                            texture_path = os.path.join(root, file)
                            if texture_path.endswith(texture_suffix_with_extension) and material_name in texture_path:
                                #print("Checking path:", texture_path)
                                if os.path.exists(texture_path):
                                    #print(f"Found texture at {texture_path}")
                                    #print(f"[BAM] Setting blend method for {material_name} using {texture_path}")
                                    mat.blend_method = scene.my_blend_mode
                                    texture_found = True
                                    break
                        if texture_found:
                            break
                else:
                    texture_path = os.path.join(path, material_name + texture_suffix_with_extension)
                    #print("Checking path:", texture_path)
                    if os.path.exists(texture_path):
                        #print(f"Found texture at {texture_path}")
                        #print(f"[BAM] Setting blend method for {material_name} using {texture_path}")
                        mat.blend_method = scene.my_blend_mode
                        texture_found = True
                        break
            if texture_found:
                break

        if not texture_found:
            print(f"[BAM] No Opacity texture found for {material_name} material")
        else:
            print(f"[BAM] Blend method set to {mat.blend_method} for material {material_name}")
            
            
            
        #Special even for shaders with displacement maps
        texture_found2 = False
        print("[BAM] Disp mode check for", material_name)
        #print("[BAM] Displcement suffixes:", getattr(scene, "displacement_suffix"))

        for format in get_active_image_formats().keys():
            suffixes = getattr(scene, "displacement_suffix").split(",")
            #print("Checking format:", format)
            for suffix in suffixes:
                texture_suffix_with_extension = suffix.strip() + "." + format.lower()
                if include_subfolders:
                    for root, _, files in os.walk(path):
                        for file in files:
                            texture_path = os.path.join(root, file)
                            if texture_path.endswith(texture_suffix_with_extension) and material_name in texture_path:
                                #print("Checking path:", texture_path)
                                if os.path.exists(texture_path):
                                    #print(f"Found texture at {texture_path}")
                                    #print(f"[BAM] Setting Disp mode for {material_name} using {texture_path}")
                                    
                                    if blender_version[0] >= 4 and blender_version[1] >= 1:
                                        mat.displacement_method = scene.my_disp_mode
                                    else:
                                        mat.cycles.displacement_method = scene.my_disp_mode
                                    
                                    
                                    texture_found2 = True
                                    
                                    break
                        if texture_found2:
                            break
                else:
                    texture_path = os.path.join(path, material_name + texture_suffix_with_extension)
                    #print("Checking path:", texture_path)
                    if os.path.exists(texture_path):
                        #print(f"Found texture at {texture_path}")
                        #print(f"[BAM] Setting Disp mode for {material_name} using {texture_path}")
                        
                        
                        if blender_version[0] >= 4 and blender_version[1] >= 1:
                            mat.displacement_method = scene.my_disp_mode
                        else:
                            mat.cycles.displacement_method = scene.my_disp_mode
                        
                        
                        texture_found2 = True
                        break
            if texture_found2:
                break

        if not texture_found2:
            print(f"[BAM] No Disp texture found for {material_name} material")
        else:
            if blender_version[0] >= 4 and blender_version[1] >= 1:
                print(f"[BAM] Disp mode set to {mat.displacement_method} for material {material_name}")
            else:
                print(f"[BAM] Disp mode set to {mat.cycles.displacement_method} for material {material_name}")
            
                    

    return materials

   
class MaterialItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()
    bamam_checked: bpy.props.BoolProperty(default=True)
    temp_bamam_checked: bpy.props.BoolProperty(default=True)

    def is_material_exists(self):
        return self.name in bpy.data.materials

    '''
    @classmethod
    def register(cls):
        bpy.types.PropertyGroup.bamam_checked = bpy.props.BoolProperty(
            name="Checked",
            get=cls.get_bamam_checked,
            set=cls.set_bamam_checked
        )

    def get_bamam_checked(self):
        return self["bamam_checked"] if "bamam_checked" in self else True

    def set_bamam_checked(self, value):
        self["bamam_checked"] = value
        self.temp_bamam_checked = value
    '''

class BAMAM_OT_check_all(bpy.types.Operator):
    bl_idname = "material.check_all"
    bl_label = "Check All"
    bl_description = "Check all materials"

    def execute(self, context):
        for material in context.scene.material_list:
            material.bamam_checked = True
        return {'FINISHED'}

class BAMAM_OT_uncheck_all(bpy.types.Operator):
    bl_idname = "material.uncheck_all"
    bl_label = "Uncheck All"
    bl_description = "Uncheck all materials"

    def execute(self, context):
        for material in context.scene.material_list:
            material.bamam_checked = False
        return {'FINISHED'}

class BAMAM_OT_invert_selection(bpy.types.Operator):
    bl_idname = "material.invert_selection"
    bl_label = "Invert Selection"
    bl_description = "Invert the selection of materials"

    def execute(self, context):
        for material in context.scene.material_list:
            material.bamam_checked = not material.bamam_checked
        return {'FINISHED'}

class BAMAM_UL_material_list(bpy.types.UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            split = layout.split(factor=0.05)

            if item.bamam_checked:
                icon_check = 'CHECKBOX_HLT'
            else:
                icon_check = 'CHECKBOX_DEHLT'

            split.prop(item, "bamam_checked", text="", toggle=True, icon=icon_check)

            # Check if the material exists in the scene
            if item.name in bpy.data.materials:
                icon_text = 'SCENE_DATA'
            else:
                icon_text = 'NONE'

            col = split.column(align=True)
            sub = col.row(align=True)
            
            
            
            sub.label(text=f"{index + 1}. {item.name}")

            # If we have an icon to display, add it
            if icon_text != 'NONE':
                sub.operator("material.dummy_operator", text="", emboss=False, icon=icon_text)

        elif self.layout_type in {'GRID'}:
            layout.prop(item, "bamam_checked", text="", toggle=True)

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        for material in scene.material_list:
            material_row = layout.row(align=True)
            material_row.template_list("BAMAM_UL_material_list", "", scene, "material_list", scene,
                                       "material_list_index", rows=12)
                                       

     
# colorspace func
def match_textures_colorspace(scene):
    for image in bpy.data.images:
        print(f"[BAM] Processing Image: {image.name}, Colorspace: {image.colorspace_settings.name}")
        for info_key, _ in textures_info.items():
            suffix = getattr(scene, f"{info_key}_suffix")
            for format in get_active_image_formats().keys():
                texture_suffix_with_extension = f"{suffix}.{format.lower()}"
                if image.name.endswith(texture_suffix_with_extension):
                    colorspace = getattr(scene, f"{info_key}_colorspace")
                    image.colorspace_settings.name = colorspace
                    print(f"[BAM] Updated Colorspace for {image.name} to {colorspace}")
                    break
                    
    for area in bpy.context.screen.areas:
        if area.type == 'NODE_EDITOR':
            area.tag_redraw()



class BAMAM_OT_match_colorspaces(bpy.types.Operator):
    bl_idname="material.match_colorspaces"
    bl_label="Scene ColorSpace Match"
    bl_description="Apply Color Space rules to all textures in Project."

    def execute(self,context):
        match_textures_colorspace(context.scene)
        self.report({'INFO'},"Color spaces matched!")
        return {'FINISHED'}


        
# Main button for creating and updating materials
class BAMAM_OT_create_bsdf(bpy.types.Operator):
    bl_idname = "material.create_bsdf"
    bl_label = "Create and update Materials"
    bl_description = "Batch Materials Creator and Updater"

    def execute(self, context):
        path = resolve_path(context.scene.texture_folder_path)
        if not os.path.exists(path):
            self.report({'ERROR'}, f"[BAMAM_OT_create_bsdf] Path not found: {path}")
            return {'CANCELLED'}



        # Log of the start of the materials update process
        print("\n")
        print("=======================================================================================")
        print(f"------------------ [BAM] Start Processing Materials (New Operation) ------------------")
        print("=======================================================================================")


        create_material_from_textures(path, context.scene)
        
        # Применяем кастомные значения после обработки всех материалов
        texture_processor = TextureProcessor(context.scene, None, None, None)
        texture_processor.apply_custom_values_to_all()
        
        return {'FINISHED'}




class BAMAM_OT_dummy_operator(bpy.types.Operator):
    bl_idname="material.dummy_operator"
    bl_label="Hi Stranger"
    bl_description="Material already exists in scene"

    def execute(self,context):
        return {'PASS_THROUGH'}


def init_props():
    bpy.types.Scene.invert_normal_map_green_channel = bpy.props.BoolProperty(
        name="Invert Normal Map Green Channel",
        description="Invert the green channel of the normal map",
        default=False
    )

    for key in texture_keys:
        if key == "specular_tint" and blender_version[0] < 4:
            setattr(bpy.types.Scene, f"{key}_use_value", bpy.props.BoolProperty(
                name="Value",
                description=f"[BAM] Use custom value for {key} map",
                default=False
            ))
            setattr(bpy.types.Scene, f"{key}_custom_value", bpy.props.FloatProperty(
                name=f"{key.capitalize()} Custom Value",
                description=f"[BAM] Custom value for {key} map",
                default=0.5,
                min=0.0,
                max=1.0
            ))
        else:
            setattr(bpy.types.Scene, f"{key}_use_value", bpy.props.BoolProperty(
                name="Value",
                description=f"[BAM] Use custom value for {key} map",
                default=False
            ))
            setattr(bpy.types.Scene, f"{key}_custom_value", bpy.props.FloatVectorProperty(
                name=f"{key.capitalize()} Custom Value",
                description=f"[BAM] Custom value for {key} map",
                subtype='COLOR_GAMMA' if key in ["basecolor", "emission", "specular_tint"] else 'NONE',
                size=4 if key in ["basecolor", "emission", "specular_tint"] else 1,
                default=(0.0, 0.0, 0.0, 0.0) if key in ["basecolor", "emission", "specular_tint"] else (1.0,),
                min=0.0,
                max=1.0
            ))

def clear_props():
    del bpy.types.Scene.invert_normal_map_green_channel
    
    for key in texture_keys:
        del bpy.types.Scene[f"{key}_use_value"]
        del bpy.types.Scene[f"{key}_custom_value"]
        
        
def update_materials_count(scene):
    path = resolve_path(scene.texture_folder_path)
    if not os.path.exists(path):
        print(f"[update_materials_count] Path not found: {path}")
        return 0

    materials_count = 0

    def check_suffixes(file, suffixes, format):
        file_lower = file.lower()
        for suffix in suffixes:
            if file_lower.endswith(f"{suffix.strip().lower()}.{format.lower()}"):
                return True
        return False

    if scene.include_subfolders:
        for root, dirs, files in os.walk(path):
            for file in files:
                for format in get_active_image_formats().keys():
                    suffixes = getattr(scene, 'basecolor_suffix').split(",")
                    if check_suffixes(file, suffixes, format):
                        materials_count += 1
                        break
    else:
        for item in os.listdir(path):
            for format in get_active_image_formats().keys():
                suffixes = getattr(scene, 'basecolor_suffix').split(",")
                if check_suffixes(item, suffixes, format):
                    materials_count += 1
                    break

    return materials_count

class BAMAM_PT_AutoMat(bpy.types.Panel):
    bl_label = "[BAM] AutoMat"
    bl_idname = "BAMAM_PT_AutoMat"
    bl_space_type = 'VIEW_3D'  # Значение по умолчанию
    bl_region_type = 'UI'      # Значение по умолчанию
    bl_category = '[BAM] AutoMat'  # Значение по умолчанию

    @classmethod
    def poll(cls, context):
        prefs = context.preferences.addons[__package__].preferences
        cls.bl_category = prefs.bl_category_material
        cls.bl_region_type = prefs.bl_region_type_material
        cls.bl_space_type = prefs.bl_space_type_material
        return True


    def draw(self, context):
        layout = self.layout
        scene = context.scene

        row = layout.row(align=True)
        split = row.split(factor=0.4)
        split.label(text="TextureFolder:")
        split.prop(scene, "texture_folder_path", text="")
        row.operator("material.force_refresh", text="", icon="FILE_REFRESH")
        row.prop(scene, "include_subfolders", text="Subfolders")

        row = layout.row(align=True)

        if scene.texture_folder_path:
            box = layout.box()
            row = box.row()
            row.scale_y = 1
            row.alignment = 'CENTER'

            materials_count = update_materials_count(scene)
            row.label(text=f"[BAM] Detected Materials in Folder: ", icon="MATSHADERBALL")
            row.label(text=f"{materials_count}", icon="KEYTYPE_JITTER_VEC" if materials_count > 0 else "KEYTYPE_EXTREME_VEC")

            row = box.row(align=True)

            row.alert = True
            row.operator("material.create_bsdf", icon="FORCE_TEXTURE")
            row = box.row(align=True)
            row.operator("material.match_colorspaces", icon="RESTRICT_COLOR_ON")

            box = layout.box()
            row = box.row()
            row.label(text=f"Definitions Presets", icon="PRESET")
            row = box.row(align=True)
            row.prop(scene, "preset_list", text="Presets")
            row = box.row()
            row.operator("material.save_preset_dialog", text="Save Preset")
            row.operator("material.delete_preset", text="Delete Preset")

            box = layout.box()
            row = box.row(align=True)
            split = row.split(factor=0.05)
            split.prop(scene, "show_texture_settings", icon='TRIA_DOWN' if scene.show_texture_settings else 'TRIA_RIGHT', emboss=False, text="")
            row = split.row(align=True)
            row.label(text="", icon='NODE_TEXTURE')
            row.label(text="TextureMap Definitions:")
            
            if scene.show_texture_settings:
                row = box.row(align=True)
                row.prop(scene, "invert_normal_map_green_channel")
                row.prop(scene, "invert_roughness")  # Добавляем чекбокс для инверсии Roughness

                row = box.row(align=True)
                split = row.split(factor=0.5)
                split.label(text="Blend Mode for Opacity")
                split.prop(scene, "my_blend_mode", text="")

                row = box.row(align=True)
                split = row.split(factor=0.5)
                split.label(text="Displacement Mode")
                split.prop(scene, "my_disp_mode", text="")

                main_suffixes = ["basecolor", "normal", "roughness", "metallic", "ao", "opacity", "displacement", "emission"]
                for suffix in main_suffixes:
                    display_name = textures_info[suffix]["display_name"]

                    row = box.row(align=True)
                    split = row.split(factor=0.3)

                    if scene.get(f"{suffix}_use_value", False):
                        row = box.row(align=True)
                        row.prop(scene, f"{suffix}_custom_value", text=display_name)
                    else:
                        split.label(text=display_name)
                        split.prop(scene, f"{suffix}_suffix", text="")
                        split.prop(scene, f"{suffix}_channel", text="")
                        row.prop(scene, f"{suffix}_colorspace", text="")
                    row.prop(scene, f"{suffix}_use_value", text="")

                row = box.row()
                row.prop(scene, "show_advanced_texture_settings", icon='TRIA_DOWN' if scene.show_advanced_texture_settings else 'TRIA_RIGHT', emboss=True, text="Additional TextureMap Definitions:")

                if scene.show_advanced_texture_settings:
                    advanced_suffixes = ["subsurface", "specular", "specular_tint", "anisotropic", "sheen", "sheen_tint", "clearcoat", "clearcoat_roughness", "ior", "transmission"]
                    for suffix in advanced_suffixes:
                        display_name = textures_info[suffix]["display_name"]

                        row = box.row(align=True)
                        split = row.split(factor=0.3)

                        if scene.get(f"{suffix}_use_value", False):
                            row = box.row(align=True)
                            row.prop(scene, f"{suffix}_custom_value", text=display_name)
                        else:
                            split.label(text=display_name)
                            split.prop(scene, f"{suffix}_suffix", text="")
                            split.prop(scene, f"{suffix}_channel", text="")
                            row.prop(scene, f"{suffix}_colorspace", text="")
                        row.prop(scene, f"{suffix}_use_value", text="")

            box = layout.box()
            row = box.row(align=True)
            split = row.split(factor=0.05)
            split.prop(scene, "show_filter", icon='TRIA_DOWN' if scene.show_filter else 'TRIA_RIGHT', emboss=False, text="")
            row = split.row(align=True)
            row.label(text="", icon='FILTER')
            row.label(text="Materials Create/Update filter")
            
            if scene.show_filter:
           
                #row.scale_y = 1
                #row.alignment = 'LEFT'
                #row.label(text="Materials Create/Update filter.", icon="FILTER")

                row = box.row(align=True)
                row.operator("material.check_all", icon='CHECKBOX_HLT')
                row.operator("material.uncheck_all", icon='CHECKBOX_DEHLT')
                row.operator("material.invert_selection", icon='ARROW_LEFTRIGHT')

                detected_materials = detect_materials_in_folder(scene)
                row = box.row(align=True)
                row = box.row(align=True)
                row.template_list("BAMAM_UL_material_list", "", scene, "material_list", scene, "material_list_index")

                if scene.material_list:
                    material = scene.material_list[scene.material_list_index]
        else:
            layout.label(text="Please select a texture folder", icon="ERROR")

# Operator for forced refresh
class BAMAM_OT_ForceRefresh(bpy.types.Operator):
    bl_idname = "material.force_refresh"
    bl_label = "Force Refresh"
    bl_description = "Refresh the texture list"
    
    def execute(self, context):
        combined_update(context.scene, context)
        return {'FINISHED'}

        
# Operator to save the preset
class BAMAM_OT_save_preset_dialog(bpy.types.Operator):
    bl_idname = "material.save_preset_dialog"
    bl_label = "Save Preset"
    bl_description = "Save Material Preset"

    preset_name: bpy.props.StringProperty(name="Preset Name")

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        scene = context.scene
        preset_name = self.preset_name.strip()
        if not preset_name:
            self.report({'WARNING'}, "Preset name cannot be empty")
            return {'CANCELLED'}

        preset_file = os.path.join(presets_dir, f"{preset_name}_bpres.json")

        settings = {
            "suffixes": {key: getattr(scene, f"{key}_suffix").split(",") for key in texture_keys},
            "channels": {key: getattr(scene, f"{key}_channel") for key in texture_keys},
            "colorspaces": {key: getattr(scene, f"{key}_colorspace") for key in texture_keys},
            "additional_settings": {
                "invert_normal_map_green_channel": scene.invert_normal_map_green_channel,
                "blend_mode": scene.my_blend_mode,
                "displacement_mode": scene.my_disp_mode
            }
        }

        with open(preset_file, 'w') as outfile:
            json.dump(settings, outfile, indent=4)

        self.report({'INFO'}, f"Preset '{preset_name}' saved")
        return {'FINISHED'}



# Operator to delete a preset
class BAMAM_OT_delete_preset(bpy.types.Operator):
    bl_idname = "material.delete_preset"
    bl_label = "Delete Preset"

    def execute(self, context):
        scene = context.scene
        preset_name = scene.preset_list
        preset_file = os.path.join(presets_dir, f"{preset_name}_bpres.json")

        if os.path.exists(preset_file):
            os.remove(preset_file)
            self.report({'INFO'}, f"Preset '{preset_name}' deleted")
        else:
            self.report({'WARNING'}, f"Preset file not found: {preset_file}")

        return {'FINISHED'}




def update_preset_items(scene, context):
    items = []
    for file in os.listdir(presets_dir):
        if file.endswith("_bpres.json"):
            preset_name = file.rsplit("_bpres.json", 1)[0]
            items.append((preset_name, preset_name, ""))
    
    # Убедимся, что Default всегда первый
    items.sort(key=lambda x: (x[0] != "Default", x[0].lower()))
    
    # Если список пуст, добавляем Default по умолчанию
    if not items:
        items = [('Default', 'Default', 'Default settings')]
    
    return items




def apply_preset_settings(scene, preset_name):
    preset_file = os.path.join(presets_dir, f"{preset_name}_bpres.json")
    if not os.path.exists(preset_file):
        print(f"Preset file not found: {preset_file}")
        return

    with open(preset_file, 'r') as infile:
        preset_settings = json.load(infile)

    # Применение настроек аналогично текущему коду
    for key, value in preset_settings["suffixes"].items():
        setattr(scene, f"{key}_suffix", ",".join(value) if isinstance(value, list) else value)

    for key, value in preset_settings["channels"].items():
        setattr(scene, f"{key}_channel", value)

    for key, value in preset_settings["colorspaces"].items():
        setattr(scene, f"{key}_colorspace", value)

    additional_settings = preset_settings.get("additional_settings", {})
    scene.invert_normal_map_green_channel = additional_settings.get("invert_normal_map_green_channel", False)
    scene.my_blend_mode = additional_settings.get("blend_mode", "HASHED")
    scene.my_disp_mode = additional_settings.get("displacement_mode", "BOTH")


def on_preset_change(self, context):
    scene = context.scene
    preset_name = scene.preset_list
    apply_preset_settings(scene, preset_name)

    # Update the UI
    for area in bpy.context.screen.areas:
        if area.type in ['PROPERTIES', 'VIEW_3D']:
            area.tag_redraw()


def load_handler(dummy):
    scene = bpy.context.scene

def update_path(scene, context):
    absolute_path = bpy.path.abspath(scene.texture_folder_path)
    if scene.texture_folder_path != absolute_path:
        scene.texture_folder_path = absolute_path
        context.area.tag_redraw()


def combined_update(scene, context):
    update_path(scene, context)
    update_material_list(scene, context)


if blender_version[0] >= 4:
    texture_properties = {
        "basecolor": ("_basecolor", "sRGB", (1.0, 1.0, 1.0, 1.0)),
        "normal": ("_normal", "Non-Color", (1.0, 1.0, 1.0)),
        "roughness": ("_roughness", "Non-Color", (1.0,)),
        "metallic": ("_metallic", "Non-Color", (1.0,)),
        "opacity": ("_opacity", "Non-Color", (1.0,)),
        "subsurface": ("_subsurface", "sRGB", (1.0,)),
        "ao": ("_ao", "sRGB", (1.0,)),
        "specular": ("_specular_ior", "Non-Color", (1.0,)),
        "specular_tint": ("_specular", "Non-Color", (0.0, 0.0, 0.0, 1.0)),
        "anisotropic": ("_anisotropic", "Non-Color", (1.0,)),
        "sheen": ("_sheen", "Non-Color", (1.0,)),
        "sheen_tint": ("_sheen_tint", "Non-Color", (1.0, 1.0, 1.0, 1.0)),
        "clearcoat": ("_clearcoat", "Non-Color", (1.0,)),
        "clearcoat_roughness": ("_clearcoat_roughness", "Non-Color", (1.0,)),
        "ior": ("_ior", "Non-Color", (1.0,)),
        "transmission": ("_transmission", "Non-Color", (1.0,)),
        "displacement": ("_height", "Non-Color", (1.0,)),
        "emission": ("_emissive", "sRGB", (1.0, 1.0, 1.0, 1.0))
    }
else:
    texture_properties = {
        "basecolor": ("_basecolor", "sRGB", (1.0, 1.0, 1.0, 1.0)),
        "normal": ("_normal", "Non-Color", (1.0, 1.0, 1.0)),
        "roughness": ("_roughness", "Non-Color", (1.0,)),
        "metallic": ("_metallic", "Non-Color", (1.0,)),
        "opacity": ("_opacity", "Non-Color", (1.0,)),
        "subsurface": ("_subsurface", "sRGB", (1.0,)),
        "ao": ("_ao", "sRGB", (1.0,)),
        "specular": ("_specular", "Non-Color", (1.0,)),
        "specular_tint": ("_specular_tint", "Non-Color", (0.5,)),
        "anisotropic": ("_anisotropic", "Non-Color", (1.0,)),
        "sheen": ("_sheen", "Non-Color", (1.0,)),
        "sheen_tint": ("_sheen_tint", "Non-Color", (1.0,)),
        "clearcoat": ("_clearcoat", "Non-Color", (1.0,)),
        "clearcoat_roughness": ("_clearcoat_roughness", "Non-Color", (1.0,)),
        "ior": ("_ior", "Non-Color", (1.0,)),
        "transmission": ("_transmission", "Non-Color", (1.0,)),
        "displacement": ("_height", "Non-Color", (1.0,)),
        "emission": ("_emissive", "sRGB", (1.0, 1.0, 1.0, 1.0))
    }


def register():

    register_class(MaterialItem)
    register_class(BAMAM_OT_check_all)
    register_class(BAMAM_OT_uncheck_all)
    register_class(BAMAM_OT_invert_selection)
    register_class(BAMAM_UL_material_list)   
    
    register_class(BAMAM_OT_dummy_operator)
    register_class(BAMAM_OT_save_preset_dialog)
    register_class(BAMAM_OT_delete_preset)
    register_class(BAMAM_OT_create_bsdf)
    register_class(BAMAM_PT_AutoMat)
    register_class(BAMAM_OT_ForceRefresh)    
    register_class(BAMAM_OT_match_colorspaces)    


    bpy.types.Scene.texture_folder_path = bpy.props.StringProperty(
        name="Texture Folder",
        subtype='DIR_PATH',
        update=combined_update,
        get=lambda self: bpy.path.abspath(self['texture_folder_path']) if 'texture_folder_path' in self else '',
        set=lambda self, value: self.__setitem__('texture_folder_path', bpy.path.abspath(value))
    )

    bpy.types.Scene.material_list = bpy.props.CollectionProperty(type=MaterialItem)
    bpy.types.Scene.material_list_index = bpy.props.IntProperty()
    
    bpy.types.Scene.new_preset_name = bpy.props.StringProperty(name="New Preset Name")

    bpy.types.Scene.show_advanced_texture_settings = bpy.props.BoolProperty(
        name="Show Advanced Texture Settings",
        description="Toggle the visibility of advanced texture settings",
        default=False
    )

    bpy.types.Scene.show_texture_settings = bpy.props.BoolProperty(
        name="Show Texture Settings",
        description="Toggle the visibility of texture settings",
        default=True
    )
    
    bpy.types.Scene.show_filter = bpy.props.BoolProperty(
        name="Show Filter",
        description="Toggle the visibility of Filter",
        default=True
    )

    bpy.types.Scene.invert_normal_map_green_channel = bpy.props.BoolProperty(
        name="Flip Normal Green Channel",
        description="Invert the Green channel of the normal map using RGB curves",
        default=False
    )
    bpy.types.Scene.invert_roughness = bpy.props.BoolProperty(
        name="Invert Roughness",
        description="Invert the roughness using RGB curves",
        default=False
    )
    bpy.types.Scene.include_subfolders = bpy.props.BoolProperty(
        name="Include Subfolders",
        description="Search for textures in subfolders",
        default=False,
        update=update_material_list
    )

    bpy.types.Scene.preset_list = bpy.props.EnumProperty(
        items=update_preset_items,
        name="Presets",
        description="Select a preset to apply",
        update=on_preset_change
    )



    for key, (suffix_default, colorspace_default, custom_value_default) in texture_properties.items():
        setattr(bpy.types.Scene, f"{key}_suffix", bpy.props.StringProperty(
            name=f"{key.capitalize()} Suffix",
            default=suffix_default,
            update=update_material_list
        ))
        setattr(bpy.types.Scene, f"{key}_colorspace", bpy.props.EnumProperty(
            items=colorspace_items,
            name=f"{key.capitalize()}: ColorSpace",
            default=colorspace_default
        ))
        setattr(bpy.types.Scene, f"{key}_use_value", bpy.props.BoolProperty(
            name=f"Value",
            description=f"Use custom value for {key.capitalize()} or set a texture",
            default=False
        ))
        setattr(bpy.types.Scene, f"{key}_custom_value", bpy.props.FloatVectorProperty(
            name=f"{key.capitalize()} Custom Value",
            description=f"Custom value for {key.capitalize()} when texture is not used",
            default=custom_value_default,
            subtype='COLOR' if len(custom_value_default) == 4 else 'NONE',
            size=len(custom_value_default)
        ))

    
    bpy.types.Scene.basecolor_suffix=bpy.props.StringProperty(
        name="Base Color Suffix",
        default="_basecolor, _albedo",
        update=update_material_list
    )
    bpy.types.Scene.ao_suffix=bpy.props.StringProperty(
        name="AO Suffix",
        default="_ao, _ambientocclusion",
    )
    bpy.types.Scene.normal_suffix=bpy.props.StringProperty(
        name="Normal Suffix",
        default="_normal, _nrm",
    )
    bpy.types.Scene.roughness_suffix=bpy.props.StringProperty(
        name="Roughness Suffix",
        default="_roughness",
    )
    bpy.types.Scene.metallic_suffix=bpy.props.StringProperty(
        name="Metallic Suffix",
        default="_metallic, _metalness",
    )
    bpy.types.Scene.opacity_suffix=bpy.props.StringProperty(
        name="Opacity Suffix",
        default="_opacity",
    )
    bpy.types.Scene.subsurface_suffix=bpy.props.StringProperty(
        name="Subsurface Suffix",
        default="_subsurface",
    )

    bpy.types.Scene.specular_suffix=bpy.props.StringProperty(
        name="Specular Suffix",
        default="_specular_ior",
    )
    bpy.types.Scene.specular_tint_suffix=bpy.props.StringProperty(
        name="Specular Tint Suffix",
        default="_specular",
    )
    bpy.types.Scene.anisotropic_suffix=bpy.props.StringProperty(
        name="Anisotropic Suffix",
        default="_anisotropic",
    )
    bpy.types.Scene.sheen_suffix=bpy.props.StringProperty(
        name="Sheen Suffix",
        default="_sheen",
    )
    bpy.types.Scene.sheen_tint_suffix=bpy.props.StringProperty(
        name="Sheen Tint Suffix",
        default="_sheen_tint",
    )
    bpy.types.Scene.clearcoat_suffix=bpy.props.StringProperty(
        name="Clearcoat Suffix",
        default="_clearcoat",
    )
    bpy.types.Scene.clearcoat_roughness_suffix=bpy.props.StringProperty(
        name="Clearcoat Roughness Suffix",
        default="_clearcoat_roughness",
    )
    bpy.types.Scene.ior_suffix=bpy.props.StringProperty(
        name="IOR Suffix",
        default="_ior",
    )
    bpy.types.Scene.transmission_suffix=bpy.props.StringProperty(
        name="Transmission Suffix",
        default="_transmission",
    )
    bpy.types.Scene.displacement_suffix=bpy.props.StringProperty(
        name="Displacement Suffix",
        default="_displacement",
    )
    bpy.types.Scene.emission_suffix=bpy.props.StringProperty(
        name="Emission Suffix",
        default="_emissive",
    )


    bpy.types.Scene.basecolor_colorspace=bpy.props.EnumProperty(
        items=colorspace_items,
        name="Base Color: ColorSpace",
        default="sRGB"
    )
    bpy.types.Scene.normal_colorspace=bpy.props.EnumProperty(
        items=colorspace_items,
        name="Normal: ColorSpace",
        default="Non-Color"
    )
    bpy.types.Scene.ao_colorspace=bpy.props.EnumProperty(
        items=colorspace_items,
        name="AO: ColorSpace",
        default="sRGB"
    )
    bpy.types.Scene.roughness_colorspace=bpy.props.EnumProperty(
        items=colorspace_items,
        name="Roughness: ColorSpace",
        default="Non-Color"
    )
    bpy.types.Scene.metallic_colorspace=bpy.props.EnumProperty(
        items=colorspace_items,
        name="Metallic: ColorSpace",
        default="Non-Color"
    )
    bpy.types.Scene.opacity_colorspace=bpy.props.EnumProperty(
        items=colorspace_items,
        name="Opacity: ColorSpace",
        default="Non-Color"
    )
    bpy.types.Scene.subsurface_colorspace=bpy.props.EnumProperty(
        items=colorspace_items,
        name="Subsurface: ColorSpace",
        default="sRGB"
    )

    bpy.types.Scene.specular_colorspace=bpy.props.EnumProperty(
        items=colorspace_items,
        name="Specular: ColorSpace",
        default="Non-Color"
    )
    bpy.types.Scene.specular_tint_colorspace=bpy.props.EnumProperty(
        items=colorspace_items,
        name="Specular Tint: ColorSpace",
        default="Non-Color"
    )
    bpy.types.Scene.anisotropic_colorspace=bpy.props.EnumProperty(
        items=colorspace_items,
        name="Anisotropic: ColorSpace",
        default="Non-Color"
    )
    bpy.types.Scene.sheen_colorspace=bpy.props.EnumProperty(
        items=colorspace_items,
        name="Sheen: ColorSpace",
        default="Non-Color"
    )
    bpy.types.Scene.sheen_tint_colorspace=bpy.props.EnumProperty(
        items=colorspace_items,
        name="Sheen Tint: ColorSpace",
        default="Non-Color"
    )
    bpy.types.Scene.clearcoat_colorspace=bpy.props.EnumProperty(
        items=colorspace_items,
        name="Clearcoat: ColorSpace",
        default="Non-Color"
    )
    bpy.types.Scene.clearcoat_roughness_colorspace=bpy.props.EnumProperty(
        items=colorspace_items,
        name="Clearcoat Roughness: ColorSpace",
        default="Non-Color"
    )
    bpy.types.Scene.ior_colorspace=bpy.props.EnumProperty(
        items=colorspace_items,
        name="IOR: ColorSpace",
        default="Non-Color"
    )
    bpy.types.Scene.transmission_colorspace=bpy.props.EnumProperty(
        items=colorspace_items,
        name="Transmission: ColorSpace",
        default="Non-Color"
    )
    bpy.types.Scene.displacement_colorspace=bpy.props.EnumProperty(
        items=colorspace_items,
        name="Displacement: ColorSpace",
        default="Non-Color"
    )
    bpy.types.Scene.emission_colorspace=bpy.props.EnumProperty(
        items=colorspace_items,
        name="Emission: ColorSpace",
        default="sRGB"
    )


    bpy.app.handlers.load_post.append(load_handler)
    bpy.app.handlers.load_post.append(update_material_list)

def unregister():
    # Handlers delete
    if update_material_list in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(update_material_list)
    if load_handler in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(load_handler)
    
    
    # Property delete
    del bpy.types.Scene.material_list_index
    del bpy.types.Scene.invert_normal_map_green_channel 
    
    del bpy.types.Scene.new_preset_name
    del bpy.types.Scene.show_advanced_texture_settings
    del bpy.types.Scene.show_texture_settings
    del bpy.types.Scene.show_filter
    del bpy.types.Scene.preset_list

    # Classes unregister
    unregister_class(MaterialItem)
    unregister_class(BAMAM_OT_check_all)
    unregister_class(BAMAM_OT_uncheck_all)
    unregister_class(BAMAM_OT_invert_selection)
    unregister_class(BAMAM_UL_material_list)
    
    unregister_class(BAMAM_OT_dummy_operator)
    unregister_class(BAMAM_OT_save_preset_dialog)
    unregister_class(BAMAM_OT_delete_preset)
    unregister_class(BAMAM_OT_create_bsdf)
    unregister_class(BAMAM_PT_AutoMat)
    unregister_class(BAMAM_OT_ForceRefresh)
    unregister_class(BAMAM_OT_match_colorspaces)

    for key in texture_properties.keys():
        delattr(bpy.types.Scene, f"{key}_suffix")
        delattr(bpy.types.Scene, f"{key}_colorspace")
        delattr(bpy.types.Scene, f"{key}_use_value")
        delattr(bpy.types.Scene, f"{key}_custom_value")

    
    del bpy.types.Scene.texture_folder_path
    del bpy.types.Scene.include_subfolders
    del bpy.types.Scene.material_list


if __name__=="__main__":
    register()