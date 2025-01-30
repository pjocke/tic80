# title:   matmult
# author:  pjocke, ChatGPT
# desc:    
# site:    
# license:
# version: 0.1
# script:  python

import math

width, height = 240.0, 136.0

def matrix_multiply(A, B):
    # Validate if multiplication is possible
    if len(A[0]) != len(B):
        raise ValueError("Number of columns in A must equal number of rows in B")
    
    # Get dimensions of the result matrix
    rows_A, cols_A = len(A), len(A[0])
    rows_B, cols_B = len(B), len(B[0])
    
    # Initialize the result matrix with zeros
    result = [[0 for _ in range(cols_B)] for _ in range(rows_A)]
    
    # Perform matrix multiplication
    for i in range(rows_A):          # Iterate through rows of A
        for j in range(cols_B):      # Iterate through columns of B
            for k in range(cols_A):  # Iterate through columns of A / rows of B
                result[i][j] += A[i][k] * B[k][j]
    
    return result

def transpose(matrix):
    result = []

    for col in range(len(matrix[0])):  # Iterate over columns of the original matrix
        new_row = []
        for row in range(len(matrix)):  # Iterate over rows of the original matrix
            new_row.append(matrix[row][col])  # Collect elements in the new row
        result.append(new_row)

    return result

def element_wise_division_in_place(arr1, arr2):
    # Ensure the arrays have the same length
    if len(arr1) != len(arr2):
        raise ValueError("Arrays must have the same length")
    
    # Perform element-wise division in place
    for i in range(len(arr1)):
        arr1[i] /= arr2[i]  # Update arr1 in place

def rotation_x(theta):
    return [
        [1, 0, 0, 0],
        [0, math.cos(theta), -math.sin(theta), 0],
        [0, math.sin(theta), math.cos(theta), 0],
        [0, 0, 0, 1]
    ]

def rotation_y(phi):
    return [
        [math.cos(phi), 0, math.sin(phi), 0],
        [0, 1, 0, 0],
        [-math.sin(phi), 0, math.cos(phi), 0],
        [0, 0, 0, 1]
    ]

