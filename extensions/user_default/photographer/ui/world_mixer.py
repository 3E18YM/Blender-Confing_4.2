import bpy
from ..operators import world as wd
from ..functions.nodes import get_shader_node
from ..icons.icons import preview_collections
from ..operators.world import get_hdri_ground_node, get_hdri_ground_groups
from .. import __package__ as base_package

hdri_scale_y = 11

def world_mixer_draw_header_preset(self,context):
    layout = self.layout
    row = layout.row(align=True)

    if context.preferences.addons[base_package].preferences.show_compact_ui:
        if context.scene.world:
            world_name = context.scene.world.name
            label = (world_name[:12] + '...') if len(world_name) > 14 else world_name
            row.label(text=label)
    # sub = row.row(align=True)
    row.operator('lightmixer.cycle_world', text='', icon='TRIA_LEFT').previous=True
    row.operator('lightmixer.cycle_world', text='', icon='TRIA_RIGHT').previous=False

def world_mixer_draw(self,context, panel_version=False):
    layout = self.layout
    layout.use_property_split = False

    scene = context.scene
    world =scene.world
    lightmixer = scene.lightmixer

    world_box = layout.column()
    # Column to align buttons together
    world_col = world_box.column(align=True)

    if scene.camera and scene.camera.data.photographer.override_world:
        row = world_col.row(align=True)
        row.label(text='Camera World Override is enabled', icon="INFO")

    row = world_col.row(align=True)

    if world:
        if world.get('solo',False):
            icn = 'EVENT_S'
        elif world.get('enabled',True):
            icn = 'OUTLINER_OB_LIGHT'
        else:
            icn = 'LIGHT'
            
        row.operator("lightmixer.world_enable", text="", icon=icn, emboss=False)

    if world:
        name_row = row.row(align=True)
        if scene:
            if scene.camera and scene.camera.data.photographer.override_world:
                name_row.prop(scene.camera.data.photographer, 'cam_world', text='')
                name_row.operator('lightmixer.world_add', text='', icon='DUPLICATE')
            else:
                name_row.template_ID(scene, "world", new="lightmixer.world_add")
    else:
        name_row = row.row(align=True)
        name_row.template_ID(scene, "world", text='', new='world.new')

    intensity_row = world_col.row(align=True)

    if world and not world.get('enabled',True):
        if not world.get('solo',False):
            name_row.enabled = False
            intensity_row.enabled = False

    if world:
        wd_lightmixer = world.lightmixer
        if context.scene.render.engine == "LUXCORE" and not world.luxcore.use_cycles_settings:
            intensity_row.prop(lightmixer, 'world_show_more', text="",
                            icon='TRIA_DOWN' if lightmixer.world_show_more else 'TRIA_RIGHT',
                            emboss=False, icon_only=True)

            sub = intensity_row.row(align=True)
            if world.luxcore.light != 'none':
                # Turn red if Solo
                if world.get('solo',False):
                    name_row.alert = True
                    sub.alert = True

                if world.get('enabled',True):
                    if world.luxcore.light != 'none':
                        if world.luxcore.light == 'sky2':
                            sub.prop(world.luxcore,'sun_sky_gain')
                        else:
                            sub.prop(world.luxcore,'gain')
                else:
                    sub.enabled = False
                    sub.prop(world,'strength', text='Gain')
                sub.prop(world.luxcore,'exposure', text='')

                minus = sub.operator("lightmixer.emissive_stop", text='', icon='REMOVE')
                minus.factor = -0.5
                minus.world = True
                plus = sub.operator("lightmixer.emissive_stop", text='', icon='ADD')
                plus.factor = 0.5
                plus.world = True
            else:
                sub.label(text="Sky is set to None")
                sub.alignment='CENTER'

            if lightmixer.world_show_more:
                more_col = world_box.column(align=False)
                more_col.enabled = world.enabled
                row = more_col.row(align=True)
                row.prop(world.luxcore, "light", expand=True)
                if world.luxcore.light != 'none':
                    row = more_col.row(align=True)
                    if world.luxcore.color_mode == 'temperature':
                        row.prop(world.luxcore, "temperature", text='')
                    else:
                        row.prop(world.luxcore, "rgb_gain", text='')
                    icn = 'EVENT_K' if world.luxcore.color_mode == 'temperature' else 'EVENT_C'
                    row.prop(world.luxcore, "color_mode", icon=icn, icon_only=True)
                    if world.luxcore.light == 'sky2':
                        row = more_col.row(align=True)
                        row.prop(world.luxcore, "sun")
                    if world.luxcore.light == 'infinite':
                        row = more_col.row(align=True)
                        row.template_ID(world.luxcore, "image", open="image.open")

                    row = more_col.row(align=True)
                    row.prop(world.luxcore, "visibility_indirect_diffuse", toggle=True)
                    row.prop(world.luxcore, "visibility_indirect_glossy", toggle=True)
                    row.prop(world.luxcore, "visibility_indirect_specular", toggle=True)

        else:
            if not world.use_nodes:
                layout.row().prop(world, "use_nodes", icon='NODETREE')
            else:
                backgrounds = get_shader_node(world,'ShaderNodeBackground')

                if not backgrounds:
                    intensity_row.label(text='No Background nodes in World shader')
                else:
                    intensity_row.prop(lightmixer, 'world_show_more', text="",
                                    icon='TRIA_DOWN' if lightmixer.world_show_more else 'TRIA_RIGHT',
                                    emboss=False, icon_only=True)

                    sub = intensity_row.row(align=True)
                    # Turn red if Solo
                    if world:
                        if world.get('solo',False):
                            sub.alert = True

                    # If HDRI is cube, dome or cylinder
                    hdri_ground_name = wd_lightmixer.get('hdri_ground',None)
                    if hdri_ground_name:
                        sub.prop(wd_lightmixer, 'hdri_ground_emissive')
                    else:
                        sub.prop(backgrounds[0].inputs[1],'default_value', text=backgrounds[0].name+' Strength')
                    minus = sub.operator("lightmixer.emissive_stop", text='', icon='REMOVE')
                    minus.factor = -0.5
                    minus.world = True
                    minus.background_name = backgrounds[0].name
                    plus = sub.operator("lightmixer.emissive_stop", text='', icon='ADD')
                    plus.factor = 0.5
                    plus.world = True
                    plus.background_name = backgrounds[0].name

                    if len(backgrounds)>=2:
                        for bg in backgrounds[1:]:
                            bg_row = world_col.row(align=True)
                            bg_row.enabled = intensity_row.enabled
                            if world.get('solo',False):
                                bg_row.alert = True
                            bg_empty = bg_row.row()
                            bg_empty.ui_units_x = 1
                            bg_empty.separator()
                            # if bg_row.enabled:
                            bg_row.prop(bg.inputs[1],'default_value', text=bg.name+' Strength')
                            # else:
                            #     bg_row.label(text='Strength: '+ str(round(bg.get('strength'),3)))
                            minus = bg_row.operator("lightmixer.emissive_stop", text='', icon='REMOVE')
                            minus.factor = -0.5
                            minus.world = True
                            minus.background_name = bg.name
                            plus = bg_row.operator("lightmixer.emissive_stop", text='', icon='ADD')
                            plus.factor = 0.5
                            plus.world = True
                            plus.background_name = bg.name

                if lightmixer.world_show_more:
                    more_col = world_box.column(align=False)
                    more_col.enabled = world.enabled
                    col = more_col.column(align=True)
                    col.use_property_split = False

                    if world.get('is_world_hdri',False):
                        prefs = context.preferences.addons[base_package].preferences
                        if not prefs.hdri_lib_path:
                            col.label(text='Please set your HDRI library path:')
                            col.prop(prefs, 'hdri_lib_path', text = '')
                            col.separator()
                        else:
                            row = col.row(align=True)
                            row.prop(lightmixer, 'hdri_category', text='')
                            row.operator('lightmixer.generate_thumbnails',icon='RENDERLAYERS', text='').image_type='HDRI'
                            row.operator('lightmixer.refresh_hdr_categories', icon='FILE_REFRESH', text='')

                            hdri_tex = scene.world.get('hdri_tex','')

                            if hdri_tex and scene.lightmixer.hdri_tex != hdri_tex:
                                row = col.row(align=True)
                                row.scale_y = hdri_scale_y
                                row.operator('lightmixer.refresh_hdri_preview', icon='FILE_REFRESH')
                            else:
                                col.template_icon_view(lightmixer, "hdri_tex",
                                                    show_labels=True, scale=hdri_scale_y)
                            if world.get('hdri_tex_name','') and bpy.data.images[world['hdri_tex_name']]:
                                col.prop(bpy.data.images[world['hdri_tex_name']].colorspace_settings, 'name', text='')
                            col.separator()
                            col.prop(wd_lightmixer, 'hdri_rotation', slider=True, )

                    elif world.get('is_sky',False):
                        if world.use_nodes:
                            sky = get_shader_node(world,'ShaderNodeTexSky')
                            if sky:
                                col.prop(sky[0], 'sky_type')
                                col.separator()
                                if sky[0].sky_type == "NISHITA":
                                    col.prop(sky[0], 'sun_size')
                                    col.prop(sky[0], 'sun_intensity')
                                    col.separator()
                                    col.prop(sky[0], 'sun_elevation')
                                    col.prop(sky[0], 'sun_rotation')
                                    col.prop(sky[0], 'altitude')
                                    col.separator()
                                    col.prop(sky[0], 'air_density')
                                    col.prop(sky[0], 'dust_density')
                                    col.prop(sky[0], 'ozone_density')
                                elif sky[0].sky_type in {"PREETHAM","HOSEK_WILKIE"}:
                                    col.prop(sky[0], 'sun_direction', text='')
                                    col.prop(sky[0], 'turbidity')
                                    if sky[0].sky_type == "HOSEK_WILKIE":
                                        col.prop(sky[0], 'ground_albedo')
                    else:
                        col.separator()
                        col_large = col.column(align=True)
                        col_large.scale_y = 2
                        col_large.operator('lightmixer.hdri_add')
                        col_large.operator('lightmixer.sky_add')

                    # White Balance controls
                    if world.get('is_world_hdri', False) or world.get('is_sky', False):
                        mappings = wd.get_mapping_groups(context)
                        world_color_controls = wd.get_color_controls_groups(context)

                        # Blur and Horizon level if using HDRI
                        if world.get('is_world_hdri', False) and mappings:
                            col.prop(wd_lightmixer, 'hdri_horizon_level', slider=True)
                            col.prop(wd_lightmixer, 'hdri_blur', slider=True)                        
                            col.prop(wd_lightmixer, 'hdri_clamp')                        

                        if world_color_controls:
                            icn = 'EVENT_K' if wd_lightmixer.hdri_use_temperature else 'EVENT_C'
                            col.separator()
                            col.prop(wd_lightmixer, 'hdri_exposure_comp', slider=True)
                            row = col.row(align=True)
                            if wd_lightmixer.hdri_use_temperature:
                                row.prop(wd_lightmixer, 'hdri_temperature', slider=True)

                                col.prop(wd_lightmixer, 'hdri_tint', slider=True)
                            else:
                                row.prop(wd_lightmixer, 'hdri_color', text='')
                            row.prop(wd_lightmixer, "hdri_use_temperature", icon=icn, icon_only=True, toggle=True)

                            row = col.row(align=True)
                            row.prop(wd_lightmixer, "hdri_hue", text='H')
                            row.prop(wd_lightmixer, "hdri_saturation", text='S')
                            row.prop(wd_lightmixer, "hdri_value", text='V')

                        else:
                            col.separator()
                            col.operator('lightmixer.world_add_controls', icon='ERROR')

                    # if world.get('is_world_hdri', False):
                    if context.scene.render.engine == "CYCLES":
                        col.separator()
                        row = col.row(align=True)
                        row.prop(world.cycles_visibility, "diffuse", toggle=True)
                        row.prop(world.cycles_visibility, "glossy", toggle=True)
                        row.prop(world.cycles_visibility, "camera", toggle=True)

                    col.separator()

                    hdri_ground_name = wd_lightmixer.get('hdri_ground',None)
                    hdri_ground = None
                    if hdri_ground_name:
                        hdri_ground = bpy.data.objects.get(hdri_ground_name,None)

                    split = col.split(factor=0.3)
                    split.label(text='Lightgroup')
                    view_layer = context.view_layer
                    row = split.row(align=True)
                    if hdri_ground:
                        row.prop_search(hdri_ground, "lightgroup", view_layer, "lightgroups", text="", results_are_suggestions=True)
                    else:
                        row.prop_search(world, "lightgroup", view_layer, "lightgroups", text="", results_are_suggestions=True)
                    row.operator("lightmixer.add_lightgroup", text='', icon='ADD').world=True

                    more_col.enabled = intensity_row.enabled

                    col.separator()
                    col_film = col.column(align=True)
                    row = col_film.row(align=False)
                    split = row.split(factor=0.6)
                    split.label(text='Film Transparent Override')
                    sub = split.row(align=True)
                    sub.prop(wd_lightmixer, 'film_transparent_override', text='')
                    row = sub.row(align=True)
                    row.active = wd_lightmixer.film_transparent_override
                    row.prop(wd_lightmixer, 'film_transparent',
                             text='ON' if wd_lightmixer.film_transparent else 'OFF', toggle=True)

                    col.separator()
                    split = col.split(factor=0.3)
                    split.label(text='BG Color')
                    row = split.row(align=True)
                    split = row.split(align=True, factor=0.7)
                    split.prop(wd_lightmixer, "bg_color_opacity", text='')
                    split.prop(wd_lightmixer, "bg_color", text='')
                    custom_icons = preview_collections["icons"]
                    row.operator('lightmixer.background_color_exp_compensate', icon_value=custom_icons['EXP_COMP'].icon_id, text='')

                    if context.scene.render.engine == "BLENDER_EEVEE_NEXT" and panel_version:
                        sun_panel_header,sun_panel_body = layout.panel('Sun')
                        sun_panel_header.label(text='Sun')
                        if sun_panel_body:
                            col = sun_panel_body.column(align=True)
                            col.prop(world, "sun_threshold", text="Threshold")
                            col.prop(world, "sun_angle", text="Angle")
                            col.separator()
                            row = col.row(align=True)
                            row.prop(world, "use_sun_shadow", text="Shadows",toggle=True)
                            sub = row.row(align=True)
                            sub.prop(world, "sun_shadow_filter_radius", text="Filter")
                            sub.enabled = world.use_sun_shadow
                            jitter = col.row(align=True)
                            jitter.enabled = world.use_sun_shadow
                            jitter.prop(world, "use_sun_shadow_jitter",text="Jitter",toggle=True)
                            sub = jitter.row(align=True)
                            sub.active = world.use_sun_shadow_jitter
                            sub.prop(world, "sun_shadow_jitter_overblur", text="Overblur")
                            sub.enabled = world.use_sun_shadow
                            sub = col.column(align=True)
                            sub.prop(world, "sun_shadow_maximum_resolution", text="Resolution Limit")
                            sub.enabled = world.use_sun_shadow

                    if context.scene.world and bpy.app.version >= (4, 1, 0):
                        hdri_ground_panel_header,hdri_ground_panel_body = layout.panel('HDRI Ground')
                        hdri_ground_panel_header.label(text='HDRI Ground')
                        hdri_ground_draw_header_preset(hdri_ground_panel_header,context)
                        if hdri_ground_panel_body:
                            hdri_ground_draw(hdri_ground_panel_body,context,show_picker=panel_version)

