from .common_imports import *

from .general_functions import apply_matrix_to_points, points_to_world_matrix


# -- Context dependent functions --

def align_tool_selected(context, mode=None):

    """Returns if the align tool is selected in the current context mode,
       unless some mode is specified, which may be different than the current"""

    context_modes = {"OBJECT": "align_tool.tool_object",
                     "EDIT_MESH": "align_tool.tool_edit"}

    if mode is not None:

        tool_mode = mode

    else:

        tool_mode = context.mode

    mode_idname = context_modes[tool_mode] if tool_mode in context_modes else None
    active_tool = context.workspace.tools.from_space_view3d_mode(mode=context.mode)

    if active_tool is not None:

        if active_tool.idname == mode_idname:

            return True

    return False


def get_plane_individual_object(context):

    addon = context.window_manager.align_tool

    is_plane_object = addon.plane_object in context.scene.objects

    if is_plane_object:
        return context.scene.objects[addon.plane_object]

    return context.object


def get_plane_type(context):

    addon = context.window_manager.align_tool

    if addon.plane_target in ("WORLD", "CURSOR"):

        return addon.plane_target

    if addon.plane_target == "OBJECT":

        if addon.plane_object:

            if addon.plane_type == "LOCATION":

                return "OBJECT_LOCATION_PLANE"

            if addon.plane_type == "BOUNDS":

                return "OBJECT_BOUNDS_PLANE"

        if addon.plane_type == "LOCATION":

            return "OBJECT_LOCATION"

        if addon.plane_type == "BOUNDS":

            if addon.plane_reference == "ACTIVE":

                return "OBJECT_BOUNDS_ACTIVE"

            if addon.plane_reference == "SELECTED":

                return "OBJECT_BOUNDS_SELECTED"


def get_origin_type(context):

    addon = context.window_manager.align_tool

    if addon.origin_target in ("WORLD", "CURSOR"):

        return addon.origin_target

    if addon.origin_target == "OBJECTS":

        if addon.origin_type == "CUSTOM":

            return "CUSTOM"

        if addon.origin_type == "LOCATION":

            return "OBJECTS_LOCATION"

        if addon.origin_type == "BOUNDS":

            return "OBJECTS_BOUNDS"


def get_plane_box_matrix(context):

    addon = context.window_manager.align_tool
    CACHE = addon.CACHE
    plane_type = get_plane_type(context)

    if plane_type in ("OBJECT_BOUNDS_PLANE",
                      "OBJECT_BOUNDS_ACTIVE"):

        individual_object = get_plane_individual_object(context)

        if individual_object is not None:
            cached_object = CACHE["cached_objects"][individual_object.name]

            if addon.plane_use_local:

                return cached_object["boxes"]["local"]

            if addon.plane_use_geometry:

                return cached_object["boxes"]["world_geometry"]

            return cached_object["boxes"]["world"]

        return None

    if plane_type == "OBJECT_BOUNDS_SELECTED":

        if addon.plane_use_local:

            if addon.plane_use_geometry:

                return CACHE["selection_bounds"]["local_geometry"]

            return CACHE["selection_bounds"]["local"]

        if addon.plane_use_geometry:

            return CACHE["selection_bounds"]["geometry"]

        return CACHE["selection_bounds"]["world"]

    return None



def delete_custom_origin(context):

    addon = context.window_manager.align_tool

    if "custom_origin" in addon.CACHE:
        del addon.CACHE["custom_origin"]

    if addon.origin_type == "CUSTOM":
        addon.origin_type = "BOUNDS"

def delete_custom_plane(context):

    addon = context.window_manager.align_tool
    addon.drag_star.clear()

    if addon.plane_target == "CUSTOM":
        addon.plane_target = "OBJECT"



def get_mouse_vector_ratio(context, event, vector_base, vector_tip):
    region = context.region
    rv3d = context.region_data
    mouse_3D_location = reg2d_to_loc3d(region, rv3d, (event.mouse_x - region.x, event.mouse_y - region.y), vector_base)
    vector_world = vector_tip - vector_base
    return (mouse_3D_location - vector_base).dot(vector_world) / vector_world.length

