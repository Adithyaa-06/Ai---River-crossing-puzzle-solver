# River Crossing Puzzle Solver (BFS / State Space Search)

An AI course project that solves two classic river crossing puzzles by searching the
state space with **Breadth-First Search (BFS)** and **Depth-First Search (DFS)**.
Both algorithms are written from scratch, with no search libraries.

- **Farmer, Wolf, Goat, Cabbage**
- **Missionaries and Cannibals** (3 missionaries, 3 cannibals, boat for 2 by default)

The project includes a command-line demo, a web app with an animated river scene,
a state space graph picture, and automated tests.

## Requirements

- Python 3 (tested with Python 3.11.9)
- The packages in `requirements.txt`: flask, networkx, matplotlib, pytest

## Install

```bash
pip install -r requirements.txt
```

## Run

| What | Command | Result |
|---|---|---|
| Command-line demo | `python solver.py` | Prints both solutions and a BFS vs DFS table |
| Web app | `python app.py` | Open http://127.0.0.1:5000 in a browser |
| State space graph | `python visualize.py` | Saves `state_space.png` |
| Tests | `pytest` | Runs the tests in `test_solver.py` |

### Using the web app

1. Pick a puzzle and an algorithm (BFS or DFS), then press **Solve**.
2. Step through the solution with **Previous** / **Next**, or press **Auto-play**
   and set the speed with the slider. **Reset** goes back to the start.
3. Click any line in the move log to jump to that step.
4. The stats card shows the result of the search you ran; the table below it
   compares BFS and DFS on the same puzzle.

### Web API

| Method | URL | Body / query | Returns |
|---|---|---|---|
| GET | `/` | none | the web page (`static/index.html`) |
| GET | `/api/puzzles` | none | `{"puzzles": ["farmer", "missionaries"]}` |
| POST | `/api/solve` | `{"puzzle": "farmer", "algorithm": "bfs"}` | path and stats |
| GET | `/api/compare` | `?puzzle=farmer` | BFS and DFS stats |

Bad input returns a JSON error such as `{"error": "Unknown puzzle 'x'. ..."}` with status 400.
If a puzzle has no solution, `/api/solve` returns an error with status 404.

## Folder structure

```
Ai project/
├── solver.py          # Problem class, BFS, DFS, compare, both puzzles, CLI demo
├── app.py             # Flask web server and JSON API
├── visualize.py       # Draws the farmer puzzle state space graph
├── test_solver.py     # pytest tests
├── requirements.txt   # Python packages
├── state_space.png    # Output of visualize.py
├── README.md          # This file
├── report.md          # Project report
└── static/
    ├── index.html     # Web page layout
    ├── style.css      # Light theme and boat animation
    └── script.js      # Fetches solutions and animates them
```
