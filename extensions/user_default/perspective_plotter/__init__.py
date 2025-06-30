# -*- coding: UTF-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "Perspective Plotter",
    "author" : "Mark Kingsnorth, iBlender@taobao.com",
    "description" : "Match a camera to an image with Perspective Plotter",
    "blender" : (3, 0, 0),
    "version" : (1, 2, 7),
    "location" : "",
    "warning" : "",
    "category" : "3D View",
    "doc_url": "https://blendermarket.com/products/perspective-plotter",
    "tracker_url": "https://item.taobao.com/item.htm?ft=t&id=671230166152"
}

if 'bpy' in locals():
    from importlib import reload
    import sys
    for k, v in list(sys.modules.items()):
        if k.startswith(__package__ + "."):
            try:
                reload(v)
            except Exception as e:
                print("Couldn't parse: {}".format(e))
                
import bpy

from . import property, ui, operators, preferences, keymaps, util
from bpy.app.handlers import persistent

@persistent
def load_handler(dummy):
    for obj in bpy.data.objects:
        if obj.type == 'CAMERA':
            try:
                obj.perspective_plotter.running_uuid = ''
            except AttributeError:
                pass

def register():
    
    preferences.register()
    property.register()
    ui.register()
    operators.register()
    keymaps.register_keymap()

    bpy.app.handlers.load_post.append(load_handler)


def unregister():

    bpy.app.handlers.load_post.remove(load_handler)

    keymaps.unregister_keymap()
    operators.unregister()
    ui.unregister()
    property.unregister()
    preferences.unregister()


