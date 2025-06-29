# Maze Generator

This is a full-stack web application designed to demonstrate and visualize five classical maze generation algorithms. A Python backend computes the mazes, and a JavaScript frontend renders the generation process in real-time using WebSockets.

## Live Demo

The project is deployed on Render and can be viewed here:

[https://maze-generator-ywll.onrender.com/](https://maze-generator-ywll.onrender.com/)

## How It Works

The application operates on a client-server model designed for real-time interaction:

1.  **User Request:** The user selects an algorithm from the frontend interface.
2.  **Session-Specific Backend Processing:** A WebSocket message is sent to the Python Flask server. The server identifies the client by its unique Session ID (SID).
3.  **Step-by-Step Generation:** The Python algorithms are implemented as generators. Instead of creating the whole maze at once, they `yield` each small change (e.g., carving a single path).
4.  **Targeted Real-Time Streaming:** For each step yielded by the algorithm, the server sends a WebSocket message back *only* to the specific client's SID, ensuring sessions are independent.
5.  **Frontend Visualization:** The JavaScript on the client side listens for these messages and draws each step on the HTML5 Canvas as it arrives, creating a live animation of the generation process.

## The Algorithms Explained

Each algorithm creates a "perfect maze" (a maze with no loops and exactly one path between any two cells) but approaches the problem with a different strategy, resulting in mazes with distinct visual characteristics.

### Depth-First Search (DFS)

This algorithm behaves like a single person exploring a cave. It picks a random direction and goes as deep as possible until it hits a dead end. It then backtracks to the previous junction and tries a different unexplored path. This process creates mazes with long, winding corridors and very few dead ends.
DFS uses a stack (either explicitly or via system recursion) to manage the path. The time complexity is linear, O(N) where N is the number of cells, as each cell is visited exactly once.

### Prim's Algorithm

Prim's algorithm grows the maze like a crystal. It starts with a single cell and maintains a list of "frontier" cells (walls that are adjacent to the existing maze). At each step, it randomly picks a frontier cell, carves a path to it from the main maze, and adds that cell's new frontier walls to the list. This results in a maze with many short branches.
This is a graph-based algorithm that grows a Minimum Spanning Tree. This implementation uses a simple list for the frontier set. With a more optimized data structure like a priority queue, the time complexity would be O(N log N).

### Kruskal's Algorithm

This algorithm thinks of the maze as a grid of disconnected rooms. It creates a list of all the walls between the rooms and then shuffles that list randomly. One by one, it removes a wall from the list, but only if the two rooms that wall separates are not already connected. This process continues until all rooms are connected.
To efficiently check if two cells are already connected, this algorithm uses a Disjoint Set Union (DSU) or "Union-Find" data structure. Its time complexity is dominated by sorting the list of walls, making it O(E log E), where E is the number of walls.

### Eller's Algorithm

Eller's is a unique algorithm that generates the maze one row at a time, making it very memory-efficient. For each row, it randomly decides whether to connect adjacent cells within that row. Then, for each group of connected cells, it creates at least one random vertical connection down to the next row.
It processes the maze row-by-row, managing cell connectivity through sets. This approach makes it one of the fastest algorithms with an O(N) time complexity and allows for the generation of infinitely large mazes as the full grid does not need to be stored in memory.

### Aldous-Broder Algorithm

This algorithm performs a "random walk." It starts at a random cell and moves to a random neighbor. If the neighbor has not been visited before, it carves a path between the current cell and the new one. The process continues until every cell in the grid has been visited.
As a "uniform spanning tree" algorithm, it produces a completely random and unbiased maze. However, the random walk can be very inefficient as it may revisit cells many times before finding an unvisited one. Its expected time complexity is significantly higher than other methods.

## Features

*   Real-time visualization of five different maze generation algorithms.
*   Independent user sessions managed by unique WebSocket Session IDs.
*   Clear start (green) and end (red) markers on the completed maze.
*   A "Download Maze" feature to save the final maze as a PNG image.
*   A clean, responsive user interface.

## Technology Stack

*   **Backend:** Python, Flask, Flask-SocketIO, NumPy
*   **Frontend:** HTML5, CSS3, JavaScript (ES Modules), Socket.IO Client
*   **DevOps:** Docker for containerization, Gunicorn for the production server, and Render for cloud deployment.
*   **Testing:** Pytest for backend unit testing.

## Local Installation

To run this project on your local machine, follow these steps.

### Using Docker (Recommended)

1.  **Prerequisites:** Docker must be installed and running.
2.  **Clone the repository:**
    ```bash
    git clone https://github.com/YourUsername/Your-Repo-Name.git
    cd Your-Repo-Name
    ```
3.  **Build and run the container:**
    ```bash
    docker build -t maze-generator .
    docker run -p 5000:5000 maze-generator
    ```
4.  Open your browser and navigate to `http://localhost:5000`.

### Using a Python Environment

1.  **Prerequisites:** Python 3.9+ must be installed.
2.  **Clone the repository and navigate into it.**
3.  **Create and activate a virtual environment:**
    ```bash
    # For Windows
    python -m venv .venv
    .\.venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv .venv
    source .venv/bin/activate
    ```
4.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
5.  **Run the application:**
    ```bash
    python app.py
    ```
6.  Open your browser and navigate to `http://localhost:5000`.
