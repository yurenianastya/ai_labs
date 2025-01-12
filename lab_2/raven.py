from dataclasses import dataclass
from collections import defaultdict
import math
from typing import Optional
import pygame
import triggers
import graph
import utils

class RavenMap:

    def __init__(self, walls):
        self.walls = walls
        # class for managing event triggers
        self.trigger_sys = triggers.TriggerSystem()
        self.spawn_points = utils.SPAWN_POINTS
        self.nav_graph = graph.NavGraph()

    def update_trigger_sys(bots):
        pass


class RavenWeapons:
    
    def __init__(self, type, fire_rate, projectile_spd, ideal_range):
        self.type = type
        self.fire_rate = fire_rate
        self.owner = None
        self.projectile_spd = projectile_spd
        self.ideal_range = ideal_range

    def aim_at(target):
        return False
    
    def shoot_at(target):
        return 0

    def get_desirability(dist_to_target):
        return 0
    
    def get_projectile_speed():
        return 0
    
    def num_rounds_remaining():
        return 0
    
    def decrement_num_rounds():
        return 0
    
    def increment_num_rounds():
        return 0
    
    def get_gun_type():
        return ''


class RavenGame: 

    def __init__(self, map, bots, projectiles):
        self.map = map
        self.bots = bots
        # the user may select a bot to control manually. This variable points which one
        self.selected_bot = None
        # this list contains any active projectiles 
        self.projectiles = projectiles

    def update():
        pass

    def is_path_obstructed(vec_a, vec_b, bounding_radius=0):
        return False
    
    def get_all_bots_in_fov(bot):
        return []
    
    def if_second_visible_to_first(first_bot, second_bot):
        return False


class RavenBot:

    def __init__(self, spawn_node):
        self.brain = GoalThink(self)
        self.sensory_memory = SensoryMemory(self, 15.0)
        self.targeting_system = TargetingSystem(self)
        self.weapon_system = WeaponSystem(self, 10, 1, 2)
        self.vision_update_regulator = Regulator(1.0)
        self.target_selection_regulator = Regulator(1.0)
        self.goal_arbitration_regulator = Regulator(1.0)
        self.weapon_selection_regulator = Regulator(1.0)
        self.possessed = False
        self.radius = 5
        self.color = utils.BOT_COLOR
        self.node = spawn_node
        self.position = pygame.Vector2(spawn_node.x, spawn_node.y)

    def update(self):
        self.brain.process()
        self.update_movement()
        if not self.possessed:
            if self.vision_update_regulator.is_ready():
                self.sensory_memory.update_vision()
            if self.target_selection_regulator.is_ready():
                self.targeting_system.update()
            if self.goal_arbitration_regulator.is_ready():
                self.brain.arbitrate()
            if self.weapon_selection_regulator.is_ready():
                self.weapon_system.select_weapon()
            self.weapon_system.take_aim_and_shoot()

    def update_movement(self):
        pass

    def is_possessed(self):
        return self.possessed


class MemoryRecord:
    time_last_sensed: int = 0
    time_became_visible: int = 0
    time_last_visible: int = 0
    last_sensed_position: pygame.Vector2 = pygame.Vector2(0, 0)
    is_within_fov: bool = False
    is_shootable: bool = False
    

class GoalThink:
    def __init__(self, owner):
        self.owner = owner
        self.subgoals = []

    def process(self):
        # Process subgoals and remove completed ones
        while self.subgoals and self.subgoals[0].is_complete():
            self.subgoals.pop(0)
        if self.subgoals:
            self.subgoals[0].process()

    def add_subgoal(self, goal):
        self.subgoals.insert(0, goal)

    def arbitrate(self):
        # Determine the most appropriate goal to pursue
        pass
    

