import bpy
from bpy.props import IntProperty, StringProperty, FloatVectorProperty, FloatProperty, BoolProperty
from bpy.types import CollectionProperty, PropertyGroup, UIList, Panel, Operator, PointerProperty
from ..functions.functions import are_obj_transform_equal
from .. import __package__ as base_package


class PhotographerBookmarksSettings(PropertyGroup):
    index : IntProperty(name='Index')
    name : StringProperty(name="Cam name", default="Cam")
    location : FloatVectorProperty(name="Cam Location",subtype='XYZ', precision=4, size=3)
    rotation_euler : FloatVectorProperty(name="Cam Rotation",subtype='XYZ', precision=4, size=3)

class PHOTOGRAPHER_UL_Bookmarks_Item(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
    
        row = layout.row(align=True)
        icn = 'PLAY'
        cam_obj = [o for o in bpy.data.objects if o.data is data.id_data][0]
        if are_obj_transform_equal(cam_obj, item):
            icn = "RADIOBUT_ON"

        apply = row.operator('photographer.bookmark_apply', text='', icon=icn)
        apply.camera = data.name        
        apply.index = item.index        
        row.prop(item, "name", text="", icon_value=icon, emboss=False)
        update = row.operator('photographer.bookmark_update', text='', icon='FILE_REFRESH')
        update.camera = data.name
        update.index = item.index
        delete = row.operator('photographer.bookmark_delete', text='', icon='PANEL_CLOSE')
        delete.camera = data.name
        delete.index = item.index
        
class PHOTOGRAPHER_PT_ViewPanel_Bookmarks(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Position Bookmarks"
    bl_category = "Photographer"
    bl_parent_id = 'PHOTOGRAPHER_PT_ViewPanel_Camera'
    
    @classmethod
    def poll(cls, context):
        bpe = context.preferences.addons[base_package].preferences.bookmarks_panel_enable
        return context.scene.camera is not None and context.scene.camera.type == 'CAMERA' and bpe
    
    def draw_header_preset(self,context):
        layout = self.layout
        layout.operator("photographer.bookmark_add", icon='ADD', text="").camera=context.scene.camera.data.name

        if not context.scene.camera:
            layout.enabled=False

    def draw(self, context):
        layout = self.layout  
        layout.template_list("PHOTOGRAPHER_UL_Bookmarks_Item", "", context.scene.camera.data, "bookmarks",
                            context.scene.camera.data.photographer, "active_bookmark_index")
            
class PHOTOGRAPHER_PT_Panel_Bookmarks(bpy.types.Panel):
    bl_label = 'Position Bookmarks'
    bl_parent_id = 'PHOTOGRAPHER_PT_Panel'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.camera

    def draw_header_preset(self,context):
        layout = self.layout
        layout.operator("photographer.bookmark_add", icon='ADD', text="Add").camera=context.camera.name

    def draw(self, context):
        layout = self.layout  
        layout.template_list("PHOTOGRAPHER_UL_Bookmarks_Item", "", context.camera, "bookmarks",
                            context.camera.photographer, "active_bookmark_index")
        
class PHOTOGRAPHER_OT_Bookmarks_Add(Operator):
    bl_idname = "photographer.bookmark_add"
    bl_label = "Add"
    bl_description = "Add a Position Bookmark for this camera"

    camera : StringProperty()
    
    def execute(self, context):
        cam = bpy.data.cameras.get(self.camera,None)
        cam_obj = [o for o in bpy.data.objects if o.data is cam.id_data][0]
        bookmark = cam.bookmarks.add()
        bookmark.index = len(cam.bookmarks)-1
        name = "Position "+str(len(cam.bookmarks))
        for bookmark in cam.bookmarks:
            while bookmark.name == name:
                name = "Position "+str(len(cam.bookmarks)+1)

        bookmark.name = name
        bookmark.location = cam_obj.location
        bookmark.rotation_euler = cam_obj.rotation_euler

        return{'FINISHED'}

class PHOTOGRAPHER_OT_Bookmarks_Delete(Operator):
    bl_idname = "photographer.bookmark_delete"
    bl_label = "Remove"
    bl_description = "Remove cam"
    
    camera : StringProperty()
    index : IntProperty()
    
    def execute(self, context):
        cam = bpy.data.cameras.get(self.camera,None)
        cam.bookmarks.remove(self.index)

        # Update index of remaining bookmarks
        for bookmark in cam.bookmarks:
            if bookmark.index > self.index:
                bookmark.index -= 1
        return{'FINISHED'}

class PHOTOGRAPHER_OT_Bookmarks_Apply(Operator):
    bl_idname = "photographer.bookmark_apply"
    bl_label = "Apply Bookmark"
    bl_description = "Apply Bookmark position to current Scene Camera"

    camera : StringProperty()
    index : IntProperty()
    
    def execute(self, context):
        cam = bpy.data.cameras.get(self.camera,None)
        bookmark = cam.bookmarks[self.index]

        cam_obj = [o for o in bpy.data.objects if o.data is cam.id_data][0]
        cam_obj.location = bookmark.location
        cam_obj.rotation_euler = bookmark.rotation_euler
        return{'FINISHED'}
        
class PHOTOGRAPHER_OT_Bookmarks_Update(Operator):
    bl_idname = "photographer.bookmark_update"
    bl_label = "Update Bookmark"
    bl_description = "Update Bookmark with current Scene Camera Position"

    camera : StringProperty()
    index : IntProperty()
    
    @classmethod
    def poll(cls, context):
        return context.scene.camera and len(context.scene.camera.data.bookmarks) > 0
    
    def execute(self, context):
        cam = bpy.data.cameras.get(self.camera,None)
        bookmark = cam.bookmarks[self.index]

        cam_obj = [o for o in bpy.data.objects if o.data is cam.id_data][0]
        bookmark.location = cam_obj.location
        bookmark.rotation_euler = cam_obj.rotation_euler
        return{'FINISHED'}
        
classes = (
    PHOTOGRAPHER_PT_Panel_Bookmarks,
    PHOTOGRAPHER_UL_Bookmarks_Item,
    PHOTOGRAPHER_OT_Bookmarks_Add,
    PHOTOGRAPHER_OT_Bookmarks_Apply,
    PHOTOGRAPHER_OT_Bookmarks_Update,
    PHOTOGRAPHER_OT_Bookmarks_Delete,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
