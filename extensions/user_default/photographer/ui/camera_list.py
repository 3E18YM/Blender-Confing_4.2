import bpy,math
from ..functions.functions import traverse_tree, list_cameras
from ..rigs.build_rigs import get_camera_rig
from ..operators.target import get_target
from ..icons.icons import preview_collections
from .. import __package__ as base_package

def camera_row(context,cam,col):
    # cam_obj = bpy.data.objects.get(cam)
    cam_obj = cam
    cam = cam.name
    scene = context.scene
    custom_icons = preview_collections["icons"]

    # if cam_obj.type=='CAMERA':
    cam_settings = cam_obj.data.photographer

    row = col.row(align=True)
    # row.scale_y = 1
    if scene.camera and scene.camera == bpy.data.objects.get('DroneCamera'):
        target_camera = scene.camera.data.photographer.target_camera
        icn = "PLAY"
        if target_camera and cam == target_camera.name:
            icn = "RADIOBUT_ON"
        row.operator("view3d.switch_camera", text="", icon=icn).camera=cam
    else:
        row.prop(cam_settings, "renderable", text="")

    if scene.camera == cam_obj:
        row.operator("photographer.look_through", text="", icon='RESTRICT_RENDER_OFF').camera=cam
    else:
        row.operator("photographer.look_through", text="", icon='RESTRICT_RENDER_ON').camera=cam

    sel = row.operator("photographer.select", text='',
                    icon="%s" % 'RESTRICT_SELECT_OFF'if cam_obj.select_get()
                    else 'RESTRICT_SELECT_ON').obj_name = cam

    if cam_obj.get('is_rigged', False):
        rig_obj = get_camera_rig(cam_obj)
        if rig_obj:
            row.operator("photographer.select", text='',
                        icon="%s" % 'OUTLINER_OB_ARMATURE'if rig_obj.select_get()
                        else 'ARMATURE_DATA').obj_name = rig_obj.name

    main_cam = context.scene.photographer.main_camera
    if main_cam:
        if cam_obj.data == main_cam:
            row.label(icon_value = custom_icons['MAIN_CAMERA'].icon_id,text='')
    row.prop(bpy.data.objects[cam], "name", text='')
    if cam_settings.show_focus_plane:
        row.operator("photographer.delete_focus_plane", text="", icon='CANCEL').camera=cam
    else:
        row.operator("photographer.create_focus_plane", text="", icon='NORMALS_FACE').camera=cam
    if cam_settings.target_enabled:
        target = get_target(cam)
        if target:
            if target.select_get():
                icn = 'TARGET_SELECT_ON'
            else:
                icn = 'TARGET_SELECT_OFF'
            sel = row.operator("photographer.select", text="", icon_value = custom_icons[icn].icon_id)
            sel.obj_name=target.name
            sel.is_target=True
        row.operator("photographer.target_delete", text="", icon_value=custom_icons['TARGET_DELETE'].icon_id).obj_name=cam
    else:
        row.operator("photographer.target_add", text="", icon_value=custom_icons['TARGET'].icon_id).obj_name=cam
    row.operator("photographer.delete_cam", text="", icon='PANEL_CLOSE', emboss=False).camera=cam

    if cam not in context.view_layer.objects:
        row.enabled = False

