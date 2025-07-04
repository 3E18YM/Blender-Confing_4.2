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

"""
    Zen UV Stack System
"""

import bpy
import bmesh
from bpy.props import BoolProperty, FloatProperty, EnumProperty
from mathutils import Vector
from ZenUV.utils.generic import get_mesh_data, select_all, update_indexes, get_dir_vector, ZenKeyEventSolver
from ZenUV.prop.zuv_preferences import get_prefs
from ZenUV.utils.transform import bound_box
from ZenUV.stacks.utils import (
    Cluster,
    StacksSystem,
    get_master_parameters,
    # show_statistic,
    STATISTIC
)

from ZenUV.ui.labels import ZuvLabels
from ZenUV.utils.clib.lib_init import StackSolver
from ZenUV.ui.pie import ZsPieFactory
from ZenUV.utils.progress import ProgressBar
from ZenUV.utils.vlog import Log

from ZenUV.utils.generic import (
    ZUV_PANEL_CATEGORY,
    ZUV_REGION_TYPE,
    ZUV_CONTEXT
)


def unstack(context, data, direction, increment, progress: ProgressBar, relative_to_master=False):
    increment = Vector((increment, increment))
    magnitude = Vector((0.0, 0.0))
    if relative_to_master:
        master_name, master, master_cen, master_td, master_face_indices = find_master_in_data(context, data)

    for obj_name, islands in data["objs"].items():
        obj = context.scene.objects[obj_name]
        me, bm = get_mesh_data(obj)
        for island_name, indices in islands.items():
            # progress.update()
            cluster = Cluster(context, obj, [bm.faces[index] for index in indices])
            if not relative_to_master:
                master_cen = cluster.bbox["cen"]
            if increment.magnitude > 0.0:
                position = master_cen + (direction * increment) + (direction * magnitude)
            else:
                position = master_cen + direction + (direction * increment) + (direction * magnitude)
            if island_name != "master_island":
                # island = [bm.faces[index] for index in indices]
                if not relative_to_master and cluster.in_uv_area():
                    cluster.move_to(position)
                elif relative_to_master:
                    cluster.move_to(position)
                magnitude += increment
        bmesh.update_edit_mesh(me, loop_triangles=False)


def find_master_in_data(context, objs_data):
    """
        Find master island in data and return list master_name, master, position
        If master not found in DATA - try to find master by paramethers and return.
    """
    master_name = "master_island"
    for obj_name, islands in objs_data['objs'].items():
        if master_name in islands:
            indices = islands[master_name]
            master_loop_indices, position, master_td, master_face_indices = get_master_parameters(context, obj_name, indices)
            return master_name, master_loop_indices, position, master_td, master_face_indices
    for obj_name, islands in objs_data['objs'].items():
        island_name = list(islands.keys())[0]
        master_loop_indices, position, master_td, master_face_indices = get_master_parameters(context, obj_name, islands[island_name])
    return master_name, master_loop_indices, position, master_td, master_face_indices


def calc_position_distortion(island, uv_layer):
    """ Return conditional distortion by mean island position """
    pos_distortion = bound_box(islands=[island], uv_layer=uv_layer)["cen"]
    return pos_distortion


def calc_distortion_fac(bm, island_ind, uv_layer):
    """ Returns the distortion factor for a given set of polygons """
    distortion = 0
    bm.faces.ensure_lookup_table()
    island = [bm.faces[index] for index in island_ind]
    loops = [loop for face in island for loop in face.loops]
    # for face in island:
    for loop in loops:
        mesh_angle = loop.calc_angle()
        vec_0 = get_dir_vector(loop[uv_layer].uv, loop.link_loop_next[uv_layer].uv)
        vec_1 = get_dir_vector(loop[uv_layer].uv, loop.link_loop_prev[uv_layer].uv)
        uv_angle = vec_0.angle(vec_1, 0.00001)
        distortion += abs(mesh_angle - uv_angle)
    pos_distortion = calc_position_distortion(island, uv_layer)
    if max(pos_distortion) >= 1 \
            or min(pos_distortion) <= 0:
        distortion += 1
    return distortion


