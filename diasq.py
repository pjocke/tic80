# script:  python

import math
import random

# https://en.wikipedia.org/wiki/Diamond-square_algorithm
#
#  The diamond-square algorithm starts with a two-dimensional grid, then
# randomly generates terrain height from four seed values arranged in a grid
# of points so that the entire plane is covered in squares.
#

side, matrix = 0, [[]]

##
## TODO:
## Add randomness
## 
def diamondsquare(size):
    half = int(size/2)
    trace(f"size = {size}, half = {half}")

    # The diamond step: For each square in the array, set the midpoint of that
    # square to be the average of the four corner points plus a random value.
    for y in range(0, side-1, size):
        for x in range(0, side-1, size):
            x1, y1, x2, y2 = x, y, x+size, y+size

            value = int(math.fabs((matrix[y1][x1] + matrix[y2][x1] + matrix[y2][x2] + matrix[y1][x2])/4))
            matrix[half][half] = value

            trace(f"{x1}, {y1} -- {x2}, {y2}")
            trace(value)

def BOOT():
    global side, matrix

    # Begin with a two-dimensional square array of width and height 2n + 1. 
    n = 7
    side = int(math.pow(2, n) + 1)
    matrix = [[0 for _ in range(side)] for _ in range(side)]

    # Initialise the random number generator
    random.seed(tstamp())

    # The four corner points of the array must be set to initial values.
    matrix[0][0] = random.randint(4, 15)
    matrix[128][0] = random.randint(4, 15)
    matrix[128][128] = random.randint(4, 15)
    matrix[0][128] = random.randint(4, 15)

    trace(f"{matrix[0][0]}, {matrix[128][0]}, {matrix[128][128]}, {matrix[0][128]}")

    # Calculate the landscape
    diamondsquare(128)


def TIC():
    global side, matrix

    cls(0)

    for y in range(0, len(matrix)):
        for x in range(0, len(matrix[y])):
            pix(x, y, matrix[y][x])

# <TILES>
# </TILES>

# <WAVES>
# </WAVES>

# <SFX>
# </SFX>

# <TRACKS>
# </TRACKS>

# <PALETTE>
# 000:1a1c2c5d275db13e53ef7d57ffcd75a7f07038b76425717929366f3b5dc941a6f673eff7f4f4f494b0c2566c86333c57
# </PALETTE>

