import random
import matplotlib.pyplot as plt

def diamond_square(size, roughness, min_value=0, max_value=11):
    grid_size = 2**size + 1
    terrain = [[0] * grid_size for _ in range(grid_size)]
    
    # Seed the corners
    terrain[0][0] = random.randint(min_value, max_value)
    terrain[0][-1] = random.randint(min_value, max_value)
    terrain[-1][0] = random.randint(min_value, max_value)
    terrain[-1][-1] = random.randint(min_value, max_value)
    
    def diamond_step(x, y, step_size, offset):
        """Diamond step: Set center of square to average of corners + random offset."""
        avg = (terrain[x - step_size][y - step_size] +
               terrain[x - step_size][y + step_size] +
               terrain[x + step_size][y - step_size] +
               terrain[x + step_size][y + step_size]) // 4
        terrain[x][y] = max(min(avg + offset, max_value), min_value)
    
    def square_step(x, y, step_size, offset):
        """Square step: Set midpoints of edges to average of adjacent corners + random offset."""
        neighbors = []
        if x - step_size >= 0:
            neighbors.append(terrain[x - step_size][y])
        if x + step_size < grid_size:
            neighbors.append(terrain[x + step_size][y])
        if y - step_size >= 0:
            neighbors.append(terrain[x][y - step_size])
        if y + step_size < grid_size:
            neighbors.append(terrain[x][y + step_size])
        
        avg = sum(neighbors) // len(neighbors)
        terrain[x][y] = max(min(avg + offset, max_value), min_value)
    
    step_size = (grid_size - 1) // 2
    scale = roughness
    
    while step_size > 0:
        # Diamond Step
        for x in range(step_size, grid_size - 1, step_size * 2):
            for y in range(step_size, grid_size - 1, step_size * 2):
                offset = random.randint(-scale, scale)
                diamond_step(x, y, step_size, offset)
        
        # Square Step
        for x in range(0, grid_size, step_size):
            for y in range((x + step_size) % (step_size * 2), grid_size, step_size * 2):
                offset = random.randint(-scale, scale)
                square_step(x, y, step_size, offset)
        
        step_size //= 2
        scale //= 2
    
    return terrain

# Example usage
terrain = diamond_square(size=7, roughness=7)
plt.imshow(terrain, cmap='terrain')
plt.colorbar()
plt.show()

tile = 0
for y in range(0, 128, 8):
    for x in range(0, 128, 8):
        pixels = ""
        for iny in range(y, y+8):
            for inx in range(x, x+8):
                pixels = pixels + str(hex(terrain[iny][inx] + 4)[2:])

        print(f"# {str(tile).zfill(3)}:{pixels}")
    
        tile += 1
