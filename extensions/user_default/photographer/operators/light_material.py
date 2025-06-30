import bpy, os, math
from .. import __package__ as base_package
from ..ui.library import enum_previews_from_directory_items, gobo_lib_path_update, ies_lib_path_update
from ..constants import HDR_FORMATS,MOVIE_FORMATS
from ..functions.functions import set_node_param
from ..functions.nodes import append_node_group
from bpy_extras.image_utils import load_image

LTC_VERSION = 1
AIV_VERSION = 1

light_tex_controls_grp_name = 'Light Textures Controls v' + str(LTC_VERSION)
area_ies_vector_grp_name = 'Area IES Vector v' + str(AIV_VERSION)
gobo_tex_name = 'Gobo Texture'
gobo_mapping_name = 'Gobo Mapping'
gobo_coord_name = 'Gobo Coordinates'
gobo_tangent_name = 'Gobo Tangent'
gobo_mult_scale_name = 'Gobo Scale'
gobo_mult_scale_y_name = 'Gobo Scale Y'
gobo_combine_scale_name = 'Gobo Combine Scale Vector'
gobo_mapping_area_name = 'Gobo Mapping Area'
gobo_geometry_name = 'Gobo Geometry'
ies_name = 'IES Texture'
falloff_name = 'Light Falloff'
emission_name = 'Lightmixer Emission'

def enum_previews_gobo(self, context):
    return enum_previews_from_directory_items(self, context,'gobo')

def update_gobo(self,context):
    light_name = [o.name for o in bpy.data.objects if o.type == 'LIGHT' and o.data is self.id_data][0]

    if self.gobo:
        bpy.ops.lightmixer.light_textures_add(light = light_name)
        ltc,aiv = get_light_tex_controls_groups(self.id_data)
        if ltc:
            ltc[0].inputs[0].default_value = 1.0
        update_gobo_tex(self,context)
        update_gobo_link_spot_size(self,None)
    else:
        ltc, aiv = get_light_tex_controls_groups(self.id_data)
        if ltc:
            ltc[0].inputs[0].default_value = 0.0
        

def update_gobo_tex(self,context):
    if self.gobo:
        light = self.id_data
        if light.use_nodes:
            nodes = light.node_tree.nodes
            for node in nodes:
                if type(node) is bpy.types.ShaderNodeTexImage:
                    if node.name == gobo_tex_name:
                        if self.gobo_tex != 'empty':
                            node.image = bpy.data.images.load(self.gobo_tex, check_existing=True)
                            image = node.image
                            if self.gobo_tex.lower().endswith(HDR_FORMATS):
                                colorspaces = ['Raw', 'Linear Rec.709']
                                for cs in colorspaces:
                                    try:
                                        image.colorspace_settings.name = cs
                                    except:
                                        pass
                            else:
                                colorspaces = ['sRGB', 'sRGB 2.2']
                                for cs in colorspaces:
                                    try:
                                        image.colorspace_settings.name = cs
                                    except:
                                        pass
                                if self.gobo_tex.lower().endswith(MOVIE_FORMATS):
                                    node.image_user.use_cyclic = True
                                    node.image_user.use_auto_refresh = True

                                    # Using bpy_utils load_image to retrieve movie information
                                    movie = load_image(os.path.basename(self.gobo_tex), os.path.dirname(self.gobo_tex), check_existing=True)
                                    node.image_user.frame_duration = movie.frame_duration

def update_gobo_category(self,context):
    if self.gobo:
        self['gobo_tex'] = 0
        update_gobo_tex(self,context)

def update_gobo_tex_repeat(self,context):
    light = self.id_data
    nodes = light.node_tree.nodes
    tex = nodes.get(gobo_tex_name)

    if tex is not None:
        if self.gobo_tex_repeat:
            tex.extension = 'REPEAT'
        else:
            tex.extension = 'EXTEND'

