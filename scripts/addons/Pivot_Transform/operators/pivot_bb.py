import bpy, bmesh
from bpy.types import Gizmo, GizmoGroup
from mathutils import Matrix, Vector
from ..utils.draw import draw_circle_2d, draw_cross, draw_box
from ..utils.utils import del_duplicate, set_pivot_location
from bpy_extras import view3d_utils
from gpu import state


# --- координаты элементов
def co_elements(): # Нужно добавить для режима редактирования проверку на выделенные элементы
    co = []

    context = bpy.context

    selObj = context.selected_objects
    for obj in selObj:
        mw = obj.matrix_world



        if obj.type == 'MESH':
            if obj.mode == 'EDIT':
                bm = bmesh.from_edit_mesh(obj.data)
                for v in bm.verts:
                    if v.select:
                        co.append(mw @ v.co)
            else:
                for v in obj.data.vertices:
                    co.append(mw @ v.co)


        elif obj.type == 'ARMATURE':
            coOld = []
            if obj.mode == 'EDIT':
                for bone in obj.data.bones:
                    coOld.append(mw @ bone.head_local)
                    coOld.append(mw @ bone.tail_local)
            else:
                for bone in obj.pose.bones:
                    coOld.append(mw @ bone.head)
                    coOld.append(mw @ bone.tail)

            delDup = del_duplicate(coOld)
            co.append(delDup)


        elif obj.type == 'CURVE':
            for s in obj.data.splines:
                for p in s.bezier_points:
                    co.append(mw @ p.co)


        elif obj.type == 'SURFACE':
            for s in obj.data.splines:
                for p in s.points:
                    co.append(mw @ p.co)


        elif obj.type == 'META':
            for e in obj.data.elements:
                co.append(mw @ e.co)


        elif obj.type == 'LATTICE':
            for p in obj.data.points:
                co.append(mw @ p.co)


        else:
            pass


    return co



# --- координаты точек
def points_bb():
    vertex_co = co_elements()

    orient = bpy.context.scene.transform_orientation_slots[0].type

    if orient == 'GLOBAL':
        vCo = []
        minX = min([vCo.x for vCo in vertex_co])
        maxX = max([vCo.x for vCo in vertex_co])

        minY = min([vCo.y for vCo in vertex_co])
        maxY = max([vCo.y for vCo in vertex_co])

        minZ = min([vCo.z for vCo in vertex_co])
        maxZ = max([vCo.z for vCo in vertex_co])

        vec0 = Vector((minX, minY, minZ))
        vec1 = Vector((minX, minY, maxZ))
        vec2 = Vector((minX, maxY, minZ))
        vec3 = Vector((minX, maxY, maxZ))
        vec4 = Vector((maxX, minY, minZ))
        vec5 = Vector((maxX, minY, maxZ))
        vec6 = Vector((maxX, maxY, minZ))
        vec7 = Vector((maxX, maxY, maxZ))
    else:
        mat = bpy.context.object.matrix_world
        verts_rot = []
        verts_rot.extend([mat.inverted()  @ v for v in vertex_co])

        vCo = []

        minX = min([vCo.x for vCo in verts_rot])
        maxX = max([vCo.x for vCo in verts_rot])

        minY = min([vCo.y for vCo in verts_rot])
        maxY = max([vCo.y for vCo in verts_rot])

        minZ = min([vCo.z for vCo in verts_rot])
        maxZ = max([vCo.z for vCo in verts_rot])


        vec0 = mat @ Vector((minX, minY, minZ))
        vec1 = mat @ Vector((minX, minY, maxZ))
        vec2 = mat @ Vector((minX, maxY, minZ))
        vec3 = mat @ Vector((minX, maxY, maxZ))
        vec4 = mat @ Vector((maxX, minY, minZ))
        vec5 = mat @ Vector((maxX, minY, maxZ))
        vec6 = mat @ Vector((maxX, maxY, minZ))
        vec7 = mat @ Vector((maxX, maxY, maxZ))


    vCo.append(vec0)  # 0
    vCo.append(vec1)  # 1
    vCo.append(vec2)  # 2
    vCo.append(vec3)  # 3
    vCo.append(vec4)  # 4
    vCo.append(vec5)  # 5
    vCo.append(vec6)  # 6
    vCo.append(vec7)  # 7

    vCo.append( (vCo[0] + vCo[1]) / 2 )  # 8
    vCo.append( (vCo[1] + vCo[5]) / 2 )  # 9
    vCo.append( (vCo[5] + vCo[4]) / 2 )  # 10
    vCo.append( (vCo[0] + vCo[4]) / 2 )  # 11

    vCo.append( (vCo[3] + vCo[7]) / 2 )  # 12
    vCo.append( (vCo[7] + vCo[6]) / 2 )  # 13
    vCo.append( (vCo[3] + vCo[2]) / 2 )  # 14
    vCo.append( (vCo[2] + vCo[6]) / 2 )  # 15

    vCo.append( (vCo[5] + vCo[7]) / 2 )  # 16
    vCo.append( (vCo[3] + vCo[1]) / 2 )  # 17
    vCo.append( (vCo[4] + vCo[6]) / 2 )  # 18
    vCo.append( (vCo[2] + vCo[0]) / 2 )  # 19

    vCo.append( (vCo[1] + vCo[2]) / 2 )  # 20
    vCo.append( (vCo[3] + vCo[6]) / 2 )  # 21
    vCo.append( (vCo[7] + vCo[4]) / 2 )  # 22
    vCo.append( (vCo[5] + vCo[0]) / 2 )  # 23
    vCo.append( (vCo[1] + vCo[7]) / 2 )  # 24
    vCo.append( (vCo[0] + vCo[6]) / 2 )  # 25

    return vCo



