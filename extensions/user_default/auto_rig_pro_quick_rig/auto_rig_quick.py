import bpy, sys, linecache, ast, os, time, math, difflib
from mathutils import Vector, Euler, Matrix
from bpy.types import Panel, UIList, Operator, Menu
from bpy.props import BoolProperty, FloatProperty, StringProperty, IntProperty, EnumProperty, FloatVectorProperty
from .utils import *
import addon_utils
import requests, webbrowser# check for updates online

# CLASSES
#############################################################################
class ARP_OT_quick_limbs_move(Operator):
    """Move entry"""
    bl_idname = "arp.quick_limbs_move"
    bl_label = "Quick Limbs Move"
    bl_options = {'UNDO'}   
  
    direction: StringProperty(default="UP")
    
    def execute(self, context):        
        try:   
            scn = bpy.context.scene
            fac = -1
            if self.direction == 'DOWN':
                fac = 1
                
            target_idx = scn.limb_map_index + fac
            if target_idx < 0:
                target_idx = len(scn.limb_map)-1
            if target_idx > len(scn.limb_map)-1:
                target_idx = 0

            scn.limb_map.move(scn.limb_map_index, target_idx)
            scn.limb_map_index = target_idx
            
        except:
            pass
        return {'FINISHED'}
        
        
class ARP_OT_quick_check_for_update(Operator):
    """Check if a new Quick Rig version has been released"""
    
    bl_idname = "arp.quick_check_for_update"
    bl_label = "Check for Update"        
    
    current_version = 0
    latest_version = 0
    current_version_digits = ''
    message = ''
    same_major_version = False
    new_log_diff = []
    fixed_log_diff = []
    new_log_diff_brk = {}
    fixed_log_diff_brk = {}
    
    def invoke(self, context, event): 
        self.same_major_version = False
        self.new_log_diff = []
        self.fixed_log_diff = []
        new_log_diff_brk = {}
        fixed_log_diff_brk = {}
        link = "https://blendermarket.com/products/auto-rig-pro-quick-rig"
        req = requests.get(link, verify=False, timeout=5)
        f = req.text
        char1 = '--['
        char2 = ']--'
        ver_string = f[f.find(char1)+3 : f.find(char2)]
        if ver_string == '':
            self.message = 'Failed to check, is there an internet connection?'
        else:
            ver_list = ver_string.split('.')
            ver_int = int(ver_list[0] + ver_list[1] + ver_list[2])
            self.latest_version = ver_int        
            self.current_version = get_quickrig_version()
            str_current = str(self.current_version)
            self.current_version_digits = str_current[0]+'.'+str_current[1]+str_current[2]+'.'+str_current[3]+str_current[4]
            if self.current_version < self.latest_version:
                latest_ver_string = ver_int_to_str(self.latest_version)                
                self.message = '* New version available! * ' + latest_ver_string
            else:
                #print('ver_string', ver_string)           
                self.message = 'Already up to date! ['+self.current_version_digits+'] Keep on riggin\''
                
            
            # get first three digits of the version
            if str(self.latest_version)[:3] == str(self.current_version)[:3]:
                self.same_major_version = True            
            
            # evaluate log diff
            version_seq = '<b>--['+ver_string+']--</b>'
            ver_split = f.split(version_seq)
            ul_op_split = ver_split[1].split('<ul>')
            ul_split = ul_op_split[1].split('</ul>')
            li_split = ul_split[0].split('<li>')
            
            # get new log
            #print('')
            #print('New/Improved:')
            new_log = []
            for li in li_split:
                logline = li.replace('</li>', '')
                logline = logline.strip()
                if logline != '':
                    # remove '- ' at the start
                    if logline.startswith('-'):
                        logline = logline[1:]
                    if logline.startswith(' '):
                        logline = logline[1:]
                    while logline.endswith('<br>'):
                        logline = logline[:-4]
                    new_log.append(logline)
                
            fixed_seq = '<p><strong>Fixed:</strong></p>'
            fixed_split = ver_split[1].split(fixed_seq)
            ul_op_split = fixed_split[1].split('<ul>')
            ul_split = ul_op_split[1].split('</ul>')
            li_split = ul_split[0].split('<li>')

            fixed_log = []
            for li in li_split:
                logline = li.replace('</li>', '')
                logline = logline.strip()
                if logline != '':
                    # remove '- ' at the start
                    if logline.startswith('-'):
                        logline = logline[1:]
                    if logline.startswith(' '):
                        logline = logline[1:]
                    while logline.endswith('<br>'):                       
                        logline = logline[:-4]                     
                    
                    fixed_log.append(logline)
            
            # get current log
            current_new_log = []
            current_fixed_log = []
            addon_directory = os.path.dirname(os.path.abspath(__file__))      
            log_path = os.path.join(addon_directory, '00_LOG.txt')
            print('log_path', log_path)
            if os.path.exists(log_path) and self.same_major_version:
                log_file = open(log_path, 'r') if sys.version_info >= (3, 11) else open(log_path, 'rU').readlines()
                register_new_log = False
                register_fixed_log = False
                
                for line in log_file:
                    if line.startswith('New/improved:'):
                        register_new_log = True
                        continue
                    if line.startswith('Fixed:'):
                        register_fixed_log = True
                        continue                        
                    if register_new_log:
                        valid_line = False
                        if len(line) and not line.startswith(' '):
                            line = line.strip()
                            # remove '- ' at the start
                            if line.startswith('-'):
                                line = line[1:]
                            if line.startswith(' '):
                                line = line[1:]
                            if len(line):
                                current_new_log.append(line)                            
                                valid_line = True
                        
                        if valid_line:
                            continue
                        else:
                            register_new_log = False
                            continue   
                            
                    if register_fixed_log:
                        valid_line = False
                        if len(line) and not line.startswith(' '):
                            line = line.strip()
                            # remove '- ' at the start
                            if line.startswith('-'):
                                line = line[1:]
                            if line.startswith(' '):
                                line = line[1:]
                            if len(line):
                                current_fixed_log.append(line)
                                valid_line = True
                        
                        if valid_line:
                            continue
                        else:
                            register_fixed_log = False
                            continue
            else:
                print('Missing log file, or major new version available')               
            
            '''
            print('current_new_log')
            for i in current_new_log:
                print('start', i)
            
            print('')
            print('new_log')
            for i in new_log:
                print('start', i)
            '''
            
            for i in new_log:
                if not i in current_new_log:                  
                    self.new_log_diff.append('- '+i)
            
            for i in fixed_log:
                if not i in current_fixed_log:
                    self.fixed_log_diff.append('- '+i)      
            
            # format with line breaks to fit windows size wrap
            for idx, i in enumerate(self.new_log_diff):
                indexes = [100, 200, 300]
                substring_list = []
                start_index = 0
                for index in indexes:
                    while index < len(i) and i[index] != ' ':
                        index += 1
                    substring = i[start_index:index]
                    substring_list.append(substring)
                    start_index = index + 1
                substring_list.append(i[start_index:])
                
                # clear blank entries breaks
                for j in reversed(substring_list):
                    if j == '':
                        substring_list.pop(substring_list.index(j))
                        
                self.new_log_diff_brk[idx] = substring_list
              
                    
            for idx, i in enumerate(self.fixed_log_diff):
                indexes = [100, 200, 300]
                substring_list = []
                start_index = 0
                for index in indexes:
                    while index < len(i) and i[index] != ' ':
                        index += 1
                    substring = i[start_index:index]
                    substring_list.append(substring)
                    start_index = index + 1
                substring_list.append(i[start_index:])
                
                # clear blank entries breaks
                for j in reversed(substring_list):
                    if j == '':
                        substring_list.pop(substring_list.index(j))
                        
                self.fixed_log_diff_brk[idx] = substring_list
            
            
        # show window
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=600)
        

    def draw(self, context):
        layout = self.layout
        layout.label(text=self.message)       
        layout.separator()
        
        # show log diff if same version digit        
        if len(self.new_log_diff) or len(self.fixed_log_diff):
            add_text = '' if self.same_major_version else ' (include '+str(self.latest_version)[0]+'.'+str(self.latest_version)[:3][-2:] +' log only)'
            layout.label(text='Changes since current version '+self.current_version_digits+add_text)
            layout.separator()
            if len(self.new_log_diff):
                layout.label(text='[New/Improved]:', icon='KEYTYPE_JITTER_VEC')
                for i in self.new_log_diff_brk:
                    for line in self.new_log_diff_brk[i]:                    
                        layout.label(text=line)
            if len(self.fixed_log_diff):
                layout.separator()
                layout.label(text='[Fixed]:', icon='KEYTYPE_JITTER_VEC')
                for i in self.fixed_log_diff_brk:
                    for line in self.fixed_log_diff_brk[i]:                    
                        layout.label(text=line)
            layout.separator()
                
        #layout.operator('arp.open_update_log', text='See Latest Official Release Log', icon='WORLD')
        layout.separator()

    def execute(self, context): 
        return {'FINISHED'}
        
        
class ARP_MT_quick_export(Menu):
    bl_label = "Export as custom preset"

    def draw(self, _context):
        layout = self.layout
        layout.operator("arp.quick_export_preset", text="Save as New Preset")


class ARP_OT_quick_export_preset(Operator):
    """Export as custom preset"""

    bl_idname = "arp.quick_export_preset"
    bl_label = "Export Preset"

    preset_name: StringProperty(default='CoolPreset')

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)


    def draw(self, context):
        layout = self.layout
        layout.prop(self, "preset_name", text="Preset Name")


    def execute(self, context):
        # get filepath
        custom_dir = get_prefs().custom_presets_path
        
        if not (custom_dir.endswith("\\") or custom_dir.endswith('/')):
            custom_dir += '/'

        filepath = custom_dir+self.preset_name+'.py'
        if not os.path.exists(os.path.dirname(filepath)):
            try:
                os.makedirs(os.path.dirname(filepath))
            except:
                pass

        # export
        _export_mapping(filepath)

        # update list
        update_quick_presets()

        return {'FINISHED'}


class ARP_MT_quick_import(Menu):
    bl_label = "Import built-in presets list"

    custom_presets = []

    def draw(self, _context):
        layout = self.layout
        presets_dict = {"Advanced Skeleton":"advanced_skeleton",
                        "Character Creator":"CC",
                        "Character Creator +":"CC+",
                        "Character Creator Accurig":"CC_Accurig",
                        "DAZ (Genesis 3, 8, 8.1)": "DAZ",
                        "DAZ (Genesis 9)": "DAZ_genesis_9",
                        "DAZ (Genesis 9 v2)": "DAZ_genesis_9_v2",
                        "DAZ (Other #1)": "DAZ_genesis_01",
                        "DAZ (Other #2)": "DAZ_genesis_02",
                        "Human Generator": "human_generator",
                        "Human Generator V2": "human_generator_v2",
                        "MB Lab":"MB_LAB",
                        "Mixamo":"mixamo",
                        "Mixamo (Old)": "mixamo_old",
                        "UE4 Mannequin": "UE_mannequin",
                        "UE4 Mannequin (Automatic Orientations)": "UE_mannequin_automatic",
                        "UE5 Manny": "UE5_manny",
                        "UE5 Manny (2 Twists, for UE export)":"UE5_manny_2_twists",
                        "UE MetaHuman":"UE_MetaHuman",
                        "VRoid":"VRoid",
                        "VRoid (CATS fixed)":"VRoid_cats"}
        
        for pname in presets_dict:
            op = layout.operator("arp.quick_import_preset", text=pname)
            op.preset_name = presets_dict[pname]

        if len(self.custom_presets):
            layout.label(text='__________')
        for cp in self.custom_presets:
            op = layout.operator("arp.quick_import_preset", text=cp.title()).preset_name = 'CUSTOM_'+cp


class ARP_OT_quick_import_preset(Operator):
    """ Import the selected preset """

    bl_idname = "arp.quick_import_preset"
    bl_label = "Import Preset"

    preset_name: StringProperty(default="")
    clear: BoolProperty(default=True, description="Clear existing limbs mapping before importing the preset")
    filepath: StringProperty(subtype="FILE_PATH", default='py')
    fuzzy_match: BoolProperty(default=False, description="Approximate names match, if the preset does not match the exact names of the bones\nWarning, can be wrong!")

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if obj:
            return obj.type == "ARMATURE"
        return False


    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)


    def draw(self, context):
        layout = self.layout
        layout.prop(self, "clear", text="Clear Current Limbs")
        layout.prop(self, "fuzzy_match", text="Fuzzy Match")

    def execute(self, context):
        print("IMPORT PRESET")
        scn = bpy.context.scene
        try:
            scn.arp_quick_hold_update = True

            if self.clear:
                for i in range(0, len(scn.limb_map)):
                    _remove_limb()

            # custom presets
            if self.preset_name.startswith('CUSTOM_'):
                custom_dir = bpy.context.preferences.addons[__package__].preferences.custom_presets_path
                if not (custom_dir.endswith("\\") or custom_dir.endswith('/')):
                    custom_dir += '/'

                try:
                    os.listdir(custom_dir)
                except:
                    self.report({'ERROR'}, 'The custom presets directory seems invalid: '+custom_dir+'\nCheck the path in the addon preferences')
                    return

                self.filepath = custom_dir + self.preset_name[7:]+'.py'

            # built-in presets
            else:
                addon_directory = os.path.dirname(os.path.abspath(__file__))
                self.filepath = addon_directory + '/presets/'+self.preset_name+'.py'
            
            import_success = _import_mapping(self)
            print("import_success", import_success)
            if import_success == False and self.fuzzy_match == False:
                bpy.ops.arp.reimport_fuzzy('INVOKE_DEFAULT', preset_name=self.preset_name, clear=self.clear, filepath=self.filepath)

        finally:
            scn.arp_quick_hold_update = False

        return {'FINISHED'}
        
        
class ARP_OT_reimport_preset_fuzzy(Operator):
    """Import with fuzzy names match"""    
    bl_idname = 'arp.reimport_fuzzy'
    bl_label = ''

    preset_name: StringProperty(default="")
    clear: BoolProperty(default=True, description="Clear existing limbs mapping before importing the preset")
    filepath: StringProperty(subtype="FILE_PATH", default='py')

    def draw(self, context):
        layout = self.layout
        layout.label(text="", icon='ERROR')   
        layout.label(text="Bone names stored in this preset don't match the bones of this skeleton!")   
        layout.label(text='Try to import again with approximate names matching (fuzzy match)?')
        layout.label(text='Warning, prone to error.')
        
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)   

    def execute(self, context):
        print("REIMPORT", self.preset_name, self.filepath)
        bpy.ops.arp.quick_import_preset('EXEC_DEFAULT',preset_name=self.preset_name, clear=self.clear, filepath=self.filepath, fuzzy_match=True)        
        return {"FINISHED"}


class ARP_OT_quick_report_message(Operator):
    """ Report a message in a popup window"""

    bl_label = 'Report Message'
    bl_idname = "arp.quick_report_message"

    message = ""
    icon_type = 'INFO'

    def draw(self, context):
        layout = self.layout
        split_message = self.message.split('\n')

        for i, line in enumerate(split_message):
            if i == 0:
                layout.label(text=line, icon=self.icon_type)
            else:
                layout.label(text=line)

    def execute(self, context):
        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)


def update_limb_name(self, context):
    scn = context.scene

    # skip name update on certain cases e.g. import preset
    if scn.arp_quick_hold_update:
        return

    selected_limb = scn.limb_map[scn.limb_map_index]
    limb_type = scn.limb_map[scn.limb_map_index].type

    dupli_count = 0
    limb_map_len = None

    # workaround for recursion depth error due to the function being called recursively when changing side/type
    try:
        limb_map_len = len(scn.limb_map)
        for i in range(0, limb_map_len):
            foo = 1
    except:
        return

    # evaluate number of duplicated limbs if any
    for i in range(0, limb_map_len):
        if i == scn.limb_map_index:
            break
        limb = scn.limb_map[i]
        if limb.type == limb_type and selected_limb.side == limb.side:
            dupli_count += 1

    # always set head and spine limb to center side for now
    try:# recursion depth error due to the function being called recursively when changing side/type
        if limb_type == "HEAD" or limb_type == "SPINE":
            if selected_limb.side != "CENTER":
                selected_limb.side = "CENTER"
    except:
        pass

    try:# recursion depth error due to the function being called recursively when changing side/type
        if limb_type == "LEG" or limb_type == "ARM":
            if selected_limb.side == "CENTER":
                selected_limb.side = "LEFT"
    except:
        pass

    _side = ".l"
    if selected_limb.side == "RIGHT":
        _side = ".r"
    elif selected_limb.side == "CENTER":
        _side = ".x"

    # multi limb support
    dupli_idx = ""
    if dupli_count > 0:
        dupli_idx = '{:03d}'.format(dupli_count)
        dupli_idx = "_dupli_"+str(dupli_idx)

    if selected_limb.name != limb_type.title() + dupli_idx + _side:# only set if necessary to avoid update recursion errors
        selected_limb.name = limb_type.title() + dupli_idx + _side


class LimbProp(bpy.types.PropertyGroup):
    name: StringProperty(default="", description="Limb Name")
    type: bpy.props.EnumProperty(items=(
        ('LEG', 'Leg', 'Leg type'), ('ARM', 'Arm', 'Arm type'), 
        ('SPINE', 'Spine', 'Spine type'), ('HEAD', 'Head', 'Head type'), ('TAIL', 'Tail', 'Tail type')), 
        name="Limb Type", description="Type of the limb", update=update_limb_name)
    side: bpy.props.EnumProperty(items=(('LEFT', 'Left', 'Left side'), ('RIGHT', 'Right', 'Right side'), ('CENTER', 'Center', 'Center side')), name="Limb Side", description="Side of the limb", update=update_limb_name)
    bone_01: StringProperty(default="", name="Bone1", description="")
    bone_02: StringProperty(default="", name="Bone2", description="")
    bone_03: StringProperty(default="", name="Bone3", description="")
    bone_04: StringProperty(default="", name="Bone4", description="")
    bone_05: StringProperty(default="", name="Bone5", description="")
    bone_06: StringProperty(default="", name="Bone6", description="")
    bone_07: StringProperty(default="", name="Bone7", description="")

    bone_twist_02_01: StringProperty(default="", name="Bone Twist 02 01", description="")
    bone_twist_02_02: StringProperty(default="", name="Bone Twist 02 02", description="")
    bone_twist_03_01: StringProperty(default="", name="Bone Twist 03 01", description="")
    bone_twist_03_02: StringProperty(default="", name="Bone Twist 03 02", description="")
    bone_twist_04_01: StringProperty(default="", name="Bone Twist 04 01", description="")
    bone_twist_04_02: StringProperty(default="", name="Bone Twist 04 02", description="")
    bone_twist_05_01: StringProperty(default="", name="Bone Twist 05 01", description="")
    bone_twist_05_02: StringProperty(default="", name="Bone Twist 05 02", description="")
    bone_twist_06_01: StringProperty(default="", name="Bone Twist 06 01", description="")
    bone_twist_06_02: StringProperty(default="", name="Bone Twist 06 02", description="")
    bone_twist_07_01: StringProperty(default="", name="Bone Twist 07 01", description="")
    bone_twist_07_02: StringProperty(default="", name="Bone Twist 07 02", description="")
    twist_bones_amount: IntProperty(default=1, min=0, max=7, description="Numbers of twist bones per sub-limb")

    neck_bones_amount: IntProperty(default=2, min=1, max=10, description="Numbers of neck bones")
    neck3: StringProperty(default="", name="Neck3", description="")
    neck4: StringProperty(default="", name="Neck4", description="")
    neck5: StringProperty(default="", name="Neck5", description="")
    neck6: StringProperty(default="", name="Neck6", description="")
    neck7: StringProperty(default="", name="Neck7", description="")
    neck8: StringProperty(default="", name="Neck8", description="")
    neck9: StringProperty(default="", name="Neck9", description="")
    neck10: StringProperty(default="", name="Neck10", description="")

    fingers: bpy.props.EnumProperty(items=(('NONE', 'None', 'None'), ('3', '3 Bones (No Metacarps)', '3 Bones per finger, without metacarps'), ('4', '4 Bones (With Metacarps)', '4 Bones per finger, including metacarps')), description="Fingers setup", name="Fingers")

    up_axis: bpy.props.EnumProperty(items=(('X', 'X', 'X is pointing up'), ('-X', '-X', '-X is pointing up'), 
                                        ('Y', 'Y', 'Y is pointing up'), ('-Y', '-Y', '-Y is pointing up'), 
                                        ('Z', 'Z', 'Z is pointing up'), ('-Z', '-Z', '-Z is pointing up')), description="Bone axis pointing up", name="Up Axis")
    up_axis_arm: bpy.props.EnumProperty(items=(('DEFAULT', 'Do not Align', 'No alignment, leave to default positioning'), ('X', 'X', 'X is pointing up'), ('-X', '-X', '-X is pointing up'), ('Y', 'Y', 'Y is pointing up'), ('-Y', '-Y', '-Y is pointing up'), ('Z', 'Z', 'Z is pointing up'), ('-Z', '-Z', '-Z is pointing up')), description="Bone axis pointing up", name="Up Axis")
    force_up_axis: BoolProperty(name="Force Up Axis", default=True, description="Force Auto-Rig Pro foot Z axis upward (recommended for typical humanoid characters facing the Y axis)")
    foot_dir_axis: EnumProperty(items=(('X','X','X'),('Y','Y','Y'),('Z','Z','Z'),
                                    ('-X','-X','-X'),('-Y','-Y','-Y'),('-Z','-Z','-Z')), default='Y', 
                                    description='The foot bone axis determining the foot direction, in case no toe bone is set')
    force_z_axis: BoolProperty(name="Force Z Axis", default=True, description="Force Auto-Rig Pro Z axes with world vectors (recommended for typical humanoid characters facing the Y axis)")
    primary_axis_auto: BoolProperty(default=True, description="Use automatic primary axis")
    primary_axis: bpy.props.EnumProperty(name="Primary Axis", items=(("X", "X", "X"), ("Y", "Y", "Y"), ("Z", "Z", "Z"), 
                                        ("-X", "-X", "-X"), ("-Y", "-Y", "-Y"), ("-Z", "-Z", "-Z")), default='Y', description="The bone axis pointing toward the child bone")
    connect: BoolProperty(name="Connect", description="Connect the head of a bone with its parent tail", default=True)
    connect_foot_to_calf: BoolProperty(name="Connect Foot to Calf", description="Force the foot bone's head position to match the calf bone's tail position.\nIf disabled, the calf bone's tail is connected to the foot bone's head (default)", default=False)
    IK_axis_correc: bpy.props.EnumProperty(items=(('X', 'X', 'X'),
                                        ('Y', 'Y', 'Y'),
                                        ('Z', 'Z', 'Z'),
                                        ('-X', '-X', '-X'),
                                        ('-Y', '-Y', '-Y'),
                                        ('-Z', '-Z', '-Z')), default='Y', description='Axis used to correct the IK bones straight alignment if necessary', name='IK_axis_correc')
    pelvis_up: bpy.props.BoolProperty(default=False, description="Ensure the pelvis bone is pointing upward, should generally be enabled for humanoids")

    auto_ik_roll: BoolProperty(default=False, name='Auto IK Roll', description='Automatically align IK bones axes for coherent rotation axes and perfectly lined up IK pole')
    
    auto_knee: BoolProperty(name="Auto-Knee", description="Automatic knee direction for in-line IK pole based on the foot direction", default=True)
    leg_type: bpy.props.EnumProperty(name="Leg Type", description="Type of leg, using 2 or 3 bones", items=(('2', 'Default', '2 bones leg (humanoids)'), ('3', '3 Bones Leg', '3 bones leg, typicall for quadrupedal creatures')))
    upper_thigh: StringProperty(default="", name="Upper Thigh", description="Additional thigh bone for 3 bones leg")

    thumb: StringProperty(default="", name="Thumb", description="")# metacarpal if fingers are set to 4
    index: StringProperty(default="", name="Index", description="")
    middle: StringProperty(default="", name="Middle", description="")
    ring: StringProperty(default="", name="Ring", description="")
    pinky: StringProperty(default="", name="Pinky", description="")

    manual_phalanges: BoolProperty(default=False, name="All Fingers", description="Set all finger bones manually. \nIf disabled, only set the first phalange of each finger, the other phalanges will be found automatically if they are children bones")

    thumb1: StringProperty(default="", name="Thumb1", description="")
    index1: StringProperty(default="", name="Index1", description="")
    middle1: StringProperty(default="", name="Middle1", description="")
    ring1: StringProperty(default="", name="Ring1", description="")
    pinky1: StringProperty(default="", name="Pinky1", description="")

    thumb2: StringProperty(default="", name="Thumb2", description="")
    index2: StringProperty(default="", name="Index2", description="")
    middle2: StringProperty(default="", name="Middle2", description="")
    ring2: StringProperty(default="", name="Ring2", description="")
    pinky2: StringProperty(default="", name="Pinky2", description="")

    thumb3: StringProperty(default="", name="Thumb3", description="")
    index3: StringProperty(default="", name="Index3", description="")
    middle3: StringProperty(default="", name="Middle3", description="")
    ring3: StringProperty(default="", name="Ring3", description="")
    pinky3: StringProperty(default="", name="Pinky3", description="")
    
    toes_parent_foot: BoolProperty(default=False)
    
    weights_override: BoolProperty(default=False, name="Weights Override", description="Use another bone weight instead of the selected one\nUseful for skeleton with complex bones hierarchy")

    override_bone_01: StringProperty(default="", name="Bone", description="Bone")
    override_bone_02: StringProperty(default="", name="Bone", description="Bone")
    override_bone_03: StringProperty(default="", name="Bone", description="Bone")
    override_bone_04: StringProperty(default="", name="Bone", description="Bone")
    override_bone_05: StringProperty(default="", name="Bone", description="Bone")
    override_bone_06: StringProperty(default="", name="Bone", description="Bone")
    override_bone_07: StringProperty(default="", name="Bone", description="Bone")
    override_upper_thigh: StringProperty(default="", name="Bone", description="Bone")

    dupli_idx: StringProperty(default='')


class ARP_UL_quick_limbs_list(UIList):
    """
    @classmethod
    def poll(cls, context):
        return
    """
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.prop(item, "name", text="", emboss=False, translate=False)# icon='BONE_DATA')

    def invoke(self, context, event):
        pass


class ARP_OT_quick_export_mapping(Operator):
    """Export bones mapping to file"""
    bl_idname = "arp.quick_export_mapping"
    bl_label = "Export bones mapping"

    filter_glob: StringProperty(default="*.py", options={'HIDDEN'})
    filepath: StringProperty(subtype="FILE_PATH", default='py')

    def execute(self, context):
        _export_mapping(self.filepath)
        return {'FINISHED'}

    def invoke(self, context, event):
        self.filepath = 'quick_rig_mapping.py'
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class ARP_OT_quick_import_mapping(Operator):
    """Import bones mapping from file"""
    bl_idname = "arp.quick_import_mapping"
    bl_label = "Import bones mapping"

    filter_glob: StringProperty(default="*.py", options={'HIDDEN'})
    filepath: StringProperty(subtype="FILE_PATH", default='py')

    @classmethod
    def poll(cls, context):
        if context.active_object:
            if context.active_object.type == "ARMATURE":
                return True


    def execute(self, context):
        scn = bpy.context.scene
        try:
            scn.arp_quick_hold_update = True
            
            for i in range(0, len(scn.limb_map)):
                _remove_limb()

            _import_mapping(self)
        finally:
            scn.arp_quick_hold_update = False
        return {'FINISHED'}


    def invoke(self, context, event):
        self.filepath = 'quick_rig_mapping.py'
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class ARP_OT_quick_freeze_armature(Operator):
    """Clear animation datas from the armature object and initialized its transforms. Preserve bones animation"""

    bl_idname = "arp.quick_freeze_armature"
    bl_label = "quick_freeze_armature"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        if context.active_object.type == "ARMATURE":
            return True

    def execute(self, context):
        use_global_undo = context.preferences.edit.use_global_undo
        context.preferences.edit.use_global_undo = False

        try:
            _freeze_armature()

        finally:
            context.preferences.edit.use_global_undo = use_global_undo
        return {'FINISHED'}


class ARP_OT_quick_set_weight_override(Operator):
    """Set weight override for the selected bone"""
    bl_idname = "arp.quick_set_weight_override"
    bl_label = "Override weight with this bone:"
    bl_options = {'UNDO'}
    """
    @classmethod
    def poll(cls, context):
        if context.active_object:
            return context.active_object.type == "ARMATURE"
        return False
    """
    value: StringProperty(default="")

    def invoke(self, context, event):
        # open dialog
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        limb = scn.limb_map[scn.limb_map_index]
        row = layout.column().row(align=True)
        row.prop(limb, "override_"+self.value, text="")
        row.operator(ARP_OT_quick_pick_bone.bl_idname, text="", icon='EYEDROPPER').value = "override_"+self.value

    def execute(self, context):
        print("")
        return {'FINISHED'}


class ARP_OT_quick_revert(Operator):
    """Revert to original armature and weights"""
    bl_idname = "arp.quick_revert"
    bl_label = "Revert"
    bl_options = {'UNDO'}

    meshes_parented_to_bones = {}
    skin_dict = {}

    def execute(self, context):
        try:
            _revert(self)
        finally:
            print("")
        return {'FINISHED'}


