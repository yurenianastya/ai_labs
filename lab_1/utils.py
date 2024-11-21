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
DETECTION = {
    "MIN": 5,
    "MAX": 50,
}
MAX_STEERING_FORCE = 2.0
NEIGHBOR_RADIUS = 100
PANIC_DISTANCE = 250

# Positions
OBSTACLES = [
    {"position": pygame.math.Vector2(120, 500), "radius": 60},
    {"position": pygame.math.Vector2(600, 100), "radius": 70},
    {"position": pygame.math.Vector2(1300, 200), "radius": 94},
    {"position": pygame.math.Vector2(900, 300), "radius": 70},
    {"position": pygame.math.Vector2(450, 300), "radius": 80},
    {"position": pygame.math.Vector2(450, 600), "radius": 80},
    {"position": pygame.math.Vector2(1000, 700), "radius": 80},
    {"position": pygame.math.Vector2(100, 100), "radius": 70},
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
    # pygame.math.Vector2(60, 40),
    # pygame.math.Vector2(20, 40),
    # pygame.math.Vector2(40, 40),
    # pygame.math.Vector2(700, 40),
    # pygame.math.Vector2(500, 600),
    # pygame.math.Vector2(70, 340),
    # pygame.math.Vector2(0, 30),
    # pygame.math.Vector2(40, 405),
    # pygame.math.Vector2(160, 40),
    # pygame.math.Vector2(120, 40),
    # pygame.math.Vector2(140, 40),
]

# Utility functions
def truncate(vec, max_len=MAX_STEERING_FORCE):
    """Truncate a vector to a maximum length."""
    if vec.length() > max_len:
        vec.scale_to_length(max_len)
    return vec