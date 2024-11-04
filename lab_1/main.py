import pygame
import math
import entity
import constants

pygame.init()
pygame.display.set_caption("Zombie attack")

zombies = [
    entity.Agent((520,440)),
    entity.Agent((500,420)),
    entity.Agent((480,400)),
    entity.Agent((520,400)),
    entity.Agent((500,440)),
    entity.Agent((480,420))
]

def draw_triangle(surface, pos):
    length = 20
    angle = 60
    points = [
        pos + pygame.Vector2(math.cos(angle), math.sin(angle)) * length,
        pos + pygame.Vector2(math.cos(angle + 2.5), math.sin(angle + 2.5)) * length,
        pos + pygame.Vector2(math.cos(angle - 2.5), math.sin(angle - 2.5)) * length,
    ]
    pygame.draw.polygon(surface, constants.COLOR_RED, points)


def draw_obstacles():
    for obstacle_pos in constants.OBSTACLES_POS:
        obstacle = entity.Obstacle(obstacle_pos[0], obstacle_pos[1])
        obstacle.draw()


def draw_zombies():
    for zombie in zombies:
        zombie.update(30)
        zombie.draw()

# Game running
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    constants.SCREEN.fill((0, 0, 0))

    draw_obstacles()
    draw_zombies()

    pygame.display.flip()
    constants.CLOCK.tick(60)
