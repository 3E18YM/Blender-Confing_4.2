import bpy

def PHOTOGRAPHER_MT_SceneSettings(self, context):
    layout = self.layout
    if context.scene.camera:
        if context.scene.photographer.main_camera == context.scene.camera.data:
            txt = 'Remove Main Camera'
        else:
            txt = 'Set Scene Camera as Main Camera'
        layout.operator("photographer.set_main_camera", text=txt)

    layout.prop(context.scene.photographer, "main_camera", text='Photographer Main Camera')

def register():
    bpy.types.SCENE_PT_scene.append(PHOTOGRAPHER_MT_SceneSettings)

def unregister():
    bpy.types.SCENE_PT_scene.remove(PHOTOGRAPHER_MT_SceneSettings)