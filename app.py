# app.py
from flask import Flask, render_template, request
from flask_socketio import SocketIO
import numpy as np
import importlib
import time
import threading

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a_very_secret_and_unguessable_key_for_production!'
socketio = SocketIO(app)

# --- State Management Dictionaries ---
# These dictionaries store the state for each connected client, keyed by their session ID.
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


# --- NEW: Handler for client disconnection ---
@socketio.on('disconnect')
def handle_disconnect():
    """
    Cleans up state when a client disconnects. This is crucial for preventing memory leaks.
    This event is automatically triggered by Flask-SocketIO when a user closes their tab or browser.
    """
    client_sid = request.sid
    # Safely remove the client's data from our state dictionaries.
    # The .pop() method removes a key and returns its value, or None if the key doesn't exist.
    client_speeds.pop(client_sid, None)
    
    pause_event = pause_events.pop(client_sid, None)
    if pause_event:
        # If a generation thread was paused for this client, we must unblock it
        # so that it can terminate gracefully instead of becoming a zombie thread.
        pause_event.set()

    print(f"Client {client_sid} disconnected. Cleaned up their state.")


@socketio.on('pause_resume')
def handle_pause_resume(data):
    client_sid = request.sid
    is_paused = data.get('isPaused', False)
    
    if client_sid in pause_events:
        if is_paused:
            pause_events[client_sid].clear()  # clear() blocks the thread's .wait() call.
        else:
            pause_events[client_sid].set()    # set() unblocks the thread's .wait() call.

@socketio.on('set_speed')
def handle_set_speed(data):
    client_sid = request.sid
    client_speeds[client_sid] = int(data.get('speed', 75))

@socketio.on('generate_maze')
def handle_maze_generation(data):
    client_sid = request.sid
    print(f"Generating maze for client with SID: {client_sid}")

    # Create and store a threading Event for this specific generation task.
    # We start it in the "set" (running) state.
    pause_events[client_sid] = threading.Event()
    pause_events[client_sid].set()
    
    client_speeds.setdefault(client_sid, 75)

    width = int(data.get('width', 41)) | 1
    height = int(data.get('height', 41)) | 1
    algorithm_name = data.get('algorithm', 'dfs')
    generator_func = ALGORITHMS.get(algorithm_name)
    grid = np.zeros((height, width), dtype=np.int8)

    start_time = time.time()
    
    for update in generator_func(grid):
        # Check if the client is still connected before proceeding.
        # This handles cases where a client disconnects mid-generation.
        if client_sid not in pause_events:
            print(f"Client {client_sid} disconnected mid-generation. Terminating thread.")
            break

        # Before each step, wait on the event. It will only block if the event is "cleared" (paused).
        pause_events[client_sid].wait()

        speed = client_speeds.get(client_sid, 75)
        sleep_duration = (101 - speed) * 0.001 

        socketio.emit('maze_update', update, to=client_sid)
        socketio.sleep(sleep_duration)
    
    end_time = time.time()
    
    # Only send completion message if the client is still connected.
    if client_sid in pause_events:
        generation_time = (end_time - start_time) * 1000
        socketio.emit('generation_complete', {
            'time': f'{generation_time:.2f} ms',
            'algo': algorithm_name.upper(),
        }, to=client_sid)
        # Clean up the pause event for this finished task.
        pause_events.pop(client_sid, None)

if __name__ == '__main__':
    socketio.run(app, debug=True)
