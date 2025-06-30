import bpy, os, bgl, math, gpu, blf
from .. import __package__ as base_package
from ..ui.library import enum_previews_from_directory_items, hdri_lib_path_update
from ..properties.node import get_em_strength
from ..properties.post_effects import postfx_grp_name
from ..functions.nodes import append_node_group, get_shader_node, get_comp_group_node,get_comp_node_in_group
from ..functions.meshes import append_mesh
from ..functions.functions import create_unique_name, read_pixel_color, rgb_to_luminance, show_message
from .autofocus import hide_focus_planes
from ..constants import DEFAULT_COLOR_TEMPERATURE

wb_name = 'White Balance'
WD_MP_VERSION = 2
WD_CC_VERSION = 3
WD_BG_VERSION = 1
mapping_grp_name = 'World Mapping v' + str(WD_MP_VERSION)
color_controls_name = 'World Color Controls v' + str(WD_CC_VERSION)
background_color_name = 'Background Color v' + str(WD_BG_VERSION)

HDRI_GD_VERSION = 2
hdri_ground_grp_name = 'HDRI Ground v' + str(HDRI_GD_VERSION)
hdri_dome_mesh_name = 'HDRI_Dome'
hdri_cylinder_mesh_name = 'HDRI_Cylinder'
hdri_cube_mesh_name = 'HDRI_Cube'

def get_mapping_groups(context):
    return get_shader_node(context.scene.world,'ShaderNodeGroup',mapping_grp_name)

def get_color_controls_groups(context):
    return get_shader_node(context.scene.world,'ShaderNodeGroup',color_controls_name)

def get_background_color_groups(context):
    return get_shader_node(context.scene.world,'ShaderNodeGroup',background_color_name)

def get_hdri_ground_object(wd_lightmixer=None):
    if wd_lightmixer:
        gp_name = wd_lightmixer.get('hdri_ground',None)
        if gp_name:
            gp = bpy.data.objects.get(gp_name,None)
            if gp:
                return gp
            else:
                return None

def get_hdri_ground_groups(affect_ground=True,wd_lightmixer=None):
    ground_tex = ground_mapping = ground_color = ground_bgc = []
    gp = get_hdri_ground_object(wd_lightmixer)
    if gp:
        if affect_ground==False and gp.data.materials[0].get('is_hdri_ground_mat'):
            pass
        else:
            hg_grp = get_shader_node(gp.data.materials[0],'ShaderNodeGroup',tag='hdri_ground_node')
            if hg_grp:
                ground_tex = get_shader_node(hg_grp[0],'ShaderNodeTexEnvironment')[0]
                ground_mapping = get_shader_node(hg_grp[0],'ShaderNodeGroup',None,'world_mapping')[0]
                ground_color = get_shader_node(hg_grp[0],'ShaderNodeGroup',None,'ground_color_controls')[0]
                ground_bgc = get_shader_node(hg_grp[0],'ShaderNodeGroup',None,'ground_bg_color',startswith=True)

    return ground_tex, ground_mapping, ground_color, ground_bgc

def get_hdri_ground_node(wd_lightmixer=None):
    gp = get_hdri_ground_object(wd_lightmixer)
    if gp:
        hg_nodes = get_shader_node(gp.data.materials[0],'ShaderNodeGroup',tag='hdri_ground_node')
        if hg_nodes:
            return hg_nodes[0]

def get_hdri_rotation(self):
    return self.get('hdri_rotation',  0)

def set_hdri_rotation(self,value):
    world = bpy.context.scene.world
    if world and world.get('is_world_hdri',False):
        self['hdri_rotation'] = value
        mappings = get_mapping_groups(bpy.context)
        for n in mappings:
            n.inputs[1].default_value=value
            world['hdri_rotation']=value
        _,ground_mapping,_,_ = get_hdri_ground_groups(wd_lightmixer=self)
        if ground_mapping:
            ground_mapping.inputs[1].default_value=value
    return None

def get_hdri_blur(self):
    return self.get('hdri_blur',  0)

def set_hdri_blur(self,value):
    self['hdri_blur'] = value
    mappings = get_mapping_groups(bpy.context)
    for n in mappings:
        n.inputs[2].default_value=value
    _, ground_mapping, _, _ = get_hdri_ground_groups(wd_lightmixer=self)
    if ground_mapping:
        ground_mapping.inputs[2].default_value=value
    return None

def get_hdri_horizon_level(self):
    return self.get('hdri_horizon_level',  0)

def set_hdri_horizon_level(self,value):
    self['hdri_horizon_level'] = value
    mappings = get_mapping_groups(bpy.context)
    for n in mappings:
        n.inputs[0].default_value=value
    _, ground_mapping, _,_ = get_hdri_ground_groups(wd_lightmixer=self)
    if ground_mapping:
        ground_mapping.inputs[0].default_value=value
    return None

def get_hdri_projection_height(self):
    return self.get('hdri_projection_height',  1.5)

def set_hdri_projection_height(self,value):
    self['hdri_projection_height'] = value
    _, ground_mapping,_,_ = get_hdri_ground_groups(wd_lightmixer=self)
    if ground_mapping:
        ground_mapping.inputs[6].default_value=value
    return None

def get_hdri_temperature(self):
    return self.get('hdri_temperature',  DEFAULT_COLOR_TEMPERATURE)

def set_hdri_temperature(self,value):
    self['hdri_temperature'] = value
    cc = get_color_controls_groups(bpy.context)
    for n in cc:
        n.inputs[1].default_value=value
    _,_, ground_color,_ = get_hdri_ground_groups(affect_ground=False,wd_lightmixer=self)
    if ground_color:
        ground_color.inputs[1].default_value=value
    return None

def get_hdri_tint(self):
    return self.get('hdri_tint', 0)

def set_hdri_tint(self,value):
    self['hdri_tint'] = value
    cc = get_color_controls_groups(bpy.context)
    for n in cc:
        n.inputs[2].default_value=value
    _,_,ground_color,_ = get_hdri_ground_groups(affect_ground=False,wd_lightmixer=self)
    if ground_color:
        ground_color.inputs[2].default_value=value
    return None

