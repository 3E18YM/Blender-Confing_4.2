import bpy
from ..functions.functions import traverse_tree, list_lights
from ..properties.light import energy_check
from ..operators.target import get_target
from ..icons.icons import preview_collections
from .. import __package__ as base_package

def light_textures_ui(parent_col, context, settings,light_name):

    engine = context.scene.render.engine
    if engine == 'CYCLES':
        box = parent_col.box()
        top_row = box.row(align=True)
        top_row.prop(settings,'gobo')
        if settings.gobo:
            col = box.column(align=True)
            row = col.row(align=True)
            row.prop(settings,'gobo_scale')
            row.prop(settings,'gobo_scale_y')
            row = col.row(align=True)
            row.prop(settings,'gobo_offset_x')
            row.prop(settings,'gobo_offset_y')
            col.prop(settings,'gobo_opacity', slider=True)
            row=col.row(align=True)
            row.prop(settings,'gobo_tex_repeat', text='Repeat')
            if settings.light_type == 'SPOT':
                if bpy.app.version < (4,0,0):
                    row.prop(settings,'gobo_link_spot_size')

            col.separator()
            row = col.row(align=True)
            row.prop(settings, 'gobo_category', text='')
            row.operator('lightmixer.generate_thumbnails', icon='RENDERLAYERS', text='').image_type='GOBO'
            row.operator('photographer.refresh_gobo_categories', icon='FILE_REFRESH', text='')
            col.template_icon_view(settings, "gobo_tex", show_labels=True, scale=5)
        box.enabled = settings.light_type != 'SUN'      
        
        box = parent_col.box()
        top_row = box.row(align=True)
        top_row.prop(settings,'ies')
        if settings.ies:
            col = box.column(align=True)
            col.prop(settings,'ies_opacity', slider=True)
            col.separator()
            row = col.row(align=True)
            row.prop(settings, 'ies_category', text='')
            row.operator('lightmixer.generate_ies_thumbs',icon='RENDERLAYERS', text='')
            row.operator('photographer.refresh_ies_categories', icon='FILE_REFRESH', text='')
            col.template_icon_view(settings, "ies_tex", show_labels=True, scale=5)
            col.separator()
            col.operator("lightmixer.reset_intensity").light=light_name
        box.enabled = settings.light_type not in {'SUN'}            

