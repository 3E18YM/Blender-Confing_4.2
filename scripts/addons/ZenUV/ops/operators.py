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

# Zen UV Generic Opertators

import bpy
import bmesh
from bpy.props import BoolProperty
from ZenUV.utils import get_uv_islands as island_util
from ZenUV.utils.generic import (
    get_mesh_data,
    select_all,
    check_selection,
    check_selection_mode,
    switch_mesh_to_smooth_mode,
    collect_selected_objects_data,
    select_edges,
    is_island_flipped,
    resort_objects,
    select_islands,
    switch_to_edge_sel_mode,
    select_by_context,
    resort_by_type_mesh_in_edit_mode_and_sel
)

from ZenUV.utils.messages import zen_message

from ZenUV.ui.labels import ZuvLabels
from ZenUV.ui.pie import ZsPieFactory
from ZenUV.utils.blender_zen_utils import ZenPolls


class ZUV_OT_Select_UV_Overlap(bpy.types.Operator):
    bl_idname = "uv.zenuv_select_uv_overlap"
    bl_label = ZuvLabels.SELECT_OVERLAP_LABEL
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = ZuvLabels.SELECT_OVERLAP_DESC

    @classmethod
    def poll(cls, context):
        """ Validate context """
        active_object = context.active_object
        return active_object is not None and active_object.type == 'MESH' and context.mode == 'EDIT_MESH'

    def execute(self, context):

        ZsPieFactory.mark_pie_cancelled()

        for obj in context.objects_in_mode:
            me, bm = get_mesh_data(obj)
            uv_layer = bm.loops.layers.uv.verify()
            select_all(bm, action=False)
            context.scene.tool_settings.use_uv_select_sync = True
            bpy.ops.uv.select_overlap()
            overlapped_islands = island_util.get_island(context, bm, uv_layer)
            for island in overlapped_islands:
                for face in island:
                    face.select = True

            if not check_selection(context):
                zen_message(context, message="Overlappings are not found.",)

        return {'FINISHED'}


class ZUV_OT_SmoothBySharp(bpy.types.Operator):
    bl_idname = "view3d.zenuv_set_smooth_by_sharp"
    bl_label = ZuvLabels.AUTOSMOOTH_LABEL
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = ZuvLabels.AUTOSMOOTH_DESC

    @classmethod
    def poll(cls, context):
        """ Validate context """
        active_object = context.active_object
        return active_object is not None and active_object.type == 'MESH' and context.mode == 'EDIT_MESH'

    def execute(self, context):
        for obj in context.objects_in_mode:
            data = obj.data

            switch_mesh_to_smooth_mode(context)

            if data.auto_smooth_angle != 3.141590118408203:
                data.auto_smooth_angle = 3.141590118408203
                data.use_auto_smooth = True
            else:
                data.use_auto_smooth = not data.use_auto_smooth

        return {'FINISHED'}


