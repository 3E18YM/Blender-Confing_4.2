import bpy
import os
import json

def Create_node_bl(n_cre_type, n_cre_name, mat, mat_dict):

    mat_comm = mat_dict["blender_command"]#load command for each node type.
    exist_node = mat.node_tree.nodes.get(n_cre_name)
    if not exist_node:                        
        cre_node = mat.node_tree.nodes.new(mat_comm[n_cre_type])
        cre_node.name = n_cre_name
    elif exist_node.type is not n_cre_type:
        mat.node_tree.nodes.remove(exist_node)
        cre_node = mat.node_tree.nodes.new(mat_comm[n_cre_type])
        cre_node.name = n_cre_name
    else:
        cre_node = exist_node

    if cre_node.type == "MAPPING":
        TexCoord_node = mat.node_tree.nodes.new("ShaderNodeTexCoord")
        mat.node_tree.links.new(TexCoord_node.outputs["UV"], cre_node.inputs["Vector"])
        TexCoord_node.location = (100, 100)
    return cre_node

def Set_node_att_bl(mat_dict, node_data, cre_node):
    n_data_type = node_data["type"]
    
    for in_att in node_data["input_att"]:        
        in_att_name = in_att["name"]
        if in_att_name in mat_dict["vray"][n_data_type]["input_att"]:
            in_att_name_bl = mat_dict["vray"][n_data_type]["input_att"][in_att_name]["blender"]

            if cre_node.inputs.get(in_att_name_bl):#Make sure attr exists
                in_att_bl = cre_node.inputs[in_att_name_bl]
                in_att_type_bl = in_att_bl.type
                
                if in_att["type"] != "LINK":
                    if in_att["type"] == "RGB":
                        if in_att_type_bl == "RGBA":
                            in_att_bl.default_value = (in_att["value"]["red"], in_att["value"]["green"], in_att["value"]["blue"], 1) 
                        elif in_att_type_bl == "VALUE":
                            in_att_bl.default_value = in_att["value"]["red"]
                    elif in_att["type"] == "VALUE":
                        if in_att_type_bl == "RGBA":
                            in_att_bl.default_value = (in_att["value"], in_att["value"], in_att["value"], 1)
                        elif in_att_type_bl == "VALUE":
                            in_att_bl.default_value = in_att["value"]
                    elif in_att["type"] == "VECTOR":#set value for place2dTexture Repeat U/V and Retate UV
                        in_att_bl.default_value = (in_att["value"]["x"], in_att["value"]["y"], in_att["value"]["z"])

    if n_data_type == "file":
        cre_node.image = bpy.data.images.load( node_data["extra_info"]["filepath"])        

def Link_node_att_bl(mat_dict, link_data, mat):

    out_name = link_data["output"]["node_name"]
    out_type = link_data["output"]["node_type"]
    out_att = link_data["output"]["att_name"]

    in_name = link_data["input"]["node_name"]
    in_type = link_data["input"]["node_type"]
    in_att = link_data["input"]["att_name"]
    
    try:
        if in_type == "shadingEngine":            
            att_out_name_bl = mat_dict["vray"][out_type]["output_att"][out_att]["blender"]
            att_in_name_bl = "Surface"
            in_node = mat.node_tree.nodes[in_name + "_Output"]              

        elif in_type == "VRayMtl":
            att_out_name_bl = mat_dict["vray"][out_type]["output_att"][out_att]["blender"]
            att_in_name_bl = mat_dict["vray"][in_type]["input_att"][in_att]["blender"]
            
            if att_in_name_bl == "Normal":
                n = mat.node_tree.nodes[in_name].inputs["Normal"].links
                nm_type = n[0].from_node.type
                if nm_type == "NORMAL_MAP":
                    in_node = mat.node_tree.nodes["nm" + in_name]
                    att_in_name_bl = "Color"
                elif nm_type == "BUMP":
                    in_node = mat.node_tree.nodes["bm" + in_name]
                    att_in_name_bl = "Height"   
            else:
                in_node = mat.node_tree.nodes[in_name]                    

        elif in_type == "VRayBlendMtl":
            att_out_name_bl = mat_dict["vray"][out_type]["output_att"][out_att]["blender"]         
            
            if in_att == "base_material":
                att_in_name_bl = 2
                in_node = mat.node_tree.nodes[in_name]     

            elif "coat_material" in in_att:
                att_in_name_bl = 1
                if in_att == "coat_material_0":       
                    in_node = mat.node_tree.nodes[in_name] 

                    if in_node.inputs[1].is_linked:#mix node middle slot is linked. use index because atts have repeat name
                        in_node = mat.node_tree.nodes[in_name + "_sub_1"]  
                        att_in_name_bl = 2                         
                else:
                    att_spt = in_att.split("_")
                    num_subfix  = int(att_spt[2])
                    att_in_name_bl = 1       

                    in_node = mat.node_tree.nodes[in_name + "_sub_" + str(num_subfix)] 

                    if in_node.inputs[1].is_linked:
                        in_node = mat.node_tree.nodes[in_name + "_sub_" + str(num_subfix + 1)] 
                        att_in_name_bl = 2   
            
            elif "blend_amount" in in_att:
                att_spt = in_att.split("_")
                num_subfix  = int(att_spt[2])
                att_in_name_bl = 0
                if in_att == "blend_amount_0":                     
                    in_node = mat.node_tree.nodes[in_name] 
                else:
                    in_node = mat.node_tree.nodes[in_name+ "_sub_" + str(num_subfix)] 

        else:
            att_out_name_bl = mat_dict["vray"][out_type]["output_att"][out_att]["blender"]
            att_in_name_bl = mat_dict["vray"][in_type]["input_att"][in_att]["blender"]
            in_node = mat.node_tree.nodes[in_name]  
                    

        out_node = mat.node_tree.nodes[out_name]   
        mat.node_tree.links.new(out_node.outputs[att_out_name_bl], in_node.inputs[att_in_name_bl])
    except:
        print("[" + out_name + "." + out_att + "]--->>[" + in_name + "." + in_att + "] :attribute is undefined in dictionary")