def find_by_condition(context, stack, selected_only):
    if selected_only:
        master_name = stack["select"]
        for obj_name, islands in stack['objs'].items():
            if master_name in islands:
                indices = islands[master_name]
                master_obj_name = obj_name
                master_island_data = {"master_island": indices}
                island_name = master_name
    else:
        distortion_dict = dict()
        # Create Distortion DICT for every island in every object
        for obj_name, islands in stack["objs"].items():
            obj = context.scene.objects[obj_name]
            me, bm = get_mesh_data(obj)
            uv_layer = bm.loops.layers.uv.verify()
            for island, indices in islands.items():
                if obj_name not in distortion_dict.keys():
                    distortion_dict[obj_name] = dict()
                obj = distortion_dict[obj_name]
                obj[island] = dict()
                obj[island]["indices"] = indices
                obj[island]["distortion"] = calc_distortion_fac(bm, indices, uv_layer)
        # Find island with minimal distortion
        min_distortion = float('inf')
        master_island = None
        for obj, islands in distortion_dict.items():
            for island, i_data in islands.items():
                if i_data["distortion"] < min_distortion:
                    master_island = dict()
                    master_island[obj] = dict()
                    master_island[obj][island] = i_data["indices"]
                    min_distortion = i_data["distortion"]

        # Store Master Island Data
        master_obj_name = list(master_island.keys())[0]
        island_name = list(master_island[master_obj_name])[0]
        indices = master_island[master_obj_name][island_name]
        master_island_data = {"master_island": indices}

    return master_obj_name, island_name, master_island_data


def detect_masters(context, sim_data, selected_only):
    stacks_count = 0
    master_obj_name = None

    for sim_index, stack in sim_data.items():
        if selected_only:
            if stack["count"] > 1 and stack["select"]:
                stacks_count += 1
                master_obj_name, island_name, master_island_data = find_by_condition(context, stack, selected_only)
            else:
                stacks_count += 1
                master_obj_name = None
        else:
            if stack["count"] > 1:
                stacks_count += 1
                master_obj_name, island_name, master_island_data = find_by_condition(context, stack, selected_only)
            else:
                stacks_count += 1
                master_obj_name = None

        if master_obj_name:
            # Implement Master Island in Sym Data
            stack["objs"][master_obj_name].pop(island_name)
            stack["objs"][master_obj_name].update(master_island_data)

    return sim_data


def get_master_position(context, data):
    """ Return position of the selected island """
    sync_uv = context.scene.tool_settings.use_uv_select_sync
    position = None
    for obj_name, islands in data["objs"].items():
        if position:
            return position
        else:
            obj = context.scene.objects[obj_name]
            me, bm = get_mesh_data(obj)
            uv_layer = bm.loops.layers.uv.verify()
            for island, indices in islands.items():
                m_island = [bm.faces[index] for index in indices]
                if sync_uv:
                    if True in [f.select for f in m_island]:
                        position = bound_box(islands=[m_island], uv_layer=uv_layer)["cen"]
                else:
                    if True in [loop[uv_layer].select for face in m_island for loop in face.loops]:
                        position = bound_box(islands=[m_island], uv_layer=uv_layer)["cen"]
    return position


