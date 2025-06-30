print("[BAM] MaterialManager Module Loaded")

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
import bmesh
import time
import math
import os
from .register import register_class, unregister_class
from bpy.types import Operator, Panel, UIList
from bpy.props import StringProperty, EnumProperty, IntProperty, BoolProperty, FloatProperty
import bpy.app as app
from bpy.app.handlers import persistent
from .BAM_MatOverlay_M import bmoverlay
from bpy_extras.view3d_utils import region_2d_to_vector_3d, region_2d_to_origin_3d
from collections import defaultdict, deque
import sys


def check_material_assigned(obj, mat_name):
    # Checks if a material is assigned to any of the slots of the selected object
    return any(slot.material and slot.material.name == mat_name for slot in obj.material_slots)

# Initialize the cache when the addon is registered, and update it only under specific conditions
material_presence_cache = {}


def update_material_presence_cache(context):
    """Optimized cache update with current material assignments."""
    global material_presence_cache
    material_presence_cache.clear()
    for obj in context.view_layer.objects:
        if obj.type == 'MESH':
            assigned_materials = {slot.material.name for slot in obj.material_slots if slot.material}
            material_presence_cache[obj.name] = assigned_materials
@persistent
def material_cache_update_handler(scene):
    """Handler to update the material presence cache."""
    update_material_presence_cache(bpy.context)
       
# Optimize registration and deletion of handlers
def register_handlers():
    if material_cache_update_handler not in bpy.app.handlers.depsgraph_update_pre:
        bpy.app.handlers.depsgraph_update_pre.append(material_cache_update_handler)

def unregister_handlers():
    if material_cache_update_handler in bpy.app.handlers.depsgraph_update_pre:
        bpy.app.handlers.depsgraph_update_pre.remove(material_cache_update_handler)



class BAMMM_OT_DuplicateMaterial(bpy.types.Operator):
    bl_idname = "material.duplicate_material"
    bl_label = "Duplicate Material"
    bl_description = "Duplicate the selected material with a '_d' suffix"

    mat_name: bpy.props.StringProperty()

    def execute(self, context):
        mat = bpy.data.materials.get(self.mat_name)
        if mat:
            dup_mat = mat.copy()
            dup_mat.name = f"{mat.name}_d"
            context.object.active_material = dup_mat
            self.report({'INFO'}, f"Material '{mat.name}' duplicated as '{dup_mat.name}'")
        else:
            self.report({'WARNING'}, "No active material to duplicate")
        return {'FINISHED'}



# Operator to show a preview of the material
class BAMMM_OT_ShowPreview(bpy.types.Operator):
    bl_idname = "material.show_preview"
    bl_label = "Show Material Preview"
    bl_description = "Show a preview of the material"

    mat_name: bpy.props.StringProperty()

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        mat = bpy.data.materials.get(self.mat_name)
        if mat:
            wm = context.window_manager
            return wm.invoke_popup(self, width=250)
        else:
            self.report({'WARNING'}, "Material not found.")
            return {'CANCELLED'}

    def draw(self, context):
        layout = self.layout
        mat = bpy.data.materials.get(self.mat_name)

        if mat and mat.preview:
            layout.template_preview(mat, show_buttons=False)
        else:
            layout.label(text="No preview available.")

# Additional function to check if the material is assigned to selected elements in Edit Mode
def is_material_assigned_to_selected(obj, mat_name):
    if obj.type == 'MESH' and obj.mode == 'EDIT':
        bm = bmesh.from_edit_mesh(obj.data)
        mat_index = None
        # Find the material index
        for i, mat in enumerate(obj.material_slots):
            if mat.material and mat.material.name == mat_name:
                mat_index = i
                break
        if mat_index is None:
            return False
        
        # Depending on the selection mode, check faces, edges, or vertices
        if bpy.context.tool_settings.mesh_select_mode[2]:  # Face select mode
            return any(face.select for face in bm.faces if face.material_index == mat_index)
        elif bpy.context.tool_settings.mesh_select_mode[1]:  # Edge select mode
            return any(edge.select for edge in bm.edges if any(face.material_index == mat_index for face in edge.link_faces))
        elif bpy.context.tool_settings.mesh_select_mode[0]:  # Vertex select mode
            return any(vert.select for vert in bm.verts if any(face.material_index == mat_index for face in vert.link_faces))
    return False


def get_uv_island_faces(obj, face_index):
    """
    Возвращает множество индексов фейсов, принадлежащих тому же UV-острову,
    что и face_index, исходя из активного UV-канала объекта (obj).
    Если UV-канала нет или у объекта нет mesh-полигонов, вернёт пустое множество.
    """
    mesh = obj.data
    uv_layer = mesh.uv_layers.active
    if not uv_layer or not mesh.polygons:
        return set()

    def round_uv(uv, prec=6):
        return (round(uv[0], prec), round(uv[1], prec))

    # Собираем, какие UV-координаты принадлежат каждому фейсу, 
    # и строим "обратный" словарь uv список индексов фейсов
    polygon_uvs = []
    uv2faces = defaultdict(set)

    for i, poly in enumerate(mesh.polygons):
        face_uv_set = set()
        for loop_idx in poly.loop_indices:
            uv = round_uv(uv_layer.data[loop_idx].uv)
            face_uv_set.add(uv)

        polygon_uvs.append(face_uv_set)

        for uv in face_uv_set:
            uv2faces[uv].add(i)

    # BFS/DFS по связанным фейсам
    visited = set()
    to_visit = deque([face_index])

    while to_visit:
        f_i = to_visit.pop()
        if f_i in visited:
            continue
        visited.add(f_i)
        # Все UV текущего фейса
        for uv in polygon_uvs[f_i]:
            neighbor_faces = uv2faces[uv]
            for nf in neighbor_faces:
                if nf not in visited:
                    to_visit.append(nf)

    return visited