def update_hdri_use_temperature(self,context):
    cc = get_color_controls_groups(context)
    _,_, ground_color,_ = get_hdri_ground_groups(affect_ground=False,wd_lightmixer=self)
    for n in cc:
        if self.hdri_use_temperature:
            n.inputs['Use Temperature'].default_value=1
            if ground_color:
                ground_color.inputs['Use Temperature'].default_value=1
        else:
            n.inputs['Use Temperature'].default_value=0
            if ground_color:
                ground_color.inputs['Use Temperature'].default_value=0


def get_hdri_hue(self):
    return self.get('hdri_hue',  0.5)

def set_hdri_hue(self,value):
    self['hdri_hue'] = value
    cc = get_color_controls_groups(bpy.context)
    for n in cc:
        n.inputs[3].default_value=value
    _,_, ground_color,_ = get_hdri_ground_groups(wd_lightmixer=self)
    if ground_color:
        ground_color.inputs[3].default_value=value
    return None

def get_hdri_saturation(self):
    return self.get('hdri_saturation',  1.0)

def set_hdri_saturation(self,value):
    self['hdri_saturation'] = value
    cc = get_color_controls_groups(bpy.context)
    for n in cc:
        n.inputs[4].default_value=value
    _,_, ground_color,_ = get_hdri_ground_groups(wd_lightmixer=self)
    if ground_color:
        ground_color.inputs[4].default_value=value
    return None

def get_hdri_value(self):
    return self.get('hdri_value',  1.0)

def set_hdri_value(self,value):
    self['hdri_value'] = value
    cc = get_color_controls_groups(bpy.context)
    for n in cc:
        n.inputs[5].default_value=value
    _,_, ground_color,_= get_hdri_ground_groups(wd_lightmixer=self)
    if ground_color:
        ground_color.inputs[5].default_value=value
    return None

def get_hdri_exposure_comp(self):
    return self.get('hdri_exposure_comp',  0.0)

def set_hdri_exposure_comp(self,value):
    self['hdri_exposure_comp'] = value
    cc = get_color_controls_groups(bpy.context)
    for n in cc:
        n.inputs['Exposure Compensation'].default_value=value
    _,_, ground_color,_= get_hdri_ground_groups(wd_lightmixer=self)
    if ground_color:
        ground_color.inputs['Exposure Compensation'].default_value=value
    return None

def get_hdri_clamp(self):
    return self.get('hdri_clamp',  0.0)

def set_hdri_clamp(self,value):
    self['hdri_clamp'] = value
    cc = get_color_controls_groups(bpy.context)
    for n in cc:
        n.inputs['Clamp Max'].default_value=value
        clamp = get_shader_node(n,'ShaderNodeGroup',node_name='hdri_clamp')
        if clamp:
            if self.hdri_clamp <= 0:
                clamp[0].mute = True
            else:
                clamp[0].mute = False
    _,_, ground_color,_= get_hdri_ground_groups(wd_lightmixer=self)
    if ground_color:
        ground_color.inputs['Clamp Max'].default_value=value
        clamp = get_shader_node(ground_color,'ShaderNodeGroup',node_name='hdri_clamp')
        if clamp:
            if self.hdri_clamp <= 0:
                clamp[0].mute = True
            else:
                clamp[0].mute = False
    return None

def get_hdri_color(self):
    return self.get('hdri_color',  (1.0,1.0,1.0,1.0))

def set_hdri_color(self,value):
    self['hdri_color'] = value
    cc = get_color_controls_groups(bpy.context)
    for n in cc:
        n.inputs[6].default_value=value
    _,_, ground_color,_ = get_hdri_ground_groups(affect_ground=False,wd_lightmixer=self)
    if ground_color:
        ground_color.inputs[6].default_value=value
    return None

def get_hdri_ground_emissive(self):
    return self.get('hdri_ground_emissive', 1.0)

def set_hdri_ground_emissive(self,value):
    self['hdri_ground_emissive'] = value
    hg_node = get_hdri_ground_node(self)
    if hg_node:
        hg_node.inputs[5].default_value=value
    backgrounds = get_shader_node(bpy.context.scene.world,'ShaderNodeBackground')
    for bg in backgrounds:
        bg.inputs[1].default_value = value
    return None

def get_bg_color(self):
    return self.get('bg_color',  (1.0,1.0,1.0,1.0))

def set_bg_color(self,value):
    context = bpy.context
    self['bg_color'] = value
    bgc = get_background_color_groups(context)
    for n in bgc:
        n.inputs['BG Color'].default_value=value
    _,_,_, ground_bgc = get_hdri_ground_groups(wd_lightmixer=self)
    for n in ground_bgc:
        n.inputs['BG Color'].default_value = value
    return None

def get_bg_color_opacity(self):
    return self.get('bg_color_opacity',  0.0)

def set_bg_color_opacity(self,value):
    self['bg_color_opacity'] = value
    bgc = get_background_color_groups(bpy.context)
    for n in bgc:
        n.inputs['BG Color Opacity'].default_value=value
    _,_,_, ground_bgc = get_hdri_ground_groups(wd_lightmixer=self)
    for n in ground_bgc:
        n.inputs['BG Color Opacity'].default_value=value
    return None

def update_film_transparent_override(self,context):
    if self.film_transparent_override:
        context.scene.render.film_transparent = self.film_transparent
    return None

def get_film_transparent(self):
    return self.get('film_transparent', False)

def set_film_transparent(self,value):
    self['film_transparent'] = value
    if self.get('film_transparent_override',False):
        bpy.context.scene.render.film_transparent = self.film_transparent
    return None

def enum_previews_hdri_tex(self, context):
    # print (enum_previews_from_directory_items(self, context,'hdri'))
    return enum_previews_from_directory_items(self, context,'hdri')

def update_cam_world(self,context,world):
    # Update Cam World for Override
    if context.scene.camera:
        settings = context.scene.camera.data.photographer
        settings.cam_world = world
        context.scene.lightmixer.hdri_rotation = world.get('hdri_rotation',0)
        return settings.cam_world