def camera_collection_row(context,coll,layout):
    settings = context.scene.photographer
    exclude = False
    coll_box = layout.box()

    coll_cams = [obj.name for obj in coll.objects if obj.type=='CAMERA' and obj.name!='DroneCamera']
    if coll_cams:
        coll_cams= sorted(coll_cams)

        coll_row = coll_box.row(align=True)
        exp = coll_row.operator("photographer.collection_expand", text="",
                        icon='TRIA_DOWN' if coll.get('cl_expand', True) else 'TRIA_RIGHT',
                        emboss=False)
        exp.collection=coll.name
        exp.cam_list=True

        if bpy.app.version >= (2, 91, 0):
            color_tag = 'OUTLINER_COLLECTION'if coll.color_tag == 'NONE' else 'COLLECTION_'+ coll.color_tag
        else:
            color_tag = 'GROUP'
        sel = coll_row.operator('photographer.select_collection', text='', icon=color_tag)
        sel.coll_name = coll.name
        sel.coll_type = 'CAMERA'
        coll_row.prop(coll, "name", text='')

        # Find Layer Collection inside the tree
        lc = [c for c in traverse_tree(context.view_layer.layer_collection) if c.name == coll.name]
        if lc:
            lc = lc[0]
            coll_row.prop(lc, "exclude", text='', icon_only=True, emboss=False)
            # coll_row.prop(coll, "hide_viewport", text='', icon_only=True, emboss=False)
            coll_row.prop(coll, "hide_render", text='', icon_only=True, emboss=False)
            exclude = lc.exclude

    # Add cameras into Collection box
    if coll.get('cl_expand', True) and not exclude:
        parent_col = coll_box.column(align=True)

        if settings.renderable_only:
            coll_cams=[c for c in coll_cams if bpy.data.objects[c].data.photographer.renderable]
        
        for cam in coll_cams:
            cam_obj = bpy.data.objects.get(cam)
            if settings.list_filter:
                if settings.use_filter_invert:
                    if settings.list_filter.lower() not in cam.lower():
                        camera_row(context,cam_obj,parent_col)
                elif settings.list_filter.lower() in cam.lower():
                    camera_row(context,cam_obj,parent_col)
            else:
                camera_row(context,cam_obj,parent_col)

def camera_list_header(context,layout):
    if context.preferences.addons[base_package].preferences.show_compact_ui:
        cameras,cam_collections = list_cameras(context)
        if not cameras:
            layout.operator("photographer.add_cam", text='Add Camera', icon="ADD")
        else:
            row=layout.row()
            row.scale_x = 1.15
            row.prop(context.scene, "camera",text='')        
        layout.separator()

