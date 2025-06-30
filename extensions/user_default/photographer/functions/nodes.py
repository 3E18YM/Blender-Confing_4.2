import bpy, os

from ..constants import photographer_folder

def get_shader_node(parent,type,node_group_name='',node_name='',tag='',startswith=False):
    nodes = []
    if parent and parent.node_tree.nodes:
        nodes = parent.node_tree.nodes
        if node_group_name:
            if startswith:
                nodes=[n for n in nodes if n.bl_idname==type and n.node_tree.name.startswith(node_group_name)]
            else:
                nodes=[n for n in nodes if n.bl_idname==type and n.node_tree.name==node_group_name]
        elif node_name:
            if startswith:
                nodes=[n for n in nodes if n.bl_idname==type and n.name.startswith(node_name)]
            else:
                nodes=[n for n in nodes if n.bl_idname==type and n.name==node_name]
        elif tag:
            nodes=[n for n in nodes if n.bl_idname==type and n.get(tag,False)]
        else:
            nodes=[n for n in nodes if n.bl_idname==type]
    return nodes

def get_comp_group_node(context,name):
    scene = context.scene
    group_node = None
    if scene.use_nodes:
        nodes = scene.node_tree.nodes
        group_nodes=[n for n in nodes if n.bl_idname=='CompositorNodeGroup']
        for n in group_nodes:
            if n.node_tree and n.node_tree.name==name:
                group_node = n
                break
    return group_node

def get_comp_node_in_group(group, name):
    node = None
    if group:
        nodes =[n for n in group.node_tree.nodes if n.name==name]
        if nodes:
            node = nodes[0]
    return node

def get_old_exposure_node(context):
    scene = context.scene
    if scene.use_nodes:
        nodes = scene.node_tree.nodes
        exp = [n for n in nodes if n.bl_idname=='CompositorNodeExposure'
            and n.get('photographer_exposure',False)]
        if exp:
            return exp[0]
        else:
            return False

def delete_compositing_node(context,node_name):
    scene = context.scene
    nodes = scene.node_tree.nodes
    links = scene.node_tree.links
    # Find the node with the specified name
    node = nodes.get(node_name)

    if node is not None:
        # Store the links connected to the node's inputs and outputs
        input_links = []
        output_links = []

        # Iterate over input sockets
        for input_socket in node.inputs:
            for link in input_socket.links:
                input_links.append((link.from_node, link.from_socket))

        # Iterate over output sockets
        for output_socket in node.outputs:
            for link in output_socket.links:
                output_links.append((link.to_node, link.to_socket))

        # Remove the node from the tree
        nodes.remove(node)
        print("Old '{}' node was successfully deleted.".format(node_name))

       # Reconnect the stored links
        for from_node, from_socket in input_links:
            for to_node, to_socket in output_links:
                links.new(from_node.outputs[from_socket.name], to_node.inputs[to_socket.name])

def post_effects_cleanup(self,context, postfx_grp_name):
    old_pe_group_name = 'Photographer Camera Post FX'

    pe_grp = append_node_group(postfx_grp_name)

    scene = context.scene
    if scene.use_nodes:
        nodes = scene.node_tree.nodes
        old_pe_nodes = []
        group_nodes = [n for n in nodes if n.bl_idname=='CompositorNodeGroup']
        for n in group_nodes:
            if n.name==old_pe_group_name:
                old_pe_nodes.append(n)
            if n.node_tree:
                if n.node_tree.name.startswith('Photographer PostFX v') and n.node_tree.name!=postfx_grp_name:
                    old_pe_nodes.append(n)

        for n in old_pe_nodes:
           n.node_tree = pe_grp

    # Not a good implementation, let's remove it.
    # exp = get_old_exposure_node(context)
    # if exp:
    #     delete_compositing_node(context,exp.name)

    return None

def append_node_group(group_name,retrocompatible=False,do_reuse_local_id=True,startswith=False):

    # Define path based on retrocompatibility
    base_path = "blends/node_groups.blend/NodeTree/"
    if retrocompatible and bpy.app.version < (3, 4, 0):
        base_path = "blends/node_groups_3.3.blend/NodeTree/"

    # Construct full directory path
    directory = os.path.join(photographer_folder, base_path)

    # Normalize directory path
    directory = os.path.normpath(directory)

    # Check if the group already exists
    if do_reuse_local_id:
        if startswith:
            group = next((g for g in bpy.data.node_groups if g.name.startswith(group_name)), None)
        else:
            group = next((g for g in bpy.data.node_groups if g.name == group_name), None)
    else:
        group = None

    # Append group if it doesn't already exist
    if not group:
        bpy.ops.wm.append(filename=group_name, directory=directory, do_reuse_local_id=do_reuse_local_id)
        # Retrieve the appended group
        if startswith:
            group = next((g for g in bpy.data.node_groups if g.name.startswith(group_name)), None)
        else:
            group = next((g for g in bpy.data.node_groups if g.name == group_name), None)
        if not group:
            print('No node group was appended. The following operator may not execute properly.')

    return group