def update_hdri_tex(self,context):
    world = context.scene.world
    if world and world.get('is_world_hdri',False):
        if not world.use_nodes:
            world.use_nodes = True
        nodes = world.node_tree.nodes
        for node in nodes:
            if type(node) is bpy.types.ShaderNodeTexEnvironment:
                prefs = context.preferences.addons[base_package].preferences
                if prefs.hdri_lib_path:
                    hdri_tex = context.scene.lightmixer.hdri_tex
                    world['hdri_tex'] = hdri_tex
                    world['hdri_category'] = context.scene.lightmixer.hdri_category
                    if hdri_tex not in {'empty','hdri_click', ''}:
                        try:
                            node.image = bpy.data.images.load(hdri_tex, check_existing=True)
                        except RuntimeError:
                            show_message("Could not find the HDRI texture at the specified path. Please refresh the library if that file has been moved or deleted.",
                                        'ERROR')
                            return
                            
                        name = os.path.splitext(node.image.name)[0]
                        world['hdri_tex_name'] = node.image.name

                        # If automatic World renaming is enabled in the preferences
                        prefs = context.preferences.addons[base_package].preferences
                        if prefs.hdri_auto_world_rename:
                            # Don't increment against itself, ignoring numbers at the end
                            if world.name.rsplit('.',1)[0] != name.rsplit('.',1)[0]:
                                counter = 0
                                # Increment name if world already exists
                                while name in bpy.data.worlds:
                                    counter += 1
                                    numbers = "." + str(counter).zfill(3)
                                    name = os.path.splitext(node.image.name)[0] + numbers
                                world.name = name
                                if world.lightmixer.get('hdri_ground',None):
                                    gp = get_hdri_ground_object(wd_lightmixer=world.lightmixer)
                                    if gp:
                                        gp.name = "HDRI_Ground_" + name
                                        gp.data.name = "HDRI_Ground_" + name
                                        gp.data.materials[0].name = "HDRI_Ground_" + name + "_Mat"
                                        world.lightmixer['hdri_ground'] = gp.name

                                # Update Cam World value
                                update_cam_world(self,context,world)
                        
                        # Update ground material
                        ground_tex,_,_,_ = get_hdri_ground_groups(wd_lightmixer=world.lightmixer)
                        if ground_tex:
                            ground_tex.image = bpy.data.images.load(hdri_tex, check_existing=True)

def update_hdri_category(self,context):
    prefs = context.preferences.addons[base_package].preferences
    world = context.scene.world
    if world and world.get('is_world_hdri',False):
        if prefs.hdri_auto_load:
            context.scene.lightmixer['hdri_tex'] = 0
        else:
            context.scene.lightmixer['hdri_tex'] = -1
        update_hdri_tex(self,context)

def update_hdri_ground(context):
    if context.scene.world:
        wd_lightmixer = context.scene.world.lightmixer
        hdri_grounds = [o for o in bpy.context.view_layer.objects if o.get('is_hdri_ground',False)]
        hdri_ground = None

        if hdri_grounds:
            for o in hdri_grounds:
                if o.name == wd_lightmixer.get('hdri_ground',False):
                    o.hide_set(False)
                    o.hide_viewport = False
                    o.hide_render = False
                    hdri_ground = o
            for o in hdri_grounds:
                if o.name != wd_lightmixer.get('hdri_ground',False):
                    o.select_set(False)
                    o.hide_set(True)
                    o.hide_viewport = True
                    o.hide_render = True
        return hdri_ground

class LIGHTMIXER_OT_World_HDRI_Add(bpy.types.Operator):
    bl_idname = "lightmixer.hdri_add"
    bl_label = "Add World HDRI"
    bl_description = "Creates HDRI Environment material"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self,context):

        world = context.scene.world
        world.name = create_unique_name("World HDRI", bpy.data.worlds)
        world['is_world_hdri'] = True
        world.use_nodes = True
        nodes = world.node_tree.nodes
        links = world.node_tree.links

        # # Mapping
        # mapping = nodes.new('ShaderNodeMapping')
        # mapping.location = (-200,0)

        # coord = nodes.new('ShaderNodeTexCoord')
        # coord.location = (-400,0)

        # Texture
        img = nodes.new('ShaderNodeTexEnvironment')
        img.location = (0,0)
        img.name = 'World HDRI Tex'

        # Shader
        bg = get_shader_node(world,'ShaderNodeBackground')
        if not bg:
            bg = nodes.new('ShaderNodeBackground')
        else:
            bg = bg[0]
        bg.location = (300,0)
        # Output
        op = get_shader_node(world,'ShaderNodeOutputWorld')
        if not op:
            output = nodes.new('ShaderNodeOutputWorld')
        else:
            output = op[0]
        output.location = (500,0)

        # Connect them
        # links.new(coord.outputs[0], mapping.inputs['Vector'])
        # links.new(mapping.outputs[0], img.inputs[0])
        links.new(img.outputs[0], bg.inputs[0])
        links.new(bg.outputs[0], output.inputs[0])

        context.scene.world = world
        update_hdri_tex(self,context)

        # Add Color controls
        bpy.ops.lightmixer.world_add_controls()

        if context.scene.render.engine == 'LUXCORE':
            world.luxcore.use_cycles_settings = True

        # Update Cam World value
        update_cam_world(self,context,world)

        # Update category to set correct thumbnail based on Prefs Auto Load
        update_hdri_category(self,context)

        return {'FINISHED'}

class LIGHTMIXER_OT_Sky_Texture_Add(bpy.types.Operator):
    bl_idname = "lightmixer.sky_add"
    bl_label = "Add Sky Texture"
    bl_description = "Creates Sky Environment material"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self,context):

        world = context.scene.world
        world.name = create_unique_name("Physical Sky", bpy.data.worlds)
        world['is_sky'] = True
        world.use_nodes = True
        nodes = world.node_tree.nodes
        links = world.node_tree.links

        # Texture
        img = nodes.new('ShaderNodeTexSky')
        img.location = (0,0)
        img.name = 'Sky Texture'

        # Shader
        bg = get_shader_node(world,'ShaderNodeBackground')
        if not bg:
            bg = nodes.new('ShaderNodeBackground')
        else:
            bg = bg[0]
        bg.location = (300,0)

        # Output
        op = get_shader_node(world,'ShaderNodeOutputWorld')
        if not op:
            output = nodes.new('ShaderNodeOutputWorld')
        else:
            output = op[0]
        output.location = (500,0)

        # Connect them
        links.new(img.outputs[0], bg.inputs[0])
        links.new(bg.outputs[0], output.inputs[0])

        context.scene.world = world
        update_hdri_tex(self,context)

        # Add Color controls
        bpy.ops.lightmixer.world_add_controls()

        if context.scene.render.engine == 'LUXCORE':
            world.luxcore.use_cycles_settings = True

        # Update Cam World value
        update_cam_world(self,context,world)

        return {'FINISHED'}

