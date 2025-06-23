import { MAZE_DIMENSIONS, VISUAL_SETTINGS } from './settings.js';

// --- DOM Element Selection ---
const canvas = document.getElementById('mazeCanvas');
const ctx = canvas.getContext('2d');
const statsDisplay = document.getElementById('stats-display');
const pauseBtn = document.getElementById('pause-btn');
const speedSlider = document.getElementById('speed-slider');

// --- Application State ---
let gridWidth, gridHeight;
let isGenerating = false;
let isPaused = false;

// --- Core Functions ---
function setupCanvas(width, height) {
    gridWidth = width;
    gridHeight = height;
    canvas.width = width * VISUAL_SETTINGS.cellSize;
    canvas.height = height * VISUAL_SETTINGS.cellSize;
    ctx.fillStyle = VISUAL_SETTINGS.colors.wall;
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
    if (type === 'frontier') color = VISUAL_SETTINGS.colors.frontier;
    
    drawCell(r, c, color);
});

socket.on('generation_complete', function(data) {
    statsDisplay.innerText = `Algorithm: ${data.algo} | Time: ${data.time}`;
    isGenerating = false;
    isPaused = false;
    pauseBtn.innerText = 'Pause';
    pauseBtn.disabled = true;

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
    if (isGenerating) return;
    isGenerating = true;
    isPaused = false; // Reset pause state
    pauseBtn.innerText = 'Pause';
    pauseBtn.disabled = false;

    // Set the initial speed value on the server when starting a new maze
    socket.emit('set_speed', { speed: speedSlider.value });

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

pauseBtn.addEventListener('click', () => {
    if (!isGenerating) return;
    isPaused = !isPaused;
    pauseBtn.innerText = isPaused ? 'Resume' : 'Pause';
    // CORRECTED LOGIC: 'isPaused' on the frontend now means "the user wants it paused"
    // The backend's Event.clear() (which blocks) corresponds to isPaused=true
    socket.emit('pause_resume', { isPaused: isPaused });
});

speedSlider.addEventListener('input', () => {
    socket.emit('set_speed', { speed: speedSlider.value });
});

// Event listeners for algorithm buttons
document.getElementById('dfs-btn').addEventListener('click', () => generateMaze('dfs'));
document.getElementById('prims-btn').addEventListener('click', () => generateMaze('prims'));
document.getElementById('kruskals-btn').addEventListener('click', () => generateMaze('kruskals'));
document.getElementById('ellers-btn').addEventListener('click', () => generateMaze('ellers'));
document.getElementById('aldous-broder-btn').addEventListener('click', () => generateMaze('aldous_broder'));

document.getElementById('download-btn').addEventListener('click', () => {
    const link = document.createElement('a');
    const filename = `maze_${new Date().toISOString().slice(0, 19).replace(/[:T]/g, '-')}.png`;
    link.download = filename;
    link.href = canvas.toDataURL('image/png').replace('image/png', 'image/octet-stream');
    link.click();
});

// --- Initial State ---
setupCanvas(MAZE_DIMENSIONS.defaultWidth, MAZE_DIMENSIONS.defaultHeight);
