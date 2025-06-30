from .common_imports import *

from .gpu_functions import draw_batch_shader, draw_batch_shader_line, draw_stipple_lines_batch_shader
# from .draw_functions import highlight_objects
from .general_functions import get_matrix_grid_point, get_matrix_midpoint_point
from .context_functions import (point_to_view_scaled_matrix, is_line_cursor_close, get_line_matrix,
                                is_point_cursor_close, get_point_draw_matrix, is_view_facing,
                                get_local_bounds_use)


# -- User Interface Widgets --

class star_box:

    def __init__(self, box_type):

        self.type = box_type
        self.stars = []

        for star_index, star_center in enumerate(((1, 0.5, 0.5), (0, 0.5, 0.5), (0.5, 1, 0.5),
                                                  (0.5, 0, 0.5), (0.5, 0.5, 1), (0.5, 0.5, 0))):
            self.stars.append(star(self, box_type, Matrix.Translation(star_center), star_index))


    def update(self, context, event, matrix, fallback_matrix=Matrix()):

        self.matrix = matrix
        self.fallback_matrix = fallback_matrix

        for star in self.stars:
            star.update(context, event)


    def draw(self, context, event, batches_database, nearest_axis, only_points=False):

        ui_scale = context.preferences.system.ui_scale
        is_local = event.alt
        pattern = batches_database.line_pattern_inverted

        if self.type == "ACTIVE":

            star_color = 1, 1, 1, 0.8
            objects_list = [context.object.name]
            box_color = 1, 1, 1, 0.4

            if is_local:
                box_color = 1, 0.3, 1, 0.8 # 1, 0.3, 0.9, 0.6

                if get_local_bounds_use(context):
                    box_color = 1, 0.8, 1, 0.8
                    pattern = batches_database.line_pattern

        elif self.type == "SELECTED":
            box_color = 0, 0, 0, 0.7
            star_color = 0, 0, 0, 0.8
            objects_list = context.window_manager.align_tool.CACHE["selected_objects"]

        for star in self.stars:
            if not only_points:
                if nearest_axis is not None:
                    if star is nearest_axis.star:
                        # highlight_objects(context, objects_list)

                        if self.matrix.to_scale() != Vector((0, 0, 0)):
                            gpu.state.line_width_set(ui_scale)
                            draw_stipple_lines_batch_shader(batches_database.bounds_batch, context, box_color,
                                                            pattern, int(6 * ui_scale), matrix=self.matrix)
                            gpu.state.line_width_set(1)

                        for axis in star.axes:
                            if axis is nearest_axis:
                                axis.draw(context, batches_database, draw_arrow=True)
                            else:
                                axis.draw(context, batches_database)

                        continue

            star.draw(context, batches_database, star_color)


class star:

    def __init__(self, box, box_type, matrix, index):

        self.box = box
        self.type = box_type
        self.matrix_base = matrix
        self.matrix_drag = None
        self.index = index
        axes_matrices = Matrix(), Matrix.Rotation(pi/2, 4, "Z"), Matrix.Rotation(-pi/2, 4, "Y")
        self.axes = [axis(box_type, self, index, matrix) for index, matrix in enumerate(axes_matrices)]


    def apply_matrix_drag(self, context, event, matrix_drag):

        self.matrix_drag = matrix_drag
        self.update(context, event)


    def update(self, context, event):

        ui_scale = context.preferences.system.ui_scale
        star_size = 80 * ui_scale
        star_search_distance = 60 * ui_scale
        axis_search_distance = 60 * ui_scale

        if self.matrix_drag:
            self.matrix = self.matrix_drag
        else:
            self.matrix = self.box.matrix @ self.matrix_base

        self.location = self.matrix.to_translation()
        if context.area.type == "VIEW_3D":  # workaround when there's no 3D view
            self.cursor_close, self.cursor_distance = is_point_cursor_close(context, event, self.location, star_search_distance)
        else:
            self.cursor_close, self.cursor_distance = False, 0

        if self.matrix.determinant() == 0:
            self.matrix = Matrix.Translation(self.location) @ self.box.fallback_matrix.to_4x4()

        if context.area.type == "VIEW_3D":  # workaround when there's no 3D view
            self.matrix = self.matrix.normalized() @ point_to_view_scaled_matrix(context, self.location, star_size).to_4x4()

        for axis in self.axes:
            axis.update(context, event, axis_search_distance, star_size)


    def draw(self, context, batches_database, color):

        ui_scale = context.preferences.system.ui_scale
        point_matrix = get_point_draw_matrix(context, self.location, 6 * ui_scale)
        draw_batch_shader(batches_database.point_batch, color, point_matrix)


