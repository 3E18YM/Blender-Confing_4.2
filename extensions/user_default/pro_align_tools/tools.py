from .common_imports import *

import os


# -- Main Tools --

def get_toolbar_icon(icon_name):

    current_filepath = os.path.dirname(__file__)

    return os.path.join(current_filepath, "icons", icon_name)


class ALIGNTOOL_tool_object(WorkSpaceTool):

    bl_idname = "align_tool.tool_object"
    bl_label = "Align"
    bl_description = "Align several objects at once"
    bl_space_type = 'VIEW_3D'
    bl_context_mode = 'OBJECT'
    bl_icon = get_toolbar_icon("toolbar_align")
    bl_widget = "ALIGNTOOL_GGT_common_gizmo_group"
    # to use when addon keymaps bug is solved, then remove current shortcuts registration
    # bl_keymap = (("proaligntools.align_objects",
    #              {"type": "RET", "value": "PRESS"},
    #              None),)
    xy = [(0, 0)]


    def draw_cursor(context, tool, xy):

        if context.area.spaces[0].show_gizmo:

            if ALIGNTOOL_tool_object.xy[0] != xy:

                context.area.tag_redraw() # this produces flickering on 3D view. Replace by something else
                ALIGNTOOL_tool_object.xy[0] = xy


    def draw_settings(context, layout, tool):

        layout.use_property_split = False
        wm = context.window_manager
        ui_scale = context.preferences.system.ui_scale
        addon = wm.align_tool
        icons = addon.icons[0]

        col = layout.column(align=True)

        row = col.row(align=True)
        row.operator("proaligntools.align_objects")

        col.separator()

        split = col.split(align=False)
        split.scale_y = context.region.width / (90 * ui_scale)
        split.prop(addon, "align_min", icon_value=icons["min"].icon_id)
        split.prop(addon, "align_center", icon_value=icons["center"].icon_id)
        split.prop(addon, "align_max", icon_value=icons["max"].icon_id)

        col.separator()

        is_perpendicular = addon.direction_custom_orientation == "PERPENDICULAR"
        box = col.box()
        split = box.split(factor=0.65, align=True)
        row = split.row(align=True)
        row.alignment = "LEFT"
        row.prop(addon, "direction_panel", icon="TRIA_DOWN" if addon.direction_panel else "TRIA_RIGHT", emboss=False)
        row = split.row(align=True)
        row.alignment = "RIGHT"
        current_direction = "Perp" if is_perpendicular else addon.direction_axis
        row.prop(addon, "direction_panel", text=current_direction, icon="BLANK1", emboss=False)


        if addon.direction_panel:

            col2 = box.column(align=True)
            row = col2.row(align=True)
            row.active = False if is_perpendicular else True
            row.prop(addon, "direction_axis", expand=True)

            col2.separator()

            col2.prop(addon, "direction_custom_orientation", text="")

            if addon.direction_custom_orientation == "LOCAL":

                all_as_group = (addon.origin_target == "OBJECTS"
                                and addon.origin_type == "BOUNDS"
                                and not addon.origin_use_local
                                and addon.origin_all_selected)

                row = col2.row(align=True)
                row.active = not all_as_group
                row.prop(addon, "direction_reference", expand=True)


        col.separator()

        box = col.box()
        split = box.split(factor=0.7)
        row = split.row(align=True)
        row.alignment = "LEFT"
        row.prop(addon, "plane_panel", text="Plane", icon="TRIA_DOWN" if addon.plane_panel else "TRIA_RIGHT", emboss=False)
        row = split.row(align=True)
        row.alignment = "RIGHT"
        row.prop(addon, "plane_show_bounds", text="", icon="SHADING_BBOX")


        if addon.plane_panel:

            col2 = box.column()
            row = col2.row(align=True)
            row.prop(addon, "plane_axis", expand=True)

            bounds_use = addon.plane_target == "OBJECT" and addon.plane_type == "BOUNDS"

            row = col2.row(align=True)
            row.active = bounds_use
            row.prop(addon, "plane_depth", expand=True)

            col2 = box.column(align=True)

            col2.label(text="Target:")
            row = col2.row(align=True)
            row.prop_enum(addon, "plane_target", "WORLD")
            row.prop_enum(addon, "plane_target", "CURSOR")
            row.prop_enum(addon, "plane_target", "OBJECT")

            if addon.plane_target == "CUSTOM":
                col2.separator()
                row = col2.row()
                row.label(text="Custom Plane")
                row.operator("proaligntools.delete_plane", text="", icon="X")

            else:
                col2.separator()
                row = col2.row()
                row.active = not bounds_use
                row.prop(addon, "plane_orientation", text="")

                if addon.plane_orientation == "":
                    addon.plane_orientation = "GLOBAL"

                if addon.plane_target == "OBJECT":
                    col2.separator()
                    if addon.plane_object:
                        col2.prop_search(addon, "plane_object", context.scene, "objects", text="")
                    else:
                        col2.prop(addon, "plane_object_picker", text="")

                    col2.separator()
                    row = col2.row(align=True)
                    row.prop(addon, "plane_type", expand=True)

                    if addon.plane_type == "BOUNDS":

                        if not addon.plane_object:
                            col2.separator()
                            row = col2.row(align=True)
                            row.prop(addon, "plane_reference", expand=True)

                        col2.separator()
                        col2.prop(addon, "plane_use_local", icon="ORIENTATION_LOCAL")

                        if True in (not addon.plane_use_local,
                                    not bool(addon.plane_object) and addon.plane_reference == "SELECTED"):
                            col2.separator()
                            col2.prop(addon, "plane_use_geometry", icon="MESH_ICOSPHERE")

        col.separator()

        box = col.box()
        split = box.split(factor=0.7)
        row = split.row(align=True)
        row.alignment = "LEFT"
        row.prop(addon, "origin_panel", icon="TRIA_DOWN" if addon.origin_panel else "TRIA_RIGHT", emboss=False)
        row = split.row(align=True)
        row.alignment = "RIGHT"
        row.prop(addon, "origin_show_bounds", text="", icon="SHADING_BBOX")


        if addon.origin_panel:

            col2 = box.column(align=True)

            col2.label(text="Target:")

            row = col2.row()
            row.prop(addon, "origin_target", expand=True)

            if addon.origin_target == "OBJECTS":
                col2 = box.column()
                row = col2.row(align=True)
                row.prop_enum(addon, "origin_type", "LOCATION")
                row.prop_enum(addon, "origin_type", "BOUNDS")

                if addon.origin_type == "BOUNDS":

                    col2.separator()
                    split = col2.split(factor=0.15)
                    split.label(text="X:")
                    row = split.row(align=True)
                    row.prop(addon, "origin_depth_X", expand=True)

                    split = col2.split(factor=0.15)
                    split.label(text="Y:")
                    row = split.row(align=True)
                    row.prop(addon, "origin_depth_Y", expand=True)

                    split = col2.split(factor=0.15)
                    split.label(text="Z:")
                    row = split.row()
                    row.prop(addon, "origin_depth_Z", expand=True)

                    col2 = box.column(align=True)
                    row = col2.row(align=True)
                    row.active = False if addon.origin_use_local else True
                    row.prop(addon, "origin_all_selected")
                    col2.separator()
                    col2.prop(addon, "origin_use_local", icon="ORIENTATION_LOCAL")
                    col2.separator()

                    if not addon.origin_use_local:
                        col2.prop(addon, "origin_use_geometry", icon="MESH_ICOSPHERE")

                elif addon.origin_type == "CUSTOM":

                    object_name = addon.CACHE["custom_origin"]["object"]
                    col2 = box.column(align=True)
                    row = col2.row()
                    row.label(text=f"Vertex in: {object_name}")
                    row.operator("proaligntools.delete_origin", text="", icon="X")

        col.separator()

        col.prop(addon, "geometry_update", icon="MESH_DATA")


