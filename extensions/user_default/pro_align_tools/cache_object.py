from .common_imports import *

from .general_functions import (apply_matrix_to_points, points_to_world_matrix, local_to_object_matrix,
                                bounds_to_matrix, get_matrix_corners, cube_size)
from .gpu_functions import create_batch_shader


def cached_objects_update(context):

    addon = context.window_manager.align_tool
    CACHE = addon.CACHE

    if "cached_objects" not in CACHE:
        CACHE["cached_objects"] = dict()

    cached_objects = CACHE["cached_objects"]
    addon.batches[0].cached_objects = CACHE["cached_objects"]

    # get current objects including the plane object if present
    current_names = get_current_objects(context)

    # check if there are new objects to add to cache
    if not set(current_names).issubset(set(cached_objects)):
        for name in current_names:
            if name not in cached_objects:
                cached_objects[name] = dict()
                update_object_cache(context, name)
            elif object_has_changed(CACHE, context, name):
                update_object_cache(context, name)
    else:
        # check if objects have changed and update its cached data if needed
        for name in current_names:
            if object_has_changed(CACHE, context, name):
                update_object_cache(context, name)


def get_current_objects(context):
    addon = context.window_manager.align_tool
    current_objects = addon.CACHE["selected_objects"].copy()
    if addon.plane_object in context.scene.objects:
        plane_object = context.scene.objects[addon.plane_object]
        if plane_object.name not in current_objects:
            current_objects.append(plane_object.name)
    elif bool(addon.plane_object):
        addon.plane_object = ""
    return current_objects


def object_has_changed(CACHE, context, object_name):

    addon = context.window_manager.align_tool

    if addon.geometry_update:
        return True

    edit_mode_types = {"MESH": "EDIT_MESH",
                       "CURVE": "EDIT_CURVE",
                       "SURFACE": "EDIT_SURFACE",
                       "FONT": "EDIT_TEXT",
                       "ARMATURE": "EDIT_ARMATURE",
                       "META": "EDIT_METABALL",
                       "LATTICE": "EDIT_LATTICE",
                       "GPENCIL": "EDIT_GPENCIL"}
    other_mode_types = {"MESH": ("SCULPT", "PAINT_WEIGHT", "PAINT_VERTEX", "PAINT_TEXTURE"),
                        "ARMATURE": ("POSE",),
                        "GPENCIL": ("SCULPT_GPENCIL", "WEIGHT_GPENCIL", "PAINT_GPENCIL")}

    cache_object = CACHE["cached_objects"][object_name]
    obj = context.scene.objects[object_name]

    # check if last mode is different than current mode
    if CACHE["mode"] != context.mode:
        # check if the object was in edit mode
        if obj.type in edit_mode_types:
            if CACHE["mode"] == edit_mode_types[obj.type]:
                return True
        # check if the active object was in another mode
        if context.object is obj:
            if obj.type in other_mode_types:
                if CACHE["mode"] in other_mode_types[obj.type]:
                    return True

    # check if modifiers had changed
    if has_outdated_modifiers(cache_object, obj):
        return True
    return False


def has_outdated_modifiers(cache_object, object):

    if "modifiers" not in cache_object:
        cache_object["modifiers"] = dict()

    outdated = False
    if len(object.modifiers) != len(cache_object["modifiers"]):
        outdated = True

    if len(object.modifiers) == 0:
        cache_object["modifiers"] = dict()

        return outdated

    CACHE_modifiers = cache_object["modifiers"]

    for modifier in object.modifiers:

        if modifier.name not in CACHE_modifiers:
            CACHE_modifiers[modifier.name] = dict()
            outdated = True

        CACHE_mod = CACHE_modifiers[modifier.name]

        for property_name in set(modifier.bl_rna.properties.keys()).difference({"type", "rna_type"}):

            modifier_property = getattr(modifier, property_name)

            if isinstance(modifier_property, bpy.types.bpy_struct):

                if property_name not in CACHE_mod:
                    CACHE_mod[property_name] = str(modifier_property)
                    outdated = True

                elif str(modifier_property) != CACHE_mod[property_name]:
                    CACHE_mod[property_name] = str(modifier_property)
                    outdated = True

            elif property_name not in CACHE_mod:
                CACHE_mod[property_name] = modifier_property
                outdated = True

            elif modifier_property != CACHE_mod[property_name]:
                CACHE_mod[property_name] = modifier_property
                outdated = True

    for CACHE_mod in set(CACHE_modifiers):

        if CACHE_mod not in object.modifiers:

            del CACHE_modifiers[CACHE_mod]

    return outdated


def update_object_cache(context, object_name):

    CACHE = context.window_manager.align_tool.CACHE
    cache_object = CACHE["cached_objects"][object_name]
    obj = context.scene.objects[object_name]

    cache_object["geometry_array"] = get_geometry_array(context, obj)
    cache_object["batch_shader"] = get_object_batch_shader(context, obj)
    cache_object["align_point"] = None


