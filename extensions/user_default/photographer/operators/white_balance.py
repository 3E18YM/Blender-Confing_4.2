import bpy, bgl, math, gpu
from .. import __package__ as base_package
import numpy as np
from ..functions.functions import (
    srgb_to_linear,
    linear_to_srgb,
    InterpolatedArray,
    rgb_to_luminance,
    read_pixel_color,
)
from ..functions.nodes import get_comp_group_node, get_comp_node_in_group
from ..properties.post_effects import postfx_grp_name
from .autofocus import hide_focus_planes
from ..constants import DEFAULT_COLOR_TEMPERATURE, DEFAULT_TINT

# Creating Color Temperature to sRGB look up tables (CIE 1964 10 degree CMFs)
# from http://www.vendian.org/mncharity/dir3/blackbody/UnstableURLs/bbr_color.html
# Using 6500 as default white: purposefully changed 255,249,251 to 255,255,255
color_temperature_red = ((1000,255),(1200,255),(1400,255),(1600,255),(1800,255),
                        (2000, 255),(2200,255),(2400,255),(2700,255),(3000,255),
                        (3300,255),(3600,255),(3900,255),(4300,255),
                        (5000,255),(6000,255),(6500, 255),(7000,245),(8000,227),
                        (9000,214),(10000,204),(11000,196),(12000,191),(13000,120),
                        (14000, 30))
color_temperature_green = ((1000,56),(1200,83),(1400,101),(1600,115),(1800,126),
                        (2000,137),(2200,147),(2400,157),(2700,169),(3000,180),
                        (3300,190),(3600,199),(3900,206),(4300,219),(5000,228),
                        (6000,243),(6500, 255),(7000,243),(8000,233),(9000,225),
                        (10000,219),(11000,215),(12000,211),(13000,200),(14000, 100))
color_temperature_blue = ((1000,1),(1200,1),(1400,1),(1600,1),(1800,1),(2000,18),
                        (2200,44),(2400,63),(2700,87),(3000,107),(3300,126),
                        (3600,143),(3900,159),(4300,175),(5000,206),(6000,239),
                        (6500, 255),(7000,255),(8000,255),(9000,255),(10000,255),
                        (11000,255),(12000,255),(13000,255),(14000,255))

# Blender Blackbody table
blackbody_table_r = np.array([
    [1.61919106e+03, -2.05010916e-03, 5.02995757e+00],
    [2.48845471e+03, -1.11330907e-03, 3.22621544e+00],
    [3.34143193e+03, -4.86551192e-04, 1.76486769e+00],
    [4.09461742e+03, -1.27446582e-04, 7.25731635e-01],
    [4.67028036e+03, 2.91258199e-05, 1.26703442e-01],
    [4.59509185e+03, 2.87495649e-05, 1.50345020e-01],
    [3.78717450e+03, 9.35907826e-06, 3.99075871e-01]
])

blackbody_table_g = np.array([
    [-4.88999748e+02, 6.04330754e-04, -7.55807526e-02],
    [-7.55994277e+02, 3.16730098e-04, 4.78306139e-01],
    [-1.02363977e+03, 1.20223470e-04, 9.36662319e-01],
    [-1.26571316e+03, 4.87340896e-06, 1.27054498e+00],
    [-1.42529332e+03, -4.01150431e-05, 1.43972784e+00],
    [-1.17554822e+03, -2.16378048e-05, 1.30408023e+00],
    [-5.00799571e+02, -4.59832026e-06, 1.09098763e+00]
])

blackbody_table_b = np.array([
    [5.96945309e-11, -4.85742887e-08, -9.70622247e-05, -4.07936148e-03],
    [2.40430366e-11, 5.55021075e-08, -1.98503712e-04, 2.89312858e-02],
    [-1.40949732e-11, 1.89878968e-07, -3.56632824e-04, 9.10767778e-02],
    [-3.61460868e-11, 2.84822009e-07, -4.93211319e-04, 1.56723440e-01],
    [-1.97075738e-11, 1.75359352e-07, -2.50542825e-04, -2.22783266e-02],
    [-1.61997957e-13, -1.64216008e-08, 3.86216271e-04, -7.38077418e-01],
    [6.72650283e-13, -2.73078809e-08, 4.24098264e-04, -7.52335691e-01]
])

