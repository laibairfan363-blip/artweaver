# Art Weaver

A collaborative platform for Writers and Artists, powered by Custom Data Structures and Algorithms.

## Features
- **Writers**: Write stories, Undo changes (Stack), and see them sorted (BST).
- **Artists**: See a Priority Queue of stories to visualize.
- **Network**: Connect with others (Graph).

## Project Structure
- `app.py`: Main Flask application.
- `dsa_modules/`: Custom implementations of Stack, Queue, BST, Graph, Heap, Sorting.
- `templates/`: HTML Templates.
- `static/`: CSS and JS files.

## Setup & Run
1. Ensure Python 3.x is installed.
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Run the application:
   ```sh
   python app.py
   ```
4. Open browser at `http://localhost:3000`.

## DSA Usage
- **Queue**: `dsa_modules/queue.py` - Used for Artist Dashboard.
- **Stack**: `dsa_modules/stack.py` - Used for Writer Undo.
- **BST**: `dsa_modules/bst.py` - Used for Story Feed sorting.
- **Graph**: `dsa_modules/graph.py` - Used for User Connections.
