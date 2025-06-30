import bpy
from ..functions.materials import list_objects_with_material
from ..operators.world import get_hdri_ground_node

def stop_adj(self, context, light):
    factor = self.factor
    if self.double:
        factor = self.factor * 2
    
    if context.scene.render.engine == 'LUXCORE' and not light.luxcore.use_cycles_settings:
        if light.type == 'SUN':
            light.luxcore.exposure += factor
        else:
            if light.luxcore.light_unit == 'artistic':
                light.luxcore.exposure += factor
            else:
                value = getattr(light.luxcore,'light_unit')
                value *= pow(2, factor)
                setattr(light.luxcore,'light_unit',value)
                
    else:
        settings = light.photographer
        if settings.light_type == 'SUN':
            unit = settings.sunlight_unit
        else:
            unit = settings.light_unit
    
        if unit == 'artistic':
            settings.light_exposure += factor
        else:
            value = getattr(settings,unit)
            value *= pow(2, factor)
            setattr(settings,unit,value)
        
# LightMixer buttons        
class PHOTOGRAPHER_OT_LightMixerStop_Adj(bpy.types.Operator):
    bl_idname = "lightmixer.light_stop"
    bl_label = "Light Exposure Adjust"
    bl_description = ("Adjust Light intensity by 0.5 stop increments. \n"
                    "Shift-Click for 1-stop increments. \n"
                    "1 stop difference doubles / halves the light intensity")
    bl_options = {'UNDO'}
    
    factor: bpy.props.FloatProperty()
    light: bpy.props.StringProperty()
    double: bpy.props.BoolProperty(default=False)
    collection: bpy.props.StringProperty()
    lightgroup: bpy.props.StringProperty()

    def execute(self, context):
        if self.collection:
            coll = bpy.data.collections[self.collection]
            lights = [l for l in coll.objects if l.type == 'LIGHT']
            for light in lights:
                stop_adj(self, context, light.data)
            # Reset Collection
            self.collection = ''
        elif self.lightgroup:
            lg_lights = [obj for obj in bpy.data.objects if obj.type=='LIGHT' and obj.lightgroup==self.lightgroup]
            for light in lg_lights:
                stop_adj(self, context, light.data)
            # Reset Lightgroup
            self.lightgroup = ''
        else:
            # Find light data from object name
            light = bpy.data.lights[self.light]
            stop_adj(self, context, light)
        return{'FINISHED'}
    
    def invoke(self, context, event):
        self.double = event.shift
        return self.execute(context)
        
# EmissiveMixer buttons
class PHOTOGRAPHER_OT_EmissiveStop_Adj(bpy.types.Operator):
    bl_idname = "lightmixer.emissive_stop"
    bl_label = "Exposure Adjust"
    bl_description = ("Adjust Strength by 0.5 stop increments. \n"
                    "Shift + Click for 1-stop increments. \n"
                    "1 stop difference doubles / halves the light intensity")
    bl_options = {'UNDO'}
    
    mat_name: bpy.props.StringProperty()
    node_name: bpy.props.StringProperty()
    factor: bpy.props.FloatProperty()
    double: bpy.props.BoolProperty(default=False)
    world: bpy.props.BoolProperty(default=False)
    background_name: bpy.props.StringProperty()
    lightgroup: bpy.props.StringProperty()

    def execute(self, context):
        factor = self.factor
        if self.double:
            factor = self.factor * 2
        
        if self.lightgroup:
            emissive_mats = [mat for mat in bpy.data.materials if mat.get('is_emissive', False)]
            lg_em_mats = []
            lg_em_objs = []
            for em in emissive_mats:
                em_objs = list_objects_with_material(em)
                lg_em_objs = [obj for obj in em_objs if obj.lightgroup==self.lightgroup]
                if lg_em_objs:
                    lg_em_mats.append(em)
            
            for mat in lg_em_mats:
                nodes = mat.node_tree.nodes
                for em_node in mat.get('em_nodes', ''):                
                    em_node = nodes.get(em_node,False)
                
                    em_strength = em_node.get('em_strength','')
                    if em_strength:
                        nodes[em_strength[0]].inputs[em_strength[1]].default_value *= pow(2, factor)
            
        elif self.world:
            world = context.scene.world
            wd_lightmixer = world.lightmixer
            if world:
                if context.scene.render.engine == 'LUXCORE' and not world.luxcore.use_cycles_settings:
                    world.luxcore.exposure += factor                
                else:
                    if world.use_nodes:
                        nodes = world.node_tree.nodes
                        background = [n for n in nodes if n.name == self.background_name]
                        background[0].inputs['Strength'].default_value *= pow(2, factor)

                        hdri_ground_name = wd_lightmixer.get('hdri_ground',None)
                        if hdri_ground_name:
                            hg_node = get_hdri_ground_node(wd_lightmixer)
                            if hg_node:
                                wd_lightmixer.hdri_ground_emissive *= pow(2, factor)

    
        else:
            if self.mat_name:
                mat = bpy.data.materials[self.mat_name]
                nodes = mat.node_tree.nodes
                node = nodes.get(self.node_name)
                em_strength = node.get('em_strength','')
                if em_strength:
                    nodes[em_strength[0]].inputs[em_strength[1]].default_value *= pow(2, factor)
        
        # Clear variable       
        self.mat_name = ''
        self.node_name = ''
        self.world = False
        self.lightgroup = ''
        return{'FINISHED'}
        
    def invoke(self, context, event):
        self.double = event.shift
        return self.execute(context)
        