def camera_list_panel(context,parent_ui):
    layout = parent_ui
    scene = context.scene
    settings = scene.photographer

    cameras,cam_collections = list_cameras(context)

    # Camera list UI
    panel_row = layout.row(align=False)
    panel_col = panel_row.column()

    if not cameras:
        row = panel_col.row(align=True)
        row.alignment = 'CENTER'
        row.label(text="No Camera in the Scene", icon='INFO')

    if settings.cam_list_sorting == 'COLLECTION':
        for coll in cam_collections:
            coll_cams = [obj.name for obj in coll.objects if obj.type=='CAMERA' and obj.name!='DroneCamera']
            if coll_cams:
                coll_cams= sorted(coll_cams)
                # If not in a Collection, add camera to the base layout
                if coll.name in {'Master Collection', 'Scene Collection'}:
                    coll_box = panel_col.box()
                    row = coll_box.row(align=True)
                    row.prop(settings, "scene_collection_expand", text="",
                                    icon='TRIA_DOWN' if settings.get('scene_collection_expand', True)
                                    else 'TRIA_RIGHT', emboss=False)
                    row.label(text='Scene Collection', icon='OUTLINER_COLLECTION')
                    col = coll_box.column(align=True)

                    if settings.scene_collection_expand:
                        for cam in coll_cams:
                            if settings.list_filter:
                                if settings.use_filter_invert:
                                    if settings.list_filter.lower() not in cam.lower():
                                        camera_row(context,bpy.data.objects[cam],col) 
                                elif settings.list_filter.lower() in cam.lower():
                                    camera_row(context,bpy.data.objects[cam],col)    
                            else:
                                camera_row(context,bpy.data.objects[cam],col)

                #     coll_box = panel_col.row(align=True)
                #     exclude = False
                # else:
                    
                #     coll_box = panel_col.box()
                #     coll_row = coll_box.row(align=True)
                #     exp = coll_row.operator("photographer.collection_expand", text="",
                #                     icon='TRIA_DOWN' if coll.get('cl_expand', True) else 'TRIA_RIGHT',
                #                     emboss=False)
                #     exp.collection=coll.name
                #     exp.cam_list=True

                #     if bpy.app.version >= (2, 91, 0):
                #         color_tag = 'OUTLINER_COLLECTION'if coll.color_tag == 'NONE' else 'COLLECTION_'+ coll.color_tag
                #     else:
                #         color_tag = 'GROUP'
                #     sel = coll_row.operator('photographer.select_collection', text='', icon=color_tag)
                #     sel.coll_name = coll.name
                #     sel.coll_type = 'CAMERA'
                #     coll_row.prop(coll, "name", text='')

                #     # Find Layer Collection inside the tree
                #     lc = [c for c in traverse_tree(context.view_layer.layer_collection) if c.name == coll.name][0]
                #     coll_row.prop(lc, "exclude", text='', icon_only=True, emboss=False)
                #     # coll_row.prop(coll, "hide_viewport", text='', icon_only=True, emboss=False)
                #     coll_row.prop(coll, "hide_render", text='', icon_only=True, emboss=False)
                #     exclude = lc.exclude

                # # Add cameras into Collection box
                # if coll.get('cl_expand', True) and not exclude:
                #     parent_col = coll_box.column(align=True)
                #     for cam in coll_cams:
                #         # Disable light boxes if Collection is hidden in Viewport
                #         if coll.hide_viewport:
                #             col.enabled = False
                #         cam_obj = bpy.data.objects.get(cam)
                #         camera_row(context,cam_obj,parent_col)
        panel_col.template_list("PHOTOGRAPHER_UL_ViewPanel_CameraCollectionsList", "Camera List", bpy.data,
                "collections", scene.photographer, "active_camera_collection_index")
    else:
        # # Alphabetical Sorting
        # col = box.column(align=True)
        # for cam in cam_list:
        #     camera_row(context,cam,col)
        panel_col.template_list("PHOTOGRAPHER_UL_ViewPanel_CameraList", "Camera List", bpy.data,
                "objects", settings, "active_camera_index")
    col = panel_row.column(align=True)
    col.operator("photographer.add_cam", text='', icon="ADD")
    col.operator("photographer.duplicate_cam",text="", icon='DUPLICATE')
    col.separator()
    order = True
    if settings.list_filter_reverse:
        order = not order
    col.operator('view3d.cycle_camera', text='', icon='TRIA_UP').previous=order
    col.operator('view3d.cycle_camera', text='', icon='TRIA_DOWN').previous=not order
    icn = 'CHECKBOX_HLT' if scene.photographer.cycle_renderable_only else 'CHECKBOX_DEHLT'
    col.prop(scene.photographer,'cycle_renderable_only', icon=icn, toggle=True, text='')

    # Local Camera
    view = context.space_data

    col = layout.column(align=True,heading="Camera Settings")

    tolerance = 1e-4
    is_scale_one = True
    if scene.camera and scene.camera.type=='CAMERA':
        is_scale_one = all(math.isclose(s, 1.0, abs_tol=tolerance) for s in scene.camera.scale)
    if not is_scale_one:
        col.operator('photographer.reset_camera_scale', icon='ERROR', text='Reset Scene Camera scaling').camera=scene.camera.name
    
    row = layout.row(align=True)
    split = row.split(factor=0.35, align=True)
    split.label(text="Local Camera")
    sub = split.row(align=True)
    sub.prop(view, "use_local_camera", text="")
    sub = sub.row(align=True)
    sub.enabled = view.use_local_camera
    sub.prop(view, "camera", text="")

    # Lock Camera to View and Border
    render = scene.render
    if view.lock_camera:
        icon="LOCKVIEW_ON"
    else:
        icon="LOCKVIEW_OFF"

    row = layout.row()
    split = row.split(factor=0.7, align=False)
    split.prop(view, "lock_camera", text="Lock Camera to View", icon=icon )
    split.prop(render, "use_border", text="Border")
 
    col = layout.column(align=True)
    # apply_col = col.column(align=True)
    # apply_col.operator("photographer.applyphotographersettings",
    #     icon='FILE_REFRESH')
    # apply_col.enabled=False
    # if scene.camera and scene.camera.type == 'CAMERA':
    #     apply_col.enabled=True
             
    col.operator("photographer.target_refresh_names",
        icon='FILE_REFRESH')

    # Drone Camera UI
    if bpy.context.preferences.addons[base_package].preferences.show_drone_camera:
        box = layout.box()
        drone_row = box.row(align=True)

        drone_cam = next((obj.name for obj in scene.objects if obj.type == 'CAMERA' and obj.name == 'DroneCamera'), None)

        if drone_cam:
            if context.scene.camera == bpy.data.objects.get(drone_cam):
                icn ='RESTRICT_RENDER_OFF'
            else:
                icn = 'RESTRICT_RENDER_ON'
            drone_row.operator("photographer.select", text="",
                icon="%s" % 'RESTRICT_SELECT_OFF' if bpy.data.objects['DroneCamera'].select_get()
                else 'RESTRICT_SELECT_ON').obj_name=drone_cam
            drone_row.operator("photographer.look_through", text=drone_cam, icon=icn).camera=drone_cam
            drone_row.operator("photographer.delete_cam", text="", icon="PANEL_CLOSE", emboss=False).camera=drone_cam
            col = box.column(align=True)
            col.prop(bpy.data.objects.get(drone_cam).data.photographer, "match_speed", slider=True)
            if context.scene.camera == bpy.data.objects.get(drone_cam):
                col.operator("photographer.set_key", text='Set Key', icon='KEY_HLT')
        else:
            drone_row.operator("photographer.add_dronecamera", text='Add Drone Camera', icon='OUTLINER_DATA_CAMERA')

    # # Render button
    # if scene.camera:
    #     if scene.camera == bpy.data.objects.get(drone_cam):
    #         layout.operator("render.render",text="Render Drone Camera").write_still=True
    #     else:
    #         col = layout.column(align=True)
    #         row = col.row(align=True)
    #         row.operator("render.render",text="Render Active").write_still=True
    #         row.operator("render.renderallbutton")
    #         renderable_cams = [c for c in cameras if c.data.photographer.renderable == True]
    #         row = col.row(align=True)
    #         row.prop(render, "filepath", text="")


