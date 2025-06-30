import bpy
from ..functions.functions import list_lights
from ..functions.nodes import append_node_group
from ..functions.materials import list_objects_with_material

LGB_VERSION = 1
lightgroup_blending_grp_name = 'Light Group Blending v' + str(LGB_VERSION)

class LIGHTMIXER_OT_AddLightgroup(bpy.types.Operator):
    bl_idname = "lightmixer.add_lightgroup"
    bl_label = "Creates Lightgroup"
    bl_description = "Add Lightgroup and assign selected lights and meshes to it"
    bl_options = {'UNDO'}

    world: bpy.props.BoolProperty()

    def execute(self, context):
        if self.world:
            bpy.ops.scene.view_layer_add_lightgroup(name='World')
        else:
            bpy.ops.scene.view_layer_add_lightgroup()
        lg = context.view_layer.lightgroups[context.view_layer.active_lightgroup_index].name
        bpy.ops.lightmixer.add_to_lightgroup(lightgroup=lg,world=self.world)
        context.view_layer.active_lightgroup_index = -1

        return {'FINISHED'}

class LIGHTMIXER_OT_AddToLightgroup(bpy.types.Operator):
    bl_idname = "lightmixer.add_to_lightgroup"
    bl_label = "Add Selected lights to Light Group"
    bl_description = "Assigns Light Group to selected Lights"
    bl_options = {'UNDO'}

    lightgroup: bpy.props.StringProperty()
    world: bpy.props.BoolProperty()

    def execute(self, context):
        if self.world:
            context.scene.world.lightgroup = self.lightgroup
        else:
            light_objs = [o for o in bpy.context.selected_ids if o.type in {'LIGHT','MESH','CURVE'}]
            for obj in light_objs:
                obj.lightgroup = self.lightgroup

        return {'FINISHED'}
    
class LIGHTMIXER_OT_AddLightgroupsFromCollections(bpy.types.Operator):
    bl_idname = "lightmixer.add_lightgroups_from_collections"
    bl_label = "Add Lightgroups from Collections"
    bl_description = "Creates Lightgroups from Collections"
    bl_options = {'REGISTER', 'UNDO'}

    collection: bpy.props.StringProperty()

    def execute(self, context):
        if self.collection:
            light_collections = [context.scene.collections[self.collection]]
        else:
            light_list,light_collections,active_light = list_lights(context)
        for coll in light_collections:
            if coll.name not in {'Master Collection', 'Scene Collection'}:
                bpy.ops.scene.view_layer_add_lightgroup(name=coll.name)
                coll_lights = [obj for obj in coll.objects if obj.type=='LIGHT']
                for l in coll_lights:
                    l.lightgroup = coll.name
        return {'FINISHED'}

class LIGHTMIXER_OT_RemoveFromLightgroup(bpy.types.Operator):
    bl_idname = "lightmixer.remove_from_lightgroup"
    bl_label = "Remove Selected lights from Lightgroup"
    bl_description = "Selected lights will join the 'No Light Group' box"
    bl_options = {'UNDO'}

    def execute(self, context):
        light_objs = [o for o in bpy.context.selected_ids if o.type in {'LIGHT','MESH','CURVE'}]
        for obj in light_objs:
            obj.lightgroup = ''

        return {'FINISHED'}
    
class LIGHTMIXER_OT_DeleteLightgroup(bpy.types.Operator):
    bl_idname = "lightmixer.delete_lightgroup"
    bl_label = "Delete Lightgroup"
    bl_description = "Lights from the deleted Lightgroup will join the 'No Light Group' box"
    bl_options = {'UNDO'}

    lightgroup: bpy.props.StringProperty()

    def execute(self, context):
        # Make Lightgroup active in the List
        for i, lg in enumerate(context.view_layer.lightgroups):
            if lg.name == self.lightgroup:
                context.view_layer.active_lightgroup_index = i
                break

        # Clear Lightgroup from object    
        light_objs = [o for o in bpy.context.selected_ids if o.type=='LIGHT' and o.lightgroup==self.lightgroup]
        for l in light_objs:
            l.lightgroup = ''

        # Delete Lightgroup
        bpy.ops.scene.view_layer_remove_lightgroup()

        context.view_layer.active_lightgroup_index = -1

        return {'FINISHED'}
    
    def invoke(self, context, event):
        self.use_global = event.shift
        wm = context.window_manager
        return wm.invoke_confirm(self, event)
    
