import bpy
import bmesh
from ..functions.materials import list_objects_with_material

def select_obj_list(self,context,obj_list):
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode="OBJECT")
    if self.toggle:
        all_selected = all(obj.select_get() for obj in obj_list)
        if all_selected:
            for obj in obj_list:
                obj.select_set(False)
        else:
            for obj in obj_list:
                obj.select_set(True)
                bpy.context.view_layer.objects.active = obj
    elif self.deselect:
        for obj in obj_list:
            obj.select_set(False)
    else:
        bpy.ops.object.select_all(action='DESELECT')
        for obj in obj_list:
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj

class StringItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()

class PHOTOGRAPHER_OT_Select(bpy.types.Operator):
    bl_idname = "photographer.select"
    bl_label = "Select"
    bl_options = {'UNDO'}

    obj_name: bpy.props.StringProperty()
    toggle: bpy.props.BoolProperty()
    deselect: bpy.props.BoolProperty()
    is_target: bpy.props.BoolProperty()
    linked: bpy.props.BoolProperty()

    @classmethod
    def description(cls, context, properties):
        if properties.is_target:
            type = 'Target : '
        else:
            type = 'Object : '
        return (type + properties.obj_name + "\n"
                "Shift-Click to toggle selection, Ctrl-Click to remove from selection")

    def execute(self, context):        
        obj = bpy.data.objects.get(self.obj_name)
        if self.linked:
            objects = [o for o in bpy.context.view_layer.objects if o.data == obj.data]
            if not self.toggle and not self.deselect:
                bpy.ops.object.select_all(action='DESELECT')
            
        else:
            objects = [obj]

        for obj in objects:
            if obj is None:
                self.report({'ERROR'}, "Object not found")
            else:
                if bpy.ops.object.mode_set.poll():
                    bpy.ops.object.mode_set(mode="OBJECT")
                if self.toggle:
                    if obj.select_get():
                        obj.select_set(False)
                    else:
                        obj.select_set(True)
                        bpy.context.view_layer.objects.active = obj
                    
                elif self.deselect:
                    obj.select_set(False)
                    
                else:
                    if self.linked:
                        obj.select_set(True)
                        bpy.context.view_layer.objects.active = obj
                    else:
                        bpy.ops.object.select_all(action='DESELECT')
                        obj.select_set(True)
                        bpy.context.view_layer.objects.active = obj

        # Reset properties to default
        self.linked = False
        self.is_target = False

        return{'FINISHED'}
        
    def invoke(self, context, event):
        self.toggle = event.shift
        self.deselect = event.ctrl
        return self.execute(context)
        
        
class PHOTOGRAPHER_OT_SelectCollection(bpy.types.Operator):
    bl_idname = "photographer.select_collection"
    bl_label = "Select Cameras or Lights in Collection"
    bl_description = "Shift-Click to toggle selection, Ctrl-Click to remove from selection"
    bl_options = {'UNDO'}

    coll_name: bpy.props.StringProperty()
    coll_type: bpy.props.EnumProperty(
        items = [('CAMERA','Camera',''),
                ('LIGHT','Light','')],
                )
    toggle: bpy.props.BoolProperty()
    deselect: bpy.props.BoolProperty()


    def execute(self, context):
        coll = bpy.data.collections[self.coll_name]
        if self.coll_type == 'CAMERA':
            obj_list = [o for o in coll.objects if o.type == 'CAMERA']
        elif self.coll_type == 'LIGHT':
            obj_list = [o for o in coll.objects if o.type == 'LIGHT']
        
        select_obj_list(self,context,obj_list)
        return{'FINISHED'}
        
    def invoke(self, context, event):
        self.toggle = event.shift
        self.deselect = event.ctrl
        return self.execute(context)
    
