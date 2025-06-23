import numpy as np
import random

def get_frontier_cells(grid, cell):
    i, j = cell
    height, width = grid.shape
    frontiers = []
    if i > 1 and grid[i - 2, j] == 0: frontiers.append((i - 2, j))
    if i < height - 2 and grid[i + 2, j] == 0: frontiers.append((i + 2, j))
    if j > 1 and grid[i, j - 2] == 0: frontiers.append((i, j - 2))
    if j < width - 2 and grid[i, j + 2] == 0: frontiers.append((i, j + 2))
    return frontiers

def get_passage_neighbors(grid, cell):
    i, j = cell
    height, width = grid.shape
    neighbors = []
    if i > 1 and grid[i - 2, j] == 1: neighbors.append((i - 2, j))
    if i < height - 2 and grid[i + 2, j] == 1: neighbors.append((i + 2, j))
    if j > 1 and grid[i, j - 2] == 1: neighbors.append((i, j - 2))
    if j < width - 2 and grid[i, j + 2] == 1: neighbors.append((i, j + 2))
    return neighbors

def generate(grid):
    height, width = grid.shape
    start_cell = (random.randrange(1, height, 2), random.randrange(1, width, 2))
    grid[start_cell] = 1
    yield {'cell': start_cell, 'type': 'path', 'algo': 'prims'}
    
    frontiers = get_frontier_cells(grid, start_cell)
    
    while frontiers:
        frontier_cell = random.choice(frontiers)
        yield {'cell': frontier_cell, 'type': 'frontier'}

        passage_neighbors = get_passage_neighbors(grid, frontier_cell)
        
        if passage_neighbors:
            neighbor = random.choice(passage_neighbors)
            wall_cell = ((frontier_cell[0] + neighbor[0]) // 2, (frontier_cell[1] + neighbor[1]) // 2)
            
            grid[wall_cell] = 1
            grid[frontier_cell] = 1
            
            yield {'cell': wall_cell, 'type': 'path'}
            yield {'cell': frontier_cell, 'type': 'path'}
            
            # Add new frontiers of the newly carved cell
            for f in get_frontier_cells(grid, frontier_cell):
                if f not in frontiers:
                    frontiers.append(f)

        frontiers.remove(frontier_cell)
