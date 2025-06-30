import bpy, os, platform, sys, ast, subprocess

def update_all_tab_names(self, context):
    try:
        from . import auto_rig
        auto_rig.update_arp_tab()
    except:
        pass
    
    try:
        from . import auto_rig_ge
        auto_rig_ge.update_arp_tab()
    except:
        pass
        
    try:
        from . import auto_rig_smart
        auto_rig_smart.update_arp_tab()
    except:
        pass
      
    try:
        from . import auto_rig_remap
        auto_rig_remap.update_arp_tab()
    except:
        pass
        
    try:
        from . import rig_functions
        rig_functions.update_arp_tab()
    except:
        pass
        
        
def get_documents_path(other_folder):
    home = os.path.expanduser("~")  # get the user documents path
    documents = os.path.join(home, "Documents")
    p = os.path.join(documents, 'AutoRigPro')
    p = os.path.join(p, other_folder)
    
    return p
    
    
def get_prefs():
    if bpy.app.version >= (4,2,0):
        return bpy.context.preferences.addons[__package__[:-4]].preferences
    else:
        return bpy.context.preferences.addons[__package__.split('.')[0]].preferences
        
        
class ARP_OT_save_prefs(bpy.types.Operator):
    """Save addon preferences to file, to preserve them when installing a new version"""

    bl_idname = 'arp.prefs_save'
    bl_label = 'Save ARP prefs'
    
    def execute(self, context):
        scn = bpy.context.scene
        fp = os.path.abspath(__file__)#get_prefs().prefs_presets_path
        fp = os.path.dirname(fp)
        fp = os.path.dirname(fp)
        fp = os.path.dirname(fp)#Blender addons folder
        #print(fp)
        
        if not (fp.endswith("\\") or fp.endswith('/')):
            fp += '/'
        
        fp = fp+'autorigpro.prefs'
        fp = os.path.abspath(fp)# automatically adds the driver letter if the path does not contain any
        #print(fp)
        if not os.path.exists(os.path.dirname(fp)):
            try:
                os.makedirs(os.path.dirname(fp))
            except:
                pass
        file = open(fp, 'w', encoding='utf8', newline='\n')
        
        prefs_settings = {   
            'arp_tab_name':get_prefs().arp_tab_name,
            'arp_tools_tab_name':get_prefs().arp_tools_tab_name,
            'beginner_mode': get_prefs().beginner_mode,
            'custom_armatures_path': get_prefs().custom_armatures_path,
            'custom_limb_path': get_prefs().custom_limb_path,
            'rig_layers_path': get_prefs().rig_layers_path,
            'remap_presets_path': get_prefs().remap_presets_path,
            'ge_presets_path': get_prefs().ge_presets_path,
            #'prefs_presets_path': get_prefs().prefs_presets_path,
            'default_ikfk_arm':get_prefs().default_ikfk_arm,
            'default_ikfk_leg': get_prefs().default_ikfk_leg,
            'default_head_lock': get_prefs().default_head_lock,
            'remove_existing_arm_mods': get_prefs().remove_existing_arm_mods,
            'remove_existing_vgroups': get_prefs().remove_existing_vgroups,
            'show_export_popup': get_prefs().show_export_popup,
            'arp_debug_mode': scn.arp_debug_mode,
            'arp_debug_bind': scn.arp_debug_bind,
            'arp_experimental_mode': scn.arp_experimental_mode,
            'arp_disable_smart_fx': scn.arp_disable_smart_fx,
            }
        
        
        file.write(str(prefs_settings))
        file.close()
        print("Auto-Rig Pro preferences saved successfully!")
        print(fp)
        
        return {'FINISHED'}
        
        
def get_downloads_folder():
    """Get the default downloads folder path based on the operating system."""
    system = platform.system().lower()
    home = os.path.expanduser("~")  # Gets the user's home directory
    downloads = os.path.join(home, "Downloads")
    
    # Ensure the path exists (optional, remove if you just want the path)
    if not os.path.exists(downloads):
        os.makedirs(downloads, exist_ok=True)

    return downloads
        
        
