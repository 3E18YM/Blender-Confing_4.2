import bpy
import os
import json
from . import warning_info as wr

def update_mat_to_center(mesh_objs):

    mat_list = []
    wr_list = {}
    wr_list["renderer"] = "blender"
    wr_list["mat_data"] = []

    try:
        current_folder = os.path.dirname(os.path.abspath(__file__))
        with open(current_folder + '\\Material_dict.json') as json_file:
            mat_dict = json.load(json_file)
    except:
        return False

    m_indx = 0
    for mesh in mesh_objs:
        for m in mesh.material_slots:
            if m.name not in mat_list:  # check for mesh use same material
                mat_list.append(m.name)
                mat = m.material

                if mat:
                    wr_list["mat_data"].insert(m_indx, {"sg_name":mat.name})
                    if mat.node_tree:  # check for material have node
                        n_indx = 0
                        wr_list["mat_data"][m_indx]["node"] = []
                        wr_list["mat_data"][m_indx]["link"] = []
                        node_list = []


                        for m_link in mat.node_tree.links:  # store link data
                            if m_link.to_node.type in mat_dict["blender"] and m_link.from_node.type in mat_dict["blender"]:

                                #ADD_SHADER/MIX_SHADER have repeat input name ("shader") need to referance by array index
                                if m_link.to_node.type == "ADD_SHADER":

                                    if m_link.from_node.name == m_link.to_node.inputs[0].links[0].from_node.name:
                                        link_dat = {"input": {"node_name": m_link.to_node.name,"node_type": m_link.to_node.type, "att_name": "Shader_01"},
                                                    "output": {"node_name": m_link.from_node.name, "node_type": m_link.from_node.type ,"att_name": m_link.from_socket.name}}
                                        wr_list["mat_data"][m_indx]["link"].append(link_dat)
                                    else:
                                        link_dat = {"input": {"node_name": m_link.to_node.name,"node_type": m_link.to_node.type, "att_name": "Shader_02"},
                                                    "output": {"node_name": m_link.from_node.name, "node_type": m_link.from_node.type ,"att_name": m_link.from_socket.name}}
                                        wr_list["mat_data"][m_indx]["link"].append(link_dat)
                                
                                elif m_link.to_node.type == "MIX_SHADER":

                                    if m_link.from_node.name == m_link.to_node.inputs[1].links[0].from_node.name:
                                        link_dat = {"input": {"node_name": m_link.to_node.name,"node_type": m_link.to_node.type, "att_name": "Shader_01"},
                                                    "output": {"node_name": m_link.from_node.name, "node_type": m_link.from_node.type ,"att_name": m_link.from_socket.name}}
                                        wr_list["mat_data"][m_indx]["link"].append(link_dat)
                                    elif m_link.from_node.name == m_link.to_node.inputs[2].links[0].from_node.name:
                                        link_dat = {"input": {"node_name": m_link.to_node.name,"node_type": m_link.to_node.type, "att_name": "Shader_02"},
                                                    "output": {"node_name": m_link.from_node.name, "node_type": m_link.from_node.type ,"att_name": m_link.from_socket.name}}
                                        wr_list["mat_data"][m_indx]["link"].append(link_dat)
                                    else:
                                        link_dat = {"input": {"node_name": m_link.to_node.name,"node_type": m_link.to_node.type, "att_name": m_link.to_socket.name},
                                                "output": {"node_name": m_link.from_node.name, "node_type": m_link.from_node.type ,"att_name": m_link.from_socket.name}}                                    
                                        wr_list["mat_data"][m_indx]["link"].append(link_dat)
                                
                                else:
                                    link_dat = {"input": {"node_name": m_link.to_node.name,"node_type": m_link.to_node.type, "att_name": m_link.to_socket.name},
                                                "output": {"node_name": m_link.from_node.name, "node_type": m_link.from_node.type ,"att_name": m_link.from_socket.name}}
                                    wr_list["mat_data"][m_indx]["link"].append(link_dat)

                                if m_link.to_node.name not in node_list:#save node connected
                                    node_list.append(m_link.to_node.name)
                                if m_link.from_node.name not in node_list:
                                    node_list.append(m_link.from_node.name)

                        for m_node in mat.node_tree.nodes:
                            if m_node.name in node_list:  # get only connected node.
                                if m_node.type in mat_dict["blender"]:
                                    # check for have difinition in dictionary

                                    wr_list["mat_data"][m_indx]["node"].insert(n_indx, {"name": m_node.name})
                                    wr_list["mat_data"][m_indx]["node"][n_indx]["type"] = m_node.type

                                    #special extra info 
                                    if m_node.type == "TEX_IMAGE":
                                        if m_node.image:
                                            wr_list["mat_data"][m_indx]["node"][n_indx]["extra_info"] = {"filepath":bpy.path.abspath(m_node.image.filepath),"color_space": m_node.image.colorspace_settings.name }
                                        else:
                                            wr_list["mat_data"][m_indx]["node"][n_indx]["extra_info"] = {"filepath":None,"color_space": None }
                                    elif m_node.type == "BUMP":
                                        wr_list["mat_data"][m_indx]["node"][n_indx]["extra_info"] = {"normal_type": "BUMP" ,"Strength":m_node.inputs["Strength"].default_value}
                                    elif m_node.type == "NORMAL_MAP":
                                        wr_list["mat_data"][m_indx]["node"][n_indx]["extra_info"] = {"normal_type": "NORMAL" }

                                    at_indx = 0
                                    wr_list["mat_data"][m_indx]["node"][n_indx]["input_att"] = []

                                    for input_att in m_node.inputs:
                                        if input_att.name in mat_dict["blender"][m_node.type]["input_att"]:

                                            wr_list["mat_data"][m_indx]["node"][n_indx]["input_att"].insert(at_indx, {"name": input_att.name})
                                            if input_att.is_linked:
                                                n = input_att.links
                                                wr_list["mat_data"][m_indx]["node"][n_indx]["input_att"][at_indx]["type"] = "LINK"
                                                wr_list["mat_data"][m_indx]["node"][n_indx]["input_att"][at_indx]["value"] = n[0].from_node.type
                                            elif input_att.type == "VALUE":
                                                wr_list["mat_data"][m_indx]["node"][n_indx]["input_att"][at_indx]["type"] = "VALUE"
                                                wr_list["mat_data"][m_indx]["node"][n_indx]["input_att"][at_indx]["value"] = input_att.default_value
                                            elif input_att.type == "RGBA":
                                                wr_list["mat_data"][m_indx]["node"][n_indx]["input_att"][at_indx]["type"] = "RGB"
                                                wr_list["mat_data"][m_indx]["node"][n_indx]["input_att"][at_indx]["value"] = {
                                                    "red": input_att.default_value[0], "green": input_att.default_value[1], "blue": input_att.default_value[2]}
                                            elif input_att.type == "VECTOR":#for node Mapping/Texture Coordinate
                                                wr_list["mat_data"][m_indx]["node"][n_indx]["input_att"][at_indx]["type"] = "VECTOR"
                                                wr_list["mat_data"][m_indx]["node"][n_indx]["input_att"][at_indx]["value"] = {
                                                    "x": input_att.default_value[0], "y": input_att.default_value[1], "z": input_att.default_value[2]}
                                            
                                            at_indx += 1
                                        
                                    n_indx += 1                                

                    else:
                        print(mat.name + " materail don't have node")
                    m_indx += 1

    try:
        with open(bpy.context.window_manager.file_path + "BL_MaterialUpdate.json", "w") as file:
            json.dump(wr_list, file, indent=2, sort_keys=False)
    except:
        return False

    return True


def get_mat_from_mesh(mesh_objs):
    mat_list = []
    for mesh in mesh_objs:
        for m in mesh.material_slots:            
            if m.name not in mat_list:
                mat_list.append(m.name)   
                
    return mat_list
