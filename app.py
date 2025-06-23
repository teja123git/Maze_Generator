# app.py
from flask import Flask, render_template, request
from flask_socketio import SocketIO
import numpy as np
import importlib
import time
import threading # Import the threading module

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a_very_secret_and_unguessable_key_for_production!'
socketio = SocketIO(app)

# --- State Management Dictionaries ---
# These will store the state for each connected client, keyed by their session ID.
# This is crucial for a multi-user environment.
client_speeds = {}
pause_events = {}

ALGORITHMS = {
    'dfs': importlib.import_module('algorithms.dfs').generate,
    'prims': importlib.import_module('algorithms.prims').generate,
    'kruskals': importlib.import_module('algorithms.kruskals').generate,
    'ellers': importlib.import_module('algorithms.ellers').generate,
    'aldous_broder': importlib.import_module('algorithms.aldous_broder').generate
}

@app.route('/')
def index():
    return render_template('index.html')

# --- NEW: Event Handlers for Pause and Speed ---
@socketio.on('pause_resume')
def handle_pause_resume(data):
    """Handles pause/resume requests from a client."""
    client_sid = request.sid
    is_paused = data.get('isPaused', False)
    
    if client_sid in pause_events:
        if is_paused:
            pause_events[client_sid].clear() # clear() means RESUME
        else:
            pause_events[client_sid].set() # set() means PAUSE

@socketio.on('set_speed')
def handle_set_speed(data):
    """Handles speed change requests from a client."""
    client_sid = request.sid
    # We store the speed value for this specific client.
    # The frontend will send a value from 1 (slow) to 100 (fast).
    client_speeds[client_sid] = int(data.get('speed', 50))

# --- NEW: Handler for client disconnection ---
@socketio.on('disconnect')
def handle_disconnect():
    """Cleans up state when a client disconnects to prevent memory leaks."""
    client_sid = request.sid
    if client_sid in client_speeds:
        del client_speeds[client_sid]
    if client_sid in pause_events:
        # Ensure any paused threads are resumed so they can terminate gracefully.
        pause_events[client_sid].clear()
        del pause_events[client_sid]
    print(f"Client {client_sid} disconnected. Cleaned up state.")


# --- MODIFIED: The main generation handler ---
@socketio.on('generate_maze')
def handle_maze_generation(data):
    client_sid = request.sid
    print(f"Generating maze for client with SID: {client_sid}")

    # Create a new threading Event for this specific generation task.
    pause_events[client_sid] = threading.Event()
    # Set a default speed for the client.
    client_speeds.setdefault(client_sid, 50)

    # ... (width, height, algorithm selection logic remains the same)
    width = int(data.get('width', 41)) | 1
    height = int(data.get('height', 41)) | 1
    algorithm_name = data.get('algorithm', 'dfs')
    generator_func = ALGORITHMS.get(algorithm_name)
    grid = np.zeros((height, width), dtype=np.int8)

    start_time = time.time()
    
    for update in generator_func(grid):
        # --- PAUSE LOGIC ---
        # Before each step, check if the pause event is set.
        # .wait() will block this thread until the event is cleared, without blocking the main server.
        pause_events[client_sid].wait()

        # --- SPEED LOGIC ---
        # Calculate sleep duration based on client's speed setting.
        # We invert the speed value: higher speed = shorter sleep time.
        speed = client_speeds.get(client_sid, 50)
        # Map speed (1-100) to sleep duration (e.g., 0.1s - 0.0s)
        sleep_duration = (101 - speed) * 0.001 

        socketio.emit('maze_update', update, to=client_sid)
        socketio.sleep(sleep_duration)
    
    end_time = time.time()
    generation_time = (end_time - start_time) * 1000
    
    socketio.emit('generation_complete', {
        'time': f'{generation_time:.2f} ms',
        'algo': algorithm_name.upper(),
    }, to=client_sid)
    
    # Clean up the pause event for this finished task
    if client_sid in pause_events:
        del pause_events[client_sid]

if __name__ == '__main__':
    socketio.run(app, debug=True)
