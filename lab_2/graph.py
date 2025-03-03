import heapq
import pygame
import utils
from collections import deque


class Node:

    def __init__(self, index, x, y):
        self.index = index
        self.x = x
        self.y = y
        self.position = pygame.Vector2(x, y)
        self.extra_info = None
        self.g_cost = float('inf')
        self.h_cost = 0
        self.f_cost = 0
        self.parent = None

    def __eq__(self, index):
        return self.index == index

    def __hash__(self):
        return hash(self.index)

    def set_extra_info(self, info):
        self.extra_info = info
    
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

    def get_node_by_index(self, index):
        return self.nodes[index]

    def add_edge(self, from_index, to_index, cost):
        
        from_node = self.nodes[from_index]
        to_node = self.nodes[to_index]
        from_pos = (from_node.x, from_node.y)
        to_pos = (to_node.x, to_node.y)

        if not self.is_line_clear(from_pos, to_pos):
            return
        
        edge = Edge(from_index, to_index, cost)
        self.edges[from_index].append(edge)
        self.edges[to_index].append(Edge(to_index, from_index, cost))


    def is_line_clear(self, from_pos, to_pos):
        for polygon in utils.POLYGONS:
            if utils.ray_intersects_polygon(from_pos, to_pos, polygon):
                return False
        for rect in utils.RECTS:
            corners = [rect.topleft, rect.topright, rect.bottomright, rect.bottomleft]
            if utils.ray_intersects_polygon(from_pos, to_pos, corners):
                return False
        for walls in utils.WALLS:
            corners = [walls.topleft, walls.topright, walls.bottomright, walls.bottomleft]
            if utils.ray_intersects_polygon(from_pos, to_pos, corners):
                return False

        return True


    def get_neighbors(self, node):
        neighbors = []
        for edge in self.edges.get(node.index, []):
            if edge.from_node == node.index:
                neighbors.append(self.nodes.get(edge.to_node, None))
        return neighbors
    

    def heuristic(self, node1, node2):
        dx = abs(node1.x - node2.x)
        dy = abs(node1.y - node2.y)
        return max(dx, dy)

    def a_star(self, start_index, goal_index):
        open_set = []
        heapq.heappush(open_set, (0, start_index))
        came_from = {}
        g_score = {node: float('inf') for node in self.nodes}
        g_score[start_index] = 0
        f_score = {node: float('inf') for node in self.nodes}
        f_score[start_index] = self.heuristic(self.nodes[start_index], self.nodes[goal_index])

        while open_set:
            _, current = heapq.heappop(open_set)

            if current == goal_index:
                return self.reconstruct_path(came_from, current)

            for edge in self.edges[current]:
                tentative_g_score = g_score[current] + edge.cost
                if tentative_g_score < g_score[edge.to_node]:
                    came_from[edge.to_node] = current
                    g_score[edge.to_node] = tentative_g_score
                    f_score[edge.to_node] = g_score[edge.to_node] + self.heuristic(self.nodes[edge.to_node], self.nodes[goal_index])
                    if edge.to_node not in [i[1] for i in open_set]:
                        heapq.heappush(open_set, (f_score[edge.to_node], edge.to_node))
        return None
    
    
    def flood_fill_graph(self, x, y):
        edge_dist = utils.CELL_SIZE
        queue = deque([(x, y)])
        visited = set()

        start_node = Node(0, x, y)
        self.add_node(start_node)

        while queue:
            cx, cy = queue.popleft()

            if (cx, cy) in visited:
                continue

            visited.add((cx, cy))
            current_node = Node(len(self.nodes), cx, cy)
            self.add_node(current_node)

            for dx, dy in [(0, -edge_dist), (0, edge_dist),
                           (-edge_dist, 0), (edge_dist, 0),
                           (-edge_dist, -edge_dist), (edge_dist, -edge_dist),
                           (-edge_dist, edge_dist), (edge_dist, edge_dist)]:
                nx, ny = cx + dx, cy + dy

                if 0 <= nx <= utils.SCREEN.get_width() and 0 <= ny <= utils.SCREEN.get_height():
                    if utils.is_on_obstacle_border(nx, ny):
                        if dx == 0 or dy == 0:
                            cost = 1.0
                        else:
                            cost = 1.414
                        neighbor_node_index = None
                        for node in self.nodes.values():
                            if node.x == nx and node.y == ny:
                                neighbor_node_index = node.index
                                break
                        if neighbor_node_index is None:
                            neighbor_node = Node(len(self.nodes), nx, ny)
                            self.add_node(neighbor_node)
                            neighbor_node_index = neighbor_node.index
                        self.add_edge(current_node.index, neighbor_node_index, cost)
                        queue.append((nx, ny))


    def generate_graph(self):
        utils.create_and_draw_obstacles()
        start_pos = utils.CELL_SIZE // 2, utils.CELL_SIZE // 2
        self.flood_fill_graph(start_pos[0], start_pos[1])

    
    def reconstruct_path(self, came_from, current):
        total_path = [self.nodes[current]]
        while current in came_from:
            current = came_from[current]
            total_path.append(self.nodes[current])
        total_path.reverse()
        return total_path
    
    
    def path_to_closest_item(self, start_node, items):
        closest_path = None
        min_cost = float('inf')

        for item in items:
            path = self.a_star(start_node.index, item.node.index)
            if path:
                cost = len(path) - 1
                if cost < min_cost:
                    min_cost = cost
                    closest_path = path

        return closest_path