import bpy
from ..icons.icons import preview_collections
from ..functions.materials import list_objects_with_material
from .. import __package__ as base_package

def emissive_row(context,mat,layout):
    lightmixer = mat.lightmixer
    scene_lm = context.scene.lightmixer
    nodes = mat.node_tree.nodes
    solo_active = context.scene.lightmixer.solo_active
    view_prefs = context.preferences.view
    preferences = context.preferences.addons[base_package].preferences

    custom_icons = preview_collections["icons"]
    
    region_width_details = 310 * (preferences.screen_resolution/1920) * view_prefs.ui_scale

    for em_node in mat.get('em_nodes', ''):
        # box = layout.box()    
        
        em_node = nodes.get(em_node,False)
        if not em_node:
            row = layout.row(align=True)
            row.scale_y = 1.25
            row.operator('lightmixer.scan_emissive',
                                text='Emissive node Missing. Press to Scan',
                                icon='VIEWZOOM')
        
        else: 
            em_color = em_node.get('em_color','')     
            em_strength = em_node.get('em_strength', '')
            connected = em_node.get('connected', '')
            node_lm = em_node.lightmixer
    
            row = layout.row(align=True)
            row.scale_y = 1.25
            # main_col = row.column(align=True)
            
            if solo_active and node_lm.solo:
                icn = 'EVENT_S'
                row.alert=True
            elif not solo_active and node_lm.enabled:
                icn = 'OUTLINER_OB_LIGHT'    
            else:
                icn = 'LIGHT'
                
            en = row.operator("lightmixer.emissive_enable", text="",
                                icon=icn, emboss=False)
            en.node_name=em_node.name
            en.mat_name=mat.name
                                
            select_row = row.row(align=True)
            name_row = row.row()
            
            emissive_obj_list = []
            if mat.users:
                for obj in bpy.context.scene.objects:
                    for m in obj.material_slots:
                        if m.name == mat.name:
                            emissive_obj_list.append(obj)
            all_selected = all(obj.select_get() for obj in emissive_obj_list)
            if all_selected and not (mat.users==1 and mat.use_fake_user):
                icn = 'RESTRICT_SELECT_OFF'
            else:
                icn = 'RESTRICT_SELECT_ON'
            select_row.operator("photographer.select_emissive", text="",
                            # icon = 'RESTRICT_SELECT_OFF',).mat_name=mat.name
                            icon=icn).mat_name=mat.name
            select_row.operator("lightmixer.assign_emissive", text="", icon='PLUS').mat_name=mat.name


            if len(mat.get('em_nodes', ''))>1:
                name_row.prop(em_node, "name", text='')
            else:
                name_row.prop(mat, "name", text='')

            name_row.ui_units_x = scene_lm.emissive_name_width
            row_sep = row.row(align=True)
            row_sep.ui_units_x = .4
            row_sep.prop(scene_lm,"emissive_name_width")
            row_sep.separator()
            name_row = row.row(align=True)

            # Color Row
            split = row.split(align=True,factor=0.45)
            color_row = split.row(align=True)
            color_row.scale_x = 1
            # Make sure Nodes still exists since last scan
            if em_color and nodes.get(em_color[0], None):
                if node_lm.use_light_temperature:
                    color_row.prop(node_lm, "light_temperature", text='')

                    if context.region.width > region_width_details:
                        row=color_row.row(align=True)
                        row.ui_units_x = 0.6
                        row.prop(node_lm, "preview_color_temp", text='')

                else:
                    # color_row.ui_units_x = 3
                    # color_row.prop(node_lm, "color", text='')
                    color_row.prop(nodes[em_color[0]].inputs[em_color[1]], "default_value", text='')
                icn = 'EVENT_K' if node_lm.use_light_temperature else 'EVENT_C'
                color_row.prop(node_lm, 'use_light_temperature',
                                icon=icn, text='', toggle=True)

            # Second Row
            intensity_row = split.row(align=True) 
            
            # Disable UI if not Emissive enabled        
            if solo_active or not node_lm.enabled:
                if not node_lm.solo:
                    name_row.enabled = False
                    intensity_row.enabled = False  
                                            
            # Disable name_row if no Emissive controls
            if connected and (not em_color or not em_strength):
                color_row.enabled = False
                name_row.enabled = False
                # main_col.enabled = False
                intensity_row.operator('lightmixer.add_emissive_controls', icon='ERROR').mat_name=mat.name
            else:
                # Check if Node hasn't been deleted since last Scan
                if not nodes.get(em_strength[0], None):
                    color_row.enabled = False
                    intensity_row.operator('lightmixer.scan_emissive',
                                        text='Missing Node, please Scan again',
                                        icon='VIEWZOOM')
                else:
                    if intensity_row.enabled:
                        intensity_row.prop(nodes[em_strength[0]].inputs[em_strength[1]], "default_value", text='')
                    else:
                        intensity_row.prop(node_lm, "strength", text='')

                    if context.region.width > region_width_details:
                        exp_col = intensity_row.row(align=True)
                        minus = exp_col.operator("lightmixer.emissive_stop", text='', icon='REMOVE')
                        plus = exp_col.operator("lightmixer.emissive_stop", text='', icon='ADD')
                    else:
                        exp_col = intensity_row.column(align=True)
                        exp_col.scale_y = 0.52
                        plus = exp_col.operator("lightmixer.emissive_stop", text='', icon='TRIA_UP')
                        minus = exp_col.operator("lightmixer.emissive_stop", text='', icon='TRIA_DOWN')

                    # exp_col = intensity_row.column(align=True)
                    # exp_col.scale_y = 0.52
                    # plus = exp_col.operator("lightmixer.emissive_stop", text='', icon='TRIA_UP')
                    plus.factor = 0.5
                    plus.mat_name = mat.name
                    plus.node_name = em_node.name
                    # minus = exp_col.operator("lightmixer.emissive_stop", text='', icon='TRIA_DOWN')
                    minus.factor = -0.5
                    minus.mat_name = mat.name
                    minus.node_name = em_node.name

                    if mat.use_backface_culling:
                        icn = 'BACKFACE_CULLING_ON'
                    else:
                        icn = 'BACKFACE_CULLING_OFF'
                    intensity_row.prop(lightmixer,'backface_culling', toggle=True, icon_only=True, icon_value=custom_icons[icn].icon_id)
                
            # main_col.operator("lightmixer.show_more", text="",
            #                 icon='TRIA_DOWN' if lightmixer.show_more else 'TRIA_RIGHT',
            #                 emboss=False).mat=mat.name

            # if lightmixer.show_more:
            #     more_col = box.column(align=False)
            #     more_col.enabled = lightmixer.enabled
            #     col = more_col.column(align=True)
            #     col.prop(lightmixer,'backface_culling', toggle=True)
            #     if solo_active or not node_lm.enabled:
            #         more_col.enabled = False
                            
            # if context.scene.render.engine == "CYCLES":
            #     row = col.row(align=True)
                # row.prop(world.cycles_visibility, "diffuse", toggle=True)
                # row.prop(world.cycles_visibility, "glossy", toggle=True)
                # row.prop(world.cycles_visibility, "camera", toggle=True)

