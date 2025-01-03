import utils
import heapq
from collections import deque


def a_star_search(graph, start_index, goal_index):
    open_set = []
    heapq.heappush(open_set, (0, start_index))
    came_from = {}
    g_score = {node: float('inf') for node in graph.nodes}
    g_score[start_index] = 0
    f_score = {node: float('inf') for node in graph.nodes}
    f_score[start_index] = graph.distance(start_index, goal_index)

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == goal_index:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            return path[::-1]

        for edge in graph.get_neighbors(current):
            tentative_g_score = g_score[current] + edge.cost
            if tentative_g_score < g_score[edge.to_node]:
                came_from[edge.to_node] = current
                g_score[edge.to_node] = tentative_g_score
                f_score[edge.to_node] = g_score[edge.to_node] + graph.distance(edge.to_node, goal_index)
                heapq.heappush(open_set, (f_score[edge.to_node], edge.to_node))

    return None


class Node:
    def __init__(self, index, position):
        self.index = index
        self.position = position
        self.g_cost = float('inf')
        self.h_cost = 0
        self.f_cost = 0
        self.parent = None
    
class Edge:
    def __init__(self, from_node, to_node, cost=1.0):
        self.from_node = from_node
        self.to_node = to_node
        self.cost = cost

class Graph:
    def __init__(self):
        self.nodes = {}
        self.edges = {}

    def add_node(self, node):
        if node.index not in self.nodes:
            self.nodes[node.index] = node
            self.edges[node.index] = []

    def add_edge(self, from_index, to_index, cost=1.0):
        if from_index not in self.nodes or to_index not in self.nodes:
            raise ValueError("One or both nodes do not exist")
        edge = Edge(from_index, to_index, cost)
        self.edges[from_index].append(edge)
        self.edges[to_index].append(Edge(to_index, from_index, cost))

    def get_neighbors(self, node):
        return self.edges.get(node, [])


def flood_fill_graph(screen, start_pos, graph):
    queue = deque([start_pos])
    visited = set()

    start_node = Node(0, start_pos)
    graph.add_node(start_node)

    while queue:
        cx, cy = queue.popleft()

        if (cx, cy) in visited:
            continue

        visited.add((cx, cy))
        current_node = Node(len(graph.nodes), (cx, cy))
        graph.add_node(current_node)

        for dx, dy in [(-utils.CELL_SIZE, 0), (utils.CELL_SIZE, 0),
                        (0, -utils.CELL_SIZE), (0, utils.CELL_SIZE)]:
            nx, ny = cx + dx, cy + dy

            if 0 <= nx <= 800 and 0 <= ny <= 600:
                if utils.is_on_obstacle_border(screen, nx, ny):
                    neighbor_node_index = None
                    for node in graph.nodes.values():
                        if node.position == (nx, ny):
                            neighbor_node_index = node.index
                            break
                    if neighbor_node_index is None:
                        neighbor_node = Node(len(graph.nodes), (nx, ny))
                        graph.add_node(neighbor_node)
                        neighbor_node_index = neighbor_node.index
                    graph.add_edge(current_node.index, neighbor_node_index)
                    queue.append((nx, ny))


pov_graph = Graph()
pov_graph.add_node((30, 30))
pov_graph.add_node((40, 280))
pov_graph.add_node((270, 320))
pov_graph.add_node((40, 510))
pov_graph.add_node((330, 470))
pov_graph.add_node((430, 560))
pov_graph.add_node((780, 580))
pov_graph.add_node((650, 320))
pov_graph.add_node((770, 100))
pov_graph.add_node((520, 50))
pov_graph.add_node((380, 30))
pov_graph.add_node((400, 300))
pov_graph.add_node((500, 400))