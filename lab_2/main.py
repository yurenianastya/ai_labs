import pygame
import graph
import utils
import raven


pygame.init()
# initial obstacle drawing for graph generating
#  which uses pixel color to determine borders
map_graph = graph.Graph()
map_graph.generate_graph()

BOTS = [
    raven.RavenBot(
        map_graph.nodes.get(45)
    ),
    raven.RavenBot(
        map_graph.nodes.get(3100)
    ),
    raven.RavenBot(
        map_graph.nodes.get(500)
    ),
    raven.RavenBot(
        map_graph.nodes.get(1200)
    ),
]


start = BOTS[1].node
end = BOTS[2].node
path = map_graph.a_star(start, end)


def draw_graph(graph, surface):
    for node in graph.nodes:
        for edge in graph.edges[node]:
            from_x, from_y = graph.nodes[edge.from_node].x, graph.nodes[edge.from_node].y
            to_x, to_y = graph.nodes[edge.to_node].x, graph.nodes[edge.to_node].y
            pygame.draw.line(surface, utils.EDGE_COLOR, (from_x, from_y), (to_x, to_y), 1)
    
    for node in graph.nodes.values():
        x, y = node.x, node.y
        pygame.draw.circle(surface, utils.NODE_COLOR, (x, y), 2)
    

def draw_path(path, surface, start_node, goal_node):
    if path and len(path) > 1:
        points = [(node.x, node.y) for node in path]
        pygame.draw.lines(surface, (0,0,0), False, points, 5)

    pygame.draw.circle(surface, utils.BOT_COLOR, (start_node.x, start_node.y), 8)
    pygame.draw.circle(surface, utils.EDGE_COLOR, (goal_node.x, goal_node.y), 8)


def draw_bots(bots, surface):
    for bot in bots:
        pygame.draw.circle(surface, utils.BOT_COLOR, bot.position, 8)


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
    
    utils.SCREEN.fill(utils.MAP_COLOR)
    
    utils.create_and_draw_obstacles()
    draw_path(path, utils.SCREEN, start, end)
    draw_graph(map_graph, utils.SCREEN)
    draw_bots(BOTS, utils.SCREEN)

    pygame.display.flip()
    utils.CLOCK.tick(60)


pygame.quit()