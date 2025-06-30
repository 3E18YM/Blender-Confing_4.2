from .common_imports import *

from .cache_system import CACHE_update, CACHE_view_update
from .context_functions import (get_mouse_vector_ratio, get_mouse_in_region,
                                redraw_3dviews, get_unit_system_text,
                                delete_custom_origin, delete_custom_plane)
from .general_functions import numpy_get_selected_verts_co
from .widgets import grid_point, star
from .context_functions import get_rounded_rectangle, align_tool_selected
from .draw_functions import get_text_size, draw_text
from .gpu_functions import create_batch_shader, draw_batch_shader


# -- Main Operators --

class ALIGNTOOL_OT_align_objects(Operator):

    bl_idname = "proaligntools.align_objects"
    bl_label = "Align Objects"
    bl_description = "Align selected objects"
    bl_options = {"REGISTER", "UNDO"}


    @classmethod
    def poll(cls, context):

        #context.mode == "EDIT_MESH" and "align_tool.tool_edit" in context.workspace.tools

        if align_tool_selected(context, mode="OBJECT"):

            if context.selected_objects:

                return True

        return False


    def invoke(self, context, event):

        CACHE_update(context)
        self.execute(context)

        return {"FINISHED"}


    def execute(self, context):

        addon = context.window_manager.align_tool
        CACHE = addon.CACHE

        def get_root_object(object_name):

            obj = context.scene.objects[object_name]

            if obj.parent is not None:

                return get_root_object(obj.parent.name)

            return obj


        def move_object(context, obj):

            align_point = CACHE["cached_objects"][obj.name]["align_point"]

            if align_point is not None:

                depsgraph = context.evaluated_depsgraph_get()
                depsgraph.update()
                position = obj.matrix_world.to_translation()

                if obj.parent is not None:

                    parent_matrix = (obj.parent.matrix_world.to_3x3() @ obj.matrix_parent_inverse.to_3x3()).to_4x4()
                    translation_matrix = Matrix.Translation(obj.matrix_world.to_translation())
                    inverse_matrix = (translation_matrix @ parent_matrix).inverted()
                    #inverse_matrix = obj.matrix_basis.to_3x3().to_4x4() @ obj.matrix_world.inverted()
                    obj.location += (inverse_matrix @ align_point) - (inverse_matrix @ position)

                else:

                    obj.location += align_point - position


        def move_childs(context, obj):

            for child in obj.children:

                if child.select_get():

                    move_object(context, child)

                move_childs(context, child)


        root_objects = set()

        for name in CACHE["selected_objects"]:
            root_objects.add(get_root_object(name))

        addon.update_available = False
        for ob in root_objects:

            if ob.select_get():
                move_object(context, ob)

            move_childs(context, ob)

        addon.update_available = True

        return {"FINISHED"}