def light_row(context,light_obj,layout,collection=None,lightgroup=''):
    scene = context.scene
    solo_active = scene.lightmixer.solo_active
    view_prefs = context.preferences.view
    preferences = context.preferences.addons[base_package].preferences
    custom_icons = preview_collections["icons"]

    light = light_obj.data
    lightmixer = light_obj.lightmixer
    settings = light.photographer
    scene_lm = scene.lightmixer

    region_width_details = 310 * (preferences.screen_resolution/1920) * view_prefs.ui_scale

    # luxcore = False
    # if context.scene.render.engine == "LUXCORE" and not light.luxcore.use_cycles_settings:
    #     luxcore = True

    row = layout.row(align=True)
    row.scale_y = 1.25
    row.scale_x = 1
    main_col = row.column(align=True)
    col = row.column(align=True)
    row = col.row(align=True)

    select_row = row.row(align=True)
    name_row = row.row()

    shared_data = [o for o in bpy.data.objects if o.data == light]
    vl_shared_data = [o for o in bpy.context.view_layer.objects if o.data == light]
    if len(shared_data) > 1 and scene_lm.group_linked_data:
        lm_enable_icn = 'LIGHTGROUP_OFF'
        if not solo_active and lightmixer.enabled:
            if all(light_obj.lightmixer.enabled for light_obj in vl_shared_data):
                lm_enable_icn = 'LIGHTGROUP'
        lm_en = main_col.operator("lightmixer.enable", text="", icon_value=custom_icons[lm_enable_icn].icon_id, emboss=False)
        lm_en.light = light_obj.name
        lm_en.linked = True
        sel = select_row.operator("photographer.select", text='',
            icon="%s" % 'RESTRICT_SELECT_OFF'if all(light_obj.select_get() for light_obj in vl_shared_data)
            else 'RESTRICT_SELECT_ON')
        sel.obj_name = light_obj.name
        sel.linked = True
        name_row.prop(settings, "expand_group_linked_data", text=light.name+" (%s)" % str(len(shared_data)), toggle=True)
    else:        
        if solo_active and lightmixer.solo:
            lm_enable_icn = 'EVENT_S'
            row.alert=True
        elif not solo_active and lightmixer.enabled:
            lm_enable_icn = 'OUTLINER_OB_LIGHT'
        else:
            lm_enable_icn = 'LIGHT'
        main_col.operator("lightmixer.enable", text="",
                            icon=lm_enable_icn, emboss=False).light=light_obj.name
        select_row.operator("photographer.select", text='',
                    icon="%s" % 'RESTRICT_SELECT_OFF'if light_obj.select_get()
                    else 'RESTRICT_SELECT_ON').obj_name=light_obj.name
        
        name_row.prop(light_obj, "name", text='')
        
    name_row.ui_units_x = scene_lm.light_name_width
    row_sep = row.row(align=True)
    row_sep.ui_units_x = .4
    row_sep.prop(scene_lm,"light_name_width")
    row_sep.separator()

    split = row.split(align=True,factor=0.45)
    color_row = split.row(align=True)
    color_row.scale_x = 1
    if preferences.use_physical_lights:
        if settings.use_light_temperature:
            color_row.prop(settings, "light_temperature", text='')
            if context.region.width > region_width_details:
                c_row=color_row.row(align=True)
                c_row.ui_units_x = 0.6
                c_row.prop(settings, "preview_color_temp", text='')
        else:
            color_row.prop(settings, "color", text='')
        
        if context.region.width > region_width_details:
            icn = 'EVENT_K' if settings.use_light_temperature else 'EVENT_C'
            color_row.operator("photographer.switchcolormode",
                            icon=icn, text='').light=light.name
    else:
        color_row.prop(light, "color", text='')

    intensity_row = split.row(align=True)


    if light.type == 'SUN':
        if preferences.use_physical_lights:
            if settings.sunlight_unit == 'irradiance':
                intensity_row.prop(settings,"irradiance", text='')
            elif settings.sunlight_unit == 'illuminance':
                intensity_row.prop(settings,"illuminance", text='')
            elif settings.sunlight_unit == 'artistic':
                sub = intensity_row.split(factor=0.5,align=True)
                sub.prop(settings,"intensity", text='Intensity')
                sub.prop(settings,"light_exposure", text='')

            # unit_row = intensity_row.row(align=True)
            # unit_row.ui_units_x = 1
            # if context.region.width > 550:
            #     unit_row.prop(settings, "sunlight_unit", icon_only=True)
            #     intensity_row.separator()
        else:
            intensity_row.prop(light,"energy")

    else:
        if preferences.use_physical_lights:
            if settings.light_unit == 'artistic':
                # sub = intensity_row.split(factor=0.5,align=True)
                intensity_row.prop(settings,"intensity", text='')
                # sub.prop(settings,"light_exposure", text='')

            elif settings.light_unit == 'power':
                intensity_row.prop(settings,"power", text='')

            elif settings.light_unit == 'advanced_power':
                # sub = intensity_row.split(factor=0.5,align=True)
                intensity_row.prop(settings,"advanced_power", text='')
                # sub.prop(settings,"efficacy", text='Efficacy')

            elif settings.light_unit == 'lumen':
                intensity_row.prop(settings,"lumen", text='')

            elif settings.light_unit == 'candela':
                intensity_row.prop(settings,"candela", text='')

            # if light.type == 'AREA' and  settings.light_unit in {'lumen', 'candela'}:
            #     sub = intensity_row.row(align=True)
            #     sub.ui_units_x = 2
            #     label = "/m\u00B2"
            #     sub.prop(settings, "per_square_meter", text=label, toggle=True)
        else:
            intensity_row.prop(light,"energy")

    if context.region.width > region_width_details:
        exp_col = intensity_row.row(align=True)
        minus = exp_col.operator("lightmixer.light_stop", text='', icon='REMOVE')
        plus = exp_col.operator("lightmixer.light_stop", text='', icon='ADD')
    else:
        exp_col = intensity_row.column(align=True)
        exp_col.scale_y = 0.52
        plus = exp_col.operator("lightmixer.light_stop", text='', icon='TRIA_UP')
        minus = exp_col.operator("lightmixer.light_stop", text='', icon='TRIA_DOWN')
    plus.light = light.name
    plus.factor = 0.5
    minus.light = light.name
    minus.factor = -0.5

    if preferences.use_physical_lights:
        unit_row = intensity_row.row(align=True)
        unit_row.ui_units_x = 1
        if context.region.width > region_width_details:
            if light.type == 'SUN':
                unit_row.prop(settings, "sunlight_unit", icon_only=True)
            else:
                unit_row.prop(settings, "light_unit", icon_only=True)

    delete_row = row.row(align=True)
    if len(shared_data) > 1 and scene_lm.group_linked_data:
        del_op = delete_row.operator("lightmixer.delete", text="", icon='PANEL_CLOSE', emboss=False)
        del_op.light=light_obj.name
        del_op.linked = True
    else:
        delete_row.operator("lightmixer.delete", text="",
        icon='PANEL_CLOSE', emboss=False).light=light_obj.name

    if scene_lm.group_linked_data and len(shared_data) > 1:
        if settings.expand_group_linked_data:
            for light_obj in shared_data:
                row = layout.row(align=True)
                vl_lights = [obj for obj in bpy.context.view_layer.objects if obj.type == 'LIGHT']

                if scene.lightmixer.light_list_sorting == 'COLLECTION':
                    row.enabled = light_obj in [l for l in vl_lights] and collection in light_obj.users_collection
                elif scene.lightmixer.light_list_sorting == 'LIGHTGROUP':
                    row.enabled = light_obj in [l for l in vl_lights] and lightgroup == light_obj.lightgroup
                else:
                    row.enabled = light_obj in [l for l in vl_lights]

                lightmixer = light_obj.lightmixer
                if solo_active and lightmixer.solo:
                    lm_enable_icn = 'EVENT_S'
                    row.alert=True
                elif not solo_active and lightmixer.enabled:
                    lm_enable_icn = 'OUTLINER_OB_LIGHT'
                else:
                    lm_enable_icn = 'LIGHT'
                
                main_col = row.column(align=True)
                select_row = row.row(align=True)
                name_row = row.row()
                main_col.operator("lightmixer.enable", text="",
                        icon=lm_enable_icn, emboss=False).light=light_obj.name
                select_row.operator("photographer.select", text='',
                            icon="%s" % 'RESTRICT_SELECT_OFF'if light_obj.select_get()
                            else 'RESTRICT_SELECT_ON').obj_name=light_obj.name
            
                name_row.prop(light_obj, "name", text='')
                delete_row = row.row(align=True)
                delete_row.operator("lightmixer.delete", text="",
                        icon='PANEL_CLOSE', emboss=False).light=light_obj.name