# Light Mixer Properties functions
def update_world_enabled(self,context):
    world = context.scene.world

    if context.scene.render.engine == 'LUXCORE' and not world.luxcore.use_cycles_settings:
        if world.enabled:
            if world.luxcore.light != 'none':
                if world.luxcore.light == "sky2":
                    world.luxcore.sun_sky_gain = world.strength
                else:
                    world.luxcore.gain = world.strength
        else:
            if world.luxcore.light != 'none':
                if world.luxcore.light == "sky2":
                    world.strength = world.luxcore.sun_sky_gain
                    world.luxcore.sun_sky_gain = 0
                else:
                    world.strength = world.luxcore.gain
                    world.luxcore.gain = 0
    else:
        backgrounds = get_shader_node(world,'ShaderNodeBackground')
        for background in backgrounds:
            if not background.mute and world.enabled:
                background.inputs['Strength'].default_value = background["strength"]
            else:
                background["strength"] = background.inputs['Strength'].default_value
                background.inputs['Strength'].default_value = 0

        # HDRI Ground Meshes
        wd_lightmixer = world.lightmixer
        hdri_ground_name = wd_lightmixer.get('hdri_ground',None)
        if hdri_ground_name:
            if not background.mute and world.enabled:
                wd_lightmixer.hdri_ground_emissive = wd_lightmixer["hdri_ground_strength"]
            else:
                wd_lightmixer["hdri_ground_strength"] = wd_lightmixer.hdri_ground_emissive
                wd_lightmixer.hdri_ground_emissive = 0

def update_world_solo(self,context):
    world = context.scene.world
    wd_lightmixer = world.lightmixer
    hdri_ground_name = wd_lightmixer.get('hdri_ground',None)
    hdri_ground_mesh = None
    if hdri_ground_name:
        hdri_ground_mesh = bpy.data.objects[hdri_ground_name]

    backgrounds = []
    if world:
        backgrounds = get_shader_node(world,'ShaderNodeBackground')

    for background in backgrounds:
        # Store Strength value
        if world.enabled:
            background["strength"] = background.inputs['Strength'].default_value
            if hdri_ground_mesh:
                wd_lightmixer["hdri_ground_strength"] = wd_lightmixer.hdri_ground_emissive

        # World Solo Update for Lights and World
        light_objs = [o for o in bpy.data.objects if o.type == 'LIGHT']
        for light_obj in light_objs:
            if world.solo:
                context.scene.lightmixer.solo_active = True
                light_obj.hide_viewport = True
                light_obj.hide_render = True
                background.inputs['Strength'].default_value = background["strength"]
                if hdri_ground_mesh:
                    wd_lightmixer.hdri_ground_emissive = wd_lightmixer["hdri_ground_strength"]
            else:
                context.scene.lightmixer.solo_active = False
                light_obj.hide_viewport = not light_obj.lightmixer.enabled
                light_obj.hide_render = not light_obj.lightmixer.enabled
                if world.enabled:
                    background.inputs['Strength'].default_value = background["strength"]
                    if hdri_ground_mesh:
                        wd_lightmixer.hdri_ground_emissive = wd_lightmixer["hdri_ground_strength"]
                else:
                    background.inputs['Strength'].default_value = 0
                    if hdri_ground_mesh:
                        wd_lightmixer.hdri_ground_emissive = 0

    # World Solo Update for Materials
    emissive_mats = [mat for mat in bpy.data.materials if mat.get('is_emissive', False)]
    for mat in emissive_mats:
        nodes = mat.node_tree.nodes
        for node in mat.get('em_nodes', ''):
            em_node,ctrl_node, ctrl_input = get_em_strength(mat,node)
            if em_node and ctrl_node and ctrl_input:
                if world.solo:
                    em_node.lightmixer.strength = nodes[ctrl_node].inputs[ctrl_input].default_value
                    nodes[ctrl_node].inputs[ctrl_input].default_value = 0
                else:
                    nodes[ctrl_node].inputs[ctrl_input].default_value = em_node.lightmixer.strength

    if world.solo:
        context.scene.lightmixer.solo_active = True
    else:
        context.scene.lightmixer.solo_active = False

class LIGHTMIXER_OT_WorldEnable(bpy.types.Operator):
    bl_idname = "lightmixer.world_enable"
    bl_label = "Enable World"
    bl_description = "Shift-Click to Solo this light"
    bl_options = {'UNDO'}

    bpy.types.World.enabled = bpy.props.BoolProperty(default=True,update=update_world_enabled)
    bpy.types.World.strength = bpy.props.FloatProperty(precision=3)
    bpy.types.World.solo = bpy.props.BoolProperty(update=update_world_solo)
    shift: bpy.props.BoolProperty()

    @classmethod
    def poll(cls,context):
        return context.scene.world.use_nodes

    def execute(self, context):
        world = context.scene.world

        if self.shift:

            if context.scene.lightmixer.solo_active and not world.solo:
                all_objs = context.scene.collection.all_objects
                solo_light=[obj for obj in all_objs if obj.type=='LIGHT' and obj.lightmixer.solo]
                solo_mat = [mat for mat in bpy.data.materials if mat.get('is_emissive', False) and mat.lightmixer.solo]
                if solo_light:
                    solo_light[0].lightmixer.solo = False
                    world.solo = True
                elif solo_mat:
                    solo_mat[0].lightmixer.solo = False
                    world.solo = True
            else:
                world.solo = not world.solo
        else:
            if not world.solo:
                world.enabled = not world.enabled

        if context.scene.render.engine == 'LUXCORE':
            # Refresh viewport Trick
            bpy.ops.object.add(type='EMPTY')
            bpy.ops.object.delete()
        return{'FINISHED'}

    def invoke(self, context, event):
        self.shift = event.shift
        return self.execute(context)