class ALIGNTOOL_OT_shortcuts_handler(Operator):

    bl_idname = "proaligntools.shortcuts_handler"
    bl_label = "Handle shortcuts"
    bl_options = {'REGISTER', 'INTERNAL'}

    @classmethod
    def poll(cls, context):

        return align_tool_selected(context)


    def invoke(self, context, event):

        def is_object_context():

            if context.area.type == "VIEW_3D":

                if context.area.spaces[0].show_gizmo:

                    mouse_in_region = get_mouse_in_region(context.region, event)

                    if mouse_in_region:

                        if context.mode == "OBJECT":

                            return True

            return False


        addon = context.window_manager.align_tool

        if is_object_context():

            if event.value == "PRESS":

                if event.type in ("X", "Y", "Z"):

                    if event.shift:

                        addon.plane_axis = event.type

                        return {"FINISHED"}

                    if not event.ctrl and not event.alt:

                        addon.direction_axis = event.type

                        if addon.direction_custom_orientation == "PERPENDICULAR":

                            addon.direction_custom_orientation = "GLOBAL"

                        return {"FINISHED"}

                elif event.type in ("L", "V", "P"):

                    if not event.ctrl and not event.shift and not event.alt:

                        orientation_index = ("L", "V", "P").index(event.type)
                        orientation = ("LOCAL", "VIEW", "PERPENDICULAR")[orientation_index]

                        if addon.direction_custom_orientation == orientation:

                            addon.direction_custom_orientation = "GLOBAL"

                        else:

                            addon.direction_custom_orientation = orientation

                        return {"FINISHED"}

                elif event.type == "G":

                    if event.shift:

                        addon.plane_use_geometry = not addon.plane_use_geometry

                        return {"FINISHED"}

                    if event.ctrl:

                        addon.origin_use_geometry = not addon.origin_use_geometry

                        return {"FINISHED"}

                elif event.type == "O":

                    if not event.ctrl and not event.shift and not event.alt:

                        addon.origin_all_selected = not addon.origin_all_selected

                        return {"FINISHED"}

                elif event.type in {"WHEELUPMOUSE", "WHEELDOWNMOUSE"}:

                    if not event.ctrl and event.alt:

                        orientations = ("GLOBAL", "LOCAL", "VIEW", "CUSTOM")
                        current_orientation_index = orientations.index(addon.plane_orientation)
                        offset = 1 if event.type == "WHEELUPMOUSE" else -1
                        orientation_index = (current_orientation_index + offset) % 4
                        addon.plane_orientation = orientations[orientation_index]

                        return {"FINISHED"}


        if event.type == "D" and event.value == "PRESS":

            if not event.ctrl and not event.shift and not event.alt:

                context.area.spaces[0].show_gizmo ^= True

                if context.area.spaces[0].show_gizmo:
                    original_state = addon.geometry_update
                    addon.geometry_update = True
                    addon.geometry_update = original_state

                return {"FINISHED"}


        return {"PASS_THROUGH"}


class ALIGNTOOL_OT_set_origin(Operator):

    bl_idname = "proaligntools.set_origin"
    bl_label = "Set Custom Origin"
    bl_description = "Set a Custom Origin from active vertex"
    bl_options = {"REGISTER", "INTERNAL"}


    @classmethod
    def poll(cls, context):

        if context.object.type == "MESH":
            return context.tool_settings.mesh_select_mode[0]

        return False


    def execute(self, context):

        addon = context.window_manager.align_tool
        obj = context.object

        bm = bmesh.from_edit_mesh(obj.data)
        bm.verts.ensure_lookup_table()

        if not bool(bm.select_history):

            self.report({'WARNING'}, "Need an active vertex to set a Custom Origin.")

        elif isinstance(bm.select_history[-1], bmesh.types.BMVert):

            vert = bm.select_history[-1]
            addon.CACHE["custom_origin"] = {"object": obj.name,
                                            "index": vert.index,
                                            "co": obj.matrix_world @ vert.co.copy(),
                                            "point": grid_point("ORIGIN")}
            addon.origin_target = "OBJECTS"
            addon.origin_type = "CUSTOM"

            return {"FINISHED"}

        return {"CANCELLED"}


class ALIGNTOOL_OT_delete_origin(Operator):

    bl_idname = "proaligntools.delete_origin"
    bl_label = "Remove"
    bl_description = "Remove origin point"
    bl_options = {"REGISTER", "INTERNAL"}


    @classmethod
    def poll(cls, context):

        return "custom_origin" in context.window_manager.align_tool.CACHE


    def execute(self, context):

        delete_custom_origin(context)

        return {"FINISHED"}


