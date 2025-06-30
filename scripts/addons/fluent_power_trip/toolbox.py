import bpy
from bpy.types import Operator
from bpy.props import IntProperty, FloatProperty, BoolProperty, StringProperty

from .constants import *
from .helpers import *
from .viewport_drawing import *
from .math_functions import *
from .ui_button import *
from .drawing import *
from .modifiers import *
from .bevels import *
from .independant_helpers import *


class FLUENT_OT_AlignView(Operator):
    "Align view to vertex"
    bl_idname = "fluent.alignview"
    bl_label = "Align view"
    bl_options = {'REGISTER', 'UNDO'}

    def modal(self, context, event):
        context.area.tag_redraw()

        self.events = event_dico_refresh(self.events, event)

        if pass_through(event):
            return {'PASS_THROUGH'}

        region = context.region
        rv3d = context.region_data

        self.draw_dots.set_dots([])
        obj = click_on(event.mouse_region_x, event.mouse_region_y)

        if obj:
            eval_obj = get_evaluated_object(obj)
            snaped_vertex = [1000, None, None]  # distance, vertex, co2_d
            for v in eval_obj.data.vertices:
                co_2d = view3d_utils.location_3d_to_region_2d(region, rv3d, v.co)
                d = distance(co_2d.x, co_2d.y, 0, event.mouse_region_x, event.mouse_region_y, 0)
                if d <= 32 and d < snaped_vertex[0]:
                    snaped_vertex[0] = d
                    snaped_vertex[1] = v
                    snaped_vertex[2] = co_2d
            if snaped_vertex[1]:
                self.draw_dots.append_a_dot([snaped_vertex[2].x, snaped_vertex[2].y, 6, (1, 1, 1, 1)])

        if event.value == 'PRESS' and event.type == 'LEFTMOUSE':
            rv3d = bpy.context.region_data
            v_normal = snaped_vertex[1].normal
            v_up = Vector((0, 0, 1))
            q_rot = v_normal.rotation_difference(v_up)
            rv3d.view_rotation = q_rot.inverted()
            context.region_data.view_perspective = 'ORTHO'
            active_object('SET', obj, True)
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'FINISHED'}

        if event.value == 'PRESS' and event.type == 'ESC':
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'FINISHED'}
        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        self.ui_items_list = []
        self.events = event_dico_builder(event)
        self.draw_dots = FLUENT_Draw_Dots()
        self.ui_items_list.append(self.draw_dots)
        self.the_vertex = None
        self.previous_object = None
        self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, (self, context), 'WINDOW', 'POST_PIXEL')
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


class FLUENT_OT_CleanBooleanObjects(Operator):
    """Remove unused boolean objects"""
    bl_idname = "fluent.cleanbooleanobjects"
    bl_label = "Fluent - Remove unused boolean objects"

    def invoke(self, context, event):
        for o in bpy.data.collections['Bool_Objects'].objects:
            modifier_found = False
            for oo in bpy.data.objects:
                for m in oo.modifiers:
                    if m.type == 'BOOLEAN' and m.object == o:
                        modifier_found = True
                        break
            if not modifier_found:
                bpy.data.objects.remove(o, do_unlink=True)
        return {'FINISHED'}


class FLUENT_OT_ApplyToBoolean(Operator):
    """Apply all modifiers from the first to the first boolean.
Especially useful to prepare the model to the boolean support tool.

/!\ Your object will be impossible to edit with Fluent./!\ """
    bl_idname = "fluent.applytoboolean"
    bl_label = "Apply to boolean"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = active_object('GET')
        if obj:
            for m in obj.modifiers:
                if m.type != 'BOOLEAN' or fluent_modifiers_name['outer_bevel'] in m.name:
                    if m.show_render:
                        try:
                            bpy.ops.object.modifier_apply(modifier=m.name)
                        except:
                            obj.modifiers.remove(m)
                    else:
                        obj.modifiers.remove(m)
                else:
                    break
            if obj.get('fluent_obj'):
                obj['fluent_obj'] = 0
            if obj.get('fluent_type'):
                obj['fluent_type'] = 'unknow'
        return {'FINISHED'}


