import pygame
import math
# Constants
# Colors
COLORS = {
    "RED": (255, 0, 0),
    "BLUE": (0, 0, 255),
    "ZOMBIE": (0, 255, 0),
    "YELLOW": (255, 255, 0),
    "OBSTACLES": (71, 105, 91),
    "BULLET": (255, 255, 255),
    "PLAYER": (0, 0, 255),
}

# Screen settings
SCREEN_WIDTH = 1500
SCREEN_HEIGHT = 800
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
CLOCK = pygame.time.Clock()

# Steering behavior constants
ZOMBIE_RADIUS = 6
MIN_DETECTION_LEN = 20
MAX_STEERING_FORCE = 25.0
NEIGHBOR_RADIUS = 60
PANIC_DISTANCE = 300
RELATIVE_SAFE_DISTANCE = 450
# Positions
OBSTACLES = [
    {"position": pygame.math.Vector2(200, 300), "radius": 50},
    {"position": pygame.math.Vector2(400, 250), "radius": 50},
    {"position": pygame.math.Vector2(600, 500), "radius": 50},
    {"position": pygame.math.Vector2(800, 200), "radius": 50},
    {"position": pygame.math.Vector2(1000, 600), "radius": 50},
    {"position": pygame.math.Vector2(1100, 200), "radius": 50},
    {"position": pygame.math.Vector2(1300, 300), "radius": 50},
]

ZOMBIES = [
    pygame.math.Vector2(700, 100),
    pygame.math.Vector2(800, 250),
    pygame.math.Vector2(900, 300),
    pygame.math.Vector2(1000, 450),
    pygame.math.Vector2(1100, 500),
    pygame.math.Vector2(1200, 650),
    pygame.math.Vector2(1300, 100),
    pygame.math.Vector2(1400, 250),
    pygame.math.Vector2(700, 300),
    pygame.math.Vector2(800, 450),
    pygame.math.Vector2(900, 500),
    pygame.math.Vector2(1000, 650),
    pygame.math.Vector2(1100, 700),
    pygame.math.Vector2(1200, 150),
    pygame.math.Vector2(1000, 200),
    pygame.math.Vector2(1100, 350),
    pygame.math.Vector2(1200, 400),
    pygame.math.Vector2(1300, 550),
    pygame.math.Vector2(1400, 650),
    pygame.math.Vector2(1500, 700),
]

# Utility functions
def truncate(vec, max_len=MAX_STEERING_FORCE):
    if vec.length() > max_len:
        vec.scale_to_length(max_len)
    return vec


def ray_circle_intersection(ray_start, ray_direction, circle_center, radius):
     # Vector from ray start to circle center
    to_circle = circle_center - ray_start
    dot_product = to_circle.dot(ray_direction)
    closest_point = ray_start + ray_direction * dot_product

    # Distance from closest point on the ray to the circle center
    distance_to_circle = (closest_point - circle_center).length()

    if distance_to_circle > radius:
        return None  # No intersection

    # Calculate intersection distance along the ray
    offset = math.sqrt(radius**2 - distance_to_circle**2)
    t1 = dot_product - offset
    t2 = dot_product + offset
    if t1 > 0:
        return ray_start + ray_direction * t1
    elif t2 > 0:
        return ray_start + ray_direction * t2

    return None