class LIGHTMIXER_OT_World_AddControls(bpy.types.Operator):
    bl_idname = "lightmixer.world_add_controls"
    bl_label = "Add Color Controls"
    bl_description = "Adds White Balance and Blur nodes to the World material"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls,context):
        return context.scene.world.use_nodes

    def execute(self, context):

        mapping_grp = append_node_group(mapping_grp_name,retrocompatible=True)
        color_control_grp = append_node_group(color_controls_name,retrocompatible=True)
        background_color_grp = append_node_group(background_color_name,retrocompatible=True)

        # Get node groups
        mapping = get_mapping_groups(context)
        if mapping:
            mapping = mapping[0]
        cc = get_color_controls_groups(context)
        if cc:
            cc = cc[0]
        
        bgc = get_background_color_groups(context)
        if bgc:
            bgc = bgc[0]

        world = context.scene.world
        nodes = world.node_tree.nodes
        links = world.node_tree.links

        # Get Environment texture and Background nodes
        if world.get('is_world_hdri', False):
            tex = [n for n in nodes if n.bl_idname=='ShaderNodeTexEnvironment' and n.name=='World HDRI Tex']
            if tex:
                img = tex[0]
                map = img.inputs['Vector']
        # If no HDRI, check for Sky
        elif world.get('is_sky', False):
            tex = [n for n in nodes if n.bl_idname=='ShaderNodeTexSky' and n.name=='Sky Texture']
            if tex:
                img = tex[0]

        if not tex:
            return {'CANCELLED'}

        bg = [n for n in nodes if n.bl_idname=='ShaderNodeBackground']
        if not bg:
            return {'CANCELLED'}
        else:
            bg = bg[0]
            color = bg.inputs['Color']

        if world.get('is_world_hdri', False) and not mapping:
            # Move nodes before the Env Texture node
            for node in nodes:
                if node.location[0] < img.location[0]:
                    node.location[0] -= 200
            mapping = nodes.new('ShaderNodeGroup')
            mapping.node_tree = mapping_grp
            mapping.location = (img.location[0]-200, img.location[1])

        if not cc:
            # Move nodes before the Background node
            for node in nodes:
                if node.location[0] < bg.location[0]:
                    node.location[0] -= 200
            cc = nodes.new('ShaderNodeGroup')
            cc.node_tree = color_control_grp
            cc.location = (bg.location[0]-200,bg.location[1])

        if not bgc:
            # Move nodes before the Background node
            for node in nodes:
                if node.location[0] < bg.location[0]:
                    node.location[0] -= 200
            bgc = nodes.new('ShaderNodeGroup')
            bgc.node_tree = background_color_grp
            bgc.location = (bg.location[0]-200,bg.location[1])

        # Insert Node groups
        if world.get('is_world_hdri', False):
            links.new(mapping.outputs[0], map)

        link_bg = [l for l in links if l.to_node == bg and l.to_socket == color]
        inc_color = link_bg[0].from_node
        inc_color_socket = link_bg[0].from_socket.name

        if inc_color != cc:
            links.new(inc_color.outputs[inc_color_socket], cc.inputs[0])
        links.new(bgc.outputs[0], color)

        links.new(cc.outputs[0], bgc.inputs[0])

        return {'FINISHED'}

class LIGHTMIXER_OT_Refresh_HDR_Categories(bpy.types.Operator):
    bl_idname = "lightmixer.refresh_hdr_categories"
    bl_label = "Refresh HDRI library"
    bl_description = "Updates HDRIs, library subfolders and thumbnails"
    # bl_options = {'UNDO'}

    def execute(self, context):
        hdri_lib_path_update(self,context)
        return {'FINISHED'}

class LIGHTMIXER_OT_Cycle_World(bpy.types.Operator):
    bl_idname = "lightmixer.cycle_world"
    bl_label = "Cycle between Worlds"
    bl_description = "Cyles through cameras in the scene"
    bl_options = {'UNDO'}

    previous: bpy.props.BoolProperty()

    def execute(self,context):
        worlds = [w.name for w in bpy.data.worlds]
        if worlds:
            current = worlds.index(context.scene.world.name)

            if self.previous:
                next = worlds[(current-1) % len(worlds)]
            else:
                next = worlds[(current+1) % len(worlds)]
                
            context.scene.world = bpy.data.worlds[next]

            return {'FINISHED'}
        