def bounds_in_use(context):
    addon = context.window_manager.align_tool
    if addon.drag_star:
        return False
    if addon.plane_target == "OBJECT":
        if addon.plane_object:
            if addon.plane_type == "BOUNDS":
                return True
        else:
            if addon.plane_reference == "ACTIVE" and addon.plane_type == "BOUNDS":
                return True
            if addon.plane_reference == "SELECTED":
                return True
    return False

def get_local_bounds_use(context):

    addon = context.window_manager.align_tool

    if addon.origin_show_bounds:
        if addon.origin_target == "OBJECTS" and addon.origin_type == "BOUNDS":

            if addon.origin_use_local:
                return True

            if not addon.origin_use_geometry:
                return True

    if addon.plane_show_bounds:
        if addon.plane_target == "OBJECT" and addon.plane_type == "BOUNDS":

            if addon.plane_use_local:

                if addon.plane_use_geometry:
                    return False

                return True

            if not addon.plane_use_geometry:
                return True

    return False


def get_plane_draw_matrix(context, plane, projected_points):

    ui_scale = context.preferences.system.ui_scale

    if bounds_in_use(context):

        generic_points = [Vector(), Vector((1, 1, 0))]

    else:

        generic_points_matrix = point_to_view_scaled_matrix(context, plane.to_translation(), 120 * ui_scale)
        generic_points = [generic_points_matrix @ Vector((-1, -1, 0)),
                          generic_points_matrix @ Vector((1, 1, 0))]


    if projected_points:

        plane_space_points = apply_matrix_to_points(projected_points, plane.inverted())
        points_matrix = points_to_world_matrix(plane_space_points)
        p1, p2, p3, p4, offseted_points = (0, 0, 0), (0, 1, 0), (1, 0, 0), (1, 1, 0), []

        for axis, sides in enumerate((((p1, p2), (p3, p4)),
                                      ((p1, p3), (p2, p4)))):

            offsets = (((-0.1, 0, 0), (0.1, 0, 0)), ((0, -0.1, 0), (0, 0.1, 0)))[axis]

            for index, edge in enumerate(sides):

                offset = Vector((offsets[index]))
                extensions = ((plane @ points_matrix @ Vector(point), plane @ ((points_matrix @ Vector(point)) + offset)) for point in edge)
                extensions_2D = ([loc3d_to_reg2d(context.region, context.region_data, p) for p in ext] for ext in extensions)
                lengths = [(ext_2D[1] - ext_2D[0]).length for ext_2D in extensions_2D if None not in ext_2D]
                factor = max(lengths) if lengths else 30 * ui_scale
                offseted_points.append((points_matrix @ Vector(edge[0])) + (offset * ((30 * ui_scale) / max(0.5, factor))))

        return plane @ points_to_world_matrix(offseted_points + generic_points)

    else:

        return plane @ points_to_world_matrix(generic_points)


def get_point_draw_matrix(context, point, point_size):
    point_scale_matrix = point_to_view_scaled_matrix(context, point, pixel_size=point_size)
    return Matrix.Translation(point) @ (context.region_data.view_rotation.to_matrix() @ point_scale_matrix).to_4x4()

def get_line_matrix(start, end):
    return Matrix([(end.x - start.x, 0, 0, start.x),
                   (end.y - start.y, 1, 0, start.y),
                   (end.z - start.z, 0, 1, start.z),
                   (0,               0, 0, 1)])
    # Matrix.Translation(start) @ Matrix([(end - start), Vector(), Vector()]).transposed().to_4x4()