def extract_zip(source_zip, destination_folder):
    import zipfile, stat
                                                       
    os.makedirs(destination_folder, exist_ok=True)

    print("Unzip...")
    
    # Use unzip process instead of zipfile for better fidelity on Linux and Mac
    if platform.system() in ["Darwin", "Linux"]:
        if platform.system() == "Darwin":
            result = subprocess.run(['xattr', source_zip], capture_output=True, text=True)            
            if 'com.apple.quarantine' in result.stdout:
                subprocess.run(['xattr', '-d', 'com.apple.quarantine', source_zip], check=True)

        result = subprocess.run(["unzip", "-o", source_zip, "-d", destination_folder], capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"unzip failed: {result.stderr}")
        print(f"unzip output: {result.stdout}")
    else:
        # Fallback to zipfile for other platforms
        with zipfile.ZipFile(source_zip, 'r') as zip_ref:
            zip_ref.extractall(destination_folder)
        
    return True, f"Successfully extracted {source_zip} to {destination_folder}"
    
        
class ARP_OT_install_ext(bpy.types.Operator):
    """Install external dependencies"""

    bl_idname = 'arp.install_ext'
    bl_label = 'Install Files'
    
    filepath: bpy.props.StringProperty(subtype='FILE_PATH', default='name')
    filename_ext = '.zip'
    
    def invoke(self, context, event):
        self.filepath = downloads_path = get_downloads_folder()
        context.window_manager.fileselect_add(self)        
        
        return {'RUNNING_MODAL'}
        
    def execute(self, context):
        if not self.filepath.endswith('.zip'):
            self.report({'ERROR'}, 'Select the zip file to install')
            return {'FINISHED'}        
        print("Extract zip...")
        extract_zip(self.filepath, get_prefs().ai_presets_path)
    
        return {'FINISHED'}
   

