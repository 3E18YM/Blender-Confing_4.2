import bpy
from .lib import *
from .ui import *
from .inits import *
from .typing import *
import bpy
class CBL_OT_ConvertCurveToGN(bpy.types.Operator):
    """"""
    bl_idname = "cbl.convert_curve_to_gn"
    bl_label = "Cablerator: Convert a Curve to a Geometry Node Object"
    bl_options = {"REGISTER", "UNDO"}
    @classmethod
    def poll(cls, context):
        return bpy.app.version >= (3, 1, 0) and context.selected_objects
    def get_selected_curve_data(self, obs):
        return [{"ob": ob, "bevel_depth": ob.data.bevel_depth,
            "bevel_resolution": ob.data.bevel_resolution,
            "resolution_u": ob.data.resolution_u,
            "bevel_mode": ob.data.bevel_mode,
            "bevel_object": ob.data.bevel_object,
            "use_fill_caps": ob.data.use_fill_caps} for ob in obs if ob.type == 'CURVE']
    def get_node_by_type(self,nodes,node_type):
        return next(iter(node for node in nodes if node.type == node_type), None)
    def get_cbl_node_group(self):
        group_name = "cablerator_geometry_curve"
        if group_name in bpy.data.node_groups:
            group =  bpy.data.node_groups[group_name]
            nodes = group.nodes
            links = group.links
            group_input = self.get_node_by_type(nodes,'GROUP_INPUT')
            node_circle = self.get_node_by_type(nodes,'CURVE_PRIMITIVE_CIRCLE')
            node_object = self.get_node_by_type(nodes,'OBJECT_INFO')
            node_curve_to_mesh = self.get_node_by_type(nodes,'CURVE_TO_MESH')
            node_reroute = self.get_node_by_type(nodes,'REROUTE')
        else:
            group = bpy.data.node_groups.new(group_name, 'GeometryNodeTree')
            ser_node = '{"46f4ef24a73f48b6b090561860f8f084": {"name": "Curve Circle", "location": [0.0, 0.0], "type": "GeometryNodeCurvePrimitiveCircle", "inputs": [[0, 32], [1, [-1.0, 0.0, 0.0]], [2, [0.0, 1.0, 0.0]], [3, [1.0, 0.0, 0.0]], [4, 1.0]], "outputs": [[0, null, [[14, "81230cd479b54f739f5eb1f2dcb82ae6"]]], [1, [0.0, 0.0, 0.0]]], "props": [{"height": 100.0}, {"hide": false}, {"mode": "RADIUS"}, {"width": 140.0}, {"width_hidden": 100.0}]}, "5afb9c5a697f4ef5a75390acd10de46a": {"name": "Group Output", "location": [860.0, 260.0], "type": "NodeGroupOutput", "inputs": [[0, null, [[0, "6cb6cf01a8194cf38122d90ff81e13f6"]]]], "outputs": [], "props": [{"height": 100.0}, {"hide": false}, {"is_active_output": true}, {"width": 140.0}, {"width_hidden": 80.0}]}, "6cb6cf01a8194cf38122d90ff81e13f6": {"name": "Curve to Mesh", "location": [640.0, 200.0], "type": "GeometryNodeCurveToMesh", "inputs": [[0, null, [[0, "d93b152b30454d52b1833c4e52860ace"]]], [1, null, [[0, "f404eacaf7b94f9e9f0ec7ff3794e9e6"]]], [2, false]], "outputs": [[0, null, [[0, "5afb9c5a697f4ef5a75390acd10de46a"]]]], "props": [{"height": 100.0}, {"hide": false}, {"width": 140.0}, {"width_hidden": 100.0}]}, "f404eacaf7b94f9e9f0ec7ff3794e9e6": {"name": "Transform", "location": [400.0, 80.0], "type": "GeometryNodeTransform", "inputs": [[0, null, [[6, "81230cd479b54f739f5eb1f2dcb82ae6"]]], [1, [0.0, 0.0, 0.0]], [2, [0.0, 0.0, 0.0]], [3, [1.0, 1.0, 1.0], [[3, "15230c8f937748459b54ccf4e4307ddc"]]]], "outputs": [[0, null, [[1, "6cb6cf01a8194cf38122d90ff81e13f6"]]]], "props": [{"height": 100.0}, {"hide": false}, {"width": 140.0}, {"width_hidden": 100.0}]}, "393e51f8505f41379fc41617957e1ab2": {"name": "Object Info", "location": [0.0, -140.0], "type": "GeometryNodeObjectInfo", "inputs": [[0, null], [1, false]], "outputs": [[0, [0.0, 0.0, 0.0]], [1, [0.0, 0.0, 0.0]], [2, [0.0, 0.0, 0.0], [[9, "15230c8f937748459b54ccf4e4307ddc"]]], [3, null, [[15, "81230cd479b54f739f5eb1f2dcb82ae6"]]]], "props": [{"height": 100.0}, {"hide": false}, {"transform_space": "ORIGINAL"}, {"width": 140.0}, {"width_hidden": 100.0}]}, "1c80bb5bba384eef94ca8d580fba5bec": {"name": "Reroute", "location": [140.0, 100.0], "type": "NodeReroute", "inputs": [[0, false]], "outputs": [[0, false, [[1, "81230cd479b54f739f5eb1f2dcb82ae6"], [0, "15230c8f937748459b54ccf4e4307ddc"]]]], "props": [{"height": 100.0}, {"hide": false}, {"width": 16.0}, {"width_hidden": 100.0}]}, "d93b152b30454d52b1833c4e52860ace": {"name": "Group Input", "location": [-240.0, 240.0], "type": "NodeGroupInput", "inputs": [], "outputs": [[0, null, [[0, "6cb6cf01a8194cf38122d90ff81e13f6"]]]], "props": [{"height": 100.0}, {"hide": false}, {"width": 140.0}, {"width_hidden": 80.0}]}, "81230cd479b54f739f5eb1f2dcb82ae6": {"name": "Switch", "location": [200.0, 60.0], "type": "GeometryNodeSwitch", "inputs": [[0, false], [1, false, [[0, "1c80bb5bba384eef94ca8d580fba5bec"]]], [2, 0.0], [3, 0.0], [4, 0], [5, 0], [6, false], [7, true], [8, [0.0, 0.0, 0.0]], [9, [0.0, 0.0, 0.0]], [10, [0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0]], [11, [0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0]], [12, ""], [13, ""], [14, null, [[0, "46f4ef24a73f48b6b090561860f8f084"]]], [15, null, [[3, "393e51f8505f41379fc41617957e1ab2"]]], [16, null], [17, null], [18, null], [19, null], [20, null], [21, null], [22, null], [23, null], [24, null], [25, null]], "outputs": [[0, 0.0], [1, 0], [2, false], [3, [0.0, 0.0, 0.0]], [4, [0.0, 0.0, 0.0, 0.0]], [5, ""], [6, null, [[0, "f404eacaf7b94f9e9f0ec7ff3794e9e6"]]], [7, null], [8, null], [9, null], [10, null], [11, null]], "props": [{"height": 100.0}, {"hide": false}, {"input_type": "GEOMETRY"}, {"width": 140.0}, {"width_hidden": 100.0}]}, "15230c8f937748459b54ccf4e4307ddc": {"name": "Switch.001", "location": [195.5906219482422, -120.74932861328125], "type": "GeometryNodeSwitch", "inputs": [[0, false, [[0, "1c80bb5bba384eef94ca8d580fba5bec"]]], [1, false], [2, 0.0], [3, 0.0], [4, 0], [5, 0], [6, false], [7, true], [8, [1.0, 1.0, 1.0]], [9, [0.0, 0.0, 0.0], [[2, "393e51f8505f41379fc41617957e1ab2"]]], [10, [0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0]], [11, [0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0]], [12, ""], [13, ""], [16, null], [17, null], [18, null], [19, null], [20, null], [21, null], [22, null], [23, null], [24, null], [25, null]], "outputs": [[0, 0.0], [1, 0], [2, false], [3, [0.0, 0.0, 0.0], [[3, "f404eacaf7b94f9e9f0ec7ff3794e9e6"]]], [4, [0.0, 0.0, 0.0, 0.0]], [5, ""], [7, null], [8, null], [9, null], [10, null], [11, null]], "props": [{"height": 100.0}, {"hide": false}, {"input_type": "VECTOR"}, {"width": 140.0}, {"width_hidden": 100.0}]}}'
            bpy.temp_string_serializer = [[0, 0], group, ser_node]
            bpy.ops.cbl.deserialize_node('INVOKE_DEFAULT')
            nodes = group.nodes
            links = group.links
            group_input = self.get_node_by_type(nodes,'GROUP_INPUT')
            node_circle = self.get_node_by_type(nodes,'CURVE_PRIMITIVE_CIRCLE')
            node_object = self.get_node_by_type(nodes,'OBJECT_INFO')
            node_curve_to_mesh = self.get_node_by_type(nodes,'CURVE_TO_MESH')
            node_reroute = self.get_node_by_type(nodes,'REROUTE')
            links.new(group_input.outputs[1], node_circle.inputs[4])
            links.new(group_input.outputs[2], node_circle.inputs[0])
            links.new(group_input.outputs[3], node_object.inputs[0])
            links.new(group_input.outputs[4], node_reroute.inputs[0])
            links.new(group_input.outputs[5], node_curve_to_mesh.inputs[2])
            group.inputs[1].name = "Circle Radius"
            group.inputs[2].name = "Circle Resolution"
            group.inputs[3].name = "Bevel Object"
            group.inputs[4].name = "Use Object as a Profile"
            group.inputs[5].name = "Fill Caps"
        return [group_input, node_circle, node_object, node_curve_to_mesh, node_reroute, group]
    def execute(self, context):
        self.obs = self.get_selected_curve_data(context.selected_objects)
        if not self.obs:
            self.report(
                {'ERROR'},
                "No valid curve objects were found among the selected objects, Aborting",
            )
            return {'CANCELLED'}
        for obj in self.obs:
            curve, bevel_depth, bevel_resolution, resolution_u, bevel_mode, bevel_object, use_fill_caps = obj.values()
            if obj["bevel_mode"] == 'OBJECT':
                curve.data.bevel_object = None
            curve.data.bevel_depth = 0
            geo_mod = curve.modifiers.new(name='Cablerator GN',type='NODES')
            group_input, node_circle, node_object, node_curve_to_mesh, node_reroute, geo_group = self.get_cbl_node_group()
            geo_mod.node_group = geo_group
            if bevel_mode == 'OBJECT':
                geo_mod["Input_5"] = 1
                geo_mod["Input_4"] = bevel_object
            elif bevel_mode == 'ROUND':
                geo_mod["Input_5"] = 0
                geo_mod["Input_3"] = math.ceil(linear(bevel_resolution, 0, 6, 4, 16))
                geo_mod["Input_2"] = bevel_depth
            geo_mod["Input_6"] = use_fill_caps
            curve.update_tag()
        return {'FINISHED'}
def register():
    bpy.utils.register_class(CBL_OT_ConvertCurveToGN)
def unregister():
    bpy.utils.unregister_class(CBL_OT_ConvertCurveToGN)