class BAMMM_OT_PipetteApplyMaterial(bpy.types.Operator):
    #Применить материал с использованием пипетки
    bl_idname = "material.pipette_apply_material"
    bl_label = "Apply Material via Pipette"
    bl_description = (
        "MODE:[Click] - replace the face/slot material.\n"
        "MODE:[Click+Shift] - replace all materials on the object.\n"
        "MODE:[Click+Ctrl] - apply the material to the entire UV island.\n"
        "MODE:[Click+Alt] - apply the material to only one face.\n"
        "Use it only in Object Mode!"
    )
    bl_options = {'REGISTER', 'UNDO'}

    mat_name: bpy.props.StringProperty()

    def invoke(self, context, event):
        # Запрет на использование в Edit Mode
        obj = context.active_object
        if obj and obj.mode == 'EDIT':
            self.report({'WARNING'}, "Pipette not supported in Edit Mode. Switch to Object Mode first.")
            return {'CANCELLED'}

        # Инициируем модальные переменные
        context.window_manager.modal_handler_add(self)
        self.shift_pressed = event.shift
        self.ctrl_pressed = event.ctrl
        self.alt_pressed = event.alt

        self.report(
            {'INFO'},
            f"[BAM] Pipette mode activated for '{self.mat_name}'. (Shift={self.shift_pressed}, "
            f"Ctrl={self.ctrl_pressed}, Alt={self.alt_pressed})"
        )
        bpy.context.window.cursor_set("EYEDROPPER")
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            region = context.region
            region_data = context.space_data.region_3d
            coord = (event.mouse_region_x, event.mouse_region_y)

            view_vector = region_2d_to_vector_3d(region, region_data, coord)
            view_origin = region_2d_to_origin_3d(region, region_data, coord)
            depsgraph = context.evaluated_depsgraph_get()

            # Raycast
            result, location, normal, face_index, obj, matrix = context.scene.ray_cast(
                depsgraph, view_origin, view_vector
            )

            # Проверки на объект/материал
            if not (obj and obj.type == 'MESH'):
                self.report({'WARNING'}, "No valid mesh-object selected.")
                return {'CANCELLED'}

            mat = bpy.data.materials.get(self.mat_name)
            if not mat:
                self.report({'WARNING'}, f"Material '{self.mat_name}' not found.")
                return {'CANCELLED'}

            # (MODES LOGIC)
            if self.shift_pressed:
                # 2) SHIFT: заменить все материалы у объекта
                obj.data.materials.clear()
                obj.data.materials.append(mat)
                obj.active_material_index = 0
                self.report(
                    {'INFO'},
                    f"[BAM] '{self.mat_name}' replaced all slots on '{obj.name}'."
                )

            elif self.ctrl_pressed:
                # 3) CTRL: заменить материал во всём UV-острове
                uv_island_faces = get_uv_island_faces(obj, face_index)
                if not uv_island_faces:
                    self.report({'WARNING'}, "No UVs for apply material, try another mode.")
                    return {'CANCELLED'}

                # Создаём новый слот под этот материал (чтобы не затирать старые слоты у других фейсов)
                new_slot_index = len(obj.material_slots)
                obj.data.materials.append(mat)

                # Назначаем всем фейсам острова этот новый индекс
                for f_idx in uv_island_faces:
                    face = obj.data.polygons[f_idx]
                    face.material_index = new_slot_index

                self.report(
                    {'INFO'},
                    f"[BAM] Material '{self.mat_name}' applied to UV island ({len(uv_island_faces)} faces) on '{obj.name}'."
                )

            elif self.alt_pressed:
                # 4) ALT: применить материал ТОЛЬКО к одному фейсу
                # Создаём новый слот
                new_slot_index = len(obj.material_slots)
                obj.data.materials.append(mat)

                # Назначаем этот слот только к кликнутому фейсу
                face = obj.data.polygons[face_index]
                face.material_index = new_slot_index

                self.report(
                    {'INFO'},
                    f"[BAM] Material '{self.mat_name}' applied only to face {face_index} "
                    f"(new slot {new_slot_index}) on '{obj.name}'."
                )

            else:
                # 1) Без Shift/Ctrl/Alt: заменить материал в слоте, соответствующем кликнутому фейсу
                if not obj.material_slots:
                    # Если слотов нет, создаём первый
                    obj.data.materials.append(mat)
                    obj.active_material_index = 0
                    self.report(
                        {'INFO'},
                        f"[BAM] Material '{self.mat_name}' added as the first slot on '{obj.name}'."
                    )
                else:
                    # Заменяем материал в уже существующем слоте
                    face = obj.data.polygons[face_index]
                    mat_index = face.material_index
                    if 0 <= mat_index < len(obj.material_slots):
                        obj.material_slots[mat_index].material = mat
                        self.report(
                            {'INFO'},
                            f"[BAM] '{self.mat_name}' replaced in slot {mat_index} on '{obj.name}'."
                        )
                    else:
                        # Если индекс фейса > кол-ва слотов, добавим новый
                        obj.data.materials.append(mat)
                        new_slot_index = len(obj.material_slots) - 1
                        face.material_index = new_slot_index
                        self.report(
                            {'INFO'},
                            f"[BAM] '{self.mat_name}' added as new slot {new_slot_index} on '{obj.name}'."
                        )

            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            self.report({'INFO'}, "Pipette mode cancelled.")
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

# UL List NODE_MATERIAL
class BAMMM_UL_list(bpy.types.UIList):

    def filter_items(self, context, data, propname):
        update_material_presence_cache(context)  # вызываем тут кэш один раз для списка
        items = getattr(data, propname)
        flt_flags = [self.bitflag_filter_item] * len(items)

        filter_name = self.filter_name.lower()
        if filter_name:
            for i, item in enumerate(items):
                if not self.bitflag_filter_item & flt_flags[i]:
                    continue
                if filter_name not in item.name.lower():
                    flt_flags[i] &= ~self.bitflag_filter_item

        return flt_flags, []

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        mat = item
        obj = context.active_object
        is_assigned_in_edit_mode = False

        # Проверяем, назначен ли материал в режиме редактирования
        if obj and obj.mode == 'EDIT':
            is_assigned_in_edit_mode = is_material_assigned_to_selected(obj, mat.name)

        # Проверяем, назначен ли материал на какие-либо выбранные объекты (в режиме Object)
        selected_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
        is_assigned = any(mat.name in material_presence_cache.get(obj.name, set())
                          for obj in selected_objects)

        row = layout.row(align=True)

        # Иконка слева от индекса ( статус назначения материала)
        if is_assigned_in_edit_mode:
            btn = row.operator("material.assign_to_selected",
                               text=str(index + 1) + ".",
                               icon='KEYTYPE_MOVING_HOLD_VEC')
        elif is_assigned:
            btn = row.operator("material.assign_to_selected",
                               text=str(index + 1) + ".",
                               icon='HANDLETYPE_FREE_VEC')
        else:
            btn = row.operator("material.assign_to_selected",
                               text=str(index + 1) + ".")

        btn.mat_name = mat.name

        # Првоерка назначения материала ( это старый код)
        #is_assigned = any(check_material_assigned(obj, mat.name)
                          #for obj in context.selected_objects if obj.type == 'MESH')

        # (subnum) — пока не используется
        subnum = row.row()

        # Если включён показ количества объектов, где используется материал
        if context.scene.show_material_object_count:
            object_count = sum(mat.name in assigned_materials
                               for assigned_materials in material_presence_cache.values())

            # Кнопка с количеством объектов
            btn = row.operator("material.assign_to_selected",
                               text=f"[{object_count}]")
            btn.mat_name = mat.name

            # стандартное превью
            icon_id = mat.preview.icon_id if mat.preview else 0
            if icon_id:
                btn = row.operator("material.assign_to_selected",
                                   text="", icon_value=icon_id)
            else:
                btn = row.operator("material.assign_to_selected",
                                   text="", icon='MATERIAL')
            btn.mat_name = mat.name

            # Кнопка пипетки
            pipette_btn = row.operator("material.pipette_apply_material",
                                       text="", icon='EYEDROPPER')
            pipette_btn.mat_name = mat.name

        else:
            # Если не показываем количество, просто иконка материала
            icon_id = mat.preview.icon_id if mat.preview else 0
            if icon_id:
                btn = row.operator("material.assign_to_selected",
                                   text="", icon_value=icon_id)
            else:
                btn = row.operator("material.assign_to_selected",
                                   text="", icon='MATERIAL')
            btn.mat_name = mat.name

            # Кнопка пипетки
            pipette_btn = row.operator("material.pipette_apply_material",
                                       text="", icon='EYEDROPPER')
            pipette_btn.mat_name = mat.name

        # Делаем строку неактивной для Dots Stroke
        if mat.name == "Dots Stroke":
            row.enabled = False

        # Поле для названия материала
        sub = row.row()
        sub.scale_x = 7
        sub.prop(mat, "name", text="", emboss=False)

        # Дополнительные кнопки,
        # если включён "show_advanced_buttons"
        row = layout.row(align=True)
        if context.scene.show_advanced_buttons:
            sel_btn = row.operator("material.select_by_material", text="", icon='FACE_MAPS')
            sel_btn.mat_name = mat.name

            select_material_btn = row.operator("material.select_material", text="", icon='VIS_SEL_11')
            select_material_btn.mat_name = mat.name

            replace_mat_btn = row.operator("material.replace_material", text="", icon='OVERLAY')
            replace_mat_btn.mat_name = mat.name

def get_selected_material_count():
    selected_objects = bpy.context.selected_objects
    material_names = set()

    for obj in selected_objects:
        if obj.type == 'MESH':
            for mat_slot in obj.material_slots:
                if mat_slot.material:
                    material_names.add(mat_slot.material.name)

    return len(material_names)

def get_selected_materials(context):
    selected_materials = set()
    for obj in context.selected_objects:
        if obj.type == 'MESH':
            for slot in obj.material_slots:
                if slot.material:
                    selected_materials.add(slot.material)
    return selected_materials