def update_gobo_link_spot_size(self, context):
    light = self.id_data
    nodes = light.node_tree.nodes
    links = light.node_tree.links

    mapping = nodes.get(gobo_mapping_name)
    combine_scale = nodes.get(gobo_combine_scale_name)

    if mapping is None:
        return

    if light.type != 'SPOT' or not self.gobo_link_spot_size:
        if mapping.inputs[3].is_linked:
            link = mapping.inputs[3].links[0]
            links.remove(link)
        return

    if combine_scale is not None:
        links.new(combine_scale.outputs[0], mapping.inputs[3])

def update_gobo_ies_area(self,context):
    light = self.id_data
    nodes = light.node_tree.nodes
    links = light.node_tree.links

    mapping = nodes.get(gobo_mapping_name)
    mapping_area = nodes.get(gobo_mapping_area_name)
    tex = nodes.get(gobo_tex_name)
    aiv = nodes.get(area_ies_vector_grp_name)
    ies = nodes.get(ies_name)

    if mapping_area and tex:
        if light.type == 'AREA':
            links.new(mapping_area.outputs[0], tex.inputs[0])
        elif mapping and tex:
            links.new(mapping.outputs[0], tex.inputs[0])
    if aiv and ies:
        if light.type == 'AREA':
            links.new(aiv.outputs[0], ies.inputs[0])
        else:
            for l in links:
                if l.to_socket == ies.inputs[0]:
                    links.remove(l)

def enum_previews_ies(self, context):
    return enum_previews_from_directory_items(self, context,'ies')

def update_ies(self,context):
    light_name = [o.name for o in bpy.data.objects if o.type == 'LIGHT' and o.data is self.id_data][0]

    if self.ies:
        bpy.ops.lightmixer.light_textures_add(light = light_name)
        ltc,aiv = get_light_tex_controls_groups(self.id_data)
        if ltc:
            ltc[0].inputs[3].default_value = 1.0
        update_ies_tex(self,context)
        update_gobo_ies_area(self,context)
    else:
        ltc,aiv = get_light_tex_controls_groups(self.id_data)
        if ltc:
            ltc[0].inputs[3].default_value = 0.0

def update_ies_tex(self,context):
    if self.ies:
        light = self.id_data
        if light.use_nodes:
            nodes = light.node_tree.nodes
            for node in nodes:
                if type(node) is bpy.types.ShaderNodeTexIES:
                    if node.name == ies_name:
                        if self.ies_tex != 'empty':
                            node.filepath = self.ies_tex

def update_ies_category(self,context):
    if self.ies:
        self['ies_tex'] = 0
        update_ies_tex(self,context)

def get_light_tex_controls_groups(light):
    light_tex_controls_grp = []
    area_ies_vector_grp = []
    if light.use_nodes:
        nodes = light.node_tree.nodes
        light_tex_controls_grp=[n for n in nodes if n.bl_idname=='ShaderNodeGroup' and n.node_tree.name==light_tex_controls_grp_name]
        area_ies_vector_grp=[n for n in nodes if n.bl_idname=='ShaderNodeGroup' and n.node_tree.name==area_ies_vector_grp_name]
    return light_tex_controls_grp,area_ies_vector_grp

