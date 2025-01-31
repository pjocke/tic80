# script:  python

import math

# This sucks
def fmod(a, b):
    return a - int(a / b) * b

# Ported from the good old mode 13 toolkit
def hsv_to_rgb(h, s, v):
    v2 = v/100.0
    c = v2*(s/100.0)
    x = c*(1.0-math.fabs(fmod(h/60.0, 2)-1.0))
    m = v2-c

    r, g, b = 0.0, 0.0, 0.0

    if h >= 0 and h < 60:
        r = c
        g = x
        b = 0
    elif h >= 60 and h < 120:
        r = x
        g = c
        b = 0
    elif h >= 120 and h < 180:
        r = 0
        g = c
        b = x
    elif h >= 180 and h < 240:
        r = 0
        g = x
        b = c
    elif h >= 240 and h < 300:
        r = x
        g = 0
        b = c
    else:
        r = c
        g = 0
        b = x
    
    r = (r+m)*255.0
    g = (g+m)*255.0
    b = (b+m)*255.0
    
    return(int(r), int(g), int(b))

colors = []

def BOOT():
    global colors

    # Catch the rainbow
    for i in range(0, 360, 10): #30
        colors.append(hsv_to_rgb(i, 100.0, 100.0))

counter = 0

def TIC():
    global colors, counter

    cls(0)

    # Create the palette, 12 colors on indices 4 -- 15, sliding through the ROYGBIV
    start = counter%36
    for hue in range(start, start+12):
        r, g, b = colors[hue%36]

        color = hue - start + 4

        poke(0x3FC0+(color*3)+0, r)
        poke(0x3FC0+(color*3)+1, g)
        poke(0x3FC0+(color*3)+2, b)

    # Plot swatches
    for i in range(0, 13):
        rect(i*20, 58, 20, 20, i+4)

    counter += 1

    #exit()

# <TILES>
# 000:0123456789abcdef000000000000000000000000000000000000000000000000
# 001:c000000c000000000000000000000000000000000000000000000000c000000c
# 255:c000000c000000000000000000000000000000000000000000000000c000000c
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