class ALIGNTOOL_OT_set_plane(Operator):

    bl_idname = "proaligntools.set_plane"
    bl_label = "Set Custom Plane"
    bl_description = "Set a Custom Plane from current selected geometry"
    bl_options = {"REGISTER", "INTERNAL"}


    @classmethod
    def poll(cls, context):

        return context.object.type == "MESH"


    def invoke(self, context, event):

        addon = context.window_manager.align_tool
        obj = context.object

        selected_verts = numpy_get_selected_verts_co(obj)

        if selected_verts.size == 0:

            self.report({'WARNING'}, "Need something selected to set a Custom Plane.")

        else:

            bpy.ops.transform.create_orientation(name="__align_tool__", overwrite=True)

            orientations = context.scene.transform_orientation_slots
            orientations[0].type = "__align_tool__"
            custom_orientation = orientations[0].custom_orientation

            if custom_orientation is not None:

                normal = custom_orientation.matrix.col[2]
                rotation_matrix = normal.to_track_quat("Z", "Y").to_matrix().to_4x4()

                selection_center = obj.matrix_world @ Vector(selected_verts.mean(0))
                translation_matrix = Matrix.Translation(selection_center)

                normal_matrix = translation_matrix @ rotation_matrix

                normal_star = star(box=None, box_type="ACTIVE", matrix=Matrix(), index=0)
                normal_star.axes[:] = [axis for axis in normal_star.axes if axis.index == 2]
                normal_star.apply_matrix_drag(context, event, normal_matrix)

                addon.drag_star[:] = [normal_star]

                CACHE_update(context)

                bpy.ops.transform.delete_orientation("EXEC_DEFAULT")

                addon.plane_target = "CUSTOM"

                return {"FINISHED"}

            else:

                self.report({'WARNING'}, "Cannot set a Custom Plane for your current selection. "
                                            "Try selecting something else.")

        return {"CANCELLED"}


class ALIGNTOOL_OT_delete_plane(Operator):

    bl_idname = "proaligntools.delete_plane"
    bl_label = "Remove"
    bl_description = "Remove custom plane"
    bl_options = {"REGISTER", "INTERNAL"}


    @classmethod
    def poll(cls, context):

        return bool(context.window_manager.align_tool.drag_star)


    def execute(self, context):

        delete_custom_plane(context)

        return {"FINISHED"}