def light_collection_row(context,coll,layout):
    settings = context.scene.lightmixer
    coll_lights = [obj.name for obj in coll.objects if obj.type=='LIGHT']
    if coll_lights:
        coll_lights= sorted(coll_lights)
        
        coll_box = layout.box()
        coll_row = coll_box.row(align=True)
        exp = coll_row.operator("photographer.collection_expand", text="",
                        icon='TRIA_DOWN' if coll.get('expand', True) else 'TRIA_RIGHT',
                        emboss=False)
        exp.collection=coll.name
        exp.cam_list=False

        if bpy.app.version >= (2, 91, 0):
            color_tag = 'OUTLINER_COLLECTION' if coll.color_tag == 'NONE' else 'COLLECTION_'+ coll.color_tag
        else:
            color_tag = 'GROUP'
        sel = coll_row.operator('photographer.select_collection', text='', icon=color_tag)
        sel.coll_name = coll.name
        sel.coll_type = 'LIGHT'
        coll_row.prop(coll, "name", text='')
        exp_col = coll_row.column(align=True)
        exp_col.scale_y = 0.52
        plus = exp_col.operator("lightmixer.light_stop", text='', icon='TRIA_UP')
        plus.collection = coll.name
        plus.factor = 0.5
        minus = exp_col.operator("lightmixer.light_stop", text='', icon='TRIA_DOWN')
        minus.collection = coll.name
        minus.factor = -0.5

        # Find Layer Collection inside the tree
        lc = [c for c in traverse_tree(context.view_layer.layer_collection) if c.name == coll.name][0]
        coll_row.prop(lc, "exclude", text='', icon_only=True, emboss=False)
        coll_row.prop(coll, "hide_viewport", text='', icon_only=True, emboss=False)
        coll_row.prop(coll, "hide_render", text='', icon_only=True, emboss=False)
        exclude = lc.exclude

    # Add lights into Collection box
    if coll.get('expand', True) and not exclude:
        parent_col = coll_box.column(align=True)

        # Remove light from list if there is already one with the same data
        if settings.group_linked_data:  
            grouped_lights = []
            seen = set()
            for light in coll_lights:                          
                if bpy.data.objects[light].data not in seen:
                    seen.add(bpy.data.objects[light].data)
                    grouped_lights.append(light)
            coll_lights= grouped_lights

        for light in coll_lights:
            if settings.list_filter:
                if settings.use_filter_invert:
                    if settings.list_filter.lower() not in light.lower():
                        light_row(context,bpy.data.objects[light],parent_col,collection=coll)
                elif settings.list_filter.lower() in light.lower():
                    light_row(context,bpy.data.objects[light],parent_col,collection=coll)
            else:
                light_row(context,bpy.data.objects[light],parent_col,collection=coll)

def lightgroup_row(context,lightgroup,layout):
    settings = context.scene.lightmixer
    custom_icons = preview_collections["icons"]
    lg_box = layout.box()
    lg_row = lg_box.row(align=True)

    # List Lights in Lightgroup
    lg_lights_objs = [obj for obj in bpy.data.objects if obj.type=='LIGHT' and obj.lightgroup==lightgroup.name]
    lg_lights = [light.name for light in lg_lights_objs]

    first_row = lg_row.row(align=True)
    exp = first_row.operator("photographer.lightgroup_expand", text="",
                        icon='TRIA_DOWN' if lightgroup.id_data.get(lightgroup.name+'_expand',True) else 'TRIA_RIGHT',
                        emboss=False)
    exp.lightgroup = lightgroup.name
    exp.emissive_mixer = False
    if all(not l.lightmixer.enabled for l in lg_lights_objs):
        icn = 'LIGHTGROUP_OFF'
    else:
        icn = 'LIGHTGROUP'
    first_row.operator("lightmixer.enable_lightgroup", text='', icon_value=custom_icons[icn].icon_id,emboss=False).lightgroup_name=lightgroup.name

    if all(light_obj.select_get() for light_obj in lg_lights_objs):
        icn = 'RESTRICT_SELECT_OFF'
    else:
        icn = 'RESTRICT_SELECT_ON' 
    first_row.operator("photographer.select_lightgroup", text='', icon=icn, emboss=False).lightgroup_name=lightgroup.name
    lg_row.operator("lightmixer.add_to_lightgroup", text='', icon='IMPORT').lightgroup=lightgroup.name
    lg_row.operator("lightmixer.remove_from_lightgroup", text='', icon='EXPORT')    
    lg_row.prop(lightgroup, "name", text='')
    exp_row = lg_row.row(align=True)
    minus = exp_row.operator("lightmixer.light_stop", text='', icon='REMOVE')
    minus.lightgroup = lightgroup.name
    minus.factor = -0.5
    plus = exp_row.operator("lightmixer.light_stop", text='', icon='ADD')
    plus.lightgroup = lightgroup.name
    plus.factor = 0.5

    if lg_lights:
        first_row.enabled = True
        col = lg_box.column(align=True)

        if lightgroup.id_data.get(lightgroup.name+'_expand',True):
            lg_lights= sorted(lg_lights)

            # Remove light from list if there is already one with the same data
            if settings.group_linked_data:
                grouped_lights = []
                seen = set()
                for light in lg_lights:                          
                    if bpy.data.objects[light].data not in seen:
                        seen.add(bpy.data.objects[light].data)
                        grouped_lights.append(light)
                lg_lights = grouped_lights

            for light in lg_lights:
                light_row(context,bpy.data.objects[light],col,lightgroup=lightgroup.name)
    else:
        first_row.enabled = False
        exp_row.enabled = False
    
    lg_row.operator("lightmixer.delete_lightgroup", text='',icon='PANEL_CLOSE', emboss=False).lightgroup=lightgroup.name