class LIGHTMIXER_PT_WorldViewPanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Photographer'
    bl_label = "World Mixer"
    bl_order = 11


    @classmethod
    def poll(cls, context):
        wmpe = context.preferences.addons[base_package].preferences.worldmixer_panel_enable
        return wmpe

    def draw_header_preset(self, context):
        world_mixer_draw_header_preset(self,context)

    def draw(self, context):
        world_mixer_draw(self,context,panel_version=True)

class LIGHTMIXER_PT_WorldProperties(bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "world"
    bl_label = "World Mixer"

    def draw_header_preset(self, context):
        world_mixer_draw_header_preset(self,context)

    def draw(self, context):
        world_mixer_draw(self,context)


def hdri_ground_draw_header_preset(layout,context):
    row = layout.row(align=True)
    row.scale_x = 1.25
    hdri_ground_name = context.scene.world.lightmixer.get('hdri_ground',None)
    if hdri_ground_name:
        icn = 'RESTRICT_SELECT_ON'
        if context.selected_objects:
            if context.view_layer.objects.active and context.view_layer.objects.active.name == hdri_ground_name:
                icn = 'RESTRICT_SELECT_OFF'

        row.operator("photographer.select", text='', icon=icn).obj_name=context.scene.world.lightmixer['hdri_ground']
        row.operator('lightmixer.delete_hdri_ground', text='', icon='X')
    else:
        if context.preferences.addons[base_package].preferences.show_compact_ui:
            row.operator('lightmixer.add_hdri_ground', text='', icon='MESH_PLANE').mesh_type='PLANE'
            row.operator('lightmixer.add_hdri_ground', text='', icon='CUBE').mesh_type='CUBE'
            custom_icons = preview_collections["icons"]
            row.operator('lightmixer.add_hdri_ground', text='', icon_value=custom_icons['DOME'].icon_id).mesh_type='DOME'
            row.operator('lightmixer.add_hdri_ground', text='', icon='MESH_CYLINDER').mesh_type='CYLINDER'


def hdri_ground_draw(layout,context, show_picker=False):
    wd_lightmixer = context.scene.world.lightmixer
    hdri_ground_name = wd_lightmixer.get('hdri_ground',None)
    custom_icons = preview_collections["icons"]
    if not hdri_ground_name:
        row = layout.row(align=True)
        row.operator('lightmixer.add_hdri_ground', text='Plane', icon='MESH_PLANE').mesh_type='PLANE'
        row.operator('lightmixer.add_hdri_ground', text='Cube', icon='CUBE').mesh_type='CUBE'
        row.operator('lightmixer.add_hdri_ground', text='Dome', icon_value=custom_icons['DOME'].icon_id).mesh_type='DOME'
        row.operator('lightmixer.add_hdri_ground', text='Cylinder', icon='MESH_CYLINDER').mesh_type='CYLINDER'

    if context.scene.world:        
        col = layout.column(align=True)
        row = col.row(align=True)
        split = row.split(factor=0.3, align=True)
        if hdri_ground_name:
            hg_node = get_hdri_ground_node(wd_lightmixer)
            if hg_node:
                split.prop(hg_node.inputs[0],'default_value', text='')
                split.prop(hg_node.inputs[1],'default_value', text='Brightness')
                if show_picker:
                    row.operator('lightmixer.hdri_ground_picker', icon='EYEDROPPER', text='')
                col.prop(hg_node.inputs[2],'default_value', text='Reflection')
                col.prop(hg_node.inputs[3],'default_value', text='Roughness')

                if wd_lightmixer.get('hdri_ground_type',None) in {'CUBE','DOME','CYLINDER'}:
                    _,ground_mapping,_,_ = get_hdri_ground_groups(wd_lightmixer=wd_lightmixer)
                    if ground_mapping:
                        col.separator()
                        col.prop(ground_mapping.inputs[6],'default_value', text='Projection Height')
                        col.prop(ground_mapping.inputs[7],'default_value', text='Lighting Distance')

# Classes below only for versions of Blender older than 4.1.0 that don't have the layout.panel method
class LIGHTMIXER_PT_WorldViewPanel_HDRIGround(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Photographer'
    bl_label = "HDRI Ground"
    bl_parent_id = 'LIGHTMIXER_PT_WorldViewPanel'

    @classmethod
    def poll(cls, context):
        wmpe = context.preferences.addons[base_package].preferences.worldmixer_panel_enable and context.scene.world
        return wmpe

    def draw_header_preset(self, context):
        hdri_ground_draw_header_preset(self.layout,context)

    def draw(self, context):
        hdri_ground_draw(self.layout,context,True)

class LIGHTMIXER_PT_WorldProperties_HDRIGround(bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "world"
    bl_label = "HDRI Ground"
    bl_parent_id = 'LIGHTMIXER_PT_WorldProperties'

    @classmethod
    def poll(cls, context):
        return context.scene.world

    def draw_header_preset(self, context):
        hdri_ground_draw_header_preset(self.layout,context)

    def draw(self, context):
        hdri_ground_draw(self.layout,context)
