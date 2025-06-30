import bpy
from bpy.props import StringProperty, CollectionProperty, BoolProperty
from bpy.types import PropertyGroup, UIList, Operator, Panel
from .functions.nodes import append_node_group, post_effects_cleanup
from .properties.post_effects import postfx_grp_name

def update_cam_view_layer(cam,context):
    render_view_layers = []

    if cam.photographer.view_layer_enabled:
        # Populate Collection property of Cameras with View Layers
        for cvl in cam.view_layers:
            render_view_layers.append(cvl.name)
            if cvl.name not in context.scene.view_layers:
                cam.view_layers.remove(cam.view_layers.find(cvl.name))

        # If View Layer is present in the Collection property, set Use with .render property.
        for vl in context.scene.view_layers:
            if vl.name in render_view_layers:
                vl.use = cam.view_layers[vl.name].render
            else:
                # Else add to the Collection Property and retrieve .render from current Use value.
                cam.view_layers.add().name = vl.name
                cam.view_layers[vl.name].render = vl.use 

        # Remove potential doubles, doing it this way to fix previous scenes
        seen = set()
        for cvl in cam.view_layers:
            if cvl.name not in seen:
                seen.add(cvl.name)
            else:
                cam.view_layers.remove(cam.view_layers.find(cvl.name))

        # Apply Camera Active View Layer
        if context.scene.view_layers.get(cam.photographer.active_view_layer,None):
            if context.view_layer != context.scene.view_layers[cam.photographer.active_view_layer]:
                bpy.ops.photographer.set_view_layer(view_layer=cam.photographer.active_view_layer, use_scene_camera=True)

def draw_view_layer_item(self, context, layout, item, use_scene_camera):

    # Make sure your code supports all 3 layout types
    if self.layout_type in {'DEFAULT', 'COMPACT'}:
        row = layout.row(align=True)
        icn = 'HIDE_OFF' if context.window.view_layer == context.scene.view_layers[item.name] else 'HIDE_ON'
        set = row.operator("photographer.set_view_layer",text="", icon=icn)
        set.view_layer = item.name
        set.use_scene_camera = use_scene_camera
        row.prop(item,"name",text="")

        if use_scene_camera:
            cam = context.scene.camera.data
        else:
            cam = context.camera
    cam_view_layers = cam.view_layers

    icn = 'RESTRICT_RENDER_OFF'
    for vl in cam_view_layers:
        if item.name == vl.name and vl.render == False:
            icn = 'RESTRICT_RENDER_ON'                        
    render_op = row.operator("photographer.render_view_layer",text="", icon=icn)
    render_op.view_layer=item.name
    render_op.use_scene_camera = use_scene_camera

def draw_view_layer_panel(context,layout,use_scene_camera):
    if use_scene_camera:
        cam = context.scene.camera.data
        uilist = "PHOTOGRAPHER_UL_ViewPanel_ViewLayerList"
    else:
        cam = context.camera
        uilist = "PHOTOGRAPHER_UL_ViewLayerList"
    scene = context.scene

    box = layout.box()
    row = box.row()
    row.template_list(uilist, "View Layer List", scene,
                    "view_layers", scene.photographer, "active_view_layer_index")
    col = row.column(align=True)
    col.operator("photographer.view_layer_copy",text="", icon='DUPLICATE').use_scene_camera=use_scene_camera
    row = col.row()
    row.operator("photographer.view_layer_remove",text="", icon='X').use_scene_camera=use_scene_camera
    vl = [vl for vl in context.scene.view_layers]
    if len(vl)<2:
        row.enabled = False

    # Image format warning to make sure Incremental Save works  
    vlr = [vl for vl in cam.view_layers if vl.render]
    if len(vlr) >=2:
        if scene.render.image_settings.file_format != "OPEN_EXR_MULTILAYER":
            col = layout.column(align=True)
            col.label(text="Use File Output node or EXR Multilayer", icon='INFO')
            col.label(text="       to save each View layer.")

    layout.operator("photographer.add_viewlayer_comp_graph", icon='NODETREE')
    layout.prop(scene.render,"use_single_layer", text="Render Single Layer (Viewport Only)")

class ViewLayerItem(PropertyGroup):
    """Group of properties representing an item in the list."""

    # Properties added to View Layers in the UI List to set them Renderable
    name: StringProperty()
    render: BoolProperty(default=True)

class PHOTOGRAPHER_UL_ViewPanel_ViewLayerList(UIList):
    """View Layer List for View Panel"""

    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_property, index):

        # Using Scene Camera
        draw_view_layer_item(self, context, layout, item, True)

class PHOTOGRAPHER_UL_ViewLayerList(UIList):
    """View Layer List for Camera Properties panel"""

    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_property, index):
    
        # Using Camera data
        draw_view_layer_item(self, context, layout, item, False)