class ALIGNTOOL_tool_edit(WorkSpaceTool):

    bl_idname = "align_tool.tool_edit"
    bl_label = "Align"
    bl_description = "Align several objects at once"
    bl_space_type = 'VIEW_3D'
    bl_context_mode = 'EDIT_MESH'
    bl_icon = get_toolbar_icon("toolbar_align")
    bl_widget = "ALIGNTOOL_GGT_common_gizmo_group"
    xy = [(0, 0)]


    def draw_cursor(context, tool, xy):

        if context.area.spaces[0].show_gizmo:

            if ALIGNTOOL_tool_edit.xy[0] != xy:

                context.area.tag_redraw()
                ALIGNTOOL_tool_edit.xy[0] = xy


    def draw_settings(context, layout, tool):

        if context.object is not None:
            addon = context.window_manager.align_tool

            col = layout.column()

            row = col.row(align=True)
            row.operator("proaligntools.set_origin", icon="PIVOT_CURSOR")
            row.operator("proaligntools.delete_origin", text="", icon="X")

            if "custom_origin" in addon.CACHE:
                object_name = addon.CACHE["custom_origin"]["object"]
                col.label(text=f"Vertex in: {object_name}")

            row = col.row(align=True)
            row.operator("proaligntools.set_plane", icon="ORIENTATION_NORMAL")
            row.operator("proaligntools.delete_plane", text="", icon="X")