class ZUV_OT_Unstack(bpy.types.Operator):
    bl_idname = "uv.zenuv_unstack"
    bl_label = ZuvLabels.OT_ZMS_UNSTACK_LABEL
    bl_description = ZuvLabels.OT_ZMS_UNSTACK_DESC
    bl_options = {'REGISTER', 'UNDO'}

    def update_break(self, context):
        if self.breakStack:
            self.increment = 1.0

    RelativeToPrimary: BoolProperty(
        name=ZuvLabels.PREF_UNSTACK_RELATIVE_LABEL,
        default=False,
        description=ZuvLabels.PREF_UNSTACK_RELATIVE_DESC
    )
    UnstackMode: EnumProperty(
        name=ZuvLabels.PREF_UNSTACK_ENUM_MODE_LABEL,
        description=ZuvLabels.PREF_UNSTACK_ENUM_MODE_DESC,
        items=[
            (
                "GLOBAL",
                ZuvLabels.PREF_UNSTACK_ENUM_MODE_GLOBAL_LABEL,
                ZuvLabels.PREF_UNSTACK_ENUM_MODE_GLOBAL_DESC
            ),
            (
                "STACKED",
                ZuvLabels.PREF_UNSTACK_ENUM_MODE_STACKED_LABEL,
                ZuvLabels.PREF_UNSTACK_ENUM_MODE_STACKED_DESC
            ),
            (
                "OVERLAPPED",
                ZuvLabels.PREF_UNSTACK_ENUM_MODE_OVERLAP_LABEL,
                ZuvLabels.PREF_UNSTACK_ENUM_MODE_OVERLAP_DESC
            ),
        ],
        default="STACKED"
    )

    breakStack: BoolProperty(
        name=ZuvLabels.PREF_UNSTACK_BREAK_LABEL,
        default=False,
        description=ZuvLabels.PREF_UNSTACK_BREAK_DESC,
        update=update_break
    )
    increment: FloatProperty(
        name=ZuvLabels.PREF_UNSTACK_INCREMENT_LABEL,
        description=ZuvLabels.PREF_UNSTACK_INCREMENT_DESC,
        min=0.0,
        max=1.0,
        step=1,
        default=1.0,
        precision=3
    )
    selected: BoolProperty(
        default=False,
        description="Selected Only",
        options={'HIDDEN'}
    )
    direction = None
    objs = None

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "UnstackMode")
        layout.prop(self, "RelativeToPrimary")
        layout.prop(self, "breakStack")
        if self.breakStack:
            layout.prop(self, "increment")

    def execute(self, context):
        self.objs = context.objects_in_mode
        if not self.objs:
            return {"CANCELLED"}
        update_indexes(self.objs)
        self.direction = get_prefs().unstack_direction
        if not self.breakStack:
            self.increment = 0.0

        progress = ProgressBar(context, 100, text_only=False)
        progress.set_text(prefix="Unstacking:", preposition=" of")

        if not self.breakStack:
            self.increment = 0.0
        stacks = StacksSystem(context)
        if self.selected:
            sim_data = stacks.forecast_selected()
        else:
            if self.UnstackMode == "STACKED":
                sim_data = stacks.get_stacked()
            if self.UnstackMode == "GLOBAL":
                sim_data = stacks.forecast_stacks()
            if self.UnstackMode == "OVERLAPPED":
                sim_data = stacks.get_overlapped()

            sim_data = detect_masters(context, sim_data, False)

        progress.iterations = len(sim_data)

        try:
            for data in sim_data.values():
                unstack(context, data, self.direction, self.increment, progress, self.RelativeToPrimary)
                progress.update()
        except Exception as e:
            progress.finish()
            Log.debug(e)
        progress.finish()
        return {'FINISHED'}


class ZUV_OT_Stack_Similar(bpy.types.Operator):
    bl_idname = "uv.zenuv_stack_similar"
    bl_label = ZuvLabels.OT_ZMS_STACK_LABEL
    bl_description = ZuvLabels.OT_ZMS_STACK_DESC
    bl_options = {'REGISTER', 'UNDO'}

    silent: BoolProperty(
        default=True,
        description="Show stacking report",
        options={'HIDDEN'}
    )
    selected: BoolProperty(
        default=False,
        description="Selected Only",
        options={'HIDDEN'}
    )

    def invoke(self, context, event):
        self.silent = not self.selected
        return self.execute(context)

    @classmethod
    def poll(cls, context):
        active_object = context.active_object
        return active_object is not None and active_object.type == 'MESH' and context.mode == 'EDIT_MESH'

    def execute(self, context):
        answer = True, "Finished"
        addon_prefs = get_prefs()
        objs = context.objects_in_mode
        if not objs:
            return {"CANCELLED"}
        update_indexes(objs)
        move_only = addon_prefs.stackMoveOnly
        # Checking that LIB is present or activated
        if not move_only:
            if not StackSolver():
                self.report(
                    {'WARNING'},
                    "Zen UV Library is not installed! Install library or switch on 'Stack Move only' in 'Stack preferences'"
                )
                return {"CANCELLED"}
        stacks = StacksSystem(context)

        progress = ProgressBar(context, 100, text_only=False)
        progress.set_text(prefix="Stacking:", preposition=" of")
        progress.current_step = 0

        if self.selected:
            input_data = stacks.clustered_selected_stacks_with_masters
        else:
            input_data = stacks.clustered_stacks_with_masters

        for master, stack in input_data(progress, self.selected):
            progress.update()
            STATISTIC["types"][master.type] += 1
            for cl in stack:
                STATISTIC["types"][cl.type] += 1
                answer = cl.remap(master, move_only=move_only)
                cl.update_mesh()
        part_report = {True: {'INFO'}, False: {'WARNING'}}

        if not self.silent:
            self.report(part_report[answer[0]], answer[1])
        else:
            self.report(part_report[True], "Finished.")

        progress.finish()

        return {'FINISHED'}