class ARP_OT_quick_make_rig(Operator):
    """Generate the Auto-Rig Pro armature from the selected armature"""
    bl_idname = "arp.quick_make_rig"
    bl_label = "Make Rig!"
    bl_options = {'UNDO'}

    mode: EnumProperty(items=(('CONVERT', 'Convert', 'Convert current skeleton to Auto-Rig Pro skeleton, changing bone names and axes.\nCompliant with Auto-Rig Pro edition and export tools'), ('PRESERVE', 'Preserve', 'Preserve current skeleton as it is, only attach Auto-Rig Pro controllers to it.\nNot compliant with Auto-Rig Pro edition and export tools')))
    match_to_rig: BoolProperty(default=True, name="Match to Rig", description="Complete rig generation with Match to Rig, otherwise shows reference bones")

    animation: EnumProperty(items=(
        ('ANIM_BAKE', 'Bake Animation', 'Bake the animation (Remap Retarget)'),
        ('ANIM_BIND', 'Bind Only (Remap)', 'Bind the animation (Remap Bind Only)'),
        ('NO_ANIM', 'No Animation', 'Do not bake animation')
        ), default='NO_ANIM', name='Animation')

    show_in_front: BoolProperty(default=True, name="Show In Front", description="Display rig controllers in front of other object (X-Ray like), so that controllers inside meshes are visible")
    remove_root: BoolProperty(default=True, name="Remove Root", description='Remove any bone named "Root" (case insensitive) at the root of the skeleton')
    neck_auto_twist: BoolProperty(default=False, description="Use automatic twist bones for the neck")
    hide_base_armature: BoolProperty(default=True, name="Hide Base Armature", description="Hide existing skeleton")
    match_origin: BoolProperty(default=True, name="Same Origin", description="Match the control rig origin point with the skeleton origin, otherwise leave it in the world center (0,0,0)")
    orphan_bones_shape: EnumProperty(items=(('NONE', 'None', 'None'), ('cs_sphere', 'cs_sphere', 'cs_sphere'), ('cs_box', 'cs_box', 'cs_box')), name="Orphan Bones Shape", description="Custom bone shape for orphan bones that are not used in the limb definition", default="cs_sphere")
    orphan_bones_scale: FloatProperty(default=0.5, name="Orphan Bones Scale", description="Custom shape scale of orphan bones")
    orphan_bones_layer: IntProperty(default=0, name="Orphan Bones Layer", description="Set orphan bones in this layer index", min=0, max=31)
    orphan_bones_collection: EnumProperty(items=(('Main','Main','Main collection'),('Secondary', 'Secondary', 'Secondary collection'),('Orphan Bones', 'Orphan Bones', 'Orphan bones collection')), default='Main', description='Collection to add orphan bones to')
    orphan_copy_cns: BoolProperty(default=False, name="Copy Constraints", description='Copy orphan bones constraints')
    retarget_sk_drivers: BoolProperty(default=False, name="Retarget Shape Keys Drivers", description='Retarget drivers from the source bones to controllers')
    preserve_volume: BoolProperty(default=False, name="Preserve Volume", description="Use dual quaternions skinning (Preserve Volume) or linear skinning")
    color_orphan_group: FloatVectorProperty(name="Color Orphan Bones", subtype="COLOR_GAMMA", default=(1.0, 1.0, 0.0), min=0.0, max=1.0, description="Orphan controllers color")
    arm_ik_fk: EnumProperty(items=(('IK', 'IK', 'IK'), ('FK', 'FK', 'FK')), default='FK', description='Arm kinematic mode')
    leg_ik_fk: EnumProperty(items=(('IK', 'IK', 'IK'), ('FK', 'FK', 'FK')), default='IK', description='Leg kinematic mode')
    orphan_bones_loc_retarget: EnumProperty(items=(('IK', 'Global', 'IK'), ('LOCAL', 'Local', 'Local')), default='IK', description='Space system to retarget orphan bones location')
    orphan_bones_parent_to_def: BoolProperty(default=False, description='Parent orphan bones to main bones that are set in the limbs list, if possible, instead of another orphan bone as parent')

    base_armature_name = ''
    base_armature_pos = None
    arp_armature_name = ''
    orphan_bones_dict = {}
    source_anim_rig_name = ''    
    fingers_ctrl = {}
    toes_ctrl = {}
    tail_ctrl = {}
    meshes_parented_to_bones = {}
    skin_dict = {}
    
    arp_ver_int = None
    arp_light = False
    
    @classmethod
    def poll(cls, context):
        if context.active_object:
            return context.active_object.type == "ARMATURE"
        return False


    def restore_base_arm_loc(self):
        base_armature = get_object(self.base_armature_name)
        print("restore base armature loc:", self.base_armature_name)
        base_armature.location = self.base_armature_pos
        bpy.context.evaluated_depsgraph_get().update()


    def invoke(self, context, event):
        self.arp_light = False
        self.fingers_ctrl = {}
        self.toes_ctrl = {}
        self.tail_ctrl = {}
        self.meshes_parented_to_bones = {}
        self.skin_dict = {}
        self.base_armature_name = bpy.context.active_object.name
        base_armature = get_object(self.base_armature_name)
        self.base_armature_pos = base_armature.location.copy()
        scn = context.scene

        def show_error(_error_message):
            ARP_OT_quick_report_message.message = _error_message
            ARP_OT_quick_report_message.icon_type = 'ERROR'
            bpy.ops.arp.quick_report_message('INVOKE_DEFAULT')

        # Safety checks
        # check Auto-Rig Pro is installed
        auto_rig_pro_found = False
        auto_rig_pro_version = False
        
        for addon in addon_utils.modules():
            if addon.bl_info['name'] == 'Auto-Rig Pro' or addon.bl_info['name'] == 'Auto-Rig Pro (Light)':
                auto_rig_pro_found = True
                ver_string = addon.bl_info['version']
                ver_string = (str(ver_string[0])+str(ver_string[1])+str(ver_string[2]))
                self.arp_ver_int = int(ver_string)
                if self.arp_ver_int >= 36910:
                    auto_rig_pro_version = True
                    
                if 'Light' in addon.bl_info['name']:
                    self.arp_light = True
                
                break

        if not auto_rig_pro_found:
            show_error('Auto-Rig Pro is not installed.\nInstall it first, it is required to use Quick Rig')
            return {"FINISHED"}

        if not auto_rig_pro_version:
            show_error('Requires Auto-Rig Pro version 3.69.10 or above. \nPlease download and install it.')
            return {"FINISHED"}


        
        # check there are limbs
        if len(scn.limb_map) == 0:
            show_error('No limbs found, cannot generate rig. Add limbs first.')
            return {"FINISHED"}

        # check for invalid multiple limbs (head, spine)
        limbs_count_dict = {"heads.x":0, "spines.x":0}
        for limb_item in scn.limb_map:
            if limb_item.type == "HEAD":
                limbs_count_dict["heads.x"] = limbs_count_dict["heads.x"]+1
            elif limb_item.type == "SPINE":
                limbs_count_dict["spines.x"] = limbs_count_dict["spines.x"]+1
        
        for limb in limbs_count_dict:
            if limbs_count_dict[limb] > 1:
                show_error('Multiple limbs of the same type and same side found, not supported yet.\nRemove duplicates (Head, Spine)')
                return {"FINISHED"}
        
        
        # check all required bones are set
        for limb in scn.limb_map:
            if limb.type == "LEG":
                bone_names = []
                if limb.leg_type == "2":
                    bone_names = ["thigh", "calf", "foot"]
                    req_bones = [limb.bone_01, limb.bone_03, limb.bone_05]
                elif limb.leg_type == "3":
                    bone_names = ["upper_thigh", "thigh", "calf", "foot"]
                    req_bones = [limb.upper_thigh, limb.bone_01, limb.bone_03, limb.bone_05]
                
                # twists
                '''# disable twist check for now... some skeletons have twist bones for thigh but not calf
                if limb.twist_bones_amount > 1:# if only one twist, twist bones are optional. Above, check.
                    req_bones.append(limb.bone_02)
                    bone_names.append('Thigh Twist 01')
                    req_bones.append(limb.bone_04)
                    bone_names.append('Calf Twist 01')
                    
                    for i in range(2, limb.twist_bones_amount+1):
                        id = '%02d' % (i)
                        req_bones.append(limb.get('bone_twist_'+id+'_01'))                        
                        bone_names.append('Thigh Twist '+id)
                        req_bones.append(limb.get('bone_twist_'+id+'_02'))
                        bone_names.append('Calf Twist '+id)
                '''        
                for i, n in enumerate(req_bones):
                    if n == "" or n == None or base_armature.data.bones.get(n) == None:
                        show_error('Error: Leg '+limb.side.lower()+' is missing required input bones: '+str(bone_names[i]).upper())
                        return {"FINISHED"}

            elif limb.type == "ARM":
                bone_names = ["arm", "forearm", "hand"]
                req_bones = [limb.bone_02, limb.bone_04, limb.bone_06]
                
                # twists
                '''# disable twist check for now... some skeletons have twist bones for upperarm but not foerarm
                if limb.twist_bones_amount > 1:# if only one twist, twist bones are optional. Above, check.
                    req_bones.append(limb.bone_03)
                    bone_names.append('Arm Twist 01')
                    req_bones.append(limb.bone_05)
                    bone_names.append('Forearm Twist 01')
                    
                    for i in range(2, limb.twist_bones_amount+1):
                        id = '%02d' % (i)
                        req_bones.append(limb.get('bone_twist_'+id+'_01'))                        
                        bone_names.append('Arm Twist '+id)
                        req_bones.append(limb.get('bone_twist_'+id+'_02'))
                        bone_names.append('Forearm Twist '+id)
                '''
                for i, n in enumerate(req_bones):
                    if n == "" or n == None or base_armature.data.bones.get(n) == None:
                        show_error('Error: Arm '+limb.side.lower()+' is missing required input bones: '+str(bone_names[i]).upper())
                        return {"FINISHED"}

            elif limb.type == "SPINE":
                for n in [limb.bone_01, limb.bone_02]:# set one minimum spine bone for now, but actually 0 could technically work. Should prevent errors though.
                    if n == '' or base_armature.data.bones.get(n) == None:
                        show_error("Error: Spine is missing required input bones")
                        return {"FINISHED"}

            elif limb.type == "HEAD":
                if limb.bone_02 == "" or base_armature.data.bones.get(limb.bone_02) == None:# only head required, neck optional
                    show_error("Error: Head is missing required input bones")
                    return {"FINISHED"}
                # neck2 can't be set if neck1 is not set
                if limb.bone_04 != "":
                    if limb.bone_01 == "" or base_armature.data.bones.get(limb.bone_04) == None or base_armature.data.bones.get(limb.bone_01) == None:
                        show_error("Error: Head is missing required input bones")
                        return {"FINISHED"}

                if limb.neck_bones_amount > 1:
                    # ensure to set/clamp neck_bones_amount to defined neck entries, if entry blank or not found, decrease amount
                    necks_list = [limb.bone_04, limb.neck3, limb.neck4, limb.neck5, limb.neck6, limb.neck7, limb.neck8, limb.neck9, limb.neck10]
                    for i in range(2, limb.neck_bones_amount+1):
                        cur_neck = necks_list[i-2]
                        if cur_neck == "" or base_armature.data.bones.get(cur_neck) == None:
                            limb.neck_bones_amount = i-1
                            #show_error("Error: Neck is missing required input bones")
                            #return {"FINISHED"}
              
            elif limb.type == 'TAIL':
                if limb.bone_01 == '' or base_armature.data.bones.get(limb.bone_01) == None:
                    show_error("Error: Tail is missing required input bones")
                    return {"FINISHED"}
        
        # open dialog
        wm = context.window_manager
        return wm.invoke_props_dialog(self)


    def draw(self, context):
        scn = context.scene
        layout = self.layout
        layout.prop(self, "mode", expand=True)

        layout.prop(self, "animation", text="Animation")
        
        if self.arp_light:# Auto-Rig Pro Light version does not support anim remap
            if self.animation != 'NO_ANIM':
                layout.label(text="Auto-Rig Pro Full version is required for animation", icon='ERROR')
        else:
            if self.animation == 'ANIM_BAKE':
                layout.operator('arp.batch_retarget', text='Multiple Anims...')
                col = layout.column()
                row = col.row().split(factor=0.45)
                row.label(text='Orphan Bones Locations')
                row.prop(self, 'orphan_bones_loc_retarget', text='')
                layout.separator()
        
        layout.prop(self, "arm_ik_fk", text="Arms")
        layout.prop(self, "leg_ik_fk", text="Legs")
        layout.prop(self, "neck_auto_twist", text="Neck Twist")
        layout.prop(self, "remove_root", text='Ignore "Root" Bone')

        col = layout.column()
        col.prop(self, "match_to_rig", text="Match to Rig")
        col.enabled = True if self.animation == 'NO_ANIM' else False

        layout.prop(self, "show_in_front", text="X-Ray Display")
        layout.prop(self, "preserve_volume", text="Preserve Volume")
        layout.prop(self, "match_origin")

        if self.mode == 'CONVERT':
            layout.prop(self, "hide_base_armature", text="Hide Base Armature")

        layout.separator()

        layout.label(text="Orphan Bones:")
        layout.prop(self, 'orphan_bones_parent_to_def', text='Parent to Main Bones (when possible)')
        layout.prop(self, 'orphan_copy_cns', text='Copy Constraints')
        layout.prop(self, 'retarget_sk_drivers', text='Retarget Shape Keys Drivers')
        layout.prop(self, "orphan_bones_shape", text="Shape")
        layout.prop(self, "orphan_bones_scale", text="Scale")
        layout.prop(self, "color_orphan_group", text="Color")
        
        layout.prop(self, 'orphan_bones_layer' if bpy.app.version < (4,0,0) else 'orphan_bones_collection', text='Layer' if bpy.app.version < (4,0,0) else 'Collection')
        layout.separator()


    def execute(self, context):
        use_global_undo = context.preferences.edit.use_global_undo
        context.preferences.edit.use_global_undo = False
        scn = bpy.context.scene
        debug = False

        time_start = time.time()
        self.orphan_bones_dict = {}# clear previous sessions data if any

        if self.arp_light:
            self.animation = "NO_ANIM"
        
        def execute_make_rig():
            if self.animation != 'NO_ANIM':
                print("-------------------------------------- ANIM--------------------------------------------------")
                rig = get_object(bpy.context.active_object.name)
                if rig.animation_data:
                    if rig.animation_data.action:
                        if len(bpy.context.selected_objects) > 1:
                            for o in bpy.context.selected_objects:
                                if o != rig:
                                    o.select_set(state=False)

                        bpy.ops.object.mode_set(mode='OBJECT')
                        
                        current_act_name = rig.animation_data.action.name
                        act_list = [act.name for act in bpy.data.actions]
                        
                        duplicate_object()
                        
                        print('set self.source_anim_rig_name', rig.name+'_ANIM_TEMP')
                        self.source_anim_rig_name = rig.name+'_ANIM_TEMP'
                        bpy.context.active_object.name = self.source_anim_rig_name
                        
                        # remove duplicated action
                        for act in bpy.data.actions:
                            if not act.name in act_list:
                                bpy.data.actions.remove(act)
                                
                        # assign action
                        bpy.context.active_object.animation_data.action = bpy.data.actions.get(current_act_name)
                        
                        bpy.ops.object.mode_set(mode='OBJECT')
                        bpy.ops.object.select_all(action='DESELECT')
                        set_active_object(rig.name)

            # Make
            _make_rig(self)
            
            # Match to rig
            if self.match_to_rig or self.animation != 'NO_ANIM':
                bpy.ops.arp.match_to_rig()
                bpy.ops.arp.reset_pose()
                
                if len(self.orphan_bones_dict):
                    # Orphan bones layer display
                    arp_armature = bpy.context.active_object
                    
                    enable_layer(self.orphan_bones_collection, idx=self.orphan_bones_layer)
                    
                    #   sort bones collections
                    if bpy.app.version >= (4,0,0):
                        sort_armature_collections(arp_armature, only_collection=self.orphan_bones_collection)
                

            # Hide armature
            base_arm = get_object(self.base_armature_name)

            if self.mode == 'CONVERT' and self.hide_base_armature:
                if base_arm:
                    base_arm.hide_set(True)

            # X-Ray display
            screen = bpy.context.screen

            for area in screen.areas:
                if area.type == "VIEW_3D":
                    for space in area.spaces:
                        try:
                            space.overlay.show_xray_bone = self.show_in_front
                        except:
                            pass

            base_arm = get_object(self.base_armature_name)
            arp_arm = get_object(self.arp_armature_name)

            if self.match_origin:
                self.restore_base_arm_loc()

                # arp loc at base armature loc
                rot_save, scale_save = arp_arm.rotation_euler.copy(), arp_arm.scale.copy()
                arp_arm.matrix_world = base_arm.matrix_world.copy()
                arp_arm.rotation_euler, arp_arm.scale = rot_save, scale_save

            # Parent meshes
            if self.mode == 'CONVERT':
                _parent_meshes(self, base_arm, arp_arm)


            # Animation
            if self.animation != 'NO_ANIM':
                _remap_animation(self)


            elapsed_time = round((time.time() - time_start), 1)
            self.report({"INFO"}, "Rig done in "+str(elapsed_time)+' seconds')
            # end execute_make_rig()

        if debug:
            try:
                execute_make_rig()

            finally:
                #if self.match_origin:
                #    self.restore_base_arm_loc()

                context.preferences.edit.use_global_undo = use_global_undo
        else:
            try:
                execute_make_rig()

            except Exception as ex:
                #pass
                error_message = get_error_message()#"Unexpected error: "+str(ex.args)+str(ex)
                self.report({'ERROR'}, error_message)
                try:
                    # delete ARP armature
                    bpy.ops.object.mode_set(mode='OBJECT')
                    set_active_object(self.arp_armature_name)
                    bpy.ops.arp.delete_arp()
                except:
                    pass

            finally:
                if self.match_origin:
                    self.restore_base_arm_loc()
                    
                # hide the qr_helpers collection
                if self.mode == 'PRESERVE':
                    hide_layer('qr_helpers', idx=15)

                context.preferences.edit.use_global_undo = use_global_undo


        return {'FINISHED'}

        
class ARP_OT_quick_mirror_limb(Operator):
    """Mirror the selected limb\nAxes settings may not mirror properly.\nThe bone names must contain left or right identifier such as _left or .l"""

    bl_idname = "arp.quick_mirror_limb"
    bl_label = "Mirror Limb"
    bl_options = {'UNDO'}
    
    
    mirrors_not_found = []

    @classmethod
    def poll(cls, context):
        if context.active_object:
            if context.mode == "POSE" or context.mode == "EDIT_ARMATURE":
                return True
        return False
        

    def execute(self, context):
        use_global_undo = context.preferences.edit.use_global_undo
        context.preferences.edit.use_global_undo = False

        if len(bpy.context.scene.limb_map) == 0:
            self.report({'ERROR'}, 'No limbs to mirror. Add limbs first.')
            return {'FINISHED'}
        
        try:        
            self.mirrors_not_found = []
            
            _mirror_limb(self)
            
        finally:
            if len(self.mirrors_not_found):
                mess = 'Mirror bones not found:'
                for i in self.mirrors_not_found:
                    mess += '\n'+i
                self.report({'ERROR'}, mess)
                
            context.preferences.edit.use_global_undo = use_global_undo
            
        return {'FINISHED'}
        

class ARP_OT_quick_add_limb(Operator):
    """Add a limb"""
    bl_idname = "arp.quick_add_limb"
    bl_label = "Add Limb"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        if context.active_object:
            if context.mode == "POSE" or context.mode == "EDIT_ARMATURE":
                return True
        return False

    type : bpy.props.EnumProperty(items=(
        ('LEG', 'Leg', 'Leg'), ('ARM', 'Arm', 'Arm'), ('SPINE', 'Spine', 'Spine'), 
        ('HEAD', 'Head', 'Head'), ('TAIL', 'Tail', 'Tail')), 
        description='Limb Type', name='Limb Type')

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        first_bone_name = ''
        if self.type == 'LEG':
            first_bone_name = 'Thigh'
        elif self.type == 'ARM':
            first_bone_name = 'Shoulder'
        elif self.type == 'SPINE':
            first_bone_name = 'Pelvis'
        elif self.type == 'HEAD':
            first_bone_name = 'Neck'
        elif self.type == 'TAIL':
            first_bone_name = 'Tail root'
        col.label(text="Make sure the following first bone of the limb is selected")
        col.label(text="before clicking OK:")
        col.label(text=first_bone_name)
        layout.prop(self, "type", expand=True)


    def execute(self, context):
        use_global_undo = context.preferences.edit.use_global_undo
        context.preferences.edit.use_global_undo = False

        try:
            check_freeze_armature()
            _add_limb(self)
        finally:
            context.preferences.edit.use_global_undo = use_global_undo
        return {'FINISHED'}
        

    def invoke(self, context, event):
        # pre-select limb type according to current selection
        sel_bone = context.active_bone
        if sel_bone:
            sel_bone_name = sel_bone.name.lower()
            if "shoulder" in sel_bone_name or "clavicle" in sel_bone_name:
                self.type = "ARM"
            elif "thigh" in sel_bone_name or "leg" in sel_bone_name:
                self.type = "LEG"
            elif "pelvis" in sel_bone_name or "root" in sel_bone_name or "hips" in sel_bone_name or "spine" in sel_bone_name:
                self.type = "SPINE"
            elif "neck" in sel_bone_name or "head" in sel_bone_name:
                self.type = "HEAD"
            else:# 'tail' in sel_bone_name:
                self.type = 'TAIL'

        # Open dialog
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)


class ARP_OT_quick_remove_limb(Operator):
    """Remove the selected limb"""
    bl_idname = "arp.quick_remove_limb"
    bl_label = "quick_remove_limb"
    bl_options = {'UNDO'}
    """
    @classmethod
    def poll(cls, context):
        if context.active_object:
            return context.active_object.type == "EMPTY"
    """
    def execute(self, context):
        use_global_undo = context.preferences.edit.use_global_undo
        context.preferences.edit.use_global_undo = False

        try:
            _remove_limb()

        finally:
            context.preferences.edit.use_global_undo = use_global_undo
        return {'FINISHED'}


class ARP_OT_quick_pick_bone(Operator):
    """Pick selected bone"""
    bl_idname = "arp.quick_pick_bone"
    bl_label = ""
    bl_options = {'UNDO'}

    value : StringProperty(default="")
    """
    @classmethod
    def poll(cls, context):
        if context.active_object:
            return context.active_object.type == "EMPTY"
    """
    def execute(self, context):
        use_global_undo = context.preferences.edit.use_global_undo
        context.preferences.edit.use_global_undo = False

        try:
            _pick_bone(self)

        finally:
            context.preferences.edit.use_global_undo = use_global_undo
        return {'FINISHED'}


# GENERIC FUNCTIONS
#############################################################################
def get_error_message():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    error_message = 'Error in ({}\nLine {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj)
    return error_message



# OPERATOR FUNCTIONS
#############################################################################
def pose_bone_constraints_from_dict(armature, pbone, cns_multi_dict):

    def get_constraint_target(target_name):
        # returns the constraint target object, being the current rig or other object
        if target_name == None:
            return None
        if target_name == "rig__self":
            return armature
        else:
            return get_object(target_name)


    for cns_dict in cns_multi_dict:
        new_cns = pbone.constraints.new(cns_dict["type"])

        for cns_prop in cns_dict:
            # specials
            if cns_prop == "action":
                action_name = cns_dict[cns_prop]
                setattr(new_cns, cns_prop, bpy.data.actions.get(action_name))

            elif cns_prop == "type":  # type can only be set when creating the constraint before
                continue

            elif cns_prop == "target" or cns_prop == "pole_target":  # fetch the object from name
                target_name = cns_dict[cns_prop]
                setattr(new_cns, cns_prop, get_constraint_target(target_name))
                continue

            elif cns_prop == "targets":  # armature constraints have multiple targets
                for tar in cns_dict[cns_prop]:
                    tar_obj_name, tar_bone_name, tar_weight = tar[0], tar[1], tar[2]
                    t = new_cns.targets.new()
                    t.target = get_constraint_target(tar_obj_name)
                    t.subtarget = tar_bone_name#get_target_bone_name(tar_bone_name)
                    t.weight = tar_weight
                continue

            elif "subtarget" in cns_prop:
                setattr(new_cns, cns_prop, cns_dict[cns_prop])#get_target_bone_name(cns_dict[cns_prop]))
                continue

            # common props
            try:
                setattr(new_cns, cns_prop, cns_dict[cns_prop])
            except:
                pass

        '''
        # set Child Of constraints inverse matrix
        if new_cns.type == "CHILD_OF":
            print("Set inverse matrix for ChildOf constraint of:", pbone.name, "...")
            set_constraint_inverse_matrix(new_cns, pbone)
        '''


def pose_bones_constraints_to_dict(armature_object, pose_bones_list):
    # returns a dict of bones constraints, containing a dict of constraints data
    # bones_data[bone_name] = constraint_data[constraint_name]
    bones_data = {}
    exclude_cns_props = ['__doc__', '__module__', '__slots__', 'active', 'bl_rna', 'error_location', 'error_rotation',
                         'is_proxy_local', 'is_valid', 'rna_type', 'joint_bindings']

    def get_constraint_relative_target(target):
        if target == armature_object:
            return "rig__self"
        else:
            return cns.target.name

    for pbone in pose_bones_list:
        if len(pbone.constraints) == 0:
            continue
        cns_dict_list = []
        for cns in pbone.constraints:
            cns_data = {}
            for prop in dir(cns):
                if prop in exclude_cns_props or "matrix" in prop:  # no need to export matrices (Child Of constraints)
                    continue

                if prop == "action":
                    if cns.action:
                        cns_data["action"] = cns.action.name
                        continue

                # get the name of the target object instead of pointer to be string compatible
                if prop == "target":
                    if cns.target:
                        # save the rig as special variable since its name can change, to import it properly later
                        cns_data["target"] = get_constraint_relative_target(cns.target)
                        continue

                # armature constraints have multiple targets
                if prop == "targets":
                    targets_list = []
                    for tar in cns.targets:
                        if tar == None:
                            targets_list.append(["", "", tar.weight])
                            continue
                        tar_name = get_constraint_relative_target(tar.target)
                        targets_list.append([tar_name, tar.subtarget, tar.weight])
                    cns_data["targets"] = targets_list
                    continue

                if prop == "pole_target":
                    if cns.pole_target:
                        cns_data["pole_target"] = get_constraint_relative_target(cns.pole_target)
                    continue

                try:
                    getattr(cns, prop)
                except:
                    continue

                prop_val = getattr(cns, prop)

                # convert Vector to list
                if type(prop_val) == Vector:
                    prop_val = [prop_val[0], prop_val[1], prop_val[2]]

                cns_data[prop] = prop_val

            cns_dict_list.append(cns_data)

        bones_data[pbone.name] = cns_dict_list

    return bones_data

    
def find_closest_match(word, word_list, threshold=0.6):
    closest_match = None
    closest_match_ratio = 0
    valid_match = None
    
    while valid_match == None and threshold > 0.3:
        for candidate in word_list:
            ratio = difflib.SequenceMatcher(None, word, candidate).ratio()
            if ratio > closest_match_ratio:
                closest_match_ratio = ratio
                closest_match = candidate
      
        if closest_match_ratio >= threshold:
            valid_match = closest_match
        else:
            threshold -= 0.1
        
    return valid_match
        

def set_mapping_from_dict(dict, armature, self):
    print("set mapping from dict")
    scn = bpy.context.scene
    for limb_name in dict:
        item = None
        if limb_name in scn.limb_map:
            item = scn.limb_map[limb_name]
        else:
            item = scn.limb_map.add()
        
        prop_dict = dict[limb_name]
        for prop in prop_dict:
            prop_value = prop_dict[prop]
            def_bone_name = prop_value
            valid = True
            # check the bone exists in the selected armature
            if prop.startswith("bone_") or prop.startswith("override_bone_") or prop in ["thumb", "index", "middle", "pinky", "ring"]:
                valid = False
                for b in armature.data.bones:
                    if b.name == prop_value:
                        valid = True
                        break
                
                if not valid:# Preset does not match
                
                    # approximate the mixamorig prefix
                    preset_name = ""
                    try:
                        preset_name = self.preset_name
                    except:
                        pass
                    if preset_name == "mixamo" or preset_name == "mixamo_old":
                        # special case for mixamo, check the 'mixamo:' prefix, may be included or not in the bone name
                        for b in armature.data.bones:
                            if ':' in b.name:
                                prefix = b.name.split(':')[0]
                                if b.name.replace(prefix+':', '') == prop_value.replace('mixamorig:', ''):
                                    def_bone_name = def_bone_name = b.name#'mixamorig:'+prop_value
                                    valid = True
                                    break
                            else:
                                if b.name == prop_value.replace('mixamorig:', ''):
                                    def_bone_name = b.name
                                    valid = True
                                    break
                                    
                    # fuzzy match
                    if not valid:        
                        if hasattr(self, 'fuzzy_match') and self.fuzzy_match:
                            closest_match = find_closest_match(prop_value, [b.name for b in armature.data.bones])                           
                            if closest_match:
                                #print("CLOSE MATCH:", prop_value, closest_match)
                                def_bone_name = closest_match
                                valid = True

            if valid:
                setattr(item, prop, def_bone_name)

    scn.limb_map_index = 0

    # check if limbs are properly set, if not show an error message
    valid = False
    for limb in scn.limb_map:
        for prop in dir(limb):
            if prop.startswith("bone_"):
                attr = getattr(limb, prop)
                if attr != "":
                    valid = True

    #if not valid:
        #err_mess = "No bone names match in this preset. Is the preset correct for this skeleton?"
        #self.report({"ERROR"}, err_mess)
        #print(err_mess)
    return valid


def _import_mapping(self):
    print("import preset:", self.filepath)
    filepath = self.filepath
    scn = bpy.context.scene
    armature = bpy.context.active_object
    file = open(filepath, 'r') if sys.version_info >= (3, 11) else open(filepath, 'rU')
    file_lines = file.readlines()
    mapping_dict_str = str(file_lines[0])
    file.close()
    mapping_dict = ast.literal_eval(mapping_dict_str)
    import_success = set_mapping_from_dict(mapping_dict, armature, self)
    return import_success


def _export_mapping(filepath):
    scn = bpy.context.scene
    if not filepath.endswith(".py"):
        filepath += ".py"

    file = open(filepath, "w", encoding="utf8", newline="\n")
    mapping_dict = {}

    for limb_item in scn.limb_map:
        # get the actual item properties
        prop_list = []
        for item_prop in dir(limb_item):
            if not item_prop.startswith("__") and item_prop != "bl_rna" and item_prop != "rna_type":
                prop_list.append(item_prop)

        # set prop dict
        prop_dict = {}
        for prop in prop_list:
            prop_dict[prop] = getattr(limb_item, prop)

        # set mapping dict
        mapping_dict[limb_item.name] = prop_dict

    file.write(str(mapping_dict))

    # close file
    file.close()


def _freeze_armature():
    context = bpy.context
    saved_frame = context.scene.frame_current
    context.scene.frame_set(bpy.context.scene.frame_current)

    # Disable auto-keying
    bpy.context.scene.tool_settings.use_keyframe_insert_auto = False

    arm_name = context.active_object.name
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    set_active_object(arm_name)

    base_arm_name = arm_name

    base_action_name = ""
    if context.active_object.animation_data:
        if context.active_object.animation_data.action:
            base_action_name = context.active_object.animation_data.action.name

    # is it animated?
    is_animated = False

    if base_action_name != "":
        for fcurve in bpy.context.active_object.animation_data.action.fcurves:
            if not "pose.bones" in fcurve.data_path:
                if "location"in fcurve.data_path or "rotation" in fcurve.data_path or "scale" in fcurve.data_path:
                    is_animated = True
                    break

    
    # disable animation
    cur_act = None
    cur_rot = [bpy.context.active_object.rotation_euler.copy(), bpy.context.active_object.rotation_quaternion.copy()]
    if is_animated:
        cur_act = bpy.context.active_object.animation_data.action
        bpy.context.active_object.animation_data.action = None
        bpy.context.active_object.rotation_euler = [0,0,0]
        bpy.context.active_object.rotation_quaternion = [0,0,0,0]
    
    # Zero out children mesh object
    armature = get_object(arm_name)
    if len(armature.children):
        for obj in armature.children:
            if obj.type == "MESH":
                obj_mat = obj.matrix_world.copy()
                obj.parent = None
                bpy.context.evaluated_depsgraph_get().update()
                obj.matrix_world = obj_mat
        print("Meshes unparented")
    
    # restore animation
    if is_animated:
        bpy.context.active_object.animation_data.action = cur_act
        bpy.context.active_object.rotation_euler = cur_rot[0]
        bpy.context.active_object.rotation_quaternion = cur_rot[1]
      
    #   if not animated, just apply the rotation
    if not is_animated:
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
        context.scene.arp_quick_freeze_check = False
        print("Armature rotation initialized")

    # if animated, freeze the armature animation
    else:
        # temporarily set keyframe rotation to 0
        
        
        bpy.context.active_object.rotation_euler = [0,0,0]
        bpy.context.active_object.rotation_quaternion = [0,0,0,0]

        # duplicate
        bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(0, 0, 0), "remove_on_cancel":False, "release_confirm":False, "use_accurate":False})

        bpy.context.active_object.animation_data.action.name = base_action_name + "_TEMP_COPY"

        # Constraint on the first armature
        bpy.ops.object.mode_set(mode='POSE')

        for pbone in bpy.context.active_object.pose.bones:
            cns = pbone.constraints.new('COPY_TRANSFORMS')
            cns.target = bpy.data.objects[base_arm_name]
            cns.subtarget = pbone.name
            cns.name = "arp_remap_temp"

        # Set frame 0
        bpy.context.scene.frame_set(0)

        # Clear armature object keyframes
        fcurves = bpy.context.active_object.animation_data.action.fcurves

        for fc_index, fc in enumerate(fcurves):
            if not "pose.bones" in fc.data_path:
                if "rotation" in fc.data_path or "location" in fc.data_path or "scale" in fc.data_path:
                    bpy.context.active_object.animation_data.action.fcurves.remove(fc)

        # Apply transforms
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=False)

        # Bake
        frame_range = bpy.context.active_object.animation_data.action.frame_range
        #bpy.ops.nla.bake(frame_start=frame_range[0], frame_end=frame_range[1], visual_keying=True, only_selected = False, bake_types={'POSE'})
        
        bake_anim(frame_start=frame_range[0], frame_end=frame_range[1], only_selected=False, bake_bones=True, bake_object=False)

        # Delete constraints
        for pbone in bpy.context.active_object.pose.bones:
            pbone.constraints.remove(pbone.constraints["arp_remap_temp"])
        
        # Delete old armature
            # change armature modifiers targets
        for obj in bpy.data.objects:
            if obj.type != "MESH":
                continue
            for mod in obj.modifiers:
                if mod.type != "ARMATURE":
                    continue
                mod.object = bpy.context.active_object

        bpy.data.objects.remove(bpy.data.objects[base_arm_name], do_unlink=True)
        bpy.context.active_object.name = base_arm_name

        # Delete old actions
        bpy.data.actions.remove(bpy.data.actions[base_action_name], do_unlink = True)
        try:
            bpy.data.actions.remove(bpy.data.actions[base_action_name + "_TEMP_COPY"], do_unlink = True)
        except:
            pass

        # Rename new action
        bpy.context.active_object.animation_data.action.name = base_action_name

        context.scene.frame_set(saved_frame)
        context.scene.arp_quick_freeze_check = False

        print("Armature is now still.")