class axis:

    def __init__(self, box_type, star, index, matrix):

        self.type = box_type
        self.star = star
        self.index = index
        self.matrix_base = matrix
        self.props = dict()


    def update(self, context, event, axis_search_distance, point_search_distance):

        self.matrix = self.star.matrix @ self.matrix_base
        self.point_max = self.matrix @ Vector((1, 0, 0))
        self.point_min = self.matrix @ Vector((-1, 0, 0))
        if context.area.type == "VIEW_3D":  # workaround when there's no 3D view
            self.cursor_close, self.cursor_distance = is_line_cursor_close(context, event, self.star.location, self.point_max, axis_search_distance)
        else:
            self.cursor_close, self.cursor_distance = False, 0

        if self.cursor_close:
            key_points = self.point_min, self.star.location, self.point_max
            points = [is_point_cursor_close(context, event, point, point_search_distance) for point in key_points]
            self.closest_index = points.index(min(points, key=lambda point: point[1]))

            is_local = event.alt

            self.props.clear()

            if self.type in ("WORLD", "CURSOR"):

                self.props["plane_target"] = self.type

                if not is_local:

                    self.props["plane_orientation"] = "GLOBAL"

            else:

                self.props["plane_target"] = "OBJECT"
                self.props["plane_object"] = ""
                self.props["plane_type"] = "BOUNDS"
                self.props["plane_reference"] = self.type
                self.props["plane_use_local"] = is_local

            self.props["direction_custom_orientation"] = "PERPENDICULAR"
            self.props["plane_depth"] = (("MAX", "CENTER", "CENTER"), ("MIN", "CENTER", "CENTER"),
                                        ("CENTER", "MAX", "CENTER"), ("CENTER", "MIN", "CENTER"),
                                        ("CENTER", "CENTER", "MAX"), ("CENTER", "CENTER", "MIN"))[self.star.index][self.index]
            self.props["plane_axis"] = ("X", "Y", "Z")[self.index]
            self.props["origin_target"] = "OBJECTS"
            self.props["origin_type"] = "BOUNDS"
            self.props["origin_use_local"] = False
            self.props["origin_depth_X"] = "CENTER"
            self.props["origin_depth_Y"] = "CENTER"
            self.props["origin_depth_Z"] = ("MAX", "CENTER", "MIN")[self.closest_index]


    def draw(self, context, batches_database, draw_arrow=False, gray=False):

        region = context.region
        ui_scale = context.preferences.system.ui_scale

        axis_outline_COLOR = ((0.88671875, 0.21875,    0.3203125,  1), # (1, 0.3, 0.3, 1)
                              (0.45,       0.675,      0.054,      1), # (0.5,        0.7578125,  0.0625,     1), # (0.2, 0.7, 0.2, 1)
                              (0.24609375, 0.56640625, 0.90234375, 1)) # (0.4, 0.4, 1, 1)
        axis_fill_COLOR = ((1, 1, 1, 0.4),
                           (1, 1, 1, 0.65),
                           (1, 1, 1, 0.5))

        if gray:
            outline_color = 1, 1, 1, 0.2
            fill_color = 1, 1, 1, 0.4
        else:
            outline_color = axis_outline_COLOR[self.index]
            fill_color = axis_fill_COLOR[self.index]

        if draw_arrow and self.cursor_close:
            view_facing = is_view_facing(context, self.star.location, self.point_min if self.closest_index == 0 else self.point_max)

            if self.closest_index == 1:
                rotated_matrix = self.matrix @ Matrix.Rotation(pi, 4, "Z")
                positive_arrow_matrix = rotated_matrix @ Matrix.Translation(Vector((-1.1, 0, 0)))
                negative_arrow_matrix = self.matrix @ Matrix.Translation(Vector((-1.1, 0, 0)))

                draw_batch_shader_line(batches_database.solid_line_batch, region, outline_color,
                                       width=3 * ui_scale, matrix=self.matrix)
                draw_batch_shader_line(batches_database.solid_line_batch, region, outline_color,
                                       width=3 * ui_scale, matrix=rotated_matrix)

                for point in (self.point_max, self.point_min):
                    point_matrix = get_point_draw_matrix(context, point, 8 * ui_scale)
                    draw_batch_shader(batches_database.point_batch, outline_color, point_matrix)

                draw_matrices = ((negative_arrow_matrix, positive_arrow_matrix),
                                 (positive_arrow_matrix, negative_arrow_matrix))[0 if view_facing else 1]

                # Draw the outlines first
                for draw_matrix in draw_matrices:
                    draw_batch_shader(batches_database.axes_arrow_outline_batch, outline_color, draw_matrix)

                # Now draw the fills. Repeating the iteration in this way prevents one of the outlines to draw on top of a previously drawn fill
                for draw_matrix in draw_matrices:
                    gpu.state.face_culling_set("BACK")
                    draw_batch_shader(batches_database.axes_arrow_fill_batch, fill_color, draw_matrix)
                    gpu.state.face_culling_set("NONE")

            else:
                if self.closest_index == 2:
                    point = self.point_min
                    matrix = self.matrix
                else:
                    point = self.point_max
                    matrix = self.matrix @ Matrix.Rotation(pi, 4, "Z")

                draw_batch_shader_line(batches_database.solid_line_batch, region, outline_color,
                                       width=3 * ui_scale, matrix=matrix)

                point_matrix = get_point_draw_matrix(context, point, 8 * ui_scale)
                draw_batch_shader(batches_database.point_batch, outline_color, point_matrix)

                for draw in (("PLANE", "ARROW"), ("ARROW", "PLANE"))[0 if view_facing else 1]:

                    if draw == "PLANE":
                        draw_batch_shader(batches_database.axes_plane_outline_batch, outline_color, matrix)
                        draw_batch_shader(batches_database.axes_plane_fill_batch, fill_color, matrix)
                    elif draw == "ARROW":
                        draw_batch_shader(batches_database.axes_arrow_outline_batch, outline_color, matrix)
                        gpu.state.face_culling_set("BACK")
                        draw_batch_shader(batches_database.axes_arrow_fill_batch, fill_color, matrix)
                        gpu.state.face_culling_set("NONE")

        else:
            for point in (self.point_max, self.point_min):
                point_matrix = get_point_draw_matrix(context, point, 8 * ui_scale)
                draw_batch_shader(batches_database.point_batch, outline_color, point_matrix)


