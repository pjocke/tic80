# script:  python

import math

counter = 0

def TIC():
    global counter

    cls(0)

    a = math.radians(counter%360)

    x = int(120 + 50 * math.sin(a))
    y = int(68 + 50 * math.cos(a))

    print(f"Radians: {a:.2f}", 10, 10)
    print(f"Degrees: {counter%360}", 7, 17)

    line(0, 68, 240, 68, 13)
    line(120, 0, 120, 136, 13)
    circb(120, 68, 50, 12)

    line(120, 68, x, y, 2)
    circ(x, y, 5, 2)

    circ(218, y, 5, 3)
    print("sin", 226, y-2, 3)

    circ(x, 130, 5, 9)
    print("cos", x+8, 128, 9)

    counter += 1

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
