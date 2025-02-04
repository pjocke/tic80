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

palette = []

counter = 0
cycle = 0

def BOOT():
    global palette

    for i in range(4, 13):
        color = []
        color.append(peek(0x03FC0 + (i * 3) + 0))
        color.append(peek(0x03FC0 + (i * 3) + 1))
        color.append(peek(0x03FC0 + (i * 3) + 2))
        palette.append(color)

# This shit is done 60 times a second, rip
def TIC():
    global counter, palette, cycle

    colors = palette[cycle%9:] + palette[:cycle%9]

    i = 4
    for color in colors:
        poke(0x03FC0 + (i * 3) + 0, color[0])
        poke(0x03FC0 + (i * 3) + 1, color[1])
        poke(0x03FC0 + (i * 3) + 2, color[2])
        i += 1

    # x
    theta = math.radians(counter%360)
    theta = math.radians(22.5)

    # y
    phi = math.radians((counter+128%360))

    # z
    psi = math.radians((counter+360%360)/3)
    psi = math.radians(-5)

    # Combine X, Y and Z rotation matrics to one rotation matrix
    rotation_matrix = matrix_multiply(rotation_z(psi), rotation_y(phi))
    rotation_matrix = matrix_multiply(rotation_matrix, rotation_x(theta))

    # Combine the rotation and translation matrices to one transformation matrix
    translation_matrix = translation(0, 0, -8.5)
    transformation_matrix = matrix_multiply(translation_matrix, rotation_matrix)

    # Do the transformation
    translated_vertices = matrix_multiply(translation_matrix, transposed_vertices)
    transformed_vertices = matrix_multiply(transformation_matrix, transposed_vertices)

    # Do the projection
    projection_matrix = perspective(math.radians(60), width/height, 0.1, 100.0)
    projected_vertices_straight = matrix_multiply(projection_matrix, translated_vertices)
    projected_vertices = matrix_multiply(projection_matrix, transformed_vertices)

    # Normalize by w
    element_wise_division_in_place(projected_vertices[0], projected_vertices[3])
    element_wise_division_in_place(projected_vertices[1], projected_vertices[3])
    element_wise_division_in_place(projected_vertices[2], projected_vertices[3])

    element_wise_division_in_place(projected_vertices_straight[0], projected_vertices_straight[3])
    element_wise_division_in_place(projected_vertices_straight[1], projected_vertices_straight[3])


    # Yes
    x = projected_vertices[0]
    y = projected_vertices[1]
    z = projected_vertices[2]

    x_straight = projected_vertices_straight[0]
    y_straight = projected_vertices_straight[1]

    square = []
    for vertex in range(0, 4):
        square.append(to_pixel(x_straight[vertex], y_straight[vertex], width, height))
    
    trace(f"Width: {square[1][1] - square[0][1]}")
    trace(f"Height: {square[2][0] - square[0][0]}")

    # Six faces, average depth, color (might not be needed after flat shading has been added)
    faces = [
        # Front
        [(0, 1, 2, 3), (z[0] + z[1] + z[2] + z[3])/4, ((32, 32), (32, 63), (63, 63), (63, 32)), 0],

        # Back
        [(4, 5, 6, 7), (z[4] + z[5] + z[6] + z[7])/4, ((127, 32), (127, 63), (96, 63), (96, 32)), 1],

        # Top
        [(4, 0, 3, 7), (z[4] + z[0] + z[3] + z[7])/4, ((32, 0), (32, 31), (63, 31), (63, 0)), 2],

        # Bottom
        [(5, 1, 2, 6), (z[5] + z[1] + z[2] + z[6])/4, ((32, 95), (32, 64), (63, 64), (63, 95)), 3],

        # Left
        [(4, 5, 1, 0), (z[4] + z[5] + z[1] + z[0])/4, ((0, 32), (0, 63), (31, 63), (31, 32)), 4],

        # Right
        [(3, 2, 6, 7), (z[3] + z[2] + z[6] + z[7])/4, ((64, 32), (64, 63), (95, 63), (95, 32)), 5]
    ]

    # Sort faces
    faces.sort(key=lambda x: x[1], reverse=True)

    # Clear screen
    cls(0)

    for face in faces:
        coords = []
        depth = []

        texture = face[2]
        for vertex in face[0]:
            coords.append(to_pixel(x[vertex], y[vertex], width, height))
            depth.append(z[vertex])

        ttri(coords[0][0], coords[0][1], coords[1][0], coords[1][1], coords[2][0], coords[2][1], texture[0][0], texture[0][1], texture[1][0], texture[1][1], texture[2][0], texture[2][1], z1=depth[0], z2=depth[1], z3=depth[2])
        ttri(coords[2][0], coords[2][1], coords[3][0], coords[3][1], coords[0][0], coords[0][1], texture[2][0], texture[2][1], texture[3][0], texture[3][1], texture[0][0], texture[0][1], z1=depth[2], z2=depth[3], z3=depth[0])

    counter += 1

    if counter%4 == 0:
        cycle += 1