def gobo_scale_apply(self):
    # Mapping
    if bpy.app.version < (4,0,0):
        gobo_scale_x = self.gobo_scale  * 2
        gobo_scale_y = self.gobo_scale * self.gobo_scale_y * 2
    else:
        gobo_scale_x = self.gobo_scale
        gobo_scale_y = self.gobo_scale * self.gobo_scale_y
    gobo_scale_z = 1.0
    gobo_scale = (gobo_scale_x,gobo_scale_y,gobo_scale_z)
    set_node_param(self.id_data,gobo_mapping_name,3,gobo_scale)

    # Mapping for Area Light
    gobo_scale_area_x = self.gobo_scale 
    gobo_scale_area_y = self.gobo_scale  * self.gobo_scale_y
    gobo_scale_area_z = 1.0
    gobo_scale_area = (gobo_scale_area_x,gobo_scale_area_y,gobo_scale_area_z)
    set_node_param(self.id_data,gobo_mapping_area_name,3,gobo_scale_area)

    # Multiply Scale when using Linked to Spot Size
    gobo_mult_scale = self.gobo_scale * 0.5
    set_node_param(self.id_data,gobo_mult_scale_name,0,gobo_mult_scale)

    # Multiply Scale Y when using Linked to Spot Size
    gobo_mult_scale_y = self.gobo_scale * self.gobo_scale_y * 0.5
    set_node_param(self.id_data,gobo_mult_scale_y_name,0,gobo_mult_scale_y)

def gobo_offset_apply(self):
    # Mapping
    if bpy.app.version < (4,0,0):
        gobo_offset_x = 0.5 - self.gobo_offset_x
        gobo_offset_y = 0.5 - self.gobo_offset_y
    else:
        gobo_offset_x = self.gobo_offset_x - ((self.gobo_scale-1) / 2)
        gobo_offset_y = self.gobo_offset_y - ((self.gobo_scale * self.gobo_scale_y -1) / 2)
    gobo_offset_z = 0
    gobo_offset = (gobo_offset_x, gobo_offset_y, gobo_offset_z)
    set_node_param(self.id_data,gobo_mapping_name,1,gobo_offset)

    # Mapping for Area Light
    gobo_area_offset_x = (self.gobo_scale-1)/-2 - self.gobo_offset_x
    gobo_area_offset_y = (self.gobo_scale * self.gobo_scale_y-1)/-2 - self.gobo_offset_y
    gobo_area_offset_z = 0
    gobo_area_offset = (gobo_area_offset_x, gobo_area_offset_y, gobo_area_offset_z)
    set_node_param(self.id_data,gobo_mapping_area_name,1,gobo_area_offset)

def get_gobo_scale(self):
    return self.get('gobo_scale', 1)

def set_gobo_scale(self, value):
    self['gobo_scale'] = value
    gobo_scale_apply(self)
    gobo_offset_apply(self)
    return None

def get_gobo_scale_y(self):
    return self.get('gobo_scale_y', 1)

def set_gobo_scale_y(self, value):
    self['gobo_scale_y'] = value
    gobo_scale_apply(self)
    gobo_offset_apply(self)
    return None

def get_gobo_offset_x(self):
    return self.get('gobo_offset_x', 0)

def set_gobo_offset_x(self, value):
    self['gobo_offset_x'] = value
    gobo_offset_apply(self)
    return None

def get_gobo_offset_y(self):
    return self.get('gobo_offset_y', 0)

def set_gobo_offset_y(self, value):
    self['gobo_offset_y'] = value
    gobo_offset_apply(self)
    return None

def get_gobo_opacity(self):
    return self.get('gobo_opacity', 1)

def set_gobo_opacity(self, value):
    self['gobo_opacity'] = value
    set_node_param(self.id_data,light_tex_controls_grp_name,2,value)
    return None

def get_ies_opacity(self):
    return self.get('ies_opacity', 1)

def set_ies_opacity(self, value):
    self['ies_opacity'] = value
    set_node_param(self.id_data,light_tex_controls_grp_name,5,value)
    return None

def get_light_falloff_smooth(self):
    return self.get('light_falloff_smooth', 0)

def set_light_falloff_smooth(self, value):
    self['light_falloff_smooth'] = value
    set_node_param(self.id_data,falloff_name,1,value)
    return None

