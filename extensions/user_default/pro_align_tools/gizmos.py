from .common_imports import *

from .general_functions import offset_by_normals
from .widgets import star_box, star, grid_box, grid_point, midpoint_box, midpoint_star
from .cache_system import CACHE_update, CACHE_depsgraph_check, CACHE_view_update, CACHE_undo_check, CACHE_clear
from .cache_functions import get_object_rotation_matrix
from .gpu_functions import (create_batch_shader, draw_batch_shader,
                            draw_batch_shader_line, draw_stipple_lines_batch_shader)
from .draw_functions import (draw_2D, draw_plane_box_matrix, draw_plane_local_boxes)
from .context_functions import (get_mouse_in_region, get_plane_draw_matrix, get_arrow_draw_matrices,
                                get_point_draw_matrix, get_current_orientation_matrix, align_tool_selected, get_simple_rectangle, get_rounded_rectangle)


# -- User Interface Gizmos --

class ALIGNTOOL_GT_custom_gizmo(Gizmo):

    bl_idname = "ALIGNTOOL_GT_custom_gizmo"

    def create_batches(self):

        addon = bpy.context.window_manager.align_tool
        batches = addon.batches[0]

        # generic point and line
        point_edges = 24
        angle = (pi * 2) / point_edges
        halfpi = pi / 2
        point_geometry = [(cos((angle * edge) - halfpi), sin((angle * edge) - halfpi), 0) for edge in range(point_edges)]
        if not hasattr(batches, "point_batch"):
            batches.point_batch = create_batch_shader("TRIANGLES", point_geometry)
        if not hasattr(batches, "square_batch"):
            batches.square_batch = create_batch_shader("TRIANGLES", ((-1, -1, 0), (1, -1, 0), (1, 1, 0), (-1, 1, 0)))
        if not hasattr(batches, "solid_line_batch"):
            batches.solid_line_batch = create_batch_shader("LINES", ((0, 0, 0), (1, 0, 0)), ((0, 1),))

        # stipple line and arrow
        if not hasattr(batches, "line_pattern"):
            batches.line_pattern = int(f"0b{'1010101010101010'}", 2)
        if not hasattr(batches, "line_pattern_inverted"):
            batches.line_pattern_inverted = int(f"0b{'0101010101010101'}", 2)
        if not hasattr(batches, "stipple_line_batch"):
            batches.stipple_line_batch = create_batch_shader("LINES", ((0, 0, 0), (1, 0, 0)), ((0, 1),), stipple_lines=True)
        if not hasattr(batches, "arrow_batch"):
            batches.arrow_batch = create_batch_shader("TRIANGLES", ((0, 0, 0), (1, radians(-10), 0), (1, radians(10), 0)))

        # projection plane
        simple_rectangle = get_simple_rectangle(1, 1)
        simple_rectangle_3D = [p.to_3d() for p in simple_rectangle]
        rounded_rectangle = get_rounded_rectangle(1, 1, padding=0.0001, inner=True)
        rounded_rectangle_3D = [p.to_3d() for p in rounded_rectangle]
        rounded_rectangle_indices = ([(x, x + 1) for x in range(len(rounded_rectangle_3D) - 1)]
                                   + [((len(rounded_rectangle_3D) - 1), 0)])
        if not hasattr(batches, "plane_outline_batch"):
            batches.plane_outline_batch = create_batch_shader("LINES", rounded_rectangle_3D, rounded_rectangle_indices)
        if not hasattr(batches, "plane_fill_batch"):
            batches.plane_fill_batch = create_batch_shader("TRIANGLES", simple_rectangle_3D)
        # plane_geometry = (0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)
        # plane_indices = (0, 1), (1, 2), (2, 3), (0, 3)
        # if not hasattr(batches, "plane_outline_batch"):
        #     batches.plane_outline_batch = create_batch_shader("LINES", plane_geometry, plane_indices)
        # if not hasattr(batches, "plane_fill_batch"):
        #     batches.plane_fill_batch = create_batch_shader("TRIANGLES", plane_geometry)

        # bound box
        bounds = ((0, 0, 0), (0, 0, 1), (0, 1, 1), (0, 1, 0), (1, 0, 0), (1, 0, 1), (1, 1, 1), (1, 1, 0))
        bounds_indices = ((0, 1), (1, 2), (2, 3), (3, 0),
                          (4, 5), (5, 6), (6, 7), (7, 4),
                          (0, 4), (1, 5), (2, 6), (3, 7))
        if not hasattr(batches, "bounds_batch"):
            batches.bounds_batch = create_batch_shader("LINES", bounds, bounds_indices, stipple_lines=True)

        # axes arrow and plane
        axes_arrow_geometry = (1.05, 0, 0), (0.75, 0.075, -0.075), (0.75, 0.075, 0.075), (0.75, -0.075, 0.075), (0.75, -0.075, -0.075)
        axes_arrow_fill_indices = (0, 1, 2), (0, 2, 3), (0, 3, 4), (0, 4, 1), (1, 3, 2), (3, 1, 4)
        axes_arrow_geometry_offset = offset_by_normals(axes_arrow_geometry, axes_arrow_fill_indices, 0.04)
        if not hasattr(batches, "axes_arrow_outline_batch"):
            batches.axes_arrow_outline_batch = create_batch_shader("TRIANGLES", axes_arrow_geometry_offset, axes_arrow_fill_indices)
        if not hasattr(batches, "axes_arrow_fill_batch"):
            batches.axes_arrow_fill_batch = create_batch_shader("TRIANGLES", axes_arrow_geometry, axes_arrow_fill_indices)

        axes_plane_geometry = (0, 0.15, -0.15), (0, 0.15, 0.15), (0, -0.15, 0.15), (0, -0.15, -0.15)
        if not hasattr(batches, "axes_plane_outline_batch"):
            batches.axes_plane_outline_batch = create_batch_shader("TRIANGLES", [Vector(v)*1.5 for v in axes_plane_geometry])
        if not hasattr(batches, "axes_plane_fill_batch"):
            batches.axes_plane_fill_batch = create_batch_shader("TRIANGLES", axes_plane_geometry)


    def setup(self):

        bpy.context.window_manager.align_tool.current_gizmo[:] = [self]
        bpy.ops.proaligntools.add_event_to_current_gizmo("INVOKE_DEFAULT")

        self.create_batches()

        # # generic point and line
        # point_edges = 16
        # angle = (pi * 2) / point_edges
        # point_geometry = [(cos(angle * edge), sin(angle * edge), 0) for edge in range(point_edges)]
        # self.point_batch = create_batch_shader("TRIANGLES", point_geometry)
        # self.square_batch = create_batch_shader("TRIANGLES", ((-1, -1, 0), (1, -1, 0), (1, 1, 0), (-1, 1, 0)))
        # self.solid_line_batch = create_batch_shader("LINES", ((0, 0, 0), (1, 0, 0)), ((0, 1),))

        # # stipple line and arrow
        # self.line_pattern = int(f"0b{'1010101010101010'}", 2)
        # self.line_pattern_inverted = int(f"0b{'0101010101010101'}", 2)
        # self.stipple_line_batch = create_batch_shader("LINES", ((0, 0, 0), (1, 0, 0)), ((0, 1),), stipple_lines=True)
        # self.arrow_batch = create_batch_shader("TRIANGLES", ((0, 0, 0), (1, radians(-10), 0), (1, radians(10), 0)))

        # # projection plane
        # plane_geometry = (0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)
        # plane_indices = (0, 1), (1, 2), (2, 3), (0, 3)
        # self.plane_outline_batch = create_batch_shader("LINES", plane_geometry, plane_indices)
        # self.plane_fill_batch = create_batch_shader("TRIANGLES", plane_geometry)

        # # bound box
        # bounds = ((0, 0, 0), (0, 0, 1), (0, 1, 1), (0, 1, 0), (1, 0, 0), (1, 0, 1), (1, 1, 1), (1, 1, 0))
        # bounds_indices = ((0, 1), (1, 2), (2, 3), (3, 0),
        #                   (4, 5), (5, 6), (6, 7), (7, 4),
        #                   (0, 4), (1, 5), (2, 6), (3, 7))
        # self.bounds_batch = create_batch_shader("LINES", bounds, bounds_indices, stipple_lines=True)

        # # axes arrow and plane
        # axes_arrow_geometry = (1.05, 0, 0), (0.75, 0.075, -0.075), (0.75, 0.075, 0.075), (0.75, -0.075, 0.075), (0.75, -0.075, -0.075)
        # axes_arrow_fill_indices = (0, 1, 2), (0, 2, 3), (0, 3, 4), (0, 4, 1), (1, 3, 2), (3, 1, 4)
        # axes_arrow_geometry_offset = offset_by_normals(axes_arrow_geometry, axes_arrow_fill_indices, 0.025)
        # self.axes_arrow_outline_batch = create_batch_shader("TRIANGLES", axes_arrow_geometry_offset, axes_arrow_fill_indices)
        # self.axes_arrow_fill_batch = create_batch_shader("TRIANGLES", axes_arrow_geometry, axes_arrow_fill_indices)

        # axes_plane_geometry = (0, 0.15, -0.15), (0, 0.15, 0.15), (0, -0.15, 0.15), (0, -0.15, -0.15)
        # self.axes_plane_outline_batch = create_batch_shader("TRIANGLES", [Vector(v)*1.3 for v in axes_plane_geometry])
        # self.axes_plane_fill_batch = create_batch_shader("TRIANGLES", axes_plane_geometry)

        # auto-align star widgets
        self.world_star = star(None, "WORLD", Matrix(), 0)
        self.cursor_star = star(None, "CURSOR", Matrix(), 0)
        self.active_object_star_box = star_box("ACTIVE")
        self.selected_objects_star_box = star_box("SELECTED")

        # origin selection widgets
        self.world_point = grid_point("WORLD")
        self.cursor_point = grid_point("CURSOR")
        self.location_point = grid_point("OBJECT_LOCATION")
        self.active_object_grid_box = grid_box("OBJECT_BOUNDS")
        self.selection_grid_box = grid_box("SELECTION")

        # plane selection widgets
        self.world_midpoint_star = midpoint_star("WORLD")
        self.cursor_midpoint_star = midpoint_star("CURSOR")
        self.object_midpoint_star = midpoint_star("OBJECT_LOCATION")
        self.object_midpoint_box = midpoint_box("OBJECT_BOUNDS")
        self.selection_midpoint_box = midpoint_box("SELECTION")
        self.plane_object_midpoint_star = midpoint_star("OBJECT_LOCATION")
        self.plane_object_midpoint_box = midpoint_box("OBJECT_BOUNDS")


    def draw(self, context):

        event = self.event
        region = context.region
        addon = context.window_manager.align_tool
        batches = addon.batches[0]
        ui_scale = context.preferences.system.ui_scale

        CACHE = addon.CACHE
        mouse_in_region = get_mouse_in_region(region, event)
        is_perpendicular = CACHE["plane"] is not None and addon.direction_custom_orientation == "PERPENDICULAR"

        triangles_regular_COLOR = 1, 1, 1, 0.2
        triangles_error_COLOR = 1, 0, 0, 0.1
        edge_regular_COLOR = 1, 1, 1, 0.5
        edge_error_COLOR = 1, 0, 0, 0.5
        bounds_local_COLOR = 1, 0.3, 1, 1
        bounds_world_COLOR = 0, 0, 0, 0.7
        bounds_projected_COLOR = 1, 1, 1, 0.4
        bounds_error_COLOR = 1, 0, 0, 1
        if addon.drag_star:
            plane_axis_index = addon.drag_star[0].axes[0].index
        else:
            plane_axis_index = ("X", "Y", "Z").index(addon.plane_axis)
        plane_fill_COLOR = ((1, 0.4, 0.4, 0.2),
                            (0.4, 1, 0.4, 0.2),
                            (0.4, 0.4, 1, 0.2))[plane_axis_index]
        plane_outline_COLOR = ((1, 0.6, 0.6, 0.8),
                               (0.6, 1, 0.6, 0.8),
                               (0.6, 0.6, 1, 0.8))[plane_axis_index]
        plane_axis_COLOR = ((1, 0.6, 0.6, 1),
                            (0.6, 1, 0.6, 1),
                            (0.6, 0.6, 1, 1))[plane_axis_index]
        origin_COLOR = ((1, 0.5, 0.5, 1),
                        (0.5, 1, 0.5, 1),
                        (0.6, 0.6, 1, 1))[plane_axis_index if is_perpendicular else ("X", "Y", "Z").index(addon.direction_axis)]

        if mouse_in_region and "VIEW" in (addon.plane_orientation, addon.direction_custom_orientation):
            CACHE_view_update(context)

        gpu_blend = gpu.state.blend_get()
        gpu.state.blend_set("ALPHA")

        if context.mode == "EDIT_MESH":
            # Draw custom origin
            if "custom_origin" in CACHE:
                origin = CACHE["custom_origin"]
                origin["point"].update(context, event, Matrix.Translation(origin["co"]))
                origin["point"].draw(context, event, batches, is_selected=False)

            # Draw custom drag star widget
            middlemouse_press = event.type == "MIDDLEMOUSE" and event.value == "PRESS"

            if mouse_in_region and not middlemouse_press:

                if addon.drag_star:

                    drag_star = addon.drag_star[0]
                    drag_star.update(context, event)
                    normal_axis = drag_star.axes[0]

                    if addon.drag_star_shadow:
                        addon.drag_star_shadow[0].axes[0].draw(context, batches, draw_arrow=True, gray=True)

                    normal_axis.draw(context, batches, draw_arrow=True)

                    if normal_axis.cursor_close:

                        addon.props.clear()

                        for key in normal_axis.props.keys():
                            addon.props[key] = normal_axis.props[key]

                        addon.nearest_axis[:] = [normal_axis]

                    else:
                        addon.props.clear()
                        addon.nearest_axis[:] = []

                else:
                    addon.props.clear()
                    addon.nearest_axis[:] = []

            # Draw projection Plane
            if "plane" in CACHE:
                if CACHE["plane"] is not None:
                    plane_draw_matrix = get_plane_draw_matrix(context, CACHE["plane"], [])

                    gpu_depth_test = gpu.state.depth_test_get()
                    gpu.state.depth_test_set("LESS")
                    gpu.state.depth_mask_set(False)
                    draw_batch_shader(batches.plane_fill_batch, plane_fill_COLOR, plane_draw_matrix, offset=True)
                    gpu.state.depth_test_set(gpu_depth_test)
                    gpu.state.depth_mask_set(True)

                    draw_batch_shader_line(batches.plane_outline_batch, region, plane_outline_COLOR,
                                           width=2 * ui_scale, matrix=plane_draw_matrix)


        elif context.mode == "OBJECT":

            gpu_depth_test = gpu.state.depth_test_get()
            gpu.state.depth_test_set("LESS")
            gpu.state.face_culling_set("BACK")
            gpu.state.depth_mask_set(False)

            # Draw object silhouettes and bounding boxes
            for projection in CACHE["projection_lines"]:
                start, end, object_names = projection

                if end is not None:

                    translation = end - start

                    if isclose(translation.length, 0, abs_tol=0.00001):

                        translation = None

                    else:

                        translation = Matrix.Translation(translation)

                else:

                    translation = None


                for name in object_names:

                    ob = context.scene.objects[name]
                    cache_object = CACHE["cached_objects"][name]

                    # Draw object silhouette
                    if cache_object["batch_shader"] is not None:

                        ob_batch, ob_shader, ob_draw_type = cache_object["batch_shader"]

                        if end is None:
                            matrix = ob.matrix_world
                            color = triangles_error_COLOR if ob_draw_type == "TRIANGLES" else edge_error_COLOR
                        elif translation:
                            matrix = translation @ ob.matrix_world
                            color = triangles_regular_COLOR if ob_draw_type == "TRIANGLES" else edge_regular_COLOR
                        else:
                            matrix = None

                        if matrix:
                            draw_batch_shader((ob_batch, ob_shader), color, matrix, offset=True)

                    # Draw object bounding boxes
                    if addon.origin_show_bounds:
                        if addon.origin_target == "OBJECTS" and addon.origin_type == "BOUNDS":
                            if not addon.origin_use_local and not addon.origin_all_selected:

                                box_matrix = cache_object["boxes"]["perpendicular" if addon.origin_use_geometry else "world"]
                                box_color = bounds_error_COLOR if end is None else bounds_world_COLOR

                                if box_matrix is not None:

                                    if box_matrix.to_scale() != Vector((0, 0, 0)):
                                        gpu.state.line_width_set(ui_scale)
                                        draw_stipple_lines_batch_shader(batches.bounds_batch, context, box_color,
                                                                        batches.line_pattern, int(6 * ui_scale), matrix=box_matrix)
                                        gpu.state.line_width_set(1)

                                        if end is not None:
                                            if translation:
                                                gpu.state.line_width_set(ui_scale)
                                                draw_stipple_lines_batch_shader(batches.bounds_batch, context,
                                                                                bounds_projected_COLOR,
                                                                                batches.line_pattern_inverted,
                                                                                int(6 * ui_scale),
                                                                                matrix=translation @ box_matrix)
                                                gpu.state.line_width_set(1)

                            if True in (addon.origin_use_local, not addon.origin_use_local and not addon.origin_use_geometry):
                                if not ob.show_bounds:
                                    box_matrix = cache_object["boxes"]["local"]
                                    box_color = bounds_error_COLOR if end is None else bounds_local_COLOR

                                    if box_matrix is not None:

                                        if box_matrix.to_scale() != Vector((0, 0, 0)):
                                            gpu.state.line_width_set(ui_scale)
                                            draw_stipple_lines_batch_shader(batches.bounds_batch, context, box_color,
                                                                            batches.line_pattern, int(6 * ui_scale), matrix=box_matrix)
                                            gpu.state.line_width_set(1)

                                            if end is not None:
                                                if translation:
                                                    gpu.state.line_width_set(ui_scale)
                                                    draw_stipple_lines_batch_shader(batches.bounds_batch, context,
                                                                                    bounds_projected_COLOR,
                                                                                    batches.line_pattern_inverted,
                                                                                    int(6 * ui_scale),
                                                                                    matrix=translation @ box_matrix)
                                                    gpu.state.line_width_set(1)

                # Draw selection bounding box if used
                if addon.origin_show_bounds:

                    if addon.origin_target == "OBJECTS" and addon.origin_type == "BOUNDS":

                        if addon.origin_all_selected and not addon.origin_use_local:

                            box_type = "perpendicular" if addon.origin_use_geometry else "world"
                            box_matrix = CACHE["selection_bounds"][box_type]
                            box_color = bounds_error_COLOR if end is None else bounds_world_COLOR

                            if box_matrix is not None:

                                if box_matrix.to_scale() != Vector((0, 0, 0)):
                                    gpu.state.line_width_set(ui_scale)
                                    draw_stipple_lines_batch_shader(batches.bounds_batch, context, box_color,
                                                                    batches.line_pattern, int(6 * ui_scale), matrix=box_matrix)
                                    gpu.state.line_width_set(1)

                                    if end is not None:
                                        if translation:
                                            gpu.state.line_width_set(ui_scale)
                                            draw_stipple_lines_batch_shader(batches.bounds_batch, context,
                                                                            bounds_projected_COLOR,
                                                                            batches.line_pattern_inverted,
                                                                            int(6 * ui_scale),
                                                                            matrix=translation @ box_matrix)
                                            gpu.state.line_width_set(1)

            gpu.state.depth_test_set(gpu_depth_test)
            gpu.state.face_culling_set("NONE")
            gpu.state.depth_mask_set(True)


            for projection in CACHE["projection_lines"]:
                start, end, object_names = projection

                # Draw origin point
                point_size = (8 if end is None else 5) * ui_scale
                point_matrix = get_point_draw_matrix(context, start, point_size)
                point_color = (1, 0, 0, 0.8) if end is None else origin_COLOR
                draw_batch_shader(batches.point_batch, color=point_color, matrix=point_matrix)

                # Draw arrow
                if end is not None:
                    line_matrix, arrow_matrix = get_arrow_draw_matrices(context, start, end)
                    if line_matrix is not None:
                        gpu.state.line_width_set(1.5 * ui_scale)
                        draw_stipple_lines_batch_shader(batches.stipple_line_batch, context, origin_COLOR, batches.line_pattern, int(12 * ui_scale), matrix=line_matrix)
                        gpu.state.line_width_set(1)
                    if arrow_matrix is not None:
                        draw_batch_shader(batches.arrow_batch, origin_COLOR, arrow_matrix)

            # Draw projection Plane
            if "plane" in CACHE:
                if CACHE["plane"] is not None:
                    plane_draw_matrix = get_plane_draw_matrix(context, CACHE["plane"], CACHE["projected_points"])

                    gpu_depth_test = gpu.state.depth_test_get()
                    gpu.state.depth_test_set("LESS")
                    gpu.state.depth_mask_set(False)
                    draw_batch_shader(batches.plane_fill_batch, plane_fill_COLOR, plane_draw_matrix, offset=True)
                    gpu.state.depth_test_set(gpu_depth_test)
                    gpu.state.depth_mask_set(True)

                    draw_batch_shader_line(batches.plane_outline_batch, region, plane_outline_COLOR,
                                           width=2 * ui_scale, matrix=plane_draw_matrix)


            # Draw plane bounds
            if addon.plane_show_bounds:
                draw_plane_box_matrix(context, batches, plane_axis_COLOR)
                draw_plane_local_boxes(context, batches, bounds_local_COLOR)

            # Draw custom origin
            if "custom_origin" in CACHE:
                origin = CACHE["custom_origin"]
                origin["point"].update(context, event, Matrix.Translation(origin["co"]))
                origin["point"].draw(context, event, batches, is_selected=False)

            # Process and draw all UI widgets
            if mouse_in_region:
                leftmouse_press = event.type == "LEFTMOUSE" and event.value == "PRESS"
                middlemouse_press = event.type == "MIDDLEMOUSE" and event.value == "PRESS"
                no_active_action = not addon.drag and not addon.running_modal
                is_local = event.alt

                if event.ctrl and no_active_action and not middlemouse_press:

                    active_object = context.object is not None
                    active_object_in_cache = active_object and context.object.name in CACHE["cached_objects"]

                    if active_object_in_cache and context.object.visible_get():
                        boxes_active_object = CACHE["cached_objects"][context.object.name]["boxes"]
                        bounds_type = ("local" if is_local
                                       else ("perpendicular" if addon.origin_use_geometry else "world"))
                        BOX_active_object = boxes_active_object[bounds_type]
                    else:
                        BOX_active_object = None

                    if len(CACHE["selected_objects"]) > 1:
                        bounds_type = "perpendicular" if addon.origin_use_geometry else "world"
                        BOX_selected = CACHE["selection_bounds"][bounds_type]
                    else:
                        BOX_selected = None

                    points = [self.world_point, self.cursor_point]
                    boxes = []

                    self.world_point.update(context, event, Matrix())
                    self.world_point.draw(context, event, batches, is_selected=False)

                    self.cursor_point.update(context, event, context.scene.cursor.matrix)
                    self.cursor_point.draw(context, event, batches, is_selected=False)

                    if "custom_origin" in CACHE:
                        origin = CACHE["custom_origin"]
                        origin["point"].update(context, event, Matrix.Translation(origin["co"]))
                        # origin["point"].draw(context, event, self, is_selected=False)
                        points.append(origin["point"])

                    if BOX_selected is not None and not is_local:
                        self.selection_grid_box.update(context, event, BOX_selected)
                        self.selection_grid_box.draw(context, event, batches)
                        boxes.append(self.selection_grid_box)

                    if BOX_active_object is not None:
                        self.location_point.update(context, event, context.object.matrix_world)
                        self.location_point.draw(context, event, batches, is_selected=False)
                        points.append(self.location_point)

                        self.active_object_grid_box.update(context, event, BOX_active_object)
                        self.active_object_grid_box.draw(context, event, batches)
                        boxes.append(self.active_object_grid_box)

                    near_points = [point for box in boxes for point in box.points if point.cursor_close is True]
                    near_points += [point for point in points if point.cursor_close is True]
                    nearest_point = None
                    if near_points:
                        nearest_point = min(near_points, key=lambda point: point.cursor_distance)

                    if nearest_point is not None:
                        nearest_point.draw(context, event, batches)
                        addon.props.clear()

                        for key in nearest_point.props.keys():
                            addon.props[key] = nearest_point.props[key]

                    else:
                        addon.props.clear()

                else:
                    active_object = context.object is not None
                    active_object_in_cache = active_object and context.object.name in CACHE["cached_objects"]

                    if active_object_in_cache and context.object.visible_get():
                        boxes_active_object = CACHE["cached_objects"][context.object.name]["boxes"]
                        bounds_type = ("local" if is_local
                                       else ("world_geometry" if addon.plane_use_geometry else "world"))
                        BOX_active_object = boxes_active_object[bounds_type]
                    else:
                        BOX_active_object = None

                    # if not is_local and len(CACHE["selected_objects"]) > 1:
                    #     bounds_type = "geometry" if addon.plane_use_geometry else "world"
                    #     BOX_selected = CACHE["selection_bounds"][bounds_type]
                    # else:
                    #     BOX_selected = None

                    if len(CACHE["selected_objects"]) > 1:

                        if is_local:

                            if addon.plane_use_geometry:
                                bounds_type = "local_geometry"
                            else:
                                bounds_type = "local"

                        else:

                            if addon.plane_use_geometry:
                                bounds_type = "geometry"
                            else:
                                bounds_type = "world"

                        BOX_selected = CACHE["selection_bounds"][bounds_type]

                    else:
                        BOX_selected = None

                    if event.shift and no_active_action and not middlemouse_press:

                        boxes = [self.world_midpoint_star, self.cursor_midpoint_star]

                        world_matrix = Matrix()
                        if is_local:
                            world_matrix = get_current_orientation_matrix(context, world_matrix)

                        self.world_midpoint_star.update(context, event, world_matrix)
                        self.world_midpoint_star.draw(context, batches)

                        cursor_matrix = Matrix.Translation(context.scene.cursor.location)
                        if is_local:
                            cursor_matrix = cursor_matrix @ get_current_orientation_matrix(context, context.scene.cursor.matrix)

                        self.cursor_midpoint_star.update(context, event, cursor_matrix)
                        self.cursor_midpoint_star.draw(context, batches)

                        if BOX_selected is not None:
                            self.selection_midpoint_box.update(context, event, BOX_selected)
                            self.selection_midpoint_box.draw(context, event, batches)
                            boxes.append(self.selection_midpoint_box)

                        if BOX_active_object is not None:
                            star_matrix = Matrix.Translation(context.object.matrix_world.to_translation())

                            if is_local:
                                star_matrix = star_matrix @ get_current_orientation_matrix(context, context.object.matrix_world)

                            self.object_midpoint_star.update(context, event, star_matrix, context.object.name)
                            self.object_midpoint_star.draw(context, batches)
                            boxes.append(self.object_midpoint_star)

                            self.object_midpoint_box.update(context, event, BOX_active_object, context.object.name)
                            self.object_midpoint_box.draw(context, event, batches)
                            boxes.append(self.object_midpoint_box)

                        if addon.plane_object:

                            active_is_not_plane = True

                            if active_object:
                                if context.object.name == addon.plane_object:
                                    active_is_not_plane = False

                            if active_is_not_plane:

                                if addon.plane_object in CACHE["cached_objects"]:
                                    boxes_plane_object = CACHE["cached_objects"][addon.plane_object]["boxes"]
                                    bounds_type = "local" if is_local else ("world_geometry" if addon.plane_use_geometry else "world")
                                    BOX_plane_object = boxes_plane_object[bounds_type]
                                else:
                                    BOX_plane_object = None

                                if BOX_plane_object is not None:
                                    plane_object_matrix = context.scene.objects[addon.plane_object].matrix_world

                                    star_matrix = Matrix.Translation(plane_object_matrix.to_translation())
                                    if is_local:
                                        star_matrix = star_matrix @ get_current_orientation_matrix(context, plane_object_matrix)

                                    self.plane_object_midpoint_star.update(context, event, star_matrix, addon.plane_object)
                                    self.plane_object_midpoint_star.draw(context, batches)
                                    boxes.append(self.plane_object_midpoint_star)

                                    self.plane_object_midpoint_box.update(context, event, BOX_plane_object, addon.plane_object)
                                    self.plane_object_midpoint_box.draw(context, event, batches)
                                    boxes.append(self.plane_object_midpoint_box)

                        near_edges = [edge for box in boxes for edge in box.midpoint_edges if edge.cursor_close is True]
                        nearest_edge = None
                        if near_edges:
                            nearest_edge_by_line_distance = min(near_edges, key=lambda edge: edge.cursor_distance)
                            nearest_edge_by_point_distance = min(near_edges, key=lambda edge: edge.point2_distance)

                            if isclose(nearest_edge_by_line_distance.cursor_distance, nearest_edge_by_point_distance.cursor_distance, abs_tol=0.1):
                                nearest_edge = nearest_edge_by_point_distance
                            else:
                                nearest_edge = nearest_edge_by_line_distance

                        if nearest_edge is not None:
                            nearest_edge.draw(context, event, batches)
                            addon.props.clear()

                            for key in nearest_edge.props.keys():
                                addon.props[key] = nearest_edge.props[key]

                        else:
                            addon.props.clear()

                    elif not event.ctrl and not event.shift:
                        # Draw auto-align axis widgets
                        star_lists = [[self.world_star], [self.cursor_star]]

                        world_matrix = Matrix()
                        if is_local:
                            world_matrix = get_current_orientation_matrix(context, world_matrix)

                        self.world_star.apply_matrix_drag(context, event, world_matrix)

                        cursor_matrix = Matrix.Translation(context.scene.cursor.location)
                        if is_local:
                            cursor_matrix = cursor_matrix @ get_current_orientation_matrix(context, context.scene.cursor.matrix)

                        self.cursor_star.apply_matrix_drag(context, event, cursor_matrix)

                        # self.world_midpoint_star.draw(context, batches)

                        if BOX_active_object is not None:
                            fallback_matrix = get_object_rotation_matrix(context.object) if active_object and is_local else Matrix()
                            self.active_object_star_box.update(context, event, BOX_active_object, fallback_matrix)
                            star_lists.append(self.active_object_star_box.stars)

                        if BOX_selected is not None:
                            self.selected_objects_star_box.update(context, event, BOX_selected)
                            star_lists.append(self.selected_objects_star_box.stars)

                        if addon.drag_star:
                            addon.drag_star[0].update(context, event)
                            star_lists.append([addon.drag_star[0]])

                        nearest_axis = None
                        if not middlemouse_press:
                            near_stars = [star for star_list in star_lists for star in star_list if star.cursor_close is True]

                            if near_stars:
                                axes_list = [axis for star in near_stars for axis in star.axes if axis.cursor_close is True]

                                if axes_list:
                                    nearest_axis = min(axes_list, key=lambda axis: axis.cursor_distance)


                        only_points = True in (not no_active_action, leftmouse_press)

                        if nearest_axis is None:

                            self.world_star.draw(context, batches, (1, 1, 1, 0.8))
                            self.cursor_star.draw(context, batches, (1, 1, 1, 0.8))

                        else:

                            if nearest_axis.star is self.world_star:

                                for axis in self.world_star.axes:

                                    if axis is nearest_axis:
                                        axis.draw(context, batches, draw_arrow=True)
                                    else:
                                        axis.draw(context, batches)

                            else:

                                self.world_star.draw(context, batches, (1, 1, 1, 0.8))


                            if nearest_axis.star is self.cursor_star:

                                for axis in self.cursor_star.axes:

                                    if axis is nearest_axis:
                                        axis.draw(context, batches, draw_arrow=True)
                                    else:
                                        axis.draw(context, batches)

                            else:

                                self.cursor_star.draw(context, batches, (1, 1, 1, 0.8))


                        if BOX_active_object is not None and no_active_action:
                            self.active_object_star_box.draw(context, event, batches, nearest_axis, only_points=only_points)

                        if BOX_selected is not None and no_active_action:
                            self.selected_objects_star_box.draw(context, event, batches, nearest_axis, only_points=only_points)

                        if addon.drag_star_shadow:
                            addon.drag_star_shadow[0].axes[0].draw(context, batches, draw_arrow=True, gray=True)

                        if addon.drag_star:
                            addon.drag_star[0].axes[0].draw(context, batches, draw_arrow=True)

                        if nearest_axis is not None:
                            addon.props.clear()

                            for key in nearest_axis.props.keys():
                                addon.props[key] = nearest_axis.props[key]

                            addon.nearest_axis[:] = [nearest_axis]

                        else:
                            addon.props.clear()
                            addon.nearest_axis[:] = []


        gpu.state.blend_set(gpu_blend)