class PHOTOGRAPHER_OT_SetViewLayer(Operator):
    """Set active View Layer"""
    bl_idname = "photographer.set_view_layer"
    bl_label = "Set active View Layer"

    view_layer : StringProperty()
    use_scene_camera : BoolProperty(default=False)

    def execute(self, context):
        scene = context.scene
        if scene.view_layers.get(self.view_layer,None):
            if context.view_layer != scene.view_layers[self.view_layer]:
                # if hasattr(context,'window'):
                context.window.view_layer = scene.view_layers[self.view_layer]

            # Store Active View Layer in Camera data
            if self.use_scene_camera:
                cam = scene.camera.data
            else:
                cam = context.camera
            cam.photographer.active_view_layer = self.view_layer

        return{'FINISHED'}

class PHOTOGRAPHER_OT_RenderViewLayer(Operator):
    """Make View Layer renderable"""
    bl_idname = "photographer.render_view_layer"
    bl_label = "Render View Layer"

    view_layer : StringProperty()
    use_scene_camera: BoolProperty(default=False)

    def execute(self, context):
        if self.use_scene_camera:
            cam = context.scene.camera.data
        else:
            cam = context.camera

        update_cam_view_layer(cam,context)

        cvl = cam.view_layers[self.view_layer]
        cvl.render = not cvl.render
        context.scene.view_layers[self.view_layer].use = cvl.render

        return{'FINISHED'}

class PHOTOGRAPHER_OT_CopyViewLayer(Operator):
    """Copy current View Layer"""
    bl_idname = "photographer.view_layer_copy"
    bl_label = "Copy View Layer"

    use_scene_camera : BoolProperty(default=False)

    def execute(self, context):
        if self.use_scene_camera:
            cam = context.scene.camera.data
        else:
            cam = context.camera
        bpy.ops.scene.view_layer_add(type='COPY')
        cam.photographer.active_view_layer = context.view_layer.name

        return{'FINISHED'}

class PHOTOGRAPHER_OT_RemoveViewLayer(Operator):
    """Remove Active View Layer"""
    bl_idname = "photographer.view_layer_remove"
    bl_label = "Remove View Layer"

    use_scene_camera : BoolProperty(default=False)

    def execute(self, context):
        if self.use_scene_camera:
            cam = context.scene.camera.data
        else:
            cam = context.camera
        bpy.ops.scene.view_layer_remove()
        cam.photographer.active_view_layer = context.view_layer.name

        if not self.use_scene_camera:
            cam_obj = [o for o in bpy.data.objects if o.type == 'CAMERA' and o.data is cam.id_data][0]
            context.view_layer.objects.active = cam_obj

        return{'FINISHED'}

class PHOTOGRAPHER_OT_AddViewLayerCompGraph(bpy.types.Operator):
    bl_idname = "photographer.add_viewlayer_comp_graph"
    bl_label = "Add View Layer Output graph"
    bl_description = "Connects all View Layers together in Compositing in order to save them as separate files"
    bl_options = {'UNDO'}

    def execute(self, context):
        scene = context.scene

        if not scene.use_nodes:
            scene.use_nodes = True

        nodes = scene.node_tree.nodes
        links = scene.node_tree.links

        # Create File Output node
        file_output_node = nodes.new('CompositorNodeOutputFile')
        file_output_node.base_path = "//"
        file_output_node.location = (500,0)
        file_output_node.file_slots.remove(file_output_node.inputs[0])
        for vl in scene.view_layers:
            file_output_node.file_slots.new(vl.name)
        
        # For each view layers, create a Render Layer node with the View layer selected
        location = (0, 0)
        post_fx_nodes = {}
        for vl in scene.view_layers:
            render_layers_node = nodes.new('CompositorNodeRLayers')
            render_layers_node.layer = vl.name
            render_layers_node.location = location
            
            post_effects_cleanup(self,context,postfx_grp_name)
            pe_grp = append_node_group(postfx_grp_name)
            post_effects = nodes.new('CompositorNodeGroup')
            post_effects.node_tree = pe_grp
            post_effects.location = (location[0] + 300,location[1])
            post_fx_nodes.update({post_effects:vl.name})

            links.new(render_layers_node.outputs['Image'], post_effects.inputs['Image'])
    
            location = (location[0],location[1] - 250) 

        # Connect Post FX nodes to File Output node
        for post_fx_node, vl_name in post_fx_nodes.items():
            links.new(post_fx_node.outputs['Image'], file_output_node.inputs[vl_name])

        return {'FINISHED'}

