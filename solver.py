"""
River Crossing Puzzle Solver using BFS / State Space Search.

This file contains:
  * Problem              - a base class describing a search problem
  * bfs(problem)         - Breadth-First Search (finds the shortest solution)
  * dfs(problem)         - Depth-First Search (iterative, finds *a* solution)
  * compare(problem)     - runs BFS and DFS and returns both results
  * FarmerWolfGoatCabbage and MissionariesCannibals - two river crossing puzzles

All search algorithms are written from scratch (no search libraries).
"""

import time
from collections import deque


# ---------------------------------------------------------------------------
# Base problem class
# ---------------------------------------------------------------------------

class Problem:
    """
    Base class for a state space search problem.

    A subclass must set `initial_state` and implement the methods below.
    States must be hashable (we use tuples) so they can be stored in
    sets and dictionaries.
    """

    initial_state = None

    def is_goal(self, state):
        """Return True if `state` is a goal state."""
        raise NotImplementedError

    def is_valid(self, state):
        """Return True if `state` breaks none of the puzzle's rules."""
        raise NotImplementedError

    def successors(self, state):
        """
        Return a list of (next_state, move_text) pairs reachable from `state`
        in one move. Only valid states are returned.
        """
        raise NotImplementedError

    def to_display(self, state):
        """Return {"left": [...], "right": [...]} describing who is on each bank."""
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Helper used by both searches
# ---------------------------------------------------------------------------

def build_result(problem, states_and_moves, nodes_expanded, nodes_generated, start_time):
    """
    Turn a list of (state, move_text) pairs into the result dictionary
    returned by bfs() and dfs().
    """
    path = []
    for state, move in states_and_moves:
        display = problem.to_display(state)
        path.append({
            "state": state,
            "move": move,
            "left": display["left"],
            "right": display["right"],
        })

    return {
        "path": path,
        "nodes_expanded": nodes_expanded,
        "nodes_generated": nodes_generated,
        "path_length": len(path) - 1,          # number of crossings (moves)
        "time_ms": (time.perf_counter() - start_time) * 1000,
    }


# ---------------------------------------------------------------------------
# Breadth-First Search
# ---------------------------------------------------------------------------

def bfs(problem):
    """
    Breadth-First Search.

    Uses a FIFO queue (collections.deque), so states are explored level by
    level. Because every move costs 1, the first time we reach the goal we
    have found a SHORTEST solution.

    The `parent` dictionary maps each discovered state to
    (previous_state, move_text). It is also used as the visited set:
    if a state is already a key in `parent`, we have seen it before.

    Counters:
      nodes_expanded  - states taken out of the queue and whose successors were produced
      nodes_generated - states created (the start state + every successor produced)

    Returns the result dict, or None if no solution exists.
    """
    start_time = time.perf_counter()
    start = problem.initial_state

    queue = deque([start])
    parent = {start: (None, "Start")}   # also acts as the visited set
    nodes_expanded = 0
    nodes_generated = 1

    while queue:
        state = queue.popleft()

        if problem.is_goal(state):
            # Walk back through parent links to rebuild the path.
            steps = []
            current = state
            while current is not None:
                previous, move = parent[current]
                steps.append((current, move))
                current = previous
            steps.reverse()
            return build_result(problem, steps, nodes_expanded, nodes_generated, start_time)

        nodes_expanded += 1
        for next_state, move in problem.successors(state):
            nodes_generated += 1
            if next_state not in parent:          # not visited yet
                parent[next_state] = (state, move)
                queue.append(next_state)

    return None


# ---------------------------------------------------------------------------
# Depth-First Search
# ---------------------------------------------------------------------------