class PHOTOGRAPHER_OT_Light_Textures_Add(bpy.types.Operator):
    bl_idname = "lightmixer.light_textures_add"
    bl_label = "Enable Gobo Texture"
    bl_description = "Adds Gobo texture to the Light material (Cycles Only)"
    bl_options = {'REGISTER', 'UNDO'}

    light: bpy.props.StringProperty()

    def execute(self,context):
        light_obj = bpy.data.objects[self.light]
        light = light_obj.data
        settings = light.photographer

        if not light.use_nodes:
            light.use_nodes = True

        nodes = light.node_tree.nodes
        links = light.node_tree.links

        output = emission = falloff = tangent = combine_scale = None
        img = mapping = coord = ies = mult_scale = mult_scale_y = None
        mapping_area = geometry = None

        for node in nodes:
            if isinstance(node, bpy.types.ShaderNodeOutputLight):
                output = node
            if isinstance(node, bpy.types.ShaderNodeEmission):
                if node.name == emission_name:
                    emission = node
            if isinstance(node, bpy.types.ShaderNodeTexImage):
                if node.name == gobo_tex_name:
                    img = node
            if isinstance(node, bpy.types.ShaderNodeMapping):
                if node.name == gobo_mapping_name:
                    mapping = node
                if node.name == gobo_mapping_area_name:
                    mapping_area = node
            if isinstance(node, bpy.types.ShaderNodeTexCoord):
                if node.name == gobo_coord_name:
                    coord = node
            if isinstance(node, bpy.types.ShaderNodeTexIES):
                if node.name == ies_name:
                    ies = node
            if isinstance(node, bpy.types.ShaderNodeLightFalloff):
                if node.name == falloff_name:
                    falloff = node
            if isinstance(node, bpy.types.ShaderNodeMath):
                if node.name == gobo_tangent_name:
                    tangent = node
                if node.name == gobo_mult_scale_name:
                    mult_scale = node
                if node.name == gobo_mult_scale_y_name:
                    mult_scale_y = node
            if isinstance(node, bpy.types.ShaderNodeCombineXYZ):
                if node.name == gobo_combine_scale_name:
                    combine_scale = node
            if isinstance(node, bpy.types.ShaderNodeNewGeometry):
                if node.name == gobo_geometry_name:
                    geometry = node

        if not output:
            output = nodes.new('ShaderNodeOutputLight')
        output.location = (800,0)
        if not emission:
            emission = nodes.new('ShaderNodeEmission')
        emission.location = (600,0)
        emission.name = emission_name     
        links.new(emission.outputs[0], output.inputs[0])

        # Gobo Image texture
        if not img:
            img = nodes.new('ShaderNodeTexImage')
            img.name = gobo_tex_name
            img.location = (0,0)
            if light.photographer.gobo_tex_repeat:
                img.extension = 'REPEAT'
            else:
                img.extension = 'EXTEND'
        img.mute = False

        # IES
        if not ies:
            ies = nodes.new('ShaderNodeTexIES')
            ies.name = ies_name
            ies.mode = 'EXTERNAL'
            ies.location = (100,-300)

        # Link to Spot Cone Angle nodes
        if not tangent:
            tangent = nodes.new('ShaderNodeMath')
            tangent.name = gobo_tangent_name
            tangent.operation = 'TANGENT'
            tangent.location = (-800,-300)
            tangent.inputs[0].default_value = (math.pi-settings.spot_size)/2

            # d = tangent.inputs[0].driver_add('default_value').driver
            # var = d.variables.new()
            # var.name = 'spot_size'
            # target = var.targets[0]
            # target.id_type = 'LIGHT'
            # target.id = light
            # target.data_path = 'photographer.spot_size'
            # d.expression = "(pi-spot_size)/2"

        if not mult_scale:
            mult_scale = nodes.new('ShaderNodeMath')
            mult_scale.name = gobo_mult_scale_name
            mult_scale.operation = 'MULTIPLY'
            mult_scale.location = (-600,-100)
            mult_scale.inputs[0].default_value = settings.gobo_scale * 0.5

            # d = mult_scale.inputs[0].driver_add('default_value').driver
            # var = d.variables.new()
            # var.name = 'gobo_scale'
            # target = var.targets[0]
            # target.id_type = 'LIGHT'
            # target.id = light
            # target.data_path = 'photographer.gobo_scale'
            # d.expression = "gobo_scale * 0.5"
        
        if not mult_scale_y:
            mult_scale_y = nodes.new('ShaderNodeMath')
            mult_scale_y.name = gobo_mult_scale_y_name
            mult_scale_y.operation = 'MULTIPLY'
            mult_scale_y.location = (-600,-300)
            mult_scale_y.inputs[0].default_value = settings.gobo_scale * settings.gobo_scale_y * 0.5

            # d = mult_scale_y.inputs[0].driver_add('default_value').driver
            # var = d.variables.new()
            # var.name = 'gobo_scale_y'
            # target = var.targets[0]
            # target.id_type = 'LIGHT'
            # target.id = light
            # target.data_path = 'photographer.gobo_scale_y'
            # var = d.variables.new()
            # var.name = 'gobo_scale'
            # target = var.targets[0]
            # target.id_type = 'LIGHT'
            # target.id = light
            # target.data_path = 'photographer.gobo_scale'
            # d.expression = "gobo_scale * gobo_scale_y * 0.5"

        if not combine_scale:
            combine_scale = nodes.new('ShaderNodeCombineXYZ')
            combine_scale.name = gobo_combine_scale_name
            combine_scale.location = (-400,-300)
            combine_scale.inputs[2].default_value = 1.0

        # Mapping
        if not mapping:
            mapping = nodes.new('ShaderNodeMapping')
            mapping.name = gobo_mapping_name
            mapping.location = (-200,0)
            # if bpy.app.version < (4,0,0):
            #     mapping.inputs[1].default_value[0] = 0.5 - settings.gobo_offset_x
            #     mapping.inputs[1].default_value[1] = 0.5 - settings.gobo_offset_y
            #     mapping.inputs[3].default_value[0] = settings.gobo_scale * 2
            #     mapping.inputs[3].default_value[1] = settings.gobo_scale * settings.gobo_scale_y * 2
            # else:
            #     mapping.inputs[1].default_value[0] = settings.gobo_offset_x
            #     mapping.inputs[1].default_value[1] = settings.gobo_offset_y
            #     mapping.inputs[3].default_value[0] = settings.gobo_scale
            #     mapping.inputs[3].default_value[1] = settings.gobo_scale * settings.gobo_scale_y        

            # fcurve_driver = mapping.inputs[3].driver_add('default_value')
            # drivers = [f.driver for f in fcurve_driver]
            # for d in drivers:
            #     var = d.variables.new()
            #     var.name = 'gobo_scale'
            #     target = var.targets[0]
            #     target.id_type = 'LIGHT'
            #     target.id = light
            #     target.data_path = 'photographer.gobo_scale'

            #     var = d.variables.new()
            #     var.name = 'gobo_scale_y'
            #     target = var.targets[0]
            #     target.id_type = 'LIGHT'
            #     target.id = light
            #     target.data_path = 'photographer.gobo_scale_y'
                
            # drivers[0].expression = "gobo_scale * 2"
            # drivers[1].expression = "gobo_scale * gobo_scale_y * 2"
            
             # Location driver
            # fcurve_driver = mapping.inputs[1].driver_add('default_value')
            # drivers = [f.driver for f in fcurve_driver]
            # for d in drivers:
            #     var = d.variables.new()
            #     var.name = 'gobo_offset_x'
            #     target = var.targets[0]
            #     target.id_type = 'LIGHT'
            #     target.id = light
            #     target.data_path = 'photographer.gobo_offset_x'

            #     var = d.variables.new()
            #     var.name = 'gobo_offset_y'
            #     target = var.targets[0]
            #     target.id_type = 'LIGHT'
            #     target.id = light
            #     target.data_path = 'photographer.gobo_offset_y'
                
            # drivers[0].expression = "0.5 - gobo_offset_x"
            # drivers[1].expression = "0.5 - gobo_offset_y"

        # Mapping Area
        if not mapping_area:
            mapping_area = nodes.new('ShaderNodeMapping')
            mapping_area.name = gobo_mapping_area_name
            mapping_area.location = (-200,400)
            # mapping_area.inputs[1].default_value[0] = (settings.gobo_scale-1)/-2 - settings.gobo_offset_x
            # mapping_area.inputs[1].default_value[1] = (settings.gobo_scale * settings.gobo_scale_y-1)/-2 - settings.gobo_offset_y
            # mapping_area.inputs[3].default_value[0] = settings.gobo_scale
            # mapping_area.inputs[3].default_value[1] = settings.gobo_scale * settings.gobo_scale_y

            # fcurve_driver = mapping_area.inputs[3].driver_add('default_value')
            # drivers = [f.driver for f in fcurve_driver]
            # for d in drivers:
            #     var = d.variables.new()
            #     var.name = 'gobo_scale'
            #     target = var.targets[0]
            #     target.id_type = 'LIGHT'
            #     target.id = light
            #     target.data_path = 'photographer.gobo_scale'

            #     var = d.variables.new()
            #     var.name = 'gobo_scale_y'
            #     target = var.targets[0]
            #     target.id_type = 'LIGHT'
            #     target.id = light
            #     target.data_path = 'photographer.gobo_scale_y'
                
            # drivers[0].expression = "gobo_scale"
            # drivers[1].expression = "gobo_scale * gobo_scale_y"

            # # Location driver
            # fcurve_driver = mapping_area.inputs[1].driver_add('default_value')
            # drivers = [f.driver for f in fcurve_driver]
            # for d in drivers:
            #     var = d.variables.new()
            #     var.name = 'gobo_scale'
            #     target = var.targets[0]
            #     target.id_type = 'LIGHT'
            #     target.id = light
            #     target.data_path = 'photographer.gobo_scale'

            #     var = d.variables.new()
            #     var.name = 'gobo_scale_y'
            #     target = var.targets[0]
            #     target.id_type = 'LIGHT'
            #     target.id = light
            #     target.data_path = 'photographer.gobo_scale_y'

            #     var = d.variables.new()
            #     var.name = 'gobo_offset_x'
            #     target = var.targets[0]
            #     target.id_type = 'LIGHT'
            #     target.id = light
            #     target.data_path = 'photographer.gobo_offset_x'

            #     var = d.variables.new()
            #     var.name = 'gobo_offset_y'
            #     target = var.targets[0]
            #     target.id_type = 'LIGHT'
            #     target.id = light
            #     target.data_path = 'photographer.gobo_offset_y'
                
            # drivers[0].expression = "(gobo_scale-1)/-2 - gobo_offset_x"
            # drivers[1].expression = "(gobo_scale * gobo_scale_y-1)/-2 - gobo_offset_y"

        # Coordinates
        if not coord:
            coord = nodes.new('ShaderNodeTexCoord') 
            coord.name = gobo_coord_name
            coord.location = (-400,0)

        # Geometry
        if not geometry:
            geometry = nodes.new('ShaderNodeNewGeometry') 
            geometry.name = gobo_geometry_name
            geometry.location = (-400,400)

        if not falloff:
            falloff = nodes.new('ShaderNodeLightFalloff') 
            falloff.name = falloff_name
            falloff.inputs[0].default_value = 1
            falloff.location = (300,-230)
            falloff.inputs[1].default_value = settings.light_falloff_smooth

        light_tex_controls_grp = append_node_group(light_tex_controls_grp_name, True)
        area_ies_vector_grp = append_node_group(area_ies_vector_grp_name, False)

        # Get node groups
        ltc, aiv = get_light_tex_controls_groups(light)
        if ltc:
            ltc = ltc[0]
        else:
            ltc = nodes.new('ShaderNodeGroup')
            ltc.name = light_tex_controls_grp_name
            ltc.node_tree = light_tex_controls_grp
            ltc.location = (300,000)
            ltc.inputs[2].default_value = settings.gobo_opacity
            ltc.inputs[5].default_value = settings.ies_opacity

        # Area IES Vector group
        if aiv:
            aiv = aiv[0]
        else:
            aiv = nodes.new('ShaderNodeGroup')
            aiv.name = area_ies_vector_grp_name
            aiv.node_tree = area_ies_vector_grp
            aiv.location = (-150,-400)

        # Connect them
        if bpy.app.version < (4,0,0):
            links.new(coord.outputs['Normal'], mapping.inputs['Vector'])
        else:
            links.new(coord.outputs['UV'], mapping.inputs['Vector'])
        links.new(geometry.outputs['Parametric'], mapping_area.inputs['Vector'])
        links.new(img.outputs[0], ltc.inputs[1])
        links.new(ies.outputs[0], ltc.inputs[4])
        links.new(ltc.outputs[0], emission.inputs[0])
        links.new(falloff.outputs[0], emission.inputs[1])
        links.new(tangent.outputs[0], mult_scale.inputs[1])
        links.new(tangent.outputs[0], mult_scale_y.inputs[1])
        links.new(mult_scale.outputs[0], combine_scale.inputs[0])
        links.new(mult_scale_y.outputs[0], combine_scale.inputs[1])
        if light.type == 'SPOT':
            if bpy.app.version < (4,0,0):
                if light.photographer.gobo_link_spot_size:
                    links.new(combine_scale.outputs[0], mapping.inputs[3])
            else:
                light.photographer.gobo_link_spot_size = False
                # if mapping.inputs[3].is_linked:
                #     links.remove(mapping.inputs[3].links[0])
        if light.type == 'AREA':
            links.new(mapping_area.outputs[0], img.inputs[0])
            links.new(aiv.outputs[0], ies.inputs[0])
        else:
            links.new(mapping.outputs[0], img.inputs[0])
            if mapping.inputs[3].is_linked:
                link = mapping.inputs[3].links[0]
                # Break the connection
                links.remove(link)
        
        gobo_scale_apply(light.photographer)
        gobo_offset_apply(light.photographer)
        # Keep light selected
        light_obj.select_set(True)


        return {'FINISHED'}

