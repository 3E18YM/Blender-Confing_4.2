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


from .dump_anything import Loader, Dumper
from .. import presence, operators, utils
from replication.protocol import ReplicatedDatablock
from .bl_datablock import resolve_datablock_from_uuid
from .bl_action import dump_animation_data, load_animation_data, resolve_animation_dependencies

def get_roll(bone: bpy.types.Bone) -> float:
    """ Compute the actuall roll of a pose bone

        :arg pose_bone: target pose bone
        :type pose_bone: bpy.types.PoseBone
        :return: float
    """
    return bone.AxisRollFromMatrix(bone.matrix_local.to_3x3())[1]


class BlArmature(ReplicatedDatablock):
    use_delta = True

    bl_id = "armatures"
    bl_class = bpy.types.Armature
    bl_check_common = False
    bl_icon = 'ARMATURE_DATA'
    bl_reload_parent = False

    @staticmethod
    def construct(data: dict) -> object:
        return bpy.data.armatures.new(data["name"])

    @staticmethod
    def load(data: dict, datablock: object):
        # Load parent object
        parent_object = utils.find_from_attr(
            'uuid',
            data['user'],
            bpy.data.objects
        )

        if parent_object is None:
            parent_object = bpy.data.objects.new(
                data['user_name'], datablock)
            parent_object.uuid = data['user']

        is_object_in_master = (
            data['user_collection'][0] == "Master Collection")
        # TODO: recursive parent collection loading
        # Link parent object to the collection
        if is_object_in_master:
            parent_collection = bpy.data.scenes[data['user_scene']
                                                [0]].collection
        elif data['user_collection'][0] not in bpy.data.collections.keys():
            parent_collection = bpy.data.collections.new(
                data['user_collection'][0])
        else:
            parent_collection = bpy.data.collections[data['user_collection'][0]]

        if parent_object.name not in parent_collection.objects:
            parent_collection.objects.link(parent_object)

        # Link parent collection to the scene master collection
        if not is_object_in_master and parent_collection.name not in bpy.data.scenes[data['user_scene'][0]].collection.children:
            bpy.data.scenes[data['user_scene'][0]
                            ].collection.  children.link(parent_collection)

        current_mode = bpy.context.mode
        current_active_object = bpy.context.view_layer.objects.active

        # LOAD ARMATURE BONES
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.view_layer.objects.active = parent_object

        bpy.ops.object.mode_set(mode='EDIT')

        for bone in data['bones']:
            if bone not in datablock.edit_bones:
                new_bone = datablock.edit_bones.new(bone)
            else:
                new_bone = datablock.edit_bones[bone]

            bone_data = data['bones'].get(bone)

            new_bone.tail = bone_data['tail_local']
            new_bone.head = bone_data['head_local']
            new_bone.tail_radius = bone_data['tail_radius']
            new_bone.head_radius = bone_data['head_radius']
            new_bone.roll =  bone_data['roll']
            
            if 'parent' in bone_data:
                new_bone.parent = datablock.edit_bones[data['bones']
                                                    [bone]['parent']]
                new_bone.use_connect = bone_data['use_connect']

            loader = Loader()
            loader.load(new_bone, bone_data)

        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.view_layer.objects.active = current_active_object

        # TODO: clean way to restore previous context
        if 'EDIT' in current_mode:
            bpy.ops.object.mode_set(mode='EDIT')

        load_animation_data(data.get('animation_data'), datablock)

    @staticmethod
    def dump(datablock: object) -> dict:
        dumper = Dumper()
        dumper.depth = 4
        dumper.include_filter = [
            'bones',
            'tail_local',
            'head_local',
            'tail_radius',
            'head_radius',
            'use_connect',
            'parent',
            'name',
            'layers',
        ]
        data = dumper.dump(datablock)

        for bone in datablock.bones:
            if bone.parent:
                data['bones'][bone.name]['parent'] = bone.parent.name
        # get the parent Object
        # TODO: Use id_data instead
        object_users = utils.get_datablock_users(datablock)[0]
        data['user'] = object_users.uuid
        data['user_name'] = object_users.name

        # get parent collection
        container_users = utils.get_datablock_users(object_users)
        data['user_collection'] = [
            item.name for item in container_users if isinstance(item, bpy.types.Collection)]
        data['user_scene'] = [
            item.name for item in container_users if isinstance(item, bpy.types.Scene)]

        for bone in datablock.bones:
            data['bones'][bone.name]['roll'] = get_roll(bone)

        data['animation_data'] = dump_animation_data(datablock)
        return data

    @staticmethod
    def resolve(data: dict) -> object:
        uuid = data.get('uuid')
        name = data.get('name')
        datablock = resolve_datablock_from_uuid(uuid, bpy.data.armatures)
        if datablock is None:
            datablock = bpy.data.armatures.get(name)

        return datablock

    @staticmethod
    def resolve_deps(datablock: object) -> [object]:
        return resolve_animation_dependencies(datablock)

_type = bpy.types.Armature
_class = BlArmature