def emissive_lightgroup_row(context,lightgroup,layout):
    custom_icons = preview_collections["icons"]
    lg_box = layout.box()
    lg_row = lg_box.row(align=True)

    first_row = lg_row.row(align=True)

    emissive_mats = [mat for mat in bpy.data.materials if mat.get('is_emissive', False)]
    lg_em_mats = []
    lg_em_objs = []

    exp = first_row.operator("photographer.lightgroup_expand", text="",
                        icon='TRIA_DOWN' if lightgroup.id_data.get(lightgroup.name+'_em_expand',True) else 'TRIA_RIGHT',
                        emboss=False)
    exp.lightgroup=lightgroup.name
    exp.emissive_mixer=True

    if all(not l.lightmixer.enabled for l in emissive_mats):
        icn = 'LIGHTGROUP_OFF'
    else:
        icn = 'LIGHTGROUP'
    first_row.operator("lightmixer.enable_emissive_lightgroup", text='', icon_value=custom_icons[icn].icon_id,emboss=False).lightgroup_name=lightgroup.name

    if all(light_obj.select_get() for light_obj in lg_em_objs):
        icn = 'RESTRICT_SELECT_OFF'
    else:
        icn = 'RESTRICT_SELECT_ON' 

    first_row.operator("photographer.select_emissive_lightgroup", text='', icon=icn, emboss=False).lightgroup_name=lightgroup.name
    lg_row.operator("lightmixer.add_to_lightgroup", text='', icon='IMPORT').lightgroup=lightgroup.name
    lg_row.operator("lightmixer.remove_from_lightgroup", text='', icon='EXPORT')    
    lg_row.prop(lightgroup, "name", text='')
    exp_row = lg_row.row(align=True)
    minus = exp_row.operator("lightmixer.emissive_stop", text='', icon='REMOVE')
    minus.lightgroup = lightgroup.name
    minus.factor = -0.5
    plus = exp_row.operator("lightmixer.emissive_stop", text='', icon='ADD')
    plus.lightgroup = lightgroup.name
    plus.factor = 0.5
    col = lg_box.column(align=True)
    lg_objs = [obj for obj in context.view_layer.objects if obj.type in {'MESH','CURVE'} and obj.lightgroup==lightgroup.name]
    
    if lightgroup.id_data.get(lightgroup.name+'_em_expand',True):
        if len(lg_objs) > 2:
            objs_str = " + " + str(len(lg_objs)-2) + " objects..."
            col.label(text=lg_objs[0].name + ', ' + lg_objs[1].name +objs_str)
        elif len(lg_objs) == 2:
            col.label(text=lg_objs[0].name + ', ' + lg_objs[1].name)
        elif len(lg_objs) == 1:
            col.label(text=lg_objs[0].name)

    for em in emissive_mats:
        em_objs = list_objects_with_material(em)
        lg_em_objs = [obj for obj in em_objs if obj.lightgroup==lightgroup.name]
        if lg_em_objs:
            lg_em_mats.append(em)

    if lg_em_mats:
        first_row.enabled = True
        if lightgroup.id_data.get(lightgroup.name+'_em_expand',True):
            # col = lg_box.column(align=True)
            # if len(lg_em_objs) > 1:
            #     objs_str = " + " + str(len(lg_em_objs)-1) + " objects..."
            #     col.label(text=lg_em_objs[0].name+objs_str)
            # elif len(lg_em_objs) == 1:
            #     col.label(text=lg_em_objs[0].name)
            # lg_em_mats = sorted(lg_em_mats)
            for em in lg_em_mats:
                emissive_row(context,em,col)
    else:
        first_row.enabled = False
        exp_row.enabled = False
    
    lg_row.operator("lightmixer.delete_lightgroup", text='',icon='PANEL_CLOSE', emboss=False).lightgroup=lightgroup.name

