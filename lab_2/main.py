import pygame
import graph
import utils


pygame.init()
screen = pygame.display.set_mode(utils.SCREEN)
clock = pygame.time.Clock()
example = graph.Graph()


def draw_graph(graph, surface):
    for node in graph.nodes:
        for edge in graph.edges[node]:
            from_x, from_y = graph.nodes[edge.from_node].position
            to_x, to_y = graph.nodes[edge.to_node].position
            pygame.draw.line(surface, utils.EDGE_COLOR, (from_x, from_y), (to_x, to_y), 1)
    
    for node in graph.nodes.values():
        x, y = node.position
        pygame.draw.circle(surface, utils.NODE_COLOR, (x, y), 3)



def draw_obstacles():
    for rects in utils.rects:
        pygame.draw.rect(screen, utils.OBSTACLE_COLOR, rects)
    for polygons in utils.polygons:
        pygame.draw.polygon(screen, utils.OBSTACLE_COLOR, polygons)
    

def handle_events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
            return False
        if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    example.nodes.clear()
                    generate_graph()
    return True


def generate_graph():
    start_pos = utils.CELL_SIZE // 2, utils.CELL_SIZE // 2
    graph.flood_fill_graph(screen, start_pos, example)

running = True
while running:
    running = handle_events()
    if not running:
        break
    screen.fill(utils.MAP_COLOR)
    # border for contrast
    pygame.draw.rect(
        screen,
        utils.OBSTACLE_COLOR,
        pygame.Rect(0, 0, 800, 600),
        10,
    )

    draw_obstacles()
    draw_graph(example, screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()