class ZUV_OT_Isolate_Island(bpy.types.Operator):
    bl_idname = "uv.zenuv_isolate_island"
    bl_label = ZuvLabels.ISOLATE_ISLAND_LABEL
    bl_description = ZuvLabels.ISOLATE_ISLAND_DESC
    bl_options = {'REGISTER', 'UNDO'}

    isolate_mode = False
    bms = {}
    work_mode = None
    obj_in_isolation_mode = False
    selection_mode = False
    blender_sync_mode = None

    @classmethod
    def poll(cls, context):
        """ Validate context """
        active_object = context.active_object
        return active_object is not None and active_object.type == 'MESH' and context.mode == 'EDIT_MESH'

    # def invoke(self, context, event):
    #     self.bms = collect_selected_objects_data(context)
    #     self.work_mode = check_selection_mode(context)
    #     return self.execute(context)

    def execute(self, context):

        ZsPieFactory.mark_pie_cancelled()

        self.bms = collect_selected_objects_data(context)
        self.work_mode = check_selection_mode(context)

        self.blender_sync_mode = context.scene.tool_settings.use_uv_select_sync
        for obj in self.bms:
            if not self.obj_in_isolation_mode and True in [f.hide for f in self.bms[obj]['data'].faces] or self.check_isolation(context, obj):
                self.obj_in_isolation_mode = True
            if not self.selection_mode and self.bms[obj]['pre_selected_faces'] or self.bms[obj]['pre_selected_edges'] or True in [v.select for v in self.bms[obj]['data'].verts]:
                self.selection_mode = True

        # Return From Isolation
        if self.obj_in_isolation_mode:
            if context.area.type == 'VIEW_3D':
                bpy.ops.mesh.reveal(select=False)
            elif context.area.type == 'IMAGE_EDITOR':
                if self.blender_sync_mode:
                    bpy.ops.mesh.reveal(select=False)
                else:
                    for obj in self.bms:
                        bm = self.bms[obj]['data']
                        for face in bm.faces:
                            face.select = True
                        bmesh.update_edit_mesh(obj.data, loop_triangles=False)

        elif not self.obj_in_isolation_mode and self.selection_mode:
            for obj in self.bms:
                bm = self.bms[obj]['data']
                uv_layer = bm.loops.layers.uv.verify()
                islands_for_isolate = island_util.get_island(context, bm, uv_layer)
                bmesh.update_edit_mesh(obj.data, loop_triangles=False)
                faces_for_isolate = []
                for island in islands_for_isolate:
                    faces_for_isolate.extend(island)

                if context.area.type == 'VIEW_3D':
                    self.go_to_isolate_mode([f for f in bm.faces if f not in faces_for_isolate])
                elif context.area.type == 'IMAGE_EDITOR':
                    if self.blender_sync_mode:
                        self.go_to_isolate_mode([f for f in bm.faces if f not in faces_for_isolate])
                    else:
                        self.go_to_isolate_mode_in_sync([f for f in bm.faces if f not in faces_for_isolate])

                bmesh.update_edit_mesh(obj.data, loop_triangles=False)

        return {'FINISHED'}

    def go_to_isolate_mode(self, faces_to_hide):
        for face in faces_to_hide:
            face.hide_set(True)

    def go_to_isolate_mode_in_sync(self, faces_to_hide):
        for face in faces_to_hide:
            face.select = False

    def check_isolation(self, context, obj):
        if context.area.type == 'IMAGE_EDITOR' and not self.blender_sync_mode and False in [f.select for f in self.bms[obj]['data'].faces]:
            return True
        else:
            return False


class ZUV_OT_Select_UV_Island(bpy.types.Operator):
    bl_idname = "uv.zenuv_select_island"
    bl_label = ZuvLabels.SELECT_ISLAND_LABEL
    bl_description = ZuvLabels.SELECT_ISLAND_DESC
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        """ Validate context """
        active_object = context.active_object
        return active_object is not None and active_object.type == 'MESH' and context.mode == 'EDIT_MESH'

    def execute(self, context):

        ZsPieFactory.mark_pie_cancelled()

        objs = resort_objects(context, context.objects_in_mode)
        if not objs:
            return {'CANCELLED'}
        select_islands(context, objs)
        context.tool_settings.mesh_select_mode = [False, False, True]

        return {'FINISHED'}