class PHOTOGRAPHER_UL_ViewPanel_CameraList(bpy.types.UIList):
    """Camera list for Photographer Panel"""

    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_property, index):
        col = layout.column(align=True)
        camera_row(context,item,col)

    def draw_filter(self, context, layout):
        settings = context.scene.photographer
        layout.separator()
        col_main = layout.column(align=True)

        row = col_main.row(align=True)
        row.prop(settings, 'list_filter', text='', icon='VIEWZOOM')
        if settings.list_filter:
            clear = row.operator("photographer.button_string_clear", text='',
                            icon='PANEL_CLOSE',emboss=False)
            clear.prop='list_filter'
            clear.type = 'camera'
        row.prop(settings, 'use_filter_invert', text='', icon='ARROW_LEFTRIGHT')
        row.separator()
        row.prop(settings, 'list_filter_reverse', text='', icon='SORT_DESC' if settings.list_filter_reverse else "SORT_ASC")
        row.separator()
        row.prop(settings,'renderable_only', text='', icon='CHECKBOX_HLT' if settings.renderable_only else 'CHECKBOX_DEHLT')
        row.prop(settings, 'hide_excluded', text='', icon='HIDE_ON' if settings.hide_excluded else 'HIDE_OFF')
        row.separator()
        row.prop(settings,'cam_list_sorting', icon_only=True, expand=True)

    def filter_items(self,context,data,propname):
        settings = context.scene.photographer
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
        settings = bpy.context.scene.photographer

        if settings.hide_excluded:
            filtered_items = [o for o in bpy.context.view_layer.objects if o.type=='CAMERA' and o.name!='DroneCamera']
        else:
            filtered_items = [o for o in bpy.context.scene.objects if o.type=='CAMERA' and o.name!='DroneCamera']

        if settings.renderable_only:
            filtered_items = [o for o in filtered_items if o.data.photographer.renderable]

        if settings.list_filter:
            if settings.use_filter_invert:
                filtered_items = [o for o in filtered_items if o.name.lower().find(settings.list_filter.lower()) == -1]
            else:
                filtered_items = [o for o in filtered_items if not o.name.lower().find(settings.list_filter.lower()) == -1]

        return filtered_items