class grid_box:

    def __init__(self, box_type):

        self.type = box_type
        self.points = [grid_point(box_type, i) for i in range(27)]


    def update(self, context, event, matrix):

        self.matrix = matrix

        for point in self.points:
            point.update(context, event, matrix)


    def draw(self, context, event, batches_database):

        ui_scale = context.preferences.system.ui_scale

        if self.type == "SELECTION":
            color = 0, 0, 0, 0.6
        elif self.type == "OBJECT_BOUNDS":
            if event.alt:
                color = 1, 0.3, 1, 0.8 # 1, 0.3, 0.9, 0.6
            else:
                color = 1, 1, 1, 0.5

        for i in range(27):

            if i in (0, 2, 6, 8, 18, 20, 24, 26):
                point_matrix = get_point_draw_matrix(context, self.points[i].location, 8 * ui_scale)
                draw_batch_shader(batches_database.point_batch, color, point_matrix)
            else:
                point_matrix = get_point_draw_matrix(context, self.points[i].location, 5 * ui_scale)
                draw_batch_shader(batches_database.square_batch, color, point_matrix)


class grid_point:

    def __init__(self, point_type, index=None):

        self.type = point_type
        self.index = index
        self.props = dict()

        if point_type in ("SELECTION", "OBJECT_BOUNDS"):

            x_indices = ((0, 1, 2, 3, 4, 5, 6, 7, 8),
                         (9, 10, 11, 12, 13, 14, 15, 16, 17),
                         (18, 19, 20, 21, 22, 23, 24, 25, 26))

            y_indices = ((0, 1, 2, 9, 10, 11, 18, 19, 20),
                         (3, 4, 5, 12, 13, 14, 21, 22, 23),
                         (6, 7, 8, 15, 16, 17, 24, 25, 26))

            z_indices = ((0, 3, 6, 9, 12, 15, 18, 21, 24),
                         (1, 4, 7, 10, 13, 16, 19, 22, 25),
                         (2, 5, 8, 11, 14, 17, 20, 23, 26))

            self.props["origin_depth_X"] = ("MIN", "CENTER", "MAX")[[self.index in x_plane for x_plane in x_indices].index(True)]
            self.props["origin_depth_Y"] = ("MIN", "CENTER", "MAX")[[self.index in y_plane for y_plane in y_indices].index(True)]
            self.props["origin_depth_Z"] = ("MIN", "CENTER", "MAX")[[self.index in z_plane for z_plane in z_indices].index(True)]


    def update(self, context, event, matrix):

        ui_scale = context.preferences.system.ui_scale

        if self.type in ("WORLD", "CURSOR", "OBJECT_LOCATION", "ORIGIN"):
            self.location = matrix.to_translation()
        elif self.type in ("SELECTION", "OBJECT_BOUNDS"):
            self.location = get_matrix_grid_point(matrix, self.index)

        self.matrix = matrix

        search_distance = 30 * ui_scale
        self.cursor_close, self.cursor_distance = is_point_cursor_close(context, event, self.location, search_distance)

        if self.cursor_close:
            is_local = event.alt

            if self.type == "ORIGIN":
                self.props["origin_target"] = "OBJECTS"
                self.props["origin_type"] = "CUSTOM"
            elif self.type in ("WORLD", "CURSOR"):
                self.props["origin_target"] = self.type
            else:
                self.props["origin_target"] = "OBJECTS"
                self.props["origin_type"] = "LOCATION" if self.type == "OBJECT_LOCATION" else "BOUNDS"

                if self.type == "SELECTION":
                    self.props["origin_all_selected"] = True
                    self.props["origin_use_local"] = False
                elif self.type == "OBJECT_BOUNDS":
                    self.props["origin_all_selected"] = False
                    self.props["origin_use_local"] = is_local


    def draw(self, context, event, batches_database, is_selected=True):

        # addon = context.window_manager.align_tool
        ui_scale = context.preferences.system.ui_scale

        # if self.type in ("OBJECT_LOCATION", "OBJECT_BOUNDS", "SELECTION", "ORIGIN"):

        #     if self.type == "ORIGIN":
        #         highlight_objects(context, [addon.CACHE["custom_origin"]["object"]])
        #     elif self.type == "SELECTION":
        #         highlight_objects(context, addon.CACHE["selected_objects"])
        #     else:
        #         highlight_objects(context, [context.object.name])

        if self.type in ("SELECTION", "OBJECT_BOUNDS"):

            if self.type == "SELECTION":
                color = 0, 0, 0, 0.6

            elif self.type == "OBJECT_BOUNDS":
                color = 1, 1, 1, 0.5

                if event.alt:
                    color = 1, 0.3, 1, 0.8 # 1, 0.3, 0.9, 0.6

                    if get_local_bounds_use(context):
                        color = 1, 0.8, 1, 0.8

            if self.matrix.to_scale() != Vector((0, 0, 0)):
                gpu.state.line_width_set(ui_scale)
                draw_stipple_lines_batch_shader(batches_database.bounds_batch, context, color,
                                                batches_database.line_pattern, int(6 * ui_scale), matrix=self.matrix)
                gpu.state.line_width_set(1)

        individual = self.type in ("WORLD", "CURSOR", "OBJECT_LOCATION", "ORIGIN")

        if True in (self.index in (0, 2, 6, 8, 18, 20, 24, 26), individual):
            shape = batches_database.point_batch
            size = 8 * ui_scale
        else:
            shape = batches_database.square_batch
            size = 5 * ui_scale

        if self.type == "ORIGIN":
            color = 0, 1, 0, 0.8
        else:
            color = 1, 1, 1, 0.5

        if is_selected:
            color = 1, 1, 0, 1

        point_matrix = get_point_draw_matrix(context, self.location, size)
        draw_batch_shader(shape, color, point_matrix)