class LIGHTMIXER_OT_EnableLightgroup(bpy.types.Operator):
    bl_idname = "lightmixer.enable_lightgroup"
    bl_label = "Enable Lightgroup"
    bl_description = "Toggle lights inside Lightgroup"
    bl_options = {'UNDO'}

    lightgroup_name: bpy.props.StringProperty(name='Light Group Name')

    def execute(self, context):
        lg_lights_objs = [obj for obj in bpy.data.objects if obj.type=='LIGHT' and obj.lightgroup==self.lightgroup_name]
        lg_lights = [light.name for light in lg_lights_objs]

        if all(l.lightmixer.enabled for l in lg_lights_objs) or all(not l.lightmixer.enabled for l in lg_lights_objs):
            for l in lg_lights:
                bpy.ops.lightmixer.enable(light=l)

        else:
            for obj in lg_lights_objs:
                if not obj.lightmixer.enabled:
                    bpy.ops.lightmixer.enable(light=obj.name)

        return {'FINISHED'}

class LIGHTMIXER_OT_EnableEmissiveLightgroup(bpy.types.Operator):
    bl_idname = "lightmixer.enable_emissive_lightgroup"
    bl_label = "Enable Emissive Lightgroup"
    bl_description = "Toggle Emissive materials inside Lightgroup"
    bl_options = {'UNDO'}

    lightgroup_name: bpy.props.StringProperty(name='Light Group Name')

    def execute(self, context):

        emissive_mats = [mat for mat in bpy.data.materials if mat.get('is_emissive', False)]
        lg_em_mats = []
        lg_em_nodes = []

        for em in emissive_mats:
            em_objs = list_objects_with_material(em)
            lg_em_objs = [obj for obj in em_objs if obj.lightgroup==self.lightgroup_name]
            if lg_em_objs:
                lg_em_mats.append(em)
        
        for mat in lg_em_mats:
            nodes = mat.node_tree.nodes
            for em_node in mat.get('em_nodes', ''):
                em_node = nodes.get(em_node,False)
                lg_em_nodes.append(em_node)
            
        if all(node.lightmixer.enabled for node in lg_em_nodes) or all(not node.lightmixer.enabled for node in lg_em_nodes):
            for mat in lg_em_mats:
                for node in lg_em_nodes:
                    bpy.ops.lightmixer.emissive_enable(mat_name=mat.name,node_name=node.name)
        else:
            for mat in lg_em_mats:
                nodes = mat.node_tree.nodes
                for em_node in mat.get('em_nodes', ''):
                    em_node = nodes.get(em_node,False)
                    if not em_node.lightmixer.enabled:
                        bpy.ops.lightmixer.emissive_enable(mat_name=mat.name,node_name=em_node.name)

        return {'FINISHED'}
       
