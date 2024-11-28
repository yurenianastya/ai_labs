import pygame

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
    "GUN": (255, 0, 0),
}

# Screen settings
SCREEN_WIDTH = 1500
SCREEN_HEIGHT = 800
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
CLOCK = pygame.time.Clock()

# Steering behavior constants
ZOMBIE_RADIUS = 6
MIN_DETECTION_LEN = 20
MAX_STEERING_FORCE = 5.0
NEIGHBOR_RADIUS = 60
PANIC_DISTANCE = 250
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