class midpoint_box:

    def __init__(self, box_type):

        self.type = box_type
        x_center_min = (8, 0),  (9, 2),  (10, 5),  (11, 7)
        x_center_max = (8, 12), (9, 14), (10, 17), (11, 19)
        y_center_min = (3, 0),  (4, 2),  (15, 12), (16, 14)
        y_center_max = (3, 5),  (4, 7),  (15, 17), (16, 19)
        z_center_min = (1, 0),  (6, 5),  (13, 12), (18, 17)
        z_center_max = (1, 2),  (6, 7),  (13, 14), (18, 19)

        axes_info = (((x_center_min, y_center_min, z_center_min), ("CENTER", "MIN")),
                     ((x_center_max, y_center_max, z_center_max), ("CENTER", "MAX")))

        self.midpoint_edges = []

        for axis_group in axes_info:
            axes_indices, depths = axis_group
            for axis_index, axis in enumerate(axes_indices):
                for edge_indices in axis:
                    self.midpoint_edges.append(midpoint_edge(box_type, axis_index, edge_indices, depths))


    def update(self, context, event, matrix, object_name=""):

        self.matrix = matrix

        for edge in self.midpoint_edges:
            edge.update(context, event, matrix, object_name)


    def draw(self, context, event, batches_database):

        ui_scale = context.preferences.system.ui_scale

        if self.type == "SELECTION":
            color = 0, 0, 0, 0.6
        elif self.type == "OBJECT_BOUNDS":
            if event.alt:
                color = 1, 0.3, 1, 0.8 # 1, 0.3, 0.9, 0.6
            else:
                color = 1, 1, 1, 0.5

        for i in (0, 2, 5, 7, 12, 14, 17, 19):
            point = get_matrix_midpoint_point(self.matrix, i)
            point_matrix = get_point_draw_matrix(context, point, 6 * ui_scale)
            draw_batch_shader(batches_database.point_batch, color, point_matrix)