class PHOTOGRAPHER_OT_SelectLightgroup(bpy.types.Operator):
    bl_idname = "photographer.select_lightgroup"
    bl_label = "Select Lights in Lightgroup"
    bl_description = "Shift-Click to toggle selection, Ctrl-Click to remove from selection"
    bl_options = {'UNDO'}

    lightgroup_name: bpy.props.StringProperty()
    toggle: bpy.props.BoolProperty()
    deselect: bpy.props.BoolProperty()


    def execute(self, context):

        light_objs = [o for o in context.view_layer.objects if o.type=='LIGHT' and o.lightgroup==self.lightgroup_name]
        
        select_obj_list(self,context,light_objs)
        return{'FINISHED'}
        
    def invoke(self, context, event):
        self.toggle = event.shift
        self.deselect = event.ctrl
        return self.execute(context)
    
class PHOTOGRAPHER_OT_SelectEmissiveLightgroup(bpy.types.Operator):
    bl_idname = "photographer.select_emissive_lightgroup"
    bl_label = "Select Emissive objects in Lightgroup"
    bl_description = "Shift-Click to toggle selection, Ctrl-Click to remove from selection"
    bl_options = {'UNDO'}

    lightgroup_name: bpy.props.StringProperty()
    toggle: bpy.props.BoolProperty()
    deselect: bpy.props.BoolProperty()


    def execute(self, context):
        lg_em_objs = []
        emissive_mats = [mat for mat in bpy.data.materials if mat.get('is_emissive', False)]
        for em in emissive_mats:
            em_objs = list_objects_with_material(em)
            for obj in em_objs:
                if obj.lightgroup==self.lightgroup_name:
                    if obj not in lg_em_objs:
                        lg_em_objs.append(obj)
        
        select_obj_list(self,context,lg_em_objs)
        return{'FINISHED'}
        
    def invoke(self, context, event):
        self.toggle = event.shift
        self.deselect = event.ctrl
        return self.execute(context)


class PHOTOGRAPHER_OT_SelectEmissive(bpy.types.Operator):
    bl_idname = "photographer.select_emissive"
    bl_label = "Select Objects using Emissive Material"
    bl_description = "Shift-Click to toggle selection, Ctrl-Click to remove from selection"
    bl_options = {'UNDO'}

    mat_name: bpy.props.StringProperty()
    toggle: bpy.props.BoolProperty()
    deselect: bpy.props.BoolProperty()
    
    def execute(self, context):
        material = bpy.data.materials[self.mat_name]
        obj_list = []
        mesh_objs = [ob for ob in context.scene.objects if ob.type in {'MESH','CURVE'}]
        if material.users:
            if context.object:
                if context.object.mode == 'EDIT':
                    for obj in mesh_objs:
                        for m in obj.material_slots:
                            if m.name == self.mat_name and obj.select_get():
                                slot_index = obj.material_slots[:].index(m)
                                obj.active_material_index = slot_index
                                
                                if self.toggle:
                                    faces_list = []
                                    selected_faces = []
                                    bm = bmesh.from_edit_mesh(obj.data)
                                    bm.select_mode = {'FACE'} 
                                    # for face in obj.data.polygons:
                                    for face in bm.faces:
                                        if face.select and face.material_index != slot_index:
                                            selected_faces.append(face)
                                        if face.material_index == slot_index:
                                            faces_list.append(face)
                                        
                                    all_selected = all(face.select for face in faces_list)
                                    if all_selected:
                                        for face in faces_list:
                                            face.select_set(False)
                                    else:
                                        for face in faces_list:
                                            face.select_set(True)
                                    
                                    # Reselect other faces        
                                    for face in selected_faces:
                                        face.select_set(True)
                                    obj.data.update()
                                    
                                elif self.deselect:
                                    bpy.ops.object.material_slot_deselect()
                                else:
                                    bpy.ops.mesh.select_all(action='DESELECT')
                                    bpy.ops.object.material_slot_select()

                else:
                    bpy.ops.object.mode_set(mode="OBJECT")
                    for obj in mesh_objs:
                        for m in obj.material_slots:
                            if m.name == self.mat_name:
                                obj_list.append(obj)
                                obj.active_material_index = obj.material_slots[:].index(m)
                    select_obj_list(self,context,obj_list)
        return{'FINISHED'}

    def invoke(self, context, event):
        self.toggle = event.shift
        self.deselect = event.ctrl
        return self.execute(context)