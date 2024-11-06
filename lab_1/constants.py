import pygame
# Constants
COLOR_ZOMBIE = (255,50,50)
COLOR_OBSTACLES = (71, 105, 91)
COLOR_BULLET = (255, 255, 255)  
COLOR_PLAYER =  (0, 0, 255)
COLOR_GUN = (255, 0, 0)
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
CLOCK = pygame.time.Clock()

MIN_DETECTION = 2
MAX_DETECTION = 8
MAX_AVOID_FORCE = 2

OBSTACLES_POS = [
    [pygame.math.Vector2(120, 500), 100],
    [pygame.math.Vector2(500, 100), 70],
    [pygame.math.Vector2(300, 200), 90],
    [pygame.math.Vector2(900, 300), 70],
    [pygame.math.Vector2(700, 600), 80],
]