class PHOTOGRAPHER_OT_Reset_Intensity(bpy.types.Operator):
    bl_idname = "lightmixer.reset_intensity"
    bl_label = "Reset to IES Intensity"
    bl_description = "Resets Light Intensity to 1W in order to use the IES embedded intensity"
    bl_options = {'REGISTER', 'UNDO'}

    light: bpy.props.StringProperty()

    def execute(self,context):
        light = bpy.data.lights[self.light]
        preferences = context.preferences.addons[base_package].preferences

        if preferences.use_physical_lights:
            if light.type == 'SUN':
                light.photographer.sunlight_unit = 'irradiance'
                light.photographer.irradiance = 1.0
            else:
                light.photographer.light_unit = 'power'
                light.photographer.power = 1.0
        else:
            light.energy = 1.0

        return {'FINISHED'}
    
class PHOTOGRAPHER_OT_Refresh_Gobo_Categories(bpy.types.Operator):
    bl_idname = "photographer.refresh_gobo_categories"
    bl_label = "Refresh Gobo library"
    bl_description = "Updates Gobo textures, library subfolders and thumbnails"

    def execute(self, context):
        gobo_lib_path_update(self,context)
        return {'FINISHED'}

class PHOTOGRAPHER_OT_Refresh_IES_Categories(bpy.types.Operator):
    bl_idname = "photographer.refresh_ies_categories"
    bl_label = "Refresh IES library"
    bl_description = "Updates IES textures, library subfolders and thumbnails"

    def execute(self, context):
        ies_lib_path_update(self,context)
        return {'FINISHED'}