def get_arrow_draw_matrices(context, start, end):
    region = context.region
    rv3d = context.region_data
    ui_scale = context.preferences.system.ui_scale
    line_matrix = arrow_matrix = None
    start_2D = loc3d_to_reg2d(region, rv3d, start)
    end_2D = loc3d_to_reg2d(region, rv3d, end)
    if start_2D is None and end_2D is not None:
        start_2D = point_behind_to_front(context, end, start)
    elif start_2D is not None and end_2D is None:
        end_2D = point_behind_to_front(context, start, end)

    if start_2D and end_2D:
        midpoint = (start + end) / 2
        midpoint_2D = loc3d_to_reg2d(region, rv3d, midpoint)
        if midpoint_2D is None:
            midpoint_2D = point_behind_to_front(context, end, midpoint)
        ratio = 1
        if midpoint_2D is not None:
            midpoint_end_length = (end_2D - midpoint_2D).length
            if midpoint_end_length != 0:
                ratio = (start_2D - midpoint_2D).length / midpoint_end_length
        start_2D_world = start_2D - end_2D
        length = start_2D_world.length / max(0.1, (ratio * 0.1))
        factor = max(0, length - (20 * ui_scale)) / max(0.5, length)
        line_matrix = get_line_matrix(start, ((end - start) * factor) + start)
        # line_matrix = Matrix.Translation(start) @ Matrix([(end - start) * factor, Vector(), Vector()]).transposed().to_4x4()

        line_3D = start_2D_world.to_3d()
        size = min(40 * ui_scale, max(0, (line_3D.length + (5 * ui_scale))))
        scale_matrix = point_to_view_scaled_matrix(context, end, size)
        rotation_matrix = Vector((1, 0.0001, 0)).rotation_difference(line_3D).to_matrix() # a small deviation is introduced to avoid colinearity at 180º
        arrow_matrix = Matrix.Translation(end) @ (rv3d.view_rotation.to_matrix() @ rotation_matrix @ scale_matrix).to_4x4()
    return line_matrix, arrow_matrix

def point_to_screen_space(context, point):
    point_perspective = context.region_data.perspective_matrix @ Vector(point).to_4d()
    x_ndc_space = point_perspective[0] / point_perspective[3]
    y_ndc_space = point_perspective[1] / point_perspective[3]
    x_screen_normalized = (x_ndc_space + 1) / 2
    y_screen_normalized = (y_ndc_space + 1) / 2
    return Vector((x_screen_normalized * context.region.width,
                   y_screen_normalized * context.region.height))

def is_point_cursor_close(context, event, point, distance):
    region = context.region
    point_screen_space = point_to_screen_space(context, point)
    mouse_screen_space = Vector((event.mouse_x - region.x,
                                 event.mouse_y - region.y))
    point_mouse_distance = (point_screen_space - mouse_screen_space).length
    return point_mouse_distance < distance, point_mouse_distance

def is_line_cursor_close(context, event, start, end, distance):
    region = context.region
    start_screen_space = point_to_screen_space(context, start)
    end_screen_space = point_to_screen_space(context, end)
    mouse_screen_space = Vector((event.mouse_x - region.x,
                                 event.mouse_y - region.y))
    mouse_global = mouse_screen_space - start_screen_space
    line_global = end_screen_space - start_screen_space

    projected = mouse_global.project(line_global)
    line_mouse_distance = (mouse_global - projected).length

    minimum_corner = -distance
    maximum_corner = line_global.length + distance
    if isclose(line_global.length, 0, abs_tol=0.01):
        return False, line_mouse_distance
    mouse_ratio = mouse_global.dot(line_global) / line_global.length
    in_range = mouse_ratio > minimum_corner and mouse_ratio < maximum_corner
    is_close = line_mouse_distance < distance and in_range
    return is_close, line_mouse_distance

def point_to_view_scaled_matrix(context, point, pixel_size):
    region = context.region
    rv3d = context.region_data
    point_NDC = rv3d.perspective_matrix @ point.to_4d() # point to Normalized Device Coordinates
    perspective_axis_size = max(rv3d.perspective_matrix.inverted().col[:2]).length
    scale_factor = (point_NDC.w * perspective_axis_size) / max(region.width, region.height)
    return Matrix.Scale(abs(scale_factor) * pixel_size, 3)

