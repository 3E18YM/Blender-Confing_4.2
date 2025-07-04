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
import mathutils
import logging

from .dump_anything import Loader, Dumper
from replication.protocol import ReplicatedDatablock
from .bl_datablock import resolve_datablock_from_uuid

class BlLightprobe(ReplicatedDatablock):
    use_delta = True

    bl_id = "lightprobes"
    bl_class = bpy.types.LightProbe
    bl_check_common = False
    bl_icon = 'LIGHTPROBE_GRID'
    bl_reload_parent = False

    @staticmethod
    def construct(data: dict) -> object:
        type = 'CUBE' if data['type'] == 'CUBEMAP' else data['type']
        # See https://developer.blender.org/D6396
        if bpy.app.version >= (2,83,0):
            return bpy.data.lightprobes.new(data["name"], type)
        else:
            logging.warning("Lightprobe replication only supported since 2.83. See https://developer.blender.org/D6396")

    @staticmethod
    def load(data: dict, datablock: object):
        loader = Loader()
        loader.load(datablock, data)

    @staticmethod
    def dump(datablock: object) -> dict:
        if bpy.app.version < (2,83,0):
            logging.warning("Lightprobe replication only supported since 2.83. See https://developer.blender.org/D6396")

        dumper = Dumper()
        dumper.depth = 1
        dumper.include_filter = [
            "name",
            'type',
            'influence_type',
            'influence_distance',
            'falloff',
            'intensity',
            'clip_start',
            'clip_end',
            'visibility_collection',
            'use_custom_parallax',
            'parallax_type',
            'parallax_distance',
            'grid_resolution_x',
            'grid_resolution_y',
            'grid_resolution_z',
            'visibility_buffer_bias',
            'visibility_bleed_bias',
            'visibility_blur'
        ]

        return dumper.dump(datablock)

    @staticmethod
    def resolve(data: dict) -> object:
        uuid = data.get('uuid') 
        return resolve_datablock_from_uuid(uuid, bpy.data.lightprobes)

    @staticmethod
    def resolve_deps(datablock: object) -> [object]:
        return []

_type = bpy.types.LightProbe
_class = BlLightprobe