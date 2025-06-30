from .common_imports import *

from .general_functions import (points_to_world_matrix, get_object_rotation,
                                project_to_plane, get_matrix_corners, matrix_to_point,
                                apply_matrix_to_points)
from .context_functions import (get_current_orientation_matrix, get_plane_type,
                                get_origin_type, delete_custom_origin, get_plane_individual_object)
from .cache_object import array_to_world_matrix


def add_children_to_list(obj, objects_list):
    for child in obj.children:
        if child.select_get() and child not in objects_list:
            objects_list.append(child)
        add_children_to_list(child, objects_list)

def get_selected_objects(context):
    if hasattr(context, "selected_objects"):

        selected_objects = context.selected_objects.copy()

        for ob in selected_objects.copy():

            add_children_to_list(ob, selected_objects)

        return [ob.name for ob in selected_objects]

    return []

def get_view_rotation(context):
    if context.region_data is not None:
        if hasattr(context.region_data, "view_rotation"):
            return context.region_data.view_rotation.copy()
    if "view_rotation" in context.window_manager.align_tool.CACHE:
        return context.window_manager.align_tool.CACHE["view_rotation"]
    return None


def get_selection_bounds(context):

    CACHE = context.window_manager.align_tool.CACHE
    active_object_matrix = None
    cloud_world_points = []
    cloud_world_geometry_points = []
    cloud_local_points = []
    cloud_local_geometry_points = []

    if CACHE["selected_objects"]:

        if context.object is not None:
            invertible = 0 not in context.object.matrix_world.to_scale()

            if invertible:
                active_object_matrix = context.object.matrix_world

        for name in CACHE["selected_objects"]:

            cache_object = CACHE["cached_objects"][name]

            obj_world_corners = get_matrix_corners(cache_object["boxes"]["world"])
            cloud_world_points.extend(obj_world_corners)

            obj_world_geometry_corners = get_matrix_corners(cache_object["boxes"]["world_geometry"])
            cloud_world_geometry_points.extend(obj_world_geometry_corners)

            if active_object_matrix is not None:
                obj = context.scene.objects[name]
                local_space = active_object_matrix.inverted() @ obj.matrix_world

                obj_bounds = apply_matrix_to_points(obj.bound_box, local_space)
                cloud_local_points.extend(obj_bounds)

                if cache_object["geometry_array"] is not None:
                    array_matrix = array_to_world_matrix(context, obj, matrix=local_space)
                    obj_geometry_array_corners = get_matrix_corners(array_matrix)
                    cloud_local_geometry_points.extend(obj_geometry_array_corners)


    matrix_world = matrix_world_geometry = matrix_local = matrix_local_geometry = None

    if cloud_world_points:
        matrix_world = points_to_world_matrix(cloud_world_points)

    if cloud_world_geometry_points:
        matrix_world_geometry = points_to_world_matrix(cloud_world_geometry_points)

    if cloud_local_points:
        matrix_local = active_object_matrix @ points_to_world_matrix(cloud_local_points)

    if cloud_local_geometry_points:
        matrix_local_geometry = active_object_matrix @ points_to_world_matrix(cloud_local_geometry_points)

    return {"world": matrix_world,
            "geometry": matrix_world_geometry,
            "local": matrix_local,
            "local_geometry": matrix_local_geometry}


def get_object_rotation_matrix(object):
    if object.parent is not None:
        return object.parent.matrix_world.to_3x3() @ object.matrix_parent_inverse.to_3x3() @ get_object_rotation(object).to_matrix()
    else:
        return get_object_rotation(object).to_matrix()

def custom_origin_update(context):

    CACHE = context.window_manager.align_tool.CACHE

    if "custom_origin" in CACHE:

        origin = CACHE["custom_origin"]

        if origin["object"] in context.scene.objects:

            obj = context.scene.objects[origin["object"]]

            if context.mode == "EDIT_MESH" and obj.name == context.object.name:
                bm = bmesh.from_edit_mesh(obj.data)
                bm.verts.ensure_lookup_table()
                origin["co"] = obj.matrix_world @ bm.verts[origin["index"]].co.copy()

            else:
                evaluated = obj.evaluated_get(context.evaluated_depsgraph_get())
                origin["co"] = obj.matrix_world @ evaluated.data.vertices[origin["index"]].co.copy()

        else:
            delete_custom_origin(context)