def get_header_text(context):

    addon = context.window_manager.align_tool

    def get_direction_status():

        def get_axis():

            if addon.direction_custom_orientation == "PERPENDICULAR":
                return ""

            return f"{addon.direction_axis} "


        def get_direction():

            if addon.direction_custom_orientation == "CUSTOM":
                custom_orientation = context.scene.transform_orientation_slots[0].custom_orientation
                orientation_name = "None" if custom_orientation is None else custom_orientation.name
                return f"Custom ({orientation_name})"

            return addon.direction_custom_orientation.capitalize()


        def get_reference():

            if addon.direction_custom_orientation == "LOCAL":

                if not addon.origin_use_local and addon.origin_all_selected:
                    return " (Active)"

                return " ({})".format(addon.direction_reference.capitalize())

            return ""


        concepts = get_axis(), get_direction(), get_reference()

        return f"Direction: {' '.join(c for c in concepts if c)}"


    def get_plane_status():

        def get_orientation():

            plane_type = get_plane_type(context)
            bound_types = "OBJECT_BOUNDS_PLANE", "OBJECT_BOUNDS_ACTIVE", "OBJECT_BOUNDS_SELECTED"

            if plane_type in bound_types:

                if addon.plane_use_local:

                    return "Local"

                return "Global"

            if addon.plane_orientation == "CUSTOM":
                custom_orientation = context.scene.transform_orientation_slots[0].custom_orientation
                orientation_name = "None" if custom_orientation is None else custom_orientation.name
                return f"Custom ({orientation_name})"

            return addon.plane_orientation.capitalize()


        def get_at():

            plane_type = get_plane_type(context)
            bound_types = "OBJECT_BOUNDS_PLANE", "OBJECT_BOUNDS_ACTIVE", "OBJECT_BOUNDS_SELECTED"

            if plane_type in bound_types:

                return ""

            return "at"


        def get_type():

            if addon.plane_target == "OBJECT":

                return addon.plane_type.capitalize()

            return ""


        def get_from():

            if addon.plane_target == "OBJECT":

                return "from"

            return ""


        def get_reference():

            if addon.plane_target == "OBJECT":

                plane_type = get_plane_type(context)
                plane_object_types = "OBJECT_LOCATION_PLANE", "OBJECT_BOUNDS_PLANE"
                bound_types = "OBJECT_BOUNDS_ACTIVE", "OBJECT_BOUNDS_SELECTED"

                if plane_type in plane_object_types:

                    return f"'{context.scene.objects[addon.plane_object].name}'"

                if plane_type in bound_types:

                    return addon.plane_reference.capitalize()

                return "Active"

            return ""


        def get_target():

            if addon.plane_target == "OBJECT":

                plane_type = get_plane_type(context)
                plane_object_types = "OBJECT_LOCATION_PLANE", "OBJECT_BOUNDS_PLANE"
                active_object_types = "OBJECT_LOCATION", "OBJECT_BOUNDS_ACTIVE"

                if plane_type in plane_object_types:

                    return ""

                if plane_type in active_object_types:

                    return "Object"

                if plane_type == "OBJECT_BOUNDS_SELECTED":

                    return "Objects"

            return addon.plane_target.capitalize()


        def get_geometry():

            plane_type = get_plane_type(context)
            object_bound_types = "OBJECT_BOUNDS_PLANE", "OBJECT_BOUNDS_ACTIVE"

            if plane_type in object_bound_types:

                if not addon.plane_use_local and addon.plane_use_geometry:

                    return "geometry"

            if plane_type == "OBJECT_BOUNDS_SELECTED":

                if addon.plane_use_geometry:

                    return "geometry"

            return ""


        if addon.plane_target == "CUSTOM":

            plane_axis = ("X", "Y", "Z")[addon.drag_star[0].axes[0].index]

            return f"Plane: {plane_axis} at Custom Plane"


        concepts = (addon.plane_axis,
                    get_orientation(),
                    get_at(),
                    get_type(),
                    get_from(),
                    get_reference(),
                    get_target(),
                    get_geometry())

        return f"Plane: {' '.join(c for c in concepts if c)}"


    def get_origin_status():

        def get_orientation():

            origin_type = get_origin_type(context)

            if origin_type == "OBJECTS_BOUNDS":

                is_perpendicular = addon.origin_use_geometry and not addon.origin_use_local

                if is_perpendicular:

                    return "Perpendicular"

                if addon.origin_use_local:

                    return "Local"

                return "Global"

            return ""


        def get_type():

            if addon.origin_target == "OBJECTS":

                return addon.origin_type.capitalize()

            return ""


        def get_from():

            if addon.origin_target == "OBJECTS":

                return "from"

            return ""


        def get_reference():

            if addon.origin_target == "OBJECTS":

                origin_type = get_origin_type(context)

                if origin_type == "OBJECTS_BOUNDS":

                    if not addon.origin_use_local:

                        if addon.origin_all_selected:

                            return "Selected"

                return "Individual"

            return ""


        def get_geometry():

            origin_type = get_origin_type(context)

            if origin_type == "OBJECTS_BOUNDS":

                if not addon.origin_use_local:

                    if addon.origin_use_geometry:

                        return "geometry"

            return ""


        if addon.origin_type == "CUSTOM":

            object_name = addon.CACHE["custom_origin"]["object"]

            return f"Origin: Vertex in '{object_name}'"


        concepts = (get_orientation(),
                    get_type(),
                    get_from(),
                    get_reference(),
                    addon.origin_target.capitalize(),
                    get_geometry())

        return f"Origin: {' '.join(c for c in concepts if c)}"


    return f"{get_direction_status()}  |  {get_plane_status()}  |  {get_origin_status()}"