def light_panel(context,parent_ui):
    layout = parent_ui
    scene = context.scene
    settings = scene.lightmixer
    custom_icons = preview_collections["icons"]

    light_list,light_collections,active_light = list_lights(context)

    # Light list UI
    # box = layout.box()
    panel_row = layout.row(align=False)
    panel_col = panel_row.column()

    if not light_list:
        row = panel_col.row(align=True)
        row.alignment = 'CENTER'
        row.label(text="No Light in the Scene", icon='INFO')

    if scene.lightmixer.light_list_sorting == 'COLLECTION':
        for coll in light_collections:
            coll_lights = [obj.name for obj in coll.objects if obj.type=='LIGHT']
            if coll_lights:
                coll_lights= sorted(coll_lights)

                if coll.name in {'Master Collection', 'Scene Collection'}:
                    # sc = 'Scene collection'
                    # if  scene.lightmixer.list_filter in sc.lower():
                    coll_box = panel_col.box()
                    row = coll_box.row(align=True)
                    row.prop(scene.lightmixer, "scene_collection_expand", text="",
                                    icon='TRIA_DOWN' if scene.lightmixer.get('scene_collection_expand', True)
                                    else 'TRIA_RIGHT', emboss=False)
                    row.label(text='Scene Collection', icon='OUTLINER_COLLECTION')
                    col = coll_box.column(align=True)
                    # exclude = False

                    # Remove light from list if there is already one with the same data
                    if settings.group_linked_data:
                        grouped_lights = []
                        seen = set()
                        for light in coll_lights:                          
                            if bpy.data.objects[light].data not in seen:
                                seen.add(bpy.data.objects[light].data)
                                grouped_lights.append(light)
                        coll_lights = grouped_lights

                    if scene.lightmixer.scene_collection_expand:
                        for light in coll_lights:
                            if settings.list_filter:
                                if settings.use_filter_invert:
                                    if settings.list_filter.lower() not in light.lower():
                                        light_row(context,bpy.data.objects[light],col) 
                                elif settings.list_filter.lower() in light.lower():
                                    light_row(context,bpy.data.objects[light],col)    
                            else:
                                light_row(context,bpy.data.objects[light],col)

        light_list,light_collections,active_light = list_lights(bpy.context)
        filtered_items = [c for c in light_collections]
        rows_count = len(filtered_items)
        panel_col.template_list("PHOTOGRAPHER_UL_ViewPanel_LightCollectionsList", "Light List", bpy.data,
                "collections", scene.lightmixer, "active_light_collection_index", maxrows=rows_count)
        
    elif scene.lightmixer.light_list_sorting == 'LIGHTGROUP':
        view_layer = context.view_layer
        lightgroups = view_layer.lightgroups


        lg_box = panel_col.box()
        row = lg_box.row(align=True)
        first_row = row.row(align=True)
        first_row.prop(scene.lightmixer, "scene_collection_expand", text="",
                        icon='TRIA_DOWN' if scene.lightmixer.get('scene_collection_expand', True)
                        else 'TRIA_RIGHT', emboss=False)

        no_lg_lights_objs = [o for o in context.view_layer.objects if o.type=='LIGHT' and o.lightgroup not in lightgroups]
        no_lg_lights = [o.name for o in no_lg_lights_objs]

        if all(not l.lightmixer.enabled for l in no_lg_lights_objs):
            icn = 'LIGHTGROUP_OFF'
        else:
            icn = 'LIGHTGROUP'
        first_row.operator("lightmixer.enable_lightgroup", text='', icon_value=custom_icons[icn].icon_id,emboss=False).lightgroup_name=''

        all_selected = all(light_obj.select_get() for light_obj in no_lg_lights_objs)
        if all_selected:
            icn = 'RESTRICT_SELECT_OFF'
        else:
            icn = 'RESTRICT_SELECT_ON' 
        first_row.operator("photographer.select_lightgroup", text='', icon=icn, emboss=False).lightgroup_name=''

        first_row.label(text=' No Light Group')
        row.operator("lightmixer.add_lightgroup", text='', icon='ADD')
        row.operator("lightmixer.add_lightgroups_from_collections", text='', icon='COLLECTION_NEW')
        row.separator()
        row.operator("lightmixer.add_lightgroup_comp_graph", text='', icon='NODE_COMPOSITING')

        if not no_lg_lights: 
            first_row.enabled=False
        else:
            no_lg_lights= sorted(no_lg_lights)
            col = lg_box.column()

            # Remove light from list if there is already one with the same data  
            if settings.group_linked_data:
                grouped_lights = []
                seen = set()
                for light in no_lg_lights:                          
                    if bpy.data.objects[light].data not in seen:
                        seen.add(bpy.data.objects[light].data)
                        grouped_lights.append(light)
                no_lg_lights = grouped_lights

            if scene.lightmixer.scene_collection_expand:
                for light in no_lg_lights:
                    if settings.list_filter:
                        if settings.use_filter_invert:
                            if settings.list_filter.lower() not in light.lower():
                                light_row(context,bpy.data.objects[light],col) 
                        elif settings.list_filter.lower() in light.lower():
                            light_row(context,bpy.data.objects[light],col)    
                    else:
                        light_row(context,bpy.data.objects[light],col)

        filtered_items = [lg for lg in lightgroups]
        rows_count = len(filtered_items)
        row = panel_col.row()
        row.template_list("PHOTOGRAPHER_UL_ViewPanel_LightGroupsList", "Light Groups", view_layer,
                "lightgroups", view_layer, "active_lightgroup_index", maxrows=rows_count)
    
    else:
        filtered_items = [o for o in context.view_layer.objects if o.type=='LIGHT']
        rows_count = len(filtered_items)
        panel_col.template_list("PHOTOGRAPHER_UL_ViewPanel_LightList", "Light List", bpy.data,
                "objects", scene.lightmixer, "active_light_index",maxrows=rows_count)