class ZUV_OT_Select_Loop(bpy.types.Operator):
    bl_idname = "uv.zenuv_select_loop"
    bl_label = ZuvLabels.SELECT_EDGE_LOOP_LABEL
    bl_description = ZuvLabels.SELECT_EDGE_LOOP_DESC
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        """ Validate context """
        active_object = context.active_object
        return active_object is not None \
            and active_object.type == 'MESH' \
            and context.mode == 'EDIT_MESH'

    def execute(self, context):
        for obj in context.objects_in_mode:
            me, bm = get_mesh_data(obj)
            uv_layer = bm.loops.layers.uv.verify()
            bm.edges.ensure_lookup_table()
            no_sync_mode = context.space_data.type == 'IMAGE_EDITOR' and not context.scene.tool_settings.use_uv_select_sync

            if no_sync_mode:
                if ZenPolls.version_greater_3_2_0:
                    sel_loops = [lp for edge in bm.edges for lp in edge.link_loops if lp[uv_layer].select and lp[uv_layer].select_edge]
                else:
                    sel_loops = [lp for edge in bm.edges for lp in edge.link_loops if lp[uv_layer].select]
            else:
                sel_loops = [lp for edge in bm.edges for lp in edge.link_loops if edge.select]

            if not sel_loops:
                continue

            selected_edge = sel_loops[0].edge
            scope = []
            for start_loop in sel_loops:
                # CW direction
                for i in range(len(bm.edges)):
                    next_edge_in_loop = start_loop.link_loop_next.link_loop_radial_next.edge
                    next_loop = start_loop.link_loop_next.link_loop_radial_next.link_loop_next

                    if next_edge_in_loop.seam is True \
                        or next_edge_in_loop == selected_edge \
                            or next_loop.edge == start_loop.link_loop_next.link_loop_next.edge \
                            or next_loop.edge == start_loop.link_loop_radial_next.link_loop_prev.edge \
                            or len(start_loop.link_loop_next.vert.link_edges) > 4:
                        break
                    else:
                        scope.append(next_loop)
                        start_loop = next_loop

                # CCW direction
                for i in range(len(bm.edges)):
                    next_edge_in_loop = start_loop.link_loop_prev.link_loop_radial_next.edge
                    next_loop = start_loop.link_loop_prev.link_loop_radial_next.link_loop_prev

                    if next_edge_in_loop.seam is True \
                        or next_edge_in_loop == selected_edge \
                            or next_loop.edge == start_loop.link_loop_next.link_loop_next.edge \
                            or next_loop.edge == start_loop.link_loop_radial_next.link_loop_next.edge \
                            or len(start_loop.vert.link_edges) > 4:
                        break
                    else:
                        scope.append(next_loop)
                        start_loop = next_loop

                if no_sync_mode:
                    if ZenPolls.version_greater_3_2_0:
                        for lp in scope:
                            lp[uv_layer].select = True
                            lp[uv_layer].select_edge = True
                    else:
                        for lp in scope:
                            lp[uv_layer].select = True
                else:
                    for lp in scope:
                        lp.edge.select = True

            bm.select_flush_mode()

            bmesh.update_edit_mesh(me, loop_triangles=False)
            switch_to_edge_sel_mode(context)

        return {'FINISHED'}


class ZUV_OT_SelectSharp(bpy.types.Operator):
    bl_idname = "mesh.zenuv_select_sharp"
    bl_label = ZuvLabels.OT_SELECT_EDGES_SHARP_LABEL
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = ZuvLabels.OT_SELECT_EDGES_SHARP_DESC

    @classmethod
    def poll(cls, context):
        if context.objects_in_mode:
            return True
        else:
            return False

    def execute(self, context):
        for obj in context.objects_in_mode:
            me, bm = get_mesh_data(obj)
            # data = obj.data
            select_edges([e for e in bm.edges if not e.smooth])
            bmesh.update_edit_mesh(obj.data, loop_triangles=False)
        return {'FINISHED'}


class ZUV_OT_SelectSeams(bpy.types.Operator):
    bl_idname = "mesh.zenuv_select_seams"
    bl_label = ZuvLabels.OT_SELECT_EDGES_SEAM_LABEL
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = ZuvLabels.OT_SELECT_EDGES_SEAM_DESC

    @classmethod
    def poll(cls, context):
        if context.objects_in_mode:
            return True
        else:
            return False

    def execute(self, context):
        for obj in context.objects_in_mode:
            me, bm = get_mesh_data(obj)
            # data = obj.data
            select_edges([e for e in bm.edges if e.seam])
            bmesh.update_edit_mesh(obj.data, loop_triangles=False)
        return {'FINISHED'}