class ALIGNTOOL_GGT_common_gizmo_group(GizmoGroup):

    bl_idname = "ALIGNTOOL_GGT_common_gizmo_group"
    bl_label = "Gizmo Group"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {"3D", "PERSISTENT", "SHOW_MODAL_ALL"}


    @classmethod
    def poll(cls, context):

        return align_tool_selected(context)


    def setup(self, context):

        # Check if the CACHE is empty and initialize if needed
        addon = context.window_manager.align_tool

        CACHE_update(context)

        if CACHE_depsgraph_check not in bpy.app.handlers.depsgraph_update_post:
            bpy.app.handlers.depsgraph_update_post.append(CACHE_depsgraph_check)

        if CACHE_undo_check not in bpy.app.handlers.undo_post:
            bpy.app.handlers.undo_post.append(CACHE_undo_check)

        if CACHE_clear not in bpy.app.handlers.load_pre:
            bpy.app.handlers.load_pre.append(CACHE_clear)

        if not addon.draw_handler_2D:
            handler_2D = bpy.types.SpaceView3D.draw_handler_add(draw_2D, (context,), "WINDOW", "POST_PIXEL")
            addon.draw_handler_2D[:] = [handler_2D]


        # Check for active gizmo group instances and remove them when invalid
        add_new_instance = True

        for instance in addon.gizmo_group_instances:
            area, group = instance

            if context.area == area:
                if "invalid" not in str(group):
                    add_new_instance = False
                else:
                    addon.gizmo_group_instances.remove(instance)
                break

        # Add a new gizmo group instance to the current VIEW_3D area if there isn't any
        if add_new_instance:

            addon.gizmo_group_instances.append((context.area, self))
            gizmo = self.gizmos.new(ALIGNTOOL_GT_custom_gizmo.bl_idname)
            # self.show_gizmo_state = context.area.spaces[0].show_gizmo
            #gizmo.use_select_background = True
            #gizmo.use_draw_modal = True