class PHOTOGRAPHER_UL_ViewPanel_LightList(bpy.types.UIList):
    """Light List for Lightmixer panel"""

    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_property, index):
        col = layout.column(align=True)
        light_row(context,item,col)

    def draw_filter(self, context, layout):
        settings = context.scene.lightmixer
        layout.separator()
        col_main = layout.column(align=True)

        row = col_main.row(align=True)
        row.prop(settings, 'list_filter', text='', icon='VIEWZOOM')
        if settings.list_filter:
            clear = row.operator("photographer.button_string_clear", text='',
                    icon='PANEL_CLOSE',emboss=False)
            clear.prop='list_filter'
            clear.type = 'light'
        row.prop(settings, 'use_filter_invert', text='', icon='ARROW_LEFTRIGHT')
        row.separator()
        row.prop(settings, 'list_filter_reverse', text='', icon='SORT_DESC'
                if settings.list_filter_reverse else "SORT_ASC")
        row.prop(settings, 'group_linked_data', text='', icon='GROUP_VERTEX')
        row.separator()
        row.prop(settings,'light_list_sorting', icon_only=True, expand=True)

    def filter_items(self,context,data,propname):
        settings = context.scene.lightmixer
        filtered = []
        ordered = []
        items = getattr(data, propname)
        helper_funcs = bpy.types.UI_UL_list

        filtered = [self.bitflag_filter_item] * len(items)
        self.use_filter_sort_reverse = settings.list_filter_reverse

        ordered = helper_funcs.sort_items_by_name(items, "name")

        filtered_items = self.get_props_filtered_items()

        for i, item in enumerate(items):
            if not item in filtered_items:
                filtered[i] &= ~self.bitflag_filter_item

        return filtered,ordered

    def get_props_filtered_items(self):
        settings = bpy.context.scene.lightmixer
        lights = [o for o in bpy.context.view_layer.objects if o.type=='LIGHT']

        if settings.group_linked_data:
            # Remove light from list if there is already one with the same data
            filtered_items = []
            seen = set()
            for light in lights:
                if light.data not in seen:
                    seen.add(light.data)
                    filtered_items.append(light)
        else:
            filtered_items = lights
        if settings.list_filter:
            if settings.use_filter_invert:
                filtered_items = [o for o in filtered_items if o.name.lower().find(settings.list_filter.lower()) == -1]
            else:
                filtered_items = [o for o in filtered_items if not o.name.lower().find(settings.list_filter.lower()) == -1]

        return filtered_items

class PHOTOGRAPHER_UL_ViewPanel_LightCollectionsList(bpy.types.UIList):
    """Light List for Lightmixer panel"""

    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_property, index):
        col = layout.column(align=True)
        light_collection_row(context,item,col)


    def draw_filter(self, context, layout):
        settings = context.scene.lightmixer
        layout.separator()
        col_main = layout.column(align=True)

        row = col_main.row(align=True)
        row.prop(settings, 'list_filter', text='', icon='VIEWZOOM')
        if settings.list_filter:
            clear = row.operator("photographer.button_string_clear", text='',icon='PANEL_CLOSE',
                    emboss=False)
            clear.prop='list_filter'
            clear.type = 'light'
        row.prop(settings, 'use_filter_invert', text='', icon='ARROW_LEFTRIGHT')
        row.separator()
        row.prop(settings, 'list_filter_reverse', text='', icon='SORT_DESC'
                if settings.list_filter_reverse else "SORT_ASC")
        row.prop(settings, 'group_linked_data', text='', icon='GROUP_VERTEX')
        row.separator()
        row.prop(settings,'light_list_sorting', icon_only=True, expand=True)

    def filter_items(self,context,data,propname):
        settings = context.scene.lightmixer
        filtered = []
        ordered = []
        items = getattr(data, propname)
        helper_funcs = bpy.types.UI_UL_list

        filtered = [self.bitflag_filter_item] * len(items)
        self.use_filter_sort_reverse = settings.list_filter_reverse

        ordered = helper_funcs.sort_items_by_name(items, "name")

        filtered_items = self.get_props_filtered_items()

        for i, item in enumerate(items):
            if not item in filtered_items:
                filtered[i] &= ~self.bitflag_filter_item

        return filtered,ordered

    def get_props_filtered_items(self):
        settings = bpy.context.scene.lightmixer

        light_list,light_collections,active_light = list_lights(bpy.context)
        filtered_items = [c for c in light_collections]
        # if settings.list_filter:
        #     filtered_items = [o for o in filtered_items if not o.name.lower().find(settings.list_filter.lower()) == -1]
        return filtered_items
    
class PHOTOGRAPHER_UL_ViewPanel_LightGroupsList(bpy.types.UIList):
    """Light List for Lightmixer panel"""

    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_property, index):
        col = layout.column(align=True)
        lightgroup_row(context,item,col)


    def draw_filter(self, context, layout):
        settings = context.scene.lightmixer
        layout.separator()
        col_main = layout.column(align=True)

        row = col_main.row(align=True)
        row.prop(settings, 'list_filter', text='', icon='VIEWZOOM')
        if settings.list_filter:
            clear = row.operator("photographer.button_string_clear", text='',icon='PANEL_CLOSE',
                    emboss=False)
            clear.prop='list_filter'
            clear.type = 'light'
        row.prop(settings, 'use_filter_invert', text='', icon='ARROW_LEFTRIGHT')
        row.separator()
        row.prop(settings, 'list_filter_reverse', text='', icon='SORT_DESC'
                if settings.list_filter_reverse else "SORT_ASC")
        row.prop(settings, 'group_linked_data', text='', icon='GROUP_VERTEX')
        row.separator()
        row.prop(settings,'light_list_sorting', icon_only=True, expand=True)

    def filter_items(self,context,data,propname):
        settings = context.scene.lightmixer
        filtered = []
        ordered = []
        items = getattr(data, propname)
        helper_funcs = bpy.types.UI_UL_list

        filtered = [self.bitflag_filter_item] * len(items)
        self.use_filter_sort_reverse = settings.list_filter_reverse

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