class PHOTOGRAPHER_UL_ViewPanel_EmissiveMaterialsList(bpy.types.UIList):
    """Emissive Material List for Emissive Mixer panel"""

    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_property, index):
        col = layout.column(align=True)
        emissive_row(context,item,col)

    def draw_filter(self, context, layout):
        settings = context.scene.lightmixer
        layout.separator()
        col_main = layout.column(align=True)

        row = col_main.row(align=True)
        row.prop(settings, 'emissive_list_filter', text='', icon='VIEWZOOM')
        if settings.emissive_list_filter:
            clear = row.operator("photographer.button_string_clear", text='',
                    icon='PANEL_CLOSE',emboss=False)
            clear.prop='emissive_list_filter'
            clear.type = 'light'
        row.prop(settings, 'emissive_use_filter_invert', text='', icon='ARROW_LEFTRIGHT')
        row.separator()
        row.prop(settings, 'emissive_list_filter_reverse', text='', icon='SORT_DESC'
                if settings.emissive_list_filter_reverse else "SORT_ASC")
        row.separator()
        row.prop(settings,'emissive_list_sorting', icon_only=True, expand=True)

    def filter_items(self,context,data,propname):
        settings = context.scene.lightmixer
        filtered = []
        ordered = []
        items = getattr(data, propname)
        helper_funcs = bpy.types.UI_UL_list

        filtered = [self.bitflag_filter_item] * len(items)
        self.use_filter_sort_reverse = settings.emissive_list_filter_reverse

        ordered = helper_funcs.sort_items_by_name(items, "name")

        filtered_items = self.get_props_filtered_items()

        for i, item in enumerate(items):
            if not item in filtered_items:
                filtered[i] &= ~self.bitflag_filter_item

        return filtered,ordered

    def get_props_filtered_items(self):
        em_materials = []
        for mat in bpy.data.materials:
            if mat.get('is_emissive', False):
                if mat['em_nodes']:
                    em_materials.append(mat)

        settings = bpy.context.scene.lightmixer

        filtered_items = em_materials
        if settings.emissive_list_filter:
            if settings.emissive_use_filter_invert:
                filtered_items = [o for o in filtered_items if o.name.lower().find(settings.emissive_list_filter.lower()) == -1]
            else:
                filtered_items = [o for o in filtered_items if not o.name.lower().find(settings.emissive_list_filter.lower()) == -1]

        return filtered_items