class BAMMM_UL_selected_list(bpy.types.UIList):

    def filter_items(self, context, data, propname):
        update_material_presence_cache(context)  # вызываем тут кэш один раз для списка
        items = getattr(data, propname)
        flt_flags = []

        selected_objects = context.selected_objects
        selected_materials = set()
        for obj in selected_objects:
            if obj.type == 'MESH':
                for slot in obj.material_slots:
                    if slot.material:
                        selected_materials.add(slot.material.name)

        for item in items:
            # Отображаем только материалы, которые присутствуют на выбранных объектах
            if item.name in selected_materials:
                flt_flags.append(self.bitflag_filter_item)
            else:
                flt_flags.append(0)

        return flt_flags, []

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):

        mat = item
        obj = context.active_object

        # Проверяем, назначен ли материал в режиме редактирования
        is_assigned_in_edit_mode = False
        if obj and obj.mode == 'EDIT':
            is_assigned_in_edit_mode = is_material_assigned_to_selected(obj, mat.name)

        # Проверяем, назначен ли материал на какие-либо из выбранных объектов
        selected_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
        is_assigned = any(mat.name in material_presence_cache.get(obj.name, set())
                          for obj in selected_objects)

        row = layout.row(align=True)

        # Кнопка с номером в списке и "иконкой статуса" (зависит от того, назначен ли материал)
        if is_assigned_in_edit_mode:
            btn = row.operator("material.assign_to_selected",
                               text=str(index + 1) + ".",
                               icon='KEYTYPE_MOVING_HOLD_VEC')
        elif is_assigned:
            btn = row.operator("material.assign_to_selected",
                               text=str(index + 1) + ".",
                               icon='HANDLETYPE_FREE_VEC')
        else:
            btn = row.operator("material.assign_to_selected",
                               text=str(index + 1) + ".")

        btn.mat_name = mat.name

        # Ещё одна проверка (из исходного кода):
        is_assigned = any(check_material_assigned(obj, mat.name)
                          for obj in context.selected_objects if obj.type == 'MESH')

        subnum = row.row()

        # Показать количество объектов, на которых назначен материал
        if context.scene.show_material_object_count:
            object_count = sum(mat.name in assigned_materials
                               for assigned_materials in material_presence_cache.values())

            # Кнопка с количеством
            btn = row.operator("material.assign_to_selected", text=f"[{object_count}]")
            btn.mat_name = mat.name

            # --- ВСТРОЕННОЕ ПРЕВЬЮ МАТЕРИАЛА ---
            icon_id = mat.preview.icon_id if mat.preview else 0
            if icon_id:
                btn = row.operator("material.assign_to_selected", text="", icon_value=icon_id)
            else:
                btn = row.operator("material.assign_to_selected", text="", icon='MATERIAL')
            btn.mat_name = mat.name

            # Кнопка пипетки
            pipette_btn = row.operator("material.pipette_apply_material", text="", icon='EYEDROPPER')
            pipette_btn.mat_name = mat.name

        else:
            # Если не показываем кол-во, просто отрисовываем иконку материала
            icon_id = mat.preview.icon_id if mat.preview else 0
            if icon_id:
                btn = row.operator("material.assign_to_selected", text="", icon_value=icon_id)
            else:
                btn = row.operator("material.assign_to_selected", text="", icon='MATERIAL')
            btn.mat_name = mat.name

            # Кнопка пипетки
            pipette_btn = row.operator("material.pipette_apply_material", text="", icon='EYEDROPPER')
            pipette_btn.mat_name = mat.name

        # Отключаем строку, если это специальный материал
        if mat.name == "Dots Stroke":
            row.enabled = False

        # Поле для редактирования имени материала
        sub = row.row()
        sub.scale_x = 7
        sub.prop(mat, "name", text="", emboss=False)

        # Ещё одна строка под "расширенные" кнопки
        row = layout.row(align=True)

        if context.scene.show_advanced_buttons:
            sel_btn = row.operator("material.select_by_material", text="", icon='FACE_MAPS')
            sel_btn.mat_name = mat.name

            select_material_btn = row.operator("material.select_material", text="", icon='VIS_SEL_11')
            select_material_btn.mat_name = mat.name

            replace_mat_btn = row.operator("material.replace_material", text="", icon='OVERLAY')
            replace_mat_btn.mat_name = mat.name

        # Кнопка переключения на Shader Editor
        row.operator("material.switch_to_shader_editor", text="", icon='NODE_MATERIAL').mat_name = mat.name

class BAMMM_OT_SwitchToShaderEditor(bpy.types.Operator):
    bl_idname = "material.switch_to_shader_editor"
    bl_label = "Switch to Shader Editor"
    bl_description = "Switch to the Shader Editor and display the selected material"
    bl_options = {'REGISTER', 'UNDO'}

    mat_name: bpy.props.StringProperty()

    def execute(self, context):
        mat = bpy.data.materials.get(self.mat_name)
        if not mat:
            self.report({'ERROR'}, "Material not found.")
            return {'CANCELLED'}

        
        found = False
        for obj in context.selected_objects:
            if obj.type == 'MESH' and mat.name in [slot.material.name for slot in obj.material_slots if slot.material]:
                obj.active_material_index = obj.data.materials.find(mat.name)
                found = True
                break

        if not found:
            self.report({'WARNING'}, "Material not assigned to any selected object.")
            return {'CANCELLED'}

        for area in context.screen.areas:
            if area.type == 'NODE_EDITOR':
                area.spaces.active.tree_type = 'ShaderNodeTree'
                area.spaces.active.node_tree = mat.node_tree
                break
        else:
            self.report({'WARNING'}, "No Shader Editor found. Please open a Shader Editor window.")
            return {'CANCELLED'}

        return {'FINISHED'}


# Updating the cache when the context changes, e.g. selecting another object
class BAMMM_OT_UpdCache(bpy.types.Operator):
    """Updates the material presence cache based on scene changes"""
    bl_idname = "scene.update_material_presence_cache"
    bl_label = "Update Material Cache"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        update_material_presence_cache(context)
        # Trigger UI refresh if necessary
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()
        return {'FINISHED'}
    
class BAMMM_OT_ReplaceMaterial(bpy.types.Operator):
    bl_idname = "material.replace_material"
    bl_label = "Replace Material"
    bl_description = "Replace selected material with another one in all objects"
    bl_options = {'REGISTER', 'UNDO'}

    mat_name: bpy.props.StringProperty()
    target_mat_name: bpy.props.StringProperty()

    def invoke(self, context, event):
        wm = context.window_manager
        return context.window_manager.invoke_props_dialog(self, width=300)

    def execute(self, context):
        source_mat = bpy.data.materials.get(self.mat_name)
        target_mat = bpy.data.materials.get(self.target_mat_name)

        if not source_mat or not target_mat:
            self.report({'ERROR'}, "Materials not found.")
            return {'CANCELLED'}

        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                for slot in obj.material_slots:
                    if slot.material == source_mat:
                        slot.material = target_mat

        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout

        layout.label(text="Replace with:")

        # A dropdown list to select the target material
        layout.prop_search(self, "target_mat_name", bpy.data, "materials", text="Target Mat")


class BAMMM_MT_ReplaceMenu(bpy.types.Menu):
    bl_label = "Replace Material"

    mat_name: bpy.props.StringProperty()

    def draw(self, context):
        layout = self.layout
        replace_op = layout.operator("material.replace_material")
        replace_op.mat_name = self.mat_name