class ALIGNTOOL_OT_pick_plane(Operator):

    bl_idname = "proaligntools.pick_plane"
    bl_label = "Pick a Custom Plane by pointing an Object"
    bl_options = {'REGISTER', 'INTERNAL'}

    @classmethod
    def poll(cls, context):

        return align_tool_selected(context, mode="OBJECT")


    def invoke(self, context, event):

        if context.area.type == "VIEW_3D":

            context.window.cursor_modal_set("EYEDROPPER")

            draw_handler_add = bpy.types.SpaceView3D.draw_handler_add
            self.draw_handler = draw_handler_add(self.textbox_draw, (context, event), "WINDOW", "POST_PIXEL")
            context.window_manager.align_tool.running_modal = True

            context.window_manager.modal_handler_add(self)

            return {"RUNNING_MODAL"}

        return {"CANCELLED"}


    def textbox_draw(self, context, event):

        if hasattr(self, "textbox_text"):

            ui_scale = context.preferences.system.ui_scale
            region = context.region
            self.panel_height = 14 * ui_scale

            update_batch = False

            if hasattr(self, "textbox_batch"):

                if self.textbox_text != self.textbox_batch[0]:

                    update_batch = True

            else:

                update_batch = True


            if update_batch:

                self.padding = 4 * ui_scale
                text_size = get_text_size(text=self.textbox_text, size=int(11 * ui_scale))
                self.panel_width = text_size[0] + (self.padding*2)

                rectangle = get_rounded_rectangle(self.panel_width, self.panel_height, padding=self.padding)
                rectangle = [p.to_3d() for p in rectangle]
                self.textbox_batch = (self.textbox_text, create_batch_shader("TRIANGLES", rectangle))


            text_origin = self.mouse + Vector((0, 20 * ui_scale))
            origin_matrix = Matrix.Translation(text_origin.to_3d())
            gpu_blend = gpu.state.blend_get()
            gpu.state.blend_set("ALPHA")
            draw_batch_shader(self.textbox_batch[1], (0, 0, 0, 0.4), origin_matrix)
            gpu.state.blend_set(gpu_blend)


            padding_offset = Vector((self.padding, self.padding))
            text1 = "Plane Object: "

            if self.result:

                text_size = draw_text(text=text1, size=int(11 * ui_scale), color=(1, 1, 1, 1),
                          h_alignment="LEFT",
                          v_alignment="BOTTOM",
                          frame=Vector((self.panel_width, self.panel_height)),
                          origin=text_origin + padding_offset)

                remaining_text = self.textbox_text.split(text1)[1]
                text_index = remaining_text.index("(")
                text2, text3 = remaining_text[:text_index], remaining_text[text_index:]

                text_size2 = draw_text(text=text2, size=int(11 * ui_scale), color=(0, 1, 0, 1),
                          h_alignment="LEFT",
                          v_alignment="BOTTOM",
                          frame=Vector((self.panel_width, self.panel_height)),
                          origin=text_origin + padding_offset + Vector((text_size[0], 0)))

                draw_text(text=text3, size=int(11 * ui_scale), color=(1, 1, 1, 1),
                          h_alignment="LEFT",
                          v_alignment="BOTTOM",
                          frame=Vector((self.panel_width, self.panel_height)),
                          origin=text_origin + padding_offset + Vector((text_size[0] + text_size2[0], 0)))

            else:

                text_size = draw_text(text=text1, size=int(11 * ui_scale), color=(1, 1, 1, 1),
                                      h_alignment="LEFT",
                                      v_alignment="BOTTOM",
                                      frame=Vector((self.panel_width, self.panel_height)),
                                      origin=text_origin + padding_offset)

                draw_text(text="Clear", size=int(11 * ui_scale), color=(1, 0.2, 0.2, 1),
                          h_alignment="LEFT",
                          v_alignment="BOTTOM",
                          frame=Vector((self.panel_width, self.panel_height)),
                          origin=text_origin + padding_offset + Vector((text_size[0], 0)))


    def modal(self, context, event):

        def clean():

            context.window.cursor_modal_restore()
            bpy.types.SpaceView3D.draw_handler_remove(self.draw_handler, "WINDOW")
            context.area.tag_redraw()
            addon.running_modal = False


        addon = context.window_manager.align_tool

        region = context.region
        rv3d = context.region_data
        self.mouse = Vector((event.mouse_x - region.x, event.mouse_y - region.y))

        origin = reg2d_to_orig3d(region, rv3d, self.mouse)
        direction = reg2d_to_vec3d(region, rv3d, self.mouse)
        self.result, location, normal, index, obj, matrix = context.scene.ray_cast(context.view_layer.depsgraph, origin, direction)


        if self.result:

            self.textbox_text = f"Plane Object: {obj.name} (Face: {index})"

        else:

            self.textbox_text = "Plane Object: Clear"


        if event.value == "PRESS":

            if event.type in {"LEFTMOUSE", "RET", "SPACE"}:

                if self.result:

                    addon.plane_target = "CUSTOM"
                    addon.plane_object = obj.name

                    rotation_matrix = normal.to_track_quat("Z", "Y").to_matrix().to_4x4()
                    translation_matrix = Matrix.Translation(location)

                    normal_matrix = translation_matrix @ rotation_matrix

                    normal_star = star(box=None, box_type="ACTIVE", matrix=Matrix(), index=0)
                    normal_star.axes[:] = [axis for axis in normal_star.axes if axis.index == 2]
                    normal_star.apply_matrix_drag(context, event, normal_matrix)

                    addon.drag_star[:] = [normal_star]

                    CACHE_view_update(context)

                else:

                    addon.plane_object = ""
                    delete_custom_plane(context)

                clean()

                # addon.running_modal = True # horrible hack to prevent freeze drawing

                return {"FINISHED"}


            elif event.type in {"ESC", "RIGHTMOUSE"}:

                clean()

                return {"CANCELLED"}


        context.area.tag_redraw()

        return {"RUNNING_MODAL"}