def is_view_facing(context, base, point):
    base_global = context.region_data.perspective_matrix @ base
    point_global = context.region_data.perspective_matrix @ point
    return base_global[2] > point_global[2]

def get_mouse_in_region(region, event):
    mouse = event.mouse_x - region.x, event.mouse_y - region.y
    return ((mouse[0] > 0 and mouse[0] < region.width)
        and (mouse[1] > 0 and mouse[1] < region.height))

def get_current_orientation_matrix(context, local_matrix=Matrix()):
    rv3d = context.region_data
    addon = context.window_manager.align_tool

    if addon.plane_orientation == "LOCAL":
        return local_matrix.to_3x3().to_4x4()

    if addon.plane_orientation == "VIEW" and rv3d is not None:
        return rv3d.view_rotation.to_matrix().to_4x4()

    if addon.plane_orientation == "CUSTOM":
        orientations = context.scene.transform_orientation_slots[0]
        if orientations.custom_orientation is not None:
            return orientations.custom_orientation.matrix.to_4x4()

    return Matrix()

def redraw_3dviews(context):
    for area in context.screen.areas:
        if area.type == "VIEW_3D":
            area.tag_redraw()

def nearest_axis_plane(region, rv3d, event, bounds, linked_bounds):
    mouse = event.mouse_x - region.x, event.mouse_y - region.y
    bounds_2D = [loc3d_to_reg2d(region, rv3d, b) for b in bounds]
    bounds_2D_reduced = [b for b in bounds_2D if b is not None]
    if not bounds_2D_reduced:
        return False, None, None, None, None, bounds_2D
    kd = KDTree(len(bounds_2D_reduced))
    for i, bound in enumerate(bounds_2D_reduced):
        kd.insert(bound.to_3d(), i)
    kd.balance()
    origin, origin_index = kd.find(Vector(mouse).to_3d())[:2]
    origin = origin.to_2d()
    origin_index = bounds_2D.index(bounds_2D_reduced[origin_index])

    indices, axes = linked_bounds[origin_index]

    points_2D = []
    for i in indices:
        bound = bounds_2D[i]
        if bound is None:
            bound = point_behind_to_front(context, bounds[origin_index], bounds[i])
        points_2D.append(bound - origin)
    cursor = Vector(mouse) - origin

    points = [p for p in points_2D if cursor.dot(p) > 0]
    operation = min
    if not points:
        points = [p for p in points_2D if cursor.dot(p) < 0]
        operation = max
    projections = [cursor.project(p) for p in points]

    lengths = [(cursor - p) for p in projections]
    index = lengths.index(operation(lengths))
    projection = projections[index]
    nearest = points[index]

    offset = 20
    offset_factor = offset * nearest.length
    ratio = projection.dot(nearest)

    if ((projection - cursor).length < offset
        and ratio > -offset_factor
        and ratio < nearest.length_squared + offset_factor):
            axis = axes[points_2D.index(nearest)]
            return True, origin, origin_index, nearest, axis, bounds_2D
    return False, origin, origin_index, nearest, None, bounds_2D