# Blender's blackbody implementation
def blackbody_temperature_to_rec709(t):
    if t >= 12000.0:
        return [0.8262954810464208, 0.9945080501520986, 1.566307710274283]
    elif t < 800.0:
        return [5.413294490189271, -0.20319390035873933, -0.0822535242887164]
    else:
        i = np.searchsorted([965.0, 1167.0, 1449.0, 1902.0, 3315.0, 6365.0, 12000.0], t) - 1
        r = blackbody_table_r[i]
        g = blackbody_table_g[i]
        b = blackbody_table_b[i]
        t_inv = 1.0 / t
        return [
            r[0] * t_inv + r[1] * t + r[2],
            g[0] * t_inv + g[1] * t + g[2],
            ((b[0] * t + b[1]) * t + b[2]) * t + b[3]
        ]

def blackbody_temperature_to_rgb(value):
    rec709 = blackbody_temperature_to_rec709(value)
    rgb = [linear_to_srgb(value) for value in rec709]
    # rgb = rec709  # Assuming no conversion is needed
    rgb = np.clip(rgb, 0.0, np.finfo(float).max)
    return rgb

def blackbody_temperature_to_rgb_table(width, min_val, max_val):
    r_table = np.zeros((width, 4))
    for i in range(width):
        temperature = min_val + (max_val - min_val) / width * i
        r_table[i] = blackbody_temperature_to_rgb(temperature)
    return r_table

def blackbody_rgb_to_temperature(rgb):
    r,g,b = rgb
    min_diff = float('inf')
    closest_temperature = 1000
    
    for temp in range(800, 12000, 6):
        # Convert the temperature to RGB using the blackbody_temperature_to_rec709 function
        temp_rgb = blackbody_temperature_to_rec709(temp)
        
        # Ignore the green channel
        temp_r, _, temp_b = temp_rgb
        
        # Calculate the difference between the RGB values
        diff = abs(temp_r - r) + abs(temp_b - b)
        
        # Update the closest temperature if needed
        if diff < min_diff:
            min_diff = diff
            closest_temperature = temp
            
    return closest_temperature

# Algorithm courtesy of http://www.tannerhelland.com/4435/convert-temperature-rgb-algorithm-code/
def algo_temperature_to_rgb(color_temperature):
    if color_temperature < 1000: 
        color_temperature = 1000
    elif color_temperature > 40000:
        color_temperature = 40000
    
    tmp_internal = color_temperature / 100.0
    
    # red 
    if tmp_internal <= 66:
        red = 255
    else:
        tmp_red = 329.698727446 * math.pow(tmp_internal - 60, -0.1332047592)
        if tmp_red < 0:
            red = 0
        elif tmp_red > 255:
            red = 255
        else:
            red = tmp_red
    
    # green
    if tmp_internal <=66:
        tmp_green = 99.4708025861 * math.log(tmp_internal) - 161.1195681661
        if tmp_green < 0:
            green = 0
        elif tmp_green > 255:
            green = 255
        else:
            green = tmp_green
    else:
        tmp_green = 288.1221695283 * math.pow(tmp_internal - 60, -0.0755148492)
        if tmp_green < 0:
            green = 0
        elif tmp_green > 255:
            green = 255
        else:
            green = tmp_green
    
    # blue
    if tmp_internal >=66:
        blue = 255
    elif tmp_internal <= 19:
        blue = 0
    else:
        tmp_blue = 138.5177312231 * math.log(tmp_internal - 10) - 305.0447927307
        if tmp_blue < 0:
            blue = 0
        elif tmp_blue > 255:
            blue = 255
        else:
            blue = tmp_blue
    
    return (red / 255, green / 255, blue / 255)