class ZUV_OT_Select_Similar(bpy.types.Operator):
    bl_idname = "uv.zenuv_select_similar"
    bl_label = ZuvLabels.OT_SELECT_SIMILAR_ISLANDS_LABEL
    bl_description = ZuvLabels.OT_SELECT_SIMILAR_ISLANDS_DESC
    bl_options = {'REGISTER', 'UNDO'}

    # select_master: BoolProperty(
    #     name=ZuvLabels.PREF_OT_SEL_SIMILAR_SELECT_MASTER_LABEL,
    #     default=True,
    #     description=ZuvLabels.PREF_OT_SEL_SIMILAR_SELECT_MASTER_DESC
    # )
    # select_stack: BoolProperty(
    #     name=ZuvLabels.PREF_OT_SEL_SIMILAR_SELECT_STACK_LABEL,
    #     default=True,
    #     description=ZuvLabels.PREF_OT_SEL_SIMILAR_SELECT_STACK_DESC,
    # )
    # area_match: BoolProperty(
    #     name=ZuvLabels.PREF_OT_AREA_MATCH_LABEL,
    #     default=True,
    #     description=ZuvLabels.PREF_OT_AREA_MATCH_DESC,
    # )

    def draw(self, context):
        context.scene.zen_uv.draw_select_similar(self.layout, context)

    @classmethod
    def poll(cls, context):
        active_object = context.active_object
        return active_object is not None and active_object.type == 'MESH' and context.mode == 'EDIT_MESH'

    def execute(self, context):

        ZsPieFactory.mark_pie_cancelled()

        props = context.scene.zen_uv
        self.objs = context.objects_in_mode
        if not self.objs:
            return {"CANCELLED"}
        if context.tool_settings.mesh_select_mode[:] != (False, False, True):
            self.report({'WARNING'}, "Switch to the Face selection mode. Otherwise, the result may not be correct.")
        if not props.op_area_match:
            self.report({'WARNING'}, "Area Match is disabled. The result may not be precise.")
        stacks = StacksSystem(context)

        progress = ProgressBar(context, 100, text_only=False)
        progress.set_text(prefix="Selecting:", preposition=" of")
        progress.current_step = 0

        for master, stack in stacks.clustered_selected_stacks_with_masters(progress, selected=True, area_match=props.op_area_match):
            master.select(props.op_select_master)
            for cl in stack:
                progress.update()
                cl.select(props.op_select_stack)
        progress.finish()
        return {'FINISHED'}


class ZUV_OT_Select_Stacked(bpy.types.Operator):
    bl_idname = "uv.zenuv_select_stacked"
    bl_label = ZuvLabels.OT_SELECT_STACKED_LABEL
    bl_description = ZuvLabels.OT_SELECT_STACKED_DESC
    bl_options = {'REGISTER', 'UNDO'}

    desc: bpy.props.StringProperty(
        name="Description",
        default=ZuvLabels.OT_SYNC_UV_MAPS_DESC,
        options={'HIDDEN'}
    )

    @classmethod
    def description(cls, context, properties):
        addon_prefs = get_prefs()
        zk_mod = addon_prefs.bl_rna.properties['zen_key_modifier'].enum_items
        zk_mod = zk_mod.get(addon_prefs.zen_key_modifier)
        cls.desc = ZuvLabels.OT_SELECT_STACKED_DESC.replace("*", zk_mod.name)
        return cls.desc

    def invoke(self, context, event):
        is_modifier_right = ZenKeyEventSolver(context, event, get_prefs()).solve()
        self.clear = not is_modifier_right
        return self.execute(context)

    @classmethod
    def poll(cls, context):
        active_object = context.active_object
        return active_object is not None and active_object.type == 'MESH' and context.mode == 'EDIT_MESH'

    def execute(self, context):
        StackedSolver = StacksSystem(context)
        stacked = StackedSolver.get_stacked()
        for_select = StackedSolver.get_stacked_faces_ids(stacked)

        for obj_name, faces_ids in for_select.items():
            obj = context.scene.objects[obj_name]
            me = obj.data
            bm = bmesh.from_edit_mesh(me)
            if self.clear:
                select_all(bm, action=False)
            for face_id in faces_ids:
                bm.faces[face_id].select = True

            bmesh.update_edit_mesh(me, loop_triangles=False)

        return {'FINISHED'}


