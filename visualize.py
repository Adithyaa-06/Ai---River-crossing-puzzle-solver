"""
Draw the full state space graph of the Farmer, Wolf, Goat, Cabbage puzzle.

  * Nodes  - every valid state, labelled with its (F, W, G, C) tuple
  * Edges  - legal moves between states
  * Green  - start state (0, 0, 0, 0)
  * Red    - goal state  (1, 1, 1, 1)
  * Thick blue edges - the BFS solution path

Nodes are arranged in columns by their BFS depth (number of moves from
the start), so the picture reads left to right like the search does.

Run with:  python visualize.py   -> saves state_space.png
"""

from collections import deque
from itertools import product

import matplotlib
matplotlib.use("Agg")            # draw to a file, no window needed
import matplotlib.pyplot as plt
import networkx as nx

from solver import FarmerWolfGoatCabbage, bfs


def build_graph(problem):
    """
    Build an undirected graph: one node per valid state, one edge per move.
    Every move can be reversed, so undirected edges are enough.
    """
    graph = nx.Graph()

    # All 2^4 = 16 combinations, keeping only the valid ones.
    for state in product([0, 1], repeat=4):
        if problem.is_valid(state):
            graph.add_node(state)

    for state in list(graph.nodes):
        for next_state, move in problem.successors(state):
            graph.add_edge(state, next_state, move=move)

    return graph


def bfs_depths(graph, start):
    """Return {state: number of moves from start}, found with a simple BFS."""
    depth = {start: 0}
    queue = deque([start])
    while queue:
        state = queue.popleft()
        for neighbour in graph.neighbors(state):
            if neighbour not in depth:
                depth[neighbour] = depth[state] + 1
                queue.append(neighbour)
    return depth


def draw(problem, filename="state_space.png"):
    """Draw the graph, highlight start, goal and the BFS path, and save it."""
    graph = build_graph(problem)
    start = problem.initial_state
    goal = (1, 1, 1, 1)

    # Position: x = depth from the start, y = order in which BFS found the
    # state within that depth (this order keeps the edges from crossing).
    depth = bfs_depths(graph, start)
    columns = {}
    for state in depth:                       # dict keeps BFS discovery order
        columns.setdefault(depth[state], []).append(state)

    positions = {}
    for x, states in columns.items():
        for i, state in enumerate(states):
            y = (len(states) - 1) / 2 - i     # centre each column vertically
            positions[state] = (x, y)

    # Edges on the BFS solution path.
    path_states = [step["state"] for step in bfs(problem)["path"]]
    path_edges = list(zip(path_states, path_states[1:]))

    colors = []
    for state in graph.nodes:
        if state == start:
            colors.append("#22c55e")      # green
        elif state == goal:
            colors.append("#ef4444")      # red
        else:
            colors.append("#e5e7eb")      # light grey

    plt.figure(figsize=(14, 6))
    nx.draw_networkx_edges(graph, positions, edge_color="#9ca3af", width=1.5)
    nx.draw_networkx_edges(graph, positions, edgelist=path_edges,
                           edge_color="#2563eb", width=5)
    nx.draw_networkx_nodes(graph, positions, node_color=colors,
                           node_size=2600, edgecolors="#374151")
    nx.draw_networkx_labels(graph, positions,
                            labels={s: str(s) for s in graph.nodes}, font_size=9)

    plt.title("Farmer, Wolf, Goat, Cabbage - state space (F, W, G, C), 0 = left, 1 = right\n"
              "green = start, red = goal, thick blue = BFS solution path")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    print(f"Saved {filename}: {graph.number_of_nodes()} states, "
          f"{graph.number_of_edges()} moves, BFS path of {len(path_edges)} moves")


if __name__ == "__main__":
    draw(FarmerWolfGoatCabbage())
