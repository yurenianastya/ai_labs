import pygame
# Constants
COLOR_RED = (255,0,0)
COLOR_BLUE = (0,0,255)
COLOR_GREEN = (0,255,0)
COLOR_YELLOW = (255,255,0)
COLOR_OBSTACLES = (71, 105, 91)
COLOR_BULLET = (255, 255, 255)  
COLOR_PLAYER =  (0, 0, 255)
COLOR_GUN = (255, 0, 0)
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
CLOCK = pygame.time.Clock()

MIN_DETECTION = 10
MAX_DETECTION = 30
MAX_STEERING_FORCE = 2
NEIGHBOR_RADIUS = 70
PANIC_DISTANCE = 250

OBSTACLES_POS = [
    [pygame.math.Vector2(120, 500), 100],
    [pygame.math.Vector2(600, 100), 70],
    [pygame.math.Vector2(1300, 200), 90],
    [pygame.math.Vector2(900, 300), 70],
    [pygame.math.Vector2(700, 600), 80],
    [pygame.math.Vector2(1000, 700), 80],
]


ZOMBIES_POS = [
    pygame.math.Vector2(520,440),
    pygame.math.Vector2(700,320),
    pygame.math.Vector2(200,400),
    pygame.math.Vector2(100,450),
    pygame.math.Vector2(500,800),
    pygame.math.Vector2(800,420),
    pygame.math.Vector2(10,720),
    pygame.math.Vector2(40,320),
    pygame.math.Vector2(10,10),
    pygame.math.Vector2(50,900),
    pygame.math.Vector2(60,40),
    pygame.math.Vector2(20,40),
    pygame.math.Vector2(40,40),
    pygame.math.Vector2(700,40),
    pygame.math.Vector2(500,600),
    pygame.math.Vector2(70,400),
    pygame.math.Vector2(0,30),
    pygame.math.Vector2(40,405),
    pygame.math.Vector2(160,40),
    pygame.math.Vector2(120,40),
    pygame.math.Vector2(140,40),
]

def truncate(vec, max_len=MAX_STEERING_FORCE):
    if vec.length() == 0:
        return vec
    if vec.length() > max_len:
        vec.scale_to_length(max_len)
    return vec


class Obstacle():

    # position (x,y) and radius
    def __init__(self, position, radius):
        self.position = position
        self.radius = radius

    
    def draw(self):
        pygame.draw.circle(SCREEN, COLOR_OBSTACLES,
                            (int(self.position[0]), int(self.position[1])), self.radius)
    

obstacles = [ Obstacle(pos, rad) for pos, rad in OBSTACLES_POS ]