class PHOTOGRAPHER_PT_ViewPanel_ViewLayer(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Photographer'
    bl_label = 'View Layers'
    bl_options = {'DEFAULT_CLOSED'}
    bl_order = 9

    @classmethod
    def poll(cls, context):
        vlpe = context.preferences.addons[__package__].preferences.viewlayer_panel_enable
        return context.scene.camera is not None and context.scene.camera.type == 'CAMERA' and vlpe

    def draw_header(self, context):
        settings = context.scene.camera.data.photographer    
        self.layout.prop(settings, "view_layer_enabled", text="")    

    def draw_header_preset(self, context):
        if context.preferences.addons[__package__].preferences.show_compact_ui:
            layout = self.layout
            settings = context.scene.camera.data.photographer 
            row = layout.row(align=True)
            row.enabled = settings.view_layer_enabled
            row.prop(settings,"active_view_layer",text="")
            row.separator()

    def draw(self, context):
        layout = self.layout        
        cam = context.scene.camera.data
        settings = cam.photographer
        layout.enabled = settings.view_layer_enabled

        draw_view_layer_panel(context,layout,use_scene_camera=True)


class PHOTOGRAPHER_PT_ViewLayer(Panel):
    bl_label = 'View Layers'
    bl_parent_id = 'PHOTOGRAPHER_PT_Panel'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.camera

    def draw_header(self, context):
        settings = context.camera.photographer
        self.layout.prop(settings, "view_layer_enabled", text="")

    def draw_header_preset(self, context):
        layout = self.layout
        settings = context.camera.photographer
        row = layout.row(align=True)
        row.enabled = settings.view_layer_enabled
        row.prop(settings,"active_view_layer",text="")
        row.separator()

    def draw(self, context):
        layout = self.layout
        cam = context.camera
        layout.enabled = cam.photographer.view_layer_enabled

        draw_view_layer_panel(context,layout,use_scene_camera=False)

class PHOTOGRAPHER_PT_NodeEditor_ViewLayer(Panel):
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'Photographer'
    bl_label = 'View Layers'
    bl_options = {'DEFAULT_CLOSED'}
    bl_order = 9

    @classmethod
    def poll(cls, context):
        vlpe = context.preferences.addons[__package__].preferences.viewlayer_panel_enable
        return context.scene.camera is not None and context.scene.camera.type == 'CAMERA' and vlpe

    def draw_header(self, context):
        settings = context.scene.camera.data.photographer    
        self.layout.prop(settings, "view_layer_enabled", text="")    

    def draw_header_preset(self, context):
        if context.preferences.addons[__package__].preferences.show_compact_ui:
            layout = self.layout
            settings = context.scene.camera.data.photographer 
            row = layout.row(align=True)
            row.enabled = settings.view_layer_enabled
            row.prop(settings,"active_view_layer",text="")
            row.separator()

    def draw(self, context):
        layout = self.layout        
        cam = context.scene.camera.data
        settings = cam.photographer
        layout.enabled = settings.view_layer_enabled

        draw_view_layer_panel(context,layout,use_scene_camera=True)

def register():

    bpy.utils.register_class(ViewLayerItem)
    bpy.utils.register_class(PHOTOGRAPHER_UL_ViewLayerList)
    bpy.utils.register_class(PHOTOGRAPHER_UL_ViewPanel_ViewLayerList)
    bpy.utils.register_class(PHOTOGRAPHER_OT_SetViewLayer)
    bpy.utils.register_class(PHOTOGRAPHER_OT_RenderViewLayer)
    # View Panel is registered in panel_classes
    # bpy.utils.register_class(PHOTOGRAPHER_PT_ViewPanel_ViewLayer)  
    bpy.utils.register_class(PHOTOGRAPHER_PT_ViewLayer)
    bpy.utils.register_class(PHOTOGRAPHER_OT_CopyViewLayer)
    bpy.utils.register_class(PHOTOGRAPHER_OT_RemoveViewLayer)
    bpy.utils.register_class(PHOTOGRAPHER_OT_AddViewLayerCompGraph)

    bpy.types.Camera.view_layers = CollectionProperty(type = ViewLayerItem)

def unregister():

    del bpy.types.Camera.view_layers

    bpy.utils.unregister_class(ViewLayerItem)
    bpy.utils.unregister_class(PHOTOGRAPHER_UL_ViewPanel_ViewLayerList)
    bpy.utils.unregister_class(PHOTOGRAPHER_UL_ViewLayerList)
    bpy.utils.unregister_class(PHOTOGRAPHER_OT_SetViewLayer)
    bpy.utils.unregister_class(PHOTOGRAPHER_OT_RenderViewLayer)
    bpy.utils.unregister_class(PHOTOGRAPHER_PT_ViewLayer)
    # View Panel is registered in panel_classes
    #bpy.utils.unregister_class(PHOTOGRAPHER_PT_ViewPanel_ViewLayer)
    bpy.utils.unregister_class(PHOTOGRAPHER_OT_CopyViewLayer)
    bpy.utils.unregister_class(PHOTOGRAPHER_OT_RemoveViewLayer)
    bpy.utils.unregister_class(PHOTOGRAPHER_OT_AddViewLayerCompGraph)