def check_freeze_armature():
    context = bpy.context
    if context.active_object.type == "ARMATURE":
        arm_obj = bpy.data.objects[context.active_object.name]

        # is rotation initialized?
        for rot_axis in arm_obj.rotation_euler:
            if round(rot_axis, 3) != 0.0:
                context.scene.arp_quick_freeze_check = True
                return

        # is the armature animated?
        if arm_obj.animation_data:
            if arm_obj.animation_data.action:
                for fcurve in arm_obj.animation_data.action.fcurves:
                    if not "pose.bones" in fcurve.data_path:
                        if "location"in fcurve.data_path or "rotation" in fcurve.data_path or "scale" in fcurve.data_path:
                            context.scene.arp_quick_freeze_check = True
                            return
    else:
        context.scene.arp_quick_freeze_check = False


def bake_anim(frame_start=0, frame_end=10, only_selected=False, bake_bones=True, bake_object=False):
    # similar to bpy.ops.nla.bake but faster

    scn = bpy.context.scene
    obj_data = []
    bones_data = []
    armature = get_object(bpy.context.active_object.name)

    def get_bones_matrix():
        matrix = {}
        for pbone in armature.pose.bones:
            if only_selected and not pbone.bone.select:
                continue
            matrix[pbone.name] = armature.convert_space(pose_bone=pbone, matrix=pbone.matrix, from_space="POSE", to_space="LOCAL")
        return matrix

    def get_obj_matrix():
        parent = armature.parent
        matrix = armature.matrix_world
        if parent:
            return parent.matrix_world.inverted_safe() @ matrix
        else:
            return matrix.copy()

    # store matrices
    current_frame = scn.frame_current
    for f in range(int(frame_start), int(frame_end+1)):
        scn.frame_set(f)
        bpy.context.view_layer.update()

        if bake_bones:
            bones_data.append((f, get_bones_matrix()))
        if bake_object:
            obj_data.append((f, get_obj_matrix()))

    # set new action
    action = bpy.data.actions.new("Action")
    anim_data = armature.animation_data_create()
    anim_data.action = action

    def store_keyframe(bone_name, prop_type, fc_array_index, frame, value):
        fc_data_path = 'pose.bones["' + bone_name + '"].' + prop_type
        fc_key = (fc_data_path, fc_array_index)
        if not keyframes.get(fc_key):
            keyframes[fc_key] = []
        keyframes[fc_key].extend((frame, value))


    # set transforms and store keyframes
    if bake_bones:
        for pbone in armature.pose.bones:
            if only_selected and not pbone.bone.select:
                continue

            euler_prev = None
            quat_prev = None
            keyframes = {}

            for (f, matrix) in bones_data:
                pbone.matrix_basis = matrix[pbone.name].copy()

                for arr_idx, value in enumerate(pbone.location):
                    store_keyframe(pbone.name, "location", arr_idx, f, value)

                rotation_mode = pbone.rotation_mode
                if rotation_mode == 'QUATERNION':
                    if quat_prev is not None:
                        quat = pbone.rotation_quaternion.copy()
                        quat.make_compatible(quat_prev)
                        pbone.rotation_quaternion = quat
                        quat_prev = quat
                        del quat
                    else:
                        quat_prev = pbone.rotation_quaternion.copy()

                    for arr_idx, value in enumerate(pbone.rotation_quaternion):
                        store_keyframe(pbone.name, "rotation_quaternion", arr_idx, f, value)

                elif rotation_mode == 'AXIS_ANGLE':
                    for arr_idx, value in enumerate(pbone.rotation_axis_angle):
                        store_keyframe(pbone.name, "rotation_axis_angle", arr_idx, f, value)

                else:  # euler, XYZ, ZXY etc
                    if euler_prev is not None:
                        euler = pbone.rotation_euler.copy()
                        euler.make_compatible(euler_prev)
                        pbone.rotation_euler = euler
                        euler_prev = euler
                        del euler
                    else:
                        euler_prev = pbone.rotation_euler.copy()

                    for arr_idx, value in enumerate(pbone.rotation_euler):
                        store_keyframe(pbone.name, "rotation_euler", arr_idx, f, value)

                for arr_idx, value in enumerate(pbone.scale):
                    store_keyframe(pbone.name, "scale", arr_idx, f, value)

            # Add keyframes
            for fc_key, key_values in keyframes.items():
                data_path, index = fc_key
                fcurve = action.fcurves.find(data_path=data_path, index=index)
                if fcurve == None:
                    fcurve = action.fcurves.new(data_path, index=index, action_group=pbone.name)

                num_keys = len(key_values) // 2
                fcurve.keyframe_points.add(num_keys)
                fcurve.keyframe_points.foreach_set('co', key_values)
                if bpy.app.version >= (2,90,0):# internal error when doing so with Blender 2.83, only for Blender 2.90 and higher
                    linear_enum_value = bpy.types.Keyframe.bl_rna.properties['interpolation'].enum_items['LINEAR'].value
                    fcurve.keyframe_points.foreach_set('interpolation', (linear_enum_value,) * num_keys)
                else:
                    for kf in fcurve.keyframe_points:
                        kf.interpolation = 'LINEAR'


    if bake_object:
        euler_prev = None
        quat_prev = None

        for (f, matrix) in obj_data:
            name = "Action Bake"
            armature.matrix_basis = matrix

            armature.keyframe_insert("location", index=-1, frame=f, group=name)

            rotation_mode = armature.rotation_mode
            if rotation_mode == 'QUATERNION':
                if quat_prev is not None:
                    quat = armature.rotation_quaternion.copy()
                    quat.make_compatible(quat_prev)
                    armature.rotation_quaternion = quat
                    quat_prev = quat
                    del quat
                else:
                    quat_prev = armature.rotation_quaternion.copy()
                armature.keyframe_insert("rotation_quaternion", index=-1, frame=f, group=name)
            elif rotation_mode == 'AXIS_ANGLE':
                armature.keyframe_insert("rotation_axis_angle", index=-1, frame=f, group=name)
            else:  # euler, XYZ, ZXY etc
                if euler_prev is not None:
                    euler = armature.rotation_euler.copy()
                    euler.make_compatible(euler_prev)
                    armature.rotation_euler = euler
                    euler_prev = euler
                    del euler
                else:
                    euler_prev = armature.rotation_euler.copy()
                armature.keyframe_insert("rotation_euler", index=-1, frame=f, group=name)

            armature.keyframe_insert("scale", index=-1, frame=f, group=name)


    # restore current frame
    scn.frame_set(current_frame)


def init_arp_scale(rig):
    if rig.scale == Vector((1.0, 1.0, 1.0)):
        return

    # init scale
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    # reset stretches
    bpy.ops.object.mode_set(mode='POSE')
    for pbone in bpy.context.active_object.pose.bones:
        if len(pbone.constraints):
            for cns in pbone.constraints:
                if cns.type != "STRETCH_TO":
                    continue
                cns.rest_length = 0.0


def find_primary_axis(bones_list):
    primary_axis = None
    for i, bname in enumerate(bones_list):
        ebone = get_edit_bone(bname)
        if ebone == None:
            continue
        if len(bones_list) == 1:# no children, cannot find automatically. Set default Y axis
            return "Y"
        if primary_axis == None:# find the primary axis
            child_idx = i+1
            child_ebone = get_edit_bone(bones_list[child_idx])
            dist_x = dist_y = dist_z = neg_dist_x = neg_dist_y = neg_dist_z = 0.0

            # test axes
            point_on_vec = ebone.head + ebone.x_axis.normalized()
            dist_x = (child_ebone.head - point_on_vec).magnitude
            point_on_vec = ebone.head - ebone.x_axis.normalized()
            neg_dist_x = (child_ebone.head - point_on_vec).magnitude
            point_on_vec = ebone.head + ebone.y_axis.normalized()
            dist_y = (child_ebone.head - point_on_vec).magnitude
            point_on_vec = ebone.head - ebone.y_axis.normalized()
            neg_dist_y = (child_ebone.head - point_on_vec).magnitude
            point_on_vec = ebone.head + ebone.z_axis.normalized()
            dist_z = (child_ebone.head - point_on_vec).magnitude
            point_on_vec = ebone.head - ebone.z_axis.normalized()
            neg_dist_z = (child_ebone.head - point_on_vec).magnitude

            shortest_dist = sorted([dist_x, neg_dist_x, dist_y, neg_dist_y, dist_z, neg_dist_z])[0]
            if shortest_dist == dist_x:
                primary_axis = "X"
            elif shortest_dist == neg_dist_x:
                primary_axis = "-X"
            elif shortest_dist == dist_y:
                primary_axis = "Y"
            elif shortest_dist == neg_dist_y:
                primary_axis = "-Y"
            elif shortest_dist == dist_z:
                primary_axis = "Z"
            elif shortest_dist == "-Z":
                primary_axis = "-Z"
            print("Primary Axis:", primary_axis)
            break

    if primary_axis == None:# should be a rare case, fallback to Y axis by default
        primary_axis = "Y"

    return primary_axis


def reverse_dict(dico):
    new_dict = {}
    if type(dico) != dict:# Blender 3.0
        dico = dico.to_dict()

    for entry in dico:
        keys = dico[entry]

        if 'deform' in keys:
            new_dict[keys['deform']] = entry
        else:#backward-compatibility
            new_dict[keys] = entry
    return new_dict


def _revert(self):
    arp_armature = get_object(bpy.context.active_object.name)
    data = None

    preserved = False
    if 'arp_locked' in arp_armature.data.keys():
        preserved = True


    if len(arp_armature.data.keys()):
        if "arp_qr_data" in arp_armature.data.keys():
            data = arp_armature.data["arp_qr_data"]

    if data == None:
        err_mess = "Could not find quick rig data, exit"
        print(err_mess)
        self.report({"ERROR"}, err_mess)
        return

    # reset all pose bone transforms
    bpy.ops.object.mode_set(mode='POSE')

    for pbone in arp_armature.pose.bones:
        pbone.location = [0,0,0]
        pbone.scale = [1,1,1]
        pbone.rotation_euler = [0,0,0]
        pbone.rotation_quaternion = [1,0,0,0]

    # show base armature
    base_armature_name = data["base_armature"]
    base_armature = get_object(base_armature_name)
    if base_armature == None:
        err_mess = "Base armature '"+base_armature_name+"' deleted, cannot revert"
        print(err_mess)
        self.report({"ERROR"}, err_mess)
        return

    base_armature.hide_set(False)

    skinned_objects_dict = data["skinned_objects"]
    if type(skinned_objects_dict) != dict:# Blender 3.0
        skinned_objects_dict = skinned_objects_dict.to_dict()

    meshes_parented_to_bones = data["meshes_parented_to_bones"]
    if type(meshes_parented_to_bones) != dict:# Bender 3.0
        meshes_parented_to_bones = meshes_parented_to_bones.to_dict()
        
    meshes_transf_dict = None
    
    if 'meshes_transf' in data.keys():# backward-compatibility
        meshes_transf_dict = data['meshes_transf']
        if type(meshes_transf_dict) != dict:# Blender 3.0
            meshes_transf_dict = meshes_transf_dict.to_dict()
        
    skin_dict = reverse_dict(data["vgroups"])

    # revert modifiers
    for m_name in skinned_objects_dict:
        obj = get_object(m_name)
        if obj == None:# may be deleted
            continue

        for mod in obj.modifiers:
            if mod.type != "ARMATURE":
                continue

            mod.object = base_armature


    # revert vgroups
    if not preserved:
        for m_name in skinned_objects_dict:
            obj = get_object(m_name)
            if obj == None:# may be deleted
                continue

            # revert weights
            if len(obj.vertex_groups):
                vertex_group_names_list = [vgroup.name for vgroup in obj.vertex_groups]

                for vgroup in obj.vertex_groups:
                    if vgroup.name in skin_dict:
                        try:
                            new_vgroup_name = skin_dict[vgroup.name]['deform']
                        except:#backward-compatibility
                            new_vgroup_name = skin_dict[vgroup.name]

                        # check if the vertex group name may already exist, avoid name clashing
                        # only if new name is different from base name

                        if new_vgroup_name != vgroup.name:
                            if new_vgroup_name in vertex_group_names_list and obj.vertex_groups.get(new_vgroup_name):
                                obj.vertex_groups[new_vgroup_name].name = new_vgroup_name+"_OLDGROUP"
                                skin_dict[new_vgroup_name+"_OLDGROUP"] = skin_dict[new_vgroup_name]
                                del skin_dict[new_vgroup_name]

                        # replace
                        vgroup.name = new_vgroup_name


            # revert drivers
            try:
                drivers_save = skinned_objects_dict[m_name]
            except:# backward-compatibility, skip
                continue

            for fc_dp in drivers_save:

                sk = obj.data.shape_keys
                if sk == None:
                    continue

                anim_data = obj.data.shape_keys.animation_data
                if anim_data == None:
                    continue

                drivers = anim_data.drivers
                if drivers == None:
                    continue

                fc = anim_data.drivers.find(fc_dp)
                if fc == None:
                    continue

                dr = fc.driver
                if dr:
                    var_dict = drivers_save[fc_dp]
                    for var_name in var_dict:
                        var = dr.variables.get(var_name)
                        if var:
                            ids = var_dict[var_name]['ids']
                            bone_targets = var_dict[var_name]['bone_targets']

                            for i, tar in enumerate(var.targets):
                                if len(ids):
                                    tar.id = get_object(ids[i])
                                if len(bone_targets):
                                    tar.bone_target = bone_targets[i]

                                      
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')

    set_active_object(base_armature_name)

    bpy.ops.object.mode_set(mode='POSE')

    # remove constraints
    for pbone in base_armature.pose.bones:
        if len(pbone.constraints):
            for cns in pbone.constraints:
                if cns.name.endswith('_QR'):
                    pbone.constraints.remove(cns)


    # meshes parented to bones
    self.meshes_parented_to_bones = meshes_parented_to_bones
   
    # meshes parented to armature
    _parent_meshes(self, arp_armature, base_armature)
    
    # revert meshes transforms
    if meshes_transf_dict:
        for m_name in meshes_transf_dict:
            obj = get_object(m_name)
            if obj == None:# may be deleted
                continue
                
            obj.location, obj.rotation_euler, obj.rotation_quaternion, obj.scale = meshes_transf_dict[m_name]
            print('Reverted mesh transforms', obj.name)


    # delete ARP armature
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    set_active_object(arp_armature.name)
    bpy.ops.arp.delete_arp()

    set_active_object(base_armature_name)
    bpy.ops.object.mode_set(mode='POSE')

    anim_temp = get_object(base_armature_name+'_ANIM_TEMP')
    if anim_temp:
        delete_object(anim_temp)

    print("Reverted.")


def _parent_meshes(self, current_arm, target_arm):

    # meshes parented to armature
    if len(current_arm.children):
        for obj_child in current_arm.children:
            if obj_child.type == "MESH" and not obj_child.name in self.meshes_parented_to_bones:
                mat = obj_child.matrix_world.copy()
                obj_child.parent = target_arm
                bpy.context.evaluated_depsgraph_get().update()
                obj_child.matrix_world = mat

    # meshes parented to bones (no skinning): set new bones parent
    current_arm.data.pose_position = 'REST'
    target_arm.data.pose_position = 'REST'

    for obj_name in self.meshes_parented_to_bones:
        obj = get_object(obj_name)

        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        set_active_object(obj_name)
        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

        original_parent_name = self.meshes_parented_to_bones[obj_name]
        new_parent_name = original_parent_name

        #if self.mode == 'CONVERT':
        if len(self.skin_dict):
            if original_parent_name in self.skin_dict:
                new_parent_name = self.skin_dict[original_parent_name]['deform']
        #else:
        #    new_parent_name = original_parent_name

        print("retarget bone parent", new_parent_name)
        obj.parent = target_arm
        obj.parent_type = 'BONE'
        obj.parent_bone = new_parent_name
        # bone parent use_relative option must be enabled now
        b = target_arm.data.bones.get(new_parent_name)
        b.use_relative_parent = False # doesn't work for now, disable it
        pb = target_arm.pose.bones.get(new_parent_name)
        trans = Matrix.Translation(pb.head - pb.tail)# we need to substract the bone vector, the tail position is used by default intead of head
        obj.matrix_parent_inverse = (pb.matrix.inverted() @ trans) @ target_arm.matrix_world.inverted()

    current_arm.data.pose_position = 'POSE'
    target_arm.data.pose_position = 'POSE'

    if len(self.meshes_parented_to_bones):
        bpy.ops.object.select_all(action='DESELECT')
        set_active_object(target_arm.name)
        bpy.ops.object.mode_set(mode='POSE')


def set_childof_inverse(self):
    # Set inverse matrix of Child Of constraints in hierarchy order

    #  get ChildOf constraints bones parent
    parent_dict = {}
    childof_vgroup = []

    for or_name in self.orphan_bones_dict:
        orphan_pbone = get_pose_bone(or_name)
        if orphan_pbone == None:
            continue

        for cns in orphan_pbone.constraints:
            if cns.type == 'CHILD_OF':
                if cns.target:
                    if cns.target.type == "ARMATURE" and cns.subtarget != '':
                        parent_dict[or_name] = cns.subtarget

                    elif cns.target.type == "MESH" and cns.subtarget != '':
                        childof_vgroup.append([or_name, cns.name])


    #  sort by hierarchy
    sorted_hierarchy = []

    #  get root nodes
    roots = []

    for child_name in parent_dict:
        parent_name = parent_dict[child_name]
        if not parent_name in parent_dict:
            roots.append(child_name)

    #print("roots:", roots)
    #print("parent_dict", parent_dict)

    def find_children(name, sorted_hierarchy):
        for i, j in parent_dict.items():
            if j == name:
                sorted_hierarchy.append(i)
                find_children(i, sorted_hierarchy)

    #    sort
    for root_name in roots:
        sorted_hierarchy.append(root_name)
        find_children(root_name, sorted_hierarchy)

    #print('sorted_hierarchy', sorted_hierarchy)

    # Set inverse matrices
    #   child of bone
    for or_name in sorted_hierarchy:
        orphan_pbone = get_pose_bone(or_name)

        if orphan_pbone == None:
            continue

        for cns in orphan_pbone.constraints:
            if cns.type == 'CHILD_OF':
                set_constraint_inverse_matrix(cns, orphan_pbone)

    #   child of vgroup
    for i in childof_vgroup:
        or_name, cns_name = i[0], i[1]
        orphan_pbone = get_pose_bone(or_name)

        if orphan_pbone == None:
            continue

        cns = orphan_pbone.constraints.get(cns_name)
        set_constraint_inverse_matrix(cns, orphan_pbone)


def _remap_animation(self):

    if self.source_anim_rig_name == '':# no animation to remap
        return

    print("\nRemapping animation...")
    print("  Building bones list...")
    scn = bpy.context.scene

    scn.source_rig = self.source_anim_rig_name

    source_rig = get_object(self.source_anim_rig_name)
    scn.source_action = source_rig.animation_data.action.name
    scn.target_rig = self.arp_armature_name
    target_rig = get_object(scn.target_rig)

    
    if len(scn.remap_source_nodes):
        i = len(scn.remap_source_nodes)
        while i >= 0:
            scn.remap_source_nodes.remove(i)
            i -= 1
            
    for b in source_rig.data.bones:
        item = scn.remap_source_nodes.add()
        item.source_name = b.name

        
    # setup the remap bones list
    #   clear current list
    if len(scn.bones_map_v2):
        i = len(scn.bones_map_v2)
        while i >= 0:
            scn.bones_map_v2.remove(i)
            i -= 1

    remap_dict = {}

    scn.bones_map_index = -1

    for limb in scn.limb_map:
        dupli_idx = limb.dupli_idx

        if limb.type == 'SPINE':
            for i in range(1,8):
                source_name = limb.get('bone_0'+str(i))

                if source_name != '' and source_name != None:
                    item = scn.bones_map_v2.add()
                    scn.bones_map_index += 1
                    item.name = 'c_root_master'+dupli_idx+'.x' if i == 1 else 'c_spine_0'+str(i-1)+dupli_idx+'.x'
                    item.source_bone = source_name

                    if i == 1:
                        item.set_as_root = True
                    else:
                        item.location = True


        elif limb.type == 'HEAD':
            # neck
            if limb.neck_bones_amount == 1:
                if limb.bone_01 != '' and limb.bone_01 != None:
                    source_name = limb.bone_01
                    target_name = 'c_neck'+dupli_idx+'.x'
                    item = scn.bones_map_v2.add()
                    scn.bones_map_index += 1
                    item.name = target_name
                    item.source_bone = source_name

            else:
                # subnecks
                neck_list = ['bone_01', 'bone_04', 'neck3', 'neck4', 'neck5', 'neck6', 'neck7', 'neck8', 'neck9', 'neck10']

                for i in range(1, limb.neck_bones_amount):
                    n = neck_list[i-1]
                    if limb.get(n) != '' and limb.get(n) != None:
                        source_name = limb.get(n)
                        target_name = 'c_subneck_'+str(i)+dupli_idx+'.x'
                        item = scn.bones_map_v2.add()
                        scn.bones_map_index += 1
                        item.name = target_name
                        item.source_bone = source_name

                # neck
                print(neck_list[limb.neck_bones_amount-1])
                source_name = limb.get(neck_list[limb.neck_bones_amount-1])
                target_name = 'c_neck'+dupli_idx+'.x'
                item = scn.bones_map_v2.add()
                scn.bones_map_index += 1
                item.name = target_name
                item.source_bone = source_name


            # head
            source_name = limb.bone_02
            target_name = 'c_head'+dupli_idx+'.x'
            item = scn.bones_map_v2.add()
            scn.bones_map_index += 1
            item.name = target_name
            item.source_bone = source_name


        elif limb.type == 'LEG':
            side = '.l'
            if limb.side == 'RIGHT':
                side = '.r'

            if limb.leg_type == '3':
                source_name = limb.upper_thigh
                target_name = 'c_thigh_b'+dupli_idx+side
                item = scn.bones_map_v2.add()
                scn.bones_map_index += 1
                item.name = target_name
                item.source_bone = source_name


            if self.leg_ik_fk == 'IK':

                #   foot
                source_name = limb.bone_05
                target_name = 'c_foot_ik'+dupli_idx+side
                item = scn.bones_map_v2.add()
                scn.bones_map_index += 1
                item.name = target_name
                item.source_bone = source_name
                item.ik = True
                item.ik_pole = 'c_leg_pole'+dupli_idx+side
                item.ik_auto_pole = 'RELATIVE_CHAIN'

                #   thigh and calf
                item.ik_1 = limb.bone_01
                item.ik_2 = limb.bone_03

                #   toes
                if limb.bone_06 != '' and limb.bone_06 != None:
                    source_name = limb.bone_06
                    target_name = 'c_toes_ik'+dupli_idx+side
                    item = scn.bones_map_v2.add()
                    scn.bones_map_index += 1
                    item.name = target_name
                    item.source_bone = source_name
            else:
                #   foot
                source_name = limb.bone_05
                target_name = 'c_foot_fk'+dupli_idx+side
                item = scn.bones_map_v2.add()
                scn.bones_map_index += 1
                item.name = target_name
                item.source_bone = source_name

                # thigh
                source_name = limb.bone_01
                target_name = 'c_thigh_fk'+dupli_idx+side
                item = scn.bones_map_v2.add()
                scn.bones_map_index += 1
                item.name = target_name
                item.source_bone = source_name

                # calf
                source_name = limb.bone_03
                target_name = 'c_leg_fk'+dupli_idx+side
                item = scn.bones_map_v2.add()
                scn.bones_map_index += 1
                item.name = target_name
                item.source_bone = source_name

                # toes
                if limb.bone_06 != '' and limb.bone_06 != None:
                    source_name = limb.bone_06
                    target_name = 'c_toes_fk'+dupli_idx+side
                    item = scn.bones_map_v2.add()
                    scn.bones_map_index += 1
                    item.name = target_name
                    item.source_bone = source_name


        elif limb.type == 'ARM':
            side = '.l'
            if limb.side == 'RIGHT':
                side = '.r'

            # shoulder
            item = scn.bones_map_v2.add()
            scn.bones_map_index += 1
            item.name = 'c_shoulder'+dupli_idx+side
            item.source_bone = limb.bone_01
            item.location = True

            if self.arm_ik_fk == 'IK':
                # hand
                source_name = limb.bone_06
                target_name = 'c_hand_ik'+dupli_idx+side
                item = scn.bones_map_v2.add()
                scn.bones_map_index += 1
                item.name = target_name
                item.source_bone = source_name
                item.ik = True
                item.ik_pole = 'c_arms_pole'+dupli_idx+side
                item.ik_auto_pole = 'RELATIVE_CHAIN'

                # arm and forearm
                item.ik_1 = limb.bone_02
                item.ik_2 = limb.bone_04

            else:
                # hand
                source_name = limb.bone_06
                target_name = 'c_hand_fk'+dupli_idx+side
                item = scn.bones_map_v2.add()
                scn.bones_map_index += 1
                item.name = target_name
                item.source_bone = source_name

                # arm
                source_name = limb.bone_02
                target_name = 'c_arm_fk'+dupli_idx+side
                item = scn.bones_map_v2.add()
                scn.bones_map_index += 1
                item.name = target_name
                item.source_bone = source_name

                # forearm
                source_name = limb.bone_04
                target_name = 'c_forearm_fk'+dupli_idx+side
                item = scn.bones_map_v2.add()
                scn.bones_map_index += 1
                item.name = target_name
                item.source_bone = source_name

    

    # Fingers
    for bname in self.fingers_ctrl:
        source_name = bname
        #side = get_bone_side(bname)
        target_name = self.fingers_ctrl[bname]
        item = scn.bones_map_v2.add()
        scn.bones_map_index += 1
        item.name = target_name
        item.source_bone = source_name
        
    # Toes
    for bname in self.toes_ctrl:
        source_name = bname
        #side = get_bone_side(bname)
        target_name = self.toes_ctrl[bname]
        item = scn.bones_map_v2.add()
        scn.bones_map_index += 1
        item.name = target_name
        item.source_bone = source_name
        
        
    # Tails
    for bname in self.tail_ctrl:
        source_name = bname
        #side = get_bone_side(bname)
        target_name = self.tail_ctrl[bname]
        item = scn.bones_map_v2.add()
        scn.bones_map_index += 1
        item.name = target_name
        item.source_bone = source_name

    # orphans
    for b in target_rig.data.bones:
        if 'cc' in b.keys():
            source_name = b.name
            target_name = b.name
            item = scn.bones_map_v2.add()
            scn.bones_map_index += 1
            item.name = target_name
            item.source_bone = source_name
            item.location = True if self.orphan_bones_loc_retarget == 'LOCAL' else False
            item.ik = True if self.orphan_bones_loc_retarget == 'IK' else False

    if self.animation == 'ANIM_BAKE':        
        act = source_rig.animation_data.action
        bpy.ops.arp.retarget(frame_start=int(act.frame_range[0]), frame_end=int(act.frame_range[1]))
        scn.source_rig = ''
        scn.target_rig = ''
        delete_object(source_rig)

    elif self.animation == 'ANIM_BIND':
        bpy.ops.arp.retarget_bind_only(unbind=False)
        scn.arp_retarget_decoupled_expand_ui = True

    print("Animation remapped")