def co_objects():
    selObj = bpy.context.selected_objects
    midPoint = Vector()

    if bpy.context.mode == 'EDIT_MESH':
        uniques = bpy.context.objects_in_mode_unique_data

        bms = {}
        for obj in uniques:
            bms[obj] = bmesh.from_edit_mesh(obj.data)

        verts = []
        for ob in bms:
            verts.extend([ob.matrix_world @ v.co  for v in bms[ob].verts if v.select])

        midPoint = sum(verts, Vector()) / len(verts)

        """ xCo = midPoint
        xCo[0] = 0
        yCo = midPoint
        yCo[1] = 0
        zCo = midPoint
        zCo[2] = 0 """

    else:
        object_co = [obj.location for obj in selObj]
        midPoint = sum(object_co, Vector()) / len(selObj)


        """ xCo = midPoint
        xCo[0] = 0
        yCo = midPoint
        yCo[1] = 0
        zCo = midPoint
        zCo[2] = 0 """

    return midPoint



class PT_GT_bb_circle(Gizmo):
    bl_idname = 'PT_GT_bb_circle'


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.custom_shape = None


    def draw(self, context):
        self.draw_custom_shape(self.custom_shape)

        orig_loc = self.matrix_basis.decompose()[0]
        orig_rot_camera = context.region_data.view_matrix.inverted().decompose()[1]
        orig_loc_mat = Matrix.Translation(orig_loc)
        orig_scale_mat = Matrix.Scale(1, 4, (1, 0, 0)) @ Matrix.Scale(1, 4, (0, 1, 0)) @ Matrix.Scale(1, 4, (0, 0, 1))
        self.matrix_basis = orig_loc_mat @ orig_rot_camera.to_matrix().to_4x4() @ orig_scale_mat


    def draw_select(self, context, select_id):
        self.draw_custom_shape(self.custom_shape, select_id=select_id)


    def setup(self):
        shape = draw_circle_2d(segments=4)

        if self.custom_shape is None:
            self.custom_shape = self.new_custom_shape('TRI_FAN', shape)

        self.scale_basis = 0.1
        self.alpha = 0.8
        self.alpha_highlight = 1.0
        self.color_highlight = (0.11, 0.11, 0.12)
        self.use_grab_cursor = False


    def modal(self, context, event, tweak):
        return {'FINISHED'}


    def invoke(self, context, event):
        loc = self.matrix_basis.translation
        if event.ctrl:
            set_pivot_location( self, context, location = loc, cursor = True )
        else:
            set_pivot_location( self, context, location = loc, undoPush = True, message = 'Pivot To BBox' )
        props = context.preferences.addons['Pivot_Transform'].preferences
        if props.bbCloseAfter:
            props.bbox = False

        return {'RUNNING_MODAL'}



