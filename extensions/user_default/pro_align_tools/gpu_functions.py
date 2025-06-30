from .common_imports import *

def create_batch_shader(draw_type, vertices_stream, indices=None, stipple_lines=False):

    f = gpu.types.GPUVertFormat()
    f.attr_add(id="pos", comp_type='F32', len=3, fetch_mode='FLOAT')

    vbo = gpu.types.GPUVertBuf(len=len(vertices_stream), format=f)
    vbo.attr_fill(id="pos", data=vertices_stream)

    if draw_type == "TRIANGLES":

        if indices is None:

            # The TRI_FAN type was deprecated in Blender version 3.2 with the goal
            # of providing support for other draw engines where TRI_FAN is not supported.
            # TRI_FAN will be deleted in future releases
            # batch = gpu.types.GPUBatch(type="TRI_FAN", buf=vbo)

            # This algorithm creates indices compatible with TRIS and mimics the faces produced by TRI_FAN
            # It generates a usable list of indices when no triangle indices are available
            indices = [(0, index, index+1) for index, _ in enumerate(vertices_stream[:-1]) if index != 0]

        ibo = gpu.types.GPUIndexBuf(type="TRIS", seq=indices)
        batch = gpu.types.GPUBatch(type="TRIS", buf=vbo, elem=ibo)

    elif draw_type == "LINES":
        ibo = gpu.types.GPUIndexBuf(type="LINES", seq=indices)
        batch = gpu.types.GPUBatch(type="LINES", buf=vbo, elem=ibo)

    elif draw_type == "POINTS":
        batch = gpu.types.GPUBatch(type="POINTS", buf=vbo)


    if draw_type == "LINES":

        if stipple_lines:

            shader = get_line_stipple_shader()

        else:

            shader = gpu.shader.from_builtin("POLYLINE_UNIFORM_COLOR")

    else:

        shader = gpu.shader.from_builtin("UNIFORM_COLOR")

    return batch, shader

# Custom GLSL shader for stipple lines
def get_line_stipple_shader():

    vertex_shader = """
        uniform mat4 perspective_matrix;
        in vec3 pos;

        void main()
            {gl_Position = perspective_matrix * vec4(pos, 1.0f);}
    """

    geometry_shader = """
        layout(lines) in;
        layout(line_strip, max_vertices=2) out;

        uniform vec2 screen_size;
        noperspective out float texture_coordinate;

        void main()
        {
            // get 2D position in screen space and take its length to stretch the texture pattern
            vec2 position0 = screen_size * gl_in[0].gl_Position.xy / gl_in[0].gl_Position.w;
            vec2 position1 = screen_size * gl_in[1].gl_Position.xy / gl_in[1].gl_Position.w;
            float texture_size = length(position1 - position0);

            // assign a default order to draw the lines. If the end point lies outside the frustum, invert
            // the drawing order of the points so that the lines always get drawn, even when cropped by the view
            int position0_index = 0;
            int position1_index = 1;
            if (gl_in[1].gl_Position.w < 0) {position0_index = 1; position1_index = 0;}

            // emit the first position with the base texture coordinate
            gl_Position = gl_in[position0_index].gl_Position;
            texture_coordinate = 0.0;
            EmitVertex();

            // emit the second position with the final texture coordinate
            gl_Position = gl_in[position1_index].gl_Position;
            texture_coordinate = texture_size;
            EmitVertex();

            EndPrimitive();
        }
    """

    fragment_shader = """
        uniform int pattern;      // an integer between 0 and 0xFFFF representing the bitwise pattern
        uniform int pattern_size; // the size of the "on screen" pattern, in pixels
        uniform vec4 color;
        noperspective in float texture_coordinate;
        out vec4 fragColor;

        void main()
        {
            // use 4 bytes for the masking pattern
            // map the texture coordinate to the interval [0,2*8]
            uint bitpos = uint(round(texture_coordinate / pattern_size)) % 16U;

            // move a unit bit 1U to position bitpos so that
            // bit is an integer between 1 and 1000 0000 0000 0000 = 0x8000
            uint bit = (1U << bitpos);

            // test the bit against the masking pattern
            // --SOLID--       pattern = 0xFFFF;  // = 1111 1111 1111 1111 = solid pattern
            // --DASH--        pattern = 0x3F3F;  // = 0011 1111 0011 1111
            // --DOT--         pattern = 0x6666;  // = 0110 0110 0110 0110
            // --DASHDOT--     pattern = 0xFF18;  // = 1111 1111 0001 1000
            // --DASHDOTDOT--  pattern = 0x7E66;  // = 0111 1110 0110 0110
            uint up = uint(pattern);

            // discard the bit if it doesn't match the masking pattern
            if ((up & bit) == 0U) discard;

            fragColor = color;
        }
    """
    return gpu.types.GPUShader(vertex_shader, fragment_shader, geocode=geometry_shader)


_offset_matrix = Matrix.Translation(Vector((0, 0, -0.000001)))

def _offset_projection_matrix():

    """Offsets the projection matrix towards the view to avoid Z-fighting on coplanar faces during depth tests"""

    # Offset the projection matrix in the Z axis
    gpu.matrix.load_projection_matrix(_offset_matrix @ gpu.matrix.get_projection_matrix())


def draw_batch_shader(batch_shader, color, matrix=Matrix(), offset: bool = False):

    with gpu.matrix.push_pop(), gpu.matrix.push_pop_projection():

        gpu.matrix.multiply_matrix(matrix)

        if offset:

            _offset_projection_matrix()

        batch, shader = batch_shader
        shader.bind()
        shader.uniform_float("color", color)
        batch.draw(shader)


def draw_batch_shader_line(batch_shader, region, color, width=1, matrix=Matrix()):

    with gpu.matrix.push_pop():

        gpu.matrix.multiply_matrix(matrix)

        batch, shader = batch_shader
        shader.bind()
        shader.uniform_float("color", color)
        shader.uniform_float("lineWidth", width)
        shader.uniform_float("viewportSize", (region.width, region.height))
        batch.draw(shader)


def draw_stipple_lines_batch_shader(batch_shader, context, color, pattern, pattern_size, matrix=Matrix()):

    region = context.region
    rv3d = context.region_data
    batch, shader = batch_shader
    shader.bind()
    shader.uniform_float("perspective_matrix", rv3d.perspective_matrix @ matrix)
    shader.uniform_float("screen_size", (region.width, region.height))
    shader.uniform_int("pattern", pattern)
    shader.uniform_int("pattern_size", pattern_size) # 16 pixels is the default bitwise pattern size
    shader.uniform_float("color", color)
    batch.draw(shader)