class ZUV_OT_SelectFlipped(bpy.types.Operator):
    bl_idname = "uv.zenuv_select_flipped"
    bl_label = ZuvLabels.OT_SELECT_FLIPPED_ISLANDS_LABEL
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = ZuvLabels.OT_SELECT_FLIPPED_ISLANDS_DESC

    @classmethod
    def poll(cls, context):
        """ Validate context """
        active_object = context.active_object
        return active_object is not None and active_object.type == 'MESH' and context.mode == 'EDIT_MESH'

    def execute(self, context):

        ZsPieFactory.mark_pie_cancelled()
        objs = resort_by_type_mesh_in_edit_mode_and_sel(context)
        if not objs:
            self.report({'WARNING'}, "Zen UV: Select something.")
            return {"CANCELLED"}

        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')
        self.clear_selection(context)

        p_flipped_count = 0
        for obj in objs:
            me, bm = get_mesh_data(obj)
            uv_layer = bm.loops.layers.uv.verify()

            for island in island_util.get_islands(context, bm):
                if is_island_flipped(island, uv_layer):
                    p_flipped_count += 1
                    select_by_context(context, bm, [island, ], state=True)

            bmesh.update_edit_mesh(me, loop_triangles=False)

        if p_flipped_count == 0:
            self.report({'INFO'}, "No flipped islands were found.")
        else:
            self.report({'INFO'}, f"Flipped islands found: {p_flipped_count}")

        return {'FINISHED'}

    def clear_selection(self, context):
        if context.area.type == 'VIEW_3D':
            bpy.ops.mesh.select_all(action='DESELECT')
        elif context.area.type == 'IMAGE_EDITOR':
            bpy.ops.uv.select_all(action='DESELECT')


class ZUV_OT_MirrorSeams(bpy.types.Operator):
    bl_idname = "mesh.zenuv_mirror_seams"
    bl_label = ZuvLabels.OT_MIRROR_SEAMS_LABEL
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = ZuvLabels.OT_MIRROR_SEAMS_DESC

    use_mirror_x: BoolProperty(
        name="X",
        default=True,
        options={'HIDDEN'}
    )
    use_mirror_y: BoolProperty(
        name="Y",
        default=False,
        options={'HIDDEN'}
    )
    use_mirror_z: BoolProperty(
        name="Z",
        default=False,
        options={'HIDDEN'}
    )

    @classmethod
    def poll(cls, context):
        if context.objects_in_mode:
            return True
        else:
            return False

    def draw(self, context):
        layout = self.layout
        layout.label(text="Axis:")
        row = layout.row(align=True)
        row.prop(self, "use_mirror_x", text="X", toggle=True)
        row.prop(self, "use_mirror_y", text="Y", toggle=True)
        row.prop(self, "use_mirror_z", text="Z", toggle=True)

    def execute(self, context):
        context.tool_settings.mesh_select_mode = [False, True, False]
        axis = set("X")
        if self.use_mirror_x:
            axis.update("X")
        else:
            axis.discard("X")
        if self.use_mirror_y:
            axis.update("Y")
        else:
            axis.discard("Y")
        if self.use_mirror_z:
            axis.update("Z")
        else:
            axis.discard("Z")

        for obj in context.objects_in_mode:
            me, bm = get_mesh_data(obj)
            bm.edges.ensure_lookup_table()
            seams = [e for e in bm.edges if e.seam]
            select_all(bm, action=False)
            for e in seams:
                e.select = True
            bpy.ops.mesh.select_mirror(axis=axis, extend=True)
            new_edges = [e for e in bm.edges if e.select]
            for e in new_edges:
                e.seam = True
            bmesh.update_edit_mesh(me, loop_triangles=False)

        return {'FINISHED'}


operators_classes = (
    ZUV_OT_SmoothBySharp,
    ZUV_OT_SelectSharp,
    ZUV_OT_SelectSeams,
    ZUV_OT_SelectFlipped,
    ZUV_OT_Select_UV_Overlap,
    ZUV_OT_Select_UV_Island,
    ZUV_OT_Select_Loop,
    ZUV_OT_Isolate_Island,
    ZUV_OT_MirrorSeams
)

if __name__ == '__main__':
    pass