class LIGHTMIXER_OT_AddLightgroupCompGraph(bpy.types.Operator):
    bl_idname = "lightmixer.add_lightgroup_comp_graph"
    bl_label = "Add Light Groups blending graph"
    bl_description = "Connects all Lightgroups together in Compositing for post-render adjustments"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == 'CYCLES'

    def execute(self, context):
        scene = context.scene
        view_layer = context.view_layer

        if not view_layer.lightgroups:
            self.report({'WARNING'}, "No Light Group found, won't create Compositing graph.")
            return {'CANCELLED'}

        if not scene.use_nodes:
            scene.use_nodes = True

        nodes = scene.node_tree.nodes
        links = scene.node_tree.links

        lightgroup_blending_grp = append_node_group(lightgroup_blending_grp_name)

        # Enable denoising data
        view_layer = context.view_layer
        cycles_view_layer = view_layer.cycles 
        if not cycles_view_layer.denoising_store_passes:
            cycles_view_layer.denoising_store_passes = True

        # Look for Render Layers nodes and store links from Image socket
        render_layers_nodes = {}
        denoise_node = None
        for node in nodes:
            if node.type == 'R_LAYERS': # and node.layer == view_layer.name:
                render_layers_nodes[node] = []
                for link in links:
                    if link.from_socket == node.outputs['Image']:
                        render_layers_nodes[node].append(link.to_socket)
            if node.type == 'DENOISE':
                if node.get('denoise_lightgroup', False):
                    denoise_node = node
                    break

        # If no Render Layers node, create one
        if not render_layers_nodes:
            render_layers_node = nodes.new('CompositorNodeRLayers')
            render_layers_nodes[render_layers_node] = []

        # Look for 'Light Groups' frame and delete it
        for n in nodes:
            if n.name == 'PG_Lightgroups_Frame':
                nodes.remove(n)

        for rln in render_layers_nodes:
            vl = rln.layer
            loc = rln.location
            lg_loc = None   

            # Create Lightgroup group nodes for as many Lightgroups in the view layer
            lgs = [lg.name for lg in scene.view_layers[vl].lightgroups]

            for i, lg in enumerate(lgs):
                lg_blending=[]

                # Check if there is already a Lightgroup node connected to the Render Layer output
                for link in links:
                    if link.from_socket == rln.outputs['Combined_'+lg]:
                        if link.to_node.type == 'GROUP' and link.to_node.node_tree.name == lightgroup_blending_grp_name:
                            lg_blending = link.to_node
                            lg_loc = lg_blending.location

                # If not, create a Lightgroup node
                if not lg_blending:
                    lg_blending = nodes.new('CompositorNodeGroup')
                    lg_blending.node_tree = lightgroup_blending_grp
                    lg_blending.label = lg_blending.name = lg
                    lg_blending.node_tree.use_fake_user = True
                    lg_blending.width = 170

                    # Arrange position based on already existing Lightgroup
                    if lg_loc:
                        lg_blending.location = (lg_loc[0], loc[1] + int(i)*-200)
                    # Or take Render Layer node position
                    else:
                        if i == 0:
                            rln.location[0] += -250
                            lg_blending.location = (loc[0]+300, loc[1] + int(i)*-200)
                        else:
                            lg_blending.location = (loc[0]+300, loc[1] + int(i)*-200)

                # Store Lightgroup index to reconnect them later
                lg_blending['lg_index'] = i

                # Connect first Lightgroup output reusing Render Layer node output connection
                # if i == 0:
                original_links = render_layers_nodes[rln]
                for link in original_links:
                    links.new(lg_blending.outputs[0], link)

                # Connect Render Layer node to Lightgroup node
                links.new(rln.outputs['Combined_'+lg], lg_blending.inputs[1])

                # Connect Lightgroups together
                if i>=1:
                    for node in nodes:
                        if node.get('lg_index',-1) == i-1:
                            lg_blending.location = (node.location[0], loc[1] + int(i)*-200)
                            links.new(node.outputs[0], lg_blending.inputs[0])
                else:
                    if lg_loc:
                        lg_blending.location = (lg_loc[0], loc[1] + int(i)*-200)
                    else:
                        rln.location[0] += -250
                        lg_blending.location = (loc[0]+300, loc[1] + int(i)*-200)
                
                # Keep track of the last Lightgroup blending node
                last_lg_blending_node = lg_blending
        
        # Deselecting nodes
        selected_nodes = [n for n in nodes if n.select==True]
        for n in selected_nodes:
            n.select = False

        if not denoise_node:
            denoise_node = nodes.new(type='CompositorNodeDenoise')
            denoise_node['denoise_lightgroup'] = True

        # Create and connect the Denoise node
        if last_lg_blending_node:
            denoise_node.location = (last_lg_blending_node.location[0] + 300, last_lg_blending_node.location[1])
            links.new(last_lg_blending_node.outputs[0], denoise_node.inputs['Image'])
            links.new(rln.outputs['Denoising Normal'], denoise_node.inputs['Normal'])
            links.new(rln.outputs['Denoising Albedo'], denoise_node.inputs['Albedo'])
            # Reconnect the original links to the Denoise node output
            for link in original_links:
                links.new(denoise_node.outputs['Image'], link)

        # Listing Light Group nodes to frame them
        lg_nodes = [n for n in nodes if n.type == 'GROUP' and n.node_tree.name == lightgroup_blending_grp_name]
        lg_nodes.append(denoise_node)

        # Create a Frame node
        frame = nodes.new(type='NodeFrame')
        frame.label = 'Light Groups'
        frame.name = 'PG_Lightgroups_Frame'
        frame.use_custom_color = True
        frame.color = (0.42,0.5,0.415)

        # Frame them
        for node in lg_nodes:
            node.parent = frame

        return {'FINISHED'}