class ARP_MT_arp_addon_preferences(bpy.types.AddonPreferences):
    bl_idname = __package__[:-4] if bpy.app.version >= (4,2,0) else __package__.split('.')[0]
    arp_tab_name : bpy.props.StringProperty(name='Interface Tab', description='Name of the tab to display the interface in', default='ARP', update=update_all_tab_names)
    arp_tools_tab_name : bpy.props.StringProperty(name='Tools Interface Tab', description='Name of the tab to display the tools (IK-FK snap...) interface in', default='Tool', update=update_all_tab_names)
    
    beginner_mode: bpy.props.BoolProperty(name='Beginner Mode', default=True)
    custom_armatures_path: bpy.props.StringProperty(name='Armatures', subtype='FILE_PATH', default=get_documents_path('Armatures Presets'), description='Path to store armature presets')
    custom_limb_path: bpy.props.StringProperty(name='Limbs', subtype='FILE_PATH', default=get_documents_path('Custom Limbs'), description='Path to store custom limb presets')
    rig_layers_path: bpy.props.StringProperty(name='Rig Layers', subtype='FILE_PATH', default=get_documents_path('Rig Layers'), description='Path to store rig layers presets')
    remap_presets_path: bpy.props.StringProperty(name='Remap Presets', subtype='FILE_PATH', default=get_documents_path('Remap Presets'), description='Path to store remap presets')
    ge_presets_path: bpy.props.StringProperty(name='Export Presets', subtype='FILE_PATH', default=get_documents_path('Game Engine Presets'), description='Path to store game engine export presets')
    ai_presets_path: bpy.props.StringProperty(name='AI', subtype='FILE_PATH', default=get_documents_path('AI'), description='Path to store AI executables')
    
    parent_bound_objects: bpy.props.BoolProperty(default=True, description='Parent the objects to the armature when binding.\nTurning it off *is not recommended* as it can lead to issues, but it may be useful for some custom workflows')
    default_ikfk_arm: bpy.props.EnumProperty(items=(('IK', 'IK', 'IK'), ('FK', 'FK', 'FK')), description='Default value for arms IK-FK switch', name='IK-FK Arms Default')
    default_ikfk_leg: bpy.props.EnumProperty(items=(('IK', 'IK', 'IK'), ('FK', 'FK', 'FK')), description='Default value for legs IK-FK switch', name='IK-FK Legs Default')
    default_head_lock: bpy.props.BoolProperty(default=True, name='Head Lock Default', description='Default value for the Head Lock switch')
    remove_existing_arm_mods: bpy.props.BoolProperty(default=True, name='Remove Armature Modifiers', description='Remove existing armature modifiers when binding')
    remove_existing_vgroups: bpy.props.BoolProperty(default=True, name='Remove Existing Vertex Groups', description='Remove existing vertex groups when binding')
    rem_arm_mods_set: bpy.props.BoolProperty(default=False, description='Toggle to be executed the first time binding, to set default prefs')
    rem_vgroups_set: bpy.props.BoolProperty(default=False, description='Toggle to be executed the first time binding, to set default prefs')
    show_export_popup: bpy.props.BoolProperty(default=True, description='Show a popup notification on export completion')
    
    
    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.operator(ARP_OT_save_prefs.bl_idname, text='Save Preferences')
        
        def show_rig_ui(panel):
            if panel:
                col = panel.column(align=True)
            else:
                col = layout.column(align=True)
                col.label(text='Rig:')   
            col.prop(self, 'parent_bound_objects', text='Parent Objects when Binding')
            col.prop(self, 'remove_existing_arm_mods', text='Remove Existing Armature Modifiers when Binding')
            col.prop(self, 'remove_existing_vgroups', text='Remove Existing Vertex Groups when Binding')
            col.separator()
            col.prop(self, 'default_ikfk_arm', text='IK-FK Arms')
            col.prop(self, 'default_ikfk_leg', text='IK-FK Legs')
            col.prop(self, 'default_head_lock', text='Head Lock')
            col.separator()
            
        if bpy.app.version >= (4,1,0):
            header_rig, panel_rig = layout.panel("arp_pref_ui_rig", default_closed=False)
            header_rig.label(text="Rig")
            if panel_rig:# None if collapsed
                show_rig_ui(panel_rig) 
        else:
            show_rig_ui(None)
        
        def show_interface_ui(panel):
            if panel:
                col = panel.column(align=True)
            else:
                col = layout.column(align=True)
                col.label(text='Interface:')
            row = col.row(align=True)
            row.prop(self, 'beginner_mode', text='Beginner Mode (help buttons)')
            col.separator()
            col.prop(self, 'arp_tab_name', text='Main ARP Tab')
            col.prop(self, 'arp_tools_tab_name', text='Tools Tab')
            col.prop(self, 'show_export_popup', text='Show Popup when Export Finished')
            col.separator()
            
        if bpy.app.version >= (4,1,0):
            header_interface, panel_interface = layout.panel("arp_pref_ui_interface", default_closed=False)
            header_interface.label(text="Interface")
            if panel_interface:# None if collapsed
                show_interface_ui(panel_interface) 
        else:
            show_interface_ui(None)
            
        def show_paths_ui(panel):
            if panel:
                col = panel.column(align=True)
            else:
                col = layout.column(align=True)
                col.label(text='Paths:')
            col.prop(self, 'custom_armatures_path')
            col.prop(self, 'custom_limb_path')
            col.prop(self, 'rig_layers_path')
            col.prop(self, 'remap_presets_path')
            col.prop(self, 'ge_presets_path')
            col.prop(self, 'ai_presets_path')
            col.operator('arp.install_ext', text='Install AI files...')
            col.separator()
            
        if bpy.app.version >= (4,1,0):
            header_paths, panel_paths = layout.panel("arp_pref_ui_paths", default_closed=False)
            header_paths.label(text="Paths")
            if panel_paths:# None if collapsed
                show_paths_ui(panel_paths) 
        else:
            show_paths_ui(None)
            
        def show_debug_ui(panel):
            if panel:
                col = panel.column()
            else:
                col = layout.column(align=True)
                col.label(text='Debug:')
            col.label(text='Special-Debug:', icon='ERROR')
            col.prop(context.scene, 'arp_disable_smart_fx')
            col.prop(context.scene, 'arp_debug_mode')
            col.prop(context.scene, 'arp_debug_bind')
            col.prop(context.scene, 'arp_experimental_mode')
            
        if bpy.app.version >= (4,1,0):
            header_debug, panel_debug = layout.panel("arp_pref_ui_debug", default_closed=True)
            header_debug.label(text="Debug")
            if panel_debug:# None if collapsed
                show_debug_ui(panel_debug) 
        else:
            show_debug_ui(None)
        

