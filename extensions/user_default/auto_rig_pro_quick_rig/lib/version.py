import bpy
import addon_utils

class ARP_blender_version:
    _string = bpy.app.version_string
    blender_v = bpy.app.version
    _float = blender_v[0]*100+blender_v[1]+blender_v[2]*0.01
    
blender_version = ARP_blender_version()


def get_quickrig_version():
    #addons = addon_utils.modules()[:]
    
    addons = None
    if bpy.app.version >= (4,2,0):
        addons = addon_utils.modules()
    else:
        addons = addon_utils.modules()[:]
    
    for addon in addons:    
        if addon.bl_info['name'].startswith('Auto-Rig Pro: Quick Rig'):
            print(addon)
            ver_list = addon.bl_info.get('version')
            ver_string = str(ver_list[0]) + str(ver_list[1]) + str(ver_list[2])
            ver_int = int(ver_string)
            return ver_int
            

def ver_int_to_str(version_int):
    to_str = str(version_int)
    return to_str[0] + '.' + to_str[1] + to_str[2] + '.' + to_str[3] + to_str[4]
    
    
def get_prefs():
    if bpy.app.version >= (4,2,0):
        return bpy.context.preferences.addons[__package__[:-4]].preferences
    else:
        return bpy.context.preferences.addons[__package__.split('.')[0]].preferences