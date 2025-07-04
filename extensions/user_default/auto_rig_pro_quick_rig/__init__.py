# ***** BEGIN GPL LICENSE BLOCK *****
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****


bl_info = {
    "name": "Auto-Rig Pro: Quick Rig",
    "author": "Artell",
    "version": (1, 26, 46),
    "blender": (2, 80, 0),
    "location": "3D View > ARP> Auto-Rig Pro: Quick Rig",
    "description": "Generate quickly an Auto-Rig Pro armature from an existing skeleton (Auto-Rig Pro must be installed)",
    "category": "Animation",
    "wiki_url": "http://lucky3d.fr/auto-rig-pro/doc/quick_rig_doc.html",
    "tracker_url": "https://blendermarket.com/products/auto-rig-pro-quick-rig",    
    }



import bpy
from . import auto_rig_quick_prefs
from . import auto_rig_quick


def cleanse_modules():
    import sys
    all_modules = sys.modules 
    all_modules = dict(sorted(all_modules.items(),key= lambda x:x[0]))
    for k in all_modules:
        if k.startswith(__name__):
            del sys.modules[k]
            

def register():
    auto_rig_quick_prefs.register()
    auto_rig_quick.register()


def unregister():
    auto_rig_quick_prefs.unregister()
    auto_rig_quick.unregister()
    cleanse_modules()


if __name__ == "__main__":
    register()