import bpy
render = bpy.context.scene.render
photographer = bpy.context.scene.camera.data.photographer

photographer.resolution_rotation = 'LANDSCAPE'
photographer.resolution_mode = '2391'
photographer.resolution_x = 1920
photographer.resolution_y = 1080
photographer.ratio_x = 16.0
photographer.ratio_y = 9.0
photographer.longedge = 4096
photographer.fit_inside_sensor = True