def get_plane_depth(origin_index, axis):
    x_indices = ((0, 1, 2, 3, 4, 5, 6, 7),
                 (8, 9, 10, 11),
                 (12, 13, 14, 15, 16, 17, 18, 19))

    y_indices = ((0, 1, 2, 8, 9, 12, 13, 14),
                 (3, 4, 15, 16),
                 (5, 6, 7, 10, 11, 17, 18, 19))

    z_indices = ((0, 3, 5, 8, 10, 12, 15, 17),
                 (1, 6, 13, 18),
                 (2, 4, 7, 9, 11, 14, 16, 19))

    plane_indices = (x_indices, y_indices, z_indices)[("X", "Y", "Z").index(axis)]
    return ("MIN", "CENTER", "MAX")[[origin_index in row for row in plane_indices].index(True)]

def get_axis_scale(region, rv3d, bounds, origin):
    origin_2D = loc3d_to_reg2d(region, rv3d, origin)
    X_2D = loc3d_to_reg2d(region, rv3d, bounds[0])
    if not X_2D:
        X_2D = loc3d_to_reg2d(region, rv3d, bounds[1])
    Y_2D = loc3d_to_reg2d(region, rv3d, bounds[2])
    if not Y_2D:
        Y_2D = loc3d_to_reg2d(region, rv3d, bounds[3])
    Z_2D = loc3d_to_reg2d(region, rv3d, bounds[4])
    if not Z_2D:
        Z_2D = loc3d_to_reg2d(region, rv3d, bounds[5])
    available_axes = [axis for axis in (X_2D, Y_2D, Z_2D) if axis is not None]
    if available_axes and origin_2D:
        axes_lengths = [(axis - origin_2D).length for axis in available_axes if (axis - origin_2D).length != 0]
        if axes_lengths:
            return min([30 / length for length in axes_lengths])
    return None

# def highlight_plane_items(axis, origin, nearest, nearest_length=1):
#     color = ((1, 0.5, 0.5, 1),
#              (0.5, 1, 0.5, 1),
#              (0.6, 0.6, 1, 1))[("X", "Y", "Z").index(axis)]
#     OPENGL_draw_lines_2D([origin, origin + (nearest * nearest_length)], 2, color)
#     OPENGL_draw_points_2D([origin], 6, (1, 1, 0, 0.8))

def point_behind_to_front(context, point_front, point_behind):
    region = context.region
    rv3d = context.region_data
    view_center_2d = region.width/2, region.height/2
    view_vector = reg2d_to_vec3d(region, rv3d, view_center_2d)
    view_origin = reg2d_to_orig3d(region, rv3d, view_center_2d)
    projected_front = (point_front - view_origin).project(view_vector)
    projected_behind = (point_behind - point_front).project(view_vector)
    ratio = (projected_front.length / projected_behind.length) * 0.99
    behind_cropped = ((point_behind - point_front) * ratio) + point_front
    return loc3d_to_reg2d(region, rv3d, behind_cropped)

def get_simple_rectangle(width, height, offset=0):
    return [Vector(x) for x in ((0     - offset, 0      - offset),
                                (width + offset, 0      - offset),
                                (width + offset, height + offset),
                                (0     - offset, height + offset))]