def load_arp_prefs():

    fp = os.path.abspath(__file__)#get_prefs().prefs_presets_path
    fp = os.path.dirname(fp)
    fp = os.path.dirname(fp)
    fp = os.path.dirname(fp)#Blender addons folder
    #print(fp)
    
    if not (fp.endswith("\\") or fp.endswith('/')):
        fp += '/'
    
    fp = fp+'autorigpro.prefs'
    fp = os.path.abspath(fp)# automatically adds the driver letter if the path does not contain any
    #print(fp)
    if not os.path.exists(os.path.dirname(fp)):
        print("Auto-Rig Pro preferences are not saved yet")
        return
        
    file = None
    settings = None
    try:
        file = open(fp, 'r') if sys.version_info >= (3, 11) else open(fp, 'rU')
        file_lines = file.readlines()
        settings= str(file_lines[0])
    except:
        print("Cannot read ARP prefs")
        return        
    
    settings_dict = ast.literal_eval(settings)
    
    for setting in settings_dict:
        setattr(get_prefs(), setting, settings_dict[setting])
        #print('Loaded setting', setting)
    file.close()
    
    print('Auto-Rig Pro preferences loaded successfully!')
    
        
    
def register():
    from bpy.utils import register_class

    try:
        register_class(ARP_MT_arp_addon_preferences)
        register_class(ARP_OT_save_prefs)
        register_class(ARP_OT_install_ext)
    except:
        pass
        
    # load exported prefs on addon startup
    load_arp_prefs()   
    
    bpy.types.Scene.arp_debug_mode = bpy.props.BoolProperty(name='Debug Mode', default=False, description = 'Run the addon in debug mode for debugging purposes.\nWarning, can generate earthquakes and solar tempest. Do not enable for normal usage!', options={'HIDDEN'})
    bpy.types.Scene.arp_debug_bind = bpy.props.BoolProperty(name='Debug Bind', default=False, description='Enable Debug mode for bind functions, for debugging purposes.\nWarning, will break tools and generate earthquakes!\nDo not enable for normal usage!', options={'HIDDEN'})
    bpy.types.Scene.arp_experimental_mode = bpy.props.BoolProperty(name='Experimental Mode', default=False, description = 'Enable experimental, unstable tools. Warning, can lead to errors. Use it at your own risks.', options={'HIDDEN'})
    bpy.types.Scene.arp_disable_smart_fx = bpy.props.BoolProperty(name='Disable Smart FX', default=False, description='Disable Smart markers FX for debug purposes, such as Mac systems not supporting some graphics. Safe to use.', options={'HIDDEN'})
    

def unregister():
    from bpy.utils import unregister_class
    unregister_class(ARP_MT_arp_addon_preferences)

    del bpy.types.Scene.arp_debug_mode
    del bpy.types.Scene.arp_debug_bind
    del bpy.types.Scene.arp_experimental_mode
    del bpy.types.Scene.arp_disable_smart_fx
