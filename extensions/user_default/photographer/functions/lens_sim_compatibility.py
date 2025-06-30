import bpy
from .nodes import get_shader_node

def is_lens_sim_cam(camera):
    for child in camera.children:
        # Check if the child is a mesh object
        if child.type == 'MESH':
            for mat in child.data.materials:
                if mat.name.startswith( 'LensSimMaterial' ):
                    camera['lens_sim_cam'] = True
                    camera['lens_sim_lens_obj'] = child
                    camera['lens_sim_mat'] = mat

def get_lens_sim_node(camera):
    mat = camera.get('lens_sim_mat',None)
    # mat = bpy.data.materials.get(camera['lens_sim_mat'],None)
    if mat:
        lens_sim = get_shader_node(mat,'ShaderNodeGroup',node_name='LensSim')
        if lens_sim:
            return lens_sim[0]