# --- ГИЗМО
class PT_GT_bb_point(Gizmo):
    bl_idname = 'PT_GT_bb_point'


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.custom_shape = None
        self.tipe_shape = 'CROSS'
        self.median_centr = [Vector((0,0,1)),Vector((0,0,2))]


    def test_select(self, context, location):
        context.area.tag_redraw()
        return -1


    def draw(self, context):
        state.blend_set('ALPHA')
        #state.line_width_set(4.0)
        state.point_size_set(15.0)
        self.draw_custom_shape(self.custom_shape)
        state.point_size_set(1.0)
        state.blend_set('NONE')

        # Orient To View
        if self.tipe_shape == 'CIRCLE':
            orig_loc = self.matrix_basis.decompose()[0]
            orig_rot_camera = bpy.context.region_data.view_matrix.inverted().decompose()[1]

            orig_loc_mat = Matrix.Translation(orig_loc)
            orig_scale_mat = Matrix.Scale(1, 4, (1, 0, 0)) @ Matrix.Scale(1, 4, (0, 1, 0)) @ Matrix.Scale(1, 4, (0, 0, 1))
            self.matrix_basis = orig_loc_mat @ orig_rot_camera.to_matrix().to_4x4() @ orig_scale_mat

    def draw_select(self, context, select_id):
        self.draw_custom_shape(self.custom_shape, select_id=select_id)  # LINE_STRIP, TRI_FAN LINES

    def setup(self):
        if self.tipe_shape is not None:
            if self.tipe_shape == 'CROSS':
                shape = draw_box()
            else:
                shape = draw_circle_2d(segments=16)


        if self.custom_shape is None:
            if self.tipe_shape == 'CROSS':
                self.custom_shape = self.new_custom_shape('TRIS', shape)
            else:
                self.custom_shape = self.new_custom_shape('TRI_FAN', shape)

        self.scale_basis = 0.1
        self.alpha = 0.8
        self.alpha_highlight = 1.0
        self.color_highlight = (0.11, 0.11, 0.12)
        #self.use_select_background = False
        self.use_grab_cursor = False
        #self.use_tooltip = True


    def modal(self, context, event, tweak):
        return {'FINISHED'}

    def invoke(self, context, event):
        loc = self.matrix_basis.translation
        if event.ctrl:
            set_pivot_location( self, context, location = loc, cursor = True )
        else:
            set_pivot_location( self, context, location = loc, undoPush = True, message = 'Pivot To BBox' )
        props = context.preferences.addons['Pivot_Transform'].preferences
        if props.bbCloseAfter:
            props.bbox = False

        return {'RUNNING_MODAL'}



