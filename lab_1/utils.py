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
MIN_DETECTION_LEN = 10
MAX_STEERING_FORCE = 1.5
NEIGHBOR_RADIUS = 110
PANIC_DISTANCE = 350
# Positions
OBSTACLES = [
    {"position": pygame.math.Vector2(200, 300), "radius": 60},
    {"position": pygame.math.Vector2(400, 250), "radius": 70},
    {"position": pygame.math.Vector2(600, 500), "radius": 94},
    {"position": pygame.math.Vector2(800, 200), "radius": 70},
    {"position": pygame.math.Vector2(1000, 600), "radius": 80},
    {"position": pygame.math.Vector2(1100, 200), "radius": 80},
    {"position": pygame.math.Vector2(1300, 300), "radius": 80},
]

ZOMBIES = [
    pygame.math.Vector2(570, 440),
    pygame.math.Vector2(700, 320),
    pygame.math.Vector2(200, 400),
    pygame.math.Vector2(100, 450),
    pygame.math.Vector2(500, 800),
    pygame.math.Vector2(700, 450),
    pygame.math.Vector2(10, 720),
    pygame.math.Vector2(40, 320),
    pygame.math.Vector2(10, 10),
    pygame.math.Vector2(50, 900),
    pygame.math.Vector2(60, 40),
    pygame.math.Vector2(20, 40),
    pygame.math.Vector2(40, 40),
    pygame.math.Vector2(700, 40),
    pygame.math.Vector2(500, 600),
    pygame.math.Vector2(70, 340),
    pygame.math.Vector2(0, 30),
    pygame.math.Vector2(40, 405),
    pygame.math.Vector2(160, 40),
    pygame.math.Vector2(120, 40),
    pygame.math.Vector2(140, 40),
]

# Utility functions
def truncate(vec, max_len=MAX_STEERING_FORCE):
    """Truncate a vector to a maximum length."""
    if vec.length() > max_len:
        vec.scale_to_length(max_len)
    return vec