# McCamy's approximation, only holds true within a certain distance of the Planckian locus.
def algo_rgb_to_temperature(rgb):
    R,G,B = rgb

    # Convert RGB to XYZ
    X = 0.4124*R + 0.3576*G + 0.1805*B
    Y = 0.2126*R + 0.7152*G + 0.0722*B
    Z = 0.0193*R + 0.1192*G + 0.9505*B

    # Normalize to CIE 1931 xy
    x = X / (X + Y + Z)
    y = Y / (X + Y + Z)

    n = (x-0.3320)/(0.1858-y)
    # CCT -- https://dsp.stackexchange.com/questions/8949/how-to-calculate-the-color-temperature-tint-of-the-colors-in-an-image
    # CCT = 449 * math.pow(n,3) + 3525 * math.pow(n,2) + 6823.3 * n + 5520.33

    # CCT -- Another formula, McCamy's approx? https://www.waveformlighting.com/tech/calculate-color-temperature-cct-from-cie-1931-xy-coordinates
    CCT = 437 * math.pow(n,3) + 3601 * math.pow(n,2) + 6861 * n + 5517

    return CCT

# Photographer Simplified Color Temperature only using sRGB table. CCT as Red/Blue, with Green channel separate.
def pg_temperature_ratio(red_temp, blue_temp):
    return (float(red_temp[1]) / blue_temp[1], red_temp[0])

def pg_temperature_to_rgb(temperature):
    # Interpolate Tables
    table_red = InterpolatedArray(color_temperature_red)
    table_green = InterpolatedArray(color_temperature_green)
    table_blue = InterpolatedArray(color_temperature_blue)

    # Convert Temperature to RGB using the look up tables
    red = table_red[temperature]
    green = table_green[temperature]
    blue = table_blue[temperature]

    return (red / 255, green / 255, blue / 255)

def pg_rgb_to_temperature(rgb):
    # Convert Color Temp from sRGB to linear
    color_temp_red = []
    color_temp_blue = []
    for x in color_temperature_red:
        y = [x[0], srgb_to_linear(float(x[1])/255.0)]
        color_temp_red.append(y)
    for x in color_temperature_blue:
        y = [x[0], srgb_to_linear(float(x[1])/255.0)]
        color_temp_blue.append(y)

    # Convert Table to Red/Blue ratio    
    temperature_ratio = list(map(pg_temperature_ratio, color_temp_red, color_temp_blue))
    table_ratio = InterpolatedArray(temperature_ratio)

    # Min and Max ratios from the table
    maxratio = temperature_ratio[0][0]
    minratio = temperature_ratio[-1][0]

    # rgb = [linear_to_srgb(x) for x in rgb]
    R,G,B = rgb

    # Make sure to not divide by 0
    if B == 0:
        ratio = minratio
    else: 
        ratio = R / B

    #Clamping ratio to avoid looking outside of the table
    ratio = maxratio if ratio > maxratio else minratio if ratio < minratio else ratio

    color_temperature = table_ratio[ratio]

    return (color_temperature)

def convert_temperature_to_rgb(temperature, linear=False):
    prefs = bpy.context.preferences.addons[base_package].preferences

    if prefs.color_temperature_mode == 'ALGORITHM':
        rgb = algo_temperature_to_rgb(temperature)
    elif prefs.color_temperature_mode == 'BLACKBODY':
        rgb = blackbody_temperature_to_rgb(temperature)
    else:
        rgb = pg_temperature_to_rgb(temperature)
    
    if linear:
        rgb = [srgb_to_linear(channel) for channel in rgb]

    return rgb

def convert_rgb_to_temperature(rgb):
    prefs = bpy.context.preferences.addons[base_package].preferences

    if prefs.color_temperature_mode == 'ALGORITHM':
        temperature = algo_rgb_to_temperature(rgb)
    elif prefs.color_temperature_mode == 'BLACKBODY':
        temperature = blackbody_rgb_to_temperature(rgb)
    else:
        temperature = pg_rgb_to_temperature(rgb)
    
    return temperature

