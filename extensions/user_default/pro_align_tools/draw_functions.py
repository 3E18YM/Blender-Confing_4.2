from .common_imports import *

from .general_functions import get_matrix_midpoint_point
from .gpu_functions import (create_batch_shader, draw_batch_shader, draw_batch_shader_line,
                            draw_stipple_lines_batch_shader)
from .context_functions import (get_plane_type, get_plane_box_matrix,
                                get_plane_depth, get_rounded_rectangle, get_plane_individual_object,
                                get_point_draw_matrix, get_mouse_in_region, align_tool_selected)


# -- Main drawing functions for the 3D viewport --

# def highlight_objects(context, object_names):

#     addon = context.window_manager.align_tool
#     CACHE = addon.CACHE
#     triangles_highlight_COLOR = 1, 1, 1, 0.1 # 1, 0.6, 0.3, 0.05
#     edge_highlight_COLOR = 1, 1, 1, 0.6 # 1, 0.8, 0.5, 0.6

#     for name in object_names:
#         cache_object = CACHE["cached_objects"][name]
#         obj = context.scene.objects[name]

#         if cache_object["batch_shader"] is not None:

#             ob_batch, ob_shader, ob_draw_type = cache_object["batch_shader"]

#             if ob_draw_type == "TRIANGLES":
#                 color = triangles_highlight_COLOR
#             else:
#                 color = edge_highlight_COLOR

#             draw_batch_shader((ob_batch, ob_shader), color, obj.matrix_world)


# -- Draw plane bounds functions --

def draw_plane_box_matrix(context, batches_database, box_color):

    ui_scale = context.preferences.system.ui_scale
    plane_box_matrix = get_plane_box_matrix(context)

    if plane_box_matrix is not None:

        gpu.state.line_width_set(ui_scale)
        draw_stipple_lines_batch_shader(batches_database.bounds_batch, context, box_color,
                                        batches_database.line_pattern, int(8 * ui_scale), matrix=plane_box_matrix)
        gpu.state.line_width_set(1)

        for i in (1, 3, 4, 6, 8, 9, 10, 11, 13, 15, 16, 18):
            point = get_matrix_midpoint_point(plane_box_matrix, i)
            point_matrix = get_point_draw_matrix(context, point, 4 * ui_scale)
            draw_batch_shader(batches_database.point_batch, box_color, point_matrix)

def draw_plane_local_boxes(context, batches_database, box_color):

    addon = context.window_manager.align_tool
    CACHE = addon.CACHE
    ui_scale = context.preferences.system.ui_scale
    plane_type = get_plane_type(context)

    if plane_type in ("OBJECT_BOUNDS_PLANE",
                      "OBJECT_BOUNDS_ACTIVE"):

        draw_local = not addon.plane_use_local and not addon.plane_use_geometry

        if draw_local:

            individual_object = get_plane_individual_object(context)

            if individual_object is not None:
                cached_object = CACHE["cached_objects"][individual_object.name]

                if not individual_object.show_bounds:
                    box_matrix = cached_object["boxes"]["local"]
                    gpu.state.line_width_set(ui_scale)
                    draw_stipple_lines_batch_shader(batches_database.bounds_batch, context, box_color,
                                                    batches_database.line_pattern, int(6 * ui_scale), matrix=box_matrix)
                    gpu.state.line_width_set(1)

    elif plane_type == "OBJECT_BOUNDS_SELECTED":

        if addon.plane_use_local:
            draw_local = len(CACHE["selected_objects"]) > 1 and not addon.plane_use_geometry

        else:
            draw_local = not addon.plane_use_geometry

        if draw_local:

            for name in CACHE["selected_objects"]:
                obj = context.scene.objects[name]

                if not obj.show_bounds:
                    box_matrix = CACHE["cached_objects"][obj.name]["boxes"]["local"]
                    gpu.state.line_width_set(ui_scale)
                    draw_stipple_lines_batch_shader(batches_database.bounds_batch, context, box_color,
                                                    batches_database.line_pattern, int(6 * ui_scale), matrix=box_matrix)
                    gpu.state.line_width_set(1)


# -- Draw text functions --