class DummyEvent:
    """
    Ugly workaround to make persistent the elements required from an Event object.
    Update from Event whenever possible.
    """

    def __init__(self):

        self.mouse_x = 0
        self.mouse_y = 0
        self.type = ""
        self.value = ""
        self.ctrl = False
        self.alt = False
        self.shift = False
        self.oskey = False


    def update(self, event):

        self.mouse_x = event.mouse_x
        self.mouse_y = event.mouse_y
        self.type = event.type
        self.value = event.value
        self.ctrl = event.ctrl
        self.alt = event.alt
        self.shift = event.shift
        self.oskey = event.oskey

dummy_event = DummyEvent()

def update_dummy_event(context, event):

    addon = context.window_manager.align_tool

    try:

        if addon.current_gizmo:

            d_event = getattr(addon.current_gizmo[0], "event")
            d_event.update(event)

    except ReferenceError:

        pass


class ALIGNTOOL_OT_add_event_to_current_gizmo(Operator):

    bl_idname = "proaligntools.add_event_to_current_gizmo"
    bl_label = "Add an Event object to current gizmo instance"
    bl_options = {'REGISTER', 'INTERNAL'}


    def invoke(self, context, event):

        # context.window_manager.align_tool.current_gizmo[0].event = event
        context.window_manager.align_tool.current_gizmo[0].event = dummy_event

        return {"FINISHED"}


