from .common_imports import *

from .cache_functions import (get_selected_objects, get_selection_bounds,
                              custom_origin_update, get_plane, get_projection_lines,
                              get_projected_points, get_view_rotation)
from .cache_object import (add_object_boxes, add_perpendicular_boxes, cached_objects_update)
from .context_functions import (get_header_text, delete_custom_origin,
                                delete_custom_plane, align_tool_selected)


# -- Cache system --

def CACHE_update(context):

    addon = context.window_manager.align_tool
    CACHE = addon.CACHE
    custom_origin_update(context)
    CACHE["view_rotation"] = get_view_rotation(context)

    # the running_modal flag prevents a problem with child objects being deselected when moving/rotating/scaling
    # if not addon.running_modal:
    # Shift+D conflicts this making it useless
    CACHE["selected_objects"] = get_selected_objects(context)

    cached_objects_update(context)
    add_object_boxes(context)
    CACHE["mode"] = context.mode
    CACHE["selection_bounds"] = get_selection_bounds(context)
    CACHE["plane"] = get_plane(context)
    add_perpendicular_boxes(context)
    CACHE["projection_lines"] = get_projection_lines(context)
    CACHE["projected_points"] = get_projected_points(CACHE["projection_lines"])


    if align_tool_selected(context, mode="OBJECT"):

        context.workspace.status_text_set(get_header_text(context))

    else:

        context.workspace.status_text_set(None)


def CACHE_view_update(context):
    CACHE = context.window_manager.align_tool.CACHE
    CACHE["view_rotation"] = get_view_rotation(context)
    CACHE["plane"] = get_plane(context)
    add_perpendicular_boxes(context)
    CACHE["projection_lines"] = get_projection_lines(context)
    CACHE["projected_points"] = get_projected_points(CACHE["projection_lines"])


def CACHE_undo_check(scene):

    addon = bpy.context.window_manager.align_tool
    original_state = addon.geometry_update

    # this triggers a CACHE_update
    addon.geometry_update = True
    addon.geometry_update = original_state


def CACHE_clear(scene=None):

    addon = bpy.context.window_manager.align_tool
    addon.gizmo_group_instances.clear()

    if addon.draw_handler_2D:

        bpy.types.SpaceView3D.draw_handler_remove(addon.draw_handler_2D[0], "WINDOW")
        addon.draw_handler_2D.clear()
        addon.mouse_panel_fill_batch.clear()
        addon.mouse_panel_outline_batch.clear()
        addon.shortcuts_panel_fill_batch.clear()
        addon.shortcuts_panel_outline_batch.clear()

    addon.CACHE.clear()
    addon.batches[0].clear()
    addon.drag_star.clear()
    addon.drag_star_shadow.clear()


def CACHE_depsgraph_check(scene):

    addon = bpy.context.window_manager.align_tool

    instances_status = (True not in ("invalid" in str(group), area.type != "VIEW_3D") for area, group in addon.gizmo_group_instances)
    no_active_instance = True not in instances_status

    if no_active_instance:
        addon.gizmo_group_instances.clear()

        cache_is_clearable = (not align_tool_selected(bpy.context, mode="OBJECT") and
                              not align_tool_selected(bpy.context, mode="EDIT_MESH"))

        if cache_is_clearable:

            delete_custom_origin(bpy.context)
            delete_custom_plane(bpy.context)
            bpy.context.workspace.status_text_set(None)

            CACHE_clear()

            if CACHE_depsgraph_check in bpy.app.handlers.depsgraph_update_post:
                bpy.app.handlers.depsgraph_update_post.remove(CACHE_depsgraph_check)

            if CACHE_undo_check in bpy.app.handlers.undo_post:
                bpy.app.handlers.undo_post.remove(CACHE_undo_check)

            if CACHE_clear in bpy.app.handlers.load_pre:
                bpy.app.handlers.load_pre.remove(CACHE_clear)

    if bool(addon.CACHE) and addon.update_available:
        CACHE_update(bpy.context)