def get_text_size(text, size):

    blf.size(0, size)

    return blf.dimensions(0, text)


def draw_text(text, size, color=(1, 1, 1, 1),
              h_alignment="CENTER",
              v_alignment="CENTER",
              frame=Vector((0, 0)),
              origin=Vector((0, 0))):

    if text != "":

        blf_kerning = 8  # This was the constant value of blf.KERNING_DEFAULT before being removed from the API

        blf.enable(0, blf.SHADOW)
        blf.enable(0, blf_kerning)
        blf.shadow(0, 5, *(0, 0, 0, 1))
        blf.color(0, *color)
        blf.size(0, size)
        text_size = blf.dimensions(0, text)
        text_offset = Vector(((0, -text_size[0] / 2, -text_size[0])[("LEFT", "CENTER", "RIGHT").index(h_alignment)],
                              (-text_size[1], -text_size[1] / 2, 0)[("TOP", "CENTER", "BOTTOM").index(v_alignment)]))
        frame_offset = Vector((frame[0] * (0, 0.5, 1)[("LEFT", "CENTER", "RIGHT").index(h_alignment)],
                               frame[1] * (1, 0.5, 0)[("TOP", "CENTER", "BOTTOM").index(v_alignment)]))
        blf.position(0, *(text_offset + frame_offset + origin), 0)
        blf.draw(0, text)

        blf.disable(0, blf.SHADOW)
        blf.disable(0, blf_kerning)

        return text_size


def get_text_lines(TextBlock, text_size, frame_width):
    blf.size(0, text_size)
    m_width = blf.dimensions(0, "abcdefghijklmnopqrstuvwxyz")[0] / 26 / 1.05 # correction factor
    line_width = floor(frame_width / m_width)

    lines = []
    while TextBlock != "":
        length = len(TextBlock)
        if length <= line_width:
            lines.append(TextBlock)
            break
        else:
            if "\n" in TextBlock:
                index = TextBlock.index("\n")
                TextBlock_start = TextBlock[:index].lstrip(" ")
                TextBlock_end = TextBlock[index+1:]
            else:
                TextBlock_start = TextBlock.lstrip(" ")
                TextBlock_end = ""

            if TextBlock_start == "":
                lines.append(TextBlock_start)
            else:
                while TextBlock_start != "":
                    start_length = len(TextBlock_start)
                    if start_length <= line_width:
                        lines.append(TextBlock_start)
                        break
                    else:
                        a = TextBlock_start[:line_width]
                        b = TextBlock_start[line_width:]
                        if " " in b:
                            space_index = b.index(" ")
                        else:
                            space_index = None
                        if space_index != 0:
                            if " " in a:
                                a_index = a.rindex(" ")
                                a = TextBlock_start[:a_index]
                                b = TextBlock_start[a_index:]
                        lines.append(a)
                        TextBlock_start = b.lstrip(" ")
            TextBlock = TextBlock_end.lstrip(" ")
    return lines


def get_colored_text_line(text_line):
    colored_list = []
    lines = text_line.split("\n")
    for line in lines:
        uncolored_line = line.split("$")
        if len(uncolored_line) > 1:
            for uncolored in uncolored_line:
                if uncolored:
                    if " " in uncolored:
                        space_index = uncolored.index(" ")
                    else:
                        space_index = None
                    if ":" in uncolored:
                        colon_index = uncolored.index(":")
                    else:
                        colon_index = None
                    if space_index is not None and colon_index is not None:
                        trim_index = min(space_index, colon_index)
                    elif colon_index is not None:
                        trim_index = colon_index
                    elif space_index is not None:
                        trim_index = space_index
                    colored_list.append((uncolored[:trim_index], (1, 0.7, 0.2, 1)))
                    colored_list.append((uncolored[trim_index:], None))
        else:
            colored_list.append((uncolored_line[0], None))
    return colored_list