class LIGHTMIXER_OT_World_AddHDRIGround(bpy.types.Operator):
    bl_idname = "lightmixer.add_hdri_ground"
    bl_label = "Add HDRI Mesh"
    bl_description = ""
    bl_options = {'UNDO'}

    mesh_type: bpy.props.EnumProperty(
        items = [('PLANE','Plane', 'Adds an HDRI plane that receives shadows and lighting'),
                ('CUBE','Cube','Projects the HDRI on a Cube that receives shadows and lighting'),
                ('DOME','Dome','Projects the HDRI on a Dome that receives shadows and lighting'),
                ('CYLINDER','Cylinder','Projects the HDRI on a Cylinder that receives shadows and lighting'),
                ],
        default = 'PLANE')
    update: bpy.props.BoolProperty(default=False)

    @classmethod
    def poll(cls,context):
        return context.scene.world and context.scene.world.get('is_world_hdri',False)
    
    @classmethod 
    def description(cls, context, properties):
        enum_identifier = properties.mesh_type
        return properties.bl_rna.properties["mesh_type"].enum_items[enum_identifier].description

    def execute(self,context):
        world = context.scene.world
        wd_lightmixer = world.lightmixer

        # Switch to object mode to create plane
        if bpy.context.scene.collection.all_objects:
            if bpy.context.object and bpy.context.object.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')

        for obj in bpy.context.selected_objects:
            obj.select_set(False)

        hdri_ground = update_hdri_ground(context)

        if not hdri_ground:

            if self.mesh_type == 'DOME':
                obj_name = "HDRI_Dome" + "_" + world.name
                hdri_mesh,hdri_ground = append_mesh(hdri_dome_mesh_name, obj_name)
                mat_id = 'is_hdri_mesh_mat'
            elif self.mesh_type == 'CYLINDER':
                obj_name = "HDRI_Cylinder" + "_" + world.name
                hdri_mesh,hdri_ground = append_mesh(hdri_cylinder_mesh_name, obj_name)
                mat_id = 'is_hdri_mesh_mat'
            elif self.mesh_type == 'CUBE':
                obj_name = "HDRI_Cube" + "_" + world.name
                hdri_mesh,hdri_ground = append_mesh(hdri_cube_mesh_name, obj_name)
                mat_id = 'is_hdri_mesh_mat'
            else:
            # Create Plane and name it
                bpy.ops.mesh.primitive_plane_add()
                hdri_ground = context.view_layer.objects.active
                hdri_ground.name = "HDRI_Ground" + "_" + world.name
                hdri_ground.scale = (50,50,50)
                hdri_ground.scale /= context.scene.unit_settings.scale_length
                mat_id = 'is_hdri_ground_mat'

            # Get material
            mat_name = hdri_ground.name + "_Mat"
            mat = [m for m in bpy.data.materials if m.get(mat_id,False) and m.name == mat_name]
            if not mat:
                # create material
                mat = bpy.data.materials.new(name=mat_name)
                mat[mat_id] = True
            else:
                mat = mat[0]

        hdri_ground["is_hdri_ground"] = True
        wd_lightmixer['hdri_ground'] = hdri_ground.name
        hdri_ground.select_set(True)
        bpy.context.view_layer.objects.active = hdri_ground

        # Assign it to object
        if hdri_ground.data.materials:
            # Assign to 1st material slot
            hdri_ground.data.materials[0] = mat
        else:
            # Append if no slots
            hdri_ground.data.materials.append(mat)

        # Enable 'Use nodes':
        mat.use_nodes = True
        if bpy.app.version >= (4, 2, 0):
            mat.blend_method = 'HASHED'
        else:
            mat.blend_method = 'BLEND'
        mat.use_backface_culling = True

        if mat.node_tree:
            mat.node_tree.links.clear()
            mat.node_tree.nodes.clear()

        nodes = mat.node_tree.nodes
        links = mat.node_tree.links

        hdri_ground_grp = append_node_group(hdri_ground_grp_name,retrocompatible=True,startswith=True)
        hdri_ground_grp = hdri_ground_grp.copy()
        hdri_ground_grp.name = hdri_ground_grp_name + "_" + world.name

        hg_node = nodes.new('ShaderNodeGroup')
        hg_node['hdri_ground_node'] = True
        hg_node.node_tree = hdri_ground_grp
        hg_node.location = (0,0)
        _, ground_mapping,_,_ = get_hdri_ground_groups(wd_lightmixer=world.lightmixer)
        
        if self.mesh_type in {'DOME','CUBE', 'CYLINDER'}:
            hg_node['object_mapping'] = True
            if ground_mapping:
                ground_mapping.inputs['Object Mapping'].default_value=1
        else:
            hg_node['object_mapping'] = False
            if ground_mapping:
                ground_mapping.inputs['Object Mapping'].default_value=0

        # Add output node
        output = nodes.new('ShaderNodeOutputMaterial')
        output.location = (200,0)

        # Connect them
        links.new(hg_node.outputs[0], output.inputs[0])

        # Update material settings inside group
        wd_lightmixer['hdri_ground_type'] = self.mesh_type

        if self.mesh_type in {'CUBE', 'DOME', 'CYLINDER'}:
            backgrounds = get_shader_node(world,'ShaderNodeBackground')
            if backgrounds:
                wd_lightmixer.hdri_ground_emissive = backgrounds[0].inputs['Strength'].default_value
            ### Commenting for now because of some World caching that doesn't update. ###   
            # if world.get('cycles', None):
            #     world.cycles_visibility.diffuse = False
            #     world.cycles_visibility.glossy = False
            #     world.cycles_visibility.camera = False
            #     world.cycles_visibility.transmission = False
            #     world.cycles_visibility.scatter = False

        # Match Lightgroup with World
        if world.lightgroup:
            hdri_ground.lightgroup = world.lightgroup

        update_hdri_tex(self,context)

        set_hdri_blur(wd_lightmixer,wd_lightmixer.hdri_blur)
        set_hdri_horizon_level(wd_lightmixer,wd_lightmixer.hdri_horizon_level)
        set_hdri_rotation(wd_lightmixer,wd_lightmixer.hdri_rotation)
        set_hdri_exposure_comp(wd_lightmixer,wd_lightmixer.hdri_exposure_comp)
        set_hdri_temperature(wd_lightmixer,wd_lightmixer.hdri_temperature)
        set_hdri_tint(wd_lightmixer,wd_lightmixer.hdri_tint)
        set_hdri_clamp(wd_lightmixer,wd_lightmixer.hdri_clamp)
        set_hdri_projection_height(wd_lightmixer,wd_lightmixer.hdri_projection_height)

        return {'FINISHED'}
    
class LIGHTMIXER_OT_World_DeleteHDRIGround(bpy.types.Operator):
    bl_idname = "lightmixer.delete_hdri_ground"
    bl_label = "Delete HDRI Ground"
    bl_description = "Deletes HDRI Ground based on name given at Ground creation"
    bl_options = {'UNDO'}

    def execute(self,context):
        world = context.scene.world
        wd_lightmixer = world.lightmixer

        hdri_ground_name = wd_lightmixer.get('hdri_ground',None)
        if hdri_ground_name:
            if bpy.data.objects.get(hdri_ground_name):
                hdri_ground = bpy.data.objects[hdri_ground_name]

                # Match Lightgroup with World
                if hdri_ground.lightgroup and hdri_ground.lightgroup != world.lightgroup:
                    world.lightgroup = hdri_ground.lightgroup

                if isinstance(hdri_ground.data, bpy.types.Mesh):
                    # remove the mesh data first, while the object still exists
                    bpy.data.meshes.remove(hdri_ground.data)
                    try:
                        bpy.data.objects.remove(hdri_ground)
                    except ReferenceError:
                        # ignore a ReferenceError exception when the StructRNA is removed
                        pass

        ### Commenting for now because of some World caching that doesn't update. ###       
        # if wd_lightmixer['hdri_ground_type'] in {'CUBE', 'DOME', 'CYLINDER'}:
        #     # Restore Cycles Visibility
        #     world.cycles_visibility.camera = True
        #     world.cycles_visibility.diffuse = True
        #     world.cycles_visibility.glossy = True
        #     world.cycles_visibility.transmission = True
        #     world.cycles_visibility.scatter = True

        wd_lightmixer['hdri_ground'] = None
        wd_lightmixer['hdri_ground_type'] = None

        return {'FINISHED'}
    