class FLUENT_OT_AutoSupport(Operator):
    """Automatic edge supports making.
Select the boolean object first and the main object after

Hold Shift - supports for each loose parts"""
    bl_idname = "fluent.autosupport"
    bl_label = "Boolean support creation"
    bl_options = {'REGISTER', 'UNDO'}

    def cutterObj(self):
        height = .01
        vertices = [(-1, -1, -height), (-1, 1, -height), (1, 1, -height), (1, -1, -height),
                    (-1, -1, height), (-1, 1, height), (1, 1, height), (1, -1, height),
                    (-1, 0, -height), (1, 0, -height),
                    (-1, 0, height), (1, 0, height),
                    (0, -1, -height), (0, 1, -height),
                    (0, -1, height), (0, 1, height),
                    (0, 0, -height), (0, 0, height)]

        faces = [(0, 4, 10, 8), (8, 10, 5, 1), (1, 5, 15, 13), (13, 15, 6, 2), (2, 6, 11, 9), (9, 11, 7, 3),
                 (3, 7, 14, 12), (12, 14, 4, 0),
                 (4, 10, 17, 14), (10, 5, 15, 17), (17, 15, 6, 11), (14, 17, 11, 7), (0, 8, 16, 12), (8, 1, 13, 16),
                 (16, 13, 2, 9), (12, 16, 9, 3),
                 (8, 10, 17, 16), (16, 17, 11, 9), (12, 14, 17, 16), (16, 17, 15, 13)]

        mesh_data = bpy.data.meshes.new("cutter")
        mesh_data.from_pydata(vertices, [], faces)
        mesh_data.update()
        cutter_obj = bpy.data.objects.new("cutter", mesh_data)
        bpy.context.scene.collection.objects.link(cutter_obj)
        active_object('SET', cutter_obj, True)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.object.vertex_group_add()
        bpy.ops.object.vertex_group_assign()
        v_groups = bpy.context.active_object.vertex_groups
        v_groups[0].name = 'intersect'
        bpy.ops.object.mode_set(mode='OBJECT')

        return cutter_obj

    def execute(self, context):
        bool_list = []
        cutter_list = []
        obj = active_object('GET')
        obj.select_set(False)
        for v in obj.data.vertices:
            v.select = False
        margin = 0.01

        if not obj:
            make_oops(['First : select the boolean object', 'Second : select the main object'],
                      title="Info", icon='ERROR')

            return {'CANCELLED'}

        # récupère la largeur du dernier bevel angle
        hidden_modifiers = []
        for m in obj.modifiers:
            if m.type == 'BEVEL' and m.limit_method == 'ANGLE':
                margin = m.width * 2 + margin
                hidden_modifiers.append(m)
                m.show_viewport = False
        print('--- 01')
        for o in bpy.context.selected_objects:
            print('--- --- 01 i')
            bool_list.append(o)
            o.select_set(False)
        print('--- 02')
        for b in bool_list:
            print('--- --- 02 i')
            multiparts = False
            active_object('SET', b, True)
            bpy.ops.object.duplicate()
            copy = active_object('GET')
            active_object('SET', copy, True)

            for m in copy.modifiers:
                if m.show_render and m.type in {'MIRROR', 'ARRAY'}:
                    multiparts = True

            bpy.ops.object.convert(target='MESH')
            bpy.ops.object.transform_apply(location=True, rotation=False, scale=True)

            if multiparts and self.event.shift:
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.separate(type='LOOSE')
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
                subparts = bpy.context.selected_objects

                for s in subparts:
                    cutter = self.cutterObj()
                    cutter.select_set(True)
                    context.view_layer.objects.active = cutter
                    bpy.ops.object.mode_set(mode='EDIT')
                    bpy.ops.mesh.select_all(action='SELECT')
                    bpy.ops.object.mode_set(mode='OBJECT')
                    cutter.dimensions = s.dimensions
                    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
                    cutter.dimensions.x = cutter.dimensions.x + margin
                    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
                    cutter.dimensions.y = cutter.dimensions.y + margin
                    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
                    cutter.location = s.location
                    cutter.rotation_euler = s.rotation_euler
                    cutter_list.append(cutter)
                    cutter.select_set(False)
                    bpy.data.objects.remove(s, do_unlink=True)

            else:
                bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
                b.select_set(False)
                cutter = self.cutterObj()
                cutter.select_set(True)
                context.view_layer.objects.active = cutter
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.object.mode_set(mode='OBJECT')
                cutter.dimensions = copy.dimensions
                bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
                cutter.dimensions.x = cutter.dimensions.x + margin
                bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
                cutter.dimensions.y = cutter.dimensions.y + margin
                bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
                cutter.location = copy.location
                cutter.rotation_euler = b.rotation_euler
                cutter_list.append(cutter)
                cutter.select_set(False)
                bpy.data.objects.remove(copy, do_unlink=True)
        print('--- 03')
        for o in cutter_list:
            o.select_set(True)
        print('--- 04')
        active_object('SET', obj)
        print('--- 05')
        bpy.ops.object.join()
        print('--- 06')
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_mode(type="VERT")
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.vertex_group_set_active(group='intersect')
        bpy.ops.object.vertex_group_select()
        bpy.ops.mesh.intersect()
        bpy.ops.mesh.remove_doubles()
        v_no_group = []
        bpy.ops.object.mode_set(mode='OBJECT')
        print('--- 07')
        for v in obj.data.vertices:
            if v.select:
                v_no_group.append(v.index)
        print('--- 08')
        bpy.ops.object.mode_set(mode='OBJECT')
        obj.vertex_groups['intersect'].remove(v_no_group)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.vertex_group_set_active(group='intersect')
        bpy.ops.object.vertex_group_select()
        bpy.ops.mesh.delete(type='VERT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.object.vertex_group_remove()
        bpy.ops.object.mode_set(mode='OBJECT')

        obj.select_set(False)

        context.view_layer.objects.active = bool_list[0]

        for m in hidden_modifiers:
            m.show_viewport = True

        return {'FINISHED'}

    def invoke(self, context, event):
        if len(bpy.context.selected_objects) < 2:
            make_oops(['Select 2 objects.', 'The boolean object first then the main object.'], title="How to use?",
                      icon='ERROR')

            return {'CANCELLED'}
        elif len(bpy.context.selected_objects) > 2:
            make_oops(['Select only 2 objects.', 'The boolean object first then the main object.'], title="How to use?",
                      icon='ERROR')

            return {'CANCELLED'}
        else:
            obj = active_object()
            for m in obj.modifiers:
                if m.type == 'SOLIDIFY':
                    make_oops(['Your object use a solidify modifier.',
                               'It\'s impossible to add edges on face made by a solidify modifier.',
                               'The result may not be as expected.', 'Use the "Apply to boolean" function before.'],
                              title="WARNING", icon='ERROR')
            self.event = event
            self.execute(context)
            return {'FINISHED'}


class FLUENT_OT_AllCutterMirror(Operator):
    "Apply a mirror for each cut"
    bl_idname = "fluent.allcuttermirror"
    bl_label = "Mirror all cutters"
    bl_options = {'REGISTER', 'UNDO'}

    def modal(self, context, event):
        context.area.tag_redraw()

        self.events = event_dico_refresh(self.events, event)

        if pass_through(event):
            return {'PASS_THROUGH'}

        # action des bouttons
        action = None
        for b in self.ui_items_list:
            if type(b) is FLUENT_Ui_Button:
                b.is_hover(self.events)
                if b.get_state() == 2:
                    action = b.get_action()
                    b.set_state(0)
                    break
                else:
                    action = None
            elif type(b) is FLUENT_Ui_Layout:
                layout_items_list = b.get_items()
                for i in layout_items_list:
                    i.is_hover(self.events)
                    if i.get_state() == 2:
                        action = i.get_action()
                        i.set_state(0)
                        break
                    else:
                        action = None
                if action:
                    break

        callback, screen_text = self.all_fluent_adjustments[0].adjust(self.events)
        mirror_object = self.all_fluent_adjustments[0].mirror_action(action='GET_REF')
        command = None
        for c in callback:
            if c in ['+X', '-X', '+Y', '-Y', '+Z', '-Z']:
                command = c
        for i, fa in enumerate(self.all_fluent_adjustments):
            if i != 0:
                fa.mirror_action(action='GET_MODIFIER').mirror_object = mirror_object
                fa.adjust(self.events, action=command)

        if event.type == 'ESC' and event.value == 'PRESS':
            for fa in self.all_fluent_adjustments:
                try:
                    fa.mirror_action(action='BACKUP')
                except:
                    pass
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'FINISHED'}

        if (event.type == 'Q' and event.value == 'PRESS') or action == 'FINISHED' or action == 'VALIDATE':
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'FINISHED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        # vérifications
        if not active_object():
            make_oops(['Select an object'], title="How to use ?", icon='ERROR')

            return {'FINISHED'}

        # VARIABLES
        self.obj = active_object()
        self.all_fluent_adjustments = []

        self.events = event_dico_builder(event)

        self.ui_items_list = []
        button = make_button('CANCEL')
        self.ui_items_list.append(button)

        for m in self.obj.modifiers:
            if m.type == 'BOOLEAN':
                cutter = m.object
                if cutter.get('fluent_type'):
                    self.all_fluent_adjustments.append(modifiers_manager(obj=cutter, bool_target=self.obj))
        if self.all_fluent_adjustments:
            for fa in self.all_fluent_adjustments:
                fa.mirror_action(action='ADD')
                fa.mirror_action(action='SAVE')
            ui_items_list, pie_menu = self.all_fluent_adjustments[0].get_ui('MIRROR')
            self.ui_items_list.append(pie_menu)
            for fa in self.all_fluent_adjustments:
                fa.prepare_adjustment('MIRROR', self.events)

            self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, (self, context), 'WINDOW',
                                                                  'POST_PIXEL')
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            make_oops(['No Fluent boolean object found.'], title="Info", icon='ERROR')

            return {'CANCELLED'}