class SensoryMemory:

    def __init__(self, owner, memory_span: float):
        self.owner = owner
        self.memory_map = defaultdict(MemoryRecord)
        self.memory_span = memory_span

    def make_new_record_if_not_already_present(self, bot):
        if bot not in self.memory_map:
            self.memory_map[bot] = MemoryRecord()

    def update_with_sound_source(self, noise_maker):
        self.make_new_record_if_not_already_present(noise_maker)
        record = self.memory_map[noise_maker]
        record.time_last_sensed = pygame.time.get_ticks()
        record.last_sensed_position = noise_maker.position
    
    def update_vision(self):
        bots = self.owner.get_visible_opponents()
        current_time = pygame.time.get_ticks()

        for bot in bots:
            self.make_new_record_if_not_already_present(bot)
            record = self.memory_map[bot]
            record.is_within_fov = True
            record.time_last_sensed = current_time
            record.time_became_visible = current_time
            record.last_sensed_position = bot.position

    def is_opponent_shootable(self, opponent) -> bool:
        self.make_new_record_if_not_already_present(opponent)
        return self.memory_map[opponent].is_shootable
    
    def is_opponent_within_fov(self, opponent) -> bool:
        self.make_new_record_if_not_already_present(opponent)
        return self.memory_map[opponent].is_within_fov
    
    def get_last_recorded_position_of_opponent(self, opponent) -> Optional[pygame.Vector2]:
        self.make_new_record_if_not_already_present(opponent)
        return self.memory_map[opponent].last_sensed_position

    def get_time_opponent_has_been_visible(self, opponent) -> float:
        self.make_new_record_if_not_already_present(opponent)
        return (pygame.time.get_ticks() - self.memory_map[opponent].time_became_visible) / 1000.0

    def get_time_since_last_sensed(self, opponent) -> float:
        self.make_new_record_if_not_already_present(opponent)
        return (pygame.time.get_ticks() - self.memory_map[opponent].time_last_sensed) / 1000.0

    def get_time_opponent_has_been_out_of_view(self, opponent) -> float:
        self.make_new_record_if_not_already_present(opponent)
        return (pygame.time.get_ticks() - self.memory_map[opponent].time_last_visible) / 1000.0

    def get_list_of_recently_sensed_opponents(self):
        bots = []
        current_time = pygame.time.get_ticks()
        for bot, record in self.memory_map.items():
            if (current_time - record.time_last_sensed) / 1000.0 <= self.memory_span:
                bots.append(bot)
        return bots


class TargetingSystem:
    def __init__(self, owner: RavenBot):
        self.owner = owner
        self.current_target = None

    def update(self):
        opponents = self.owner.sensory_memory.get_list_of_recently_sensed_opponents()
        if opponents:
            self.current_target = min(
                opponents,
                key=lambda bot: self.owner.position.distance_to(bot.position)
            )
        else:
            self.current_target = None

    def is_target_present(self) -> bool:
        return self.current_target is not None

    def is_target_within_fov(self) -> bool:
        return (
            self.current_target is not None
            and self.owner.sensory_memory.is_opponent_within_fov(self.current_target)
        )

    def is_target_shootable(self) -> bool:
        return (
            self.current_target is not None
            and self.owner.sensory_memory.is_opponent_shootable(self.current_target)
        )

    def get_last_recorded_position(self) -> pygame.Vector2:
        if self.current_target is None:
            raise ValueError("No target currently assigned")
        return self.owner.sensory_memory.get_last_recorded_position_of_opponent(self.current_target)

    def get_time_target_has_been_visible(self) -> float:
        if self.current_target is None:
            raise ValueError("No target currently assigned")
        return self.owner.sensory_memory.get_time_opponent_has_been_visible(self.current_target)

    def get_time_target_has_been_out_of_view(self) -> float:
        if self.current_target is None:
            raise ValueError("No target currently assigned")
        return self.owner.sensory_memory.get_time_opponent_has_been_out_of_view(self.current_target)

    def get_target(self):
        return self.current_target

    def clear_target(self):
        self.current_target = None


class Weapon:
    def __init__(self, owner, ammo, projectile_speed, damage):
        self.owner = owner
        self.ammo = ammo
        self.projectile_speed = projectile_speed
        self.damage = damage

    def shoot_at(self, target_position):
        if self.ammo > 0:
            self.ammo -= 1
            print(f"Firing at {target_position} with {self.__class__.__name__}")
        else:
            print("Out of ammo!")

    def add_ammo(self, amount=10):
        self.ammo += amount
        print(f"Ammo refilled. Current ammo: {self.ammo}")

    def evaluate_situation(self, target_position):
        distance = self.owner.position.distance_to(target_position)
        return self.damage / (distance + 1)  # Example heuristic


class Blaster(Weapon):
    def __init__(self, owner):
        super().__init__(owner, ammo=50, projectile_speed=300, damage=10)


class Shotgun(Weapon):
    def __init__(self, owner):
        super().__init__(owner, ammo=20, projectile_speed=200, damage=50)

    def shoot_at(self, target_position):
        if self.ammo > 0:
            self.ammo -= 1
            print(f"Shotgun blast at {target_position}. Effective at close range!")
        else:
            print("Out of ammo!")


