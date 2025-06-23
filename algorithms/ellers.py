import numpy as np
import random

def generate(grid):
    height, width = grid.shape
    sets = {}
    next_set_id = 0

    for r in range(1, height - 1, 2):
        # Initialize sets for the current row
        for c in range(1, width - 1, 2):
            if (r, c) not in sets:
                sets[(r, c)] = next_set_id
                next_set_id += 1
            grid[r, c] = 1
            yield {'cell': (r, c), 'type': 'path'}

        # Randomly join adjacent sets
        for c in range(1, width - 2, 2):
            if sets[(r, c)] != sets[(r, c + 2)] and random.choice([True, False]):
                wall_cell = (r, c + 1)
                grid[wall_cell] = 1
                yield {'cell': wall_cell, 'type': 'path'}
                old_set_id = sets[(r, c + 2)]
                new_set_id = sets[(r, c)]
                for cell in sets:
                    if sets[cell] == old_set_id:
                        sets[cell] = new_set_id
        
        # Create vertical connections
        row_sets = {sets[(r, c)] for c in range(1, width - 1, 2)}
        for s_id in row_sets:
            cells_in_set = [ (r,c) for c in range(1, width - 1, 2) if sets[(r,c)] == s_id]
            connections = random.randint(1, len(cells_in_set))
            for _ in range(connections):
                cell = random.choice(cells_in_set)
                wall_cell = (cell[0] + 1, cell[1])
                next_cell = (cell[0] + 2, cell[1])
                if next_cell[0] < height -1:
                    grid[wall_cell] = 1
                    grid[next_cell] = 1
                    sets[next_cell] = s_id
                    yield {'cell': wall_cell, 'type': 'path'}
                    yield {'cell': next_cell, 'type': 'path'}

    # Final row: connect all adjacent cells in different sets
    r = height - 2
    for c in range(1, width - 2, 2):
        if (r, c) not in sets:
            grid[r,c] = 1
            yield {'cell':(r,c), 'type':'path'}
            sets[(r,c)] = next_set_id
            next_set_id += 1
        if (r, c+2) not in sets:
            grid[r,c+2] = 1
            yield {'cell':(r,c+2), 'type':'path'}
            sets[(r,c+2)] = next_set_id
            next_set_id += 1

        if sets[(r,c)] != sets[(r,c+2)]:
            wall_cell = (r, c+1)
            grid[wall_cell] = 1
            yield {'cell': wall_cell, 'type': 'path'}
            old_set_id = sets[(r, c + 2)]
            new_set_id = sets[(r, c)]
            for cell in sets:
                if sets[cell] == old_set_id: sets[cell] = new_set_id