class midpoint_star:

    def __init__(self, box_type):

        self.type = box_type

        axes_indices = (((6, 0), (6, 1)),
                        ((6, 2), (6, 3)),
                        ((6, 4), (6, 5)))
        depths = "CENTER", "CENTER"

        self.midpoint_edges = []

        for axis_index, axis in enumerate(axes_indices):
            for edge_indices in axis:
                self.midpoint_edges.append(midpoint_edge(box_type, axis_index, edge_indices, depths))


    def update(self, context, event, matrix, object_name=""):

        ui_scale = context.preferences.system.ui_scale

        star_size = 60 * ui_scale
        self.matrix = matrix.normalized() @ point_to_view_scaled_matrix(context, matrix.to_translation(), star_size).to_4x4()

        for edge in self.midpoint_edges:
            edge.update(context, event, self.matrix, object_name)


    def draw(self, context, batches_database):

        ui_scale = context.preferences.system.ui_scale

        for edge in self.midpoint_edges:
            color = ((1, 0.5, 0.5, 0.6),
                     (0.5, 1, 0.5, 0.6),
                     (0.6, 0.6, 1, 0.6))[edge.axis_index]
            point_matrix = get_point_draw_matrix(context, edge.point2, 6 * ui_scale)
            draw_batch_shader(batches_database.point_batch, color, point_matrix)


