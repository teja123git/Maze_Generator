# app.py

# --- Imports ---
# We must import 'request' from Flask to access the unique session ID of each client.
from flask import Flask, render_template, request
from flask_socketio import SocketIO
import numpy as np
import importlib
import time

# --- App Initialization ---
app = Flask(__name__)
# A secret key is required by Flask-SocketIO for session management.
app.config['SECRET_KEY'] = 'qwerdhjkijuytfdcvghjkimnbvcxdfgu8765'
socketio = SocketIO(app)

# --- Algorithm Loading ---
# This dictionary dynamically loads all algorithm functions from the 'algorithms' directory.
# This makes the application easily extensible with new algorithms.
ALGORITHMS = {
    'dfs': importlib.import_module('algorithms.dfs').generate,
    'prims': importlib.import_module('algorithms.prims').generate,
    'kruskals': importlib.import_module('algorithms.kruskals').generate,
    'ellers': importlib.import_module('algorithms.ellers').generate,
    'aldous_broder': importlib.import_module('algorithms.aldous_broder').generate
}

# --- Routes ---
@app.route('/')
def index():
    """Serves the main HTML page that contains the client-side application."""
    return render_template('index.html')

# --- WebSocket Event Handlers ---
@socketio.on('generate_maze')
def handle_maze_generation(data):
    """
    Listens for the 'generate_maze' event from a specific client and streams
    updates back ONLY to that same client using their unique session ID.
    """
    # CRITICAL: Get the unique Session ID (SID) for the client who sent this message.
    # Every connected user has a different SID.
    client_sid = request.sid
    # This print statement is helpful for debugging on the server.
    print(f"Generating maze for client with SID: {client_sid}")

    # Ensure width and height are odd for maze generation logic
    width = int(data.get('width', 41))
    if width % 2 == 0: width += 1
    height = int(data.get('height', 41))
    if height % 2 == 0: height += 1

    algorithm_name = data.get('algorithm', 'dfs')
    generator_func = ALGORITHMS.get(algorithm_name)

    if not generator_func:
        # Error messages should also only be sent to the originating client.
        socketio.emit('error', {'message': f"Algorithm '{algorithm_name}' not found."}, to=client_sid)
        return
        
    # Create a new grid for this specific request.
    grid = np.zeros((height, width), dtype=np.int8)

    start_time = time.time()
    
    # Run the generator and stream updates.
    for update in generator_func(grid):
        # THE KEY CHANGE: Add `to=client_sid` to the emit call.
        # This sends the update ONLY to the client who initiated this request,
        # not to everyone connected to the server.
        socketio.emit('maze_update', update, to=client_sid)
        socketio.sleep(0.001)  # Control animation speed.
    
    end_time = time.time()
    generation_time = (end_time - start_time) * 1000 # in milliseconds
    
    # The final completion message is also sent only to the specific client.
    socketio.emit('generation_complete', {
        'time': f'{generation_time:.2f} ms',
        'algo': algorithm_name.upper(),
    }, to=client_sid)


if __name__ == '__main__':
    # This block runs when you execute "python app.py"
    # The server is started using socketio.run for proper WebSocket support.
    socketio.run(app, debug=True)