# Assign material to the selected object(s), faces
class BAMMM_OT_AssignToSelected(bpy.types.Operator):
    bl_idname = "material.assign_to_selected"
    bl_label = "Assign Material to Selection"
    bl_description = "[LMB] - Assign material to selected object/objects or faces. \n[SHIFT+LMB] - Replace Material. \n[CTRL+LMB] - Select Objects by Material (in scene or by selected).\n[ALT+LMB] - Select Faces by Material (in scene или by selected).\n[SHIFT+ALT+LMB] - Add to current material selection.\n[CTRL+ALT+LMB] - Material Preview (BETA)."
    bl_options = {'REGISTER', 'UNDO'}

    mat_name: bpy.props.StringProperty()

    def execute(self, context):
        mat = bpy.data.materials.get(self.mat_name)
        if mat:
            selected_objects = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']

            for obj in selected_objects:
                bpy.context.view_layer.objects.active = obj

                # If in edit mode, apply material to the selected faces
                if obj.mode == 'EDIT':
                    if mat.name not in obj.material_slots:
                        obj.data.materials.append(mat)
                    obj.active_material_index = obj.data.materials.find(mat.name)
                    bpy.ops.object.material_slot_assign()
                else:
                    # Remove all material slots from the object
                    obj.data.materials.clear()
                    # Add a new slot and assign the selected material to it
                    obj.data.materials.append(mat)
                    obj.active_material_index = 0
        
        # сразу обновим кэш, чтобы список был актуален           
        update_material_presence_cache(context)
        return {'FINISHED'}

    def invoke(self, context, event):
        if context.object and context.object.mode == 'EDIT':
            if event.alt and event.shift:
                bpy.ops.material.select_by_material('INVOKE_DEFAULT', mat_name=self.mat_name)
            elif event.alt and event.ctrl:
                bpy.ops.material.show_preview('INVOKE_DEFAULT', mat_name=self.mat_name)
            elif event.alt:
                bpy.ops.material.select_by_material('INVOKE_DEFAULT', mat_name=self.mat_name)
            elif event.ctrl or event.shift:
                # Show message if CTRL or SHIFT is pressed in edit mode
                self.report({'ERROR'}, "This operation cannot be performed in Edit Mode.")
                return {'CANCELLED'}
            else:
                # Directly call execute instead of returning an error
                return self.execute(context)
        else:
            if event.alt and event.shift:
                bpy.ops.material.select_by_material('INVOKE_DEFAULT', mat_name=self.mat_name)
            elif event.alt and event.ctrl:
                bpy.ops.material.show_preview('INVOKE_DEFAULT', mat_name=self.mat_name)
            elif event.shift:
                bpy.ops.material.replace_material('INVOKE_DEFAULT', mat_name=self.mat_name)
            elif event.ctrl:
                bpy.ops.material.select_material('INVOKE_DEFAULT', mat_name=self.mat_name)
            elif event.alt:
                bpy.ops.material.select_by_material('INVOKE_DEFAULT', mat_name=self.mat_name)
            else:
                return self.execute(context)
        return {'FINISHED'}




def show_temp_message(context, message):
    context.scene.temp_message = message
    context.scene.temp_message_start_time = time.time()

    if not bpy.app.timers.is_registered(clear_temp_message):
        bpy.app.timers.register(clear_temp_message, first_interval=1.3)

def clear_temp_message():
    if "temp_message_start_time" in bpy.context.scene:  # Убедимся, что ключ существует
        current_time = time.time()
        start_time = bpy.context.scene["temp_message_start_time"]
        if current_time - start_time >= 3:  # Убедимся, что прошло 3 секунды
            bpy.context.scene.temp_message = ""  # Очистка сообщения
            # Принудительное обновление интерфейса, если требуется
            bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
            return None  # Остановка таймера
    return 0.1  # Запланировать следующую проверку


# Function to select material to view its properties if there is no object
class BAMMM_OT_SelectMaterial(bpy.types.Operator):
    bl_idname = "material.select_material"
    bl_label = "Select objects by Material"
    bl_description = "Select objects that have the specified material. Offers to create a new object if none exists."
    bl_options = {'REGISTER', 'UNDO'}

    mat_name: bpy.props.StringProperty()
    create_sphere: bpy.props.BoolProperty(name="Create UV Sphere", default=False)

    def execute(self, context):
        mat = bpy.data.materials.get(self.mat_name)
        if not mat:
            self.report({'ERROR'}, "Material not found.")
            return {'CANCELLED'}

        # If objects are selected, work only with them
        selected_objects = context.selected_objects
        if selected_objects:
            objects_with_material = [obj for obj in selected_objects if obj.type == 'MESH' and any(
                mat.name == slot.material.name for slot in obj.material_slots if slot.material)]
        else:
            # If objects are not selected, work with all objects in the scene
            objects_with_material = [obj for obj in bpy.data.objects if obj.type == 'MESH' and any(
                mat.name == slot.material.name for slot in obj.material_slots if slot.material)]

        visible_objects_with_material = [obj for obj in objects_with_material if obj.visible_get()]

        if visible_objects_with_material:
            bpy.ops.object.select_all(action='DESELECT')
            for obj in visible_objects_with_material:
                obj.select_set(True)
                context.view_layer.objects.active = obj
        elif self.create_sphere:
            self.create_material_sphere(context, mat)
        else:
            if objects_with_material:
                message = "Objects with the material exist but might be hidden."
                show_temp_message(context, message)
                self.report({'INFO'}, message)
        return {'FINISHED'}

    def invoke(self, context, event):
        if context.object and context.object.mode == 'EDIT':
            self.report({'ERROR'}, "This operation cannot be performed in Edit Mode.")
            return {'CANCELLED'}

        mat = bpy.data.materials.get(self.mat_name)
        objects_with_material = [obj for obj in bpy.data.objects if obj.type == 'MESH' and any(mat.name == slot.material.name for slot in obj.material_slots if slot.material)]

        if not objects_with_material:
            return context.window_manager.invoke_props_dialog(self)
        else:
            return self.execute(context)

    def draw(self, context):
        self.layout.label(text="No objects with the selected material were found.")
        self.layout.prop(self, "create_sphere", text="Create a new object with this material?")

    def create_material_sphere(self, context, mat):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 0))
        sphere = context.object
        sphere.data.materials.append(mat)
        bpy.ops.object.shade_smooth()






# Function for selecting objects/polygons by material ID
class BAMMM_OT_SelectByMaterial(bpy.types.Operator):
    bl_idname = "material.select_by_material"
    bl_label = "Select faces by Material"
    bl_description = "Select faces of selected objects in scene by Material ID, if no objects selected, select faces of all objects."
    bl_options = {'REGISTER', 'UNDO'}

    mat_name: bpy.props.StringProperty()
    keep_selection: bpy.props.BoolProperty(default=False)

    def execute(self, context):
        mat = bpy.data.materials.get(self.mat_name)
        if not mat:
            self.report({'ERROR'}, "Material not found")
            return {'CANCELLED'}

        selected_objects = context.selected_objects
        if selected_objects:
            objects_to_process = [obj for obj in selected_objects if obj.type == 'MESH' and obj.visible_get() and mat.name in [slot.material.name for slot in obj.material_slots if slot.material]]
        else:
            objects_to_process = [obj for obj in bpy.data.objects if obj.type == 'MESH' and obj.visible_get() and mat.name in [slot.material.name for slot in obj.material_slots if slot.material]]

        if not objects_to_process:
            message = "No visible objects with the specified material found"
            self.report({'INFO'}, message)
            show_temp_message(context, message)
            return {'CANCELLED'}

        # Исключаем дочерние объекты и переходим в режим редактирования только для родительских объектов
        parent_objects = []
        for obj in objects_to_process:
            if obj.parent is None or obj.parent.instance_type == 'NONE':
                parent_objects.append(obj)

        if not parent_objects:
            message = "No valid parent objects to process"
            self.report({'INFO'}, message)
            show_temp_message(context, message)
            return {'CANCELLED'}

        initial_mode = context.object.mode if context.object else 'OBJECT'

        if initial_mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        if not self.keep_selection:
            bpy.ops.object.select_all(action='DESELECT')

        for obj in parent_objects:
            obj.select_set(True)
            context.view_layer.objects.active = obj
            bpy.ops.object.mode_set(mode='EDIT')
            if not self.keep_selection:
                bpy.ops.mesh.select_all(action='DESELECT')  # Сброс выделения всех лиц
            mat_index_list = [i for i, slot in enumerate(obj.material_slots) if slot.material and slot.material.name == mat.name]
            if mat_index_list:
                mat_index = mat_index_list[0]
                obj.active_material_index = mat_index
                bpy.ops.object.material_slot_select()
            bpy.ops.object.mode_set(mode='OBJECT')

        # Переключение режима редактирования для всех родительских объектов
        for obj in parent_objects:
            obj.select_set(True)

        if initial_mode == 'EDIT':
            bpy.ops.object.editmode_toggle()
        else:
            bpy.ops.object.mode_set(mode='EDIT')

        return {'FINISHED'}

    def invoke(self, context, event):
        self.keep_selection = event.alt and event.shift

        mat = bpy.data.materials.get(self.mat_name)
        if not mat:
            self.report({'ERROR'}, "Material not found.")
            return {'CANCELLED'}

        selected_objects = context.selected_objects
        if selected_objects:
            objects_to_process = [obj for obj in selected_objects if obj.type == 'MESH' and obj.visible_get() and mat.name in [slot.material.name for slot in obj.material_slots if slot.material]]
        else:
            objects_to_process = [obj for obj in bpy.data.objects if obj.type == 'MESH' and obj.visible_get() and mat.name in [slot.material.name for slot in obj.material_slots if slot.material]]

        if not objects_to_process:
            message = "No visible objects with the specified material found"
            self.report({'INFO'}, message)
            show_temp_message(context, message)
            return {'CANCELLED'}

        # Исключаем дочерние объекты и переходим в режим редактирования только для родительских объектов
        parent_objects = []
        for obj in objects_to_process:
            if obj.parent is None or obj.parent.instance_type == 'NONE':
                parent_objects.append(obj)

        if not parent_objects:
            message = "No valid parent objects to process"
            self.report({'INFO'}, message)
            show_temp_message(context, message)
            return {'CANCELLED'}

        initial_mode = context.object.mode if context.object else 'OBJECT'

        if initial_mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        if not self.keep_selection:
            bpy.ops.object.select_all(action='DESELECT')

        for obj in parent_objects:
            obj.select_set(True)

        if initial_mode == 'EDIT':
            bpy.ops.object.editmode_toggle()

        return self.execute(context)




