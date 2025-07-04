# ##### BEGIN GPL LICENSE BLOCK #####
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
import os

from pathlib import Path
import bpy.utils.previews

def register():

    global icons_col

    pcoll = bpy.utils.previews.new()
    icons_dir = os.path.join(os.path.dirname(__file__), ".")
    for png in Path(icons_dir).rglob("*.png"):
        pcoll.load(png.stem, str(png), "IMAGE")

    icons_col = pcoll


def unregister():

    global icons_col

    try:
        bpy.utils.previews.remove(icons_col)
    except Exception:
        pass

    icons_col = None