def dfs(problem):
    """
    Depth-First Search (iterative, using an explicit stack).

    Uses a LIFO stack (a Python list), so it goes as deep as possible
    before backtracking. DFS finds A solution, but not necessarily the
    shortest one.

    Each stack entry is (state, steps) where `steps` is the list of
    (state, move_text) pairs taken to reach that state.
    The `visited` set stops us from exploring the same state twice.

    Returns the result dict, or None if no solution exists.
    """
    start_time = time.perf_counter()
    start = problem.initial_state

    stack = [(start, [(start, "Start")])]
    visited = set()
    nodes_expanded = 0
    nodes_generated = 1

    while stack:
        state, steps = stack.pop()

        if state in visited:
            continue
        visited.add(state)

        if problem.is_goal(state):
            return build_result(problem, steps, nodes_expanded, nodes_generated, start_time)

        nodes_expanded += 1
        for next_state, move in problem.successors(state):
            nodes_generated += 1
            if next_state not in visited:
                stack.append((next_state, steps + [(next_state, move)]))

    return None


# ---------------------------------------------------------------------------
# Comparison
# ---------------------------------------------------------------------------

def compare(problem):
    """Run BFS and DFS on the same problem and return both results side by side."""
    return {"bfs": bfs(problem), "dfs": dfs(problem)}


# ---------------------------------------------------------------------------
# Puzzle 1: Farmer, Wolf, Goat, Cabbage
# ---------------------------------------------------------------------------

class FarmerWolfGoatCabbage(Problem):
    """
    Farmer, Wolf, Goat and Cabbage puzzle.

    State: (F, W, G, C) where each value is 0 (left bank) or 1 (right bank).
    Start: everyone on the left  -> (0, 0, 0, 0)
    Goal:  everyone on the right -> (1, 1, 1, 1)

    Rules:
      * The boat holds the farmer plus at most one item.
      * The wolf may not be left alone with the goat.
      * The goat may not be left alone with the cabbage.
    """

    NAMES = ["Farmer", "Wolf", "Goat", "Cabbage"]

    def __init__(self):
        self.initial_state = (0, 0, 0, 0)

    def is_goal(self, state):
        """Goal: everyone is on the right bank."""
        return state == (1, 1, 1, 1)

    def is_valid(self, state):
        """A state is invalid if something gets eaten while the farmer is away."""
        farmer, wolf, goat, cabbage = state
        if wolf == goat and farmer != goat:
            return False          # wolf eats goat
        if goat == cabbage and farmer != goat:
            return False          # goat eats cabbage
        return True

    def successors(self, state):
        """The farmer crosses alone, or with one item that is on his bank."""
        farmer = state[0]
        new_side = 1 - farmer
        direction = "right" if new_side == 1 else "left"
        result = []

        # Option 1: farmer crosses alone.
        next_state = (new_side,) + state[1:]
        if self.is_valid(next_state):
            result.append((next_state, f"Farmer crosses {direction} alone"))

        # Options 2-4: farmer takes the wolf, goat or cabbage (index 1, 2, 3).
        for item in range(1, 4):
            if state[item] == farmer:                 # item is on the farmer's bank
                new_state = list(state)
                new_state[0] = new_side
                new_state[item] = new_side
                next_state = tuple(new_state)
                if self.is_valid(next_state):
                    move = f"Farmer takes {self.NAMES[item]} {direction}"
                    result.append((next_state, move))

        return result

    def to_display(self, state):
        """List the names on each bank."""
        left = [name for name, side in zip(self.NAMES, state) if side == 0]
        right = [name for name, side in zip(self.NAMES, state) if side == 1]
        return {"left": left, "right": right}


# ---------------------------------------------------------------------------
# Puzzle 2: Missionaries and Cannibals
# ---------------------------------------------------------------------------