# Button for creating material without freaking dots in the names
class BAMMM_OT_add(bpy.types.Operator):
    bl_idname = "material.add_custom"
    bl_label = "Add Material"
    bl_description = "Add new Empty Material to Blender Scene"
    bl_options = {'REGISTER', 'UNDO'}

    new_mat_name: bpy.props.StringProperty(
        name="Material Name",
        description="Name of the new material",
        default="New_Material"
    )
    
    action: bpy.props.EnumProperty(
        name="Action",
        description="What to do with the new material",
        items=[
            ('ASSIGN', "Assign to selected faces/objects", ""),
            ('ADD_SLOT', "Add as new slot", ""),
            ('ADD_SCENE', "Add to scene", "")
        ],
        default='ASSIGN'
    )

    base_color: bpy.props.FloatVectorProperty(
        name="Base Color",
        subtype='COLOR',
        size=4,
        min=0.0,
        max=1.0,
        default=(0.8, 0.8, 0.8, 1.0),
        description="Base color of the material"
    )

    roughness: bpy.props.FloatProperty(
        name="Roughness",
        description="Roughness of the material",
        min=0.0,
        max=1.0,
        default=0.5
    )

    metallic: bpy.props.FloatProperty(
        name="Metallic",
        description="Metallic property of the material",
        min=0.0,
        max=1.0,
        default=0.0
    )

    transmission: bpy.props.FloatProperty(
        name="Transmission",
        description="Transmission of the material",
        min=0.0,
        max=1.0,
        default=0.0
    )

    alpha: bpy.props.FloatProperty(
        name="Alpha",
        description="Alpha value of the material",
        min=0.0,
        max=1.0,
        default=1.0
    )

    def execute(self, context):
        name = self.new_mat_name
        name_suffix = ""

        while bpy.data.materials.get(name + name_suffix):
            if name_suffix:
                name_suffix = "_" + str(int(name_suffix.split("_")[-1]) + 1)
            else:
                name_suffix = "_1"

        new_mat = bpy.data.materials.new(name + name_suffix)
        new_mat.use_nodes = True

        # Set material properties
        bsdf = new_mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs['Base Color'].default_value = self.base_color
            bsdf.inputs['Roughness'].default_value = self.roughness
            bsdf.inputs['Metallic'].default_value = self.metallic
            if app.version >= (4, 0, 0):
                bsdf.inputs['Transmission Weight'].default_value = self.transmission
            else:
                bsdf.inputs['Transmission'].default_value = self.transmission
            bsdf.inputs['Alpha'].default_value = self.alpha

            if self.alpha < 1.0:
                new_mat.blend_method = 'HASHED'
                new_mat.shadow_method = 'HASHED'

        if self.transmission > 0:
            if app.version >= (4, 0, 0):
                new_mat.use_screen_refraction = True
                new_mat.refraction_depth = 0.004  # 4 mm
            else:
                new_mat.use_nodes = True
                new_mat.cycles.use_transparent_shadows = True
                new_mat.cycles.refract_depth = 4  # 4 mm

        if self.action == 'ASSIGN':
            self.assign_to_selected(context, new_mat)
        elif self.action == 'ADD_SLOT':
            self.add_as_new_slot(context, new_mat)
        elif self.action == 'ADD_SCENE':
            # Material is already added to the scene by default
            pass
        
        # обновление интерфейса
        for area in bpy.context.screen.areas:
            if area.type in {'VIEW_3D', 'PROPERTIES'}:
                area.tag_redraw()
        
        return {'FINISHED'}
    
    def assign_to_selected(self, context, new_mat):
        selected_objects = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']
        for obj in selected_objects:
            bpy.context.view_layer.objects.active = obj
            if obj.mode == 'EDIT':
                if new_mat.name not in obj.material_slots:
                    obj.data.materials.append(new_mat)
                obj.active_material_index = obj.data.materials.find(new_mat.name)
                bpy.ops.object.material_slot_assign()
            else:
                obj.data.materials.clear()
                obj.data.materials.append(new_mat)
                obj.active_material_index = 0

    def add_as_new_slot(self, context, new_mat):
        selected_objects = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']
        for obj in selected_objects:
            if new_mat.name not in obj.material_slots:
                obj.data.materials.append(new_mat)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "new_mat_name")
        layout.prop(self, "action")
        layout.prop(self, "base_color")
        layout.prop(self, "roughness")
        layout.prop(self, "metallic")
        layout.prop(self, "transmission")
        layout.prop(self, "alpha")
        
# Button to delete the selected material
class BAMMM_OT_remove(bpy.types.Operator):
    bl_idname = "material.remove_custom"
    bl_label = "Del Material"
    bl_description = "Delete selected material. \nShift+LMB for Delete Material + Textures Data"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if context.scene.materials_index < len(bpy.data.materials):
            mat = bpy.data.materials[context.scene.materials_index]
            mat_name = mat.name  # Сохраняем имя материала перед удалением

            # Удаление текстурных дата-блоков, если Shift нажат
            if self.shift_pressed:
                print(f"Deleting material '{mat_name}' and its texture data blocks...")
                if mat.use_nodes:
                    nodes = mat.node_tree.nodes
                    for node in nodes:
                        if node.type == 'TEX_IMAGE' and node.image:
                            print(f"Removing texture: {node.image.name}")
                            bpy.data.images.remove(node.image, do_unlink=True)

            # Удаление самого материала
            bpy.data.materials.remove(mat)
            print(f"Material '{mat_name}' removed successfully.")  # Используем сохраненное имя
        return {'FINISHED'}

    def invoke(self, context, event):
        self.shift_pressed = event.shift  # Флаг для проверки нажатия Shift
        return self.execute(context)



