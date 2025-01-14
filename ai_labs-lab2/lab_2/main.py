import pygame
import graph
import utils
import raven
import math
import random

pygame.init()
map_graph = graph.Graph()
map_graph.generate_graph()

BOTS = [
    raven.RavenBot(
        map_graph.nodes.get(45),
        map_graph
    ),
    raven.RavenBot(
        map_graph.nodes.get(3100),
        map_graph
    ),
    raven.RavenBot(
        map_graph.nodes.get(500),
        map_graph
    ),
    raven.RavenBot(
        map_graph.nodes.get(1200),
        map_graph
    ),
]

class PickupItem:
    
    
    def __init__(self, x, y, item_type):
        self.x = x
        self.y = y
        self.item_type = item_type

    def draw(self, surface):
        if self.item_type == "health":
            radius = 13
            pygame.draw.circle(surface, (0, 100, 0), (self.x, self.y), radius)
            pygame.draw.line(surface, (255, 255, 255), (self.x - radius // 2, self.y), (self.x + radius // 2, self.y), 5)
            pygame.draw.line(surface, (255, 255, 255), (self.x, self.y - radius // 2 ), (self.x, self.y + radius // 2), 5)


            
        elif self.item_type == "armor":
            
            pygame.draw.rect(surface, (0, 0, 255), (self.x - 12, self.y - 10, 24, 20))
            pygame.draw.polygon(surface, (0, 0, 255), [
                (self.x - 12, self.y + 10), 
                (self.x + 12, self.y + 10),
                (self.x + 8, self.y + 20),
                (self.x - 8, self.y + 20)
            ])
            pygame.draw.rect(surface, (255, 255, 255), (self.x - 9, self.y - 7, 18, 14))
            pygame.draw.polygon(surface, (255, 255, 255), [
                (self.x - 9, self.y + 7),
                (self.x + 9, self.y + 7),
                (self.x + 6, self.y + 14),
                (self.x - 6, self.y + 14)
            ])  
            pygame.draw.rect(surface, (0, 0, 255), (self.x - 6, self.y - 4, 12, 8))
            pygame.draw.polygon(surface, (0, 0, 255), [
                (self.x - 6, self.y + 4),
                (self.x + 6, self.y + 4),
                (self.x + 4, self.y + 8),
                (self.x - 4, self.y + 8)
            ])  
            
def is_edge_node(node, graph):
    min_x = min(node.x for node in graph.nodes.values())
    max_x = max(node.x for node in graph.nodes.values())
    min_y = min(node.y for node in graph.nodes.values())
    max_y = max(node.y for node in graph.nodes.values())

    
    return (node.x == min_x or node.x == max_x or node.y == min_y or node.y == max_y)

def is_too_close(new_item, existing_items, min_distance=30):
    for item in existing_items:
        distance = math.sqrt((new_item.x - item.x)**2 + (new_item.y - item.y)**2)
        if distance < min_distance:  
            return True
    return False

PICKUP_ITEMS = []
used_nodes = set()  

for _ in range(5):
    
    health_node = random.choice(list(map_graph.nodes.values()))
    while health_node.index in used_nodes or is_edge_node(health_node, map_graph) or is_too_close(health_node, PICKUP_ITEMS):  
        health_node = random.choice(list(map_graph.nodes.values()))
    used_nodes.add(health_node.index)
    PICKUP_ITEMS.append(PickupItem(health_node.x, health_node.y, "health"))

    
    armor_node = random.choice(list(map_graph.nodes.values()))
    while armor_node.index in used_nodes or is_edge_node(armor_node, map_graph) or is_too_close(armor_node, PICKUP_ITEMS):  
        armor_node = random.choice(list(map_graph.nodes.values()))
    used_nodes.add(armor_node.index)
    PICKUP_ITEMS.append(PickupItem(armor_node.x, armor_node.y, "armor"))

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
        pygame.draw.lines(surface, (0, 0, 0), False, points, 5)

    pygame.draw.circle(surface, utils.BOT_COLOR, (start_node.x, start_node.y), 8)
    pygame.draw.circle(surface, utils.EDGE_COLOR, (goal_node.x, goal_node.y), 8)

def draw_bots(bots, surface):
    for bot in bots:
        pygame.draw.circle(surface, utils.BOT_COLOR, bot.position, 8)
        draw_hit_bars(bot, surface)

def draw_hit_bars(bot, surface):
    bar_width = 40
    bar_height = 5
    x, y = bot.position
    health_bar_x = x - bar_width // 2
    health_bar_y = y - 20  
    armor_bar_y = health_bar_y - 8

    health_percent = bot.health / bot.max_health
    armor_percent = bot.armor / bot.max_armor

    pygame.draw.rect(surface, (255, 0, 0), (health_bar_x, health_bar_y, bar_width, bar_height))  
    pygame.draw.rect(surface, (255, 0, 0), (health_bar_x, health_bar_y, int(bar_width * health_percent), bar_height)) 

    pygame.draw.rect(surface, (0, 200, 255), (health_bar_x, armor_bar_y, bar_width, bar_height))
    pygame.draw.rect(surface, (0, 200, 255), (health_bar_x, armor_bar_y, int(bar_width * armor_percent), bar_height)) 

def draw_pickup_items(items, surface):
    for item in items:
        item.draw(surface)

def handle_events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
            return False
    return True

for bot in BOTS:
    bot.calculate_path()

running = True
while running:
    running = handle_events()
    if not running:
        break

    dt = utils.CLOCK.tick(60) / 1000.0
    for bot in BOTS:
        bot.update(dt)

    utils.SCREEN.fill(utils.MAP_COLOR)

    utils.create_and_draw_obstacles()
    draw_graph(map_graph, utils.SCREEN)
    draw_bots(BOTS, utils.SCREEN)
    draw_pickup_items(PICKUP_ITEMS, utils.SCREEN)  

    pygame.display.flip()

pygame.quit()
