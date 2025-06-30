import bpy
from bpy.types import Menu, Operator

class CUSTOM_MT_menu(Menu):
    bl_label = "Main Menu"
    bl_idname = "CUSTOM_MT_menu"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        pie.operator("object.custom_operator")

 
class CUSTOM_OT_operator(Operator):
    bl_idname = "object.custom_operator"
    bl_label = "Test Operator"

    relations_expand: bpy.props.BoolProperty(default=True)
    display_expand: bpy.props.BoolProperty(default=True)

    def execute(self, context):
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        row = box.row()
        row.alignment = 'LEFT'
        row.emboss = 'NONE'
        expand = self.display_expand
        icon = "TRIA_DOWN" if expand else "TRIA_RIGHT"
        row.prop(self, "display_expand", text="Display", icon=icon)
        if expand:
            override = Layout(box)
            bpy.types.OBJECT_PT_display.draw(override, context)


        type(context).armature = context.object.data

        box = layout.box()
        row = box.row()
        row.alignment = 'LEFT'
        row.emboss = 'NONE'
        expand = self.relations_expand
        icon = "TRIA_DOWN" if expand else "TRIA_RIGHT"
        row.prop(self, "relations_expand", text="Relations", icon=icon)
        if expand:
            override = Layout(box)
            bpy.types.DATA_PT_display.draw(override, context)

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_popup(self)

class Context(dict):
    def __init__(self, context=None, **kwargs):
        super().__init__()
        self.__dict__ = self

        if context is not None:
            self.update(context.copy())
        self.update(**kwargs)

class Layout:
    def __init__(self, layout):
        self.layout = layout

          
classes = (    
    CUSTOM_MT_menu,
    CUSTOM_OT_operator,
    )

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()

    bpy.ops.wm.call_menu_pie(name="CUSTOM_MT_menu")