class LIGHTMIXER_PT_ViewPanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Photographer'
    bl_label = "Light Mixer"
    bl_order = 12

    @classmethod
    def poll(cls, context):
        lmpe = context.preferences.addons[base_package].preferences.lightmixer_panel_enable
        return lmpe

    def draw_header_preset(self, context):
        layout = self.layout
        custom_icons = preview_collections["icons"]
        row = layout.row(align=True)
        row.scale_x = 1.25

        light_obj = None
        if context.object:
            if context.object.type =='LIGHT' and context.object.select_get():
                light_obj = bpy.context.object
            elif context.object.get('is_target',False):
                for obj in bpy.context.scene.objects:
                    if obj.type =='LIGHT' and obj.constraints.get("Aim Target") is not None:
                        if obj.constraints["Aim Target"].target == context.object:
                            light_obj = obj
                            break         

        if light_obj:
            light = light_obj.data
            settings = light.photographer
            row.label(text=light_obj.name)

            if settings.target_enabled:
                target_obj = get_target(light_obj.name)
                if target_obj.select_get():
                    icn = 'TARGET_SELECT_ON'
                else:
                    icn = 'TARGET_SELECT_OFF'
                if target_obj:
                    sel = row.operator("photographer.select", text="", icon_value = custom_icons[icn].icon_id)
                    sel.obj_name = target_obj.name
                    sel.is_target = True
                    row.operator("photographer.target_delete", text="", icon_value=custom_icons['TARGET_DELETE'].icon_id).obj_name=light_obj.name
            if not settings.target_enabled:
                row.operator("object.light_target_add", text="", icon_value=custom_icons['TARGET'].icon_id)

            row.operator("object.light_modal",text="", icon='ORIENTATION_GIMBAL')
            
        else:
            if context.preferences.addons[base_package].preferences.show_compact_ui:
                row.operator("lightmixer.add", text="", icon='LIGHT_POINT').type='POINT'
                row.operator("lightmixer.add", text="", icon='LIGHT_SPOT').type='SPOT'
                row.operator("lightmixer.add", text="", icon='LIGHT_AREA').type='AREA'
                row.operator("lightmixer.add", text="", icon='LIGHT_SUN').type='SUN'



    def draw(self, context):
        layout = self.layout
        layout.use_property_split = False

        col=layout.column(align=True)
        if not context.preferences.addons[base_package].preferences.show_compact_ui:
            row = col.row(align=True)
            row.scale_y = 1.2
            row.operator("lightmixer.add", text='Add Point', icon="LIGHT_POINT").type='POINT'
            row.operator("lightmixer.add", text='Add Spot', icon="LIGHT_SPOT").type='SPOT'
            row = col.row(align=True)
            row.scale_y = 1.2
            row.operator("lightmixer.add", text='Add Area', icon="LIGHT_AREA").type='AREA'
            row.operator("lightmixer.add", text='Add Sun', icon="LIGHT_SUN").type='SUN'

        light_panel(context,col)

class LIGHTMIXER_PT_NodeEditor_ViewPanel(bpy.types.Panel):
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'Photographer'
    bl_label = "Light Mixer"
    bl_order = 12

    @classmethod
    def poll(cls, context):
        lmpe = context.preferences.addons[base_package].preferences.lightmixer_panel_enable
        show_image_panels = bpy.context.preferences.addons[base_package].preferences.show_image_panels
        return show_image_panels and lmpe
    
    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator('lightmixer.add_lightgroup_comp_graph', icon='NODE_COMPOSITING')