def get_mat_from_center():
    try:
        current_folder = os.path.dirname(os.path.abspath(__file__))
        with open(current_folder + '\\Material_dict.json') as json_file:
            mat_dict = json.load(json_file)
        with open(bpy.context.window_manager.file_path + 'MA_MaterialUpdate.json') as json_file:
            mat_list = json.load(json_file)
    except:
        return False

    for mat_data in mat_list["mat_data"]:#create output materail first        
        mat = bpy.data.materials.get(mat_data["sg_name"])
        if mat is None:
            mat = bpy.data.materials.new(name = mat_data["sg_name"]) 
        mat.use_nodes = True 

        #clear node unused
        node_name_list =  []
        node_name_list.append(mat_data["sg_name"])
        for node_data in mat_data["node"]:
            node_name_list.append(node_data["name"])
        for unuse_node in mat.node_tree.nodes:
            if unuse_node not in node_name_list:
                mat.node_tree.nodes.remove(unuse_node)        
        
        node_locate_x = 0  
        node_locate_y = 0   
        output_node_name = mat_data["sg_name"] + "_Output"
        output_node = mat.node_tree.nodes.get(output_node_name)#get exist material
        
        if not output_node:
            cre_node = Create_node_bl("OUTPUT_MATERIAL", output_node_name, mat, mat_dict) 
        elif output_node.type is not "OUTPUT_MATERIAL":
            mat.node_tree.nodes.remove(output_node)
            cre_node = Create_node_bl("OUTPUT_MATERIAL", output_node_name, mat, mat_dict)       

        for node_data in mat_data["node"]:
            n_data_type = node_data["type"]
            n_cre_type = mat_dict["vray"][n_data_type]["blender"]
            n_cre_name = node_data["name"]                      
            
            cre_node = Create_node_bl(n_cre_type, n_cre_name, mat, mat_dict)

            if cre_node.type == "BSDF_PRINCIPLED":#create node between normal socket and texture 
               for in_att_nm in node_data["input_att"]:
                    if in_att_nm["name"] == "bumpMap" and in_att_nm["type"] == "LINK":
                        if node_data["extra_info"]["normal_type"] == "NORMAL":
                            normal_node = Create_node_bl("NORMAL_MAP", "nm" + n_cre_name, mat, mat_dict)    
                            normal_node.inputs["Strength"].default_value =  node_data["extra_info"]["Strength"]  
                            mat.node_tree.links.new(normal_node.outputs["Normal"], cre_node.inputs["Normal"])
                        elif node_data["extra_info"]["normal_type"] == "BUMP":
                            bump_node = Create_node_bl("BUMP", "bm" + n_cre_name, mat, mat_dict) 
                            bump_node.inputs["Strength"].default_value =  node_data["extra_info"]["Strength"] 
                            mat.node_tree.links.new(bump_node.outputs["Normal"], cre_node.inputs["Normal"])   
                        break   
            elif cre_node.type == "MIX_SHADER":#create MIX_SHADER sub node for support more input
                cre_mix_count = 0
                for in_att in node_data["input_att"]:
                    if in_att["type"] == "LINK" and "coat_material" in in_att["name"]:
                        att_spt = in_att["name"].split("_")
                        num_subfix  = int(att_spt[2])
                        if num_subfix > cre_mix_count:
                            cre_mix_count = num_subfix
                
                mix_node_sub_list = []
                mix_node_base = cre_node
                mix_l_x = 0
                mix_l_y = 0
                for i in range(1, cre_mix_count+1):
                    mix_l_x += (-300)
                    mix_l_y += (30)
                    mix_node_sub = Create_node_bl("MIX_SHADER",n_cre_name + "_sub_" + str(i), mat, mat_dict)
                    mix_node_sub.location = (mix_l_x, mix_l_y)
                    mix_node_sub_list.append(mix_node_sub)
                   
                for mix_sub in mix_node_sub_list:
                    mat.node_tree.links.new(mix_sub.outputs["Shader"], mix_node_base.inputs[1])  
                    mix_node_base = mix_sub  

            cre_node.location = (node_locate_x, node_locate_y)
            node_locate_x += (-400)

            Set_node_att_bl(mat_dict, node_data, cre_node)

        for link_data in mat_data["link"]:  
            Link_node_att_bl(mat_dict, link_data, mat)                    

    return True
