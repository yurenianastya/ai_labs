import math
import pygame


SCREEN = pygame.display.set_mode((1000, 800))
CLOCK = pygame.time.Clock()
OBSTACLE_COLOR = (40, 148, 0)
NODE_COLOR = (255, 0, 0)
EDGE_COLOR = (0, 0, 200)
MAP_COLOR = (255, 255, 255)
AGENT_COLOR = (179, 0, 255)
CELL_SIZE = 20
SHOTS = []

POLYGONS = [
    [(500, 500), (600, 300), (700, 300), (800, 500)],
    [(150, 250), (300, 320), (300, 440), (400, 440), (340, 80)],
    [(10, 700), (10, 500), (160, 600)],
    [(40, 200), (200, 80), (40, 80)],
    [(800, 300), (950, 300), (800, 100)],
]

RECTS = [
    pygame.Rect(650,50,60,200),
    pygame.Rect(250,650,200,100),
    pygame.Rect(650,590,160,200),
]

WALLS = [
    # left wall
    pygame.Rect(0, 0, 10, SCREEN.get_height()),
    # lower wall
    pygame.Rect(0, SCREEN.get_height() - 10, SCREEN.get_width(), 10),
    # right wall
    pygame.Rect(SCREEN.get_width() - 10, 0, 10, SCREEN.get_height()),
    # upper wall
    pygame.Rect(0, 0, SCREEN.get_width(), 10),
]

WANDER_NODES_IDX = [1859, 3030, 584, 2375, 58, 1000]

def is_on_obstacle_border(nx, ny, border_tolerance=1):
    if SCREEN.get_at((nx, ny)) == MAP_COLOR:
        return True
    
    all_neighbors_are_obstacles = True
    for dx in range(-border_tolerance, border_tolerance + 1):
        for dy in range(-border_tolerance, border_tolerance + 1):
            if dx == 0 and dy == 0:
                continue
            
            neighbor_x, neighbor_y = nx + dx, ny + dy

            if 0 <= neighbor_x < SCREEN.get_width() and 0 <= neighbor_y < SCREEN.get_height():
                if SCREEN.get_at((neighbor_x, neighbor_y)) != OBSTACLE_COLOR:
                    all_neighbors_are_obstacles = False
                    break
        if not all_neighbors_are_obstacles:
            break
    if all_neighbors_are_obstacles:
        return False
    return True

def is_edge_node(node, graph):
    min_x = min(node.x for node in graph.nodes.values())
    max_x = max(node.x for node in graph.nodes.values())
    min_y = min(node.y for node in graph.nodes.values())
    max_y = max(node.y for node in graph.nodes.values())
    return (node.x == min_x or node.x == max_x or node.y == min_y or node.y == max_y)

def is_item_too_close(new_item, existing_items, min_distance=30):
        for item in existing_items:
            distance = math.sqrt((new_item.position.x - item.position.x)**2
              + (new_item.position.y - item.position.y)**2)
            if distance < min_distance:  
                return True
        return False

def create_and_draw_obstacles():
    for rects in RECTS:
        pygame.draw.rect(SCREEN, OBSTACLE_COLOR, rects)
    for polygons in POLYGONS:
        pygame.draw.polygon(SCREEN, OBSTACLE_COLOR, polygons)
    for walls in WALLS:
        pygame.draw.rect(SCREEN, OBSTACLE_COLOR, walls)


def get_node_by_position(graph, position):
    return next((node for node in graph.nodes.values() if node.position == position), None)


def line_intersection(p1, p2, q1, q2):
    def ccw(a, b, c):
        return (c[1] - a[1]) * (b[0] - a[0]) > (b[1] - a[1]) * (c[0] - a[0])

    if ccw(p1, q1, q2) != ccw(p2, q1, q2) and ccw(p1, p2, q1) != ccw(p1, p2, q2):
        s1_x = p2[0] - p1[0]
        s1_y = p2[1] - p1[1]
        s2_x = q2[0] - q1[0]
        s2_y = q2[1] - q1[1]

        s = (-s1_y * (p1[0] - q1[0]) + s1_x * (p1[1] - q1[1])) / (-s2_x * s1_y + s1_x * s2_y)
        t = ( s2_x * (p1[1] - q1[1]) - s2_y * (p1[0] - q1[0])) / (-s2_x * s1_y + s1_x * s2_y)

        if 0 <= s <= 1 and 0 <= t <= 1:
            # Intersection detected
            intersection_x = p1[0] + (t * s1_x)
            intersection_y = p1[1] + (t * s1_y)
            return (intersection_x, intersection_y)
    return None


def ray_intersects_polygon(start, end, polygon):
    for i in range(len(polygon)):
        p1 = polygon[i]
        p2 = polygon[(i + 1) % len(polygon)]
        if line_intersection(start, end, p1, p2) is not None:
            return True
    return False


def cast_ray(start, direction, max_distance):
    end = (start[0] + direction[0] * max_distance, start[1] + direction[1] * max_distance)
    closest_intersection = None
    min_distance = max_distance

    # Check each obstacle
    for polygon in POLYGONS:
        if ray_intersects_polygon(start, end, polygon):
            for i in range(len(polygon)):
                p1 = polygon[i]
                p2 = polygon[(i + 1) % len(polygon)]
                intersection = line_intersection(start, end, p1, p2)
                if intersection:
                    dist = math.dist(start, intersection)
                    if dist < min_distance:
                        closest_intersection = intersection
                        min_distance = dist

    for rect in RECTS + WALLS:
        corners = [
            rect.topleft, rect.topright, rect.bottomright, rect.bottomleft
        ]
        if ray_intersects_polygon(start, end, corners):
            for i in range(len(corners)):
                p1 = corners[i]
                p2 = corners[(i + 1) % len(corners)]
                intersection = line_intersection(start, end, p1, p2)
                if intersection:
                    dist = math.dist(start, intersection)
                    if dist < min_distance:
                        closest_intersection = intersection
                        min_distance = dist

    return closest_intersection or end


def closest_point_on_segment(point, segment_start, segment_end):
    segment_vector = segment_end - segment_start
    point_vector = point - segment_start
    segment_length_squared = segment_vector.length_squared()

    if segment_length_squared == 0:
        return segment_start

    t = max(0, min(1, point_vector.dot(segment_vector) / segment_length_squared))
    return segment_start + t * segment_vector


def closest_point_to_rect(point, rect):
    clamped_x = max(rect.left, min(point.x, rect.right))
    clamped_y = max(rect.top, min(point.y, rect.bottom))
    return pygame.Vector2(clamped_x, clamped_y)

def rect_edges(rect):
    top_left = pygame.Vector2(rect.topleft)
    top_right = pygame.Vector2(rect.topright)
    bottom_left = pygame.Vector2(rect.bottomleft)
    bottom_right = pygame.Vector2(rect.bottomright)
    return [
        (top_left, top_right),
        (top_right, bottom_right),
        (bottom_right, bottom_left),
        (bottom_left, top_left),
    ]

def get_nodes_within_flee_range(graph, target_position, min_distance, max_distance):
    valid_nodes = []
    for node in graph.nodes:
        distance = euclidean_distance(node.position, target_position)
        if min_distance <= distance <= max_distance:
            valid_nodes.append(node)
    return valid_nodes

def euclidean_distance(a, b):
    return math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2)

def remove_agent(agent, all_agents):
    if agent in all_agents:
        all_agents.remove(agent)
    pass