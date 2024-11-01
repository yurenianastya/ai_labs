import pygame
import math
import entity

pygame.init()

# Constants
COLOR_RED = (255,50,50)
COLOR_OBSTACLES = (71, 105, 91)
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Zombie attack")
CLOCK = pygame.time.Clock()

zombies = [
    entity.Agent((520,100)),
    entity.Agent((540,100)),
    entity.Agent((560,100)),
    entity.Agent((580,100)),
    entity.Agent((480,100)),
    entity.Agent((460,100))
]

def draw_triangle(surface, pos):
    length = 20
    angle = 60
    points = [
        pos + pygame.Vector2(math.cos(angle), math.sin(angle)) * length,
        pos + pygame.Vector2(math.cos(angle + 2.5), math.sin(angle + 2.5)) * length,
        pos + pygame.Vector2(math.cos(angle - 2.5), math.sin(angle - 2.5)) * length,
    ]
    pygame.draw.polygon(surface, COLOR_RED, points)


def create_obstacles():
    pygame.draw.circle(SCREEN, COLOR_OBSTACLES, (100, 500), 110)
    pygame.draw.circle(SCREEN, COLOR_OBSTACLES, (500, 400), 100)
    pygame.draw.circle(SCREEN, COLOR_OBSTACLES, (800, 100), 80)
    pygame.draw.circle(SCREEN, COLOR_OBSTACLES, (300, 200), 100)
    pygame.draw.circle(SCREEN, COLOR_OBSTACLES, (900, 600), 80)


# Game running
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    SCREEN.fill((0, 0, 0))

    create_obstacles()
    for zombie in zombies:
        zombie.update(30)
        pygame.draw.circle(SCREEN, COLOR_RED, zombie.position, 10)
        zombie.wrap_around(SCREEN_WIDTH, SCREEN_HEIGHT)
    pygame.display.flip()
    CLOCK.tick(60)
