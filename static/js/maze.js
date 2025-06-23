// static/js/maze.js

// Import all necessary configuration from our settings file.
import { MAZE_DIMENSIONS, VISUAL_SETTINGS } from './settings.js';

// --- DOM Element Selection ---
const canvas = document.getElementById('mazeCanvas');
const ctx = canvas.getContext('2d');
const statsDisplay = document.getElementById('stats-display');

// --- Application State ---
let gridWidth, gridHeight;
let isGenerating = false;

// --- Core Functions ---
function setupCanvas(width, height) {
    gridWidth = width;
    gridHeight = height;
    canvas.width = width * VISUAL_SETTINGS.cellSize;
    canvas.height = height * VISUAL_SETTINGS.cellSize;
    ctx.fillStyle = VISUAL_SETTINGS.colors.background;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
}

function drawCell(r, c, color) {
    ctx.fillStyle = color;
    ctx.fillRect(c * VISUAL_SETTINGS.cellSize, r * VISUAL_SETTINGS.cellSize, VISUAL_SETTINGS.cellSize, VISUAL_SETTINGS.cellSize);
}

// --- WebSocket Communication ---
const socket = io();

socket.on('maze_update', function(update) {
    const [r, c] = update.cell;
    const type = update.type;
    
    let color = VISUAL_SETTINGS.colors.path;
    // if (type === 'current') color = VISUAL_SETTINGS.colors.current;
    if (type === 'frontier') color = VISUAL_SETTINGS.colors.frontier;
    
    drawCell(r, c, color);
});

// MODIFIED: This listener now also draws the start and end points.
socket.on('generation_complete', function(data) {
    console.log(`Server finished: ${data.algo} in ${data.time}`);
    statsDisplay.innerText = `Algorithm: ${data.algo} | Time: ${data.time}`;
    isGenerating = false;

    // Draw start and end cells after generation is complete
    const startCell = [1, 1];
    const endCell = [gridHeight - 2, gridWidth - 2];
    drawCell(startCell[0], startCell[1], VISUAL_SETTINGS.colors.start);
    drawCell(endCell[0], endCell[1], VISUAL_SETTINGS.colors.end);
});

socket.on('connect_error', (err) => {
    console.error("Connection to server failed:", err);
    statsDisplay.innerText = "Error: Could not connect to the server.";
    isGenerating = false;
});

// --- UI Interaction ---
function generateMaze(algorithm) {
    if (isGenerating) {
        console.warn("Generation is already in progress.");
        return;
    }
    isGenerating = true;

    const width = Math.floor(canvas.parentElement.clientWidth / VISUAL_SETTINGS.cellSize) | 1;
    const height = Math.floor(450 / VISUAL_SETTINGS.cellSize) | 1;
    
    setupCanvas(width, height);
    statsDisplay.innerText = `Algorithm: ${algorithm.toUpperCase()} | Generating...`;

    socket.emit('generate_maze', {
        algorithm: algorithm,
        width: width,
        height: height
    });
}

// Event listeners for algorithm buttons
document.getElementById('dfs-btn').addEventListener('click', () => generateMaze('dfs'));
document.getElementById('prims-btn').addEventListener('click', () => generateMaze('prims'));
document.getElementById('kruskals-btn').addEventListener('click', () => generateMaze('kruskals'));
document.getElementById('ellers-btn').addEventListener('click', () => generateMaze('ellers'));
document.getElementById('aldous-broder-btn').addEventListener('click', () => generateMaze('aldous_broder'));

// NEW: Event listener for the download button
document.getElementById('download-btn').addEventListener('click', () => {
    // This creates a temporary link element to trigger the download.
    const link = document.createElement('a');
    // We name the file with the current date and time for uniqueness.
    const filename = `maze_${new Date().toISOString().slice(0, 19).replace(/[:T]/g, '-')}.png`;
    link.download = filename;
    // toDataURL converts the canvas content into a base64-encoded PNG image.
    link.href = canvas.toDataURL('image/png').replace('image/png', 'image/octet-stream');
    link.click();
});

// --- Initial State ---
setupCanvas(MAZE_DIMENSIONS.defaultWidth, MAZE_DIMENSIONS.defaultHeight);