class RocketLauncher(Weapon):
    def __init__(self, owner):
        super().__init__(owner, ammo=5, projectile_speed=100, damage=100)

    def shoot_at(self, target_position):
        if self.ammo > 0:
            self.ammo -= 1
            print(f"Launching rocket at {target_position}!")
        else:
            print("Out of ammo!")


class WeaponSystem:
    def __init__(self, owner, reaction_time, aim_accuracy, aim_persistence):
        self.owner = owner
        self.weapon_map = {}
        self.current_weapon = None
        self.reaction_time = reaction_time
        self.aim_accuracy = aim_accuracy
        self.aim_persistence = aim_persistence

    def initialize(self):
        blaster = self.create_blaster_weapon()
        self.weapon_map[blaster.type] = blaster
        self.current_weapon = blaster

    def take_aim_and_shoot(self):
        if (self.owner.target_system.is_target_shootable() or
            (self.owner.target_system.get_time_target_has_been_out_of_view() < self.aim_persistence)):
            
            aiming_pos = self.owner.target_system.get_target_bot().position
            
            if self.get_current_weapon().get_type() in ["rocket_launcher", "blaster"]:
                aiming_pos = self.predict_future_position_of_target()
                
                if (self.owner.rotate_facing_toward_position(aiming_pos) and
                    (self.owner.target_system.get_time_target_has_been_visible() > self.reaction_time) and
                    self.owner.world.is_line_of_sight_ok(aiming_pos, self.owner.position)):
                    self.add_noise_to_aim(aiming_pos)
                    self.get_current_weapon().shoot_at(aiming_pos)
            
            else:
                if (self.owner.rotate_facing_toward_position(aiming_pos) and
                    (self.owner.target_system.get_time_target_has_been_visible() > self.reaction_time)):
                    self.add_noise_to_aim(aiming_pos)
                    self.get_current_weapon().shoot_at(aiming_pos)
        else:
            self.owner.rotate_facing_toward_position(self.owner.position + self.owner.heading)


    def select_weapon(self):
        if not self.owner.targeting_system.is_target_present():
            return
        target_position = self.owner.targeting_system.get_last_recorded_position()
        best_weapon = max(
            self.weapon_map.values(),
            key=lambda weapon: weapon.evaluate_situation(target_position)
        )
        self.current_weapon = best_weapon

    def add_weapon(self, weapon_type):
        if weapon_type in self.weapon_map:
            self.weapon_map[weapon_type].add_ammo()
        else:
            new_weapon = self.create_weapon_of_type(weapon_type)
            self.weapon_map[weapon_type] = new_weapon

    def change_weapon(self, weapon_type):
        if weapon_type in self.weapon_map:
            self.current_weapon = self.weapon_map[weapon_type]

    def get_current_weapon(self):
        return self.current_weapon

    def get_weapon_from_inventory(self, weapon_type):
        return self.weapon_map.get(weapon_type)

    def get_ammo_remaining_for_weapon(self, weapon_type):
        weapon = self.get_weapon_from_inventory(weapon_type)
        return weapon.ammo if weapon else 0

    def reaction_time(self):
        return self.reaction_time

    def predict_future_position_of_target(self):
        target_position = self.owner.targeting_system.get_last_recorded_position()
        target_velocity = self.owner.targeting_system.get_target().velocity
        weapon_speed = self.current_weapon.projectile_speed
        time_to_target = self.owner.position.distance_to(target_position) / weapon_speed
        return target_position + target_velocity * time_to_target

    def add_noise_to_aim(self, aiming_position):
        deviation = self.aim_accuracy * (2 * math.random() - 1)
        angle = math.atan2(
            aiming_position.y - self.owner.position.y,
            aiming_position.x - self.owner.position.x
        ) + deviation
        distance = self.owner.position.distance_to(aiming_position)
        return pygame.Vector2(
            self.owner.position.x + math.cos(angle) * distance,
            self.owner.position.y + math.sin(angle) * distance
        )

    def create_blaster_weapon(self):
        return Blaster(self.owner)

    def create_weapon_of_type(self, weapon_type):
        weapon_classes = {0: Blaster, 1: Shotgun, 2: RocketLauncher}
        return weapon_classes[weapon_type](self.owner)


class Regulator:
    def __init__(self, num_updates_per_second_required):
        self.update_period = 1000 / num_updates_per_second_required
        self.next_update_time = pygame.time.get_ticks() + self.update_period

    def is_ready(self):
        current_time = pygame.time.get_ticks()
        if current_time >= self.next_update_time:
            self.next_update_time = current_time + self.update_period
            return True
        return False