class BAMMM_OT_DeleteDuplicateMaterials(bpy.types.Operator):
    bl_idname = "material.delete_duplicate_materials"
    bl_label = "Delete Duplicated Materials"
    bl_description = "Replace and delete duplicated materials. \nBased on (.001 ...) suffixes. \nWill consider the material to be original by the smallest suffix if there is no material without a suffix."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        grouped_materials = {}

        for material in bpy.data.materials:
            
            parts = material.name.rsplit('.', 1)
            base_name = parts[0] if len(parts) == 2 and parts[1].isdigit() else material.name
            
            if base_name not in grouped_materials:
                grouped_materials[base_name] = []
            grouped_materials[base_name].append(material)

        for base_name, materials in grouped_materials.items():
            # Check if there is a material without a suffix
            original_material = next((m for m in materials if m.name == base_name), None)

            if not original_material:
                # If there is no material without a suffix, select the material with the smallest numeric suffix
                original_material = sorted(materials, key=lambda m: int(m.name.rsplit('.', 1)[1]) if m.name != base_name else 0)[0]

            # Replace all duplicates in the scene objects with the original material
            for duplicate_material in materials:
                if duplicate_material != original_material:
                    for obj in bpy.data.objects:
                        for slot in obj.material_slots:
                            if slot.material == duplicate_material:
                                slot.material = original_material

                    # Delete duplicate material if it is no longer used
                    if duplicate_material.users == 0:
                        bpy.data.materials.remove(duplicate_material)

        return {'FINISHED'}


# Button to delete unused material slots
class BAMMM_OT_DeleteUnusedSlots(bpy.types.Operator):
    bl_idname = "material.delete_unused_slots"
    bl_label = "Delete Unused Material Slots"
    bl_description = "Delete material slots not assigned to any face. If objects are selected, only their slots are cleared; otherwise, the whole scene."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Получаем список выделенных объектов
        selected_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']

        if selected_objects:
            # Очищаем слоты для выделенных объектов
            for obj in selected_objects:
                context.view_layer.objects.active = obj
                bpy.ops.object.material_slot_remove_unused()
        else:
            # Очищаем слоты для всех видимых объектов в сцене
            active_object = context.view_layer.objects.active

            bpy.ops.object.select_all(action='DESELECT')
            visible_objects = [obj for obj in context.view_layer.objects if obj.type == 'MESH' and obj.visible_get()]

            for obj in visible_objects:
                obj.select_set(True)

            if visible_objects:
                context.view_layer.objects.active = visible_objects[0]

            bpy.ops.object.material_slot_remove_unused()

            # Восстанавливаем предыдущее выделение
            bpy.ops.object.select_all(action='DESELECT')
            if active_object:
                active_object.select_set(True)
                context.view_layer.objects.active = active_object

        return {'FINISHED'}




# Button for deleting unused materials
class BAMMM_OT_DeleteUnusedMaterials(bpy.types.Operator):
    bl_idname = "material.delete_unused_materials"
    bl_label = "Delete Unused Materials"
    bl_description = "Delete materials not used by any object except Dots Stroke"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # A list of all materials used in objects
        used_materials = set()
        for obj in bpy.data.objects:
            for slot in obj.material_slots:
                if slot.material:
                    used_materials.add(slot.material.name)

        # Remove materials that are not used and are not "Dots Stroke"
        for mat in bpy.data.materials:
            if mat.name not in used_materials and mat.name != "Dots Stroke":
                bpy.data.materials.remove(mat)

        return {'FINISHED'}


# Update all textures in the blender scene
class BAMMM_OT_update_textures(bpy.types.Operator):
    bl_idname = "material.update_textures"
    bl_label = "Reload Textures"
    bl_description = "Reload all textures in Blender Scene or just for selected objects if any are selected"

    def execute(self, context):
        selected_objects = bpy.context.selected_objects
        if selected_objects:
            # Reload textures for selected objects only
            self.reload_textures_for_selected_objects(selected_objects)
        else:
            # Reload all textures in the scene
            self.reload_all_textures()
            
            
        # Добавляем обновление интерфейса:
        for area in context.screen.areas:
            if area.type == 'PROPERTIES':
                area.tag_redraw()
            if area.type == 'VIEW_3D':
                area.tag_redraw()
            
            
        return {'FINISHED'}

    def reload_all_textures(self):
        for image in bpy.data.images:
            try:
                image.reload()
            except Exception as e:
                print(f"Error updating texture: {image.name} - {str(e)}")

    def reload_textures_for_selected_objects(self, selected_objects):
        materials_to_update = set()
        for obj in selected_objects:
            for mat_slot in obj.material_slots:
                if mat_slot.material and mat_slot.material.use_nodes:
                    for node in mat_slot.material.node_tree.nodes:
                        if node.type == 'TEX_IMAGE' and node.image:
                            materials_to_update.add(mat_slot.material)

        for mat in materials_to_update:
            for node in mat.node_tree.nodes:
                if node.type == 'TEX_IMAGE' and node.image:
                    try:
                        node.image.reload()
                    except Exception as e:
                        print(f"Error updating texture: {node.image.name} - {str(e)}")


def clean_material_nodes(material):
    if material.use_nodes:
        nodes = material.node_tree.nodes
        links = material.node_tree.links
        
        # Find Principled BSDF and Material Output nodes
        principled_nodes = [node for node in nodes if node.type == 'BSDF_PRINCIPLED']
        output_nodes = [node for node in nodes if node.type == 'OUTPUT_MATERIAL']
        
        # Delete all nodes except Principled BSDF and Material Output
        for node in nodes:
            if node not in principled_nodes and node not in output_nodes:
                nodes.remove(node)
        
        # Clean up all links
        for link in links:
            links.remove(link)
        
        # Reconnect Principled BSDF to Material Output if they exist
        if principled_nodes and output_nodes:
            output_node = output_nodes[0]
            principled_node = principled_nodes[0]
            material.node_tree.links.new(principled_node.outputs['BSDF'], output_node.inputs['Surface'])

def clean_material_nodes_and_textures(material):
    if material.use_nodes:
        nodes = material.node_tree.nodes
        links = material.node_tree.links
        
        # Find Principled BSDF and Material Output nodes
        principled_nodes = [node for node in nodes if node.type == 'BSDF_PRINCIPLED']
        output_nodes = [node for node in nodes if node.type == 'OUTPUT_MATERIAL']
        
        # Track used textures
        used_textures = {node.image for node in nodes if node.type == 'TEX_IMAGE'}
        
        # Delete all nodes except Principled BSDF and Material Output
        for node in nodes:
            if node not in principled_nodes and node not in output_nodes:
                if node.type == 'TEX_IMAGE' and node.image:
                    used_textures.discard(node.image)
                nodes.remove(node)
        
        # Clean up all links
        for link in links:
            links.remove(link)
        
        # Reconnect Principled BSDF to Material Output if they exist
        if principled_nodes and output_nodes:
            output_node = output_nodes[0]
            principled_node = principled_nodes[0]
            material.node_tree.links.new(principled_node.outputs['BSDF'], output_node.inputs['Surface'])
        
        # Remove unused textures
        for image in bpy.data.images:
            if image not in used_textures and image.users == 0:
                bpy.data.images.remove(image)


def clean_all_materials():
    for material in bpy.data.materials:
        clean_material_nodes(material)

def clean_all_materials_and_textures():
    for material in bpy.data.materials:
        clean_material_nodes_and_textures(material)


def clean_selected_object_materials():
    selected_objects = bpy.context.selected_objects
    materials_to_clean = set()

    for obj in selected_objects:
        if obj.type == 'MESH':
            for slot in obj.material_slots:
                if slot.material:
                    materials_to_clean.add(slot.material)

    for material in materials_to_clean:
        clean_material_nodes(material)
        
def clean_selected_object_materials_and_textures():
    selected_objects = bpy.context.selected_objects
    materials_to_clean = set()

    for obj in selected_objects:
        if obj.type == 'MESH':
            for slot in obj.material_slots:
                if slot.material:
                    materials_to_clean.add(slot.material)

    for material in materials_to_clean:
        clean_material_nodes_and_textures(material)

# Создайте оператор для функции clean_all_materials
class BAMMM_OT_CleanAllMaterials(bpy.types.Operator):
    bl_idname = "material.clean_all_materials"
    bl_label = "Clean All Materials Nodes (scene or selected)"
    bl_description = "Clean all Materials by removing unnecessary nodes and links"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if bpy.context.selected_objects:
            clean_selected_object_materials()
        else:
            clean_all_materials()
        return {'FINISHED'}