def rotation_z(psi):
    return [
        [math.cos(psi), -math.sin(psi), 0, 0],
        [math.sin(psi), math.cos(psi), 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ]

def translation(tx, ty, tz):
    return [
        [1, 0, 0, tx],
        [0, 1, 0, ty],
        [0, 0, 1, tz],
        [0, 0, 0, 1]
    ]

def perspective(fov, aspect, z_near, z_far):
    f = 1 / math.tan(fov / 2)
    return [
        [f / aspect, 0, 0, 0],
        [0, f, 0, 0],
        [0, 0, (z_far + z_near) / (z_near - z_far), (2 * z_far * z_near) / (z_near - z_far)],
        [0, 0, -1, 0]
    ]

def to_pixel(x, y, width, height):
    x_pixel = int((x + 1) / 2 * width)
    y_pixel = int((1 - y) / 2 * height)  # Flip y for screen coordinates
    return x_pixel, y_pixel

def map_value(x, in_min=0, in_max=240, out_min=-5, out_max=-10):
    return out_min + (x - in_min) * (out_max - out_min) / (in_max - in_min)


# Vertices for the cube. These are right-handed, counter-clockwise wound.
vertices = [
    [-1,  1,  1, 1],
    [-1, -1,  1, 1],
    [ 1, -1,  1, 1],
    [ 1,  1,  1, 1],
    [-1,  1, -1, 1],
    [-1, -1, -1, 1],
    [ 1, -1, -1, 1],
    [ 1,  1, -1, 1]
]

# Transpose vertices.
transposed_vertices = transpose(vertices)

counter = 0
spin = 0
zoom = 0
direction = 1

# This shit is done 60 times a second, rip
def TIC():
    global counter, spin, zoom, direction

    # x
    theta = math.radians(spin)
    # y
    phi = math.radians(spin/2)
    # z
    psi = math.radians(spin/3)

    # Combine X, Y and Z rotation matrics to one rotation matrix
    rotation_matrix = matrix_multiply(rotation_z(psi), rotation_y(phi))
    rotation_matrix = matrix_multiply(rotation_matrix, rotation_x(theta))

    # Combine the rotation and translation matrices to one transformation matrix
    translation_matrix = translation(0, 0, map_value(zoom))
    transformation_matrix = matrix_multiply(translation_matrix, rotation_matrix)

    # Do the transformation
    transformed_vertices = matrix_multiply(transformation_matrix, transposed_vertices)

    # Do the projection
    projection_matrix = perspective(math.radians(60), width/height, 0.1, 100.0)
    projected_vertices = matrix_multiply(projection_matrix, transformed_vertices)

    # Normalize by w
    element_wise_division_in_place(projected_vertices[0], projected_vertices[3])
    element_wise_division_in_place(projected_vertices[1], projected_vertices[3])
    element_wise_division_in_place(projected_vertices[2], projected_vertices[3])

    # Yes
    x = projected_vertices[0]
    y = projected_vertices[1]
    z = projected_vertices[2]

    # Six faces, average depth, color (might not be needed after flat shading has been added)
    faces = [
        # Front
        [(0, 1, 2, 3), (z[0] + z[1] + z[2] + z[3])/4, 0],

        # Back
        [(4, 5, 6, 7), (z[4] + z[5] + z[6] + z[7])/4, 1],

        # Top
        [(4, 0, 3, 7), (z[4] + z[0] + z[3] + z[7])/4, 2],

        # Bottom
        [(5, 1, 2, 6), (z[5] + z[1] + z[2] + z[6])/4, 3],

        # Left
        [(4, 5, 1, 0), (z[4] + z[5] + z[1] + z[0])/4, 4],

        # Right
        [(3, 2, 6, 7), (z[3] + z[2] + z[6] + z[7])/4, 5]
    ]

    # Sort faces
    faces.sort(key=lambda x: x[1], reverse=True)

    # Clear screen
    cls(0)

    # Hack to put the cube on a phase-shifted Lissajous curve with evenly-spaced X mapping
    t = (counter%240 / (240 - 1)) * (2 * math.pi)
    offset_x = int((120 * math.sin(t - (math.pi / 2)) + 120) - 120)
    offset_y = int(68 * math.sin(2 * (t - (math.pi / 2))))

    for face in faces:
        coords = []
        for vertex in face[0]:
            coords.append(to_pixel(x[vertex], y[vertex], width, height))
        tri(offset_x+coords[0][0], offset_y+coords[0][1], offset_x+coords[1][0], offset_y+coords[1][1], offset_x+coords[2][0], offset_y+coords[2][1], 1+face[2])
        tri(offset_x+coords[2][0], offset_y+coords[2][1], offset_x+coords[3][0], offset_y+coords[3][1], offset_x+coords[0][0], offset_y+coords[0][1], 1+face[2])

    counter += 1
    spin += 3

    zoom += direction
    if counter%240 == 0 or counter&240 == 239:
        direction = -direction

# <TILES>
# 001:eccccccccc888888caaaaaaaca888888cacccccccacc0ccccacc0ccccacc0ccc
# 002:ccccceee8888cceeaaaa0cee888a0ceeccca0ccc0cca0c0c0cca0c0c0cca0c0c
# 003:eccccccccc888888caaaaaaaca888888cacccccccacccccccacc0ccccacc0ccc
# 004:ccccceee8888cceeaaaa0cee888a0ceeccca0cccccca0c0c0cca0c0c0cca0c0c
# 017:cacccccccaaaaaaacaaacaaacaaaaccccaaaaaaac8888888cc000cccecccccec
# 018:ccca00ccaaaa0ccecaaa0ceeaaaa0ceeaaaa0cee8888ccee000cceeecccceeee
# 019:cacccccccaaaaaaacaaacaaacaaaaccccaaaaaaac8888888cc000cccecccccec
# 020:ccca00ccaaaa0ccecaaa0ceeaaaa0ceeaaaa0cee8888ccee000cceeecccceeee
# </TILES>

# <WAVES>
# 000:00000000ffffffff00000000ffffffff
# 001:0123456789abcdeffedcba9876543210
# 002:0123456789abcdef0123456789abcdef
# </WAVES>

# <SFX>
# 000:000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000304000000000
# </SFX>

# <TRACKS>
# 000:100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# </TRACKS>

# <PALETTE>
# 000:1a1c2c5d275db13e53ef7d57ffcd75a7f07038b76425717929366f3b5dc941a6f673eff7f4f4f494b0c2566c86333c57
# </PALETTE>