class PHOTOGRAPHER_UL_ViewPanel_EmissiveLightGroupsList(bpy.types.UIList):
    """Light List for Lightmixer panel"""

    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_property, index):
        col = layout.column(align=True)
        emissive_lightgroup_row(context,item,col)


    def draw_filter(self, context, layout):
        settings = context.scene.lightmixer
        layout.separator()
        col_main = layout.column(align=True)

        row = col_main.row(align=True)
        row.prop(settings, 'emissive_list_filter', text='', icon='VIEWZOOM')
        if settings.emissive_list_filter:
            clear = row.operator("photographer.button_string_clear", text='',icon='PANEL_CLOSE',
                    emboss=False)
            clear.prop='emissive_list_filter'
            clear.type = 'light'
        row.prop(settings, 'emissive_use_filter_invert', text='', icon='ARROW_LEFTRIGHT')
        row.separator()
        row.prop(settings, 'emissive_list_filter_reverse', text='', icon='SORT_DESC'
                if settings.emissive_list_filter_reverse else "SORT_ASC")
        row.separator()
        row.prop(settings,'emissive_list_sorting', icon_only=True, expand=True)

    def filter_items(self,context,data,propname):
        settings = context.scene.lightmixer
        filtered = []
        ordered = []
        items = getattr(data, propname)
        helper_funcs = bpy.types.UI_UL_list

        filtered = [self.bitflag_filter_item] * len(items)
        self.use_filter_sort_reverse = settings.emissive_list_filter_reverse

        ordered = helper_funcs.sort_items_by_name(items, "name")

        filtered_items = self.get_props_filtered_items()

        for i, item in enumerate(items):
            if not item in filtered_items:
                filtered[i] &= ~self.bitflag_filter_item

        return filtered,ordered

    def get_props_filtered_items(self):
        view_layer = bpy.context.view_layer
        filtered_items = [lg for lg in view_layer.lightgroups]
        return filtered_items

