// static/js/settings.js

// This file centralizes all configuration for the maze application.
// By exporting these values, other JavaScript files (like maze.js) can import and use them.

// --- Core Maze Parameters ---
export const MAZE_DIMENSIONS = {
    defaultWidth: 41,  // Must be odd for most algorithms to function correctly.
    defaultHeight: 23, // Must be odd.
};

// --- Visual and Style Configuration ---
export const VISUAL_SETTINGS = {
    cellSize: 20, // The size in pixels of each square cell.

    // A centralized color palette. Changing a color here will update it everywhere.
    colors: {
        wall: '#FFFFFF',       // Walls are now white.
        path: '#888888',       // Paths are now grey.
        border: '#A0522D',     // Saddle Brown for the maze border.
        current: '#39FF14',    // Bright green for the "active" cell
        frontier: '#00BFFF',   // Blue for the "frontier" cells
        // NEW COLORS FOR START AND END MARKERS
        start: '#00FF7F',      // Spring Green
        end: '#FF4500',        // Orange Red
    }
};