def _make_rig(self):
    scn = bpy.context.scene
    source_skeleton = get_object(bpy.context.active_object.name)
    source_anim_rig = get_object(self.source_anim_rig_name)

    ref_bones_fingers_3 = {"thumb":["thumb1_ref", "thumb2_ref", "thumb3_ref"], "index":["index1_ref", "index2_ref", "index3_ref"], "middle":["middle1_ref", "middle2_ref", "middle3_ref"], "ring":["ring1_ref", "ring2_ref", "ring3_ref"], "pinky":["pinky1_ref", "pinky2_ref", "pinky3_ref"]}

    ref_bones_fingers_4 = {"thumb":["thumb1_ref", "thumb2_ref", "thumb3_ref"], "index":["index1_base_ref", "index1_ref", "index2_ref", "index3_ref"], "middle":["middle1_base_ref", "middle1_ref", "middle2_ref", "middle3_ref"], "ring":["ring1_base_ref", "ring1_ref", "ring2_ref", "ring3_ref"], "pinky":["pinky1_base_ref","pinky1_ref", "pinky2_ref", "pinky3_ref"]}
    
    ref_bones_toes_3 = {"thumb":["toes_thumb1_ref", "toes_thumb2_ref"], "index":["toes_index1_ref", "toes_index2_ref", "toes_index3_ref"], "middle":["toes_middle1_ref", "toes_middle2_ref", "toes_middle3_ref"], "ring":["toes_ring1_ref", "toes_ring2_ref", "toes_ring3_ref"], "pinky":["toes_pinky1_ref", "toes_pinky2_ref", "toes_pinky3_ref"]}

    ref_bones_toes_4 = {"thumb":["toes_thumb1_base_ref", "toes_thumb1_ref", "toes_thumb2_ref"], "index":["toes_index1_base_ref", "toes_index1_ref", "toes_index2_ref", "index3_ref"], "middle":["toes_middle1_base_ref", "toes_middle1_ref", "toes_middle2_ref", "toes_middle3_ref"], "ring":["toes_ring1_base_ref", "toes_ring1_ref", "toes_ring2_ref", "toes_ring3_ref"], "pinky":["toes_pinky1_base_ref","toes_pinky1_ref", "toes_pinky2_ref", "toes_pinky3_ref"]}


    # zero out base armature location
    if self.match_origin:
        bpy.ops.object.mode_set(mode='OBJECT')
        arm_rot_euler, arm_rot_quat, arm_scale = source_skeleton.rotation_euler.copy(), source_skeleton.rotation_quaternion.copy(), source_skeleton.scale.copy()
        source_skeleton.matrix_world = Matrix()
        source_skeleton.rotation_euler, source_skeleton.rotation_quaternion, source_skeleton.scale = arm_rot_euler, arm_rot_quat, arm_scale

        bpy.context.evaluated_depsgraph_get().update()


    bpy.ops.object.mode_set(mode='POSE')


    # reset all pose bone transforms
    for pbone in source_skeleton.pose.bones:
        pbone.location = [0,0,0]
        pbone.scale = [1,1,1]
        pbone.rotation_euler = [0,0,0]
        pbone.rotation_quaternion = [1,0,0,0]


    arm_mat = source_skeleton.matrix_world.copy()
    mat_loc = arm_mat.to_translation()
    mat_rot = arm_mat.to_quaternion()
    arm_mat_no_scale = Matrix.Translation(Vector((0,0,0))) @ mat_rot.to_matrix().to_4x4()
    arm_mat_inv = arm_mat.inverted()
    arm_mat_no_scale_inv = arm_mat_no_scale
    arm_mat_rot = mat_rot.to_matrix().to_4x4()
    arm_mat2 = arm_mat.copy()# just use a copy for quick search and replace


    bpy.ops.object.mode_set(mode='EDIT')


    # make a list of orphan bones (additional bones that are not supported in the limbs definition)
    # store all then substract later
    orphan_bones = [b.name for b in source_skeleton.data.edit_bones]

    # store bones data
    limbs_coords = {}
    # store deform bones for skinning
    skin_dict = {}# skin_dict[base_bone_name] = {'deform':arp_deform_bone, 'head':base_bone_head, 'tail'...}

    if len(scn.limb_map) == 0:
        error_message = "Add limbs first"
        self.report({"ERROR"}, error_message)
        return

    # meshes object parented to bones support (no skinning): store meshes
    for obj in bpy.data.objects:
        if (obj.type != 'MESH' and obj.type != "EMPTY") or is_object_hidden(obj):
            continue

        if obj.parent:
            if obj.parent == source_skeleton and obj.parent_type == "BONE":
                if obj.parent_bone != "":
                    self.meshes_parented_to_bones[obj.name] = obj.parent_bone

    # Store limbs data
    #   multi-limb support
    leg_limb_count_left = 0
    leg_limb_count_right = 0
    
    arm_limb_count_left = 0
    arm_limb_count_right = 0
    
    tail_limb_count_left = 0
    tail_limb_count_right = 0
    tail_limb_count_mid = 0


    def get_bone_coords(bone_name):
        ebone = get_edit_bone(bone_name)
        if ebone == None:
            return None

        coords = [arm_mat @ ebone.head, arm_mat @ ebone.tail, (arm_mat_rot @ ebone.x_axis).normalized()]

        return coords


    for limb_idx in range(0, len(scn.limb_map)):
        limb = scn.limb_map[limb_idx]
        bones_coords = {}

        # dict to store source and target (ref) bones data matches:
        # bones_coords[reference_bone_name] = {}

        if limb.type == 'LEG':
            side = '.l' if limb.side == 'LEFT' else '.r'

            ref_bones_leg = ['thigh_ref', 'leg_ref', 'foot_ref', 'toes_ref']

            if limb.leg_type == "3":
                ref_bones_leg.insert(0, "thigh_b_ref")
            
            limb.toes_parent_foot = False

            # multi limb support
            if side == ".l":
                leg_limb_count_left += 1
                leg_limb_count = leg_limb_count_left
            elif side == ".r":
                leg_limb_count_right += 1
                leg_limb_count = leg_limb_count_right

            dupli_id = ""

            if leg_limb_count > 1:
                ref_bones_leg_dupli = []
                dupli_id = '{:03d}'.format(leg_limb_count-1)
                dupli_id = "_dupli_"+str(dupli_id)

                for ref_bone_name in ref_bones_leg:
                    ref_bone_name_dupli = ref_bone_name+dupli_id
                    ref_bones_leg_dupli.append(ref_bone_name_dupli)

                ref_bones_leg = ref_bones_leg_dupli

                print("Stored dupli leg side", side, ":", ref_bones_leg)

            upthigh_name = limb.upper_thigh
            thigh_name = limb.bone_01
            thigh_twist_name = limb.bone_02#optional
            calf_name = limb.bone_03
            calf_twist = limb.bone_04#optional
            foot_name = limb.bone_05
            toes_name = limb.bone_06
            toes_end_name = limb.bone_07#optional

            # skinning matches
            if limb.leg_type == "3":
                if limb.weights_override and limb.override_upper_thigh != "":
                    skin_dict[limb.override_upper_thigh] = {"deform":"c_thigh_b"+dupli_id+side, 'coords':get_bone_coords(limb.override_upper_thigh)}
                else:
                    skin_dict[upthigh_name] = {'deform':"c_thigh_b"+dupli_id+side, 'coords':get_bone_coords(upthigh_name)}

            if limb.weights_override and limb.override_bone_01 != "":
                skin_dict[limb.override_bone_01] = {'deform':"thigh_stretch"+dupli_id+side, 'coords':get_bone_coords(limb.override_bone_01)}
            else:
                skin_dict[thigh_name] = {'deform':"thigh_stretch"+dupli_id+side, 'coords':get_bone_coords(thigh_name)}

            if limb.weights_override and limb.override_bone_02 != "":
                skin_dict[limb.override_bone_02] = {'deform':"thigh_twist"+dupli_id+side, 'coords':get_bone_coords(limb.override_bone_02)}
            else:
                skin_dict[thigh_twist_name] = {'deform':"thigh_twist"+dupli_id+side, 'coords':get_bone_coords(thigh_twist_name)}

            if limb.weights_override and limb.override_bone_03 != "":
                skin_dict[limb.override_bone_03] = {'deform':"leg_stretch"+dupli_id+side, 'coords':get_bone_coords(limb.override_bone_03)}
            else:
                skin_dict[calf_name] = {'deform':"leg_stretch"+dupli_id+side, 'coords':get_bone_coords(calf_name)}

            if limb.weights_override and limb.override_bone_04 != "":
                skin_dict[limb.override_bone_04] = {'deform':"leg_twist"+dupli_id+side, 'coords':get_bone_coords(limb.override_bone_04)}
            else:
                skin_dict[calf_twist] = {'deform':"leg_twist"+dupli_id+side, 'coords':get_bone_coords(calf_twist)}

            if limb.weights_override and limb.override_bone_05 != "":
                skin_dict[limb.override_bone_05] = {'deform':"foot"+dupli_id+side, 'coords':get_bone_coords(limb.override_bone_05)}
            else:
                skin_dict[foot_name] = {'deform':"foot"+dupli_id+side, 'coords':get_bone_coords(foot_name)}

            if limb.weights_override and limb.override_bone_06 != "":
                skin_dict[limb.override_bone_06] = {'deform':"toes_01"+dupli_id+side, 'coords':get_bone_coords(limb.override_bone_06)}
            else:
                skin_dict[toes_name] = {'deform':"toes_01"+dupli_id+side, 'coords':get_bone_coords(toes_name)}

            #     additional twists
            if limb.twist_bones_amount >= 2:
                for i in range(2, limb.twist_bones_amount+1):
                    id = '%02d' % (i)
                    twist_1_name = 'bone_twist_'+id+'_01'
                    twist_1_src_name = limb.get(twist_1_name)
                    if twist_1_src_name != '':
                        if get_edit_bone(twist_1_src_name):
                            skin_dict[twist_1_src_name] = {'deform':'thigh_twist_'+str(i)+dupli_id+side, 'coords':get_bone_coords(twist_1_src_name)}
                    twist_2_name = 'bone_twist_'+id+'_02'
                    twist_2_src_name = limb.get(twist_2_name)
                    if twist_2_src_name != '':
                        if get_edit_bone(twist_2_src_name):
                            skin_dict[twist_2_src_name] = {'deform':'leg_twist_'+str(i)+dupli_id+side, 'coords':get_bone_coords(twist_2_src_name)}
                    

            leg_names = [thigh_name, calf_name, foot_name, toes_name]
            if limb.leg_type == "3":
                leg_names.insert(0, upthigh_name)

            for i, bname in enumerate(leg_names):
                ebone = get_edit_bone(bname)

                if ebone == None:# toes are optional
                    continue

                bone_tail = ebone.tail.copy()
                if bname == toes_name:# get the toes_end if any
                    if toes_end_name != "":
                        bone_tail = get_edit_bone(toes_end_name).head.copy()
                parent_name = "" if ebone.parent == None else ebone.parent.name
                if parent_name.startswith("c_thigh_b"):# exception, third leg bone. Get the top parent instead
                    if ebone.parent.parent:
                        parent_name = "" if ebone.parent.parent == None else ebone.parent.parent.name

                bones_coords[ref_bones_leg[i]] = {'head':arm_mat @ ebone.head.copy(), 'tail':arm_mat @ bone_tail, 
                    'x_axis':(arm_mat_rot @ ebone.x_axis).normalized(), 'y_axis':(arm_mat_rot @ ebone.y_axis).normalized(), 'z_axis':(arm_mat_rot @ ebone.z_axis).normalized(), 
                    'name':ebone.name, 'parent_name':parent_name}# store bone data
                
            
            # Toes fingers
            fingers_names = {'thumb':[], 'index':[], 'middle':[], 'ring':[], 'pinky':[]}

            if limb.fingers != 'NONE':
                ref_bones_fingers = {}

                if limb.fingers == "3":
                    ref_bones_fingers = ref_bones_toes_3.copy()
                elif limb.fingers == "4":
                    ref_bones_fingers = ref_bones_toes_4.copy()

                for finger_type in ref_bones_fingers:
                    current_list = ref_bones_fingers[finger_type].copy()
                    new_list = []
                    for ref_name in current_list:
                        new_list.append(ref_name+dupli_id)

                    ref_bones_fingers[finger_type] = new_list

                base_fingers_names = {"thumb":limb.thumb, "index":limb.index, "middle":limb.middle, "ring":limb.ring, "pinky":limb.pinky}

                if limb.manual_phalanges:# manual phalanges as set in the list
                    for finger_type in base_fingers_names:
                        phalange1 = get_edit_bone(base_fingers_names[finger_type])
                        if phalange1:
                            fingers_names[finger_type].append(phalange1.name)
                        
                        phal2_name = limb.get(finger_type+'2')
                        if limb.fingers == '4':
                            if finger_type != 'thumb':
                                phal2_name = limb.get(finger_type+'1')
                        if phal2_name:
                            phalange2 = get_edit_bone(phal2_name)
                            if phalange2:
                                fingers_names[finger_type].append(phalange2.name)
                        
                        phal3_name = ''
                        if (finger_type != 'thumb' and limb.fingers == '3'):# only 2 thumb phalanges
                            phal3_name = limb.get(finger_type+'3')
                        
                        if limb.fingers == '4':
                            if finger_type == 'thumb':
                                phal3_name = limb.get(finger_type+'3')
                            else:
                                phal3_name = limb.get(finger_type+'2')
                                
                        if phal3_name:
                            phalange3 = get_edit_bone(phal3_name)
                            if phalange3:
                                fingers_names[finger_type].append(phalange3.name)
                        
                        if limb.fingers == "4" and finger_type != 'thumb':# the thumb has only 3 phalanges including metacarp
                            phal4_name = limb.get(finger_type+'3')
                            if phal4_name:
                                phalange4 = get_edit_bone(phal4_name)
                                if phalange4:
                                    fingers_names[finger_type].append(phalange4.name)
                            
                else:# automatic phalange, find children
                    for finger_type in base_fingers_names:
                        phalange1 = phalange2 = phalange3 = phalange4 = None
                        finger_bone_name = base_fingers_names[finger_type]
                        phalange1 = get_edit_bone(finger_bone_name)
                        
                        if phalange1:
                            fingers_names[finger_type].append(phalange1.name)
                            if phalange1.children:
                                phalange2 = phalange1.children[0]
                                fingers_names[finger_type].append(phalange2.name)
                                if phalange2.children and (finger_type != 'thumb' or limb.fingers == '4'):
                                    phalange3 = phalange2.children[0]
                                    fingers_names[finger_type].append(phalange3.name)
                                    # 3 or 4 finger bones support
                                    if limb.fingers == "4" and finger_type != "thumb" != 0:# the thumb has only 3 phalanges including metacarp
                                        if phalange3.children:
                                            phalange4 = phalange3.children[0]
                                            fingers_names[finger_type].append(phalange4.name)


                # Check if the total fingers amount is correct. If not, skip
                valid_list = True
                expected_finger_count = 0
                for fidx, fname in enumerate((limb.thumb, limb.index, limb.middle, limb.ring, limb.pinky)):
                    if fname != "":
                        if fidx == 0:#thumb
                            expected_finger_count += 2 if limb.fingers == '3' else 3
                        else:
                            expected_finger_count += 4 if limb.fingers == "4" else 3

                phalanges_count = 0
                for finger_type in fingers_names:
                    phalanges_count += len(fingers_names[finger_type])

                if phalanges_count != expected_finger_count:
                    print("Error, found", len(fingers_names), "toes. Should have found", expected_finger_count)
                    print("Cannot setup toes, set to None")
                    valid_list = False
                    limb.fingers = "NONE"# set fingers to None

                if valid_list:
                    # skinning matches
                    for finger_type in fingers_names:
                        phalange1_name = phalange2_name = phalange3_name = phalange4_name = None

                        phal_list = fingers_names[finger_type]
                        if len(phal_list) >= 1:
                            phalange1_name = phal_list[0]
                        if len(phal_list) >= 2:
                            phalange2_name = phal_list[1]
                        if len(phal_list) >= 3:
                            phalange3_name = phal_list[2]
                        if len(phal_list) >= 4:
                            phalange4_name = phal_list[3]


                        def add_finger_deforming_match_3(finger_type):
                            if phalange1_name:
                                skin_dict[phalange1_name] = {'deform':'c_toes_'+finger_type+"1"+dupli_id+side, 'coords':get_bone_coords(phalange1_name)}
                            if phalange2_name:
                                skin_dict[phalange2_name] = {'deform':"c_toes_"+finger_type+"2"+dupli_id+side, 'coords':get_bone_coords(phalange2_name)}
                            if phalange3_name:
                                skin_dict[phalange3_name] = {'deform':"c_toes_"+finger_type+"3"+dupli_id+side, 'coords':get_bone_coords(phalange3_name)}

                        def add_finger_deforming_match_4(finger_type):
                            if phalange1_name:
                                skin_dict[phalange1_name] = {'deform':'c_toes_'+finger_type+'1_base'+dupli_id+side, 'coords':get_bone_coords(phalange1_name)}
                            if phalange2_name:
                                skin_dict[phalange2_name] = {'deform':'c_toes_'+finger_type+'1'+dupli_id+side, 'coords':get_bone_coords(phalange2_name)}
                            if phalange3_name:
                                skin_dict[phalange3_name] = {'deform':'c_toes_'+finger_type+'2'+dupli_id+side, 'coords':get_bone_coords(phalange3_name)}
                            if phalange4_name:
                                skin_dict[phalange4_name] = {'deform':'c_toes_'+finger_type+'3'+dupli_id+side, 'coords':get_bone_coords(phalange4_name)}

                        if phalange1_name:
                            if limb.fingers == "3":
                                add_finger_deforming_match_3(finger_type)

                            elif limb.fingers == "4":
                                #if finger_type == "thumb":
                                #    add_finger_deforming_match_3(finger_type)
                                #else:
                                add_finger_deforming_match_4(finger_type)

                        # remove fingers orphan bones from list
                        for f in [phalange1_name, phalange2_name, phalange3_name, phalange4_name]:
                            if f:
                                if f in orphan_bones:
                                    orphan_bones.remove(f)

                    # store finger bone data
                    for finger_type in fingers_names:
                        phal_list = fingers_names[finger_type]
                        for i, phal_name in enumerate(phal_list):
                            finger_bone = get_edit_bone(phal_name)
                            finger_ref_name = ref_bones_fingers[finger_type][i]
                            bones_coords[finger_ref_name] = {'head':arm_mat @ finger_bone.head.copy(), 'tail':arm_mat @ finger_bone.tail.copy(), 
                                'x_axis':(arm_mat_rot @ finger_bone.x_axis).normalized(), 'y_axis':(arm_mat_rot @ finger_bone.y_axis).normalized(), 
                                'z_axis':(arm_mat_rot @ finger_bone.z_axis).normalized(), 
                                'name':finger_bone.name}# store bone data
                                
                            c_toes_name = 'c_toes_'+finger_ref_name.replace('_ref', '')+side
                            self.toes_ctrl[finger_bone.name] = c_toes_name                            
                            
                            # Toes parented to foot?
                            if i == 0 and finger_bone.parent:
                                if finger_bone.parent.name == foot_name:
                                    limb.toes_parent_foot = True
                            
                            #print("SAVE TOES", finger_bone.name, c_toes_name)
                            #print('c_'+finger_ref_name.replace('_ref', '')+dupli_id+side)
        
        elif limb.type == "ARM":
            side = '.l' if limb.side == 'LEFT' else '.r'
            ref_bones_arm = ["shoulder_ref", "arm_ref", "forearm_ref", "hand_ref"]

            # multi limb support
            if side == ".l":
                arm_limb_count_left += 1
                arm_limb_count = arm_limb_count_left
            elif side == ".r":
                arm_limb_count_right += 1
                arm_limb_count = arm_limb_count_right

            dupli_id = ""
            if arm_limb_count > 1:
                ref_bones_arm_dupli = []
                dupli_id = '{:03d}'.format(arm_limb_count-1)
                dupli_id = "_dupli_"+str(dupli_id)
                for ref_bone_name in ref_bones_arm:
                    ref_bone_name_dupli = ref_bone_name+dupli_id
                    ref_bones_arm_dupli.append(ref_bone_name_dupli)
                ref_bones_arm = ref_bones_arm_dupli
                print("Stored dupli arm side", side, ":", ref_bones_arm)

            shoulder_name = limb.bone_01
            arm_name = limb.bone_02
            arm_twist_name = limb.bone_03
            forearm_name = limb.bone_04
            forearm_twist_name = limb.bone_05
            hand_name = limb.bone_06

            arm_limb_count += 1

            # skinning matches
            if limb.weights_override and limb.override_bone_01 != "":
                skin_dict[limb.override_bone_01] = {'deform':"shoulder"+dupli_id+side, 'coords':get_bone_coords(limb.override_bone_01)}
            else:
                skin_dict[shoulder_name] = {'deform':"shoulder"+dupli_id+side, 'coords':get_bone_coords(shoulder_name)}
            if limb.weights_override and limb.override_bone_02 != "":
                skin_dict[limb.override_bone_02] = {'deform':"arm_stretch"+dupli_id+side, 'coords':get_bone_coords(limb.override_bone_02)}
            else:
                skin_dict[arm_name] = {'deform':"arm_stretch"+dupli_id+side, 'coords':get_bone_coords(arm_name)}
            if limb.weights_override and limb.override_bone_03 != "":
                skin_dict[limb.override_bone_03] = {'deform':"c_arm_twist_offset"+dupli_id+side, 'coords':get_bone_coords(limb.override_bone_03)}
            else:
                skin_dict[arm_twist_name] = {'deform':"c_arm_twist_offset"+dupli_id+side, 'coords':get_bone_coords(arm_twist_name)}
            if limb.weights_override and limb.override_bone_04 != "":
                skin_dict[limb.override_bone_04] = {'deform':"forearm_stretch"+dupli_id+side, 'coords':get_bone_coords(limb.override_bone_04)}
            else:
                skin_dict[forearm_name] = {'deform':"forearm_stretch"+dupli_id+side, 'coords':get_bone_coords(forearm_name)}
            if limb.weights_override and limb.override_bone_05 != "":
                skin_dict[limb.override_bone_05] = {'deform':"forearm_twist"+dupli_id+side, 'coords':get_bone_coords(limb.override_bone_05)}
            else:
                skin_dict[forearm_twist_name] = {'deform':"forearm_twist"+dupli_id+side, 'coords':get_bone_coords(forearm_twist_name)}
            if limb.weights_override and limb.override_bone_06 != "":
                skin_dict[limb.override_bone_06] = {'deform':"hand"+dupli_id+side, 'coords':get_bone_coords(limb.override_bone_06)}
            else:
                skin_dict[hand_name] = {'deform':"hand"+dupli_id+side, 'coords':get_bone_coords(hand_name)}
                
            #     additional twists
            if limb.twist_bones_amount >= 2:
                for i in range(2, limb.twist_bones_amount+1):
                    id = '%02d' % (i)
                    twist_1_name = 'bone_twist_'+id+'_01'
                    twist_1_src_name = limb.get(twist_1_name)
                    if twist_1_src_name != '':
                        skin_dict[twist_1_src_name] = {'deform':'arm_twist_'+str(i)+dupli_id+side, 'coords':get_bone_coords(twist_1_src_name)}
                    twist_2_name = 'bone_twist_'+id+'_02'
                    twist_2_src_name = limb.get(twist_2_name)
                    if twist_2_src_name != '':
                        skin_dict[twist_2_src_name] = {'deform':'forearm_twist_'+str(i)+dupli_id+side, 'coords':get_bone_coords(twist_2_src_name)}
                        

            bones_arm_list = [shoulder_name, arm_name, forearm_name, hand_name]
            if limb.primary_axis_auto:
                limb.primary_axis = find_primary_axis(bones_arm_list)

            for i, bname in enumerate(bones_arm_list):
                ebone = get_edit_bone(bname)

                if ebone == None:# shoulder is optional
                    continue

                parent_name = "" if ebone.parent == None else ebone.parent.name
                bones_coords[ref_bones_arm[i]] = {'head':arm_mat @ ebone.head.copy(), 'tail':arm_mat @ ebone.tail.copy(), 
                                            'x_axis':(arm_mat_rot @ ebone.x_axis).normalized(), 'y_axis':(arm_mat_rot @ ebone.y_axis).normalized(), 
                                            'z_axis':(arm_mat_rot @ ebone.z_axis).normalized(), 
                                            'name':ebone.name, 'parent_name':parent_name}# store bone data

            fingers_names = {"thumb":[], "index":[], "middle":[], "ring":[], "pinky":[]}

            if limb.fingers != "NONE":
                ref_bones_fingers = {}

                if limb.fingers == "3":
                    ref_bones_fingers = ref_bones_fingers_3.copy()
                elif limb.fingers == "4":
                    ref_bones_fingers = ref_bones_fingers_4.copy()

                for finger_type in ref_bones_fingers:
                    current_list = ref_bones_fingers[finger_type].copy()
                    new_list = []
                    for ref_name in current_list:
                        new_list.append(ref_name+dupli_id)

                    ref_bones_fingers[finger_type] = new_list

                base_fingers_names = {"thumb":limb.thumb, "index":limb.index, "middle":limb.middle, "ring":limb.ring, "pinky":limb.pinky}

                if limb.manual_phalanges:# manual phalanges as set in the list
                    for finger_type in base_fingers_names:
                        phalange1 = get_edit_bone(base_fingers_names[finger_type])
                        fingers_names[finger_type].append(phalange1.name)
                        
                        phal2_name = limb.get(finger_type+'2')
                        if limb.fingers == "4" and finger_type != "thumb" != 0:# the thumb ([0]) has no metacarp
                            phal2_name = limb.get(finger_type+'1')
                        if phal2_name:
                            phalange2 = get_edit_bone(phal2_name)
                            fingers_names[finger_type].append(phalange2.name)
                        
                        phal3_name = limb.get(finger_type+'3')
                        if limb.fingers == "4" and finger_type != "thumb" != 0:# the thumb ([0]) has no metacarp
                            phal3_name = limb.get(finger_type+'2')
                        if phal3_name:
                            phalange3 = get_edit_bone(phal3_name)
                            fingers_names[finger_type].append(phalange3.name)
                        
                        if limb.fingers == "4" and finger_type != "thumb" != 0:# the thumb ([0]) has no metacarp
                            phal4_name = limb.get(finger_type+'3')
                            if phal4_name:
                                phalange4 = get_edit_bone(phal4_name)
                                fingers_names[finger_type].append(phalange4.name)                            
                            
                else:# automatic phalange, find children
                    for finger_type in base_fingers_names:
                        phalange1 = phalange2 = phalange3 = phalange4 = None
                        finger_bone_name = base_fingers_names[finger_type]
                        phalange1 = get_edit_bone(finger_bone_name)
                        
                        if phalange1:
                            fingers_names[finger_type].append(phalange1.name)
                            if phalange1.children:
                                phalange2 = phalange1.children[0]
                                fingers_names[finger_type].append(phalange2.name)
                                if phalange2.children:
                                    phalange3 = phalange2.children[0]
                                    fingers_names[finger_type].append(phalange3.name)
                                    # 3 or 4 finger bones support
                                    if limb.fingers == "4" and finger_type != "thumb" != 0:# the thumb ([0]) has no metacarp
                                        if phalange3.children:
                                            phalange4 = phalange3.children[0]
                                            fingers_names[finger_type].append(phalange4.name)


                # Check if the total fingers amount is correct. If not, skip
                valid_list = True
                expected_finger_count = 0
                for fidx, fname in enumerate((limb.thumb, limb.index, limb.middle, limb.ring, limb.pinky)):
                    if fname != "":
                        if fidx == 0:#thumb
                            expected_finger_count += 3
                        else:
                            expected_finger_count += 4 if limb.fingers == "4" else 3

                phalanges_count = 0
                for finger_type in fingers_names:
                    phalanges_count += len(fingers_names[finger_type])

                if phalanges_count != expected_finger_count:
                    print("Error, found", len(fingers_names), "fingers. Should have found", expected_finger_count)
                    print("Cannot setup fingers, set to None")
                    valid_list = False
                    limb.fingers = "NONE"# set fingers to None

                if valid_list:
                    # skinning matches
                    for finger_type in fingers_names:
                        phalange1_name = phalange2_name = phalange3_name = phalange4_name = None

                        phal_list = fingers_names[finger_type]

                        if len(phal_list) >= 1:
                            phalange1_name = phal_list[0]
                        if len(phal_list) >= 2:
                            phalange2_name = phal_list[1]
                        if len(phal_list) >= 3:
                            phalange3_name = phal_list[2]
                        if len(phal_list) >= 4:
                            phalange4_name = phal_list[3]


                        def add_finger_deforming_match_3(finger_type):
                            if phalange1_name:
                                skin_dict[phalange1_name] = {'deform':finger_type+"1"+dupli_id+side, 'coords':get_bone_coords(phalange1_name)}
                            if phalange2_name:
                                skin_dict[phalange2_name] = {'deform':"c_"+finger_type+"2"+dupli_id+side, 'coords':get_bone_coords(phalange2_name)}
                            if phalange3_name:
                                skin_dict[phalange3_name] = {'deform':"c_"+finger_type+"3"+dupli_id+side, 'coords':get_bone_coords(phalange3_name)}

                        def add_finger_deforming_match_4(finger_type):
                            if phalange1_name:
                                skin_dict[phalange1_name] = {'deform':"c_"+finger_type+"1_base"+dupli_id+side, 'coords':get_bone_coords(phalange1_name)}
                            if phalange2_name:
                                skin_dict[phalange2_name] = {'deform':finger_type+"1"+dupli_id+side, 'coords':get_bone_coords(phalange2_name)}
                            if phalange3_name:
                                skin_dict[phalange3_name] = {'deform':"c_"+finger_type+"2"+dupli_id+side, 'coords':get_bone_coords(phalange3_name)}
                            if phalange4_name:
                                skin_dict[phalange4_name] = {'deform':"c_"+finger_type+"3"+dupli_id+side, 'coords':get_bone_coords(phalange4_name)}

                        if phalange1_name:
                            if limb.fingers == "3":
                                add_finger_deforming_match_3(finger_type)

                            elif limb.fingers == "4":
                                if finger_type == "thumb":
                                    add_finger_deforming_match_3(finger_type)
                                else:
                                    add_finger_deforming_match_4(finger_type)

                        # remove fingers orphan bones from list
                        for f in [phalange1_name, phalange2_name, phalange3_name, phalange4_name]:
                            if f:
                                if f in orphan_bones:
                                    orphan_bones.remove(f)

                    # store finger bone data
                    for finger_type in fingers_names:
                        phal_list = fingers_names[finger_type]
                        for i, phal_name in enumerate(phal_list):
                            finger_bone = get_edit_bone(phal_name)
                            finger_ref_name = ref_bones_fingers[finger_type][i]
                            
                            bones_coords[finger_ref_name] = {'head':arm_mat @ finger_bone.head.copy(), 'tail':arm_mat @ finger_bone.tail.copy(), 
                                'x_axis':(arm_mat_rot @ finger_bone.x_axis).normalized(), 'y_axis':(arm_mat_rot @ finger_bone.y_axis).normalized(), 'z_axis':(arm_mat_rot @ finger_bone.z_axis).normalized(), 
                                'name':finger_bone.name}# store bone data
                            
                            self.fingers_ctrl[finger_bone.name] = 'c_'+finger_ref_name.replace('_ref', '')+side
                            #print("SAVE FINGER", finger_bone.name, 'c_'+finger_ref_name.replace('_ref', '')+side)
                            #print('c_'+finger_ref_name.replace('_ref', '')+dupli_id+side)


        elif limb.type == "SPINE":
            side = ".x"# maybe add other sides later, but ARP only supports spine bones of center side so far
            limb.side = "CENTER"

            pelvis = limb.bone_01
            spine_01 = limb.bone_02
            spine_02 = limb.bone_03
            spine_03 = limb.bone_04
            spine_04 = limb.bone_05
            spine_05 = limb.bone_06
            spine_06 = limb.bone_07

            # skinning matches
            # spine 0 pelvis
            if limb.weights_override and limb.override_bone_01 != "":
                skin_dict[limb.override_bone_01] = {'deform':"root"+side, 'coords':get_bone_coords(limb.override_bone_01)}
            else:
                skin_dict[pelvis] = {'deform':"root"+side, 'coords':get_bone_coords(pelvis)}
            # spine 1
            if limb.weights_override and limb.override_bone_02 != "":
                skin_dict[limb.override_bone_02] = {'deform':"spine_01"+side, 'coords':get_bone_coords(limb.override_bone_02)}
            else:
                skin_dict[spine_01] = {'deform':"spine_01"+side, 'coords':get_bone_coords(spine_01)}
            # spine 2
            if limb.weights_override and limb.override_bone_03 != "":
                skin_dict[limb.override_bone_03] = {'deform':"spine_02"+side, 'coords':get_bone_coords(limb.override_bone_03)}
            else:
                skin_dict[spine_02] = {'deform':"spine_02"+side, 'coords':get_bone_coords(spine_02)}
            # spine 3
            if limb.weights_override and limb.override_bone_04 != "":
                skin_dict[limb.override_bone_04] = {'deform':"spine_03"+side, 'coords':get_bone_coords(limb.override_bone_04)}
            else:
                skin_dict[spine_03] = {'deform':"spine_03"+side, 'coords':get_bone_coords(spine_03)}
            # spine 4
            if limb.weights_override and limb.override_bone_05 != "":
                skin_dict[limb.override_bone_05] = {'deform':"spine_04"+side, 'coords':get_bone_coords(limb.override_bone_05)}
            else:
                skin_dict[spine_04] = {'deform':"spine_04"+side, 'coords':get_bone_coords(spine_04)}
            # spine 5
            if limb.weights_override and limb.override_bone_06 != "":
                skin_dict[limb.override_bone_06] = {'deform':"spine_05"+side, 'coords':get_bone_coords(limb.override_bone_06)}
            else:
                skin_dict[spine_05] = {'deform':"spine_05"+side, 'coords':get_bone_coords(spine_05)}
            # spine 6
            if limb.weights_override and limb.override_bone_07 != "":
                skin_dict[limb.override_bone_07] = {'deform':"spine_06"+side, 'coords':get_bone_coords(limb.override_bone_07)}
            else:
                skin_dict[spine_06] = {'deform':"spine_06"+side, 'coords':get_bone_coords(spine_06)}

            bones_spine_list = [pelvis, spine_01, spine_02, spine_03, spine_04, spine_05, spine_06]
            if limb.primary_axis_auto:
                limb.primary_axis = find_primary_axis(bones_spine_list)

            ref_bones_spine = ["root_ref", "spine_01_ref", "spine_02_ref", "spine_03_ref", "spine_04_ref", "spine_05_ref", "spine_06_ref"]
            for i, bname in enumerate(bones_spine_list):
                ebone = get_edit_bone(bname)
                if ebone:
                    bones_coords[ref_bones_spine[i]] = {'head':arm_mat @ ebone.head.copy(), 'tail':arm_mat @ ebone.tail.copy(), 'x_axis':(arm_mat_rot @ ebone.x_axis).normalized(), 'y_axis':(arm_mat_rot @ ebone.y_axis).normalized(), 'z_axis':(arm_mat_rot @ ebone.z_axis).normalized(), 'name':ebone.name}# store bone data

        elif limb.type == "HEAD":
            side = ".x"# maybe add other sides later, but ARP only supports head bones of center side so far
            limb.side = "CENTER"

            neck = limb.bone_01
            neck2 = limb.bone_04
            neck3 = limb.neck3
            neck4 = limb.neck4
            neck5 = limb.neck5
            neck6 = limb.neck6
            neck7 = limb.neck7
            neck8 = limb.neck8
            neck9 = limb.neck9
            neck10 = limb.neck10

            necks_list = [neck, neck2, neck3, neck4, neck5, neck6, neck7, neck8, neck9, neck10]

            head = limb.bone_02
            head_end = limb.bone_03

            # skinning match
            if neck != "":
                if limb.neck_bones_amount == 1:
                    skin_dict[neck] = {'deform':"neck"+side, 'coords':get_bone_coords(neck)}
                else:
                    for i in range(2, limb.neck_bones_amount+1):
                        cur_neck = necks_list[i-2]
                        if self.neck_auto_twist:
                            skin_dict[cur_neck] = {'deform':"subneck_twist_"+str(i-1)+side, 'coords':get_bone_coords(cur_neck)}
                        else:
                            skin_dict[cur_neck] = {'deform':"c_subneck_"+str(i-1)+side, 'coords':get_bone_coords(cur_neck)}

                    last_neck = necks_list[limb.neck_bones_amount-1]
                    skin_dict[last_neck] = {'deform':"neck"+side, 'coords':get_bone_coords(last_neck)}           

            skin_dict[head] = {'deform':"head"+side, 'coords':get_bone_coords(head)}

            # store coords
            ref_bones_head = ["head_ref"]
            def_bones = [head]

            if neck != "":
                ref_bones_head.insert(0, "neck_ref")
                def_bones.insert(0, neck)

            for i in range(2, limb.neck_bones_amount+1):
                cur_neck = necks_list[i-1]
                if cur_neck != "":
                    idx = len(ref_bones_head)-2
                    ref_bones_head.insert(idx, "subneck_"+str(i-1)+"_ref")
                    def_bones.insert(len(def_bones)-1, cur_neck)

            print("ref_bones_head", ref_bones_head)
            print("def_bones", def_bones)
            """
            if neck2 != "":
                ref_bones_head = ["subneck_1_ref", "neck_ref", "head_ref"]
                def_bones = [neck, neck2, head]
            """

            if limb.primary_axis_auto:
                limb.primary_axis = find_primary_axis(def_bones)

            for i, bname in enumerate(def_bones):
                ebone = get_edit_bone(bname)
                if ebone:
                    bone_tail = ebone.tail.copy()
                    if bname == head:# get the head_end if any
                        if head_end != "":
                            bone_tail = get_edit_bone(head_end).head.copy()
                    parent_name = "" if ebone.parent == None else ebone.parent.name
                    bones_coords[ref_bones_head[i]] = {'head':arm_mat @ ebone.head.copy(), 'tail':arm_mat @ bone_tail, 
                        'x_axis':(arm_mat_rot @ ebone.x_axis).normalized(), 'y_axis':(arm_mat_rot @ ebone.y_axis).normalized(), 'z_axis':(arm_mat_rot @ ebone.z_axis).normalized(), 
                        'name':ebone.name, 'parent_name':parent_name}# store bone data

        elif limb.type == 'TAIL':
            tail_root_name = limb.bone_01
            ref_bones_tail = []
            tail_children_bones = [tail_root_name] + get_bone_children(tail_root_name, single_child_only=True)
            
            for i, b in enumerate(tail_children_bones):
                stri = '%02d' % i
                ref_name = 'tail_'+stri+'_ref'
                ref_bones_tail.append(ref_name)
            
            #print('ref_bones_tail', ref_bones_tail)
            
            side = '.x' 
            if limb.side == 'RIGHT':
                side = '.r'
            elif limb.side == 'LEFT':
                side = '.l'
            
            # multi limb support
            tail_limb_count = 0
            if side == ".l":
                tail_limb_count_left += 1
                tail_limb_count = leg_limb_count_left
            elif side == ".r":
                tail_limb_count_right += 1
                tail_limb_count = tail_limb_count_right
            elif side == ".x":
                tail_limb_count_mid += 1
                tail_limb_count = tail_limb_count_mid

            dupli_id = ''

            if tail_limb_count > 1:
                ref_bones_tail_dupli = []
                dupli_id = '{:03d}'.format(tail_limb_count-1)
                dupli_id = "_dupli_"+str(dupli_id)

                for ref_bone_name in ref_bones_tail:
                    ref_bone_name_dupli = ref_bone_name+dupli_id
                    ref_bones_tail_dupli.append(ref_bone_name_dupli)

                ref_bones_tail = ref_bones_tail_dupli

                print("Stored dupli tail side", side, ":", ref_bones_tail)
           
            for i, bname in enumerate(tail_children_bones):
                ebone = get_edit_bone(bname)
                
                # skinning matches
                stri = '%02d' % i
                c_name = 'c_tail_'+stri+dupli_id+side
                skin_dict[bname] = {'deform':c_name, 'coords':get_bone_coords(bname)}
                
                self.tail_ctrl[ebone.name] = c_name
                
                bones_coords[ref_bones_tail[i]] = {'head':arm_mat @ ebone.head.copy(), 'tail':arm_mat @ ebone.tail.copy(), 
                    'x_axis':(arm_mat_rot @ ebone.x_axis).normalized(), 'y_axis':(arm_mat_rot @ ebone.y_axis).normalized(), 'z_axis':(arm_mat_rot @ ebone.z_axis).normalized(), 
                    'name':ebone.name}# store bone data
                
        
        # store limb
        limbs_coords[limb_idx] = bones_coords


    # update orphan bones list
    
    for limb_idx, limb in enumerate(scn.limb_map):
        main_bones = [limb.bone_01, limb.bone_02, limb.bone_03, limb.bone_04, limb.bone_05, limb.bone_06, limb.bone_07]#limb.bone_twist_02_01, limb.bone_twist_02_02
        
        # not fancy... twist bones inputs are idx 2,3,4,5 depending on the limb
        # exclude them if no twist bones
        if limb.twist_bones_amount == 0:
            if limb.type == 'ARM':
                main_bones.remove(limb.bone_03)
                main_bones.remove(limb.bone_05)
            if limb.type == 'LEG':
                main_bones.remove(limb.bone_02)
                main_bones.remove(limb.bone_04)
        else:
            # twists >= 2
            for i in range(2, limb.twist_bones_amount+1):
                id = '%02d' % (i)
                main_bones.append(limb.get('bone_twist_'+id+'_01'))
                main_bones.append(limb.get('bone_twist_'+id+'_02'))

        if limb.type == "HEAD":
            if limb.neck_bones_amount > 2:
                necks_list = [limb.neck3, limb.neck4, limb.neck5, limb.neck6, limb.neck7, limb.neck8, limb.neck9, limb.neck10]

                for i in range(3, limb.neck_bones_amount+1):
                    main_bones.append(necks_list[i-3])

        if limb.type == "LEG":
            if limb.leg_type == "3":
                main_bones.append(limb.upper_thigh)
                
        if limb.type == 'TAIL':
            bones_coords = limbs_coords[limb_idx]
            for ref_name in bones_coords:
                bname = bones_coords[ref_name]['name']
                main_bones.append(bname)

        # orphan bones that are actually ARP bones, they will be generated in the ARP rig
        excluded_orphan_bones = ["c_thigh_b"]

        if self.remove_root:# root bone can be removed optionally
            root_names = ['root', 'Root']
            for rn in root_names:
                r_bone = get_edit_bone(rn)
                if r_bone == None:
                    continue
                if r_bone.parent == None:
                    excluded_orphan_bones.append(rn)

        for mb_name in main_bones:
            if mb_name in orphan_bones:
                orphan_bones.remove(mb_name)

        for ex_name in excluded_orphan_bones:
            for b in orphan_bones:
                if b.startswith(ex_name):                  
                    orphan_bones.remove(b)
    
    
    # find orphan bones parent recursively until a known bone is found
    # self.orphan_bones_dict[bone name] = {'parent':matching_parent_name, 'original_parent':original_parent_name, 'head':arm_mat @ b.head.copy(), 'tail':arm_mat @ b.tail.copy(), 'roll':b.roll, 'x_axis':b.x_axis}
    #self.orphan_bones_dict = {}

    for or_name in orphan_bones:
        b = get_edit_bone(or_name)
        last_parent = b.parent
        original_parent_name = last_parent.name if last_parent != None else ''
        search_for_parent = True
        matching_parent_name = None
        iter = 0# avoid infinite loop
        while search_for_parent and iter < 500:
            iter += 1
            if last_parent:
                # look for the bone parent in limbs
                for limb_idx, limb in enumerate(scn.limb_map):
                    main_bones = [limb.bone_01, limb.bone_02, limb.bone_03, limb.bone_04, limb.bone_05, limb.bone_06, limb.bone_07]
                    if limb.manual_phalanges:
                        for phal_name in ['thumb2', 'thumb3', 'index1', 'index2', 'index3', 'middle1', 'middle2', 'middle3', 'ring1', 'ring2', 'ring3', 'pinky1', 'pinky2', 'pinky3']:
                            main_bones.append(limb.get(phal_name))
                            
                    if limb.type == 'TAIL':
                        bones_coords = limbs_coords[limb_idx]
                        for ref_name in bones_coords:
                            bname = bones_coords[ref_name]['name']
                            main_bones.append(bname)
                            
                    override_bones = [limb.override_bone_01, limb.override_bone_02, limb.override_bone_03, limb.override_bone_04, limb.override_bone_05, limb.override_bone_06, limb.override_bone_07]
                    if last_parent.name in main_bones:
                        idx = main_bones.index(last_parent.name)
                        search_for_parent = False
                        matching_parent_name = last_parent.name
                        
                        if idx < len(override_bones):# manual fingers don't support overrides yet... TODO
                            if limb.weights_override and override_bones[idx] != "":# check for overrides
                                if override_bones[idx] != or_name:# check it's not the same orphan bone
                                    search_for_parent = False
                                    matching_parent_name = override_bones[idx]


                    if search_for_parent == False:
                        break

                last_parent = last_parent.parent

            else:
                search_for_parent = False


        # parent not found, is not a known bone, may be an orphan bone
        if matching_parent_name == None:
            if b.parent:
                if b.parent.name in orphan_bones:
                    matching_parent_name = b.parent.name
                    #if or_name == "CC_Base_L_ForearmTwist01":
                    #    print("3.", matching_parent_name)
            else:
                # no parent, set to c_traj master
                matching_parent_name = "c_traj"

        # store orphan bones data
        if matching_parent_name != None:
            self.orphan_bones_dict[or_name] = {'original_name':or_name, 'parent':matching_parent_name, 'original_parent':original_parent_name, 'head':arm_mat @ b.head.copy(), 'tail':arm_mat @ b.tail.copy(), 'roll':b.roll, 'x_axis':(arm_mat_rot @ b.x_axis).normalized()}


    bpy.ops.object.mode_set(mode='POSE')

    # store orphan bones constraints
    if len(self.orphan_bones_dict) and self.orphan_copy_cns:

        for or_name in self.orphan_bones_dict:
            #print("or_name", or_name)
            orphan_pbone = get_pose_bone(or_name)
            if len(orphan_pbone.constraints):
                bones_cns_dict = pose_bones_constraints_to_dict(source_skeleton, [orphan_pbone])
                cns_dict = bones_cns_dict[or_name]
                base_dict = self.orphan_bones_dict[or_name].copy()
                new_dict = {'constraints':cns_dict}
                base_dict.update(new_dict)
                self.orphan_bones_dict[or_name] = base_dict


    # Add limbs
    # check if there's another "rig" named object in the scene
    # if so, rename it
    existing_rig = get_object("rig")
    if existing_rig:
        print("renaming 'rig' object")
        existing_rig.name = existing_rig.name+"_old"

    #   add base armature
    if self.arp_ver_int >= 36820:
        bpy.ops.arp.append_arp(rig_preset='free')
    else:# backward-compatibility
        bpy.ops.arp.append_arp(rig_presets='free')

    
    for limb_idx, limb in enumerate(scn.limb_map):

        _side = ".l"
        if limb.side == "RIGHT":
            _side = ".r"
        elif limb.side == "CENTER":
            _side = ".x"

        # add leg
        if limb.type == "LEG":
            bpy.ops.arp.add_limb(limbs_presets='leg'+_side)
            
            # toes support
            enable_thumb = False
            enable_index = False
            enable_middle = False
            enable_ring = False
            enable_pinky = False

            if limb.fingers != "NONE":
                if limb.thumb != "":
                    enable_thumb = True
                if limb.index != "":
                    enable_index = True
                if limb.middle != "":
                    enable_middle = True
                if limb.ring != "":
                    enable_ring = True
                if limb.pinky  != "":
                    enable_pinky = True

            if enable_thumb == False and enable_index == False and enable_middle == False and enable_ring == False and enable_pinky == False:
                limb.fingers = "NONE"
                
            # twist bones amount
            _leg_twist_bones = limb.twist_bones_amount
            if _leg_twist_bones == 0:# can't be 0 for now, just leave empty twist weight if no twist bones are set
                _leg_twist_bones = 1

            # no multiple toes support for now, TODO
            bpy.ops.arp.show_limb_params(limb_type="leg", side=_side, leg_twist_bones=_leg_twist_bones, 
                toes_thumb=enable_thumb, toes_index=enable_index, toes_middle=enable_middle, toes_ring=enable_ring, 
                toes_pinky=enable_pinky, toes_metatarsal=limb.fingers == '4', toes_parent_foot=limb.toes_parent_foot,
                reset_to_default_settings=False, three_bones_leg=limb.leg_type == '3', foot_ik_offset=False,
                leg_ikfk_default=self.leg_ik_fk, leg_auto_ik_roll=limb.auto_ik_roll)

        # add arm
        elif limb.type == "ARM":

            bpy.ops.arp.add_limb(limbs_presets='arm'+_side)

            # fingers support
            enable_thumb = False
            enable_index = False
            enable_middle = False
            enable_ring = False
            enable_pinky = False

            if limb.fingers != "NONE":
                if limb.thumb != "":
                    enable_thumb = True
                if limb.index != "":
                    enable_index = True
                if limb.middle != "":
                    enable_middle = True
                if limb.ring != "":
                    enable_ring = True
                if limb.pinky  != "":
                    enable_pinky = True

            if enable_thumb == False and enable_index == False and enable_middle == False and enable_ring == False and enable_pinky == False:
                limb.fingers = "NONE"

            # twist bones amount
            _arm_twist_bones = limb.twist_bones_amount
            if _arm_twist_bones == 0:# can't be 0 for now, just leave empty twist weight if no twist bones are set
                _arm_twist_bones = 1

            bpy.ops.arp.show_limb_params(limb_type="arm", side=_side, arm_twist_bones=_arm_twist_bones, 
                finger_thumb=enable_thumb, finger_index=enable_index, finger_middle=enable_middle, 
                finger_ring=enable_ring, finger_pinky=enable_pinky, reset_to_default_settings=False, 
                arm_ikfk_default=self.arm_ik_fk, arm_auto_ik_roll= limb.auto_ik_roll)                                              
            #print("ARM IKFK", self.arm_ik_fk)
        
        elif limb.type == "SPINE":
            bpy.ops.arp.add_limb(limbs_presets='spine')

            # set spine count
            spine_bones_count = 2
            for i in [limb.bone_03, limb.bone_04, limb.bone_05, limb.bone_06, limb.bone_07]:
                if i != "":
                    spine_bones_count += 1
          
            if self.arp_ver_int >= 37110:
                bpy.ops.arp.show_limb_params(limb_type="spine", spine_count=spine_bones_count, reset_to_default_settings=False)
            else:# backward-compatibility
                bpy.context.active_object.rig_spine_count = spine_bones_count
                bpy.ops.arp.show_limb_params(limb_type="spine", reset_to_default_settings=False)

            # disconnect ref bones
            if not limb.connect:
                for idx in range(1, spine_bones_count):
                    str_idx = '%02d' % (idx)
                    spine_ref_name = "spine_" + str_idx + "_ref.x"
                    spine_ref = get_edit_bone(spine_ref_name)
                    if spine_ref:
                        spine_ref.use_connect = False
                        
            
            # increase root spine bones shape scale, generally too small
            """# disable it for now, not always relevant. Depends on the skeleton proportions
            bpy.ops.object.mode_set(mode='POSE')
            get_pose_bone("c_root_master.x").custom_shape_scale = 1.0
            get_pose_bone("c_root.x").custom_shape_scale = 2.0
            bpy.ops.object.mode_set(mode='EDIT')
            """
        
        elif limb.type == "HEAD":
            bpy.ops.arp.add_limb(limbs_presets='head')

            # disable facial
            bpy.ops.arp.show_limb_params(limb_type="head", facial=False, reset_to_default_settings=False)

            # set 2 neck bones
            #if limb.bone_04 != "":# 2 neck bones are set
            if limb.neck_bones_amount > 1:
                bpy.ops.arp.show_limb_params(limb_type="neck", neck_count=limb.neck_bones_amount, 
                    neck_twist=self.neck_auto_twist, neck_bendy=1, reset_to_default_settings=False)                             

        elif limb.type == 'TAIL':
            bpy.ops.arp.add_limb(limbs_presets='tail')
            
            bones_coords = limbs_coords[limb_idx]
            _tail_count = len(bones_coords)
        
            bpy.ops.arp.show_limb_params(limb_type="tail", tail_count=_tail_count, tail_side=_side, tail_master_at_root=True, reset_to_default_settings=False)
            
            
        
    if "arp_rig_type" in bpy.context.active_object.keys():#backward-compatibility
        bpy.context.active_object.arp_rig_type = "quadruped"
    else:
        bpy.context.active_object.rig_type = "quadruped"


    # global scale
    self.arp_armature_name = bpy.context.active_object.name
    arp_armature = get_object(self.arp_armature_name)
    
    # get the maximum dim axis
    max_dim = 0.0
    for d in source_skeleton.dimensions:
        if d > max_dim:
            max_dim = d

    arp_armature.dimensions[2] = max_dim
    arp_armature.scale[1] = arp_armature.scale[0] = arp_armature.scale[2]

    init_arp_scale(arp_armature)


    bpy.ops.object.mode_set(mode='EDIT')


    # Add orphan bones

    print("\nAdd orphan bones")

    for or_name in self.orphan_bones_dict.copy():
        if or_name.startswith("cor_"):
            continue

        or_bone = get_edit_bone(or_name)

        if or_bone == None:
            print('Create orphan bone:', or_name)
            or_bone = arp_armature.data.edit_bones.new(or_name)
            or_bone.head, or_bone.tail = [0,0,0], [0,0,0.2]# blank coordinates, aligned later

        else:
            print('Orphan bone conflict:', or_name, 'already exists in ARP armature')
            # name conflict, the orphan bone name is same name as ARP bone. Rename it with "cor_" prefix
            or_bone = arp_armature.data.edit_bones.new("cor_"+or_name)

            # replace in orphan_bones dict
            self.orphan_bones_dict["cor_"+or_name] = self.orphan_bones_dict[or_name]
            del self.orphan_bones_dict[or_name]

            # add in skin_dict dict
            skin_dict[or_name] = {'deform':"cor_"+or_name, 'coords':None}

            # replace parent match name in skin_dict
            for orname in self.orphan_bones_dict:
                if self.orphan_bones_dict[orname]['parent'] == or_name:
                    self.orphan_bones_dict[orname] = {'original_name':self.orphan_bones_dict[orname]['original_name'], 
                                                    'parent':"cor_"+or_name, 'original_parent':self.orphan_bones_dict[orname]['original_parent'], 
                                                    'head':self.orphan_bones_dict[orname]['head'], 'tail':self.orphan_bones_dict[orname]['tail'], 'roll':self.orphan_bones_dict[orname]['roll'], 
                                                    'x_axis':self.orphan_bones_dict[orname]['x_axis']}

            or_name = "cor_"+or_name
        
        set_bone_layer(or_bone, self.orphan_bones_collection, idx=self.orphan_bones_layer)
        
    
    # Set orphan bones transforms and parent
    print("\nSet orphan bones transforms and parent...")

    for or_name in self.orphan_bones_dict.copy():
        or_bone = get_edit_bone(or_name)

        matching_bone_parent_name = self.orphan_bones_dict[or_name]['parent']
        original_parent_name = self.orphan_bones_dict[or_name]['original_parent']
        or_bone.head = self.orphan_bones_dict[or_name]['head']
        or_bone.tail = self.orphan_bones_dict[or_name]['tail']
        or_bone.roll = self.orphan_bones_dict[or_name]['roll']
        or_bone_x_axis = self.orphan_bones_dict[or_name]['x_axis']
        align_bone_x_axis(or_bone, or_bone_x_axis)

        has_child_of_cns = False

        if 'constraints' in self.orphan_bones_dict[or_name]:
            or_bone_cns = self.orphan_bones_dict[or_name]['constraints']
            for cns in or_bone_cns:
                if cns['type'] == 'CHILD_OF':
                    has_child_of_cns = True

        # set parent
        parent_name = None        
        parent_name_main = None
        parent_name_or = None
        
        # orphan bone parented to orphan bone
        if original_parent_name in self.orphan_bones_dict:
            parent_name_or = original_parent_name
        elif matching_bone_parent_name in self.orphan_bones_dict:
            parent_name_or = matching_bone_parent_name
        
        # orphan bone parented to main deforming bone
        if matching_bone_parent_name in skin_dict:
            parent_name_main = skin_dict[matching_bone_parent_name]['deform']
        elif or_name in skin_dict:
            parent_name_main = skin_dict[or_name]['deform']
        
        # if only one is found, use the valid one
        if parent_name_main and parent_name_or == None:
            parent_name = parent_name_main
        elif parent_name_main == None and parent_name_or:
            parent_name = parent_name_or
            
        # if both are found, choose which to use
        if parent_name_main and parent_name_or:
            if self.orphan_bones_parent_to_def:# prioritize main bones as parent if setting enabled
                parent_name = parent_name_main
            else:
                parent_name = parent_name_or
        
        if parent_name == None:# no parent found
            print("Could not find parent for orphan bone: "+or_name+". Set to c_traj instead")
            parent_name = "c_traj"


        if parent_name:
            if has_child_of_cns == False:
                parent = get_edit_bone(parent_name)
                or_bone.parent = parent


    
    # Align limbs
    def get_source_ref_match(limb_type, ref_bone_name):

        # returns the corresponding reference bone for a given source bone
        ref_list = []
        spine_source_ref_matches = ["root_ref", "spine_01_ref", "spine_02_ref", "spine_03_ref", "spine_04_ref", "spine_05_ref", "spine_06_ref"]
        if limb_type == "SPINE":
            ref_list = spine_source_ref_matches

        # find the limb
        limb = None
        limb_side = ""
        for _limb in scn.limb_map:
            if _limb.type == limb_type:
                limb = _limb
                if _limb.side == "CENTER":
                    limb_side = ".x"
                elif limb_side == "LEFT":
                    limb_side = ".l"
                elif limb_side == "RIGHT":
                    limb_side = ".r"
                break

        bone_parent_match = None

        if limb:
            # find the matching ref bone
            limb_bones_list = [limb.bone_01, limb.bone_02, limb.bone_03, limb.bone_04, limb.bone_05, limb.bone_06, limb.bone_07]
            for i, bones_name in enumerate(ref_list):
                if limb_bones_list[i] == ref_bone_name:
                    bone_parent_match = bones_name+limb_side
                    break

        if bone_parent_match == None:
            # no parent match found, must be an orphan bone
            print("Bone parent seems to be an orphan bone, parent to "+ref_bone_name)
            bone_parent_match = ref_bone_name

        return bone_parent_match


    # if preserve skeleton, add helper bones
    if self.mode == 'PRESERVE':
        for base_bone_name in skin_dict:

            if skin_dict[base_bone_name]['coords'] == None:
                continue

            h_bone = arp_armature.data.edit_bones.new(base_bone_name+'_qr_offset')
            h_bone.head, h_bone.tail = skin_dict[base_bone_name]['coords'][0], skin_dict[base_bone_name]['coords'][1]
            h_bone_x_axis = skin_dict[base_bone_name]['coords'][2]
            align_bone_x_axis(h_bone, h_bone_x_axis)
            h_bone.parent = get_edit_bone(skin_dict[base_bone_name]['deform'])
            set_bone_layer(h_bone, 'qr_helpers', idx=15)
            h_bone.use_deform = False


    # bones_coords[reference_bone_name] = {}
    for limb_idx in range(0, len(scn.limb_map)):
        limb = scn.limb_map[limb_idx]
        print("\nAligning limb:", limb.type)
        bones_coords = limbs_coords[limb_idx]

        if limb.type == 'LEG':
            side = '.l' if limb.side == 'LEFT' else '.r'

            # multi limb support
            dupli_idx = ''

            for bone_ref_name in bones_coords:
                if "_dupli_" in bone_ref_name:
                    dupli_idx = "_dupli_"+str(bone_ref_name[-3:])
                break

            # store dupli idx for anim remap
            limb.dupli_idx = dupli_idx

            # upper thigh
            if limb.leg_type == "3":
                thigh_b_ref = get_edit_bone("thigh_b_ref"+dupli_idx+side)
                thigh_b_ref.head = bones_coords["thigh_b_ref"+dupli_idx]['head']
                thigh_b_ref.tail = bones_coords["thigh_ref"+dupli_idx]['head']
                roll_fac = 1 if side == ".l" else -1
                align_bone_x_axis(thigh_b_ref, Vector((0, 1*roll_fac, 0)))

            # thigh
            thigh_ref = get_edit_bone("thigh_ref"+dupli_idx+side)
            thigh_ref.head = bones_coords["thigh_ref"+dupli_idx]['head']
            thigh_ref.tail = bones_coords["leg_ref"+dupli_idx]['head']


            # parent thigh/upper thigh
            if limb.leg_type == "3":
                bone_parent_name = bones_coords["thigh_b_ref"+dupli_idx]['parent_name']
                bone_parent_match_name = get_source_ref_match("SPINE", bone_parent_name)
                print("  Upper Thigh parent:", bone_parent_name, ">", bone_parent_match_name)
                if bone_parent_match_name:
                    thigh_b_ref.parent = get_edit_bone(bone_parent_match_name)


            elif limb.leg_type == "2":
                bone_parent_name = bones_coords["thigh_ref"+dupli_idx]['parent_name']
                bone_parent_match_name = get_source_ref_match("SPINE", bone_parent_name)
                print("  Thigh parent:", bone_parent_name, ">", bone_parent_match_name)
                if bone_parent_match_name:
                    thigh_ref.parent = get_edit_bone(bone_parent_match_name)

            # leg
            leg_ref = get_edit_bone("leg_ref"+dupli_idx+side)
            leg_ref.head = bones_coords["leg_ref"+dupli_idx]['head']
            if limb.connect_foot_to_calf:
                leg_ref.tail = bones_coords["leg_ref"+dupli_idx]['tail']
            else:
                leg_ref.tail = bones_coords["foot_ref"+dupli_idx]['head']


            # foot
            foot_ref_name = "foot_ref"+dupli_idx
            foot_ref = get_edit_bone(foot_ref_name+side)
            if limb.connect_foot_to_calf:
                foot_ref.head = leg_ref.tail.copy()
            else:
                foot_ref.head = bones_coords[foot_ref_name]['head']


            toes_ref_name = "toes_ref"+dupli_idx
            if toes_ref_name in bones_coords:# toes are optional
                foot_ref.tail = bones_coords[toes_ref_name]['head']
            else:
                foot_length = (bones_coords[foot_ref_name]['head'] - bones_coords[foot_ref_name]['tail']).magnitude*0.5
                
                dir_vec = 1 if not '-' in limb.foot_dir_axis else -1
                
                
                if  'X' in limb.foot_dir_axis:
                    foot_ref.tail = foot_ref.head + bones_coords[foot_ref_name]['x_axis'] * dir_vec * foot_length
                elif 'Y' in limb.foot_dir_axis:
                    foot_ref.tail = foot_ref.head + (bones_coords[foot_ref_name]['y_axis'] * dir_vec) * foot_length
                elif 'Z' in limb.foot_dir_axis:
                    foot_ref.tail = foot_ref.head + bones_coords[foot_ref_name]['z_axis'] * dir_vec * foot_length

            #   roll
            if limb.force_up_axis:
                align_bone_z_axis(foot_ref, Vector((0,0,1)))
            else:
                align_bone_x_axis(foot_ref,  bones_coords["foot_ref"+dupli_idx]['x_axis'])
                if limb.up_axis == "-Z":
                    foot_ref.roll += math.radians(180)
                elif limb.up_axis == "X":
                    foot_ref.roll += math.radians(90)
                elif limb.up_axis == "-X":
                    foot_ref.roll += math.radians(-90)


            # auto-align the knee based on the foot direction for more in line rotation
            if limb.auto_knee:
                median_point = (foot_ref.head + thigh_ref.head) * 0.5

                if thigh_ref.tail[1] > median_point[1]:
                    print("  The knee is pointing backward, correct it")

                    thigh_ref.tail[1] = median_point[1] + (median_point[1] - thigh_ref.tail[1])*0.1

                # auto-align the knee based on the foot direction for more in line rotation
                thigh_ref.tail = project_point_onto_plane(thigh_ref.tail, thigh_ref.head, (foot_ref.tail-foot_ref.head).cross(foot_ref.tail-thigh_ref.head))

            # toes
            toes_ref = get_edit_bone(toes_ref_name+side)
            if toes_ref_name in bones_coords:# toes are optional
                toes_ref.head = bones_coords[toes_ref_name]['head']

                if limb.bone_07 != "":# toes tail defined by toes_end
                    toes_ref.tail = bones_coords["toes_ref"+dupli_idx]['tail']
                else:# if not toes_end, approximate it
                    toes_ref.tail = toes_ref.head + (foot_ref.tail-foot_ref.head)*0.5


            else:
                # align toes with foot
                toes_ref.head = foot_ref.tail.copy()
                toes_ref.tail = toes_ref.head + (foot_ref.tail-foot_ref.head)*0.5
                toes_ref.roll = foot_ref.roll

            #   roll
            align_bone_x_axis(toes_ref,  foot_ref.x_axis)#bones_coords["foot_ref"]['x_axis'])
            if not limb.force_up_axis:
                if limb.up_axis == "-Z":
                    toes_ref.roll += math.radians(180)
                elif limb.up_axis == "X":
                    toes_ref.roll += math.radians(90)
                elif limb.up_axis == "-X":
                    toes_ref.roll += math.radians(-90)

            # no way to evaluate the foot volume atm, without mesh evaluation
            # use approximate heel bones placement, maybe improve later
            heel_mid = get_edit_bone("foot_heel_ref"+dupli_idx+side)
            heel_mid.head[0], heel_mid.head[1], heel_mid.head[2] = foot_ref.head[0], foot_ref.head[1], foot_ref.tail[2]
            heel_mid.tail = foot_ref.tail.copy()
            heel_mid.tail[2] = heel_mid.head[2]
            heel_mid.tail = heel_mid.head + (heel_mid.tail-heel_mid.head)*0.5
            align_bone_x_axis(heel_mid, foot_ref.x_axis)
            #heel_mid.roll += math.radians(180)

            heel_in = get_edit_bone("foot_bank_02_ref"+dupli_idx+side)
            heel_in.head, heel_in.tail, heel_in.roll = heel_mid.head.copy(), heel_mid.tail.copy(), heel_mid.roll
                # use the foot x axis to determine "inside" vector, make sure it's pointing in the right direction for right and left side
            foot_x_axis = foot_ref.x_axis
            vec_test_in = foot_ref.head
            vec_test_out = foot_ref.head + foot_ref.x_axis
            if vec_test_out[0] < vec_test_in[0] and side == ".r":
                foot_x_axis *= -1
            if vec_test_out[0] > vec_test_in[0] and side == ".l":
                foot_x_axis *= -1
            heel_in.head += foot_x_axis.normalized() * foot_ref.length*0.3
            heel_in.tail += foot_x_axis.normalized() * foot_ref.length*0.3

            heel_out = get_edit_bone("foot_bank_01_ref"+dupli_idx+side)
            heel_out.head, heel_out.tail, heel_out.roll = heel_mid.head.copy(), heel_mid.tail.copy(), heel_mid.roll
            foot_x_axis *= -1
            heel_out.head += foot_x_axis.normalized() * foot_ref.length*0.3
            heel_out.tail += foot_x_axis.normalized() * foot_ref.length*0.3

            # check for straight leg angle
            thigh_proj_z = project_vec_onto_plane(thigh_ref.y_axis, thigh_ref.z_axis)
            leg_proj_z = project_vec_onto_plane(leg_ref.y_axis, thigh_ref.z_axis)            
            leg_angle = math.degrees(thigh_proj_z.angle(leg_proj_z))
            if abs(leg_angle) < 0.1:
                print("  Warning: Straight leg angle. Adding offset...")
                iter = 0
                
                while abs(leg_angle) < 0.1 and iter < 1000:# need at least 0.1 angle for the IK constraint to work properly
                    print("iter", iter)
                    foot_dir = foot_ref.tail-foot_ref.head
                    leg_ref.head += foot_dir*0.001
                    leg_angle = math.degrees(leg_ref.y_axis.angle(thigh_ref.y_axis))
                    iter += 1
                    if iter >= 1000:
                        print("  reached max iterations, exit")
                print("  New angle:", leg_angle)

            
            # Toes
            if limb.fingers != 'NONE':
                print('Aligning toes fingers...')
                ref_bones_fingers = {}
                if limb.fingers == "3":
                    ref_bones_fingers = ref_bones_toes_3
                elif limb.fingers == "4":
                    ref_bones_fingers = ref_bones_toes_4
                
                # set head and tail coordinates
                for finger_type in ref_bones_fingers:
                    for finger_ref_name in ref_bones_fingers[finger_type]:
                        finger_ref = get_edit_bone(finger_ref_name+dupli_idx+side)

                        if not finger_ref_name+dupli_idx in bones_coords or finger_ref == None:
                            print("  Finger not found", finger_ref_name+dupli_idx, finger_ref)
                            continue

                        finger_ref.head, finger_ref.tail = bones_coords[finger_ref_name+dupli_idx]['head'], bones_coords[finger_ref_name+dupli_idx]['tail']
                        # make sure the last finger in properly aligned
                        if len(finger_ref.children) == 0:
                            bone_primary_axis = get_bone_primary_axis(limb.primary_axis, bones_coords, finger_ref_name+dupli_idx)
                            finger_length = (finger_ref.tail - finger_ref.head).magnitude
                            finger_ref.tail = finger_ref.head + (bone_primary_axis.normalized() * finger_length)

                # set roll in a second loop since fingers are connected
                for finger_type in ref_bones_fingers:
                    for finger_ref_name in ref_bones_fingers[finger_type]:
                        finger_ref = get_edit_bone(finger_ref_name+dupli_idx+side)

                        if not finger_ref_name+dupli_idx in bones_coords or finger_ref == None:
                            continue

                        # roll
                        if "Y" in limb.up_axis:
                            align_bone_z_axis(finger_ref,  bones_coords[finger_ref_name+dupli_idx]['y_axis'])
                            if "-" in limb.up_axis:
                                finger_ref.roll += math.radians(180)
                        else:
                            align_bone_x_axis(finger_ref,  bones_coords[finger_ref_name+dupli_idx]['x_axis'])
                            if limb.up_axis == "-Z":
                                finger_ref.roll += math.radians(180)
                            elif limb.up_axis == "X":
                                finger_ref.roll += math.radians(90)
                            elif limb.up_axis == "-X":
                                finger_ref.roll += math.radians(-90)
                '''
                # 3 bones fingers, estimate base finger bones position
                if limb.fingers == "3":
                    base_fingers_names = ["index1_base_ref", "middle1_base_ref", "ring1_base_ref", "pinky1_base_ref"]
                    for bfinger_name in base_fingers_names:
                        base_finger = get_edit_bone(bfinger_name+dupli_idx+side)
                        if base_finger == None:# base finger not found, the current finger is probably missing
                            continue
                        base_finger.head = hand_ref.head + (base_finger.tail - hand_ref.head)*0.2
                        align_bone_x_axis(base_finger, hand_ref.x_axis)
                '''
            
        elif limb.type == "ARM":
            side = ".l" if limb.side == "LEFT" else ".r"
            # multi limb support
            dupli_idx = ""

            for bone_ref_name in bones_coords:
                if "_dupli_" in bone_ref_name:
                    dupli_idx = "_dupli_"+str(bone_ref_name[-3:])
                break

            print('  '+dupli_idx+side)
            # store dupli idx for anim remap
            limb.dupli_idx = dupli_idx

            shoulder_ref_name = "shoulder_ref"+dupli_idx
            shoulder_ref = get_edit_bone(shoulder_ref_name+side)

            if shoulder_ref_name in bones_coords:# the shoulder is optional
                shoulder_ref.head = bones_coords[shoulder_ref_name]['head']
                shoulder_ref.tail = bones_coords["arm_ref"+dupli_idx]['head']
                align_bone_z_axis(shoulder_ref, Vector((0, 0, 1)))

                # parent
                bone_parent_name = bones_coords[shoulder_ref_name]['parent_name']
                bone_parent_match_name = get_source_ref_match("SPINE", bone_parent_name)
                print("  Shoulder parent:", bone_parent_name, ">", bone_parent_match_name)
                if bone_parent_match_name:
                    shoulder_ref.parent = get_edit_bone(bone_parent_match_name)

            else:# no shoulder set, auto align shoulder
                shoulder_ref.tail = bones_coords["arm_ref"+dupli_idx]['head']
                forearm_head = bones_coords["forearm_ref"+dupli_idx]['head']
                shoulder_ref.head = shoulder_ref.tail - (forearm_head - shoulder_ref.tail)/2
                align_bone_z_axis(shoulder_ref, Vector((0, 0, 1)))

                # parent
                bone_parent_name = bones_coords["arm_ref"+dupli_idx]['parent_name']
                bone_parent_match_name = get_source_ref_match("SPINE", bone_parent_name)
                print("  Shoulder parent:", bone_parent_name, ">", bone_parent_match_name)
                if bone_parent_match_name:
                    shoulder_ref.parent = get_edit_bone(bone_parent_match_name)

            arm_ref = get_edit_bone("arm_ref"+dupli_idx+side)
            arm_ref.head = bones_coords["arm_ref"+dupli_idx]['head']
            arm_ref.tail = bones_coords["forearm_ref"+dupli_idx]['head']
            hand_ref_name = "hand_ref"+dupli_idx
            forearm_ref = get_edit_bone("forearm_ref"+dupli_idx+side)
            forearm_ref.head = bones_coords["forearm_ref"+dupli_idx]['head']
            forearm_ref.tail = bones_coords[hand_ref_name]['head']    

            # set arms roll
            if "Y" in limb.up_axis_arm:
                align_bone_z_axis(arm_ref,  bones_coords["arm_ref"+dupli_idx]['y_axis'])
                align_bone_z_axis(forearm_ref,  bones_coords["forearm_ref"+dupli_idx]['y_axis'])
            elif "Z" in limb.up_axis_arm:
                align_bone_z_axis(arm_ref,  bones_coords["arm_ref"+dupli_idx]['z_axis'])
                align_bone_z_axis(forearm_ref,  bones_coords["forearm_ref"+dupli_idx]['z_axis'])
            elif "X" in limb.up_axis_arm:
                align_bone_z_axis(arm_ref,  bones_coords["arm_ref"+dupli_idx]['x_axis'])
                align_bone_z_axis(forearm_ref,  bones_coords["forearm_ref"+dupli_idx]['x_axis']) 
            if "-" in limb.up_axis_arm:
                arm_ref.roll += math.radians(180)
                forearm_ref.roll += math.radians(180)
            
            hand_ref = get_edit_bone(hand_ref_name+side)
            hand_ref.head = bones_coords[hand_ref_name]['head']
            hand_length = (bones_coords[hand_ref_name]['tail'] - bones_coords[hand_ref_name]['head']).magnitude
            bone_primary_axis = get_bone_primary_axis(limb.primary_axis, bones_coords, hand_ref_name)

            hand_ref.tail = hand_ref.head + bone_primary_axis.normalized() * hand_length#bones_coords["hand_ref"]['tail']

            if "Y" in limb.up_axis:
                align_bone_z_axis(hand_ref,  bones_coords[hand_ref_name]['y_axis'])
            elif "Z" in limb.up_axis:
                align_bone_z_axis(hand_ref,  bones_coords[hand_ref_name]['z_axis'])
            elif "X" in limb.up_axis:
                align_bone_x_axis(hand_ref,  bones_coords[hand_ref_name]['x_axis'])
                hand_ref.roll += math.radians(90)
            if "-" in limb.up_axis:
                hand_ref.roll += math.radians(180)

            # check for straight arm angle            
            arm_proj_z = project_vec_onto_plane(arm_ref.y_axis, arm_ref.z_axis)
            forearm_proj_z = project_vec_onto_plane(forearm_ref.y_axis, arm_ref.z_axis)
            arm_angle = math.degrees(arm_proj_z.angle(forearm_proj_z))
            if abs(arm_angle) < 0.1:
                print("  Warning: Straight arm angle. Adding offset...")

                fac = -1 if '-' in limb.IK_axis_correc else 1
                vec = Vector((fac*1,0,0))
                if 'Y' in limb.IK_axis_correc:
                    vec = Vector((0,fac*1,0))
                elif 'Z' in limb.IK_axis_correc:
                    vec = Vector((0,0,fac*1))


                t = 0
                while abs(arm_angle) < 0.1 and t < 1000:# need at least 0.1 angle for the IK constraint to work properly
                    add_vec = vec * (arm_ref.tail - arm_ref.head).magnitude*0.5# need to find a better way to evaluate the elbow direction. By default use the Y axis
                    forearm_ref.head += add_vec * 0.001
                    arm_angle = math.degrees(arm_ref.y_axis.angle(forearm_ref.y_axis))
                    t += 1

                print("  New angle:", arm_angle)
            
            # fingers
            if limb.fingers != "NONE":
                ref_bones_fingers = {}
                if limb.fingers == "3":
                    ref_bones_fingers = ref_bones_fingers_3
                elif limb.fingers == "4":
                    ref_bones_fingers = ref_bones_fingers_4

                # set head and tail coordinates
                for finger_type in ref_bones_fingers:
                    for finger_ref_name in ref_bones_fingers[finger_type]:
                        finger_ref = get_edit_bone(finger_ref_name+dupli_idx+side)

                        if not finger_ref_name+dupli_idx in bones_coords or finger_ref == None:
                            print("  Finger not found", finger_ref_name+dupli_idx, finger_ref)
                            continue

                        finger_ref.head, finger_ref.tail = bones_coords[finger_ref_name+dupli_idx]['head'], bones_coords[finger_ref_name+dupli_idx]['tail']
                        # make sure the last finger in properly aligned
                        if len(finger_ref.children) == 0:
                            bone_primary_axis = get_bone_primary_axis(limb.primary_axis, bones_coords, finger_ref_name+dupli_idx)
                            finger_length = (finger_ref.tail - finger_ref.head).magnitude
                            finger_ref.tail = finger_ref.head + (bone_primary_axis.normalized() * finger_length)

                # set roll in a second loop since fingers are connected
                for finger_type in ref_bones_fingers:
                    for finger_ref_name in ref_bones_fingers[finger_type]:
                        finger_ref = get_edit_bone(finger_ref_name+dupli_idx+side)

                        if not finger_ref_name+dupli_idx in bones_coords or finger_ref == None:
                            continue

                        # roll
                        if "Y" in limb.up_axis:
                            align_bone_z_axis(finger_ref,  bones_coords[finger_ref_name+dupli_idx]['y_axis'])
                            if "-" in limb.up_axis:
                                finger_ref.roll += math.radians(180)
                        else:
                            align_bone_x_axis(finger_ref,  bones_coords[finger_ref_name+dupli_idx]['x_axis'])
                            if limb.up_axis == "-Z":
                                finger_ref.roll += math.radians(180)
                            elif limb.up_axis == "X":
                                finger_ref.roll += math.radians(90)
                            elif limb.up_axis == "-X":
                                finger_ref.roll += math.radians(-90)

                # 3 bones fingers, estimate base finger bones position
                if limb.fingers == "3":
                    base_fingers_names = ["index1_base_ref", "middle1_base_ref", "ring1_base_ref", "pinky1_base_ref"]
                    for bfinger_name in base_fingers_names:
                        base_finger = get_edit_bone(bfinger_name+dupli_idx+side)
                        if base_finger == None:# base finger not found, the current finger is probably missing
                            continue
                        base_finger.head = hand_ref.head + (base_finger.tail - hand_ref.head)*0.2
                        align_bone_x_axis(base_finger, hand_ref.x_axis)


        elif limb.type == "SPINE":
            side = ".x"

            # root
            root_ref = get_edit_bone("root_ref"+side)
            root_ref.head = bones_coords["root_ref"]['head']
            spine_01_head = bones_coords["spine_01_ref"]['head']

            # check the head pos is not same as spine1 pos (typically, inverted pelvis bone direction case)
            same_pos = [False, False, False]

            for i in range(0, 3):
                if round(spine_01_head[i], 4) == round(root_ref.head[i], 4):
                    same_pos[i] = True

            if same_pos == [True, True, True]:
                print("Warning, root_ref head pos same as tail pos (null length), then use tail position as head instead")
                root_ref.head = bones_coords["root_ref"]['tail']

            if limb.connect:
                root_ref.tail = spine_01_head
            else:
                bone_primary_axis = get_bone_primary_axis(limb.primary_axis, bones_coords, "root_ref")
                root_ref_length = (spine_01_head-root_ref.head).magnitude
                root_ref.tail = root_ref.head + (bone_primary_axis.normalized() * root_ref_length)

            if limb.force_z_axis:
                align_bone_z_axis(root_ref, Vector((0, -1, 0)))
            else:
                align_bone_x_axis(root_ref, bones_coords["root_ref"]['x_axis'])

            # other spines
            prev_spine_ref_name = "root_ref"+side
            source_spine_names = [limb.bone_02, limb.bone_03, limb.bone_04, limb.bone_05, limb.bone_06, limb.bone_07]

            for idx, source_spine_name in enumerate(source_spine_names):
                if source_spine_name != "":
                    str_idx = '%02d' % (idx+1)
                    prev_str_idx = '%02d' % idx
                    spine_ref_name_no_side = "spine_"+str_idx+"_ref"
                    spine_ref_name = spine_ref_name_no_side+side
                    spine_ref = get_edit_bone(spine_ref_name)
                    if idx > 0:
                        prev_spine_ref_name = "spine_"+prev_str_idx+"_ref"+side

                    prev_spine_ref = get_edit_bone(prev_spine_ref_name)
                    spine_ref.head = bones_coords[spine_ref_name_no_side]['head']
                    if limb.connect:
                        spine_ref.tail = spine_ref.head + (prev_spine_ref.tail - prev_spine_ref.head)
                    else:
                        bone_primary_axis = get_bone_primary_axis(limb.primary_axis, bones_coords, spine_ref_name_no_side)
                        spine_ref_length = (prev_spine_ref.tail - prev_spine_ref.head).magnitude
                        spine_ref.tail = spine_ref.head + (bone_primary_axis.normalized() * spine_ref_length)
            
            
            # Align roll (Y axis)
            for idx, source_spine_name in enumerate(source_spine_names):
                if source_spine_name != "":
                    str_idx = '%02d' % (idx+1)
                    prev_str_idx = '%02d' % idx
                    spine_ref_name_no_side = "spine_"+str_idx+"_ref"
                    spine_ref_name = spine_ref_name_no_side+side
                    spine_ref = get_edit_bone(spine_ref_name)
               
                    if limb.force_z_axis:
                        align_bone_z_axis(spine_ref, Vector((0, -1, 0)))
                    else:
                        align_bone_x_axis(spine_ref, bones_coords[spine_ref_name_no_side]['x_axis'])
                      
            # root up
            if limb.pelvis_up:
                # disconnect the first spine
                first_spine_name = "spine_01_ref.x"
                first_spine = get_edit_bone(first_spine_name)
                if first_spine:
                    first_spine.use_connect = False
                
                # set root up
                # get spine vec
                last_spine_idx = spine_bones_count-1
                str_idx = '%02d' % (last_spine_idx)                
                last_spine_name = "spine_"+str_idx+"_ref.x"
                last_spine = get_edit_bone(last_spine_name)
                spine_vec = last_spine.tail - root_ref.head
                root_ref.tail = root_ref.head + Vector((0,0,spine_vec.magnitude*0.2))
                
                if limb.force_z_axis:
                    align_bone_z_axis(root_ref, Vector((0, -1, 0)))
                else:
                    align_bone_x_axis(root_ref, bones_coords["root_ref"]['x_axis'])

        elif limb.type == "HEAD":
            side = ".x"
            subneck_ref = None
            last_subneck_ref = None

            # subnecks
            if limb.neck_bones_amount > 1:

                for i in range(2, limb.neck_bones_amount+1):
                    subneck_name = "subneck_"+str(i-1)+"_ref"
                    next_subneck_name = "subneck_"+str(i)+"_ref"
                    subneck_ref = get_edit_bone(subneck_name+side)
                    last_subneck_ref = subneck_ref
                    subneck_ref.use_connect = False
                    subneck_ref.head = bones_coords[subneck_name]['head']

                    if i == limb.neck_bones_amount:# last subneck, connect to neck
                        subneck_ref.tail = bones_coords["neck_ref"]['head']
                    else:
                        subneck_ref.tail = bones_coords[next_subneck_name]['head']

                    if limb.force_z_axis:
                        align_bone_z_axis(subneck_ref, Vector((0, -1, 0)))
                    else:
                        align_bone_x_axis(subneck_ref, bones_coords[subneck_name]['x_axis'])

                    # parent
                    bone_parent_name = bones_coords[subneck_name]['parent_name']
                    bone_parent_match_name = get_source_ref_match("SPINE", bone_parent_name)
                    print("  Neck parent: "+str(bone_parent_name)+" > "+str(bone_parent_match_name))
                    if bone_parent_match_name:
                        subneck_ref.parent = get_edit_bone(bone_parent_match_name)
            """
            # two neck bones (subneck1, neck)
            if limb.bone_04 != "":
                subneck_ref = get_edit_bone("subneck_1_ref"+side)
                subneck_ref.use_connect = False
                subneck_ref.head = bones_coords["subneck_1_ref"]['head']
                subneck_ref.tail = bones_coords["neck_ref"]['head']
                if limb.force_z_axis:
                    align_bone_z_axis(subneck_ref, Vector((0, -1, 0)))
                else:
                    align_bone_x_axis(subneck_ref, bones_coords["subneck_ref"]['x_axis'])

                # parent
                bone_parent_name = bones_coords["subneck_1_ref"]['parent_name']
                bone_parent_match_name = get_source_ref_match("SPINE", bone_parent_name)
                print("  Neck parent: "+str(bone_parent_name)+" > "+str(bone_parent_match_name))
                if bone_parent_match_name:
                    subneck_ref.parent = get_edit_bone(bone_parent_match_name)
            """

            neck_ref = get_edit_bone("neck_ref"+side)
            neck_ref.use_connect = False
            parent_ref = "neck_ref"
            if "neck_ref" in bones_coords:# neck is optional
                neck_ref.head = bones_coords["neck_ref"]['head']
                neck_ref.tail = bones_coords["head_ref"]['head']
                if limb.force_z_axis:
                    align_bone_z_axis(neck_ref, Vector((0, -1, 0)))
                else:
                    align_bone_x_axis(neck_ref, bones_coords["neck_ref"]['x_axis'])

            else:# no neck set, auto align
                parent_ref = "head_ref"
                neck_ref.tail = bones_coords["head_ref"]['head']
                head_end = bones_coords["head_ref"]['tail']
                neck_ref.head = neck_ref.tail - (head_end - neck_ref.tail)/2
                align_bone_x_axis(neck_ref, bones_coords["head_ref"]['x_axis'])

            # parent
            if limb.neck_bones_amount == 1:#no subnecks
            #if limb.bone_04 == "":# no subneck
                bone_parent_name = bones_coords[parent_ref]['parent_name']
                bone_parent_match_name = get_source_ref_match("SPINE", bone_parent_name)
                print("  Neck parent:", bone_parent_name, ">", bone_parent_match_name)
                if bone_parent_match_name:
                    neck_ref.parent = get_edit_bone(bone_parent_match_name)
            else:# subneck_1
                neck_ref.parent = last_subneck_ref#subneck_ref

            head_ref = get_edit_bone("head_ref"+side)
            head_ref.head = bones_coords["head_ref"]['head']
            #head_ref.tail = bones_coords["head_ref"]['tail']
            head_length = (bones_coords["head_ref"]['tail'] - bones_coords["head_ref"]['head']).magnitude
            bone_primary_axis = get_bone_primary_axis(limb.primary_axis, bones_coords, "head_ref")
            head_ref.tail = head_ref.head + bone_primary_axis.normalized() * head_length

            if limb.force_z_axis:
                align_bone_z_axis(head_ref, Vector((0, -1, 0)))
            else:
                align_bone_x_axis(head_ref, bones_coords["head_ref"]['x_axis'])

        elif limb.type == 'TAIL':
            
            side = '.x'
            if limb.side == 'LEFT':
                side = '.l' 
            elif limb.side == 'RIGHT':
                side = '.r'

            # multi limb support
            dupli_idx = ''

            for bone_ref_name in bones_coords:
                if "_dupli_" in bone_ref_name:
                    dupli_idx = "_dupli_"+str(bone_ref_name[-3:])
                break

            # store dupli idx for anim remap
            limb.dupli_idx = dupli_idx           
            
            for idx in range(0, len(bones_coords)):
                bones_coords_keys = list(bones_coords.keys())
                ref_name_no_side = bones_coords_keys[idx]
                print('Align tail bone', ref_name_no_side+side)
                tail_ref_name = ref_name_no_side+side
                tail_ref = get_edit_bone(tail_ref_name)  
                tail_ref_prev = None
                if idx > 0:                
                    tail_prev_name = bones_coords_keys[idx-1]+side
                    tail_ref_prev = get_edit_bone(tail_prev_name)
                    
                tail_ref.head = bones_coords[ref_name_no_side]['head']
                if limb.connect and tail_ref_prev:
                    tail_ref.tail = tail_ref.head + (tail_ref_prev.tail - tail_ref_prev.head)
                else:
                    bone_primary_axis = get_bone_primary_axis(limb.primary_axis, bones_coords, ref_name_no_side)
                    tail_ref_length = 1.0
                    if tail_ref_prev:
                        tail_ref_length = (tail_ref_prev.tail - tail_ref_prev.head).magnitude
                    else:
                        tail_next_name = bones_coords_keys[idx+1]+side
                        tail_next = get_edit_bone(tail_next_name)
                        tail_ref_length = (tail_next.head - tail_ref.head).magnitude
                    tail_ref.tail = tail_ref.head + (bone_primary_axis.normalized() * tail_ref_length)
            
            
            # Align roll (Y axis)
            for idx, ref_name_no_side in enumerate(bones_coords):
                if ref_name_no_side != "":
                    str_idx = '%02d' % idx
                    prev_str_idx = '%02d' % (idx-1)
                    tail_ref_name = ref_name_no_side+side
                    tail_ref = get_edit_bone(tail_ref_name)
                    align_bone_x_axis(tail_ref, bones_coords[ref_name_no_side]['x_axis'])
           
                    
            
    # Fix microscopic bones scale issue with certain imported skeletons
    # set the tiny bone length  equal to the parent bone length
    for ebone in arp_armature.data.edit_bones:
        if not is_bone_in_layer(ebone.name, 'Reference', idx=17):
            continue
        if len(ebone.children):# only "leaf" bones
            continue
        bparent = ebone.parent
        if bparent:
            ebone_length = (ebone.tail-ebone.head).magnitude
            bparent_length = (bparent.tail-bparent.head).magnitude
            if ebone_length < bparent_length/20:
                ebone.tail = ebone.head + (ebone.tail-ebone.head).normalized() * bparent_length

    
    # try to set correct shape scale for spine bones
    #   get armature height
    bot = 100000000
    top = -100000000
    for b in arp_armature.data.edit_bones:
        if not is_bone_in_layer(b.name, 'Reference', idx=17):
            continue
        if b.head[2] < bot:
            bot = b.head[2]
        if b.head[2] > top:
            top = b.head[2]
            
    height = top-bot
    print('Armature height:', height)
    
    # compare it with the root_ref bone length
    root_ref = get_edit_bone('root_ref.x')
    c_root_master_scale_fac = 1.0
    
    if root_ref:
        length = (root_ref.tail-root_ref.head).magnitude
        ratio = length/height
        c_root_master_scale_fac = 1 / (ratio/0.06)
        
        
    bpy.ops.object.mode_set(mode='POSE')
    
    # set custom shape scale
    if c_root_master_scale_fac != 1.0:
        c_root_master = get_pose_bone('c_root_master.x')
        set_custom_shape_scale(c_root_master, c_root_master_scale_fac)
        

    # Add orphan bones constraints
    if len(self.orphan_bones_dict) and self.orphan_copy_cns:
        print("Copy orphan bones ChildOf constraints")
        enable_layer(self.orphan_bones_collection, idx=self.orphan_bones_layer)

        # add constraints
        for or_name in self.orphan_bones_dict:
            orphan_pbone = get_pose_bone(or_name)
            if orphan_pbone == None:
                continue

            if not 'constraints' in self.orphan_bones_dict[or_name]:
                continue

            cns_multi_dict = self.orphan_bones_dict[or_name]['constraints']
            pose_bone_constraints_from_dict(arp_armature, orphan_pbone, cns_multi_dict)

        # set inverse matrix of ChildOf constraints
        print('  set inverse matrix')
        set_childof_inverse(self)

    
    # Drawing options    
    if len(self.orphan_bones_dict):
    
        if bpy.app.version < (4,0,0):
            # orphan bones color group
                                   
            group_name = "Custom Controllers"
            group = arp_armature.pose.bone_groups.get(group_name)
            if group == None:  # the group doesn't exist yet, create it
                group = arp_armature.pose.bone_groups.new(name=group_name)
                group.color_set = "CUSTOM"
            group.colors.normal = self.color_orphan_group

            for i, channel in enumerate(group.colors.select):
                group.colors.select[i] = self.color_orphan_group[i] + 0.4
            for i, channel in enumerate(group.colors.active):
                group.colors.active[i] = self.color_orphan_group[i] + 0.5

        if self.orphan_bones_shape != "None":
            # Orphan bones drawing style
            for or_name in self.orphan_bones_dict:
                orphan_pbone = get_pose_bone(or_name)
                if orphan_pbone == None:
                    print("Warning, orphan bone not found:", or_name)

                # color
                if bpy.app.version >= (4,0,0):
                    normal_color = self.color_orphan_group
                    sel_color = [i+0.4 for i in normal_color]
                    active_color = [i+0.6 for i in normal_color]
                    set_bone_color(orphan_pbone.bone, [normal_color, sel_color, active_color])
                else:
                    orphan_pbone.bone_group = group
                
                # custom shape
                orphan_pbone.custom_shape = get_object(self.orphan_bones_shape)
                if orphan_pbone.custom_shape:
                    set_custom_shape_scale(orphan_pbone, self.orphan_bones_scale)

                # Set is as custom controller for ARP export
                orphan_pbone["cc"] = 1
                orphan_pbone.bone["cc"] = 1

    # Disable custom shape override transform for the shoulder, generally looks too far from the shoulder position otherwise
    for pbone in arp_armature.pose.bones:
        if pbone.name.startswith("c_shoulder"):
            pbone.custom_shape_transform = None

    # Set neck auto twist values
    if self.neck_auto_twist:
        for limb_item in scn.limb_map:
            if limb_item.type == "HEAD":
                side = ".x"

                for i in range(2, limb_item.neck_bones_amount+1):
                    subneck = get_pose_bone("c_subneck_"+str(i-1)+side)
                    if subneck:
                        subneck["neck_twist"] = 1.0

    bpy.ops.object.mode_set(mode='EDIT')

    # --Skinning--
    # Set armature modifier
    skinned_objects = []
    for obj in bpy.data.objects:
        if obj.type != "MESH":
            continue

        # switch armature modifier object
        if len(obj.modifiers):
            for mod in obj.modifiers:
                if mod.type != "ARMATURE":
                    continue

                if mod.object == source_skeleton:
                    if self.mode == 'CONVERT':
                        mod.object = arp_armature

                    mod.use_deform_preserve_volume = self.preserve_volume

                    if not obj in skinned_objects:
                        skinned_objects.append(obj)


    if self.mode == 'PRESERVE':
        # constrain source bones to ARP bones

        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        set_active_object(source_skeleton.name)
        bpy.ops.object.mode_set(mode='POSE')

        for pbone in source_skeleton.pose.bones:
            bone_qr_offset_name = pbone.name+'_qr_offset'
            bone_qr_offset = arp_armature.data.bones.get(bone_qr_offset_name)
            if bone_qr_offset:
                cns = pbone.constraints.new('COPY_TRANSFORMS')
                cns.name = 'CopyTransforms_QR'
                cns.target = arp_armature
                cns.subtarget = bone_qr_offset_name

                cns2 = pbone.constraints.new('COPY_SCALE')
                cns2.name = 'CopyScale_QR'
                cns2.target = arp_armature
                cns2.subtarget = bone_qr_offset_name
                cns2.target_space = cns2.owner_space = 'POSE'

        for or_name in orphan_bones:
            or_pbone = source_skeleton.pose.bones.get(or_name)
            cor_bone = arp_armature.data.bones.get(or_name)
            if cor_bone == None:
                cor_bone = arp_armature.data.bones.get('cor_'+or_name)

            if or_pbone and cor_bone:
                cns = or_pbone.constraints.get('CopyTransforms_QR')
                if cns == None:
                    cns = or_pbone.constraints.new('COPY_TRANSFORMS')
                    cns.name = 'CopyTransforms_QR'
                    cns.target = arp_armature
                    cns.subtarget = cor_bone.name

                cns2 = or_pbone.constraints.get('CopyScale_QR')
                if cns2 == None:
                    cns2 = or_pbone.constraints.new('COPY_SCALE')
                    cns2.name = 'CopyScale_QR'
                    cns2.target = arp_armature
                    cns2.subtarget = cor_bone.name
                    cns2.target_space = cns2.owner_space = 'POSE'


        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        set_active_object(arp_armature.name)

        # tag as locked armature to prevent edition
        arp_armature.data["arp_locked"] = True


    # replace vertex groups names
    if self.mode == 'CONVERT':

        for obj in skinned_objects:
            if len(obj.vertex_groups):
                for vgroup in obj.vertex_groups:
                    if vgroup.name in skin_dict:
                        new_name = skin_dict[vgroup.name]['deform']

                        # handles names conflict
                        new_grp = obj.vertex_groups.get(new_name)
                        if new_grp != None:
                            new_grp.name = new_name+"_OLDGROUP"

                        if new_name in skin_dict:
                            skin_dict[new_name+"_OLDGROUP"] = skin_dict[new_name]
                            del skin_dict[new_name]

                        vgroup.name = new_name


        # clears up temporary renaming in dict
        for n in skin_dict.copy():
            if n.endswith("_OLDGROUP"):
                skin_dict[n.replace("_OLDGROUP", "")] = skin_dict[n]
                del skin_dict[n]

    
    skinned_objects_dict = {}
    meshes_transf_dict = {}
    
    for obj in skinned_objects:
        skinned_objects_dict[obj.name] = {}
        meshes_transf_dict[obj.name] = obj.location, obj.rotation_euler, obj.rotation_quaternion, obj.scale

    # retarget drivers data path
    if len(self.orphan_bones_dict) and self.retarget_sk_drivers:
        print("Retarget shape keys drivers...")

        for obj in skinned_objects:
            drivers_save = {}

            sk = obj.data.shape_keys
            if sk == None:
                continue

            anim_data = obj.data.shape_keys.animation_data
            if anim_data == None:
                continue

            drivers = anim_data.drivers
            if drivers == None:
                continue

            for fc_driver in drivers:
                dr = fc_driver.driver

                var_save = {}

                for var in dr.variables:
                    for i, tar in enumerate(var.targets):
                        ids = []
                        bone_targets = []

                        if tar.id == source_skeleton:
                            tar.id = arp_armature
                            ids.append(source_skeleton.name)

                        if tar.bone_target != "":
                            for or_name in self.orphan_bones_dict:
                                if self.orphan_bones_dict[or_name]['original_name'] == tar.bone_target:
                                    bone_targets.append(tar.bone_target)
                                    tar.bone_target = or_name
                                    break

                        var_save[var.name] = {'ids':ids, 'bone_targets':bone_targets}

                drivers_save[fc_driver.data_path] = var_save

            skinned_objects_dict[obj.name] = drivers_save


    # store quick rig data in props
    arp_qr_data = {'skinned_objects': skinned_objects_dict, 'vgroups': skin_dict, 'base_armature': source_skeleton.name, 
                    'meshes_parented_to_bones': self.meshes_parented_to_bones, 'meshes_transf': meshes_transf_dict,
                    }
    arp_armature.data['arp_qr_data'] = arp_qr_data


    if self.mode == 'CONVERT':
        bpy.ops.object.mode_set(mode='POSE')

        # add meshes to rig collection
        arm_col = arp_armature.users_collection[0]
        master_rig_col = bpy.data.collections.get(arm_col.name[:-4])# trim '_rig'

        if master_rig_col:
            for obj in skinned_objects:
                try:
                    master_rig_col.objects.link(obj)
                except:# already in
                    pass

            for obj_name in self.meshes_parented_to_bones:
                o = get_object(obj_name)
                try:
                    master_rig_col.objects.link(o)
                except:# already in
                    pass
        else:
            print("Rig collection not found, could not set objects in")

        bpy.ops.object.mode_set(mode='EDIT')

    self.skin_dict = skin_dict
    # end make_rig()
    