class midpoint_edge:

    def __init__(self, edge_type, axis_index, edge_indices, depths):

        self.type = edge_type
        self.axis_index = axis_index
        self.point1_index, self.point2_index = edge_indices
        self.point1_depth, self.point2_depth = depths
        self.props = dict()


    def update(self, context, event, matrix, object_name):

        ui_scale = context.preferences.system.ui_scale

        if self.type in ("WORLD", "CURSOR", "OBJECT_LOCATION"):
            axes = (1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1), (0, 0, 0)
            self.point1 = matrix @ Vector(axes[self.point1_index])
            self.point2 = matrix @ Vector(axes[self.point2_index])
        else:
            self.point1 = get_matrix_midpoint_point(matrix, self.point1_index)
            self.point2 = get_matrix_midpoint_point(matrix, self.point2_index)

        self.matrix = matrix
        self.object_name = object_name

        search_distance = 20 * ui_scale
        self.cursor_close, self.cursor_distance = is_line_cursor_close(context, event, self.point1, self.point2, search_distance)

        if self.cursor_close:
            cursor_close, self.point1_distance = is_point_cursor_close(context, event, self.point1, search_distance)
            cursor_close, self.point2_distance = is_point_cursor_close(context, event, self.point2, search_distance)
            points = (0, self.point1_distance), (1, self.point2_distance)
            self.closest_index = min(points, key=lambda p: p[1])[0]

            is_local = event.alt

            self.props.clear()

            if self.type in ("WORLD", "CURSOR"):
                self.props["plane_axis"] = ("X", "Y", "Z")[self.axis_index]
                self.props["plane_target"] = self.type

                if not is_local:

                    self.props["plane_orientation"] = "GLOBAL"

            elif self.type == "SELECTION":
                self.props["plane_axis"] = ("X", "Y", "Z")[self.axis_index]
                self.props["plane_target"] = "OBJECT"
                self.props["plane_object"] = object_name
                self.props["plane_reference"] = "SELECTED"
                self.props["plane_type"] = "BOUNDS"
                self.props["plane_use_local"] = True if is_local else False
                self.props["plane_depth"] = (self.point1_depth, self.point2_depth)[self.closest_index]

            elif self.type in ("OBJECT_LOCATION", "OBJECT_BOUNDS"):

                self.props["plane_axis"] = ("X", "Y", "Z")[self.axis_index]
                self.props["plane_target"] = "OBJECT"
                self.props["plane_object"] = object_name

                if self.type == "OBJECT_LOCATION":
                    self.props["plane_type"] = "LOCATION"

                    if not is_local:

                        self.props["plane_orientation"] = "GLOBAL"

                elif self.type == "OBJECT_BOUNDS":
                    self.props["plane_type"] = "BOUNDS"
                    self.props["plane_use_local"] = True if is_local else False
                    self.props["plane_depth"] = (self.point1_depth, self.point2_depth)[self.closest_index]


    def draw(self, context, event, batches_database):

        # addon = context.window_manager.align_tool
        region = context.region
        ui_scale = context.preferences.system.ui_scale

        # if self.type in ("OBJECT_LOCATION", "OBJECT_BOUNDS", "SELECTION"):

        #     if self.type == "SELECTION":
        #         highlight_objects(context, addon.CACHE["selected_objects"])
        #     else:
        #         highlight_objects(context, [self.object_name])

        if self.type in ("SELECTION", "OBJECT_BOUNDS"):

            if self.type == "SELECTION":
                color = 0, 0, 0, 0.6

            elif self.type == "OBJECT_BOUNDS":
                color = 1, 1, 1, 0.5

                if event.alt:
                    color = 1, 0.3, 1, 0.8 # 1, 0.3, 0.9, 0.6

                    if get_local_bounds_use(context):
                        color = 1, 0.8, 1, 0.8

            if self.matrix.to_scale() != Vector((0, 0, 0)):
                gpu.state.line_width_set(ui_scale)
                draw_stipple_lines_batch_shader(batches_database.bounds_batch, context, color,
                                                batches_database.line_pattern, int(6 * ui_scale), matrix=self.matrix)
                gpu.state.line_width_set(1)

        color = ((1, 0.5, 0.5, 1),
                 (0.5, 1, 0.5, 1),
                 (0.6, 0.6, 1, 1))[self.axis_index]
        line_matrix = get_line_matrix(self.point1, self.point2)

        draw_batch_shader_line(batches_database.solid_line_batch, region, color,
                               width=2 * ui_scale, matrix=line_matrix)

        if self.type in ("WORLD", "CURSOR", "OBJECT_LOCATION"):
            closest_point = self.point2
        else:
            closest_point = (self.point1, self.point2)[self.closest_index]

        point_matrix = get_point_draw_matrix(context, closest_point, 6 * ui_scale)
        draw_batch_shader(batches_database.point_batch, (1, 1, 0, 1), point_matrix)
