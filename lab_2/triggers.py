import pygame
import math
from abc import ABC, abstractmethod


class TriggerSystem():
    
    def __init__(self, trigger_list):
        self.trigger_list = trigger_list

    def update_triggers(self):
        # iterate through triggers
        for trigger in self.trigger_list:
            if trigger.set_to_be_removed_from_game():
                self.trigger_list.remove(trigger)
            else:
                trigger.update()
    
    def try_triggers(entities):
        for entity in entities:
            if entity.is_ready_for_trigger_update and entity.is_alive:
                for trigger in entity.triggers:
                    trigger.try_trigger(entity)

    def clear(self):
        self.trigger_list = []

    # This method should be called each update step of the game.
    #  It will first update the internal state of the triggers and
    #  then try each entity against each active trigger to test
    #  if any should be triggered.
    def update(self, entities):
        self.update_triggers()
        self.try_triggers(entities)

    def get_triggers_list(self):
        return self.trigger_list
    
    def render():
        pass


class Trigger(ABC):

    def __init__(self, id):
        self.id = id
        self.region_of_influence = None
        self.remove_from_game = False
        self.active = True
        self.graph_node_index = -1  # Default to an invalid index

    def set_graph_node_index(self, idx):
        self.graph_node_index = idx

    def set_to_be_removed_from_game(self):
        self.remove_from_game = True

    def set_inactive(self):
        self.active = False

    def set_active(self):
        self.active = True
    
    def is_touching_trigger(self, entity_pos, entity_radius):
        """
        Checks if an entity is overlapping the trigger's region.
        """
        if self.region_of_influence:
            return self.region_of_influence.is_touching(entity_pos, entity_radius)
        return False

    def add_circular_trigger_region(self, center, radius):
        self.region_of_influence = TriggerRegionCircle(center, radius)

    def add_rectangular_trigger_region(self, top_left, bottom_right):
        self.region_of_influence = TriggerRegionRectangle(top_left, bottom_right)

    # Abstract methods
    @abstractmethod
    def try_trigger(self, entity):
        """
        Determines if the trigger should activate for the given entity.
        """
        pass

    @abstractmethod
    def update(self):
        """
        Updates the internal state of the trigger.
        """
        pass

    # Public methods
    def graph_node_index(self):
        return self.graph_node_index

    def is_to_be_removed(self):
        return self.remove_from_game

    def is_active(self):
        return self.active


class TriggerRegion(ABC):

    @abstractmethod
    def is_touching(entity_pos, entity_radius):
        pass


class TriggerRegionCircle(TriggerRegion):

    def __init__(self, position, radius):
        super().__init__()
        self.position = position
        self.radius = radius

    def is_touching(self, entity_pos, entity_radius):
        return pygame.Vector2.distance_squared_to(
            self.position, entity_pos) < (entity_radius + self.radius) ** 2


class TriggerRegionRectangle(TriggerRegion):

    def __init__(self, top_left, w, h):
        super().__init__()
        self.top_left = top_left
        self.w = w
        self.h = h

    def is_touching(self, entity_pos, entity_radius):
        x, y = entity_pos
        rect_x, rect_y = self.top_left
        rect_right = rect_x + self.w
        rect_bottom = rect_y + self.h

        closest_x = max(rect_x, min(x, rect_right))
        closest_y = max(rect_y, min(y, rect_bottom))
        dx = closest_x - x
        dy = closest_y - y
        distance = math.sqrt(dx**2 + dy**2)
        return distance <= entity_radius
    

class TriggerRespawning(Trigger):

    def __init__(self, id, respawn_delay):
        super().__init__(id)
        self.respawn_delay = respawn_delay
        self.updates_remaining_to_respawn = 0

    @abstractmethod
    def try_trigger(self, entity):
        """
        Determines if the trigger should activate for the given entity.
        Must be implemented by subclasses.
        """
        raise NotImplementedError("This method should be implemented by a subclass.")
    
    def update(self):
        """
        Updates the trigger's state. Respawns the trigger if it's inactive and the delay is over.
        """
        if self.updates_remaining_to_respawn > 0:
            self.updates_remaining_to_respawn -= 1

        if self.updates_remaining_to_respawn <= 0 and not self.active:
            self.set_active()

    def set_respawn_delay(self, num_ticks):
        """
        Sets the number of ticks required before the trigger can respawn.
        :param num_ticks: Number of ticks before respawn.
        """
        self.respawn_delay = num_ticks
        self.num_updates_remaining_until_respawn = num_ticks

    def deactivate(self):
        self.set_inactive()
        self.updates_remaining_to_respawn = self.respawn_delay


class TriggerWeaponGiver(TriggerRespawning):

    def __init__(self, id, respawn_delay, datafile):
        super().__init__(id, respawn_delay)
        self.datafile = datafile

    def try_trigger(self, bot):
        if self.is_active() and self.is_touching_trigger(bot.position, bot.radius):
            bot.pickup_weapon()
            self.deactivate()
    
    def render():
        pass


class TriggerHealthGiver(TriggerRespawning):

    def __init__(self, id, respawn_delay, hp_amount, datafile):
        super().__init__(id, respawn_delay)
        self.hp_amount = hp_amount
        self.datafile = datafile
    
    def try_trigger(self, bot):
        if self.is_active() and self.is_touching_trigger(bot.position, bot.radius):
            bot.increase_hp(self.hp_amount)
            self.deactivate()
    
    def render():
        pass


class TriggerLimitedLifetime(Trigger):

    def __init__(self, id, lifetime):
        super().__init__(id)
        self.lifetime = lifetime

    @abstractmethod
    def try_trigger(self, entity):
        """
        Determines if the trigger should activate for the given entity.
        Must be implemented by subclasses.
        """
        raise NotImplementedError("This method should be implemented by a subclass.")

    def update(self):
        if (self.lifetime - 1) <= 0:
            self.set_to_be_removed_from_game()


class TriggerSoundNotify(TriggerLimitedLifetime):

    def __init__(self, id, lifetime, source_bot, range):
        super().__init__(id, lifetime)
        self.source_bot = source_bot
        self.range = range

    def try_trigger(self, bot):
        if self.is_touching_trigger(bot.position, bot.radius):
            # implement sending signal to bots in radius
            pass

    