class LIGHTMIXER_PT_EmissiveViewPanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Photographer'
    bl_label = "Emissive Mixer"
    bl_order = 13

    @classmethod
    def poll(cls, context):
        empe = context.preferences.addons[base_package].preferences.emissivemixer_panel_enable
        return empe

    def draw_header_preset(self, context):
        custom_icons = preview_collections["icons"]
        layout = self.layout
        if context.preferences.addons[base_package].preferences.show_compact_ui:
            row = layout.row(align=True)
            row.alignment = 'RIGHT'
            row.scale_x = 1.25
            # row.operator("lightmixer.add_emissive", text="Add Emissive", icon='LIGHT_AREA')                    
            row.operator("lightmixer.scan_emissive", icon='VIEWZOOM', text='')
            row.operator("lightmixer.create_emissive", icon_value=custom_icons['EMISSIVE_ADD'].icon_id, text='')

    def draw(self,context):
        custom_icons = preview_collections["icons"]
        layout = self.layout
        layout.use_property_split = False
        scene = context.scene
        settings = scene.lightmixer

        emissive_mats = [mat for mat in bpy.data.materials if mat.get('is_emissive', False)]
        no_lg_em_mats = []
        
        if not context.preferences.addons[base_package].preferences.show_compact_ui:
            row = layout.row(align=True)
            # row.operator("lightmixer.add_emissive", text="Add Emissive", icon='LIGHT_AREA')                    
            row.operator("lightmixer.scan_emissive", icon='VIEWZOOM')
            row.operator("lightmixer.create_emissive", icon_value=custom_icons['EMISSIVE_ADD'].icon_id, text='Create')

        # Light list UI
        box = layout.box()
        panel_row = box.row(align=False)
        panel_col = panel_row.column()
        
        if not emissive_mats:
            row = panel_col.row(align=True)
            row.alignment = 'CENTER'
            row.label(text="No Emissive material in the Scene", icon='INFO')

        if scene.lightmixer.emissive_list_sorting == 'LIGHTGROUP':
            view_layer = context.view_layer
            lightgroups = view_layer.lightgroups

            lg_box = panel_col.box()
            row = lg_box.row(align=True)
            first_row = row.row(align=True)
            first_row.prop(scene.lightmixer, "scene_collection_expand", text="",
                            icon='TRIA_DOWN' if scene.lightmixer.get('scene_collection_expand', True)
                            else 'TRIA_RIGHT', emboss=False)

            
            for em in emissive_mats:
                em_objs = list_objects_with_material(em)
                no_lg_em_objs = [obj for obj in em_objs if obj.lightgroup=='']
                if no_lg_em_objs:
                    no_lg_em_mats.append(em)

            if all(not l.lightmixer.enabled for l in no_lg_em_objs):
                icn = 'LIGHTGROUP_OFF'
            else:
                icn = 'LIGHTGROUP'
            first_row.operator("lightmixer.enable_emissive_lightgroup", text='', icon_value=custom_icons[icn].icon_id,emboss=False).lightgroup_name=''

            all_selected = all(em_obj.select_get() for em_obj in no_lg_em_objs)
            if all_selected:
                icn = 'RESTRICT_SELECT_OFF'
            else:
                icn = 'RESTRICT_SELECT_ON' 
            first_row.operator("photographer.select_emissive_lightgroup", text='', icon=icn, emboss=False).lightgroup_name=''

            first_row.label(text=' No Light Group')
            row.operator("lightmixer.add_lightgroup", text='', icon='ADD')
            row.operator("lightmixer.add_lightgroups_from_collections", text='', icon='COLLECTION_NEW')
            row.separator()
            row.operator("lightmixer.add_lightgroup_comp_graph", text='', icon='NODE_COMPOSITING')

            if not no_lg_em_mats: 
                first_row.enabled=False
            else:
                # no_lg_em_objs= sorted(no_lg_em_objs)
                col = lg_box.column()
                if scene.lightmixer.scene_collection_expand:
                    for em in no_lg_em_mats:
                        if settings.emissive_list_filter:
                            if settings.emissive_use_filter_invert:
                                if settings.emissive_list_filter.lower() not in em.name.lower():
                                    emissive_row(context,em,col) 
                            elif settings.emissive_list_filter.lower() in em.name.lower():
                                emissive_row(context,em,col)    
                        else:
                            emissive_row(context,em,col)

            filtered_items = [lg for lg in lightgroups]
            rows_count = len(filtered_items)
            row = panel_col.row()
            row.template_list("PHOTOGRAPHER_UL_ViewPanel_EmissiveLightGroupsList", "Light Groups", view_layer,
                    "lightgroups", view_layer, "active_lightgroup_index", maxrows=rows_count)
        
        else:
            rows_count = len(emissive_mats)
            row = panel_col.row()
            row.template_list("PHOTOGRAPHER_UL_ViewPanel_EmissiveMaterialsList", "Emissive List", bpy.data,
                "materials", scene.lightmixer, "active_emissive_index", maxrows=rows_count)    