class PT_GGT_bbox(GizmoGroup):
    bl_idname = 'PT_GGT_bbox'
    bl_label = 'BBox'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {'3D', 'PERSISTENT'} # , 'TOOL_INIT', 'SELECT', , 'SCALE' , 'SHOW_MODAL_ALL' , 'DEPTH_3D'


    @classmethod
    def poll(cls, context):
        props = context.preferences.addons['Pivot_Transform'].preferences
        if props.bbox:
            mode = {'OBJECT', 'EDIT_MESH'} # context.object.type in {'MESH', 'ARMATURE', 'CURVE', 'SURFACE', 'META', 'LATTICE'}
            if context.mode in mode:
                obj = context.object
                if obj is not None:
                    obSel = context.selected_objects
                    edObj = context.objects_in_mode_unique_data

                    if context.mode=='OBJECT':
                        return len(obSel)>0

                    elif context.mode=='EDIT_MESH' and len(edObj)>0:
                        s = context.scene.statistics(context.view_layer)
                        v = s.split('Verts:')[1].split(' ')[0]
                        return v[0] != '0'


    def setup(self, context):
        bb_seg = 4
        align_seg = 12

        scale_r = 0.1
        scale_b = 0.05
        scale_g = 0.07
        # BB points
        # R
        self.bb_1 = self.gizmos.new('PT_GT_bb_point')
        self.bb_1.scale_basis = scale_r
        self.bb_1.segments = bb_seg

        self.bb_2 = self.gizmos.new('PT_GT_bb_point')
        self.bb_2.scale_basis = scale_r
        self.bb_2.segments = bb_seg

        self.bb_3 = self.gizmos.new('PT_GT_bb_point')
        self.bb_3.scale_basis = scale_r
        self.bb_3.segments = bb_seg

        self.bb_4 = self.gizmos.new('PT_GT_bb_point')
        self.bb_4.scale_basis = scale_r
        self.bb_4.segments = bb_seg

        self.bb_5 = self.gizmos.new('PT_GT_bb_point')
        self.bb_5.scale_basis = scale_r
        self.bb_5.segments = bb_seg

        self.bb_6 = self.gizmos.new('PT_GT_bb_point')
        self.bb_6.scale_basis = scale_r
        self.bb_6.segments = bb_seg

        self.bb_7 = self.gizmos.new('PT_GT_bb_point')
        self.bb_7.scale_basis = scale_r
        self.bb_7.segments = bb_seg

        self.bb_8 = self.gizmos.new('PT_GT_bb_point')
        self.bb_8.scale_basis = scale_r
        self.bb_8.segments = bb_seg


        # B
        self.bb_9 = self.gizmos.new('PT_GT_bb_point')
        self.bb_9.scale_basis = scale_b
        self.bb_9.segments = bb_seg

        self.bb_10 = self.gizmos.new('PT_GT_bb_point')
        self.bb_10.scale_basis = scale_b
        self.bb_10.segments = bb_seg

        self.bb_11 = self.gizmos.new('PT_GT_bb_point')
        self.bb_11.scale_basis = scale_b
        self.bb_11.segments = bb_seg

        self.bb_12 = self.gizmos.new('PT_GT_bb_point')
        self.bb_12.scale_basis = scale_b
        self.bb_12.segments = bb_seg

        self.bb_13 = self.gizmos.new('PT_GT_bb_point')
        self.bb_13.scale_basis = scale_b
        self.bb_13.segments = bb_seg

        self.bb_14 = self.gizmos.new('PT_GT_bb_point')
        self.bb_14.scale_basis = scale_b
        self.bb_14.segments = bb_seg

        self.bb_15 = self.gizmos.new('PT_GT_bb_point')
        self.bb_15.scale_basis = scale_b
        self.bb_15.segments = bb_seg

        self.bb_16 = self.gizmos.new('PT_GT_bb_point')
        self.bb_16.scale_basis = scale_b
        self.bb_16.segments = bb_seg

        self.bb_17 = self.gizmos.new('PT_GT_bb_point')
        self.bb_17.scale_basis = scale_b
        self.bb_17.segments = bb_seg

        self.bb_18 = self.gizmos.new('PT_GT_bb_point')
        self.bb_18.scale_basis = scale_b
        self.bb_18.segments = bb_seg

        self.bb_19 = self.gizmos.new('PT_GT_bb_point')
        self.bb_19.scale_basis = scale_b
        self.bb_19.segments = bb_seg

        self.bb_20 = self.gizmos.new('PT_GT_bb_point')
        self.bb_20.scale_basis = scale_b
        self.bb_20.segments = bb_seg

        # G
        self.bb_21 = self.gizmos.new('PT_GT_bb_point')
        self.bb_21.scale_basis = scale_g
        self.bb_21.segments = bb_seg

        self.bb_22 = self.gizmos.new('PT_GT_bb_point')
        self.bb_22.scale_basis = scale_g
        self.bb_22.segments = bb_seg

        self.bb_23 = self.gizmos.new('PT_GT_bb_point')
        self.bb_23.scale_basis = scale_g
        self.bb_23.segments = bb_seg

        self.bb_24 = self.gizmos.new('PT_GT_bb_point')
        self.bb_24.scale_basis = scale_g
        self.bb_24.segments = bb_seg

        self.bb_25 = self.gizmos.new('PT_GT_bb_point')
        self.bb_25.scale_basis = scale_g
        self.bb_25.segments = bb_seg

        self.bb_26 = self.gizmos.new('PT_GT_bb_point')
        self.bb_26.scale_basis = scale_g
        self.bb_26.segments = bb_seg


        # Align points
        self.align_x = self.gizmos.new('PT_GT_bb_circle')#.tipe_shape = 'CIRCLE'
        self.align_x.scale_basis = 0.05
        self.align_x.segments = align_seg

        self.align_y = self.gizmos.new('PT_GT_bb_circle')#.tipe_shape = 'CIRCLE'
        self.align_y.scale_basis = 0.05
        self.align_y.segments = align_seg

        self.align_z = self.gizmos.new('PT_GT_bb_circle')#.tipe_shape = 'CIRCLE'
        self.align_z.scale_basis = 0.05
        self.align_z.segments = align_seg

    def draw_prepare(self, context):
        # Определение минимальных и максимальных значений прозрачности и цвета
        min_alpha = 0.1  # Минимальная прозрачность
        max_alpha = 1.0  # Максимальная прозрачность
        min_scale = 0.02  # Минимальный масштаб
        max_scale = 0.15  # Максимальный масштаб
        # Базовые цвета для вершин, рёбер и граней
        x_color_axis = (1, 0.23, 0.18)
        y_color_axis = (0.15, 0.8, 0.25)
        z_color_axis = (0, 0.48, 1)
        vertex_color = (0.02, 0.78, 0.75)
        edge_color = (1, 0.58, 0)
        face_color = (0.35, 0.34, 0.84)

        # Минимальная интенсивность цвета (чем меньше значение, тем темнее цвет)
        min_color_intensity = 0.2

        pCo = points_bb()
        cam_pos = context.region_data.view_matrix.inverted().translation
        gizmos = []
        distances = []

        # Вершинные точки
        gizmos_vertex = [self.bb_1, self.bb_2, self.bb_3, self.bb_4, self.bb_5, self.bb_6, self.bb_7, self.bb_8]
        for i, gizmo in enumerate(gizmos_vertex):
            gizmo.matrix_basis.translation = pCo[i]
            pos = gizmo.matrix_basis.translation
            gizmos.append(gizmo)
            distance = (pos - cam_pos).length
            distances.append(distance)

        # Рёберные точки
        gizmos_edge = [self.bb_9, self.bb_10, self.bb_11, self.bb_12, self.bb_13, self.bb_14, self.bb_15, self.bb_16, self.bb_17, self.bb_18, self.bb_19, self.bb_20]
        for i, gizmo in enumerate(gizmos_edge, start=8):
            gizmo.matrix_basis.translation = pCo[i]
            pos = gizmo.matrix_basis.translation
            gizmos.append(gizmo)
            distance = (pos - cam_pos).length
            distances.append(distance)

        # Гранные точки
        gizmos_face = [self.bb_21, self.bb_22, self.bb_23, self.bb_24, self.bb_25, self.bb_26]
        for i, gizmo in enumerate(gizmos_face, start=20):
            gizmo.matrix_basis.translation = pCo[i]
            pos = gizmo.matrix_basis.translation
            gizmos.append(gizmo)
            distance = (pos - cam_pos).length
            distances.append(distance)

        # Точки выравнивания
        pos_align = co_objects()
        self.align_x.matrix_basis.translation = pos_align
        self.align_x.matrix_basis.translation[0] = 0
        self.align_y.matrix_basis.translation = pos_align
        self.align_y.matrix_basis.translation[1] = 0
        self.align_z.matrix_basis.translation = pos_align
        self.align_z.matrix_basis.translation[2] = 0

        # Устанавливаем постоянные цвета и прозрачность для точек выравнивания
        self.align_x.color = x_color_axis
        self.align_x.alpha = max_alpha
        self.align_y.color = y_color_axis
        self.align_y.alpha = max_alpha
        self.align_z.color = z_color_axis
        self.align_z.alpha = max_alpha

        # Вычисление минимального и максимального расстояния для остальных гизмо
        if distances:
            min_distance = min(distances)
            max_distance = max(distances)
        else:
            min_distance = max_distance = 0

        # Настройка прозрачности и цвета на основе расстояния
        for gizmo, distance in zip(gizmos, distances):
            if max_distance - min_distance > 1e-6:
                normalized_distance = (distance - min_distance) / (max_distance - min_distance)
            else:
                normalized_distance = 0.0

            # Расчёт прозрачности
            alpha = max_alpha - normalized_distance * (max_alpha - min_alpha)
            alpha = max(min_alpha, min(max_alpha, alpha))
            gizmo.alpha = alpha

            # Расчёт масштаба
            scale = max_scale - normalized_distance * (max_scale - min_scale)
            scale = max(min_scale, min(max_scale, scale))
            gizmo.scale_basis = scale

            # Расчёт цветовой интенсивности
            color_intensity = max(1.0 - normalized_distance * (1.0 - min_color_intensity), min_color_intensity)

            # Установка базового цвета в зависимости от типа гизмо
            if gizmo in gizmos_vertex:
                base_color = vertex_color
            elif gizmo in gizmos_edge:
                base_color = edge_color
            elif gizmo in gizmos_face:
                base_color = face_color
            else:
                base_color = gizmo.color  # На всякий случай

            # Применение цветовой интенсивности
            gizmo.color = tuple([component * color_intensity for component in base_color])






classes = [
    PT_GT_bb_circle,
    PT_GT_bb_point,
    PT_GGT_bbox,
    ]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)