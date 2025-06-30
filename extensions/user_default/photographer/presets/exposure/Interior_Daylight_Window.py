import bpy
camera = bpy.context.scene.camera.data
photographer = bpy.context.scene.camera.data.photographer
scene_pg = bpy.context.scene.photographer

scene_pg.comp_exposure = False
photographer.exposure_mode = 'EV'
photographer.ev = 7.610000133514404
photographer.exposure_compensation = 0.0
photographer.center_weight = 25
photographer.ae_speed = 0.10000000149011612
photographer.shutter_speed_slider_enable = False
photographer.shutter_mode = 'SPEED'
photographer.shutter_speed_preset = '50'
photographer.shutter_angle_preset = '180'
photographer.shutter_speed = 100.0
photographer.shutter_angle = 180.0
photographer.aperture_slider_enable = False
photographer.aperture = 1.399999976158142
photographer.aperture_preset = '2.8'
photographer.iso_slider_enable = False
photographer.iso = 100
photographer.iso_preset = '200'
photographer.motionblur_enabled = False
photographer.falsecolor_enabled = False
photographer.colorchart_enabled = False