# <TILES>
# 000:c748596a74858596c848596a84849596c849595a8c9495a6c8494a5a8c9495a6
# 001:7a7b8c9ca7b8b9ca6a7b8c94a7b8c9ca6b7b8c94a7b8c94a6b7c8c94b7b8c94a
# 002:a4b5c6474b5c5c64a4b5c6474b5c6c64a4b5c6474b5b6c74a5b5c6475a5b6c74
# 003:58696a7a758697a75859697b758696a748586a7a758596a74859696b748596a6
# 004:8c8c94a5b8c9494a7b8494a5b8c8495a7c8c9595b7c849597b848495b7c84859
# 005:b6b6c7c85b6b7c74a6b6b7c85a6b7c8ca6a7b7c85a6b7b8c96a7b8b86a6a7b8c
# 006:48595a6a849595a649495a5b8494a5a5c9494a5b9c94a4b5c9ca4a4b9caca4b4
# 007:6b7b7c84b6b7c7c86b6c7c84b6c6c7485c6c7c74b5c6c7475c6c6474c5c64647
# 008:849595a64859596a858596964858696985868697585868797586878757686878
# 009:a6b7b7c86a7b7b8ca7a7b8b87a7a8b8b97a7a8b9797a8a9b9798a8a979898a9a
# 010:c849495a8c9494a5c9c94a4a9c9ca4a4b9caca4b9bacacb4babacbcbababbcbc
# 011:5a6b6b6ca5b6b6c65b5b5c6cb5b5c5c64b4c5c5cb4c4c5c5cc4c4c54ccc4c445
# 012:7c7c8484c7c748486c747475c647475764646575464656575455656645555666
# 013:8595969658596969858686965868686976768687676778786677778766777788
# 014:a6a7a7b86a7a7a8b9797a8a879798a8a97989898798989998888899988889899
# 015:b8b8c9c98b8b9c9ca8b9b9ba8a9b9baba9a9aaaa9a9aaaaa999aaaaaa9a9a9ba
# 016:c9c94a5b8c94a5a6b94a4a5b9c94a5b6c9ca5b5b9ca4a5b6ba4a4b6b9ca4b5b6
# 017:6b7c8c94b7c8c94a6c7c8494b7c849496c748495b7c848596c748595c7c74859
# 018:a5b6c6c75a6b6c7ca5b6b6c75a6b6b7ca5b6b7c75a6b7b7ca5a6b7c85a6a7b8c
# 019:48595a6a848595a648595a6b849595a648495a5b8494a5a6c8494a5b8c94a5a5
# 020:7c7c8485b7c848596b7c8485b7c748586b7c7485b6c747586c6c7475b6c64758
# 021:96a7a8b8697a7b8b9697a8b9697a8a8b8697a8a969798a9a869798a96879899a
# 022:c9cacb4b9cacbcb4b9cacb4b9bacbcb4babacbcc9babbcccaababbccaaabbbcc
# 023:5c546465c54546564c545565c44555564c445556c4445565c44445564c445465
# 024:7576878757677878667677886667778866677778667677875667687865768687
# 025:889899a98889999a8889999a889899a989898a9a9898a8a979898a8b9798a8b8
# 026:aabbbbbcaabbbbcbaaabbcbcaabacbcb9babacbcb9bacacb9b9caca4b9c9ca4a
# 027:cccc4444cccc4444bcc4c445cb4c4c54b4b4c5c54b4b5c5cb4b5b5b64a5b5b6b
# 028:45555666545565664546565754646575464647576c647474c6c747486c7c7c84
# 029:6767787876768787676868697586869658585959858595954849595a849495a5
# 030:7879898a979798a869797a8a96a7a7a76a6a7a7ba6a6b6b65a6b6b6ba5b5b5b6
# 031:8a9a9b9ba8b8b9b98b8b8b8cb7b8c8c87b7c7c8cb7c7c7476c7c7474c6c64646
# 032:cacb5b5caca4b5c6ca4b4c5cacb4b5c6bb4b4c54abb4c5c5bbcc4c54bbbcc545
# 033:6c748595c7474859647485864647585864747586464758686465758646575768
# 034:96a6b7b8696a7b8c96a7a7b8697a7b8b9797a8b8697a8a8b8798a8a979798a9a
# 035:c9c94a5b9c94a4b5c9ca4a5b9c9ca4b5b9ca4b4b9baca4b4b9cacb4c9bacbcb4
# 036:6c646475b6c647575c646475c5c646575c546565c5c546564c545566c4454556
# 037:8687989968788999768788996778898976778899677878996677888967778888
# 038:aaabbbbc9ababbcb9aabacbca9aacacb9a9baca499b9ba4a9a9b9ca4a9a9c9ca
# 039:c4c545464c5c5464b4c5c6464b5c5c64b4b5c6c74b5b6c6ca4b5b6c74a5b6b7c
# 040:575768697575869647585869748585964748595974848595c848495a7c849494
# 041:797a8a8b97a7a7b86a7a7b7ba6a6b7b76a6b6b7ca5b6b6b75a5b6b6ca5b5b6c6
# 042:8c9c94a4c8c949498c849495c8c848597c848585c747485874747576c6475757
# 043:a5a5a6b65a5a6a6b9596a6a759696a7a869696a76869697a8686979768687979
# 044:b7b7c8c87b7b8c8ca7b8b8c97a8b8b9ba8a8b9b98a8a9a9b98a9a9aa89999aaa
# 045:c9494a5a9c94a4a4c9ca4a4b9cacacbcbababbcbababbbbcaabbbbbbaabbbbbb
# 046:5b5b5b5cb4b4b5c54b4b4c5cb4b4c4c4cb4c4c44bccccc4cbcbcc4c4cbcb4b4b
# 047:6c646465c545465654545555444555554445454544545454c5c5c6c65b5c6b6c
# 048:bbccc454bbccc445bcbcc445cbcc4c44acc4c445cb4c4c54b4b4c545cb4b5c54
# 049:5565767656566768556666775666677756666777556676774657677764657677
# 050:879898a97889899a879899a97889999a8888999a888899a97889899a879898a9
# 051:babacb4cababbcb4aabbcbccaabbbcccaabbbcccaabbcbccaaabbcb4aabacb4b
# 052:44445556c444555644454556c4445555c44545564c445465c4c546464c4c5464
# 053:6677788966778798676778796676879757686879657686975758696975758696
# 054:8a9b9c9498b9b9c98a8b9c94a8a8b9c97a8b8c94a7a8b8c97a7b8c84a7b7b8c8
# 055:a5a5b6b74a5a6b7b95a6a6b7495a6a7b9596a7a749596a7a959697a84959697a
# 056:c8c9494a7c8c9ca4b8c9caca8b8c9cacb8b9caca8b9b9caca8b9bacb8a9b9bac
# 057:4b5b5c6ca4b5c5c54b4c5c54a4b4c545cb4c4c54bcb4c444cbcc4c44bccccc44
# 058:6465757646465767546566764556566655556667555565664555565754546575
# 059:7687878867787888777778887777878767687879768686975868686975868696
# 060:98999a9a8899a9a989899a9b9898a8b9798a8a8b97a7a8b87a7a7b7ba6a7b7b7
# 061:abababacbababaca9b9b9cacb9b9c9c98b8c9c94b8c8c8488c8c8484c7c74748
# 062:acb4b4b5ca4a4a5ba4a4a5a549495a5a94959596495959698585868658586868
# 063:b5b6b6b75b6a6b7aa6a6a7a76a6a797a96979798697979898787888878788888
# 064:a4b5c5464a4b5c64a4b5c6c64a5b5c6ca5b5b6c75a5b6b6ca5a6b6b75a6b6b7c
# 065:46575768647576874747586874758586c748585974848595c84859597c849595
# 066:78798a9a8797a8a979798a8b9797a8b8697a7a8b96a7a7b8596a7b7b96a6b7b7
# 067:9babacb4b9baca4b9b9caca4b9c9ca4a8c9ca4a4c8c9ca4a8c9c94a5c8c9494a
# 068:b4c5c6474b5c5c64b5b5c6c75b5b6c6ca5b6b6c75a6b6b7ca5a6b7b75a6a7b7b
# 069:47585969748585964848595a74849595c848495a7c8494a5c8c9494a8c8c94a4
# 070:6a7b7c84a6b7c7c86a6b7c74a6b6c7c75b6b6c74a5b6c6475b5b6c64b5b5c646
# 071:8596979848596979858687984858687975768787475768786576768856576778
# 072:a9a9babb8a9aabab98aaaaab899aaaba99999bab8999a9b9888a9a9c8898a8b9
# 073:bcccc4c4bbcb4c4cbcbcb4c5bacb4b4baca4b4b5caca4b5b9caca5b5c9ca4a5a
# 074:454646475c646474c5c647475c6c7474b6c6c7c85b6c7c7cb6b7b7c86b6b7b8b
# 075:58586969858595954859595a849494a548494a4a8c9ca4a4c9c9ca4a8c9cacac
# 076:6a6b6b7ca6b6b6c65a5b6c6ca5b5c5c55b5b5c54b4b4c4454b4c4c44bcc4c444
# 077:7c747475c6474757646465654646565654555566455555554545554654545464
# 078:7576767757676777666667676666767656575758657575855747485864748484
# 079:777878897787879768687979868696966869696a859595a659595a5a9495a5a5
# 080:96a6b7b76a6a7b7b96a7a7b8697a7a8b9797a8b879798a8b8798a8a978898a9a
# 081:c84949598c849495c8c9494a8c9c94a4b9c9ca4a9b9caca4b9cacacb9bacacbc
# 082:5a6a6b7ca5a6b6c75a5b6b6ca5b5b6c74b5b5c6cb4b5c6c64b4c5c64b4c5c546
# 083:8c849495c8484959748485954748585974758586475758686475768646576768
# 084:a6a6a7b85a6a7a7b96a7a7a8696a7a8a9697a8a869797a8a879798a96879898a
# 085:b8c9ca4a8b9c9ca4b9b9caca8b9bacaca9babacb9a9babbca9aabbbb9a9aabbb
# 086:4b5c5c54b4c5c5454b4c4454b4c44445cb4c4444bcc44444cccc4445cccc4454
# 087:6566777756566777556667685566667655566768556576764556575854657585
# 088:79898b8b8798a8b8787a8a8b8797a8b869797a7b8697a7b769696a7b8696a6b6
# 089:9c94a4a6c949495a8c949595c8c859598c848586c74848587c747586c7c74758
# 090:a6a7b8b86a6a7a8b96a7a8a9697a7a8a969798a9697989898787989968788899
# 091:b9cacacb9b9babbbb9babbbb9a9aabbba9aaabac99aaaaba9a9a9b9c99a9b9b9
# 092:cbccc4c4bccc4c4cbcbcb4c5cbcb4b5baca4b4b5ca4a4a5aa4a4a5a5c9494959
# 093:c545c6465c5c6c6cc5b6c6b75b6b6b7bb6b6a7b76a6a7a7aa6a7a7a869797979
# 094:c74848497c7c8c9cc7c8c9c97b8b8c9cb8b8b9ba8a8b9b9ba8a9a9ba8a9a9aaa
# 095:494a5a5a94a4a4a4ca4a4a4bacacacb4cacacbcbababbcbcbabbbbccabbbbbcc
# 096:889899a98889999a898999aa989899aa79899a9a9798a9a9798a8a9b97a8a8b9
# 097:babacbcbababbcbcaabbbbcbaabbbbbcababbbbcbababbcb9babacbcb9bacacb
# 098:cb4c5454b4c44545cc4c4455ccc44455ccc44445cc4c4454b4c4c5454b4c5c54
# 099:6565767656566767556666775566667756566767656576764657576864757586
# 100:878898997878899977888999778888997878898a878798986879798a868797a7
# 101:a9aaabbc9aaaaabb9aaaabaca9a9baba9a9b9baca8b9b9ca8b8b9b9ca8b8b9c9
# 102:bcccc445cbcc4c5cbcb4c4c5cb4b4b5ca4b4b5b5ca4a5b5ba4a5a5a6494a5a6a
# 103:4646475864647485c6c747486c7c7484b6c7c8c86b7c7c8cb6b7c8c96b7b8c8c
# 104:595a6a6b8595a5b6495a5b5b9495a5b5494a5b5b94a4a4b5c94a4b4c9caca4b4
# 105:6c747576c6c747576c646566c6c646565c545566c5c545564c445556c4444555
# 106:778888896777889877787979667787976768696a667686965758596a65758595
# 107:8a8b8b9ca8a8b8c87a8b8c8ca7b7b7c77a7b7c7ca6b6c7c66b6b6c64a5b6b546
# 108:94949596c8485858848585864747576774757676465656676465666645556666
# 109:9697979868787989878788886778888877787879777787976768697976868697
# 110:9999aaaa8999a9aa899a9a9b9898a9b9898a8b9b98a8a8b87a7a8b8c97a7b7b8
# 111:abbbbcbcbabacbcbabacaca4b9caca4a9c9c94a4c9c9494a8c849494c8484949
# 112:7a7a8b8ba7a7b8b86a7b7b8cb6b7b7c86b6b7c8cb6c6c7c85c6c7c74c5c64747
# 113:9b9caca4c9c9ca4a9c9c94a4c949494a84949495484959598485959548585969
# 114:b4b5c5c64b5b5c6ca5b5b6c65a5b6b6ca5a6b6b75a6a6b7b96a6a7b7696a7a7b
# 115:4647585864748585c74748587c748485c7c848497c8c8494b8c8c9498b8c9c94
# 116:68697a7a869697a759696a6b9596a6a6595a5a6b95a5a5b64a4a5b5ba4a4b5b5
# 117:7b8b8c9cb7b8c8c87b7c8c84b7c7c7486c7c7474b6c747476c647475c6c64657
# 118:949596a64959596a849596964859696985859697585868797586868757676878
# 119:a7b7b8b97a7b8b9ba7a8a8b97a8a8a9a9798a9a97989999a8898999a888899a9
# 120:cacacbcc9bacbcbcbabbbbcc9babbbccaabbbcbcaaaabbcbaaabacaca9babaca
# 121:4c444546c4445454c4c4c5c6cc4c5c6cbcb5c5c6cb4b5b6ba4b4b6b64a4a5a6b
# 122:4758595a647484944748494a6c7c8494c7c8c9c97b7c8c9cb7b8b8ba7b8b8b9b
# 123:5b5b5c54a5b4c5c44a4c4c44acb4cc44cbcbc4c4acbbcc4cbabcbcb4abbbcb4b
# 124:55555657555565754545464744546474c5c646475c5c6c74b5c6c7c75b6b6c7c
# 125:57686969758696965858595a858595a54848495a848494a5c8c9494a8c9c94a4
# 126:6a7b7b7ca6a6b7c76a6b6c7ca5b6b6c75b5b6c64b5b5c6c65b5c5c54b4c5c545
# 127:74848495c7484859747485854747585864757576465757676565667646566667
# 128:5c646474c5464657545465654545565644555566545555664545565654646565
# 129:7585869657586869757686876767687866767787666777786667777866767787
# 130:9697a7a879797a8a979798a87989898a88989899888989998888999988889999
# 131:b8b9c9ca8b9b9caca9b9baca9a9babaca9aababa9aaaabab9aaaaabba9aaaabb
# 132:ca4b4b5caca4b4c5cacb4c4cacbcb4c4cbcbcc44bcbcccc4bbccccc4bbcbcc4c
# 133:5c546565c545465654545565454555564455555644545565454546464c546464
# 134:7576777756677777666667786666768756676768657676865757586875758585
# 135:8888899a888898a87889898a879797a879797a7a9696a7a7696a6a7b95a6a6a6
# 136:9b9b9cacb9b9b9c98b8b9c94b8b8c8c87b8c8c84b7c7c7487b7c7474b6c6c747
# 137:a4a5a5a749595a6a949596964959696985858687485868687576867757576777
# 138:a7a8a9a97a7a9a9a9798999a798989a98788898a788898987878798a778797a7
# 139:ababaca4aabaca4a9a9baca4a9b9c9498a9b9c94a8b8c8498b8b8c84a7b7c848
# 140:b5b6b7b85a6b7b7ba5a6a7b85a6a7a8b9596a7a859697a8a9596979858697989
# 141:c8c9ca4a8c9cacacb9b9cacb8b9babbca9bababb9a9aabbba9aaabbb99aaaabb
# 142:4b4c4c54b4c4c445cbcc4444bccc4444bcccc445bbcc4c54bcb4c4c5cbcb4c5c
# 143:5556666655556666455656675465657645465757546475754646475854647485
# 144:c64646576c647475c7c747477c7c7484b7c7c8487b8c8c84b8b8c8c98b8b9c9c
# 145:57676878757686875858686985858696485959699495959649495a5a9494a5a5
# 146:7889899a879898a879798a8a9797a7a86a7a7a7ba6a6a7b76a6b6b7ba5b6b6b7
# 147:9a9aababa9a9baba8b9b9bacb8b9b9c98b8c9c9cb8c8c8c97c8c8484c7c74848
# 148:bcbcb4c4cacb4b4baca4b4b5ca4a4a5b94a4a5a549495a5a949595a64859596a
# 149:c5c6c6475c5c6c74b5b6c7c75b6b6c7cb6b6b7c76b6b7b7ba6b7b7b86a7a7a8b
# 150:4747585974748595474848497c848494c8c8c9498c8c9c9cb8b9c9ca8b9b9cac
# 151:595a6a6b95a5a5b55a5a5b5ba4a4b4b54a4b4b4ca4b4b4c4cacbccccacbccccc
# 152:6c6c6465b6c646465c5c5455c5c545554c445455c4444454c44445454c4c5c5c
# 153:65766777566666766556675855657575465647586464748446c747486c7c7c8c
# 154:6869797a868696a668696a6a858595a658595a5b849595a549494a5b9494a4a4
# 155:7b7c7c84b7b7c7476b7c7474b6c6c6476b6c6465b5b546465b5c5465b4c5c556
# 156:8586879858687888757687885767788865767788566777876666777856667677
# 157:999aaaac99a9aaba899a9bab9899b9b9898a9b9c88a8a8c9798a8b8c9797b8b8
# 158:bcb4b5c5ca4b4b5ca4a4b5b6ca4a4b5b9ca4a5b6c94a5a5a9494a5a6c949596a
# 159:c64747486c6c7484c6c7c8486b7c7c84b7b7c8c96b7b7c8ca7b7b8c96a7b8b8c
# 160:a9b9b9c99a9b9baca9aababa9aaaababaaaaaabbbaaababb9babababb9babaca
# 161:c94a4a5baca4a4b4caca4b4bbcbcb4b4bbcbcb4cbbccccc4bcbccccccbcbcc4c
# 162:5b5b6c6cb5b5c6c64b5c5c64b4c5c5464c4c5454c4c445454444445544444455
# 163:7c747485c6474758646475754646575765656576565656665555666655556566
# 164:8585969658586969868686976768687876778787677777776777777876767787
# 165:a7a7a8a879798a8a979898a97889899a88889999888899997889898987989898
# 166:a9b9baba9a9bababa9a9aaab9a9aaaba999a9aab99a9a9b98a9a9b9ba8a8b8b8
# 167:bbbbccc4bbbbcbcbbbbcbcb4bacacb4bacaca4a4c9ca4a4a9c949495c9c94959
# 168:c4c4c5c64b4b5b6bb4b5b5b64a5a5a6aa5a5a6a65a5969699596969759696979
# 169:c6c7c7c86b7b7b8cb7b7b8b87a7b8b8ba7a8a8a97a8a8a9a979899a97989999a
# 170:c9ca4a4b9cacacb4b9cacacb9babacbcb9babbcb9aabbbbbaaaabbbc9aaabacb
# 171:4c4c5455b4c445454c444445ccc44454ccc4c545cc4c4c5cbcb4c5c5cb4b5c5c
# 172:566767686565768656565868546575854647575964647585c64748586c747485
# 173:797a7b8c86a7a7b8696a7b7c9696a7b7596a6b7c9596a6b7595a6b6c95a5a6b6
# 174:84959596c848596984858696c748586974758687c747586874757687c7475768
# 175:a7a8b8b97a7a8b9b97a8a9b9798a8a9b9798a9aa79899a9a889899aa788999aa
# 176:9b9cacacc9c9caca849c94944849494984858495585858597575858567676868
# 177:acbcb4c44a4b4b4ca4a4b4b54a5a5b5b95a5a5a5595a6a6a969696a66969697a
# 178:c4c545455c5c5454b5c5c6c65b6c6c6cb6b6b6c76b6b6b7ca6a7b7b77a7a7b7b
# 179:4556565764646575464647576c747475c7c747487c7c8484c8c8c8c88c8c8c9c
# 180:6767687875768686575868698585859648585959849495954949494a9c94a4a4
# 181:7979797a979797a769696a7a96a6a6a65a6a6a6ba5a5b5b55a5b5b5ba4b4b5c5
# 182:8a8b8b8ca7b7b8c87b7b7c8cb6b7c7c76b6c7c64b6c6c6465c6c5464c5c54545
# 183:8c848585c8484858747475764747575774656576465656665565665655556565
# 184:8686868768686878867677876767777766777778667676876767686875758686
# 185:88889999888899998889898a889898a878797a8a8797a7a769797a7b9696a7b7
# 186:9aababaca9a9baca9a9b9c9ca8b9b9c98b8b9c94b8b8c9c97b8c8c84b7c8c848
# 187:a4b4b5c64a4b5b6ca4a5b5b64a4a5b6b94a5a6a6495a5a6a959596a74959696a
# 188:c6c748496c7c8484b7c7c8497b7c8c94b7b7c8c97b7b8c9ca7b8b8b97a8b8b9b
# 189:595a5b6c95a5b5b64a4a5b5c94a4b5c5ca4b4b5caca4b4c5caca4c4cacacb4c4
# 190:64757677c647576764657677c646576754656677454656675455666745555666
# 191:888999aa7888999a7889999a778899a978888a9a778898a97779898b778798a8
# 192:6676768676777778676777778686878758686878959696975959696995a5a6a6
# 193:86879797787879797787889787888889787888899797989879797979a697a7a7
# 194:97a7a8b8798a8a8b9898a8a989899a9a88999999989999998a898a8aa8a8a8a8
# 195:b8b8b9c98b8b9b9ba9a9b9ba9a9a9bab9aaaaabaa9aaaaaa9a9bababa9b9b9b9
# 196:c9ca4a4aacacacbcbacacbcbababbbbcbabbbbbcbababbcbababacacbacacaca
# 197:4b4b4c4cbcb4c4c4cbcccc44cccccc4cbcb4c4c4cb4b4b4ba4b4b4b54a4a4a5a
# 198:54445445444444544445c5454c5c5c5cc5c5c6c65b5b6b6bb5b6b6b65a6a6a6a
# 199:5556565754646474464647476c6c7c74c6c7c7c86b7b7c8cb7b7b8c87a7b8b8b
# 200:57585869748585954848585984848494484849498c8c9c94c8c9c9ca8b9c9cac
# 201:696a6a7b95a6a6b65a5a5b6ba5a5b5b64a5b5b5ca4b5b5c54a4b4c5ca4b4c4c4
# 202:7c7c7484c7c7c7486c6c7475c6c647476c646465c54646565454656545455656
# 203:8586969758586969758686975768687976768787576778786677778866677788
# 204:a8a8a9b97a8a9a9b9899a9aa79899a9a889999aa888999aa88899a9a889899a9
# 205:bacbcb44abbcbcc4babbccccabbbccccabbbbcc4aabbcb4cabacbcb4babacb4c
# 206:44555666445565664545565744555575c445565744546565c54546574c546475
# 207:68787a8a768797a86769798a768697a85868797a858697a75868697b758696b7
# 208:5a5a5a6aa4a5b5b54b4b5b5bb4b4b4b5cb4c4b4cccccc4c4ccccc4444b4c4c44
# 209:6a6a6a7aa6b6a6b75b5b6b6bc5b5c6b64c5c5c6cc44545454444545444445455
# 210:7a7a8a8bb7a7b8b86b7b7b7bb6c7b7c76c6c6c7c464646465454646455555556
# 211:8b9b9b9cb8b8b8c98c8c8c8cc7c748487c747474474747576464656556565656
# 212:9c9c9494c9494949848494954848595874858585575857587575757667666766
# 213:a4a4a5a549595959959595965858686986868686676768777677777767777677
# 214:a6a6a6a76969697a969697976878797987878788787888887778788887878797
# 215:a7a8b8b87a8a8a8a98a8a8a98989999a98999999889999a989898a9a9898a8a8
# 216:b9b9caca9b9babaca9bababb9aaaabbbaaaaababa9aababa9a9b9bacb9b9b9ca
# 217:cbcb4c44bcbccc44bbccccc4bbcbcc4cbcbcb4c4cbcb4b4cacb4b4b5ca4b4b5b
# 218:44555566445455564545455654545465c54546465c546464c5c646475c6c6474
# 219:6667787866767787676768786576868757586869757586964758596974858596
# 220:88898a9b8898a8a979898a8b9798a8b8797a8a8b97a7a8b86a7a7b8ba6a7b7b8
# 221:9baca4b4b9cacb4b9c9ca4b5b9ca4a4b8c9ca4a5c9c94a5a8c9494a5c849495a
# 222:c5c646475c5c6474b5c6c7475b6c6c74b6b6c7c85b6c6c7ca6b6c7c86b6b7c8c
# 223:58596a7b8585a6b7485a6a6b8495a6a6495a5a6b9495a6b6494a5b6b9495a5b6
# 224:b4b4c4c54b5b5c5ca5b5b5c55a5b6b6ba5a6b6b66a6a6a6a96a6a7a76979797a
# 225:454545455c5c5464c5c6c6c66b6c6c6cb6b6c7c77b7b7c7ca7b7b7b77a8b8b8b
# 226:45555555646555654646464674647464c7c7c7477c8c7c8cb8b8c8c88b8b9b8b
# 227:55556566656565664656565674747575474747477c848474c8c8c8c89c8c8c9c
# 228:666666666566757656575757757475854747484884848484c8c8c8c98c9c9c9c
# 229:676767687676768657585858858585854848495984949495c9c9494a9c9ca4a4
# 230:68687979869697975969696a959696a659595a5a95a5a5a54a4a4a5ba4a4b4b5
# 231:797a8a8ba7a7a7b86a7a7b7ba6b6b7b76b6b6b7cb6b6c6c75b6c6c6cb5c5c6c6
# 232:8b8b9c9cb8c8c9c98c8c8c94c8c848497c748484c74748586474757546475757
# 233:a4a4a5b54a4a5a5b9495a5a649595a6a859596a65859696a8586969758686979
# 234:b6c6c7c76b6c7c7cb6b7b7c86b7b7b7ca7a7b7b87a7a7b8b97a7a8b8797a8a8b
# 235:4848595a84849595c849495a8c9494a5c9c94a4a8c9ca4a4b9caca4b9b9cacb4
# 236:6a6b7b7ca6b6b7c75b6b6b7ca5b6b6c75b6b6c6cb5b6c6c64b5c6c64b4c5c646
# 237:8c849595c848595a748485954748595974758596475858696475868747576879
# 238:a6b7b8c86a7b8b8ca6a7b8b86a7a8b8c97a8a8b9797a8b9b9798a9b9797a8a9b
# 239:c94a5b5c94a4a5b5c94a4b5c9ca4b4b5c9ca4b5c9ca4b4b5baca4b4cacacb4c5
# 240:979797987879898987889898888888997888898987979898797979799697a7a7
# 241:a8a8a8a88a8a8a9a999999a999999999898a9a9a98a8a8a88a8a8b8ba7a7b7b8
# 242:b8b9b9b99a9a9aaba9a9aaaaa9aaaaaa9a9aaa9aa9b9b9b98b9b8b9bb8b8b8c8
# 243:b9b9b9b99b9b9b9baaaaaaaaaaaaaaaa9b9b9babb9b9b9b98b8c9c8cc8c8c8c8
# 244:b9b9b9b9ab9b9babaaaaaabaaaaaaaaa9b9bababb9b9b9ba9c9c9c9cc8c8c9c9
# 245:bacacacaabacacacbabbbbbbbbbbbbbbababacbcbabacacb9cacaca4c9c9ca4a
# 246:cb4b4b4bbcb4b4c4cbcccc4cbcccccccbcbcc4c4cbcb4b4ca4b4b4b44a4a4b4b
# 247:5c5c5c54c4c5c5454c44445444444445c4c445454c5c5454c5c5c5465c5c6c64
# 248:6465657546565657555565665555566655565666556565664656575764657575
# 249:7686878767687878767777876777777867777878767787876768787976868797
# 250:9798a8a979898a9a889899a98889999a8889999a889899a979898a9a9798a8a9
# 251:b9bacbcb9babacb4aababbccaaabbcbcaaabbbccaabbbbcc9babbcbcbabacbcb
# 252:4c4c5464c4c445464c444454c4444445c4444455cc444455c4c445464c4c5464
# 253:6575768756576878656677875667677856667778656677775667777865667787
# 254:9798a9aa79898a9b889899aa88899a9a888999aa88999aaa79899aaa889999aa
# 255:bacbcb4cabacb4c4babbcc4cabbcbcc4abbbcc44abbbccc4abbcccc4babbcc44
# </TILES>

# <PALETTE>
# 000:000000aaaaaa555555ffffff880088ff44aaee0000ff6600ffee0000dd000088000000aa6622000066ff00ccccffaa88
# </PALETTE>
