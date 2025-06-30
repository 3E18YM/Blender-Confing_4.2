from .common_imports import *


# -- Normal routine functions --

def numpy_get_verts_selection(obj):
    vertices_count = len(obj.data.vertices)
    selection_array = np.zeros(vertices_count, dtype=np.bool)
    obj.data.vertices.foreach_get("select", selection_array)

    return selection_array


def numpy_get_verts_co(obj):
    vertices_count = len(obj.data.vertices)
    coordinates_array = np.zeros(vertices_count * 3, dtype=np.float32)
    obj.data.vertices.foreach_get("co", coordinates_array)
    coordinates_array.shape = (vertices_count, 3)

    return coordinates_array


def numpy_get_selected_verts_co(obj):
    obj.update_from_editmode()
    verts_selection = numpy_get_verts_selection(obj)
    verts_co = numpy_get_verts_co(obj)

    return verts_co[verts_selection]


def numpy_get_selected_verts_indices(obj):
    obj.update_from_editmode()
    vertices_count = len(obj.data.vertices)
    verts_indices = np.array(range(vertices_count))
    verts_selection = numpy_get_verts_selection(obj)

    return verts_indices[verts_selection]


def corners_to_world_matrix(minimum=(0, 0, 0), maximum=(1, 1, 1)):
    x = Vector((maximum[0] - minimum[0], 0, 0))
    y = Vector((0, maximum[1] - minimum[1], 0))
    z = Vector((0, 0, maximum[2] - minimum[2]))
    return Matrix.Translation(minimum) @ Matrix([x, y, z]).transposed().to_4x4()

def points_to_world_matrix(points):
    min_corner, max_corner = points_to_corners(points)
    return corners_to_world_matrix(min_corner, max_corner)

def points_to_corners(points):
    if isinstance(points, np.ndarray):
        minimum = np.min(points, axis=0)
        maximum = np.max(points, axis=0)
    elif isinstance(points, list):
        minimum = tuple(min(points, key=lambda point: point[x])[x] for x in (0, 1, 2))
        maximum = tuple(max(points, key=lambda point: point[x])[x] for x in (0, 1, 2))
    return minimum, maximum

def local_to_object_matrix(object):
    return object.matrix_world @ bounds_to_matrix(object.bound_box)

def bounds_to_matrix(bounds):
    origin = Vector(bounds[0])
    x = Vector(bounds[4]) - origin
    y = Vector(bounds[3]) - origin
    z = Vector(bounds[1]) - origin
    return Matrix.Translation(origin) @ Matrix([x, y, z]).transposed().to_4x4()

def get_matrix_corners(matrix):
    return matrix @ Vector((0, 0, 0)), matrix @ Vector((1, 1, 1))

def cube_size(matrix):
    corners = get_matrix_corners(matrix)
    return (corners[1] - corners[0]).length

def matrix_to_point(matrix, x_depth, y_depth, z_depth):
    depths = {"MIN": 0, "CENTER": 0.5, "MAX": 1}
    return matrix @ Vector((depths[x_depth], depths[y_depth], depths[z_depth]))

def apply_matrix_to_points(points, matrix):
    return [matrix @ Vector(point) for point in points]

def get_matrix_grid_point(matrix, index):
    points = ((0, 0, 0),     (0, 0, 0.5),     (0, 0, 1),
              (0, 0.5, 0),   (0, 0.5, 0.5),   (0, 0.5, 1),
              (0, 1, 0),     (0, 1, 0.5),     (0, 1, 1),
              (0.5, 0, 0),   (0.5, 0, 0.5),   (0.5, 0, 1),
              (0.5, 0.5, 0), (0.5, 0.5, 0.5), (0.5, 0.5, 1),
              (0.5, 1, 0),   (0.5, 1, 0.5),   (0.5, 1, 1),
              (1, 0, 0),     (1, 0, 0.5),     (1, 0, 1),
              (1, 0.5, 0),   (1, 0.5, 0.5),   (1, 0.5, 1),
              (1, 1, 0),     (1, 1, 0.5),     (1, 1, 1))
    return matrix @ Vector(points[index])

def get_matrix_midpoint_point(matrix, index):
    points = ((0, 0, 0),   (0, 0, 0.5), (0, 0, 1),
              (0, 0.5, 0), (0, 0.5, 1),
              (0, 1, 0),   (0, 1, 0.5), (0, 1, 1),
              (0.5, 0, 0), (0.5, 0, 1),
              (0.5, 1, 0), (0.5, 1, 1),
              (1, 0, 0),   (1, 0, 0.5), (1, 0, 1),
              (1, 0.5, 0), (1, 0.5, 1),
              (1, 1, 0),   (1, 1, 0.5), (1, 1, 1))
    return matrix @ Vector(points[index])

def get_object_rotation(object):
    if object.rotation_mode not in ("QUATERNION", "AXIS_ANGLE"):
        return object.rotation_euler.to_quaternion()
    elif object.rotation_mode == "QUATERNION":
        return object.rotation_quaternion
    elif object.rotation_mode == "AXIS_ANGLE":
        return Quaternion(object.rotation_axis_angle[1:], object.rotation_axis_angle[0])

def get_submatrix(matrix, subtype, object=None):
    translation = rotation = scale = Matrix()
    if "TRANSLATION" in subtype:
        translation = Matrix.Translation(matrix.to_translation())
    if "ROTATION" in subtype:
        if object:
            rotation = get_object_rotation(object).to_matrix().to_4x4()
        else:
            rotation = matrix.to_3x3().normalized().to_4x4()
    if "SCALE" in subtype:
        scale_factor = matrix.to_scale()
        scale = Matrix([(scale_factor[0], 0, 0, 0),
                        (0, scale_factor[1], 0, 0),
                        (0, 0, scale_factor[2], 0),
                        (0, 0, 0, 1)])
    new_matrix = translation @ rotation @ scale
    return new_matrix

def offset_by_normals(geometry, geometry_indices, distance):
    vertices = [Vector(v) for v in geometry]
    tri_normals = []
    for tri in geometry_indices:
        v1 = vertices[tri[1]] - vertices[tri[0]]
        v2 = vertices[tri[2]] - vertices[tri[0]]
        tri_normals.append(v1.cross(v2).normalized())

    vertex_normals = []
    tri_indices = []
    for vert_index, vertex in enumerate(vertices):
        normal = Vector()
        add_tri_index = True
        for tri_index, tri in enumerate(geometry_indices):
            if vert_index in tri:
                if add_tri_index:
                    tri_indices.append(tri_index)
                    add_tri_index = False
                index1, index2 = set(tri) - {vert_index}
                v1 = vertices[index1] - vertices[vert_index]
                v2 = vertices[index2] - vertices[vert_index]
                normal += tri_normals[tri_index] * v1.rotation_difference(v2).angle
        vertex_normals.append(normal.normalized())

    return [vertices[i] + (vertex_normals[i] * ((1 / vertex_normals[i].dot(tri_normals[tri_indices[i]])) * distance))
            for i in range(len(vertices))]

def project_to_plane(plane, origin_point, direction_point):
    plane_inverted = plane.inverted()
    origin = plane_inverted @ origin_point
    direction = plane_inverted.to_3x3() @ direction_point
    return plane @ project_to_worldplane(origin, direction)

def project_to_worldplane(origin_point, direction):
    hit_point = direction * (origin_point[2] / -direction[2])
    return hit_point + origin_point