class ALIGNTOOL_OT_click_handler(Operator):

    bl_idname = "proaligntools.click_handler"
    bl_label = "Click handler"
    bl_options = {'REGISTER', 'INTERNAL'}

    @classmethod
    def poll(cls, context):

        return align_tool_selected(context)


    def invoke(self, context, event):

        wm = context.window_manager

        if context.area.type == "VIEW_3D":

            addon = wm.align_tool

            if event.type == "LEFTMOUSE" and event.value == "PRESS":

                mouse_in_shortcuts_button = False

                for region_dict in addon.region_dicts:

                    if region_dict["mouse_in_shortcuts_button"]:

                        mouse_in_shortcuts_button = True

                if mouse_in_shortcuts_button:

                    addon.show_shortcuts_help ^= True
                    addon.region_dicts.clear()

                    redraw_3dviews(context)

                    return {"FINISHED"}


            if context.area.spaces[0].show_gizmo:

                if addon.props and addon.nearest_axis:
                    self.axis = addon.nearest_axis[0]
                    self.star = self.axis.star
                    self.initial_matrix = self.star.matrix.copy()
                    self.init_point1 = self.star.location.copy()
                    self.init_point2 = self.axis.point_max.copy()
                    self.initial_mouse_vector_ratio = get_mouse_vector_ratio(context, event, self.init_point1, self.init_point2)
                    self.basis_vector = self.init_point2 - self.init_point1
                    self.drag_distance = 0
                    self.is_drag_star = self.star in addon.drag_star

                    if self.is_drag_star:
                        addon.origin_depth_Z = addon.props["origin_depth_Z"]
                    else:
                        addon.drag_star.clear()
                        addon.plane_target = "OBJECT"

                        for prop in addon.props:
                            setattr(addon, prop, addon.props[prop])

                    self.is_mouse_drag = None
                    self.expression = None
                    wm.modal_handler_add(self)

                    return {"RUNNING_MODAL"} # prevent dragging actions to be spawned

        return {"PASS_THROUGH"} # allow dragging actions


    def modal(self, context, event):

        def insert_character(text, character, index):
            return text[:index] + character + text[index:]

        def delete_character(text, index):
            return text[:index] + text[index + 1:]

        def drag_update(self, context, event):
            distance = (self.drag_distance if self.expression is None else self.custom_drag_distance)
            star_matrix = Matrix.Translation(self.basis_vector.normalized() * distance) @ self.initial_matrix
            self.star.apply_matrix_drag(context, event, star_matrix)
            CACHE_view_update(context)


        addon = context.window_manager.align_tool

        if self.is_mouse_drag is None:

            if event.type == "LEFTMOUSE":
                self.is_mouse_drag = False
            elif event.type in ("MOUSEMOVE", "INBETWEEN_MOUSEMOVE"):
                self.is_mouse_drag = True

            if not self.is_mouse_drag:
                double_click = False

                if addon.last_clicked_axis:
                    if addon.last_clicked_axis[0] is self.axis:
                        current_key_points = self.axis.point_min, self.axis.star.location, self.axis.point_max
                        current_closest_point = current_key_points[self.axis.closest_index]

                        if current_closest_point == addon.last_point[0]:
                            double_click = True

                if not double_click:
                    addon.last_clicked_axis[:] = [self.axis]
                    key_points = self.axis.point_min, self.axis.star.location, self.axis.point_max
                    addon.last_point[:] = [key_points[self.axis.closest_index]]
                    redraw_3dviews(context)

                    return {"FINISHED"}

        addon.drag = True

        if not self.is_drag_star:
            self.is_drag_star = True
            self.star = deepcopy(self.star)
            self.star.axes[:] = [axis for axis in self.star.axes if axis.index is self.axis.index]
            addon.drag_star[:] = [self.star]
            addon.plane_target = "CUSTOM"

        if not addon.drag_star_shadow:
            addon.drag_star_shadow[:] = [deepcopy(self.star)]

        if self.expression is None:
            current_mouse_vector_ratio = get_mouse_vector_ratio(context, event, self.init_point1, self.init_point2)
            system_unit_factor = 0.3048 if context.scene.unit_settings.system == "IMPERIAL" else 1
            system_factor = context.scene.unit_settings.scale_length / system_unit_factor
            distance = (current_mouse_vector_ratio - self.initial_mouse_vector_ratio) * system_factor

            if event.ctrl and event.shift:
                distance = round(distance * 10) / 10
            elif event.ctrl:
                distance = round(distance)
            elif event.shift:
                distance = round(distance * 100) / 100

            self.drag_distance = distance / system_factor
            init_characters = ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9", ".", "-")

            if True in (event.unicode == "=", event.unicode in init_characters):

                if event.unicode == "=":
                    self.expression = ""
                    self.cursor_offset = 0
                else:
                    self.expression = event.unicode
                    self.cursor_offset = 1

                self.original_drag_distance = self.drag_distance
                self.custom_drag_distance = 0

            result_text = get_unit_system_text(context, self.drag_distance)
            header_text = f"Drag distance: {result_text}"

        else:
            if event.value == "PRESS":

                if event.unicode and event.type != "DEL":
                    self.expression = insert_character(self.expression, event.unicode, self.cursor_offset)
                    self.cursor_offset += 1

                if event.type == "BACK_SPACE":

                    if self.cursor_offset > 0:
                        self.expression = delete_character(self.expression, self.cursor_offset - 1)
                        self.cursor_offset -= 1
                    elif self.cursor_offset == 0:
                        self.expression = None
                        self.drag_distance = self.original_drag_distance

                        return {"RUNNING_MODAL"}

                elif event.type == "DEL" and len(self.expression) > self.cursor_offset:
                    self.expression = delete_character(self.expression, self.cursor_offset)

                elif event.type in ("ESC", "RIGHTMOUSE"):
                    self.expression = None
                    self.drag_distance = self.original_drag_distance

                    return {"RUNNING_MODAL"}


                if event.type == "HOME":
                    self.cursor_offset = 0

                elif event.type == "END":
                    self.cursor_offset = len(self.expression)

                elif event.type in ("LEFT_ARROW", "NDOF_BUTTON_LEFT"):
                    self.cursor_offset = max(self.cursor_offset - 1, 0)

                elif event.type in ("RIGHT_ARROW", "NDOF_BUTTON_RIGHT"):
                    self.cursor_offset = min(self.cursor_offset + 1, len(self.expression))


            if self.expression == "":
                result_text = get_unit_system_text(context, 0)

            else:
                try:
                    self.custom_drag_distance = blender_units_system.to_value(context.scene.unit_settings.system, "LENGTH", self.expression)
                    self.custom_drag_distance /= context.scene.unit_settings.scale_length
                    result_text = get_unit_system_text(context, self.custom_drag_distance)

                except ValueError:
                    result_text = "Invalid!"

            header_text = f"Drag distance: [{insert_character(self.expression, '|', self.cursor_offset)}] = {result_text}"

        context.area.header_text_set(header_text)

        drag_update(self, context, event)

        apply = False

        if self.is_mouse_drag:
            if event.type == "LEFTMOUSE" and event.value == "RELEASE":
                apply = True
        else:
            if event.type == "LEFTMOUSE" and event.value == "PRESS":
                apply = True


        if event.type in ("RET", "NUMPAD_ENTER"):
            apply = True

        elif event.type == "SPACE" and self.expression is None:
            apply = True

        elif event.type in ("ESC", "RIGHTMOUSE") and event.value == "PRESS" and self.expression is None:
            self.drag_distance = 0
            drag_update(self, context, event)
            apply = True


        if apply:
            addon.drag = False
            addon.last_clicked_axis.clear()
            addon.drag_star_shadow.clear()
            context.area.header_text_set(None)
            redraw_3dviews(context)

            return {"FINISHED"}

        redraw_3dviews(context)

        return {"RUNNING_MODAL"}


