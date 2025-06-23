import numpy as np
import random

class DSU:
    def __init__(self, n): self.parent = list(range(n))
    def find(self, i):
        if self.parent[i] == i: return i
        self.parent[i] = self.find(self.parent[i])
        return self.parent[i]
    def union(self, i, j):
        root_i, root_j = self.find(i), self.find(j)
        if root_i != root_j:
            self.parent[root_i] = root_j
            return True
        return False

def generate(grid):
    height, width = grid.shape
    # Create a list of all interior walls
    walls = []
    for r in range(1, height, 2):
        for c in range(1, width, 2):
            if r > 1: walls.append(((r, c), (r - 2, c)))
            if c > 1: walls.append(((r, c), (r, c - 2)))
    random.shuffle(walls)

    dsu = DSU(height * width)
    cell_to_dsu_idx = lambda r, c: r * width + c

    # Start with a grid of unconnected paths
    for r in range(1, height, 2):
        for c in range(1, width, 2):
            grid[r, c] = 1
            yield {'cell': (r, c), 'type': 'path'}
    
    for cell1, cell2 in walls:
        idx1 = cell_to_dsu_idx(*cell1)
        idx2 = cell_to_dsu_idx(*cell2)
        if dsu.union(idx1, idx2):
            wall_cell = ((cell1[0] + cell2[0]) // 2, (cell1[1] + cell2[1]) // 2)
            grid[wall_cell] = 1
            yield {'cell': wall_cell, 'type': 'path'}