def get_bone_primary_axis(primary_axis, bones_coords, bone_name):
    if primary_axis == "X":
        return bones_coords[bone_name]['x_axis']
    elif primary_axis == "-X":
        return -bones_coords[bone_name]['x_axis']

    elif primary_axis == "Y":
        return bones_coords[bone_name]['y_axis']
    elif primary_axis == "-Y":
        return -bones_coords[bone_name]['y_axis']

    elif primary_axis == "Z":
        return bones_coords[bone_name]['z_axis']
    elif primary_axis == "-Z":
        return -bones_coords[bone_name]['z_axis']


def _pick_bone(self):
    current_mode = get_current_mode()
    scn = bpy.context.scene

    bpy.ops.object.mode_set(mode='EDIT')
    rig = get_object(bpy.context.active_object.name)

    # disable X mirror
    xmirror_state = rig.data.use_mirror_x
    rig.data.use_mirror_x = False
    valid = True
    if len(bpy.context.selected_editable_bones) == 0:
        self.report({'ERROR'}, "No bone selected: select a bone.")
        valid = False

    if valid:
        selected_bone_name = bpy.context.selected_editable_bones[0].name
        setattr(scn.limb_map[scn.limb_map_index], self.value, selected_bone_name)

    # restore mode and x mirror
    restore_current_mode(current_mode)
    rig.data.use_mirror_x = xmirror_state
    