def get_rounded_rectangle(width, height, padding, inner=False):
    rectangle = get_simple_rectangle(width, height, offset=-padding if inner else 0)
    angle_start = pi
    circle_steps = 5
    angle_step = (pi / 2) / circle_steps
    points = []
    for corner in rectangle:
        x = cos(angle_start) * padding
        y = sin(angle_start) * padding
        points.append(Vector((x, y)) + corner)
        for _ in range(circle_steps):
            angle_start += angle_step
            x = cos(angle_start) * padding
            y = sin(angle_start) * padding
            points.append(Vector((x, y)) + corner)
    points.append(points[0])
    return points

def get_unit_system_text(context, value):
    def get_absolute_metric_unit(value, unit):
        if unit == "KILOMETERS":
            return value / 1000, "km", 1000
        elif unit == "METERS":
            return value, "m", 1
        elif unit == "CENTIMETERS":
            return value / 0.01, "cm", 0.01
        elif unit == "MILLIMETERS":
            return value / 0.001, "mm", 0.001
        elif unit == "MICROMETERS":
            return value / 0.000001, "µm", 0.000001

    def get_adaptive_metric_unit(value):
        if abs(value) >= 1000:
            return get_absolute_metric_unit(value, "KILOMETERS")
        elif 1 <= abs(value) < 1000:
            return get_absolute_metric_unit(value, "METERS")
        elif 0.01 <= abs(value) < 1:
            return get_absolute_metric_unit(value, "CENTIMETERS")
        elif 0.001 <= abs(value) < 0.01:
            return get_absolute_metric_unit(value, "MILLIMETERS")
        elif abs(value) <= 0.001:
            return get_absolute_metric_unit(value, "MICROMETERS")

    def get_absolute_imperial_unit(value, unit):
        if unit == "MILES":
            return value / 5280, "mi", 5280
        elif unit == "FEET":
            return value, "'", 1
        elif unit == "INCHES":
            return value * 12, "''", 1 / 12
        elif unit == "THOU":
            return value * 12000, "thou", 1 / 12000

    def get_adaptive_imperial_unit(value):
        if abs(value) >= 5280:
            return get_absolute_imperial_unit(value, "MILES")
        elif 1 <= abs(value) < 5280:
            return get_absolute_imperial_unit(value, "FEET")
        elif 1 / 12 <= abs(value) < 1:
            return get_absolute_imperial_unit(value, "INCHES")
        elif abs(value) <= 1 / 12:
            return get_absolute_imperial_unit(value, "THOU")

    settings = context.scene.unit_settings

    if settings.system == "NONE":
        return f"{value:0.6f}"
    else:
        value *= settings.scale_length
        if settings.system == "METRIC":
            get_adaptive_unit = get_adaptive_metric_unit
            get_absolute_unit = get_absolute_metric_unit
            absolute_value = f"{value:0.6f}m"
        elif settings.system == "IMPERIAL":
            value /= 0.3048
            get_adaptive_unit = get_adaptive_imperial_unit
            get_absolute_unit = get_absolute_imperial_unit
            absolute_value = f"{value:0.6f}'"

        if settings.length_unit == "ADAPTIVE":
            value_converted, value_unit, unit_factor = get_adaptive_unit(value)
        else:
            value_converted, value_unit, unit_factor = get_absolute_unit(value, settings.length_unit)

        if settings.use_separate and value_unit not in ("µm", "thou"):
            float_part, integer_part = modf(value_converted)
            remainder = value - (integer_part * unit_factor)
            integer_value, integer_unit = integer_part, value_unit
            float_value, float_unit, float_unit_factor = get_adaptive_unit(remainder)
            relative_value = f"{int(integer_value)}{integer_unit} {float_value:0.6f}{float_unit}"
        else:
            relative_value = f"{value_converted:0.6f}{value_unit}"

        return f"{relative_value} ({absolute_value})"
