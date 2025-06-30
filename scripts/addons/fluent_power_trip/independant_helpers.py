import bpy
import math

def get_addon_preferences():
    addon_key = __package__.split(".")[0]
    addon_prefs = bpy.context.preferences.addons[addon_key].preferences

    return addon_prefs

def active_object(action = 'GET', obj = None, solo = False):
    if solo:
        bpy.ops.object.select_all(action="DESELECT")
    if action == 'SET':
        if obj != None:
            obj.hide_set(False)
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
        return obj
    elif action == 'GET':
        return bpy.context.active_object

def auto_bevel_segments(bevel=None, displace=None, revolver_obj=None):
    longueur = 1
    min_segments = 0
    if bevel:
        rayon = bevel.width
        longueur = math.pi*rayon/2

        if bpy.context.scene.fluentProp.min_auto_bevel_segments != 0:
            min_segments = bpy.context.scene.fluentProp.min_auto_bevel_segments
    if displace:
        rayon = displace.strength
        longueur = 2*math.pi*rayon

        if bpy.context.scene.fluentProp.min_auto_cylinder_segments != 0:
            min_segments = bpy.context.scene.fluentProp.min_auto_cylinder_segments
    if revolver_obj:
        rayon = 0
        for v in revolver_obj.data.vertices:
            if math.fabs(v.co.x) > rayon:
                rayon = math.fabs(v.co.x)
        longueur = 2 * math.pi * rayon

        if bpy.context.scene.fluentProp.min_auto_cylinder_segments != 0:
            min_segments = bpy.context.scene.fluentProp.min_auto_cylinder_segments

    segments = longueur*bpy.context.scene.fluentProp.model_resolution
    if segments < min_segments:
        segments = min_segments

    return math.ceil(segments)