def convert_rgb_to_white_level(rgb):
    red,green,blue = [srgb_to_linear(channel) for channel in rgb]
    average = (red + green + blue) / 3

    return [red/average,green/average,blue/average]

def convert_rgb_to_whitebalance(picked_color,use_scene_camera=True):
    if use_scene_camera:
        settings = bpy.context.scene.camera.data.photographer
    else:
        settings = bpy.context.camera.photographer

    prefs = bpy.context.preferences.addons[base_package].preferences
    if prefs.color_temperature_mode == 'BLENDER' and bpy.app.version >= (4,3,0):
        bpy.context.scene.view_settings.white_balance_whitepoint = picked_color
        settings.color_temperature = int(bpy.context.scene.view_settings.white_balance_temperature)
        settings.tint = int(bpy.context.scene.view_settings.white_balance_tint)
    
    else:
        # glReadPixels returns raw linear pixel values
        red,green,blue = picked_color

        average = rgb_to_luminance(picked_color)

        if average != 0:
            # Calculating Curves white level values
            curve_mult = [x / average for x in picked_color]

            # # Debug - closest multipliers
            # bpy.context.scene.view_settings.curve_mapping.white_level = picked_color
            # #Little trick to update viewport as Color Management Curves don't update automatically
            # exposure = bpy.context.scene.view_settings.exposure
            # bpy.context.scene.view_settings.exposure = exposure

            temperature = int(convert_rgb_to_temperature(curve_mult))
            settings.color_temperature = temperature

            prefs = bpy.context.preferences.addons[base_package].preferences
            if prefs.color_temperature_mode in {'ALGORITHM','BLACKBODY'}:
                # Convert Curve value to Temperature

                new_rgb = convert_temperature_to_rgb(temperature)
                applied_white_balance = convert_rgb_to_white_level(new_rgb)
                # print(curve_mult[1],applied_white_balance[1])

                target = red / applied_white_balance[0]
                green_mult = green / target
                green_deviation = applied_white_balance[1]-green_mult
                # print(green_deviation)

                # Convert Curve value to Tint
                if green_deviation+1 < 1 :
                    settings.tint = -int((green_deviation) * 200) # Reverse Tint Math
                else:
                    settings.tint = -int((green_deviation) * 50) # Reverse Tint Math

            else:
                # # Make sure that Green is the same as Red after conversion to Color Temperature
                target = red / bpy.context.scene.view_settings.curve_mapping.white_level[0]
                green_mult = green / target
                
                # # Convert Curve value to Tint
                if green_mult < 1 :
                    settings.tint = int((green_mult -1) * 200) # Reverse Tint Math
                else:
                    settings.tint = int((green_mult -1) * 50) # Reverse Tint Math

class PHOTOGRAPHER_OT_WBReset(bpy.types.Operator):

    bl_idname = "white_balance.reset"
    bl_label = "Reset White Balance"
    bl_description = "Reset White Balance"
    bl_options = {'UNDO'}

    use_scene_camera: bpy.props.BoolProperty(default=False)

    def execute(self, context):
        if self.use_scene_camera:
            settings = context.scene.camera.data.photographer
        else:
            settings = context.camera.photographer

        settings.color_temperature = DEFAULT_COLOR_TEMPERATURE
        settings.tint = DEFAULT_TINT
        settings.wb_color = (0.5,0.5,0.5)

        return{'FINISHED'}