class LIGHTMIXER_OT_Background_Color_Exposure_Compensate(bpy.types.Operator):
    bl_idname = "lightmixer.background_color_exp_compensate"
    bl_label = "Exposure Compensation"
    bl_description = "Multiplies Background Solid Color to compensate for Scene Exposure"
    bl_options = {'UNDO'}

    def execute(self,context):
        if context.scene.photographer.comp_exposure:
            pfx_node = get_comp_group_node(bpy.context,postfx_grp_name)
            if pfx_node:
                exposure_node = get_comp_node_in_group(pfx_node,'exposure')
                if exposure_node:
                    exp = exposure_node.inputs['Exposure'].default_value
        else:
            exp = context.scene.view_settings.exposure

        backgrounds = get_shader_node(context.scene.world,'ShaderNodeBackground')
        if backgrounds:
            bg_strength = backgrounds[0].inputs[1].default_value
        else:
            bg_strength = 1

        bgc = get_background_color_groups(context)
        for n in bgc:
            n.inputs['BG Exp Compensation'].default_value= math.pow(2,exp) * bg_strength
        _,_,_,ground_bgc = get_hdri_ground_groups(wd_lightmixer=context.scene.world.lightmixer)
        for n in ground_bgc:
            n.inputs['BG Exp Compensation'].default_value = math.pow(2,exp) * bg_strength
        return {'FINISHED'}
    
def world_ground_color_picker(self,context):
    x,y = self.mouse_region_x, self.mouse_region_y

    area = context.area
    if area.type=='VIEW_3D':

        red = 0
        green = 0
        blue = 0
        lum = 0

        if bpy.app.version >= (3,2,2):
            # get currently bound framebuffer
            buffer = gpu.state.active_framebuffer_get()
        else:
            bgl.glDisable(bgl.GL_DEPTH_TEST)
            buffer = bgl.Buffer(bgl.GL_FLOAT, 3)

        for i in range(x-4, x+5):
            for j in range(y-4, y+5):
                value = read_pixel_color(i,j,buffer)
                red += value[0]
                green += value[1]
                blue += value[2]
                lum += rgb_to_luminance(value)

        average_r = red / 81
        average_g = green / 81
        average_b = blue / 81
        average_lum = lum / 81

        average_color = (average_r,average_g,average_b)
        # print(average_color, average_lum)

        # Clear Buffer
        del buffer

        if average_color != (0.0,0.0,0.0) and average_lum != 0:
            color_mult = [x / average_lum for x in average_color]
            self.picked_color = (color_mult[0],color_mult[1],color_mult[2],average_lum)
    
    return self.picked_color

    
class LIGHTMIXER_OT_HDRI_Ground_Picker(bpy.types.Operator):
    bl_idname = "lightmixer.hdri_ground_picker"
    bl_label = "Fix HDRI Ground color tint and brightness"
    bl_description = "Pick the color of the plane under the current HDRI to fix its tint and brightness"
    bl_options = {'REGISTER', 'UNDO'}

    mouse_region_x: bpy.props.IntProperty(default=0)
    mouse_region_y: bpy.props.IntProperty(default=0)
    stored_bg_color : bpy.props.FloatVectorProperty(size=4)
    stored_hdri_ground_tint : bpy.props.FloatVectorProperty(size=4)
    stored_hdri_color : bpy.props.FloatVectorProperty(size=4)
    picked_color : bpy.props.FloatVectorProperty(size=4)

    def modal(self, context, event):
        world = context.scene.world
        settings = world.lightmixer
        context.area.tag_redraw()

        self.mouse_region_x = event.mouse_region_x
        self.mouse_region_y = event.mouse_region_y

        # Allow navigation for Blender and Maya shortcuts
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'} or event.alt and event.type == 'LEFTMOUSE' or event.alt and event.type == 'RIGHTMOUSE':
            return {'PASS_THROUGH'}

        if event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            if context.area.type=='VIEW_3D':
                bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')

            red,green,blue,lum = self.picked_color
            self.hg_node.inputs[0].default_value =(red,green,blue,1.0)

            if context.scene.photographer.comp_exposure:
                persp = context.area.spaces[0].region_3d.view_perspective
                view_comp = context.space_data.shading.use_compositor
                if view_comp == 'CAMERA' and persp == 'CAMERA' or view_comp == 'ALWAYS':
                    exp = 0
                else:
                    pfx_node = get_comp_group_node(bpy.context,postfx_grp_name)
                    if pfx_node:
                        exposure_node = get_comp_node_in_group(pfx_node,'exposure')
                        if exposure_node:
                            exp = exposure_node.inputs['Exposure'].default_value
                            # print (exposure_node, exp)
                
            else:
                exp = context.scene.view_settings.exposure
            
            bg_color = context.scene.world.lightmixer.bg_color[0]
            self.hg_node.inputs[1].default_value =(bg_color/(lum*math.pow(2,exp)))

            # Restore Materials value
            self.hg_node.inputs[2].default_value = self.stored_hdri_ground_reflection
            # self.hg_node.inputs[5].default_value = self.stored_hdri_ground_emissive
            settings.hdri_ground_emissive = self.stored_hdri_ground_emissive

            # Restore Mouse Cursor from EYEDROPPER Icon
            if self.cursor_set:
                context.window.cursor_modal_restore()

            # Restore state
            # Doesn't fix the Update Lights freeze
            # if context.engine == 'CYCLES':
            #     context.scene.world.cycles.sampling_method = self.stored_sampling
            settings.hdri_exposure_comp = self.stored_hdri_exposure_comp
            settings.hdri_temperature = self.stored_hdri_temperature
            settings.hdri_tint = self.stored_hdri_tint
            settings.hdri_color = self.stored_hdri_color

            settings.bg_color = self.stored_bg_color
            settings.bg_color_opacity = self.stored_bg_color_opacity

            # Restore Focus Planes visibility
            for o in self.fp:
                o.hide_viewport = False

            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            if context.area.type=='VIEW_3D':
                bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')

            # Restore state
            # Doesn't fix the Update Lights freeze
            # if context.engine == 'CYCLES':
            #     context.scene.world.cycles.sampling_method = self.stored_sampling
            settings.hdri_exposure_comp = self.stored_hdri_exposure_comp
            settings.hdri_temperature = self.stored_hdri_temperature
            settings.hdri_tint = self.stored_hdri_tint
            settings.hdri_color = self.stored_hdri_color
            settings.bg_color = self.stored_bg_color
            settings.bg_color_opacity = self.stored_bg_color_opacity
            self.hg_node.inputs[0].default_value = self.stored_hdri_ground_tint
            self.hg_node.inputs[1].default_value = self.stored_hdri_ground_intensity
            self.hg_node.inputs[2].default_value = self.stored_hdri_ground_reflection
            settings.hdri_ground_emissive = self.stored_hdri_ground_emissive

            # Restore Focus Planes visibility
            for o in self.fp:
                o.hide_viewport = False

            # Restore Mouse Cursor from EYEDROPPER Icon
            if self.cursor_set:
                context.window.cursor_modal_restore()

            return {'CANCELLED'}

        return {'RUNNING_MODAL'}


    def invoke(self, context, event):
        settings = context.scene.world.lightmixer

        # Doesn't fix the Update Lights freeze
        # if context.engine == 'CYCLES':
        #     self.stored_sampling = context.scene.world.cycles.sampling_method
        #     context.scene.world.cycles.sampling_method = 'NONE'

        self.hg_node = get_hdri_ground_node(settings)
        if self.hg_node and context.area.type=='VIEW_3D':
            # Store state
            self.stored_hdri_exposure_comp = settings.hdri_exposure_comp
            self.stored_hdri_temperature = settings.hdri_temperature
            self.stored_hdri_tint = settings.hdri_tint
            self.stored_hdri_color = settings.hdri_color
            self.stored_bg_color = settings.bg_color
            self.stored_bg_color_opacity = settings.bg_color_opacity
            self.stored_hdri_ground_tint = self.hg_node.inputs[0].default_value
            self.stored_hdri_ground_intensity = self.hg_node.inputs[1].default_value
            self.stored_hdri_ground_reflection = self.hg_node.inputs[2].default_value
            self.stored_hdri_ground_emissive = settings.hdri_ground_emissive

            settings.hdri_exposure_comp = 0
            settings.hdri_temperature = DEFAULT_COLOR_TEMPERATURE
            settings.hdri_tint = 0
            settings.hdri_color = (1.0,1.0,1.0,1.0)
            if settings.hdri_use_temperature:
                settings.bg_color = (0.2399,0.254,0.2415,1.0) # 0.25/6500K Blackbody which is not pure white (default World Color Controls)
            else:
                settings.bg_color = (0.25,0.25,0.25,1.0)
            settings.bg_color_opacity = 1.0
            self.hg_node.inputs[0].default_value = (1.0,1.0,1.0,1.0)
            self.hg_node.inputs[1].default_value = 1.0
            self.hg_node.inputs[2].default_value = 0.0
            settings.hdri_ground_emissive = 1.0
            bpy.ops.lightmixer.background_color_exp_compensate()

        
            self.fp = hide_focus_planes()

            args = (self, context)
            self._handle = bpy.types.SpaceView3D.draw_handler_add(world_ground_color_picker, args, 'WINDOW', 'PRE_VIEW')

            # Set Cursor to EYEDROPPER icon
            self.cursor_set = True
            context.window.cursor_modal_set('EYEDROPPER')

            context.window_manager.modal_handler_add(self)

            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "No 3D view or no HDRI Ground material found")
            return {'CANCELLED'}

