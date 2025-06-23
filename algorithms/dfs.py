import numpy as np
import random

def get_unvisited_neighbors(grid, cell):
    i, j = cell
    height, width = grid.shape
    neighbors = []
    if i > 1 and grid[i - 2, j] == 0: neighbors.append((i - 2, j))
    if i < height - 2 and grid[i + 2, j] == 0: neighbors.append((i + 2, j))
    if j > 1 and grid[i, j - 2] == 0: neighbors.append((i, j - 2))
    if j < width - 2 and grid[i, j + 2] == 0: neighbors.append((i, j + 2))
    return neighbors

def generate(grid):
    height, width = grid.shape
    start_cell = (random.randrange(1, height, 2), random.randrange(1, width, 2))
    stack = [start_cell]
    grid[start_cell] = 1
    yield {'cell': start_cell, 'type': 'path', 'algo': 'dfs'}

    while stack:
        current_cell = stack[-1]
        yield {'cell': current_cell, 'type': 'current'}
        
        neighbors = get_unvisited_neighbors(grid, current_cell)
        
        if neighbors:
            next_cell = random.choice(neighbors)
            wall_cell = ((current_cell[0] + next_cell[0]) // 2, (current_cell[1] + next_cell[1]) // 2)
            
            grid[wall_cell] = 1
            grid[next_cell] = 1
            
            yield {'cell': wall_cell, 'type': 'path'}
            yield {'cell': next_cell, 'type': 'path'}
            
            stack.append(next_cell)
        else:
            stack.pop()
