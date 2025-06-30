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

import os, shutil, bpy

bl_info = {
    "name": "Proxy picker",
    "author": "Max Hammond, Artell ",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    "location": "Properties Editor > Bone",
    "description": "Enables the proxy picker feature for the rig",     
    "category": "Animation"}

from . import proxy_picker

def cleanse_modules():
    import sys
    all_modules = sys.modules 
    all_modules = dict(sorted(all_modules.items(),key= lambda x:x[0]))
    for k in all_modules:
        if k.startswith(__name__):
            del sys.modules[k]
            
            
def register():
    proxy_picker.register()


def unregister():
    proxy_picker.unregister()    
    cleanse_modules()
    

if __name__ == "__main__":
    register()