class BAMMM_OT_CleanAllMaterialsAndTextures(bpy.types.Operator):
    bl_idname = "material.clean_all_materials_and_textures"
    bl_label = "Clean All Materials Nodes + Textures Data (scene or selected)"
    bl_description = "Clean all materials by removing unnecessary nodes, links, and associated texture data blocks"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if bpy.context.selected_objects:
            clean_selected_object_materials_and_textures()
        else:
            clean_all_materials_and_textures()
        return {'FINISHED'}


class BAMMM_OT_CreateMatSpheres(bpy.types.Operator):
    bl_idname = "material.create_spheres_for_materials"
    bl_label = "Create Spheres for Materials"
    bl_description = "Create Spheres for Materials"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        materials = bpy.data.materials
        num_materials = len(materials)
        if num_materials == 0:
            print("No materials found in the scene.")
            return {'CANCELLED'}
        
        # Determine the number of rows and columns for the square grid
        num_columns = math.ceil(math.sqrt(num_materials))
        num_rows = math.ceil(num_materials / num_columns)
        
        spacing = 3.0  # Distance between the spheres
        radius = 1.0  # Radius of the UVSphere
        segments = 64  # Number of segments
        rings = 32     # Number of rings

        standard_materials = {"Dots Stroke"}

        for index, material in enumerate(materials):
            if material.name in standard_materials:
                continue
            
            row = index // num_columns
            col = index % num_columns
            
            x = col * spacing
            y = row * spacing
            z = 0
            
            bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings, radius=radius, location=(x, y, z))
            sphere = bpy.context.object
            sphere.name = material.name  # Set the object's name to the material's name
            sphere.data.materials.append(material)
            
            # Shade smooth
            bpy.ops.object.shade_smooth()

        return {'FINISHED'}


class BAMMM_MT_OptionsMenu(bpy.types.Menu):
    bl_label = "Options"
    bl_idname = "BAMMM_MT_options_menu" 

    def draw(self, context):
        layout = self.layout

        layout.operator("material.delete_unused_slots", text="Clear Unused Material Slots (scene or selected)", icon='CANCEL')
        layout.operator("material.delete_unused_materials", text="Clear Unused Materials", icon='CANCEL')
        layout.operator("material.delete_duplicate_materials", text="Clear Materials Duplicates", icon='CANCEL')
        layout.operator("material.create_spheres_for_materials", text="Create MatSpheres", icon='OUTLINER_OB_POINTCLOUD')
        layout.operator("material.clean_all_materials", text="Clean All Materials Nodes (scene or selected)", icon='BRUSH_DATA')
        layout.operator("material.clean_all_materials_and_textures", text="Clean All Materials Nodes + Textures Data (scene or selected)", icon='BRUSH_DATA')
        layout.separator()
        # Create a submenu
        layout.menu("BAMMM_MT_sub_menu", text="Future Sub Menu", icon='NODE_MATERIAL')  # Изменено: добавлен явный идентификатор подменю



class BAMMM_MT_SubMenu(bpy.types.Menu):
    bl_label = "Future Sub Menu"
    bl_idname = "BAMMM_MT_sub_menu"

    def draw(self, context):
        layout = self.layout

        layout.operator("material.add_custom", text="Add Material", icon='ADD')


# Global variable to track timer status + data table for file dates
timer_reference = None
textures_last_modified = {}




def get_addon_preferences():
    try:
        return bpy.context.preferences.addons[__package__].preferences
    except KeyError:
        print("Addon preferences not found. Please check if the addon is registered correctly.")
        return None
        
def update_texture_sync_enabled(self, context):
    global timer_reference
    if self.texture_sync_enabled:
        addon_prefs = get_addon_preferences()
        if addon_prefs:
            sync_interval = addon_prefs.texture_sync_interval
            if timer_reference is None:
                print("Starting texture sync...")
                scan_textures()
                timer_reference = bpy.app.timers.register(check_for_texture_updates, first_interval=sync_interval)
    else:
        if timer_reference is not None:
            print("Stopping texture sync...")
            bpy.app.timers.unregister(timer_reference)
            timer_reference = None

def update_texture_sync_interval(self, context):
    global timer_reference
    if self.texture_sync_enabled:
        addon_prefs = get_addon_preferences()
        if addon_prefs:
            sync_interval = addon_prefs.texture_sync_interval
            # Only if synchronization is already enabled, restart the timer with a new interval
            if timer_reference is not None:
                print("Updating timer interval...")
                bpy.app.timers.unregister(timer_reference)
                timer_reference = bpy.app.timers.register(check_for_texture_updates, first_interval=sync_interval)


# Synchronize texture updates
def scan_textures():
    global textures_last_modified
    textures_last_modified.clear()
    for image in bpy.data.images:
        if image.source == 'FILE' and image.filepath:
            file_path = bpy.path.abspath(image.filepath)
            try:
                last_modified = os.path.getmtime(file_path)
                textures_last_modified[file_path] = last_modified
            except:
                textures_last_modified[file_path] = 0

def try_reload_image(image, file_path, attempts=3, delay=0.5):
    while attempts > 0:
        try:
            image.reload()
            print(f"Texture updated: {image.name}")
            break
        except Exception as e:
            print(f"Error updating texture: {e}")
            time.sleep(delay)
            attempts -= 1



def check_for_texture_updates():
    addon_prefs = get_addon_preferences()
    if addon_prefs:
        sync_interval = addon_prefs.texture_sync_interval
        if not bpy.context.scene.texture_sync_enabled:
            print("Texture sync disabled, stopping timer...")
            return None  # Stop the timer by returning None

        global textures_last_modified
        print("Checking for texture updates...")
        for file_path, last_modified in list(textures_last_modified.items()):
            try:
                new_last_modified = os.path.getmtime(file_path)
                if new_last_modified > last_modified:
                    for image in bpy.data.images:
                        if bpy.path.abspath(image.filepath) == file_path:
                            try_reload_image(image, file_path)
                            textures_last_modified[file_path] = new_last_modified
                            print(f"Texture updated: {image.name}")
            except Exception as e:
                print(f"Error updating texture: {e}")

        return sync_interval


# Функция для обновления интерфейса
def update_material_list(self, context):
    for area in context.screen.areas:
        if area.type == 'VIEW_3D':
            area.tag_redraw()
        if area.type == 'PROPERTIES':
            area.tag_redraw()


