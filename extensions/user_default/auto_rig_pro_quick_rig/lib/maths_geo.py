import bpy
from math import *
from mathutils import *

def signed_angle(vector_u, vector_v, normal):
    normal = normal.normalized()
    a = vector_u.angle(vector_v)
    if vector_u.cross(vector_v).angle(normal) < 1:
        a = -a
    return a
    
    
def rotate_vec_mat(vec, angle, pivot, axis):
    # rotate a vector around given pivot point,
    # angle and axis
    mat_rot = Matrix.Rotation(-angle, 4, axis)
    mat_to_center = Matrix.Translation(-pivot).to_4x4()
    return mat_to_center.inverted() @ mat_rot @ mat_to_center @ vec      
    
    
def project_point_onto_plane(q, p, n):
    # q = point
    # p = point belonging to the plane
    # n = plane normal
    n = n.normalized()
    return q - ((q - p).dot(n)) * n
    
    
def project_vec_onto_plane(x, n):
    # x: Vector
    # n: plane normal vector
    d = x.dot(n) / n.magnitude
    p = [d * n.normalized()[i] for i in range(len(n))]
    return Vector([x[i] - p[i] for i in range(len(x))])
    
    
def mat3_to_vec_roll(mat):
    vec = mat.col[1]
    vecmat = vec_roll_to_mat3(mat.col[1], 0)
    vecmatinv = vecmat.inverted()
    rollmat = vecmatinv @ mat
    roll = math.atan2(rollmat[0][2], rollmat[2][2])
    return vec, roll
    
    
def vec_roll_to_mat3(vec, roll):
    target = Vector((0, 0.1, 0))
    nor = vec.normalized()
    axis = target.cross(nor)
    if axis.dot(axis) > 0.0000000001: # this seems to be the problem for some bones, no idea how to fix
        axis.normalize()
        theta = target.angle(nor)
        bMatrix = Matrix.Rotation(theta, 3, axis)
    else:
        updown = 1 if target.dot(nor) > 0 else -1
        bMatrix = Matrix.Scale(updown, 3)
        bMatrix[2][2] = 1.0

    rMatrix = Matrix.Rotation(roll, 3, nor)
    mat = rMatrix @ bMatrix
    return mat