class ALIGNTOOL_OT_shift_click_handler(Operator):

    bl_idname = "proaligntools.shift_click_handler"
    bl_label = "Shift click handler"
    bl_options = {'REGISTER', 'INTERNAL'}

    @classmethod
    def poll(cls, context):

        return align_tool_selected(context, mode="OBJECT")


    def invoke(self, context, event):

        wm = context.window_manager
        if context.area.type == "VIEW_3D":
            if context.area.spaces[0].show_gizmo:

                addon = wm.align_tool

                if addon.props:
                    addon.drag_star.clear()

                    for prop in addon.props:
                        setattr(addon, prop, addon.props[prop])

                    wm.modal_handler_add(self)

                    return {"RUNNING_MODAL"} # prevent dragging actions to be spawned

        return {"PASS_THROUGH"} # allow dragging actions


    def modal(self, context, event):

        update_dummy_event(context, event)

        addon = context.window_manager.align_tool

        if event.type in ("MOUSEMOVE", "INBETWEEN_MOUSEMOVE"):

            if addon.props:

                for prop in addon.props:
                    setattr(addon, prop, addon.props[prop])

        if event.type == "LEFTMOUSE" and event.value == "RELEASE":

            return {"FINISHED"}

        redraw_3dviews(context)

        return {"RUNNING_MODAL"}


class ALIGNTOOL_OT_ctrl_click_handler(Operator):

    bl_idname = "proaligntools.ctrl_click_handler"
    bl_label = "Ctrl click handler"
    bl_options = {'REGISTER', 'INTERNAL'}

    @classmethod
    def poll(cls, context):

        return align_tool_selected(context, mode="OBJECT")


    def invoke(self, context, event):

        if context.area.type == "VIEW_3D":
            if context.area.spaces[0].show_gizmo:

                addon = context.window_manager.align_tool

                if addon.props:

                    for prop in addon.props:
                        setattr(addon, prop, addon.props[prop])

                    context.window_manager.modal_handler_add(self)

                    return {"RUNNING_MODAL"} # prevent dragging actions to be spawned

        return {"PASS_THROUGH"} # allow dragging actions


    def modal(self, context, event):

        update_dummy_event(context, event)

        addon = context.window_manager.align_tool

        if event.type in ("MOUSEMOVE", "INBETWEEN_MOUSEMOVE"):

            if addon.props:

                for prop in addon.props:
                    setattr(addon, prop, addon.props[prop])

        if event.type == "LEFTMOUSE" and event.value == "RELEASE":

            return {"FINISHED"}

        redraw_3dviews(context)

        return {"RUNNING_MODAL"}


