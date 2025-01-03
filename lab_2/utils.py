import pygame


SCREEN = (800, 600)
OBSTACLE_COLOR = (40, 148, 0)
NODE_COLOR = (255, 0, 0)
EDGE_COLOR = (0, 0, 200)
MAP_COLOR = (255, 255, 255)
CELL_SIZE = 20

polygons = [
    [(450, 550), (550, 350), (650, 350), (700, 550)],
    [(150, 250), (300, 300), (300, 450), (400, 450), (340, 70)],
    [(10, 500), (10, 300), (200, 350)],
    [(50, 250), (190, 90), (40, 90)],
    [(650, 300), (750, 100), (550, 100)],
]
rects = [
    pygame.Rect(455,50,50,200),
    pygame.Rect(150,490,200,100),
]

def is_on_obstacle_border(screen, nx, ny, border_tolerance=1):
    if screen.get_at((nx, ny)) == MAP_COLOR:
        return True
    
    all_neighbors_are_obstacles = True
    for dx in range(-border_tolerance, border_tolerance + 1):
        for dy in range(-border_tolerance, border_tolerance + 1):
            if dx == 0 and dy == 0:
                continue
            
            neighbor_x, neighbor_y = nx + dx, ny + dy

            if 0 <= neighbor_x < screen.get_width() and 0 <= neighbor_y < screen.get_height():
                if screen.get_at((neighbor_x, neighbor_y)) != OBSTACLE_COLOR:
                    all_neighbors_are_obstacles = False
                    break
        if not all_neighbors_are_obstacles:
            break
    if all_neighbors_are_obstacles:
        return False
    return True