def draw_hdri_rotation_value(self,context):
    font_id = 0
    text = None
    x_offset = context.region.width / 2 - 75
    # 75 = text horizontal dimension / 2
    y_offset = 35

    if context.area.type == 'VIEW_3D':
        shading = context.area.spaces.active.shading
        if shading.type == "MATERIAL" and not shading.use_scene_world:
            text = "Studio Light Rotation: " + str(round(math.degrees(shading.studiolight_rotate_z),1))
        elif context.scene.world and context.scene.world.get('is_world_hdri',False):
            world = context.scene.world
            text = "HDRI Rotation: " + str(round(math.degrees(world.lightmixer.hdri_rotation),1))

    # find text dimensions
    blf.position(font_id, x_offset, y_offset ,0)
    if bpy.app.version >= (4,0,0):
        blf.size(font_id, 28)
    else:
        blf.size(font_id, 28, 72)
    blf.color(font_id, 1.0,0.7,0.02,1.0)
    if text:
        blf.draw(font_id,text)

class LIGHTMIXER_OT_HDRI_Rotation_Drag(bpy.types.Operator):
    bl_idname = "lightmixer.hdri_rotation_drag"
    bl_label = "Photographer HDRI Rotation"
    bl_description = "Rotate HDRI using the assigned shortcut and dragging the mouse"
    bl_options = {'REGISTER', 'UNDO'}

    rotation_speed: bpy.props.FloatProperty(name='Speed',default=1.0)
    axis:bpy.props.EnumProperty(items=[('HORIZONTAL','Horizontal','Rotate HDRI Horizontally'),
                                        ('VERTICAL','Vertical','Rotate HDRI Vertically')],default='HORIZONTAL', name='Axis')
    dragging = True
    start_mouse_x = 0
    start_mouse_y = 0

    def modal(self, context, event):
        if event.type == 'MOUSEMOVE':
            if self.dragging:
                if self.axis == 'VERTICAL':
                    offset = (event.mouse_y - self.start_mouse_y)
                else:
                    offset = (event.mouse_x - self.start_mouse_x)
                
                offset /= (360/self.rotation_speed)

                shading = context.area.spaces.active.shading
                if shading.type == "MATERIAL" and not shading.use_scene_world:
                    shading.studiolight_rotate_z += offset
                else:
                    if context.scene and context.scene.world and context.scene.world.lightmixer:
                        if context.scene.world.get('is_world_hdri',False):
                            context.scene.world.lightmixer.hdri_rotation += offset
                    context.area.tag_redraw()
                # Reset start position
                self.start_mouse_x = event.mouse_x
                self.start_mouse_y = event.mouse_y

        elif event.type == 'RIGHTMOUSE':
            if event.value == 'RELEASE':
                self.dragging = False
                bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
                return {'FINISHED'}

        elif event.type in {'ESC'}:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        if context.area.type == 'VIEW_3D':
            self.start_mouse_x = event.mouse_x
            self.start_mouse_y = event.mouse_y
            context.window_manager.modal_handler_add(self)

            args = (self, context)
            self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_hdri_rotation_value, args, 'WINDOW', 'POST_PIXEL')
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}

# Add new World opertor
class LIGHTMIXER_OT_World_Add(bpy.types.Operator):
    bl_idname = "lightmixer.world_add"
    bl_label = "Add World"
    bl_description = "Adds a new World"
    bl_options = {'UNDO'}

    def execute(self, context):
        new_world = bpy.data.worlds.new(name="World")
        new_world.use_nodes = True
        if context.scene.camera.data.photographer.override_world:
            context.scene.camera.data.photographer.cam_world = new_world
        else:
            context.scene.world = new_world
        return {'FINISHED'}