class LIGHTMIXER_PT_PropertiesSubPanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Photographer'
    bl_label = "Light Properties"
    bl_parent_id = "LIGHTMIXER_PT_ViewPanel"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = False
        custom_icons = preview_collections["icons"]

        preferences = context.preferences.addons[base_package].preferences
        luxcore = False
        if context.scene.render.engine == "LUXCORE" and not light.luxcore.use_cycles_settings:
            luxcore = True

        light_obj = None
        if context.object:
            if context.object.type =='LIGHT' and context.object.select_get():
                light_obj = bpy.context.object
            elif context.object.get('is_target',False):
                for obj in bpy.context.scene.objects:
                    if obj.type =='LIGHT' and obj.constraints.get("Aim Target") is not None:
                        if obj.constraints["Aim Target"].target == context.object:
                            light_obj = obj
                            break         

        if light_obj:
            light = light_obj.data
            settings = light.photographer

            main_col = layout.column(align=True)
            if preferences.use_physical_lights:
                color_row = main_col.row(align=True)
                if settings.use_light_temperature:
                    color_row.prop(settings, "light_temperature", slider=True)
                    row2 = color_row.row(align=True)
                    row2.ui_units_x = 2
                    row2.prop(settings, "preview_color_temp", text='')
                    color_row.operator("photographer.switchcolormode",
                                icon="EVENT_K", text='').light=light.name
                else:
                    color_row.prop(settings, "color", text='')
                    color_row.operator("photographer.switchcolormode",
                                icon="EVENT_C", text='').light=light.name

                intensity_row = main_col.row(align=True)
                if light.type == 'SUN':
                    if settings.sunlight_unit == 'irradiance':
                        intensity_row.prop(settings,"irradiance", text='Irradiance')
                    elif settings.sunlight_unit == 'illuminance':
                        intensity_row.prop(settings,"illuminance", text='Lux')
                    elif settings.sunlight_unit == 'artistic':
                        sub = intensity_row.split(factor=0.5,align=True)
                        sub.prop(settings,"intensity", text='Intensity')
                        sub.prop(settings,"light_exposure", text='')
                else:
                    if settings.light_unit == 'artistic':
                            sub = intensity_row.split(factor=0.5,align=True)
                            sub.prop(settings,"intensity", text='Intensity')
                            sub.prop(settings,"light_exposure", text='')
                    elif settings.light_unit == 'power':
                        intensity_row.prop(settings,"power", text='Power')

                    elif settings.light_unit == 'advanced_power':
                        sub = intensity_row.split(factor=0.5,align=True)
                        sub.prop(settings,"advanced_power", text='Watts')
                        sub.prop(settings,"efficacy", text='Efficacy')

                    elif settings.light_unit == 'lumen':
                        intensity_row.prop(settings,"lumen", text='Lumen')

                    elif settings.light_unit == 'candela':
                        intensity_row.prop(settings,"candela", text='Candela')

                    if light.type == 'AREA' and  settings.light_unit in {'lumen', 'candela'}:
                        sub = intensity_row.row(align=True)
                        sub.ui_units_x = 2
                        label = "/m\u00B2"
                        sub.prop(settings, "per_square_meter", text=label, toggle=True)
            else:
                color_row = main_col.row(align=True)
                color_row.prop(light, "color", text='')
                intensity_row = main_col.row(align=True)
                intensity_row.prop(light,"energy")

            intensity_row.ui_units_x = 2
            minus = intensity_row.operator("lightmixer.light_stop", text='', icon='REMOVE')
            minus.light = light.name
            minus.factor = -0.5
            plus = intensity_row.operator("lightmixer.light_stop", text='', icon='ADD')
            plus.light = light.name
            plus.factor = 0.5

            row = intensity_row.row(align=True)
            row.ui_units_x = 1
            if preferences.use_physical_lights:
                if light.type == 'SUN':
                    row.prop(settings, "sunlight_unit", icon_only=True)
                else:
                    row.prop(settings, "light_unit", icon_only=True)
            else:
                row.separator()

            main_col.separator()
            shape_row = main_col.row(align=True)

            # Keep Photographer Light Type to rename automatically
            shape_row.prop(settings, "light_type", text='', icon='LIGHT_%s' % light.type, icon_only=True)
            if light.type == 'SUN':
                if luxcore:
                    shape_row.prop(light.luxcore, "relsize")
                else:
                    shape_row.prop(light, "angle", text='Disk Angle')
            elif light.type in  ('POINT','SPOT'):
                shape_row.prop(light, "shadow_soft_size", text='Radius')
                if light.type == 'SPOT' and settings.light_unit == 'advanced_power':
                    shape_row.prop(settings, "spot_power_conservation", icon='CONE', icon_only=True, toggle=True)
                if bpy.app.version >= (4,1,0):
                    soft_falloff_icn = 'SPHERECURVE' if light.use_soft_falloff else 'LINCURVE'
                    shape_row.prop(light, "use_soft_falloff", icon=soft_falloff_icn, icon_only=True, toggle=True)

            elif light.type == 'SPOT':
                sub =  main_col.row(align=True)
                if preferences.use_physical_lights:
                    sub.prop(settings, "spot_size", text='Cone')
                else:
                    sub.prop(light, "spot_size", text='Cone')
                sub.prop(light, "spot_blend", text='Blend')
            elif light.type == 'AREA':
                if energy_check(settings):
                    check_col = main_col.column(align=False)
                    check_col.label(text="Light Size changed", icon='INFO')
                    check_col.operator("photographer.applyphotographersettings",
                                        text="Recalculate Intensity")
                if context.scene.render.engine == "CYCLES" and bpy.app.version >= (2,93,0):
                    sub =  main_col.row(align=True)
                    sub.prop(light, "spread", text='Spread')

                if preferences.use_physical_lights:
                    # Use Photographer settings
                    data = settings
                else:
                    #Use Blender settings
                    data = light
                shape_row.prop(data, "shape", text='')
                if settings.shape in {'SQUARE','DISK'}:
                    shape_row.prop(data, "size", text='')
                else:
                    shape_row.prop(data, "size", text='')
                    shape_row.prop(data, "size_y", text='')

            # Target
            shape_row.separator()
            row = shape_row.row(align=True)
            row.scale_x = 1.25
            if settings.target_enabled:
                target_obj = get_target(light_obj.name)
                if target_obj.select_get():
                    icn = 'TARGET_SELECT_ON'
                else:
                    icn = 'TARGET_SELECT_OFF'
                if target_obj:
                    sel = row.operator("photographer.select", text="", icon_value = custom_icons[icn].icon_id)
                    sel.obj_name = target_obj.name
                    sel.is_target = True
                row.operator("photographer.target_delete", text="",
                             icon_value=custom_icons['TARGET_DELETE'].icon_id).obj_name=light_obj.name
            else:
                row.operator("object.light_target_add", text="", icon_value=custom_icons['TARGET'].icon_id)

            row.operator("object.light_modal",text="", icon='ORIENTATION_GIMBAL')
            # modal.light = light_obj.name
            # if settings.target_enabled and target_obj:
            #     modal.target = target_obj.name
            # else:
            #     modal.target = ''

            if light.type == 'SUN':
                main_col.separator()
                row = main_col.row(align=True)
                if settings.target_enabled:
                    row.enabled = False
                row.prop(settings, "use_elevation", text='')
                sub = row.row(align=True)
                sub.enabled = settings.use_elevation
                sub.prop(settings, "azimuth", slider=True)
                sub.prop(settings, "elevation", slider=True)

                if context.scene.render.engine == "LUXCORE":
                    row = main_col.row(align=True)
                    row.prop(light.luxcore, "sun_type", expand=True)
                    col = main_col.column(align=True)
            
            elif light.type == 'SPOT':
                main_col.separator()
                row = main_col.row(align=True)
                if preferences.use_physical_lights:
                    row.prop(settings, "spot_size", text='Cone')
                else:
                    row.prop(light, "spot_size", text='Cone')
                row.prop(light, "spot_blend", text='Blend')
            
            main_col.separator()
            light_textures_ui(main_col, context, settings, light.name)

            main_col.separator()
            main_col.label(text='Lightgroup:')
            row = main_col.row(align=True)
            view_layer = context.view_layer
            row.prop_search(light_obj, "lightgroup", view_layer, "lightgroups", text="", results_are_suggestions=True)
            row.operator("scene.view_layer_add_lightgroup", text='', icon='ADD')

        else:
            box = layout.box()
            row = box.row()
            row.alignment = 'CENTER'
            row.label(text="No Light selected and active")
            col = box.column()
            col.separator()