class ZUV_OT_Select_Stack(bpy.types.Operator):
    bl_idname = "uv.zenuv_select_stack"
    bl_label = ZuvLabels.OT_SELECT_STACK_PARTS_LABEL
    bl_description = ZuvLabels.OT_SELECT_STACK_PARTS_DESC
    bl_options = {'REGISTER', 'UNDO'}

    mode: bpy.props.EnumProperty(
        name='Mode',
        items=[
            ('PRIMARIES', ZuvLabels.OT_SELECT_STACK_PRIMARY_LABEL, ''),
            ('REPLICAS', ZuvLabels.OT_SELECT_STACK_REPLICAS_LABEL, ''),
            ('SINGLES', ZuvLabels.OT_SELECT_STACK_SINGLES_LABEL, '')
        ],
        default='PRIMARIES',
        options={'HIDDEN', 'SKIP_SAVE'}
    )

    desc: bpy.props.StringProperty(name="Description", default=ZuvLabels.OT_SELECT_STACK_PARTS_DESC, options={'HIDDEN'})

    def invoke(self, context, event):
        self.objs = context.objects_in_mode
        if not self.objs:
            return {"CANCELLED"}

        is_modifier_right = ZenKeyEventSolver(context, event, get_prefs()).solve()

        if not is_modifier_right:
            bpy.ops.mesh.select_all(action='DESELECT')
        return self.execute(context)

    @classmethod
    def description(cls, context, properties):
        desc = properties.desc
        return desc

    @classmethod
    def poll(cls, context):
        active_object = context.active_object
        return active_object is not None and active_object.type == 'MESH' and context.mode == 'EDIT_MESH'

    def execute(self, context):
        stacks = StacksSystem(context)

        progress = ProgressBar(context, 100, text_only=False)
        progress.set_text(prefix="Search:", preposition=" of")
        progress.update()
        progress.current_step = 0

        if self.mode == 'SINGLES':
            for singleton in stacks.clustered_singletons(progress):
                singleton.select(True)
        else:
            for master, stack in stacks.clustered_stacks_with_masters(progress, selected=False):
                progress.update()
                if self.mode == 'PRIMARIES':
                    master.select(True)
                if self.mode == 'REPLICAS':
                    for cl in stack:
                        cl.select(True)

        if progress.pb is not None:
            progress.finish()

        return {'FINISHED'}


def draw_substack(layout: bpy.types.UILayout, context: bpy.types.Context):
    from ZenUV.zen_checker.check_utils import draw_checker_display_items, t_draw_stack_modes

    draw_checker_display_items(layout, context, t_draw_stack_modes)

    t_extra = {
        'PRIMARIES': ZuvLabels.OT_SELECT_STACK_PRIMARY_DESC,
        'REPLICAS': ZuvLabels.OT_SELECT_STACK_REPLICAS_DESC,
        'SINGLES': ZuvLabels.OT_SELECT_STACK_SINGLES_DESC
    }

    if context.space_data.type != 'IMAGE_EDITOR':
        col = layout.column(align=True)
        for k, v in t_extra.items():
            row = col.row(align=True)
            op = row.operator("uv.zenuv_select_stack", text=k.title(), icon="RESTRICT_SELECT_OFF")
            op.mode = k
            op.desc = v


class ZUV_PT_3DV_SubStack(bpy.types.Panel):
    bl_label = 'Stacks'
    bl_context = ZUV_CONTEXT
    bl_space_type = "VIEW_3D"
    bl_region_type = ZUV_REGION_TYPE
    bl_category = ZUV_PANEL_CATEGORY
    # bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "ZUV_PT_Stack"

    def draw_header(self, context: bpy.types.Context):
        layout = self.layout

        layout.popover(panel='STACK_PT_DrawProperties', text='', icon='PREFERENCES')

    def draw(self, context):
        draw_substack(self.layout, context)
        pass


class ZUV_PT_UVL_SubStack(bpy.types.Panel):
    bl_label = 'Stacks'
    bl_context = ZUV_CONTEXT
    bl_space_type = "IMAGE_EDITOR"
    bl_region_type = ZUV_REGION_TYPE
    bl_category = ZUV_PANEL_CATEGORY
    # bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "ZUV_PT_UVL_Stack"

    draw_header = ZUV_PT_3DV_SubStack.draw_header

    draw = ZUV_PT_3DV_SubStack.draw


if __name__ == '__main__':
    pass