def white_balance_picker(self,context):
    x,y = self.mouse_region_x, self.mouse_region_y

    area = context.area
    if area.type=='VIEW_3D':

        red = 0
        green = 0
        blue = 0

        if bpy.app.version >= (3,2,2):
            # get currently bound framebuffer
            buffer = gpu.state.active_framebuffer_get()
        else:
            bgl.glDisable(bgl.GL_DEPTH_TEST)
            buffer = bgl.Buffer(bgl.GL_FLOAT, 3)

        for i in range(x-4, x+5):
            for j in range(y-4, y+5):
                value = read_pixel_color(i,j,buffer)
                red += value[0]
                green += value[1]
                blue += value[2]

        average_r = red / 81
        average_g = green / 81
        average_b = blue / 81

        picked_average = (average_r,average_g,average_b)

        # Clear Buffer
        del buffer

        if picked_average != (0.0,0.0,0.0):
            convert_rgb_to_whitebalance(picked_average,self.use_scene_camera)

class PHOTOGRAPHER_OT_WBPicker(bpy.types.Operator):
    bl_idname = "white_balance.picker"
    bl_label = "Pick White Balance"
    bl_description = "Pick a grey area in the 3D view to adjust the White Balance.\nShift + Click to reset"
    bl_options = {'REGISTER', 'UNDO'}

    use_scene_camera: bpy.props.BoolProperty(default=False)
    mouse_region_x: bpy.props.IntProperty(default=0)
    mouse_region_y: bpy.props.IntProperty(default=0)
    comp_wb: bpy.props.BoolProperty(default=False)

    def modal(self, context, event):
        if self.use_scene_camera:
            settings = context.scene.camera.data.photographer
        else:
            settings = context.camera.photographer

        context.area.tag_redraw()

        self.mouse_region_x = event.mouse_region_x
        self.mouse_region_y = event.mouse_region_y

        # Allow navigation for Blender and Maya shortcuts
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'} or event.alt and event.type == 'LEFTMOUSE' or event.alt and event.type == 'RIGHTMOUSE':
            return {'PASS_THROUGH'}

        if event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            context.scene.photographer.comp_wb = self.comp_wb

            if context.area.type=='VIEW_3D':
                bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')

            # Restore Mouse Cursor from EYEDROPPER Icon
            if self.cursor_set:
                context.window.cursor_modal_restore()

            # Restore Focus Planes visibility
            for o in self.fp:
                o.hide_viewport = False

            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            if context.area.type=='VIEW_3D':
                bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')

            # Restore previous state
            context.scene.photographer.comp_wb = self.comp_wb
            context.scene.view_settings.use_curve_mapping = self.stored_use_curve_mapping
            settings.color_temperature = self.stored_color_temperature
            settings.tint = self.stored_tint

            # Restore Focus Planes visibility
            for o in self.fp:
                o.hide_viewport = False

            # Restore Mouse Cursor from EYEDROPPER Icon
            if self.cursor_set:
                context.window.cursor_modal_restore()

            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):

        self.comp_wb = False

        if event.shift == True:
            bpy.ops.white_balance.reset(use_scene_camera=True)
            return {'FINISHED'}

        else:
            if context.area.type=='VIEW_3D':
                if self.use_scene_camera:
                    settings = context.scene.camera.data.photographer
                else:
                    settings = context.camera.photographer

                # Store state
                self.stored_use_curve_mapping = context.scene.view_settings.use_curve_mapping
                self.stored_color_temperature = settings.color_temperature
                self.stored_tint = settings.tint

                # Work around Apply at Compositing picker issue
                if context.scene.photographer.comp_wb:
                    self.comp_wb = True
                    context.scene.photographer.comp_wb = False

                self.fp = hide_focus_planes()

                if not context.scene.view_settings.use_curve_mapping:
                    context.scene.view_settings.use_curve_mapping = True

                args = (self, context)
                self._handle = bpy.types.SpaceView3D.draw_handler_add(white_balance_picker, args, 'WINDOW', 'PRE_VIEW')

                # Set Cursor to EYEDROPPER icon
                self.cursor_set = True
                context.window.cursor_modal_set('EYEDROPPER')

                context.window_manager.modal_handler_add(self)

                return {'RUNNING_MODAL'}
            else:
                self.report({'WARNING'}, "No 3D view found")
                return {'CANCELLED'}

