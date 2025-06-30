import bpy, traceback
from bpy.app.handlers import persistent
from .camera import update_settings, update_world, PhotographerCameraSettings
from .properties import post_effects

LAST_CAMERA = None
LAST_SENSOR_WIDTH = 1
LAST_SENSOR_HEIGHT = 1
LAST_WORLD = None
LAST_VIEWLAYER = None

@persistent
def update_render_camera(scene,depsgraph):
    if scene.camera:
        update_settings(scene.camera.data.photographer,bpy.context)

        # # Update the Post Effects - needed for animation support in the future
        # post_effects.update_post_effects_params(scene.camera.data.post_effects,bpy.context)
        # post_effects.update_post_effects_color_params(scene.camera.data.post_effects,bpy.context)
        # post_effects.update_streaks(scene.camera.data.post_effects,bpy.context)
        # post_effects.update_bloom(scene.camera.data.post_effects,bpy.context)

@persistent
def update_scene_camera(scene):
    global LAST_CAMERA
    global LAST_SENSOR_WIDTH
    global LAST_SENSOR_HEIGHT
    global LAST_WORLD
    global LAST_VIEWLAYER
    if scene.camera and scene.camera.type == 'CAMERA':
        if scene.camera != LAST_CAMERA or scene.camera.data.sensor_width != LAST_SENSOR_WIDTH or scene.camera.data.sensor_height != LAST_SENSOR_HEIGHT:
            LAST_CAMERA = scene.camera
            LAST_SENSOR_WIDTH = scene.camera.data.sensor_width
            LAST_SENSOR_HEIGHT = scene.camera.data.sensor_height
            update_settings(scene.camera.data.photographer,bpy.context)
            post_effects.update_post_effects(scene.camera.data.post_effects,bpy.context)
        try:
            if scene.world and scene.world != LAST_WORLD:
                LAST_WORLD = scene.world
                update_world(scene.camera.data.photographer,bpy.context)
                # raise Exception('Photographer Exception')
        except Exception as e:
            print(f'Photographer Handler {type(e)}: {e} {traceback.format_exc()}')

def on_view_layer_change():
    scene = bpy.context.scene
    if scene.camera and scene.camera.type == 'CAMERA':
        scene.camera.data.photographer.active_view_layer = bpy.context.view_layer.name

@persistent
def update_view_layer(dummy):
    on_view_layer_change()
    bpy.msgbus.subscribe_rna(
        key=(bpy.types.Window, 'view_layer'),
        owner=bpy,
        args=(),
        notify=on_view_layer_change
    )

def register():
    bpy.app.handlers.frame_change_post.append(update_render_camera)
    bpy.app.handlers.depsgraph_update_post.append(update_scene_camera)
    bpy.app.handlers.load_post.append(update_view_layer)

def unregister():
    bpy.app.handlers.frame_change_post.remove(update_render_camera)
    bpy.app.handlers.depsgraph_update_post.remove(update_scene_camera)
    bpy.app.handlers.load_post.remove(update_view_layer)