class MissionariesCannibals(Problem):
    """
    Missionaries and Cannibals puzzle.

    State: (M_left, C_left, boat_side)
      M_left    - missionaries on the left bank
      C_left    - cannibals on the left bank
      boat_side - 0 if the boat is on the left, 1 if on the right

    Start: (missionaries, cannibals, 0)  -> everyone on the left
    Goal:  (0, 0, 1)                     -> everyone on the right

    Rules:
      * The boat carries 1 to `boat_capacity` people.
      * On either bank, if there are missionaries there, the cannibals
        must not outnumber them.
    """

    def __init__(self, missionaries=3, cannibals=3, boat_capacity=2):
        self.missionaries = missionaries
        self.cannibals = cannibals
        self.boat_capacity = boat_capacity
        self.initial_state = (missionaries, cannibals, 0)

    def is_goal(self, state):
        """Goal: nobody left on the left bank and the boat on the right."""
        return state == (0, 0, 1)

    def is_valid(self, state):
        """Check the counts are in range and no missionaries are outnumbered."""
        m_left, c_left, boat = state
        m_right = self.missionaries - m_left
        c_right = self.cannibals - c_left

        if not (0 <= m_left <= self.missionaries and 0 <= c_left <= self.cannibals):
            return False
        if m_left > 0 and c_left > m_left:
            return False          # missionaries outnumbered on the left
        if m_right > 0 and c_right > m_right:
            return False          # missionaries outnumbered on the right
        return True

    def successors(self, state):
        """Try every boat load of m missionaries and c cannibals (1 <= m + c <= capacity)."""
        m_left, c_left, boat = state
        result = []

        for m in range(self.boat_capacity + 1):
            for c in range(self.boat_capacity + 1 - m):
                if m + c == 0:
                    continue          # the boat cannot cross empty

                if boat == 0:         # boat goes left -> right
                    next_state = (m_left - m, c_left - c, 1)
                    direction = "right"
                else:                 # boat goes right -> left
                    next_state = (m_left + m, c_left + c, 0)
                    direction = "left"

                if self.is_valid(next_state):
                    move = f"Move {m}M {c}C {direction}"
                    result.append((next_state, move))

        return result

    def to_display(self, state):
        """List 'M', 'C' and 'Boat' on each bank."""
        m_left, c_left, boat = state
        m_right = self.missionaries - m_left
        c_right = self.cannibals - c_left

        left = ["M"] * m_left + ["C"] * c_left
        right = ["M"] * m_right + ["C"] * c_right
        if boat == 0:
            left.append("Boat")
        else:
            right.append("Boat")
        return {"left": left, "right": right}


# ---------------------------------------------------------------------------
# Registry of available puzzles
# ---------------------------------------------------------------------------

PUZZLES = {
    "farmer": FarmerWolfGoatCabbage,
    "missionaries": MissionariesCannibals,
}


# ---------------------------------------------------------------------------
# Command-line demo
# ---------------------------------------------------------------------------

def print_solution(title, result):
    """Print a solution path step by step."""
    print(f"\n=== {title} ===")
    if result is None:
        print("No solution found.")
        return
    for i, step in enumerate(result["path"]):
        left = ", ".join(step["left"]) or "-"
        right = ", ".join(step["right"]) or "-"
        print(f"{i:2}. {step['move']:<32} | Left: {left:<30} | Right: {right}")


def print_comparison(name, results):
    """Print a BFS vs DFS table for one puzzle."""
    print(f"\n{name}")
    print(f"{'Algorithm':<10}{'Path length':>12}{'Expanded':>10}{'Generated':>11}{'Time (ms)':>11}")
    for algo in ("bfs", "dfs"):
        r = results[algo]
        if r is None:
            print(f"{algo.upper():<10}{'no solution':>12}")
        else:
            print(f"{algo.upper():<10}{r['path_length']:>12}{r['nodes_expanded']:>10}"
                  f"{r['nodes_generated']:>11}{r['time_ms']:>11.3f}")


if __name__ == "__main__":
    for key, puzzle_class in PUZZLES.items():
        problem = puzzle_class()
        print_solution(f"{puzzle_class.__name__} (BFS)", bfs(problem))

    print("\n=== BFS vs DFS ===")
    for key, puzzle_class in PUZZLES.items():
        print_comparison(puzzle_class.__name__, compare(puzzle_class()))