class LIGHTMIXER_PT_PropertiesRaysSubPanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Photographer'
    bl_label = "Ray Properties"
    bl_parent_id = "LIGHTMIXER_PT_PropertiesSubPanel"

    @classmethod
    def poll(cls, context):
        lmpe = context.preferences.addons[base_package].preferences.lightmixer_panel_enable
        return lmpe

    def draw(self, context):
        layout = self.layout

        light_obj = None
        if context.object:
            if context.object and context.object.type =='LIGHT':
                light_obj = bpy.context.object
            elif context.object.get('is_target',False):
                for obj in bpy.context.scene.objects:
                    if obj.type =='LIGHT' and obj.constraints.get("Aim Target") is not None:
                        if obj.constraints["Aim Target"].target == context.object:
                            light_obj = obj
                            break         

        if light_obj:
            light = light_obj.data
            settings = light.photographer

            main_col = layout.column(align=True)
            col = main_col.column(align=True)
            row = col.row(align=True)
            if context.scene.render.engine in {"BLENDER_EEVEE","BLENDER_EEVEE_NEXT"}:
                if bpy.app.version >= (4,2,0):
                    row.prop(light, "diffuse_factor", slider=True, text='Diffuse')
                    row.prop(light, "specular_factor", slider=True, text='Specular')
                    row = col.row(align=True)
                    row.prop(light, "transmission_factor", slider=True, text='Transmission')
                    row.prop(light, "volume_factor", slider=True, text='Volume')
                else:
                    row.prop(light, "diffuse_factor", slider=True, text='Diffuse')
                    row.prop(light, "specular_factor", slider=True, text='Specular')
                    row.prop(light, "volume_factor", slider=True, text='Volume')
            elif context.scene.render.engine == "CYCLES":
                if bpy.app.version >= (3,0,0):
                    row.prop(light_obj, "visible_camera", toggle=True, text='Camera')
                    row.prop(light_obj, "visible_diffuse", toggle=True, text='Diffuse')
                    row.prop(light_obj, "visible_glossy", toggle=True, text='Glossy')
                else:
                    # row.prop(light_obj.cycles_visibility, "camera", toggle=True)
                    row.prop(light_obj.cycles_visibility, "diffuse", toggle=True)
                    row.prop(light_obj.cycles_visibility, "glossy", toggle=True)
                
            elif context.scene.render.engine == "LUXCORE":
                row.prop(light_obj.luxcore, "visible_to_camera", text="Camera", toggle=True)
                if light.type == 'SUN' and not light.luxcore.use_cycles_settings:
                    row.prop(light.luxcore, "visibility_indirect_diffuse", toggle=True)
                    row = col.row(align=True)
                    row.prop(light.luxcore, "visibility_indirect_glossy", toggle=True)
                    row.prop(light.luxcore, "visibility_indirect_specular", toggle=True)

            col.separator()
            row = col.row(align=True)
            if context.scene.render.engine == "BLENDER_EEVEE":
                row.prop(light, "use_shadow", text='Shadows', toggle=True)
                sub = row.row(align=True)
                sub.prop(light, "shadow_buffer_bias", text='Bias')
                sub.enabled = light.use_shadow
                row = col.row(align=True)
                row.prop(light, "use_contact_shadow", text='Contact Shadows', toggle=True)
                sub = row.row(align=True)
                sub.prop(light, "contact_shadow_distance", text='Distance')
                sub.enabled = light.use_contact_shadow
            elif context.scene.render.engine == 'BLENDER_EEVEE_NEXT':
                row.prop(light, "use_shadow", text='Shadows', toggle=True)
                if bpy.app.version >= (4,2,0):
                    sub = row.row(align=True)
                    sub.prop(light, "shadow_filter_radius", text="Filter")
                    sub.enabled = light.use_shadow
                    jitter = col.row(align=True)
                    jitter.enabled = light.use_shadow
                    jitter.prop(light, "use_shadow_jitter",text="Jitter",toggle=True)
                    sub = jitter.row(align=True)
                    sub.active = light.use_shadow_jitter
                    sub.prop(light, "shadow_jitter_overblur", text="Overblur")
                    sub.enabled = light.use_shadow
                    sub = col.column(align=True)
                    row = sub.row(align=True)
                    row.prop(light, "shadow_maximum_resolution", text="Resolution Limit")
                    if light.type != 'SUN':
                        row.prop(light, "use_absolute_resolution", text="", icon='DRIVER_DISTANCE') 
                    sub.enabled = light.use_shadow
                else:
                    row.prop(light, "shadow_softness_factor", text='Softness')
                    if light.type == 'SUN':
                        col.prop(light,'shadow_trace_distance',text='Trace Distance')

            elif context.scene.render.engine == "CYCLES":
                if bpy.app.version >= (4,2,0):
                    row.prop(light, "use_shadow", text='Shadows', toggle=True)
                else:
                    row.prop(light.cycles, "cast_shadow", text='Shadows', toggle=True)
                if bpy.app.version >= (3,2,0):
                    row.prop(light.cycles, "is_caustics_light", text='Caustics', toggle=True)
                col.separator()
                row = col.row(align=True)
                row.prop(settings, "light_falloff", text='')
                row.prop(settings,"light_falloff_smooth")
                row.enabled = light.type != 'SUN'