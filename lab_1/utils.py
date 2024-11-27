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
MAX_STEERING_FORCE = 2.0
NEIGHBOR_RADIUS = 70
PANIC_DISTANCE = 150
RELATIVE_SAFE_DISTANCE = 300
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
    pygame.math.Vector2(570, 440),
    pygame.math.Vector2(700, 320),
    pygame.math.Vector2(200, 400),
    pygame.math.Vector2(100, 450),
    pygame.math.Vector2(500, 800),
    pygame.math.Vector2(700, 450),
    pygame.math.Vector2(10, 720),
    pygame.math.Vector2(700, 500),
    pygame.math.Vector2(200, 500),
    pygame.math.Vector2(100, 600),
    pygame.math.Vector2(500, 600),
    pygame.math.Vector2(700, 700),
    pygame.math.Vector2(10, 800),
    
]

# Utility functions
def truncate(vec, max_len=MAX_STEERING_FORCE):
    if vec.length() > max_len:
        vec.scale_to_length(max_len)
    return vec