def get_geometry_array(context, obj):

    if obj.type in ("MESH", "CURVE", "SURFACE", "META", "FONT"):

        evaluated = obj.evaluated_get(context.evaluated_depsgraph_get())
        mesh = evaluated.to_mesh()
        vert_count = len(mesh.vertices)

        if vert_count > 0:

            array = np.zeros(vert_count*3, dtype=np.float32)
            mesh.vertices.foreach_get('co', array)
            array.shape = (vert_count, 3)
            evaluated.to_mesh_clear()

            return array

        evaluated.to_mesh_clear()

    return None


def get_object_batch_shader(context, object):
    CACHE = context.window_manager.align_tool.CACHE
    cache_object = CACHE["cached_objects"][object.name]
    if cache_object["geometry_array"] is not None:
        vertices_stream = cache_object["geometry_array"]
        evaluated = object.evaluated_get(context.evaluated_depsgraph_get())
        mesh = evaluated.to_mesh()

        if mesh.polygons:
            mesh.calc_loop_triangles()
            triangles_count = len(mesh.loop_triangles)
            indices_array = np.zeros(triangles_count*3, dtype=np.int32)
            mesh.loop_triangles.foreach_get("vertices", indices_array)
            indices_array.shape = (triangles_count, 3)
            batch_shader = (*create_batch_shader("TRIANGLES", vertices_stream, indices_array), "TRIANGLES")
        elif mesh.edges:
            edges_count = len(mesh.edges)
            indices_array = np.zeros(edges_count*2, dtype=np.int32)
            mesh.edges.foreach_get("vertices", indices_array)
            indices_array.shape = (edges_count, 2)
            batch_shader = (*create_batch_shader("LINES", vertices_stream, indices_array), "LINES")
        else:
            batch_shader = (*create_batch_shader("POINTS", vertices_stream), "POINTS")

        mesh = evaluated.to_mesh_clear()
        return batch_shader
    return None


def add_object_boxes(context):
    CACHE = context.window_manager.align_tool.CACHE
    for name in get_current_objects(context):
        ob = context.scene.objects[name]
        CACHE["cached_objects"][ob.name]["boxes"] = get_boxes(context, ob)


def get_boxes(context, obj):

    local_matrix = local_to_object_matrix(obj)
    bounds_world_space = apply_matrix_to_points(obj.bound_box, obj.matrix_world)
    world_matrix = points_to_world_matrix(bounds_world_space)
    world_geometry_matrix = world_matrix

    if cube_size(local_matrix) > 0:

        if obj.type in ("MESH", "CURVE", "SURFACE", "META", "FONT"):

            world_geometry_matrix = array_to_world_matrix(context, obj)

    return {"local": local_matrix,
            "world": world_matrix,
            "world_geometry": world_geometry_matrix}


def array_to_world_matrix(context, object, matrix=None):
    array = context.window_manager.align_tool.CACHE["cached_objects"][object.name]["geometry_array"]
    if array is not None:
        base_matrix = (object.matrix_world if matrix is None else matrix).to_3x3().transposed() # a 3x3 matrix contains rotation and scale information
        translation = object.matrix_world.to_translation() if matrix is None else matrix.to_translation()
        return Matrix.Translation(translation) @ points_to_world_matrix(array @ base_matrix)
    return None


def add_perpendicular_boxes(context):
    CACHE = context.window_manager.align_tool.CACHE

    def get_perpendicular_matrix(object=None, points=None):
        plane = CACHE["plane"]
        if plane is None:
            return None
        if object is None:
            plane_space_points = apply_matrix_to_points(points, plane.inverted())
            world_matrix = points_to_world_matrix(plane_space_points)
        else:
            cache_object = CACHE["cached_objects"][object.name]
            plane_space = plane.inverted() @ object.matrix_world
            if cache_object["geometry_array"] is not None:
                world_matrix = array_to_world_matrix(context, object, matrix=plane_space)
            else:
                world_matrix = plane_space @ bounds_to_matrix(object.bound_box)
        return plane @ world_matrix

    cached_objects = CACHE["cached_objects"]

    perpendicular_points = []
    for name in CACHE["selected_objects"]:
        cache_object = cached_objects[name]
        ob = context.scene.objects[name]
        perpendicular_matrix = get_perpendicular_matrix(object=ob)
        cache_object["boxes"]["perpendicular"] = perpendicular_matrix
        if perpendicular_matrix is not None:
            perpendicular_points.extend(get_matrix_corners(perpendicular_matrix))

    CACHE["selection_bounds"]["perpendicular"] = get_perpendicular_matrix(points=perpendicular_points) if perpendicular_points else None