class PHOTOGRAPHER_OT_AddWhiteBalanceNode(bpy.types.Operator):
    bl_idname = "photographer.add_wb_node"
    bl_label = "Add White Balance Node"
    bl_description = ("Apply White Balance during Compositing. \n White Balance won't be "
                    "visible in viewport if Viewport Compositing is disabled, but will be applied to EXR files")
    bl_options = {'UNDO'}

    def execute(self,context):
        scene = context.scene
        if not scene.use_nodes:
            scene.use_nodes = True

        pfx_node = get_comp_group_node(context,postfx_grp_name)
        
        if not pfx_node:
            bpy.ops.photographer.post_effects_add()
            pfx_node = get_comp_group_node(context,postfx_grp_name)

        # Make sure PostFX node is also enabled
        if pfx_node.mute:
            pfx_node.mute = False

        # Get White Balance node in PFX group
        white_balance_node = get_comp_node_in_group(pfx_node,'wb_curves')
        if white_balance_node:
            white_balance_node.mute = False
        
        # Disable Color Management White Balance
        scene.view_settings.curve_mapping.white_level = (1,1,1)

        # Update Color Temperature and Tint
        settings = scene.camera.data.photographer
        settings.color_temperature = settings.color_temperature
        settings.tint = settings.tint

        return {'FINISHED'}

class PHOTOGRAPHER_OT_DisableWhiteBalanceNode(bpy.types.Operator):
    bl_idname = "photographer.disable_wb_node"
    bl_label = "Disable White Balance Node"
    bl_description = "Remove White Balance from Compositing and use Color Management White Balance"
    bl_options = {'UNDO'}

    def execute(self, context):
        pfx_node = get_comp_group_node(context,postfx_grp_name)
        
        if pfx_node:
            white_balance_node = get_comp_node_in_group(pfx_node,'wb_curves')
            if white_balance_node:
                white_balance_node.mute = True

        # Update Color Temperature and Tint
        settings = context.scene.camera.data.photographer
        settings.color_temperature = settings.color_temperature
        settings.tint = settings.tint

        return {'FINISHED'}
    

class PHOTOGRAPHER_OT_ApplyColorTemperatureMode(bpy.types.Operator):
    bl_idname = "photographer.apply_color_temperature_mode"
    bl_label = "Apply"
    bl_description = ("Updates White Balance after changing the Color Temperature Mode. \n"
                    "Default values will be updated if changing to Blender 4.3 mode, as they expect a Tint of 10")
    bl_options = {'UNDO'}

    def execute(self,context):
        prefs = bpy.context.preferences.addons[base_package].preferences
        cameras = [o for o in bpy.data.objects if o.type== 'CAMERA']
        lights = [o for o in bpy.data.objects if o.type== 'LIGHT']

        # Update Photographer Color Temperature defaults
        for cam in cameras :
            photographer = cam.data.photographer
            if prefs.color_temperature_mode == 'BLENDER':
                if photographer.tint == 0:
                    photographer.tint = 10
            else:
                if photographer.tint == 10:
                    photographer.tint = 0

            # Force refresh of Camera values:
            photographer.wb_enabled = photographer.wb_enabled
            if photographer.wb_enabled:
                photographer.color_temperature = photographer.color_temperature
                photographer.tint = photographer.tint

        # Update lights
        for world in bpy.data.worlds:
            lightmixer = world.lightmixer
            if prefs.color_temperature_mode == 'BLENDER':
                if lightmixer.hdri_tint == 0:
                    lightmixer.hdri_tint = 10
            else:
                if lightmixer.hdri_tint == 10:
                    lightmixer.hdri_tint = 0

            # Force refresh of World values
            if world.lightmixer.hdri_use_temperature:
                world.lightmixer.hdri_temperature = world.lightmixer.hdri_temperature
                world.lightmixer.hdri_tint =  world.lightmixer.hdri_tint

        bpy.ops.photographer.applylightsettings()

        return {'FINISHED'}