def get_region_offsets_area3d(context, area, alignment_h: str = "LEFT", alignment_v: str = "TOP"):

    if not context.preferences.system.use_region_overlap:

        return 0, 0

    space = area.spaces[0]

    region_types_horizontal = {"TOOLS": "show_region_toolbar",
                               "UI": "show_region_ui"}
    region_types_vertical = {"HEADER": "show_region_header",
                             "TOOL_HEADER": "show_region_tool_header",
                             "ASSET_SHELF": "show_region_asset_shelf",
                             "ASSET_SHELF_HEADER": "show_region_asset_shelf"}

    regions_width = 0
    regions_height = 0

    for r in area.regions:

        if r.type in region_types_horizontal:

            if getattr(space, region_types_horizontal.get(r.type)):

                if r.alignment == alignment_h:

                    regions_width += r.width

            continue

        if r.type in region_types_vertical:

            if getattr(space, region_types_vertical.get(r.type)):

                if r.alignment == alignment_v:

                    regions_height += r.height

            continue

    return regions_width, regions_height


def draw_2D(context):

    addon = context.window_manager.align_tool
    ui_scale = context.preferences.system.ui_scale

    panels_drawable = False

    if align_tool_selected(context, mode="OBJECT"):

        try:

            getattr(addon.current_gizmo[0], "event")
            panels_drawable = True

        except ReferenceError:

            pass


    if panels_drawable:

        event = addon.current_gizmo[0].event
        batches = addon.batches[0]
        area = context.area
        region = context.region
        space = context.space_data

        mouse = Vector((event.mouse_x - region.x, event.mouse_y - region.y))
        offset = mouse - Vector((0, 100 * ui_scale))
        middlemouse_press = event.type == "MIDDLEMOUSE" and event.value == "PRESS"
        interline = Vector((0, 16 * ui_scale))
        padding = 5 * ui_scale
        panel_width = 40 * ui_scale
        panel_height = 18 * ui_scale

        orientation_text = ""

        if event.alt:

            orientation_text = addon.plane_orientation

            if addon.plane_orientation == "CUSTOM":

                sc = context.scene
                custom_orientation = sc.transform_orientation_slots[0].custom_orientation
                orientation_name = "None" if custom_orientation is None else custom_orientation.name
                orientation_text = f"{addon.plane_orientation} ({orientation_name})"


        if True in (event.ctrl and not middlemouse_press,
                    event.shift and not middlemouse_press,
                    event.alt):

            if event.alt:

                text_lines = ("Auto-Align", orientation_text)

            if event.ctrl:

                text_lines = ("Origin",)

            if event.shift:

                if event.alt:

                    text_lines = ("Plane", orientation_text)

                else:

                    text_lines = ("Plane",)


            if len(text_lines) == 2:

                line0_size = get_text_size(text=text_lines[0], size=int(11 * ui_scale))
                line1_size = get_text_size(text=text_lines[1], size=int(11 * ui_scale))
                panel_width = max(panel_width,
                                  line0_size[0] + (padding * 2),
                                  line1_size[0] + (padding * 2))
                panel_height += 12 * ui_scale


            update_batches = True

            if batches.mouse_panel_fill_batch:

                text_lines_batch = batches.mouse_panel_fill_batch[0][0]

                if text_lines is text_lines_batch:

                    update_batches = False

            if update_batches:

                rectangle = get_rounded_rectangle(panel_width, panel_height, padding=padding)
                rectangle = [p.to_3d() for p in rectangle]
                edge_indices = [(x, x + 1) for x in range(len(rectangle) - 1)]
                batches.mouse_panel_fill_batch[:] = [(text_lines, create_batch_shader("TRIANGLES", rectangle))]
                batches.mouse_panel_outline_batch[:] = [(text_lines, create_batch_shader("LINES", rectangle, edge_indices))]


            text_origin = offset - Vector((panel_width / 2, panel_height))
            origin_matrix = Matrix.Translation(text_origin.to_3d())# + Vector((0, 2, 0)))
            mouse_panel_fill_batch = batches.mouse_panel_fill_batch[0][1]
            mouse_panel_outline_batch = batches.mouse_panel_outline_batch[0][1]

            gpu_blend = gpu.state.blend_get()
            gpu.state.blend_set("ALPHA")
            draw_batch_shader(mouse_panel_fill_batch, (0, 0, 0, 0.2), origin_matrix)
            draw_batch_shader_line(mouse_panel_outline_batch, region, (1, 1, 1, 0.1),
                                   width=1.5 * ui_scale, matrix=origin_matrix)
            gpu.state.blend_set(gpu_blend)


            draw_text(text=text_lines[0], size=int(11 * ui_scale), color=(1, 1, 1, 0.5),
                      h_alignment="CENTER",
                      v_alignment="TOP",
                      frame=Vector((panel_width, panel_height)),
                      origin=text_origin + Vector((0, (-2 * ui_scale) if text_lines[0] == "Plane" else 0)))

            if len(text_lines) == 2:

                draw_text(text=text_lines[1], size=int(11 * ui_scale), color=(1, 0.3, 0.9, 0.8),
                          h_alignment="CENTER",
                          v_alignment="TOP",
                          frame=Vector((panel_width, panel_height)),
                          origin=text_origin - interline)


        # Draw shortcuts panel

        if not addon.show_shortcuts_help:
            panel_width = 120 * ui_scale
            panel_height = 18 * ui_scale
            text_lines = None
        else:
            TextBlock = """$• $Ctrl + $Alt + $A: Select the Align Tool
                        $• $Return / $Enter: Align Objects
                        $• $O: Toggle moving objects individually or as a group
                        $• $D: Toggle gizmos visibility

                        AUTO ALIGN:
                        $• $Left $Click on a gizmo: Automatically set some preset settings for the selected alignment
                        $Gestures $with $Left $Click:
                        $> $First $Click on a gizmo: Use the alignment of the currently selected gizmo
                        $> $Second $Click on a gizmo: Drag the selected gizmo without the need to hold the mouse pressed
                        Manual offset values can be introduced in the header
                        $> $Click $and $Drag on a gizmo: Drag the selected gizmo while holding the mouse pressed. Confirms the new gizmo position when releasing the mouse
                        $• $Alt + $Mousewheel $Up/Down: Scroll through plane orientations

                        DIRECTION:
                        $• $X / $Y / $Z: Select Axis
                        $• $L: Switch between Local and Global direction
                        $• $V: Switch between View and Global direction
                        $• $P: Switch between Perpendicular and Global direction

                        PROJECTION PLANE:
                        $• $Shift + $X / $Y / $Z: Select Plane Axis
                        $• $Shift + $Left $Click: Select Global projection plane
                        $• $Shift + $Alt + $Left $Click: Select Local or oriented projection plane
                        $• $Shift + $Alt + $Mousewheel $Up/Down: Scroll through plane orientations
                        $• $Shift + $P: Pick the Face of a Mesh Object as projection plane. Useful to align at objects outside the current selection
                        $• $Shift + $G: Use geometry for bounds

                        ORIGIN:
                        $• $Ctrl + $Left $Click: Select Global origin point
                        $• $Ctrl + $Alt + $Left $Click: Select Local origin point
                        $• $Ctrl + $G: Use geometry for bounds"""
            panel_width = 330 * ui_scale
            text_lines = get_text_lines(TextBlock, int(12 * ui_scale), panel_width)

            blf.size(0, int(12 * ui_scale))
            word_height = floor(blf.dimensions(0, "M")[1] * 1.8)
            textblock_offset_X = 20
            textblock_offset_Y = 16
            panel_height = (word_height * (len(text_lines) + 1)) + textblock_offset_Y

        padding = 6 * ui_scale
        rectangle = get_rounded_rectangle(panel_width, panel_height, padding=padding)
        regions_width, regions_height = get_region_offsets_area3d(context, area)
        total_panel_height = panel_height + (padding * 2)
        offset_width = regions_width
        offset_height = region.height - regions_height - total_panel_height
        text_info_height = 35 if space.overlay.show_text else 0
        stats_height = 100 if space.overlay.show_stats else 0
        ui_x_offset = 10 * ui_scale
        ui_y_offset = 12 * ui_scale if True in (space.overlay.show_text, space.overlay.show_stats) else 0
        ui_height = (text_info_height + stats_height) * ui_scale

        x_offset = offset_width + ui_x_offset + padding
        y_offset = offset_height - ui_x_offset - ui_height - ui_y_offset + padding
        offset = Vector((x_offset, y_offset))

        update_batches = True

        # This was useful to prevent the batches to be recreated in every draw call, but also prevented batches from updating in realtime when changing the UI Resolution Scale factor. Commenting by now

        # if batches.shortcuts_panel_fill_batch:

        #     batch_type = batches.shortcuts_panel_fill_batch[0][0]

        #     if batch_type == "collapsed" and not addon.show_shortcuts_help:

        #         update_batches = False

        #     if batch_type == "expanded" and addon.show_shortcuts_help:

        #         update_batches = False


        if update_batches:

            rectangle = [p.to_3d() for p in rectangle]
            edge_indices = [(x, x + 1) for x in range(len(rectangle) - 1)] + [((len(rectangle) - 1), 0)]
            batch_type = "expanded" if addon.show_shortcuts_help else "collapsed"
            batches.shortcuts_panel_fill_batch[:] = [(batch_type, create_batch_shader("TRIANGLES", rectangle))]
            batches.shortcuts_panel_outline_batch[:] = [(batch_type, create_batch_shader("LINES", rectangle, edge_indices))]


        mouse = Vector((event.mouse_x - region.x, event.mouse_y - region.y)) - offset + Vector((padding, padding))
        mouse_in_region = get_mouse_in_region(region, event)
        mouse_x_in_button = mouse[0] > 0 and mouse[0] < panel_width + (padding * 2)
        mouse_y_in_button = mouse[1] > 0 and mouse[1] < panel_height + (padding * 2)

        if mouse_in_region and mouse_x_in_button and mouse_y_in_button:

            mouse_in_shortcuts_button = True

            fill_color = 0, 0, 0, 0.4
            border_color = 0.5, 1, 0.5, 0.8

        else:

            mouse_in_shortcuts_button = False

            fill_color = 0, 0, 0, 0.2 if addon.show_shortcuts_help else 0.05
            border_color = 1, 1, 1, 0.4 if addon.show_shortcuts_help else 0.2


        add_to_region_dicts = True

        for region_dict in addon.region_dicts:

            if region_dict["region"] == region:

                add_to_region_dicts = False
                region_dict["mouse_in_shortcuts_button"] = mouse_in_shortcuts_button

        if add_to_region_dicts:

            addon.region_dicts.append({"region": region, "mouse_in_shortcuts_button": mouse_in_shortcuts_button})


        # text_origin = offset - Vector((panel_width / 2, panel_height))
        origin_matrix = Matrix.Translation(offset.to_3d())
        shortcuts_panel_fill_batch = batches.shortcuts_panel_fill_batch[0][1]
        shortcuts_panel_outline_batch = batches.shortcuts_panel_outline_batch[0][1]

        gpu_blend = gpu.state.blend_get()
        gpu.state.blend_set("ALPHA")
        draw_batch_shader(shortcuts_panel_fill_batch, fill_color, origin_matrix)
        draw_batch_shader_line(shortcuts_panel_outline_batch, region, border_color,
                               width=1.5 * ui_scale, matrix=origin_matrix)
        gpu.state.blend_set(gpu_blend)


        if True in (mouse_in_shortcuts_button, addon.show_shortcuts_help):

            shortcuts_color = 0.8, 1, 0.8, 0.8

        else:

            shortcuts_color = 1, 1, 1, 0.6

        draw_text(text="Align Tool Shortcuts", size=int(12 * ui_scale), color=shortcuts_color,
                  h_alignment="CENTER",
                  v_alignment="TOP",
                  frame=Vector((panel_width, panel_height)),
                  origin=offset)


        if addon.show_shortcuts_help and text_lines:
            for i, line in enumerate(reversed(text_lines)):
                if line != "":
                    word_offset = 0
                    for fragment in get_colored_text_line(line):
                        text, color = fragment
                        if not color:
                            color = (1,1,1,1)
                        text_size = draw_text(text=text, size=int(12 * ui_scale), color=color,
                                              h_alignment="LEFT",
                                              v_alignment="BOTTOM",
                                              frame=Vector((panel_width - textblock_offset_X, panel_height)),
                                              origin=offset + Vector(((textblock_offset_X / 4) + word_offset, (word_height * i) + (textblock_offset_Y / 2))))
                        if text_size:
                            word_offset += text_size[0]
