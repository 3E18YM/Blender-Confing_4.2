import bpy
import blf
import gpu
import random
import math
import colorsys
from gpu_extras.batch import batch_for_shader
from bpy_extras.view3d_utils import region_2d_to_origin_3d, region_2d_to_vector_3d
import logging

# Logger
logging.basicConfig(
    level=logging.DEBUG,
    format='[BAM] [%(levelname)s] MatOverlay: %(message)s'
)
logger = logging.getLogger(__name__)

# Словарь для случайного цвета оверлея
random_overlay_colors = {}

def get_random_legible_color(bg_color=(0.1, 0.1, 0.1, 1.0), threshold=0.25):
    while True:
        # hue, saturation, value
        h = random.random()
        s = random.uniform(0.5, 1.0)
        v = random.uniform(0.9, 1.0)

        # 2) back to RGB
        r, g, b = colorsys.hsv_to_rgb(h, s, v)

        # 3) Checking the distance to bg_color
        dist = math.sqrt(
            (r - bg_color[0])**2 +
            (g - bg_color[1])**2 +
            (b - bg_color[2])**2
        )
        if dist > threshold:
            return (r, g, b, 1.0)


class BAMMaterialOverlay:
    def __init__(self):
        self.handler = None
        self.text = ""
        self.font_id = 0  # font
        self.mouse_coords = (0, 0)
        self.overlay_active = False
        self.logging_enabled = True
        self.modal_running = False
        self.timer_active = False



    def draw_callback(self, context):
        if not self.overlay_active:
            return
        
        prefs = context.preferences.addons[__package__].preferences
        
        offset_x = prefs.overlay_offset_x
        offset_y = prefs.overlay_offset_y
        text_size = prefs.overlay_text_size
        text_color = prefs.overlay_text_color
        bg_color = prefs.overlay_bg_color
        border_color = prefs.overlay_border_color
        
            
        # Храним имя материала из под курсора в self.text
        material_name = self.text

        if prefs.overlay_text_color_random and material_name != "No Material":
            # Проверяем, есть ли уже цвет в кэше
            if material_name not in random_overlay_colors:
                random_overlay_colors[material_name] = get_random_legible_color(
                    bg_color, threshold=0.3
                )
            text_color = random_overlay_colors[material_name]
        else:
            # Иначе используем обычный цвет из настроек
            text_color = prefs.overlay_text_color
        
        
        gpu.state.blend_set('ALPHA')  # enable transparency


        # mouse and text coordinates
        mouse_x, mouse_y = self.mouse_coords
        text = self.text
        blf.size(self.font_id, text_size)

        # text width and height
        text_width, text_height = blf.dimensions(self.font_id, text)

        # box frame padding
        padding_x = 10
        padding_y = 10

        # box size
        box_x1 = mouse_x + offset_x - padding_x
        box_y1 = mouse_y + offset_y - padding_y - text_height
        box_x2 = mouse_x + offset_x + text_width + padding_x
        box_y2 = mouse_y + offset_y + padding_y

        # box color
        shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        shader.bind()

        # box color fill
        vertices = [
            (box_x1, box_y1),
            (box_x1, box_y2),
            (box_x2, box_y2),
            (box_x2, box_y1),
        ]
        batch = batch_for_shader(shader, 'TRI_FAN', {"pos": vertices})
        shader.uniform_float("color", bg_color)
        batch.draw(shader)

        # Outline
        line_vertices = vertices + [vertices[0]]
        batch = batch_for_shader(shader, 'LINE_STRIP', {"pos": line_vertices})
        shader.uniform_float("color", border_color)
        batch.draw(shader)

        # Draw text
        blf.position(self.font_id, mouse_x + offset_x, mouse_y + offset_y - text_height, 0)
        blf.color(self.font_id, *text_color) # White text
        blf.draw(self.font_id, text)

        gpu.state.blend_set('NONE')



    def add_draw_handler(self):
        if not self.handler:
            if self.logging_enabled:
                logger.debug("Adding a drawing handler.")
            self.handler = bpy.types.SpaceView3D.draw_handler_add(self.draw_callback, (bpy.context,), 'WINDOW', 'POST_PIXEL')
            if not self.timer_active:
                bpy.app.timers.register(self.refresh, persistent=True)
                self.timer_active = True
            self.overlay_active = True
            self.modal_running = True

    def remove_draw_handler(self):
        if self.handler:
            try:
                if self.logging_enabled:
                    logger.debug("Deleting the drawing handler.")
                bpy.types.SpaceView3D.draw_handler_remove(self.handler, 'WINDOW')
                self.handler = None
                self.overlay_active = False
                self.modal_running = False
                if self.timer_active:
                    bpy.app.timers.unregister(self.refresh)
                    self.timer_active = False
            except ValueError:
                logger.warning("An attempt to delete a non-existent handler.")
                self.handler = None


    def refresh(self):
        if self.overlay_active:
            #logger.debug("The timer performs a refresh.")  # time check
            for window in bpy.context.window_manager.windows:
                for area in window.screen.areas:
                    if area.type == 'VIEW_3D':
                        for region in area.regions:
                            if region.type == 'WINDOW':
                                area.tag_redraw()
        else:
            logger.debug("The timer is completed.") 
            return None
        return 0.016



