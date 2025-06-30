import bpy
from bpy.types import Operator
from .camera_list import camera_list_panel, camera_list_header
from .. import __package__ as base_package
from .. import camera_presets
from ..ui import camera_panel,lens_panel, post_effects_panel

property_names=["tab","camera_list_expand","camera_expand","pos_bookmarks_expand","lens_expand",
                "dof_expand","focus_expand","autofocus_expand","post_fx_expand","expo_expand",
                "whitebalance_expand","postfx_expand","resolution_expand","viewlayer_expand"]

globals_dict = {}

class PHOTOGRAPHER_OT_Sticky_Menu(Operator):
    bl_label = "Photographer Sticky Menu"
    bl_idname = "photographer.sticky_menu"
    bl_options = {'REGISTER', 'UNDO'}

    tab : bpy.props.EnumProperty(
        name = "Menu Tab",
        items = [('CAMERA','Camera',''),('LENS','Lens',''),('POST_FX','Post FX',''),('RENDER','Render', '')],
    )
    camera_list_expand : bpy.props.BoolProperty(default=True, name='Expand Camera List')
    camera_expand : bpy.props.BoolProperty(name='Expand Camera Panel')
    pos_bookmarks_expand : bpy.props.BoolProperty(name='Expand Position Bookmarks')
    lens_expand : bpy.props.BoolProperty(name='Expand Lens')
    dof_expand : bpy.props.BoolProperty(name='Expand Depth of Field')
    focus_expand : bpy.props.BoolProperty(name='Expand Focus')
    autofocus_expand : bpy.props.BoolProperty(name='Expand Autofocus')
    post_fx_expand : bpy.props.BoolProperty(name='Expand Camera Post FX')
    expo_expand : bpy.props.BoolProperty(name='Expand Exposure')
    whitebalance_expand : bpy.props.BoolProperty(name='Expand White Balance')
    postfx_expand : bpy.props.BoolProperty(name='Expand Post FX')
    resolution_expand : bpy.props.BoolProperty(name='Expand Resolution')
    resize_canvas_expand : bpy.props.BoolProperty(name='Expand Resize Canvas')
    viewlayer_expand : bpy.props.BoolProperty(name='Expand View Layer')

    def draw(self, context):
        scene = context.scene
        prefs = context.preferences.addons[base_package].preferences
        layout = self.layout

        if prefs.menu_multi_tab:
            row = layout.row(align=True)
            row.scale_y = 1.5
            row.prop(self, 'tab', expand=True)

        menu = layout.column()

        if scene.camera:
            settings = scene.camera.data.photographer

        if self.tab == 'CAMERA' or not prefs.menu_multi_tab:
            clme = prefs.camera_list_menu_enable
            if clme:
                box = menu.box()
                header_row = box.row(align=True)
                header_row.prop(self, 'camera_list_expand', toggle=True, text='',emboss=False,
                                icon='DOWNARROW_HLT' if self.camera_list_expand else 'RIGHTARROW')
                header_row.label(text='Camera List')
                camera_list_header(context,header_row)
                if self.camera_list_expand:
                    camera_list_panel(context,box)     

            if scene.camera and scene.camera!= bpy.data.objects.get('DroneCamera'):
                col = menu.column()

                cme = prefs.camera_menu_enable
                if context.scene.camera.type == 'CAMERA' and cme:
                    box = menu.box()
                    header_row = box.row(align=True)
                    header_row.prop(self, 'camera_expand', toggle=True, text='',emboss=False,
                                    icon='DOWNARROW_HLT' if self.camera_expand else 'RIGHTARROW')
                    header_row.label(text='Camera')
                    camera_panel.camera_panel_draw_header_preset(context,header_row)
                    header_row.separator()
                    camera_presets.PHOTOGRAPHER_PT_CameraPresets.draw_panel_header(header_row)
                    if self.camera_expand:
                        camera_panel.camera_panel_draw(context,box)
                    
                    bme = prefs.bookmarks_menu_enable
                    if bme:
                        box = menu.box()
                        header_row = box.row(align=True)
                        header_row.prop(self, 'pos_bookmarks_expand', toggle=True, text='',emboss=False,
                                        icon='DOWNARROW_HLT' if self.pos_bookmarks_expand else 'RIGHTARROW')
                        header_row.label(text='Position Bookmarks')
                        header_row.operator("photographer.bookmark_add", icon='ADD', text="").camera=context.scene.camera.data.name
                        if self.pos_bookmarks_expand:
                            box.template_list("PHOTOGRAPHER_UL_Bookmarks_Item", "", context.scene.camera.data, "bookmarks",
                                                context.scene.camera.data.photographer, "active_bookmark_index")
        
        if (self.tab == 'LENS' or not prefs.menu_multi_tab) and scene.camera:
            lme = prefs.lens_menu_enable
            if context.scene.camera.type == 'CAMERA' and lme:
                box = menu.box()
                header_row = box.row(align=True)
                header_row.prop(self, 'lens_expand', toggle=True, text='',emboss=False,
                                icon='DOWNARROW_HLT' if self.lens_expand else 'RIGHTARROW')
                header_row.label(text='Lens')
                lens_panel.lens_panel_draw_header_preset(context,header_row)
                header_row.separator()
                camera_presets.PHOTOGRAPHER_PT_LensPresets.draw_panel_header(header_row)
                if self.lens_expand:
                    lens_panel.lens_panel_draw(context,box)

            dme = prefs.dof_menu_enable
            if context.scene.camera.type == 'CAMERA' and dme:
                box = menu.box()
                header_row = box.row(align=True)
                header_row.prop(self, 'dof_expand', toggle=True, text='',emboss=False,
                                icon='DOWNARROW_HLT' if self.dof_expand else 'RIGHTARROW')
                header_row.prop(settings, "use_dof", text="")
                header_row.label(text='Depth of Field')
                row=header_row.row(align=True)
                camera_panel.dof_panel_draw_header_preset(context,row)
                if self.dof_expand:
                    col=box.column(align=True)
                    camera_panel.dof_panel_draw(self,context,col)

            fme = prefs.focus_menu_enable
            if context.scene.camera.type == 'CAMERA' and fme:
                box = menu.box()
                header_row = box.row(align=True)
                header_row.prop(self, 'focus_expand', toggle=True, text='',emboss=False,
                                icon='DOWNARROW_HLT' if self.focus_expand else 'RIGHTARROW')
                header_row.label(text='Focus')
                camera_panel.focus_panel_draw_header_preset(context,header_row)
                if self.focus_expand:
                    camera_panel.focus_panel_draw(context,box)
                    box=box.box()
                    header_row = box.row(align=True)
                    header_row.prop(self, 'autofocus_expand', toggle=True, text='',emboss=False,
                                    icon='DOWNARROW_HLT' if self.autofocus_expand else 'RIGHTARROW')
                    header_row.label(text='Autofocus')
                    if self.autofocus_expand:
                        col=box.column(align=True)
                        camera_panel.autofocus_panel_draw(context,col)
                
        if (self.tab == 'POST_FX' or not prefs.menu_multi_tab) and scene.camera:
            # Exposure
            eme = prefs.exposure_menu_enable
            if context.scene.camera.type == 'CAMERA' and eme:
                box = menu.box()
                header_row = box.row(align=True)
                header_row.prop(self, 'expo_expand', toggle=True, text='',emboss=False,
                                icon='DOWNARROW_HLT' if self.expo_expand else 'RIGHTARROW')
                camera_panel.exposure_header(context,header_row,True)
                header_row.label(text='Exposure')
                camera_panel.exposure_header_preset(context,header_row,settings,False)
                header_row.separator()
                camera_presets.PHOTOGRAPHER_PT_ExposurePresets.draw_panel_header(header_row)
                if self.expo_expand:
                    col = box.column()
                    camera_panel.exposure_panel(context,col,settings,False,True)

            # White Balance
            wbme = prefs.wb_menu_enable
            if context.scene.camera.type == 'CAMERA' and wbme:
                box = menu.box()
                header_row = box.row(align=True)
                header_row.prop(self, 'whitebalance_expand', toggle=True, text='',emboss=False,
                                icon='DOWNARROW_HLT' if self.whitebalance_expand else 'RIGHTARROW')
                camera_panel.whitebalance_header(context,header_row,True)
                header_row.label(text='White Balance')
                
                header_row.separator()
                camera_panel.whitebalance_header_preset(context,header_row,True,'3D_VIEW_MENU')
                if self.whitebalance_expand:
                    col = box.column()
                    camera_panel.whitebalance_panel(context,col,settings)

            # Post FX
            pfme = prefs.postfx_menu_enable
            if context.scene.camera.type == 'CAMERA' and pfme:
                box = menu.box()
                header_row = box.row(align=True)
                header_row.prop(self, 'postfx_expand', toggle=True, text='',emboss=False,
                                icon='DOWNARROW_HLT' if self.postfx_expand else 'RIGHTARROW')
                post_effects_panel.post_effects_header(context,header_row,True)
                header_row.label(text='Post FX')
                header_row.separator()
                camera_presets.PHOTOGRAPHER_PT_LensEffectsPresets.draw_panel_header(header_row)
                if self.postfx_expand:
                    col = box.column()
                    post_effects_panel.post_effects_draw(context,col,True)               

        if (self.tab == 'RENDER' or not prefs.menu_multi_tab) and scene.camera:
            rme = prefs.resolution_menu_enable
            if scene.camera is not None and scene.camera.type == 'CAMERA' and rme:
                box = menu.box()
                from .resolution_panel import resolution_header_preset, resolution_header, resolution_panel, resize_canvas_panel
                header_row = box.row(align=True)
                header_row.prop(self, 'resolution_expand', toggle=True, text='',emboss=False,
                                icon='DOWNARROW_HLT' if self.resolution_expand else 'RIGHTARROW')
                resolution_header(context,header_row,True,True)
                resolution_header_preset(context,header_row)
                header_row.separator()
                camera_presets.PHOTOGRAPHER_PT_ResolutionPresets.draw_panel_header(header_row)
                if self.resolution_expand:
                    col = box.column()
                    resolution_panel(context,settings,col)

                    resize_canvas_box=box.box()
                    header_row = resize_canvas_box.row(align=True)
                    header_row.prop(self, 'resize_canvas_expand', toggle=True, text='',emboss=False,
                                    icon='DOWNARROW_HLT' if self.resize_canvas_expand else 'RIGHTARROW')
                    header_row.label(text='Resize Canvas (Experimental)')
                    if self.resize_canvas_expand:
                        col = resize_canvas_box.column(align=True)
                        resize_canvas_panel(context,col,True)

            vlme = prefs.viewlayer_menu_enable
            if scene.camera is not None and scene.camera.type == 'CAMERA' and vlme:
                box = menu.box()
                header_row = box.row(align=True)
                header_row.prop(self, 'viewlayer_expand', toggle=True, text='',emboss=False,
                                icon='DOWNARROW_HLT' if self.viewlayer_expand else 'RIGHTARROW')
                header_row.prop(settings, "view_layer_enabled", text="View Layers")
                sub = header_row.row(align=True)
                sub.enabled = settings.view_layer_enabled
                sub.prop(settings,"active_view_layer",text="")

                if self.viewlayer_expand:
                    from ..view_layer import draw_view_layer_panel
                    draw_view_layer_panel(context,box,use_scene_camera=True)

            col = menu.column(align=True)
            from ..render_queue import render_buttons
            render_buttons(self,context,col)

    def execute(self, context):
        prefs = context.preferences.addons[base_package].preferences
        if prefs.menu_store_ui:
            # Store last menu state
            for p in property_names:
                globals_dict[p] = getattr(self, p) 
            
        context.scene.photographer.is_sticky_menu_open = False
        return {'FINISHED'}
        
    def cancel(self,context):
        prefs = context.preferences.addons[base_package].preferences
        if prefs.menu_store_ui:
            # Store last menu state
            for p in property_names:
                globals_dict[p] = getattr(self, p)
    
    def invoke(self, context, event):
        prefs = context.preferences.addons[base_package].preferences
        if prefs.menu_store_ui:
            print(globals_dict)
            for p in property_names:
                if globals_dict.get(p,None):
                    setattr(self,p,globals_dict[p])
                    
        context.scene.photographer.is_sticky_menu_open = True

        return context.window_manager.invoke_props_dialog(self,width=300)
        