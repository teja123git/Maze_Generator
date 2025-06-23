# algorithms/aldous_broder.py

import numpy as np
import random

def generate(grid):
    height, width = grid.shape
    # Start at a random cell (must be a path cell, so odd coordinates)
    current_cell = (random.randrange(1, height, 2), random.randrange(1, width, 2))
    grid[current_cell] = 1
    yield {'cell': current_cell, 'type': 'path'}

    # Calculate the total number of cells to visit
    total_cells = ((height - 1) // 2) * ((width - 1) // 2)
    visited_count = 1

    while visited_count < total_cells:
        yield {'cell': current_cell, 'type': 'current'} # Highlight the walker's current position
        r, c = current_cell
        
        # Find potential neighbors to walk to (N, S, E, W)
        potential_neighbors = []
        if r > 1: potential_neighbors.append((r - 2, c))
        if r < height - 2: potential_neighbors.append((r + 2, c))
        if c > 1: potential_neighbors.append((r, c - 2))
        if c < width - 2: potential_neighbors.append((r, c + 2))
        
        # Choose a random neighbor and move there
        next_cell = random.choice(potential_neighbors)
        
        # If the neighbor hasn't been visited, carve a path to it
        if grid[next_cell] == 0:
            wall_cell = ((current_cell[0] + next_cell[0]) // 2, (current_cell[1] + next_cell[1]) // 2)
            grid[wall_cell] = 1
            grid[next_cell] = 1
            visited_count += 1
            yield {'cell': wall_cell, 'type': 'path'}
            yield {'cell': next_cell, 'type': 'path'}
        
        # The walker moves regardless of whether a path was carved
        current_cell = next_cell
