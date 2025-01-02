import math
import heapq


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

class Edge:
    def __init__(self, from_node, to_node, cost=1.0):
        self.from_node = from_node
        self.to_node = to_node
        self.cost = cost

class Graph:
    def __init__(self):
        self.nodes = {}
        self.edges = {}

    def add_node(self, index, position):
        self.nodes[index] = Node(index, position)
        self.edges[index] = []

    def add_edge(self, from_index, to_index, cost=1.0):
        edge = Edge(from_index, to_index, cost)
        self.edges[from_index].append(edge)
        self.edges[to_index].append(Edge(to_index, from_index, cost))

    def get_neighbors(self, node_index):
        return self.edges[node_index]

    def distance(self, node1_index, node2_index):
        pos1 = self.nodes[node1_index].position
        pos2 = self.nodes[node2_index].position
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)


pov_graph = Graph()
pov_graph.add_node(0, (30, 30))
pov_graph.add_node(1, (40, 280))
pov_graph.add_node(2, (270, 320))
pov_graph.add_node(3, (40, 510))
pov_graph.add_node(4, (330, 470))
pov_graph.add_node(5, (430, 560))
pov_graph.add_node(6, (780, 580))
pov_graph.add_node(7, (650, 320))
pov_graph.add_node(8, (770, 100))
pov_graph.add_node(9, (520, 50))
pov_graph.add_node(10, (380, 30))
pov_graph.add_node(11, (400, 300))
pov_graph.add_node(12, (500, 400))