class ALIGNTOOL_OT_check_running_modal(Operator):

    bl_idname = "proaligntools.check_running_modal"
    bl_label = "Check running modal"
    bl_options = {'REGISTER', 'INTERNAL'}

    @classmethod
    def poll(cls, context):

        return align_tool_selected(context)


    def invoke(self, context, event):

        self.addon = context.window_manager.align_tool
        self.update_running_modal(context, event)
        # self.update_gizmos_visibility()

        return {"PASS_THROUGH"}


    def update_running_modal(self, context, event):

        addon = self.addon

        key_states = set()

        for area, group in addon.gizmo_group_instances:
            if area.type == "VIEW_3D" and "invalid" not in str(group) and context.mode == "OBJECT":

                if event.shift and event.type == "D":
                    key_states.add(True)

                elif not event.ctrl and not event.alt and not event.shift:

                    if event.type in ("G", "R", "S"):
                        key_states.add(True)
                    elif event.type in ("ESC", "RET", "SPACE", "RIGHTMOUSE"):
                        key_states.add(False)

                    elif event.value == "PRESS":

                        if event.type == "LEFTMOUSE":

                            if addon.props:
                                key_states.add(False) # cursor is over some gizmo
                            else:
                                current_regions = set()

                                for region in area.regions:

                                    if get_mouse_in_region(region, event):
                                        current_regions.add(region.type)

                                    for region_dict in addon.region_dicts:

                                        if region_dict["region"] == region:

                                            if "mouse_in_shortcuts_button" in region_dict:

                                                mouse_in_shortcuts_button = region_dict["mouse_in_shortcuts_button"]

                                if "WINDOW" in current_regions:

                                    if not mouse_in_shortcuts_button:

                                        if len(current_regions) > 1: # cursor is on some mixed area of the 3D view probably over a button or panel
                                            key_states.add(False)
                                        else: # cursor is on a free area of the 3D view region only
                                            key_states.add(not addon.running_modal)

                    elif event.value == "RELEASE":

                        if event.type == "LEFTMOUSE":
                            key_states.add(False)

                    # elif event.value == "NOTHING":

                    #     if event.type == "MOUSEMOVE":
                    #         key_states.add(False)

        if True in key_states:
            addon.running_modal = True
        elif False in key_states:
            addon.running_modal = False

    # def update_gizmos_visibility(self):

    #     addon = self.addon

    #     for area, group in addon.gizmo_group_instances:
    #         if area.type == "VIEW_3D" and "invalid" not in str(group):

    #             if addon.running_modal:
    #                 if group.show_gizmo_state:

    #                     if not area.spaces[0].show_gizmo:
    #                         area.spaces[0].show_gizmo = True

    #             else:
    #                 group.show_gizmo_state = area.spaces[0].show_gizmo


class ALIGNTOOL_OT_redraw(Operator):

    bl_idname = "proaligntools.redraw"
    bl_label = "Redraw"
    bl_options = {'REGISTER', 'INTERNAL'}

    @classmethod
    def poll(cls, context):

        return align_tool_selected(context)


    def invoke(self, context, event):

        if True in (event.type == "MOUSEMOVE", event.value in ("PRESS", "RELEASE")):

            update_dummy_event(context, event)

        context.area.tag_redraw()

        return {"PASS_THROUGH"}