def heal_and_offset_matrix(matrix, plane_axis="X", fallback_matrix=Matrix(), scale=0.2):
    fallback_matrix = fallback_matrix.to_3x3() @ Matrix.Scale(scale, 3)
    origin = matrix.to_translation()
    x, y, z = matrix.to_3x3().col
    if x.length == 0 and plane_axis in ("Y", "Z"):
        x = fallback_matrix.col[0]
        origin -= x / 2
    if y.length == 0 and plane_axis in ("X", "Z"):
        y = fallback_matrix.col[1]
        origin -= y / 2
    if z.length == 0 and plane_axis in ("X", "Y"):
        z = fallback_matrix.col[2]
        origin -= z / 2
    return Matrix.Translation(origin) @ Matrix([x, y, z]).transposed().to_4x4()

def get_plane(context):

    addon = context.window_manager.align_tool
    CACHE = addon.CACHE

    if addon.drag_star:
        star = addon.drag_star[0]
        x, y, z = star.matrix_drag.to_3x3().normalized().col
        up = (x, y, z)[star.axes[0].index]
        axes = [x, y, z]
        axes.remove(up)

        rotation_star_matrix = Matrix([*axes, up]).transposed().to_4x4()
        location_star_matrix = Matrix.Translation(star.location)

        return location_star_matrix @ rotation_star_matrix


    plane_type = get_plane_type(context)

    if plane_type == "WORLD":

        plane_matrix = get_current_orientation_matrix(context)

    elif plane_type == "CURSOR":

        cursor_matrix = context.scene.cursor.matrix.copy()
        translation_matrix = Matrix.Translation(context.scene.cursor.location)
        orientation_matrix = get_current_orientation_matrix(context, cursor_matrix)
        plane_matrix = translation_matrix @ orientation_matrix

    elif plane_type in ("OBJECT_LOCATION_PLANE",
                        "OBJECT_LOCATION",
                        "OBJECT_BOUNDS_PLANE",
                        "OBJECT_BOUNDS_ACTIVE"):

        individual_object = get_plane_individual_object(context)

        if individual_object is None:

            return None

        if plane_type in ("OBJECT_LOCATION_PLANE",
                          "OBJECT_LOCATION"):

            object_matrix = individual_object.matrix_world.copy()
            translation_matrix = Matrix.Translation(object_matrix.to_translation())
            orientation_matrix = get_current_orientation_matrix(context, object_matrix)
            plane_matrix = translation_matrix @ orientation_matrix

        elif plane_type in ("OBJECT_BOUNDS_PLANE",
                            "OBJECT_BOUNDS_ACTIVE"):

            cached_object = CACHE["cached_objects"][individual_object.name]

            if addon.plane_use_local:
                box_matrix = cached_object["boxes"]["local"]
                rotation_matrix = get_object_rotation_matrix(individual_object)
                plane_matrix = heal_and_offset_matrix(box_matrix, addon.plane_axis, rotation_matrix)

            else:
                if addon.plane_use_geometry:
                    box_matrix = cached_object["boxes"]["world_geometry"]
                else:
                    box_matrix = cached_object["boxes"]["world"]

                plane_matrix = heal_and_offset_matrix(box_matrix, addon.plane_axis)

            axis_index = ("X", "Y", "Z").index(addon.plane_axis)
            depth = (0, 0.5, 1)[("MIN", "CENTER", "MAX").index(addon.plane_depth)]
            depth_translation = Matrix.Translation(box_matrix.col[axis_index].to_3d() * depth)
            plane_matrix = depth_translation @ plane_matrix

    elif plane_type == "OBJECT_BOUNDS_SELECTED":

        if not bool(CACHE["selected_objects"]):

            return None

        if addon.plane_use_local:

            if addon.plane_use_geometry:
                box_matrix = CACHE["selection_bounds"]["local_geometry"]
            else:
                box_matrix = CACHE["selection_bounds"]["local"]

        else:

            if addon.plane_use_geometry:
                box_matrix = CACHE["selection_bounds"]["geometry"]
            else:
                box_matrix = CACHE["selection_bounds"]["world"]

        plane_matrix = heal_and_offset_matrix(box_matrix, addon.plane_axis)
        axis_index = ("X", "Y", "Z").index(addon.plane_axis)
        depth = (0, 0.5, 1)[("MIN", "CENTER", "MAX").index(addon.plane_depth)]
        depth_translation = Matrix.Translation(box_matrix.col[axis_index].to_3d() * depth)
        plane_matrix = depth_translation @ plane_matrix


    x, y, z = plane_matrix.to_3x3().col
    horizontal, vertical = ((y, z), (z, x), (x, y))[("X", "Y", "Z").index(addon.plane_axis)]
    up = horizontal.cross(vertical)

    if up != Vector():
        new_matrix = Matrix([horizontal, vertical, up]).transposed().to_4x4()

        return Matrix.Translation(plane_matrix.to_translation()) @ new_matrix

    return None

