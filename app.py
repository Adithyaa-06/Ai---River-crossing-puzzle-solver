"""
Flask web app for the River Crossing Puzzle Solver.

Routes:
  GET  /                         -> the web page (static/index.html)
  GET  /api/puzzles              -> list of puzzle names
  POST /api/solve                -> solve a puzzle with BFS or DFS
  GET  /api/compare?puzzle=...   -> BFS vs DFS statistics

Run with:  python app.py   then open http://127.0.0.1:5000
"""

from flask import Flask, jsonify, request, send_from_directory

from solver import PUZZLES, bfs, dfs, compare

app = Flask(__name__, static_folder="static")

ALGORITHMS = {"bfs": bfs, "dfs": dfs}


def error(message, status=400):
    """Return a JSON error response."""
    return jsonify({"error": message}), status


def stats_only(result):
    """Copy a search result without the (long) path, for the comparison table."""
    if result is None:
        return None
    return {key: value for key, value in result.items() if key != "path"}


@app.route("/")
def index():
    """Serve the main web page."""
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/puzzles")
def list_puzzles():
    """Return the names of the available puzzles."""
    return jsonify({"puzzles": list(PUZZLES.keys())})


@app.route("/api/solve", methods=["POST"])
def solve():
    """
    Solve a puzzle.

    Expects JSON: {"puzzle": "farmer" | "missionaries", "algorithm": "bfs" | "dfs"}
    Returns the search result (path + stats) as JSON.
    """
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return error("Request body must be JSON, e.g. {\"puzzle\": \"farmer\", \"algorithm\": \"bfs\"}")

    puzzle = data.get("puzzle")
    algorithm = data.get("algorithm", "bfs")

    if puzzle not in PUZZLES:
        return error(f"Unknown puzzle '{puzzle}'. Choose one of: {', '.join(PUZZLES)}")
    if algorithm not in ALGORITHMS:
        return error(f"Unknown algorithm '{algorithm}'. Choose 'bfs' or 'dfs'")

    problem = PUZZLES[puzzle]()
    result = ALGORITHMS[algorithm](problem)
    if result is None:
        return error("No solution exists for this puzzle", 404)

    result["puzzle"] = puzzle
    result["algorithm"] = algorithm
    return jsonify(result)


@app.route("/api/compare")
def compare_puzzle():
    """Return BFS and DFS statistics for one puzzle, e.g. /api/compare?puzzle=farmer"""
    puzzle = request.args.get("puzzle")
    if puzzle not in PUZZLES:
        return error(f"Unknown puzzle '{puzzle}'. Choose one of: {', '.join(PUZZLES)}")

    results = compare(PUZZLES[puzzle]())
    return jsonify({
        "puzzle": puzzle,
        "bfs": stats_only(results["bfs"]),
        "dfs": stats_only(results["dfs"]),
    })


if __name__ == "__main__":
    app.run(debug=True)