def _mirror_limb(self):
    scn = bpy.context.scene
    limb = scn.limb_map[scn.limb_map_index]
    rig = bpy.context.active_object
    
    if not limb.side in ['LEFT', 'RIGHT']:
        self.report({'ERROR'}, 'This is not a left or right limb, cannot be mirrored')
        return
    
    print(limb.name)
    print(limb.side)
    
    # find mirrorred limb if any
    mirror_side = 'RIGHT' if limb.side == 'LEFT' else 'LEFT'
    mirror_limb = None
    
    print('Look for mirror limb', mirror_side, limb.type)
    
    for l in scn.limb_map:
        #print(limb.type, l.type, mirror_side, l.side)
        if limb.type == l.type and l.side == mirror_side:
            print('Found mirror', l.name)
            # check dupli
            if '_dupli_' in limb.name:
                if get_bone_side(limb.name) == get_bone_side(l.name):
                    mirror_limb = l
                    break
                    
            mirror_limb = l
            break
    
    if mirror_limb:
        print('Mirror limb found:', mirror_limb.name)
    else:
        # create mirror limb
        cur_side = get_bone_side(limb.name)
        mirror_side_name = cur_side[:-2]+'.l' if cur_side.endswith('.r') else cur_side[:-2]+'.r'
        mirror_limb_name = get_bone_base_name(limb.name)+mirror_side_name
        print('Create mirror limb', limb.type, mirror_limb_name)
        
        mirror_limb = scn.limb_map.add()
        mirror_limb.name = mirror_limb_name
        mirror_limb.side = mirror_side
        mirror_limb.type = limb.type
    
    # Copy and mirror props
    for prop_name in dir(limb):
        
        # exclude invalid class props
        invalid_prop = False
        if prop_name in ['name', 'side']:
            invalid_prop = True
        for i in ['__', 'rna_', 'bl_rna']:
            if prop_name.startswith(i):
                invalid_prop = True
        if invalid_prop:
            continue
        
        
        val = getattr(limb, prop_name)
        
        # Mirror prop value
        sides_dict = {'l': 'r', 'left': 'right'}
        reverse_dict = {}
        for i in sides_dict:
            reverse_dict[sides_dict[i]] = i
        sides_dict.update(reverse_dict)
        
        def get_mirror_side(side_word):
            mirror_word = None
            
            for dict_word in sides_dict:
                if dict_word == side_word:
                    mirror_word = sides_dict[dict_word]
                if dict_word.upper() == side_word:# upper case
                    mirror_word = sides_dict[dict_word].upper()
                if dict_word.title() == side_word:# capital first
                    mirror_word = sides_dict[dict_word].title()
                    
            return mirror_word
            
        
        if type(val) == str:
            # bone 
            if rig.data.bones.get(val):                
                for sep in ['.', '_', ' ']:
                    split = val.split(sep)
                    
                    if len(split) == 0:
                        continue
                        
                    # side suffix
                    suff = split[len(split)-1]#.l, .r, _left ...
                    
                    mirror_word = get_mirror_side(suff)
                    if mirror_word:
                        val = val[:-len(suff)]+mirror_word            
                        break
                        
                    # prefix
                    pref = split[0]#l., r., right_
                    mirror_word = get_mirror_side(pref)
                    if mirror_word:
                        val = mirror_word + val[len(pref):]
                        break            

                    # inside
                    for wordi, word in enumerate(split):#thigh right twist
                        mirror_word = get_mirror_side(word)
                        if mirror_word:
                            val = ''
                            for _i, _word in enumerate(split):
                                val += _word if _i != wordi else mirror_word
                                if _i != len(split)-1:
                                    val += sep
            
                # ensure the mirror bone name is valid
                if rig.data.bones.get(val):
                    setattr(mirror_limb, prop_name, val)
                else:
                    #print('Mirror bone not found:', val)
                    self.mirrors_not_found.append(val)
            
            else:# string but not bone
                setattr(mirror_limb, prop_name, val)
                #print('Set prop', prop_name, val)
            
        else:# non string data
            setattr(mirror_limb, prop_name, val)
            #print('Set prop', prop_name, val)
    
    
    # Sort the mirror limb in the list
    mirror_index = 0
    for i in range(0, len(scn.limb_map)):
        if scn.limb_map[i] == mirror_limb:
            mirror_index = i
            break

    try:
        scn.limb_map.move(mirror_index, scn.limb_map_index+1)
    except:
        pass

    