def get_projection_lines(context):

    addon = context.window_manager.align_tool
    CACHE = addon.CACHE
    selected_objects = CACHE["selected_objects"]
    cached_objects = CACHE["cached_objects"]
    selection_bounds = CACHE["selection_bounds"]
    plane = CACHE["plane"]
    projections = []

    def objects_to_projections(objects_list, start_point):

        if objects_list:

            for name in objects_list:

                obj = context.scene.objects[name]
                cached_object = cached_objects[name]

                position = obj.matrix_world.to_translation()
                projection = get_projection(context, obj, start_point, plane)

                if projection is not None:

                    cached_object["align_point"] = projection + (position - start_point)

                else:

                    cached_object["align_point"] = None


                if not projections:

                    projections.append((start_point, projection, [name]))

                else:

                    if projection == projections[-1][1]:

                        projections[-1][2].append(name)

                    else:

                        projections.append((start_point, projection, [name]))


    origin_type = get_origin_type(context)

    if origin_type in ("WORLD", "CURSOR"):

        if origin_type == "WORLD":
            origin = Vector()
        else:
            origin = context.scene.cursor.location.copy()

        objects_to_projections(selected_objects, origin)

    elif origin_type == "CUSTOM":

        origin = CACHE["custom_origin"]["co"]

        if origin is not None:

            objects_to_projections(selected_objects, origin)

    elif origin_type == "OBJECTS_LOCATION":

        for name in selected_objects:

            origin = context.scene.objects[name].matrix_world.to_translation()
            objects_to_projections([name], origin)

    elif origin_type == "OBJECTS_BOUNDS":

        if addon.origin_use_local:

            for name in selected_objects:

                box_matrix = cached_objects[name]["boxes"]["local"]
                origin = matrix_to_point(box_matrix,
                                         addon.origin_depth_X,
                                         addon.origin_depth_Y,
                                         addon.origin_depth_Z)
                objects_to_projections([name], origin)

        elif addon.origin_all_selected:

            box_type = "perpendicular" if addon.origin_use_geometry else "world"
            box_matrix = selection_bounds[box_type]

            if box_matrix is None:
                origin = None

            else:
                origin = matrix_to_point(box_matrix,
                                         addon.origin_depth_X,
                                         addon.origin_depth_Y,
                                         addon.origin_depth_Z)

            objects_to_projections(selected_objects, origin)

        else:

            for name in selected_objects:

                box_type = "perpendicular" if addon.origin_use_geometry else "world"
                box_matrix = cached_objects[name]["boxes"][box_type]

                if box_matrix is not None:

                    origin = matrix_to_point(box_matrix,
                                             addon.origin_depth_X,
                                             addon.origin_depth_Y,
                                             addon.origin_depth_Z)
                    objects_to_projections([name], origin)

    return projections


def get_projection(context, obj, origin_point, plane):

    if not plane:
        return None

    if obj is not None:
        if obj.parent is not None:
            try:
                obj.parent.matrix_world.inverted()
            except ValueError:
                return None

    direction = get_direction(context, obj, plane)
    if not direction:
        return None

    if isclose(direction.dot(plane.to_3x3().col[2]), 0, abs_tol=0.00001):
        return None

    return project_to_plane(plane, origin_point, direction)


def get_direction(context, obj, plane):

    addon = context.window_manager.align_tool
    direction_matrix = Matrix().to_3x3()

    if addon.direction_custom_orientation == "LOCAL":

        if addon.direction_reference == "ACTIVE":

            if context.object is None:

                return None

            direction_object = context.object

        elif addon.direction_reference == "INDIVIDUAL":

            all_as_group = (addon.origin_target == "OBJECTS"
                            and addon.origin_type == "BOUNDS"
                            and not addon.origin_use_local
                            and addon.origin_all_selected)

            if all_as_group:

                if context.object is None:

                    return None

                direction_object = context.object

            else:

                if obj is None:

                    return None

                direction_object = obj

        direction_matrix = get_object_rotation_matrix(direction_object)

    elif addon.direction_custom_orientation == "VIEW":

        if addon.CACHE["view_rotation"] is None:

            return None

        direction_matrix = addon.CACHE["view_rotation"].to_matrix()

    elif addon.direction_custom_orientation == "PERPENDICULAR":

        return plane.to_3x3().col[2]

    elif addon.direction_custom_orientation == "CUSTOM":

        orientations = context.scene.transform_orientation_slots[0]

        if orientations.custom_orientation is not None:

            direction_matrix = orientations.custom_orientation.matrix

    return direction_matrix.col[("X", "Y", "Z").index(addon.direction_axis)]


def get_projected_points(projection_lines):
    return [projection[1] for projection in projection_lines if projection[1] is not None]