bmoverlay = BAMMaterialOverlay()


class BAM_OT_toggle_bmat_overlay(bpy.types.Operator):
    bl_idname = "view3d.toggle_bmat_overlay"
    bl_label = "BAM Material Overlay Toggle"

    def get_material_name(self, context, event):
        region = context.region
        rv3d = context.region_data
        coord = (event.mouse_region_x, event.mouse_region_y)

        ray_origin = region_2d_to_origin_3d(region, rv3d, coord)
        view_vector = region_2d_to_vector_3d(region, rv3d, coord).normalized()

        depsgraph = context.evaluated_depsgraph_get()
        result, location, normal, index, obj, _ = context.scene.ray_cast(depsgraph, ray_origin, view_vector, distance=1000.0)

        if result and obj and obj.type == 'MESH':
            if index != -1 and obj.material_slots:
                # Use evaluated mesh to get the correct material index
                evaluated_obj = obj.evaluated_get(depsgraph)
                evaluated_mesh = evaluated_obj.to_mesh(preserve_all_data_layers=True, depsgraph=depsgraph)
                try:
                    if index < len(evaluated_mesh.polygons):
                        material_index = evaluated_mesh.polygons[index].material_index
                        if material_index < len(obj.material_slots):
                            material = obj.material_slots[material_index].material
                            if material:
                                return material.name
                finally:
                    evaluated_obj.to_mesh_clear()  # Clean up the temporary mesh
        return "No Material"


    def modal(self, context, event):
        if not bmoverlay.overlay_active:
            logger.debug("The modal operator is forcibly terminated.")
            return {'CANCELLED'}

        if event.type == 'MOUSEMOVE':
            bmoverlay.mouse_coords = (event.mouse_region_x, event.mouse_region_y)
            bmoverlay.text = self.get_material_name(context, event)
            context.area.tag_redraw()

        # Проверяем сочетание Shift + ESC
        elif event.type == 'ESC' and event.shift:
            logger.debug("Shift + ESC pressed, disabling overlay.")
            bmoverlay.remove_draw_handler()  # Отключаем оверлей
            if bmoverlay.modal_running:
                logger.debug("Forced termination of a modal operator.")
                bmoverlay.modal_running = False  # Устанавливаем false при полном отключении
            logger.debug("The overlay is disabled.")
            return {'CANCELLED'}

        return {'PASS_THROUGH'}


    def execute(self, context):
        if not bmoverlay.overlay_active:
            # Включаем оверлей
            bmoverlay.add_draw_handler()
            context.window_manager.modal_handler_add(self)
            bmoverlay.modal_running = True  # Устанавливаем True
            logger.debug("The overlay is enabled.")
            return {'RUNNING_MODAL'}
        else:
            # Отключаем оверлей
            bmoverlay.remove_draw_handler()
            if bmoverlay.modal_running:
                logger.debug("Forced termination of a modal operator.")
                bmoverlay.modal_running = False  # Устанавливаем false при полном отключении
            logger.debug("The overlay is disabled.")
            return {'FINISHED'}


def register():
    bpy.utils.register_class(BAM_OT_toggle_bmat_overlay)
    #bpy.utils.register_class(BAM_PT_BmatOverlay_panel)


def unregister():
    bpy.utils.unregister_class(BAM_OT_toggle_bmat_overlay)
    #bpy.utils.unregister_class(BAM_PT_BmatOverlay_panel)


if __name__ == "__main__":
    register()