class PHOTOGRAPHER_UL_ViewPanel_CameraCollectionsList(bpy.types.UIList):
    """Camera Collection list for Photographer Panel"""

    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_property, index):
        col = layout.column(align=True)
        camera_collection_row(context,item,col)

    def draw_filter(self, context, layout):
        settings = context.scene.photographer
        layout.separator()
        col_main = layout.column(align=True)

        row = col_main.row(align=True)
        row.prop(settings, 'list_filter', text='', icon='VIEWZOOM')
        if settings.list_filter:
            clear = row.operator("photographer.button_string_clear", text='',
                            icon='PANEL_CLOSE',emboss=False)
            clear.prop='list_filter'
            clear.type = 'camera'
        row.prop(settings, 'use_filter_invert', text='', icon='ARROW_LEFTRIGHT')
        row.separator()
        row.prop(settings, 'list_filter_reverse', text='', icon='SORT_DESC' if settings.list_filter_reverse else 'SORT_ASC')
        row.separator()
        row.prop(settings,'renderable_only', text='', icon='CHECKBOX_HLT' if settings.renderable_only else 'CHECKBOX_DEHLT')
        row.prop(settings, 'hide_excluded', text='', icon='HIDE_ON' if settings.hide_excluded else 'HIDE_OFF')
        row.separator()
        row.prop(settings,'cam_list_sorting', icon_only=True, expand=True)

    def filter_items(self,context,data,propname):
        settings = context.scene.photographer
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
        settings = bpy.context.scene.photographer

        cameras,cam_collections = list_cameras(bpy.context, not settings.hide_excluded)
        filtered_items = [c for c in cam_collections]

        return filtered_items

class PHOTOGRAPHER_PT_ViewPanel_CameraList(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Photographer'
    bl_label = "Camera List"
    bl_order = 0

    @classmethod
    def poll(cls, context):
        clpe = context.preferences.addons[base_package].preferences.camera_list_panel_enable
        return clpe

    def draw_header_preset(self, context):
        camera_list_header(context,self.layout)

    def draw(self, context):
        camera_list_panel(context,self.layout)


# class PHOTOGRAPHER_PT_NodeEditor_CameraList(PHOTOGRAPHER_PT_ViewPanel_CameraList):
#     bl_space_type = 'NODE_EDITOR'

#     @classmethod
#     def poll(cls, context):
#         snode = context.space_data
#         show_image_panels =  bpy.context.preferences.addons[base_package].preferences.show_image_panels
#         return context.scene.camera and context.scene.camera.type == 'CAMERA' and show_image_panels and snode.tree_type == 'CompositorNodeTree'

# class PHOTOGRAPHER_PT_ImageEditor_CameraList(PHOTOGRAPHER_PT_ViewPanel_CameraList):
#     bl_space_type = 'IMAGE_EDITOR'

#     @classmethod
#     def poll(cls, context):
#         # Add Panel properties to cameras
#         return bpy.context.preferences.addons[base_package].preferences.show_image_panels