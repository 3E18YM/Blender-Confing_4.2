import bpy
render = bpy.context.scene.render
photographer = bpy.context.scene.camera.data.photographer

photographer.resolution_rotation = 'LANDSCAPE'
photographer.resolution_mode = 'CUSTOM_RATIO'
photographer.resolution_x = 4448
photographer.resolution_y = 1080
photographer.ratio_x = 1.4366
photographer.ratio_y = 1.0
photographer.longedge = 4448
photographer.fit_inside_sensor = True