def _add_limb(self):
    input_type = self.type
    current_mode = get_current_mode()
    scn = bpy.context.scene

    bpy.ops.object.mode_set(mode='EDIT')
    rig = get_object(bpy.context.active_object.name)

    # disable X mirror
    xmirror_state = rig.data.use_mirror_x
    rig.data.use_mirror_x = False

    # create new limb item in the list
    new_item = scn.limb_map.add()
    new_item.name = input_type.title()
    new_item.type = input_type
    scn.limb_map_index = len(scn.limb_map)-1

    # if bones are selected, try to make an automatic match based on the hierarchy
    if len(bpy.context.selected_editable_bones):
        active_bone = bpy.context.selected_editable_bones[0]
        
        if input_type == "LEG":
            thigh_bone = active_bone
            thigh_twist_bone = None            
            thigh_twist2_bone = None
            thigh_twist3_bone = None
            thigh_twist4_bone = None
            thigh_twist5_bone = None
            thigh_twist6_bone = None
            thigh_twist7_bone = None
            thigh_twist_count = 0
            calf_bone = None
            calf_twist_bone = None
            calf_twist2_bone = None
            calf_twist3_bone = None
            calf_twist4_bone = None
            calf_twist5_bone = None
            calf_twist6_bone = None
            calf_twist7_bone = None
            calf_twist_count = 0
            foot_bone = None
            toes_bone = None
            toes_end_bone = None

            if thigh_bone.children:
                # calf
                for child in thigh_bone.children:
                    if child.children:
                        calf_bone = child

                # thigh twists
                for thigh_child in thigh_bone.children:
                    if "twist" in thigh_child.name.lower():
                        if thigh_twist_count == 0:
                            thigh_twist_bone = thigh_child
                        elif thigh_twist_count == 1:
                            thigh_twist2_bone = thigh_child
                        elif thigh_twist_count == 2:
                            thigh_twist3_bone = thigh_child
                        elif thigh_twist_count == 3:
                            thigh_twist4_bone = thigh_child
                        elif thigh_twist_count == 4:
                            thigh_twist5_bone = thigh_child
                        elif thigh_twist_count == 5:
                            thigh_twist6_bone = thigh_child
                        elif thigh_twist_count == 6:
                            thigh_twist7_bone = thigh_child
                        thigh_twist_count += 1

            if calf_bone:
                # calf twists
                for calf_child in calf_bone.children:
                    if "twist" in calf_child.name.lower():
                        if calf_twist_count == 0:
                            calf_twist_bone = calf_child
                        elif calf_twist_count == 1:
                            calf_twist2_bone = calf_child
                        elif calf_twist_count == 2:
                            calf_twist3_bone = calf_child
                        elif calf_twist_count == 3:
                            calf_twist4_bone = calf_child
                        elif calf_twist_count == 4:
                            calf_twist5_bone = calf_child
                        elif calf_twist_count == 5:
                            calf_twist6_bone = calf_child
                        elif calf_twist_count == 6:
                            calf_twist7_bone = calf_child
                        calf_twist_count += 1

                    # foot
                    if calf_child.children and not "twist" in calf_child.name.lower():
                        foot_bone = calf_child                        

            if thigh_bone:
                new_item.bone_01 = thigh_bone.name
                
            if thigh_twist_bone:
                new_item.bone_02 = thigh_twist_bone.name
            if thigh_twist2_bone:
                new_item.bone_twist_02_01 = thigh_twist2_bone.name
            if thigh_twist3_bone:
                new_item.bone_twist_03_01 = thigh_twist3_bone.name
            if thigh_twist4_bone:
                new_item.bone_twist_04_01 = thigh_twist4_bone.name
            if thigh_twist5_bone:
                new_item.bone_twist_05_01 = thigh_twist5_bone.name
            if thigh_twist6_bone:
                new_item.bone_twist_06_01 = thigh_twist6_bone.name
            if thigh_twist7_bone:
                new_item.bone_twist_07_01 = thigh_twist7_bone.name
            
            if calf_bone:
                new_item.bone_03 = calf_bone.name
            if calf_twist_bone:
                new_item.bone_04 = calf_twist_bone.name
            if calf_twist2_bone:
                new_item.bone_twist_02_02 = calf_twist2_bone.name
            if calf_twist3_bone:
                new_item.bone_twist_03_02 = calf_twist3_bone.name
            if calf_twist4_bone:
                new_item.bone_twist_04_02 = calf_twist4_bone.name
            if calf_twist5_bone:
                new_item.bone_twist_05_02 = calf_twist5_bone.name
            if calf_twist6_bone:
                new_item.bone_twist_06_02 = calf_twist6_bone.name
            if calf_twist7_bone:
                new_item.bone_twist_07_02 = calf_twist7_bone.name
            

            if foot_bone:
                new_item.bone_05 = foot_bone.name
                
                if len(foot_bone.children):
                    toes_bone = foot_bone.children[0]
                            
            if toes_bone:
                new_item.bone_06 = toes_bone.name
                if len (toes_bone.children) == 1:
                    toes_end_bone = toes_bone.children[0]
                        
            if toes_end_bone:
                new_item.bone_07 = toes_end_bone.name

            new_item.twist_bones_amount = thigh_twist_count if thigh_twist_count > calf_twist_count else calf_twist_count# always use the greater twist count found

            # evaluate the foot up axis
            #   look for the axis with highest magnitude in Z among X and Z
            if foot_bone:
                vec_in = rig.matrix_world @ foot_bone.head.copy()
                vec_out = vec_in + (foot_bone.x_axis*10)# x_axis and z_axis are in world space
                x_z_vec = (vec_out[2] - vec_in[2])

                vec_out = vec_in + (foot_bone.z_axis*10)# x_axis and z_axis are in world space
                z_z_vec = (vec_out[2] - vec_in[2])

                up_axis = x_z_vec if abs(x_z_vec) > abs(z_z_vec) else z_z_vec
                up_axis_string = "X" if up_axis == x_z_vec else "Z"
                    # evaluate axis direction
                if up_axis < 0:
                    up_axis_string = "-"+up_axis_string

                new_item.up_axis = up_axis_string

            
            # toes fingers
            if foot_bone:# toes fingers can be parented to the main toes bone or foot bone
                par_list = [foot_bone]
                if toes_bone:
                    par_list.append(toes_bone)
                    
                for par in par_list:
                    if len(par.children):
                        found_toe_finger = False

                        for finger_bone in par.children:
                            if "THUMB" in finger_bone.name.upper():
                                new_item.thumb = finger_bone.name
                                found_toe_finger = True
                            elif "MIDDLE" in finger_bone.name.upper() or "MID" in finger_bone.name.upper():
                                new_item.middle = finger_bone.name
                                found_toe_finger = True
                            elif "INDEX" in finger_bone.name.upper():
                                new_item.index = finger_bone.name
                                found_toe_finger = True
                            elif "RING" in finger_bone.name.upper():
                                new_item.ring = finger_bone.name
                                found_toe_finger = True
                            elif "PINKY" in finger_bone.name.upper():
                                new_item.pinky = finger_bone.name
                                found_toe_finger = True
                            
                        # determining if the fingers are made of 3 or 4 bones is tricky since there may be "end" bones at the tip
                        # always set to 3 if any toes found atm
                        if found_toe_finger:
                            new_item.fingers = '3'
                            break
                
            
        elif input_type == "ARM":
            shoulder_bone = active_bone
            arm_bone = None
            arm_twist_bone = None
            arm_twist2_bone = None
            arm_twist3_bone = None
            arm_twist4_bone = None
            arm_twist5_bone = None
            arm_twist6_bone = None
            arm_twist7_bone = None
            arm_twist_count = 0
            forearm_bone = None
            forearm_twist_bone = None
            forearm_twist2_bone = None
            forearm_twist3_bone = None
            forearm_twist4_bone = None
            forearm_twist5_bone = None
            forearm_twist6_bone = None
            forearm_twist7_bone = None
            forearm_twist_count = 0
            hand_bone = None

            # arm
            if len(shoulder_bone.children) == 1:
                arm_bone = shoulder_bone.children[0]

            if arm_bone:
                if arm_bone.children:
                    # arm twist
                    for arm_child in arm_bone.children:
                        if "twist" in arm_child.name.lower():
                            if arm_twist_count == 0:
                                arm_twist_bone = arm_child
                            elif arm_twist_count == 1:
                                arm_twist2_bone = arm_child
                            elif arm_twist_count == 2:
                                arm_twist3_bone = arm_child
                            elif arm_twist_count == 3:
                                arm_twist4_bone = arm_child
                            elif arm_twist_count == 4:
                                arm_twist5_bone = arm_child
                            elif arm_twist_count == 5:
                                arm_twist6_bone = arm_child
                            elif arm_twist_count == 6:
                                arm_twist7_bone = arm_child
                            arm_twist_count += 1

                # forearm
                for arm_child in arm_bone.children:
                    if len(arm_child.children) > 0 and not "twist" in arm_child.name.lower():
                        forearm_bone = arm_child                        
                                

            if forearm_bone:
                # forearm twist
                for forearm_child in forearm_bone.children:
                    if "twist" in forearm_child.name.lower():
                        if forearm_twist_count == 0:
                            forearm_twist_bone = forearm_child
                        elif forearm_twist_count == 1:
                            forearm_twist2_bone = forearm_child
                        elif forearm_twist_count == 2:
                            forearm_twist3_bone = forearm_child
                        elif forearm_twist_count == 3:
                            forearm_twist4_bone = forearm_child
                        elif forearm_twist_count == 4:
                            forearm_twist5_bone = forearm_child
                        elif forearm_twist_count == 5:
                            forearm_twist6_bone = forearm_child
                        elif forearm_twist_count == 6:
                            forearm_twist7_bone = forearm_child
                        forearm_twist_count += 1

                    # hand
                    if len(forearm_child.children) > 0 and not "twist" in forearm_child.name.lower():
                        hand_bone = forearm_child
                

            if hand_bone:
                # fingers
                if len(hand_bone.children) > 0:
                    new_item.fingers = "3"# determining if the fingers are made of 3 or 4 bones is tricky since there may be "end" bones at the tip
                    for finger_bone in hand_bone.children:
                        if "THUMB" in finger_bone.name.upper():
                            new_item.thumb = finger_bone.name
                        elif "MIDDLE" in finger_bone.name.upper() or "MID" in finger_bone.name.upper():
                            new_item.middle = finger_bone.name
                        elif "INDEX" in finger_bone.name.upper():
                            new_item.index = finger_bone.name
                        elif "RING" in finger_bone.name.upper():
                            new_item.ring = finger_bone.name
                        elif "PINKY" in finger_bone.name.upper():
                            new_item.pinky = finger_bone.name

            # set limb props
            if shoulder_bone:
                new_item.bone_01 = shoulder_bone.name
            if arm_bone:
                new_item.bone_02 = arm_bone.name
            if arm_twist_bone:
                new_item.bone_03 = arm_twist_bone.name
            if arm_twist2_bone:
                new_item.bone_twist_02_01 = arm_twist2_bone.name
            if arm_twist3_bone:
                new_item.bone_twist_03_01 = arm_twist3_bone.name
            if arm_twist4_bone:
                new_item.bone_twist_04_01 = arm_twist4_bone.name
            if arm_twist5_bone:
                new_item.bone_twist_05_01 = arm_twist5_bone.name
            if arm_twist6_bone:
                new_item.bone_twist_06_01 = arm_twist6_bone.name
            if arm_twist7_bone:
                new_item.bone_twist_07_01 = arm_twist7_bone.name
            if forearm_bone:
                new_item.bone_04 = forearm_bone.name
            if forearm_twist_bone:
                new_item.bone_05 = forearm_twist_bone.name
            if forearm_twist2_bone:
                new_item.bone_twist_02_02 = forearm_twist2_bone.name
            if forearm_twist3_bone:
                new_item.bone_twist_03_02 = forearm_twist3_bone.name
            if forearm_twist4_bone:
                new_item.bone_twist_04_02 = forearm_twist4_bone.name
            if forearm_twist5_bone:
                new_item.bone_twist_05_02 = forearm_twist5_bone.name
            if forearm_twist6_bone:
                new_item.bone_twist_06_02 = forearm_twist6_bone.name
            if forearm_twist7_bone:
                new_item.bone_twist_07_02 = forearm_twist7_bone.name
            if hand_bone:
                new_item.bone_06 = hand_bone.name

            new_item.twist_bones_amount = arm_twist_count if arm_twist_count > forearm_twist_count else forearm_twist_count# always use the greater twist count found

            # evaluate the hand up axis
            #   look for the axis with highest magnitude in Z among X and Z
            if hand_bone:
                # evaluate in T-pose
                world_x = Vector((1,0,0))
                hand_pos = rig.matrix_world @ (hand_bone.head)
                arm_pos = rig.matrix_world @ (arm_bone.head)
                
                if hand_pos[0] < arm_pos[0]:
                    world_x *= -1
                    
                world_y = Vector((0,1,0))
                arm_dir_vec  = rig.matrix_world @ (hand_bone.head - arm_bone.head)
                arm_dir_proj_y = project_vec_onto_plane(arm_dir_vec, world_y)
                angle = signed_angle(arm_dir_proj_y, world_x, world_y)
                print('Arm Angle:', math.degrees(angle))
                
                vec_in = rig.matrix_world @ hand_bone.head.copy()

                x_axis_tpose = rotate_vec_mat(hand_bone.x_axis, angle, Vector((0,0,0)), world_y)
                vec_out = vec_in + (x_axis_tpose*10)# x_axis is in world space already
                x_z_vec = vec_out[2] - vec_in[2]

                y_axis_tpose = rotate_vec_mat(hand_bone.y_axis, angle, Vector((0,0,0)), world_y)
                vec_out = vec_in + (y_axis_tpose*10)# y_axis is in world space already
                y_z_vec = vec_out[2] - vec_in[2]

                z_axis_tpose = rotate_vec_mat(hand_bone.z_axis, angle, Vector((0,0,0)), world_y)
                vec_out = vec_in + (z_axis_tpose*10)# z_axis is in world space already
                z_z_vec =vec_out[2] - vec_in[2]
                up_axis_dict = {abs(x_z_vec): ["X", x_z_vec], abs(y_z_vec): ["Y", y_z_vec], abs(z_z_vec):["Z", z_z_vec]}

                longer_dist = sorted([abs(x_z_vec), abs(y_z_vec), abs(z_z_vec)], reverse=True)[0]
                up_axis_string = up_axis_dict[longer_dist][0]
                up_axis_value = up_axis_dict[longer_dist][1]
                # evaluate axis direction
                if up_axis_value < 0:
                    up_axis_string = "-"+up_axis_string
                new_item.up_axis = up_axis_string
                
                
            # evaluate the arm up axis
            if arm_bone and hand_bone:
                # evaluate in T-pose                
                world_x = Vector((1,0,0))
                hand_pos = rig.matrix_world @ (hand_bone.head)
                arm_pos = rig.matrix_world @ (arm_bone.head)
                
                if hand_pos[0] < arm_pos[0]:
                    world_x *= -1
                    
                world_y = Vector((0,1,0))
                arm_dir_vec  = rig.matrix_world @ (hand_bone.head - arm_bone.head)
                arm_dir_proj_y = project_vec_onto_plane(arm_dir_vec, world_y)
                angle = signed_angle(arm_dir_proj_y, world_x, world_y)
                print('Arm Angle:', math.degrees(angle))
                
                #   look for the axis with highest magnitude in Z among X and Z          
                vec_in = rig.matrix_world @ arm_bone.head.copy() 
                
                x_axis_tpose = rotate_vec_mat(arm_bone.x_axis, angle, Vector((0,0,0)), world_y)
                vec_out = vec_in + (x_axis_tpose*10)# x_axis is in world space already
                x_z_vec = vec_out[2] - vec_in[2]
                
                y_axis_tpose = rotate_vec_mat(arm_bone.y_axis, angle, Vector((0,0,0)), world_y)
                vec_out = vec_in + (y_axis_tpose*10)
                y_z_vec = vec_out[2] - vec_in[2]

                z_axis_tpose = rotate_vec_mat(arm_bone.z_axis, angle, Vector((0,0,0)), world_y)
                vec_out = vec_in + (z_axis_tpose*10)
                z_z_vec =vec_out[2] - vec_in[2]
                
                up_axis_dict = {abs(x_z_vec): ["X", x_z_vec], abs(y_z_vec): ["Y", y_z_vec], abs(z_z_vec):["Z", z_z_vec]}

                longer_dist = sorted([abs(x_z_vec), abs(y_z_vec), abs(z_z_vec)], reverse=True)[0]
                up_axis_string = up_axis_dict[longer_dist][0]
                up_axis_value = up_axis_dict[longer_dist][1]
                # evaluate axis direction
                if up_axis_value < 0:
                    up_axis_string = "-"+up_axis_string
                new_item.up_axis_arm = up_axis_string
            

        elif input_type == "SPINE":
            pelvis = active_bone
            spine_01_bone = None
            spine_02_bone = None
            spine_03_bone = None
            spine_04_bone = None
            spine_05_bone = None
            spine_06_bone = None

            def is_a_spine_name(bone):
                if "spine" in bone.name.lower() or "abdomen" in bone.name.lower() or "chest" in bone.name.lower():
                    return True
                return False

            if len(active_bone.children):
                # pelvis has thighs + spine as children, find by name match
                for pelvis_child in active_bone.children:
                    if "spine" in pelvis_child.name.lower() or "hips" in pelvis_child.name.lower():
                        spine_01_bone = pelvis_child
                        break

                if spine_01_bone == None:
                    # not found, find by bones height
                    for pelvis_child in active_bone.children:
                        if (rig.matrix_world @ pelvis_child.tail)[2] > (rig.matrix_world @ active_bone.tail)[2]:
                            spine_01_bone = pelvis_child
                            break

                spine_bones_list = [spine_01_bone, spine_02_bone, spine_03_bone, spine_04_bone, spine_05_bone, spine_06_bone]
                for i, spine_bone in enumerate(spine_bones_list):
                    if i == len(spine_bones_list)-1:
                        break
                    next_spine_bone = spine_bones_list[i+1]

                    if spine_bone:
                        print("Found spine bone")
                        if len(spine_bone.children) == 1:
                            spine_bones_list[i+1] = spine_bone.children[0]
                        else:# multiple children, maybe tail bones, breast... look up by name
                            for spine_child in spine_bone.children:
                                if is_a_spine_name(spine_child):
                                    spine_bones_list[i+1] = spine_child
                                    break


            new_item.bone_01 = pelvis.name if pelvis else ""
            if spine_bones_list[0]:
                new_item.bone_02 = spine_bones_list[0].name
            if spine_bones_list[1]:
                new_item.bone_03 = spine_bones_list[1].name
            if spine_bones_list[2]:
                new_item.bone_04 = spine_bones_list[2].name
            if spine_bones_list[3]:
                new_item.bone_05 = spine_bones_list[3].name
            if spine_bones_list[4]:
                new_item.bone_06 = spine_bones_list[4].name
            if spine_bones_list[5]:
                new_item.bone_07 = spine_bones_list[5].name

        
        elif input_type == "HEAD":
            neck_bone = active_bone
            neck_name = active_bone.name
            neck2_bone = None
            neck2_name = ""
            head_bone = None
            head_name = ""
            head_end_bone = None
            head_end_name = ""

            # find neck2 if any
            if len(neck_bone.children):
                neck_child = neck_bone.children[0]
                # may be a second neck bone
                if "neck" in neck_child.name.lower():
                    neck2_bone = neck_child
                    neck2_name = neck2_bone.name

            head_parent = neck2_bone if neck2_bone else neck_bone

            # find head
            if len(head_parent.children):
                if len(head_parent.children) == 1:
                    head_bone = head_parent.children[0]
                    head_name = head_bone.name

            #  find head end
            if head_bone:
                if len(head_bone.children):
                    for cbone in head_bone.children:
                        if "head" in cbone.name.lower():
                            head_end_bone = cbone
                            head_end_name = head_end_bone.name
                            break

            new_item.bone_01 = neck_name
            new_item.bone_04 = neck2_name
            new_item.bone_02 = head_name
            new_item.bone_03 = head_end_name

        
        elif input_type == 'TAIL':
            new_item.bone_01 = active_bone.name
        
        # set side
        if active_bone.name.upper().endswith(".L") or active_bone.name.upper().endswith("_L") or active_bone.name.upper().endswith("-L") or "LEFT" in active_bone.name.upper() or "_L_" in active_bone.name.upper() or " L " in active_bone.name.upper() or active_bone.name.upper().startswith("L_"):
            new_item.side = "LEFT"
        elif active_bone.name.upper().endswith(".R") or active_bone.name.upper().endswith("_R") or active_bone.name.upper().endswith("-R") or "RIGHT" in active_bone.name.upper() or "_R_" in active_bone.name.upper() or " R " in active_bone.name.upper() or active_bone.name.upper().startswith("R_"):
            new_item.side = "RIGHT"
        else:
            new_item.side = "CENTER"


    # restore mode and x mirror
    restore_current_mode(current_mode)
    rig.data.use_mirror_x = xmirror_state


def _remove_limb():
    scn = bpy.context.scene
    scn.limb_map.remove(scn.limb_map_index)
    if scn.limb_map_index > len(scn.limb_map)-1:
        scn.limb_map_index = len(scn.limb_map)-1


def update_arp_tab():
    interface_classes = (ARP_PT_quick_rig_menu, ARP_PT_quick_rig_update)

    for cl in reversed(interface_classes):
        try:
            bpy.utils.unregister_class(cl)
        except:
            pass

    QuickRigPanel.bl_category = bpy.context.preferences.addons[__package__].preferences.arp_tab_name
    
    for cl in interface_classes:
        bpy.utils.register_class(cl)


def update_quick_presets():
    # print("  look for custom presets...")
    presets_directory = bpy.context.preferences.addons[__package__].preferences.custom_presets_path

    if not (presets_directory.endswith("\\") or presets_directory.endswith('/')):
        presets_directory += '/'

    try:
        os.listdir(presets_directory)
    except:
        #print("The custom presets directory seems invalid:", presets_directory)
        return

    for file in os.listdir(presets_directory):
        if not file.endswith(".py"):
            continue

        preset_name = file.replace('.py', '')

        if preset_name in ARP_MT_quick_import.custom_presets:
            continue

        ARP_MT_quick_import.custom_presets.append(preset_name)


###########  UI PANELS  ###################
class QuickRigPanel:
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "ARP"
    

