import pygame
import graph

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()
OBSTACLE_COLOR = (40, 148, 0)

def draw_nodes(graph):
    for node in graph.nodes:
        pygame.draw.circle(screen, (200, 0, 0), graph.nodes[node].position, 7)

def render_map():
    # obstacles
    pygame.draw.rect(screen, OBSTACLE_COLOR, pygame.Rect(450,50,50,200))
    pygame.draw.rect(screen, OBSTACLE_COLOR, pygame.Rect(150,500,200,90))
    pygame.draw.polygon(screen, OBSTACLE_COLOR, [(450, 550), (550, 350), (650, 350), (700, 550)])
    pygame.draw.polygon(screen, OBSTACLE_COLOR, [(150, 250), (300, 300), (300, 450), (400, 450), (350, 100)])
    pygame.draw.polygon(screen, OBSTACLE_COLOR, [(10, 500), (10, 300), (200, 350)])
    pygame.draw.polygon(screen, OBSTACLE_COLOR, [(50, 250), (220, 80), (50, 80)])
    pygame.draw.polygon(screen, OBSTACLE_COLOR, [(650, 300), (750, 100), (550, 100)])

def handle_events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
            return False
    return True


running = True
while running:
    running = handle_events()
    if not running:
        break
    screen.fill((255, 255, 255))
    # border for contrast
    pygame.draw.rect(
        screen,
        OBSTACLE_COLOR,
        pygame.Rect(0, 0, 800, 600),
        10,
    )

    render_map()
    draw_nodes(graph.pov_graph)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()