# Основная панель
class BAMMM_PT_MaterialManager(bpy.types.Panel):
    bl_label = "[BAM] MaterialManager"
    bl_idname = "BAMMM_PT_MaterialManager"
    bl_space_type = 'VIEW_3D'  # Значение по умолчанию
    bl_region_type = 'UI'      # Значение по умолчанию
    bl_category = '[BAM] AutoMat'  # Значение по умолчанию

    @classmethod
    def poll(cls, context):
        prefs = context.preferences.addons[__package__].preferences
        cls.bl_category = prefs.bl_category_bam
        cls.bl_region_type = prefs.bl_region_type_bam
        cls.bl_space_type = prefs.bl_space_type_bam
        return True
        
    def draw(self, context):
        layout = self.layout
        scn = context.scene


        row = layout.row(align=True)
        if hasattr(context.scene, "temp_message") and context.scene.temp_message:
            layout.label(text=context.scene.temp_message, icon='INFO')

        # Options Menu
        layout.menu("BAMMM_MT_options_menu", icon='PREFERENCES')

        # Main row with two columns
        split = layout.split(factor=0.5)

        # Left column: Add and Duplicate Buttons
        col_left = split.column(align=True)
        add_dup_box = col_left.box()
        add_dup_row = add_dup_box.row(align=True)
        add_material_op = add_dup_row.operator("material.add_custom", icon='ADD', text="Add Material")
        dup_material_op = add_dup_row.operator("material.duplicate_material", text="", icon='DUPLICATE')
        dup_material_op.mat_name = bpy.data.materials[scn.materials_index].name if bpy.data.materials else ""

        # Right column: Delete Material Button
        col_right = split.column(align=True)
        del_box = col_right.box()
        del_box_row = del_box.row(align=True)
        del_box_row.operator("material.remove_custom", icon='REMOVE')


        # "Update/refresh textures" button
        row = layout.row(align=True)
        row.operator("material.update_textures", icon="FILE_REFRESH")

        if bmoverlay.overlay_active:
            row.operator("view3d.toggle_bmat_overlay", text="Disable Overlay", icon='PAUSE')
        else:
            row.operator("view3d.toggle_bmat_overlay", text="Enable Overlay", icon='PLAY')

        # Sync Checkbox
        row = layout.row(align=True)
        row.prop(scn, "texture_sync_enabled")
        row.prop(scn, "show_material_preview", text="Material Preview")
        
        row = layout.row(align=True)
        # Checkbox to enable/disable counting of objects with material
        row.prop(scn, "show_material_object_count", text="ObjMat Count")
        # Checkbox to control button visibility
        row.prop(scn, "show_advanced_buttons", text="Adv Buttons")
        
        row.prop(scn, "show_selected_materials", text="Show Selected")

        # Selected Materials count label
        row = layout.row(align=True)
        selected_material_count = get_selected_material_count()
        row.label(text=f"Mats on selected: [{selected_material_count}]")
        
        # Total Materials count label
        total_material_count = len(bpy.data.materials)
        row.label(text=f"Mats total count: [{total_material_count}]")


        if scn.show_material_preview:
            box = layout.box()
            row = box.row()
            row.prop(scn, "expand_material_preview", icon="TRIA_DOWN" if scn.expand_material_preview else "TRIA_RIGHT", icon_only=True, emboss=False)
            row.label(text="Material Preview")

            if scn.expand_material_preview:
                if scn.materials_index < len(bpy.data.materials):
                    selected_material = bpy.data.materials[scn.materials_index]
                    if selected_material:
                        box.template_preview(selected_material, show_buttons=False)
                    else:
                        box.label(text="No preview available.")


        row = layout.row(align=True)
        # Use optimized UIList and other elements...
        layout.template_list("BAMMM_UL_list", "", bpy.data, "materials", scn, "materials_index")


        # Conditional display of the second list for selected materials
        if scn.show_selected_materials:
            layout.label(text="Materials on selected:")
            row = layout.row(align=True)
            layout.template_list("BAMMM_UL_selected_list", "selected", bpy.data, "materials", scn, "selected_materials_index")



def register():


    # Register a new property to control the counting of material objects
    bpy.types.Scene.show_material_object_count = bpy.props.BoolProperty(
        name="Show Material Object Count",
        description="Show the count of objects using each material",
        default=False
    )

    bpy.types.Scene.show_selected_materials = bpy.props.BoolProperty(
        name="Show Selected Materials",
        description="Show only materials assigned to selected objects",
        default=False,
        update=update_material_list
    )

    bpy.types.Scene.selected_materials_index = IntProperty()

    bpy.types.Scene.keep_selection = bpy.props.BoolProperty(
        name="Keep Selection",
        description="Keep the previous selection when selecting faces by material",
        default=False
    )

    register_handlers()
    register_class(BAMMM_OT_PipetteApplyMaterial)
    register_class(BAMMM_OT_ShowPreview)
    register_class(BAMMM_OT_UpdCache)
    register_class(BAMMM_UL_list)
    register_class(BAMMM_UL_selected_list) 
    register_class(BAMMM_OT_DuplicateMaterial)
    register_class(BAMMM_OT_add)
    register_class(BAMMM_OT_remove)
    register_class(BAMMM_OT_ReplaceMaterial)
    register_class(BAMMM_MT_ReplaceMenu)
    register_class(BAMMM_OT_update_textures)
    register_class(BAMMM_OT_DeleteUnusedSlots)
    register_class(BAMMM_OT_DeleteUnusedMaterials)
    register_class(BAMMM_OT_CreateMatSpheres)
    register_class(BAMMM_OT_AssignToSelected)
    register_class(BAMMM_OT_DeleteDuplicateMaterials)
    register_class(BAMMM_OT_SwitchToShaderEditor)
    register_class(BAMMM_OT_CleanAllMaterials)
    register_class(BAMMM_OT_CleanAllMaterialsAndTextures)

    bpy.types.Scene.temp_message = bpy.props.StringProperty()
    bpy.types.Scene.temp_message_start_time = bpy.props.FloatProperty()

    register_class(BAMMM_OT_SelectByMaterial)
    register_class(BAMMM_OT_SelectMaterial)
    register_class(BAMMM_MT_OptionsMenu)
    register_class(BAMMM_MT_SubMenu)
    register_class(BAMMM_PT_MaterialManager)

    bpy.types.Scene.materials_index=IntProperty()


    # Hide buttons 
    bpy.types.Scene.show_advanced_buttons = bpy.props.BoolProperty(
        name="Show Advanced Buttons",
        description="Show or hide advanced buttons in the Material Manager",
        default=True
    )
    
    
    # Adding EnumProperty for material thumbnail mode
    bpy.types.Scene.material_thumbnail_mode = bpy.props.EnumProperty(
        items=[
            ('OFF', 'Thumbnails OFF', ''),
            ('ON', 'Thumbnails ON', '')
        ],
        default='OFF'
    )

    bpy.types.Scene.materials_index = bpy.props.IntProperty()

    #Texture synchronization checkbox
    bpy.types.Scene.texture_sync_enabled = bpy.props.BoolProperty(
        name="Texture Sync",
        description="Automatically sync textures when their files are updated.",
        default=False,
        update=update_texture_sync_enabled
    )
    
    bpy.types.Scene.show_material_preview = bpy.props.BoolProperty(
    name="Show Material Preview",
    description="Toggle display of the Material Preview",
    default=False
    )
    
    bpy.types.Scene.expand_material_preview = bpy.props.BoolProperty(
        name="Expand Material Preview",
        description="Expand or collapse the Material Preview section",
        default=False
    )



def unregister():
    del bpy.types.Scene.show_material_object_count
    del bpy.types.Scene.show_selected_materials
    del bpy.types.Scene.selected_materials_index
    unregister_handlers()
    unregister_class(BAMMM_OT_PipetteApplyMaterial)
    unregister_class(BAMMM_OT_ShowPreview)
    unregister_class(BAMMM_OT_UpdCache)
    unregister_class(BAMMM_UL_list)
    unregister_class(BAMMM_UL_selected_list)
    unregister_class(BAMMM_OT_DuplicateMaterial)
    unregister_class(BAMMM_OT_add)
    unregister_class(BAMMM_OT_remove)
    unregister_class(BAMMM_OT_ReplaceMaterial)
    unregister_class(BAMMM_MT_ReplaceMenu)
    unregister_class(BAMMM_OT_update_textures)
    unregister_class(BAMMM_OT_DeleteUnusedSlots)
    unregister_class(BAMMM_OT_DeleteUnusedMaterials)
    unregister_class(BAMMM_OT_DeleteDuplicateMaterials)
    unregister_class(BAMMM_OT_CreateMatSpheres)
    unregister_class(BAMMM_OT_SwitchToShaderEditor)
    unregister_class(BAMMM_OT_CleanAllMaterials)
    unregister_class(BAMMM_OT_CleanAllMaterialsAndTextures)
   
    del bpy.types.Scene.temp_message
    if "temp_message" in dir(bpy.types.Scene):
        del bpy.types.Scene.temp_message
    if "temp_message_start_time" in dir(bpy.types.Scene):
        del bpy.types.Scene.temp_message_start_time

    unregister_class(BAMMM_OT_AssignToSelected)
    unregister_class(BAMMM_OT_SelectByMaterial)
    unregister_class(BAMMM_OT_SelectMaterial)
    unregister_class(BAMMM_MT_OptionsMenu)
    unregister_class(BAMMM_MT_SubMenu)
    unregister_class(BAMMM_PT_MaterialManager)
    
    del bpy.types.Scene.show_advanced_buttons
    del bpy.types.Scene.material_thumbnail_mode

    del bpy.types.Scene.materials_index

    del bpy.types.Scene.texture_sync_enabled


if __name__ == "__main__":
    register()