class ARP_PT_quick_rig_menu(bpy.types.Panel, QuickRigPanel):   
    bl_label = "Auto-Rig Pro: Quick Rig"
    bl_idname = "ARP_PT_quick_rig_menu"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        object = context.active_object
        scene = context.scene

        has_rigged = False
        if object:
            if object.type == "ARMATURE":
                if len(object.data.keys()):
                    if "arp_qr_data" in object.data.keys():
                        has_rigged = True

        col = layout.column(align=True)
        col.scale_y = 1.3
        if has_rigged:
            col.operator(ARP_OT_quick_revert.bl_idname, text="Revert", icon='RECOVER_LAST')
        else:
            col.operator(ARP_OT_quick_make_rig.bl_idname, text="Quick Rig!")
        col.separator()
        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator(ARP_OT_quick_import_mapping.bl_idname, text="Import")
        row.menu('ARP_MT_quick_import', text="", icon='DOWNARROW_HLT')
        row = row.row(align=True)
        row.operator(ARP_OT_quick_export_mapping.bl_idname, text="Export")
        row.menu('ARP_MT_quick_export', text="", icon='DOWNARROW_HLT')
        col.separator()
        row = col.row()
        row.template_list("ARP_UL_quick_limbs_list", "", scene, "limb_map", scene, "limb_map_index", rows=5)
        col = row.column(align=True)
        col.operator(ARP_OT_quick_add_limb.bl_idname, text='', icon='ADD')
        col.operator(ARP_OT_quick_remove_limb.bl_idname, text='', icon='REMOVE')
        col.operator(ARP_OT_quick_mirror_limb.bl_idname, text='', icon='MOD_MIRROR')
        
        col.separator()
        col.separator()
        col.operator(ARP_OT_quick_limbs_move.bl_idname, text="", icon="TRIA_UP").direction = 'UP'
        col.operator(ARP_OT_quick_limbs_move.bl_idname, text="", icon="TRIA_DOWN").direction = 'DOWN'
        '''# disable for now. Zeroing out the armature does not seem necessary anymore in latest Blender and QR versions
        if scene.arp_quick_freeze_check:
            layout.label(text="Armature transforms not frozen", icon="ERROR")
            layout.label(text="Freeze it first below:")
            col = layout.column(align=True)
            col.operator("arp.quick_freeze_armature", text="Freeze Armature")
            return
        '''
        layout.separator()
        col = layout.column(align=True)

        if len(scene.limb_map):
            selected_limb = scene.limb_map[scene.limb_map_index]
            col.prop(selected_limb,"type", text="Type")
            col.prop(selected_limb,"side", text="Side")
            col.separator()
            
            if selected_limb.type == "LEG":
                col.prop(selected_limb, "leg_type", text="Leg Type")
                col.separator()
                col.prop(selected_limb, "twist_bones_amount", text="Twist Bones Amount")
                col.separator()

                row = col.row(align=True)

                # upper thigh
                if selected_limb.leg_type == "3":
                    row.prop(selected_limb, "upper_thigh", text="UpThigh")
                    row.operator(ARP_OT_quick_pick_bone.bl_idname, text="", icon='EYEDROPPER').value = "upper_thigh"
                    if selected_limb.weights_override:
                        row.operator(ARP_OT_quick_set_weight_override.bl_idname, text="", icon='GROUP_BONE').value = "upper_thigh"

                # thigh
                row = col.row(align=True)
                row.prop(selected_limb, "bone_01", text="Thigh")
                row.operator(ARP_OT_quick_pick_bone.bl_idname, text="", icon='EYEDROPPER').value = "bone_01"
                if selected_limb.weights_override:
                    row.operator(ARP_OT_quick_set_weight_override.bl_idname, text="", icon='GROUP_BONE').value = "bone_01"

                # thigh twist 1
                if selected_limb.twist_bones_amount >= 1:
                    row = col.row(align=True)
                    row.prop(selected_limb, "bone_02", text="Twist")
                    row.operator(ARP_OT_quick_pick_bone.bl_idname, text="", icon='EYEDROPPER').value = "bone_02"
                    if selected_limb.weights_override:
                        row.operator(ARP_OT_quick_set_weight_override.bl_idname, text="", icon='GROUP_BONE').value = "bone_02"

                # thigh twist 2
                if selected_limb.twist_bones_amount >= 2:
                    for i in range(2, selected_limb.twist_bones_amount+1):
                        id = '%02d' % (i)
                        row = col.row(align=True)                        
                        row.prop(selected_limb, 'bone_twist_'+id+'_01', text="Twist "+str(i))
                        row.operator(ARP_OT_quick_pick_bone.bl_idname, text="", icon='EYEDROPPER').value = 'bone_twist_'+id+'_01'
          

                row = col.row(align=True)
                row.prop(selected_limb, "bone_03", text="Calf")
                row.operator(ARP_OT_quick_pick_bone.bl_idname, text="", icon='EYEDROPPER').value = "bone_03"
                if selected_limb.weights_override:
                    row.operator(ARP_OT_quick_set_weight_override.bl_idname, text="", icon='GROUP_BONE').value = "bone_03"

                 # calf twist 1
                if selected_limb.twist_bones_amount >= 1:
                    row = col.row(align=True)
                    row.prop(selected_limb, "bone_04", text="Twist")
                    row.operator(ARP_OT_quick_pick_bone.bl_idname, text="", icon='EYEDROPPER').value = "bone_04"
                    if selected_limb.weights_override:
                        row.operator(ARP_OT_quick_set_weight_override.bl_idname, text="", icon='GROUP_BONE').value = "bone_04"

                # calf twist 2
                if selected_limb.twist_bones_amount >= 2:
                    for i in range(2, selected_limb.twist_bones_amount+1):
                        id = '%02d' % (i)
                        row = col.row(align=True)
                        row.prop(selected_limb, 'bone_twist_'+id+'_02', text='Twist '+str(i))
                        row.operator(ARP_OT_quick_pick_bone.bl_idname, text='', icon='EYEDROPPER').value = 'bone_twist_'+id+'_02'
                    

                row = col.row(align=True)
                row.prop(selected_limb, "bone_05", text="Foot")
                row.operator(ARP_OT_quick_pick_bone.bl_idname, text="", icon='EYEDROPPER').value = "bone_05"
                if selected_limb.weights_override:
                    row.operator(ARP_OT_quick_set_weight_override.bl_idname, text="", icon='GROUP_BONE').value = "bone_05"
                row = col.row(align=True)
                row.prop(selected_limb, "bone_06", text="Toes")
                row.operator(ARP_OT_quick_pick_bone.bl_idname, text="", icon='EYEDROPPER').value = "bone_06"
                if selected_limb.weights_override:
                    row.operator(ARP_OT_quick_set_weight_override.bl_idname, text="", icon='GROUP_BONE').value = "bone_06"
                row = col.row(align=True)
                row.prop(selected_limb, "bone_07", text="Toes End")
                row.operator(ARP_OT_quick_pick_bone.bl_idname, text="", icon='EYEDROPPER').value = "bone_07"
                
                # Toes fingers
                row = col.row().split(factor=0.35)
                row.label(text='Toes Fingers:')
                row.prop(selected_limb, 'fingers', text='')

                if selected_limb.fingers != "NONE":
                    col.prop(selected_limb, 'manual_phalanges', text='Manual Phalanges')
                    row = col.row(align=True)
                    row.prop(selected_limb, 'thumb', text='Thumb Meta' if selected_limb.fingers == '4' else 'Thumb')
                    row.operator(ARP_OT_quick_pick_bone.bl_idname, text="", icon='EYEDROPPER').value = "thumb"
                    
                    if selected_limb.manual_phalanges:
                        row = col.row(align=True)
                        row.prop(selected_limb, "thumb2", text="thumb2")
                        row.operator(ARP_OT_quick_pick_bone.bl_idname, text='', icon='EYEDROPPER').value = "thumb2"
                    if selected_limb.manual_phalanges and selected_limb.fingers == '4':
                        row = col.row(align=True)
                        row.prop(selected_limb, "thumb3", text="thumb3")
                        row.operator(ARP_OT_quick_pick_bone.bl_idname, text="", icon='EYEDROPPER').value = "thumb3"
                    
                    row = col.row(align=True)
                    row.prop(selected_limb, "index", text='Index Meta' if selected_limb.fingers == '4' else 'Index')
                    row.operator(ARP_OT_quick_pick_bone.bl_idname, text="", icon='EYEDROPPER').value = "index"
                    if selected_limb.manual_phalanges:
                        if selected_limb.fingers == '4':
                            row = col.row(align=True)
                            row.prop(selected_limb, "index1", text="index1")
                            row.operator(ARP_OT_quick_pick_bone.bl_idname, text="", icon='EYEDROPPER').value = "index1"
                    if selected_limb.manual_phalanges:
                        row = col.row(align=True)
                        row.prop(selected_limb, "index2", text="index2")
                        row.operator(ARP_OT_quick_pick_bone.bl_idname, text="", icon='EYEDROPPER').value = "index2"
                    if selected_limb.manual_phalanges:                                
                        row = col.row(align=True)
                        row.prop(selected_limb, "index3", text="index3")
                        row.operator(ARP_OT_quick_pick_bone.bl_idname, text="", icon='EYEDROPPER').value = "index3"                    
                    
                    row = col.row(align=True)
                    row.prop(selected_limb, "middle", text='Middle Meta' if selected_limb.fingers == '4' else 'Middle')
                    row.operator(ARP_OT_quick_pick_bone.bl_idname, text="", icon='EYEDROPPER').value = "middle"
                    if selected_limb.manual_phalanges:
                        if selected_limb.fingers == '4':
                            row = col.row(align=True)
                            row.prop(selected_limb, "middle1", text="middle1")
                            row.operator(ARP_OT_quick_pick_bone.bl_idname, text="", icon='EYEDROPPER').value = "middle1"
                    if selected_limb.manual_phalanges:
                        row = col.row(align=True)
                        row.prop(selected_limb, "middle2", text="middle2")
                        row.operator(ARP_OT_quick_pick_bone.bl_idname, text="", icon='EYEDROPPER').value = "middle2"
                    if selected_limb.manual_phalanges:                                 
                        row = col.row(align=True)
                        row.prop(selected_limb, "middle3", text="middle3")
                        row.operator(ARP_OT_quick_pick_bone.bl_idname, text="", icon='EYEDROPPER').value = "middle3"                    
                    
                    row = col.row(align=True)
                    row.prop(selected_limb, "ring", text='Ring Meta' if selected_limb.fingers == '4' else 'Ring')
                    row.operator(ARP_OT_quick_pick_bone.bl_idname, text="", icon='EYEDROPPER').value = "ring"
                    if selected_limb.manual_phalanges:
                        if selected_limb.fingers == '4':
                            row = col.row(align=True)
                            row.prop(selected_limb, "ring1", text="ring1")
                            row.operator(ARP_OT_quick_pick_bone.bl_idname, text="", icon='EYEDROPPER').value = "ring1"
                    if selected_limb.manual_phalanges:
                        row = col.row(align=True)
                        row.prop(selected_limb, "ring2", text="ring2")
                        row.operator(ARP_OT_quick_pick_bone.bl_idname, text="", icon='EYEDROPPER').value = "ring2"
                    if selected_limb.manual_phalanges:                                
                        row = col.row(align=True)
                        row.prop(selected_limb, "ring3", text="ring3")
                        row.operator(ARP_OT_quick_pick_bone.bl_idname, text="", icon='EYEDROPPER').value = "ring3"
                    
                    row = col.row(align=True)
                    row.prop(selected_limb, "pinky", text='Pinky Meta' if selected_limb.fingers == '4' else 'Pinky')
                    row.operator(ARP_OT_quick_pick_bone.bl_idname, text="", icon='EYEDROPPER').value = "pinky"
                    if selected_limb.manual_phalanges:
                        if selected_limb.fingers == '4':
                            row = col.row(align=True)
                            row.prop(selected_limb, "pinky1", text="pinky1")
                            row.operator(ARP_OT_quick_pick_bone.bl_idname, text="", icon='EYEDROPPER').value = "pinky1"
                    if selected_limb.manual_phalanges:
                        row = col.row(align=True)
                        row.prop(selected_limb, "pinky2", text="pinky2")
                        row.operator(ARP_OT_quick_pick_bone.bl_idname, text="", icon='EYEDROPPER').value = "pinky2"
                    if selected_limb.manual_phalanges:                            
                        row = col.row(align=True)
                        row.prop(selected_limb, "pinky3", text="pinky3")
                        row.operator(ARP_OT_quick_pick_bone.bl_idname, text="", icon='EYEDROPPER').value = "pinky3"
                

                col.separator()
                col.prop(selected_limb, "weights_override", text="Enable Weights Override")
                col.separator()

                col.label(text="Foot Up Axis:")
                col = layout.column()
                col.enabled = selected_limb.fingers == "NONE"
                col.prop(selected_limb, "force_up_axis", text="Use World Z")
                col = layout.column(align=True)
                col.prop(selected_limb, "up_axis", text="")
                col.enabled = not selected_limb.force_up_axis or selected_limb.fingers != "NONE"

                col = layout.column(align=True)
                col.label(text="Foot Dir Axis:")
                col.prop(selected_limb, "foot_dir_axis", text="")
                
                col.separator()
                col.prop(selected_limb, "auto_knee", text="Auto-Knee Direction")
                col.prop(selected_limb, "connect_foot_to_calf", text="Connect Foot to Calf")
                col.prop(selected_limb, 'auto_ik_roll')


            elif selected_limb.type == "ARM":
                col.prop(selected_limb, "twist_bones_amount", text="Twist Bones Amount")
                col.separator()
                row = col.row(align=True)
                row.prop(selected_limb, "bone_01", text="Shoulder")
                row.operator(ARP_OT_quick_pick_bone.bl_idname, text="", icon='EYEDROPPER').value = "bone_01"
                if selected_limb.weights_override:
                    row.operator(ARP_OT_quick_set_weight_override.bl_idname, text="", icon='GROUP_BONE').value = "bone_01"
                row = col.row(align=True)
                row.prop(selected_limb, "bone_02", text="Arm")
                row.operator(ARP_OT_quick_pick_bone.bl_idname, text="", icon='EYEDROPPER').value = "bone_02"
                if selected_limb.weights_override:
                    row.operator(ARP_OT_quick_set_weight_override.bl_idname, text="", icon='GROUP_BONE').value = "bone_02"

                # arm twist 1
                if selected_limb.twist_bones_amount >= 1:
                    row = col.row(align=True)
                    row.prop(selected_limb, "bone_03", text="Twist")
                    row.operator(ARP_OT_quick_pick_bone.bl_idname, text="", icon='EYEDROPPER').value = "bone_03"
                    if selected_limb.weights_override:
                        row.operator(ARP_OT_quick_set_weight_override.bl_idname, text="", icon='GROUP_BONE').value = "bone_03"

                # arm twist 2
                if selected_limb.twist_bones_amount >= 2:
                    for i in range(2, selected_limb.twist_bones_amount+1):
                        id = '%02d' % (i)
                        row = col.row(align=True)
                        row.prop(selected_limb, 'bone_twist_'+id+'_01', text='Twist '+str(i))
                        row.operator(ARP_OT_quick_pick_bone.bl_idname, text="", icon='EYEDROPPER').value = 'bone_twist_'+id+'_01'
                  

                row = col.row(align=True)
                row.prop(selected_limb, "bone_04", text="Forearm")
                row.operator(ARP_OT_quick_pick_bone.bl_idname, text="", icon='EYEDROPPER').value = "bone_04"
                if selected_limb.weights_override:
                    row.operator(ARP_OT_quick_set_weight_override.bl_idname, text="", icon='GROUP_BONE').value = "bone_04"

                # forearm twist 1
                if selected_limb.twist_bones_amount >= 1:
                    row = col.row(align=True)
                    row.prop(selected_limb, "bone_05", text="Twist")
                    row.operator(ARP_OT_quick_pick_bone.bl_idname, text="", icon='EYEDROPPER').value = "bone_05"
                    if selected_limb.weights_override:
                        row.operator(ARP_OT_quick_set_weight_override.bl_idname, text="", icon='GROUP_BONE').value = "bone_05"

                # forearm twist 2
                if selected_limb.twist_bones_amount >= 2:
                    for i in range(2, selected_limb.twist_bones_amount+1):
                        id = '%02d' % (i)
                        row = col.row(align=True)
                        row.prop(selected_limb, 'bone_twist_'+id+'_02', text='Twist '+str(i))
                        row.operator(ARP_OT_quick_pick_bone.bl_idname, text='', icon='EYEDROPPER').value = 'bone_twist_'+id+'_02'
                        
                      
                row = col.row(align=True)
                row.prop(selected_limb, "bone_06", text="Hand")
                row.operator(ARP_OT_quick_pick_bone.bl_idname, text="", icon='EYEDROPPER').value = "bone_06"
                if selected_limb.weights_override:
                    row.operator(ARP_OT_quick_set_weight_override.bl_idname, text="", icon='GROUP_BONE').value = "bone_06"
                col.prop(selected_limb, "fingers", text="Fingers")
                if selected_limb.fingers != "NONE":
                    col.prop(selected_limb, 'manual_phalanges', text='Manual Phalanges')
                    row = col.row(align=True)
                    row.prop(selected_limb, 'thumb', text='Thumb')
                    row.operator(ARP_OT_quick_pick_bone.bl_idname, text="", icon='EYEDROPPER').value = "thumb"
                    
                    if selected_limb.manual_phalanges:
                        row = col.row(align=True)
                        row.prop(selected_limb, "thumb2", text="thumb2")
                        row.operator(ARP_OT_quick_pick_bone.bl_idname, text="", icon='EYEDROPPER').value = "thumb2"
                    if selected_limb.manual_phalanges:                                  
                        row = col.row(align=True)
                        row.prop(selected_limb, "thumb3", text="thumb3")
                        row.operator(ARP_OT_quick_pick_bone.bl_idname, text="", icon='EYEDROPPER').value = "thumb3"
                    
                    row = col.row(align=True)
                    row.prop(selected_limb, "index", text='Index Meta' if selected_limb.fingers == '4' else 'Index')
                    row.operator(ARP_OT_quick_pick_bone.bl_idname, text="", icon='EYEDROPPER').value = "index"
                    if selected_limb.manual_phalanges:
                        if selected_limb.fingers == '4':
                            row = col.row(align=True)
                            row.prop(selected_limb, "index1", text="index1")
                            row.operator(ARP_OT_quick_pick_bone.bl_idname, text="", icon='EYEDROPPER').value = "index1"
                    if selected_limb.manual_phalanges:
                        row = col.row(align=True)
                        row.prop(selected_limb, "index2", text="index2")
                        row.operator(ARP_OT_quick_pick_bone.bl_idname, text="", icon='EYEDROPPER').value = "index2"
                    if selected_limb.manual_phalanges:                                
                        row = col.row(align=True)
                        row.prop(selected_limb, "index3", text="index3")
                        row.operator(ARP_OT_quick_pick_bone.bl_idname, text="", icon='EYEDROPPER').value = "index3"                    
                    
                    row = col.row(align=True)
                    row.prop(selected_limb, "middle", text='Middle Meta' if selected_limb.fingers == '4' else 'Middle')
                    row.operator(ARP_OT_quick_pick_bone.bl_idname, text="", icon='EYEDROPPER').value = "middle"
                    if selected_limb.manual_phalanges:
                        if selected_limb.fingers == '4':
                            row = col.row(align=True)
                            row.prop(selected_limb, "middle1", text="middle1")
                            row.operator(ARP_OT_quick_pick_bone.bl_idname, text="", icon='EYEDROPPER').value = "middle1"
                    if selected_limb.manual_phalanges:
                        row = col.row(align=True)
                        row.prop(selected_limb, "middle2", text="middle2")
                        row.operator(ARP_OT_quick_pick_bone.bl_idname, text="", icon='EYEDROPPER').value = "middle2"
                    if selected_limb.manual_phalanges:                                 
                        row = col.row(align=True)
                        row.prop(selected_limb, "middle3", text="middle3")
                        row.operator(ARP_OT_quick_pick_bone.bl_idname, text="", icon='EYEDROPPER').value = "middle3"                    
                    
                    row = col.row(align=True)
                    row.prop(selected_limb, "ring", text='Ring Meta' if selected_limb.fingers == '4' else 'Ring')
                    row.operator(ARP_OT_quick_pick_bone.bl_idname, text="", icon='EYEDROPPER').value = "ring"
                    if selected_limb.manual_phalanges:
                        if selected_limb.fingers == '4':
                            row = col.row(align=True)
                            row.prop(selected_limb, "ring1", text="ring1")
                            row.operator(ARP_OT_quick_pick_bone.bl_idname, text="", icon='EYEDROPPER').value = "ring1"
                    if selected_limb.manual_phalanges:
                        row = col.row(align=True)
                        row.prop(selected_limb, "ring2", text="ring2")
                        row.operator(ARP_OT_quick_pick_bone.bl_idname, text="", icon='EYEDROPPER').value = "ring2"
                    if selected_limb.manual_phalanges:                                
                        row = col.row(align=True)
                        row.prop(selected_limb, "ring3", text="ring3")
                        row.operator(ARP_OT_quick_pick_bone.bl_idname, text="", icon='EYEDROPPER').value = "ring3"
                    
                    row = col.row(align=True)
                    row.prop(selected_limb, "pinky", text='Pinky Meta' if selected_limb.fingers == '4' else 'Pinky')
                    row.operator(ARP_OT_quick_pick_bone.bl_idname, text="", icon='EYEDROPPER').value = "pinky"
                    if selected_limb.manual_phalanges:
                        if selected_limb.fingers == '4':
                            row = col.row(align=True)
                            row.prop(selected_limb, "pinky1", text="pinky1")
                            row.operator(ARP_OT_quick_pick_bone.bl_idname, text="", icon='EYEDROPPER').value = "pinky1"
                    if selected_limb.manual_phalanges:
                        row = col.row(align=True)
                        row.prop(selected_limb, "pinky2", text="pinky2")
                        row.operator(ARP_OT_quick_pick_bone.bl_idname, text="", icon='EYEDROPPER').value = "pinky2"
                    if selected_limb.manual_phalanges:                            
                        row = col.row(align=True)
                        row.prop(selected_limb, "pinky3", text="pinky3")
                        row.operator(ARP_OT_quick_pick_bone.bl_idname, text="", icon='EYEDROPPER').value = "pinky3"
                
                col.separator()                
                col.prop(selected_limb, "weights_override", text="Enable Weights Override")
                col.separator()
                
                col.label(text="Arms Up Axis:")
                col.prop(selected_limb, "up_axis_arm", text="")
                
                col.label(text="Hand and Fingers Up Axis:")
                col.prop(selected_limb, "up_axis", text="")
                col.separator()
                col.prop(selected_limb, "primary_axis_auto", text="Auto Primary Axis")
                col = layout.column(align=True)
                col.enabled = not selected_limb.primary_axis_auto
                col.prop(selected_limb, "primary_axis", text="")

                col = layout.column(align=True)
                col.label(text='Elbow Axis Correction:')
                col.prop(selected_limb, 'IK_axis_correc', text='')
                col.prop(selected_limb, 'auto_ik_roll')


            elif selected_limb.type == "SPINE":
                row = col.row(align=True)
                row.prop(selected_limb, "bone_01", text="Pelvis")
                row.operator(ARP_OT_quick_pick_bone.bl_idname, text="", icon='EYEDROPPER').value = "bone_01"
                if selected_limb.weights_override:
                    row.operator(ARP_OT_quick_set_weight_override.bl_idname, text="", icon='GROUP_BONE').value = "bone_01"
                row = col.row(align=True)
                row.prop(selected_limb, "bone_02", text="Spine1")
                row.operator(ARP_OT_quick_pick_bone.bl_idname, text="", icon='EYEDROPPER').value = "bone_02"
                if selected_limb.weights_override:
                    row.operator(ARP_OT_quick_set_weight_override.bl_idname, text="", icon='GROUP_BONE').value = "bone_02"
                row = col.row(align=True)
                row.prop(selected_limb, "bone_03", text="Spine2")
                row.operator(ARP_OT_quick_pick_bone.bl_idname, text="", icon='EYEDROPPER').value = "bone_03"
                if selected_limb.weights_override:
                    row.operator(ARP_OT_quick_set_weight_override.bl_idname, text="", icon='GROUP_BONE').value = "bone_03"
                row = col.row(align=True)
                row.prop(selected_limb, "bone_04", text="Spine3")
                row.operator(ARP_OT_quick_pick_bone.bl_idname, text="", icon='EYEDROPPER').value = "bone_04"
                if selected_limb.weights_override:
                    row.operator(ARP_OT_quick_set_weight_override.bl_idname, text="", icon='GROUP_BONE').value = "bone_04"
                row = col.row(align=True)
                row.prop(selected_limb, "bone_05", text="Spine4")
                row.operator(ARP_OT_quick_pick_bone.bl_idname, text="", icon='EYEDROPPER').value = "bone_05"
                if selected_limb.weights_override:
                    row.operator(ARP_OT_quick_set_weight_override.bl_idname, text="", icon='GROUP_BONE').value = "bone_05"
                row = col.row(align=True)
                row.prop(selected_limb, "bone_06", text="Spine5")
                row.operator(ARP_OT_quick_pick_bone.bl_idname, text="", icon='EYEDROPPER').value = "bone_06"
                if selected_limb.weights_override:
                    row.operator(ARP_OT_quick_set_weight_override.bl_idname, text="", icon='GROUP_BONE').value = "bone_06"
                row = col.row(align=True)
                row.prop(selected_limb, "bone_07", text="Spine6")
                row.operator(ARP_OT_quick_pick_bone.bl_idname, text="", icon='EYEDROPPER').value = "bone_07"
                if selected_limb.weights_override:
                    row.operator(ARP_OT_quick_set_weight_override.bl_idname, text="", icon='GROUP_BONE').value = "bone_07"

                col = layout.column()                
                col.prop(selected_limb, "weights_override", text="Enable Weights Override")
                col.separator()
                
                col.label(text="Spine Z Axis:")
                col.prop(selected_limb, "force_z_axis", text="Use World Y")

                col.separator()
                col.prop(selected_limb, "primary_axis_auto", text="Auto Primary Axis")
                col = layout.column(align=True)
                col.enabled = not selected_limb.primary_axis_auto
                col.prop(selected_limb, "primary_axis", text="")
                col = layout.column(align=True)
                if not selected_limb.primary_axis_auto:
                    col.enabled=False
                col.prop(selected_limb, "connect", text="Connect")
                
                col.prop(selected_limb, 'pelvis_up', text="Force Pelvis Up")

                col = layout.column(align=True)
                
            
            elif selected_limb.type == "HEAD":
                col.prop(selected_limb, "neck_bones_amount", text="Neck Bones Amount")
                col.separator()
                row = col.row(align=True)
                row.prop(selected_limb, "bone_01", text="Neck")
                row.operator(ARP_OT_quick_pick_bone.bl_idname, text="", icon='EYEDROPPER').value = "bone_01"

                if selected_limb.neck_bones_amount > 1:
                    row = col.row(align=True)
                    row.prop(selected_limb, "bone_04", text="Neck 2")
                    row.operator(ARP_OT_quick_pick_bone.bl_idname, text="", icon='EYEDROPPER').value = "bone_04"

                if selected_limb.neck_bones_amount > 2:
                    row = col.row(align=True)
                    row.prop(selected_limb, "neck3", text="Neck 3")
                    row.operator(ARP_OT_quick_pick_bone.bl_idname, text="", icon='EYEDROPPER').value = "neck3"

                if selected_limb.neck_bones_amount > 3:
                    row = col.row(align=True)
                    row.prop(selected_limb, "neck4", text="Neck 4")
                    row.operator(ARP_OT_quick_pick_bone.bl_idname, text="", icon='EYEDROPPER').value = "neck4"

                if selected_limb.neck_bones_amount > 4:
                    row = col.row(align=True)
                    row.prop(selected_limb, "neck5", text="Neck 5")
                    row.operator(ARP_OT_quick_pick_bone.bl_idname, text="", icon='EYEDROPPER').value = "neck5"

                if selected_limb.neck_bones_amount > 5:
                    row = col.row(align=True)
                    row.prop(selected_limb, "neck6", text="Neck 6")
                    row.operator(ARP_OT_quick_pick_bone.bl_idname, text="", icon='EYEDROPPER').value = "neck6"

                if selected_limb.neck_bones_amount > 6:
                    row = col.row(align=True)
                    row.prop(selected_limb, "neck7", text="Neck 7")
                    row.operator(ARP_OT_quick_pick_bone.bl_idname, text="", icon='EYEDROPPER').value = "neck7"

                if selected_limb.neck_bones_amount > 7:
                    row = col.row(align=True)
                    row.prop(selected_limb, "neck8", text="Neck 8")
                    row.operator(ARP_OT_quick_pick_bone.bl_idname, text="", icon='EYEDROPPER').value = "neck8"

                if selected_limb.neck_bones_amount > 8:
                    row = col.row(align=True)
                    row.prop(selected_limb, "neck9", text="Neck 9")
                    row.operator(ARP_OT_quick_pick_bone.bl_idname, text="", icon='EYEDROPPER').value = "neck9"

                if selected_limb.neck_bones_amount > 9:
                    row = col.row(align=True)
                    row.prop(selected_limb, "neck10", text="Neck 10")
                    row.operator(ARP_OT_quick_pick_bone.bl_idname, text="", icon='EYEDROPPER').value = "neck10"

                row = col.row(align=True)
                row.prop(selected_limb, "bone_02", text="Head")
                row.operator(ARP_OT_quick_pick_bone.bl_idname, text="", icon='EYEDROPPER').value = "bone_02"
                row = col.row(align=True)
                row.prop(selected_limb, "bone_03", text="Head End")
                row.operator(ARP_OT_quick_pick_bone.bl_idname, text="", icon='EYEDROPPER').value = "bone_03"
                col.separator()
                col.label(text="Head Z Axis:")
                col.prop(selected_limb, "force_z_axis", text="Use World Y")
                col.separator()
                col.prop(selected_limb, "primary_axis_auto", text="Auto Primary Axis")
                col = layout.column(align=True)
                col.enabled = not selected_limb.primary_axis_auto
                col.prop(selected_limb, "primary_axis", text="")


            elif selected_limb.type == 'TAIL':
                col.prop(selected_limb, 'bone_01', text='Tail Root')
                
                col.separator()
                col.prop(selected_limb, "primary_axis_auto", text="Auto Primary Axis")
                col = layout.column(align=True)
                col.enabled = not selected_limb.primary_axis_auto
                col.prop(selected_limb, "primary_axis", text="")
                col = layout.column(align=True)
                if not selected_limb.primary_axis_auto:
                    col.enabled=False
                col.prop(selected_limb, "connect", text="Connect")
                
                
class ARP_PT_quick_rig_update(Panel, QuickRigPanel):
    bl_label = "Updates"
    bl_parent_id = "ARP_PT_quick_rig_menu"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        layout.operator(ARP_OT_quick_check_for_update.bl_idname, text='Check for Updates')
        

###########  REGISTER  ##################
classes = (ARP_OT_quick_report_message, ARP_OT_quick_import_mapping, ARP_OT_quick_export_mapping, ARP_UL_quick_limbs_list, LimbProp, 
ARP_OT_quick_add_limb, ARP_OT_quick_remove_limb, ARP_OT_quick_mirror_limb,
ARP_OT_quick_pick_bone, ARP_PT_quick_rig_menu, ARP_PT_quick_rig_update, ARP_OT_quick_make_rig, 
ARP_OT_quick_revert, ARP_OT_quick_set_weight_override,
ARP_OT_quick_freeze_armature, ARP_MT_quick_import,
ARP_OT_quick_limbs_move,
ARP_MT_quick_export, ARP_OT_quick_import_preset, ARP_OT_quick_export_preset, ARP_OT_quick_check_for_update, ARP_OT_reimport_preset_fuzzy)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    update_arp_tab()
    update_quick_presets()

    bpy.types.Scene.limb_map = bpy.props.CollectionProperty(type=LimbProp, name="Limb Map", description="List of limbs")
    bpy.types.Scene.limb_map_index = IntProperty(name="List Index", description="Index of the list", default=0)
    bpy.types.Scene.arp_quick_freeze_check = BoolProperty(default=False, description="")
    bpy.types.Scene.arp_quick_hold_update = BoolProperty(default=False)


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

    del bpy.types.Scene.limb_map
    del bpy.types.Scene.limb_map_index
    del bpy.types.Scene.arp_quick_freeze_check
    del bpy.types.Scene.arp_quick_hold_update


if __name__ == "__main__":
    register()