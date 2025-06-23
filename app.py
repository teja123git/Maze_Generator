# app.py
from flask import Flask, render_template
from flask_socketio import SocketIO
import numpy as np
import importlib # The library used to import modules by name
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_super_secret_and_unguessable_key!'
socketio = SocketIO(app)

# This dictionary is where the error is happening.
# It tries to find each .py file inside the 'algorithms' folder.
# This requires the folder structure and filenames to be perfect.
ALGORITHMS = {
    'dfs': importlib.import_module('algorithms.dfs').generate,
    'prims': importlib.import_module('algorithms.prims').generate,
    'kruskals': importlib.import_module('algorithms.kruskals').generate,
    'ellers': importlib.import_module('algorithms.ellers').generate,
    'aldous_broder': importlib.import_module('algorithms.aldous_broder').generate
}

@app.route('/')
def index():
    """Serves the main HTML page from the templates folder."""
    return render_template('index.html')

@socketio.on('generate_maze')
def handle_maze_generation(data):
    """
    Listens for the 'generate_maze' event from the frontend and runs the
    corresponding algorithm, streaming updates back to the client.
    """
    width = int(data.get('width', 41))
    if width % 2 == 0: width += 1
    height = int(data.get('height', 41))
    if height % 2 == 0: height += 1

    algorithm_name = data.get('algorithm', 'dfs')
    generator_func = ALGORITHMS.get(algorithm_name)

    if not generator_func:
        socketio.emit('error', {'message': f"Algorithm '{algorithm_name}' not found on the server."})
        return
        
    grid = np.zeros((height, width), dtype=np.int8)

    start_time = time.time()
    
    # Run the chosen generator and emit each step.
    for update in generator_func(grid):
        socketio.emit('maze_update', update)
        socketio.sleep(0.001)
    
    end_time = time.time()
    generation_time = (end_time - start_time) * 1000 # in milliseconds
    
    socketio.emit('generation_complete', {
        'time': f'{generation_time:.2f} ms',
        'algo': algorithm_name.upper()
    })

if __name__ == '__main__':
    # When you run "python app.py", this is the code that executes.
    socketio.run(app, debug=True)
