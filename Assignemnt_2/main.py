from FMS import FMSPriority
from random import uniform, randrange
from enum import Enum, auto
import pygame as pg
from pygame.math import Vector2
from vi import Agent, Simulation
from vi.config import Config, dataclass, deserialize
from math import cos, radians

LEO_COUNT = 10
MAX_NUM = 10 ** 9
SHEEP_COUNT = 100

# Leopard
@deserialize
@dataclass
class FMSConfig(Config):
    direction_change: int = 100

    leo_speed_wander: float = 2.0
    leo_hunt_speed: float = 4.0

    sheep_speed_wander: float = 1.0
    sheep_hunt_speed: float = 2.0
    sheep_run_speed: float = 6.0
    sheep_acceleration: float = 0.5

    leo_vision_field: float = cos(radians(100))
    # sheep_vision_field: float = cos(radians(145))
    sheep_vision_field: float = -100

    leo_nat_death: float = (10000) ** -1
    leo_rot_timer: int = 1000
    leo_hunt_timer: int = 100
    leo_stealth: float = 0.01
    leo_eat_speed: float = 0.4

    leo_still_weight: float = 0.0001
    leo_walk_weight: float = 0.001

    leo_hungry: float = 0.70
    sheep_hungry: float = 0.70

    leo_full: float = 0.95
    sheep_full: float = 0.95

    sheep_nat_death: float = (10000) ** -1
    sheep_rot_timer: int = 1000
    sheep_run_timer: int = 100
    sheep_eat_timer: int = 3

    sheep_still_weight: float = 0.0001
    sheep_walk_weight: float = 0.001
    sheep_eat_weight: float = 0.04

    grass_still_weight: float = 0.00001

    join_t_max: int = 30

def leo_see_sheep(leo, sheep):
    v1 = leo.move
    v2 = sheep.pos - leo.pos
    if v1.length() == 0:
        return False
    leo_sheep_cos = v1.dot(v2) / v1.length() / v2.length()
    return leo_sheep_cos > leo.config.leo_vision_field


def sheep_see_leo(sheep, leo):
    v1 = sheep.move
    v2 = leo.pos - sheep.pos
    if v1.length() == 0:
        return False
    sheep_leo_cos = v1.dot(v2) / v1.length() / v2.length()
    return sheep_leo_cos > sheep.config.sheep_vision_field

class LeoAction():
    def __init__(self, config = FMSConfig()):
        self.config = config
class WanderLeo():
    pass
class HuntLeo():
    pass
class DieLeo():
    pass
class EatLeo():
    pass
class DieLeo():
    pass
class Sheep(Agent):
    pass
class Leopard(Agent):
    pass
class WanderSheep():
    pass
class RunSheep():
    pass
class HuntSheep():
    pass
class EatSheep():
    pass
class DieSheep():
    pass
class Grass(Agent):
    pass

class WanderLeo(LeoAction):
    def do(self, ag):
        global MAX_NUM
        if ag.timer % self.config.direction_change == 0:
            ag.timer = ag.timer % MAX_NUM
            ag.move = Vector2(uniform(-1, 1), uniform(-1, 1)).normalize() * config.leo_speed_wander * uniform(0, (1 - ag.E))
        return

    def switch(self, ag):
        return

    def prob(self, ag):
        prey = ag.in_proximity_accuracy().without_distance().filter_kind(Sheep).filter(lambda sheep: type(sheep.current_action) == DieSheep).first()
        if prey is None:
            prey = ag.in_proximity_accuracy().without_distance().filter_kind(Sheep).filter(lambda sheep: leo_see_sheep(ag, sheep)).first()
        ag.current_prey = prey
        hunt_p = [HuntLeo(), 0]
        if prey is not None:
            hungry = ag.E < self.config.leo_hungry
            hunt_p = [HuntLeo(), int(hungry) * 0.99]
        nat_death_p = [DieLeo(), self.config.leo_nat_death]
        wander_p = [WanderLeo(), 1.0]

        return [nat_death_p, hunt_p, wander_p]

class HuntLeo(LeoAction):
    def do(self, ag):
        prey_move = ag.current_prey.pos - ag.pos
        prey_move = prey_move.normalize() * config.leo_hunt_speed
        ag.move = prey_move

    def switch(self, ag):
        ag.leo_hunt_timer = config.leo_hunt_timer

    def prob(self, ag):
        nat_death_p = [DieLeo(), self.config.leo_nat_death]
        eat_p = [EatLeo(), int((ag.pos - ag.current_prey.pos).length() <= 5)]
        hunt_p = [HuntLeo(), ag.leo_hunt_timer > 0]
        wander_p = [WanderLeo(), 1.0]

        return [nat_death_p, eat_p, hunt_p, wander_p]



class EatLeo(LeoAction):
    def do(self, ag: Leopard):
        ag.current_prey.current_action = DieSheep()
        ag.move = Vector2(0, 0)
        change_E = min(config.leo_eat_speed, ag.current_prey.E)
        ag.E = min(ag.E + change_E, 1.0)
        ag.current_prey.E -= change_E

    def switch(self, ag):
        pass

    def prob(self, ag):
        full = ag.E > self.config.leo_full
        prey_nutritional = ag.current_prey is not None and ag.current_prey.E > 0
        nat_death_p = [DieLeo(), self.config.leo_nat_death]
        eat_p = [EatLeo(), int(prey_nutritional and not full)]
        wander_p = [WanderLeo(), 1]

        return [nat_death_p, eat_p, wander_p]

class DieLeo(LeoAction):
    def do(self, ag):
        ag.change_image(1)
        ag.move = Vector2(0, 0)
        ag.death_timer -= 1
        if ag.death_timer == 0:
            ag.kill()
    
    def switch(self, ag):
        return
    
    def prob(self, ag):
        return [[DieLeo(), 1]]


class Leopard(Agent, FMSPriority):
    config = FMSConfig()
    current_action = WanderLeo()
    E: float = 1.0
    timer: int = 0

    death_timer = config.leo_rot_timer
    leo_hunt_timer = config.leo_hunt_timer
        
    current_prey = None

    def change_position(self):
        self.there_is_no_escape()
        self.do()
        self.pos += self.move
        self.E = self.E - self.config.leo_still_weight - self.config.leo_walk_weight * self.move.length()
        self.timer += 1
        if self.E < 0:
            self.kill()

# Sheep

class SheepAction():
    def __init__(self, config = FMSConfig()):
        self.config = config

class JoinGrassSiteSheep(SheepAction):
    def do(self, ag):
        ag.move = ag.move.normalize() * self.config.sheep_hunt_speed
        ag.join_timer -= 1
    
    def switch(self, ag):
        ag.join_timer = randrange(self.config.join_t_max)
    
    def prob(self, ag):
        nat_death_p = [DieSheep(), self.config.sheep_nat_death]
        hunter = ag.in_proximity_accuracy().without_distance().filter_kind(Leopard).first()
        run_p = [RunSheep(), 0]
        if hunter is not None:
            run_p = [RunSheep(), hunter.config.leo_stealth]
        join_p = [JoinGrassSiteSheep(), int(ag.join_timer == 0)]
        eat_p = [EatSheep(), 1]
        return [nat_death_p, run_p, join_p, eat_p]

class WanderSheep(SheepAction):
    def do(self, ag):
        global MAX_NUM
        if ag.timer % self.config.direction_change == 0:
            ag.timer = ag.timer % MAX_NUM
            ag.move = Vector2(uniform(-1, 1), uniform(-1, 1)).normalize() * self.config.sheep_speed_wander * uniform(0, (1 - ag.E) ** 2)
        return

    def switch(self, ag):
        return

    def prob(self, ag):
        hunter = ag.in_proximity_accuracy().without_distance().filter_kind(Leopard).filter(lambda leo: sheep_see_leo(ag, leo)).first()
        grass = ag.in_proximity_accuracy().without_distance().filter_kind(Grass).first()
        ag.current_prey = grass
        ag.current_hunter = hunter
        run_p = [RunSheep(), 0]
        if hunter is not None:
            run_p = [RunSheep(), hunter.config.leo_stealth]
        hunt_p = [JoinGrassSiteSheep(), int(ag.E < self.config.sheep_hungry) * int(grass is not None) * 0.99]
        nat_death_p = [DieSheep(), self.config.sheep_nat_death]
        wander_p = [WanderSheep(), 1.0]

        return [nat_death_p, run_p, hunt_p, wander_p]

class RunSheep(SheepAction):
    def do(self, ag):
        hunter = ag.in_proximity_accuracy().without_distance().filter_kind(Leopard).first()
        if hunter is not None:
            # ag.move = (ag.current_hunter.pos - ag.pos).normalize() * (self.config.sheep_run_speed * (-1))
            l = ag.move.length()
            if l == 0:
                ag.move = Vector2(uniform(-1, 1), uniform(-1, 1)).normalize() * self.config.sheep_run_speed * 0.1
            else:
                ag.move = ag.move.normalize() * min(l + self.config.sheep_acceleration, self.config.sheep_run_speed)
        else:
            ag.run_timer -= 1

    def switch(self, ag):
        ag.run_timer = self.config.sheep_run_timer

    def prob(self, ag):
        nat_death_p = [DieSheep(), self.config.sheep_nat_death]
        hunter = ag.in_proximity_accuracy().without_distance().filter_kind(Leopard).first()
        run_p = [RunSheep(), 0]
        if hunter is not None:
            run_p = [RunSheep(), hunter.config.leo_stealth]
        run_p = [RunSheep(), int(hunter is not None and ag.run_timer != 0)]
        wander_p = [WanderSheep(), 1]

        return [nat_death_p, run_p, wander_p]

# class HuntSheep(SheepAction):
#     def do(self, ag):
#         prey_move = ag.current_prey.pos - ag.pos
#         prey_move = prey_move.normalize() * config.sheep_hunt_speed
#         ag.move = prey_move

#     def switch(self, ag):
#         pass

#     def prob(self, ag):
#         nat_death_p = [DieSheep(), self.config.sheep_nat_death]
#         eat_p = [EatSheep(), int((ag.pos - ag.current_prey.pos).length() <= 5)]
#         hunter = ag.in_proximity_accuracy().without_distance().filter_kind(Leopard).first()
#         run_p = [RunSheep(), 0]
#         if hunter is not None:
#             run_p = [RunSheep(), hunter.config.leo_stealth]
#         hunt_p = [HuntSheep(), 1.0]
#         wander_p = [WanderSheep(), 1.0]

#         return [nat_death_p, run_p, eat_p, hunt_p, wander_p]

class EatSheep(SheepAction):
    def do(self, ag):
        ag.move = Vector2(0, 0)
        change_E = min(config.sheep_eat_weight, ag.current_prey.E)
        ag.E += change_E
        ag.current_prey.E -= change_E

    def switch(self, ag):
        pass

    def prob(self, ag):
        full = ag.E > self.config.sheep_full
        prey_nutritional = ag.current_prey is not None and ag.current_prey.E > 0
        nat_death_p = [DieSheep(), self.config.sheep_nat_death]
        hunter = ag.in_proximity_accuracy().without_distance().filter_kind(Leopard).first()
        run_p = [RunSheep(), 0]
        if hunter is not None:
            run_p = [RunSheep(), hunter.config.leo_stealth]
        eat_p = [EatSheep(), int(not full and prey_nutritional)]
        wander_p = [WanderSheep(), 1]

        return [nat_death_p, run_p, eat_p, wander_p]

class DieSheep(DieLeo):
    def do(self, ag):
        ag.change_image(1)
        ag.move = Vector2(0, 0)
        ag.death_timer -= 1
        if ag.death_timer == 0:
            ag.kill()
    
    def switch(self, ag):
        return
    
    def prob(self, ag):
        return [[DieSheep(), 1]]


class Sheep(Agent, FMSPriority):
    config = FMSConfig()
    current_action = WanderSheep()
    E: float = 1.0
    timer: int = 0
    join_timer: int = randrange(config.join_t_max)

    death_timer = config.sheep_rot_timer
    run_timer = config.sheep_run_timer
        
    current_prey = None

    def change_position(self):
        self.there_is_no_escape()
        self.do()
        self.pos += self.move
        self.E = self.E - self.config.sheep_still_weight - self.config.sheep_walk_weight * self.move.length()
        self.timer += 1
        if self.E < 0:
            self.kill()

#Grass

class Grass(Agent):
    config: FMSConfig
    E: float = 10.0
    disp: float = 50.0

    def change_position(self):
        self.there_is_no_escape()
        self.E -= self.config.grass_still_weight
        if self.E <= 0:
            self.E = 10.0
            self.move = Vector2(uniform(-1, 1), uniform(-1, 1)).normalize() * self.disp
            self.pos += self.move

class FMSLive(Simulation):
    tmp: int

config = FMSConfig(
            image_rotation=True,
            movement_speed=1,
            radius=100,
            seed=1,
        )
(
    FMSLive(
        config
    )
    # .spawn_site("images/circle2.png", config.window.as_tuple()[0] / 4, config.window.as_tuple()[0] / 4)
    # .spawn_site("images/site1.png", config.window.as_tuple()[0] / 4 * 3, config.window.as_tuple()[0] / 4)
    .batch_spawn_agents(5, Grass, images=['images/green_circle.png'])
    .batch_spawn_agents(20, Sheep, images=['images/sheep.png', 'images/dead_sheep.png'])
    .batch_spawn_agents(1, Leopard, images=["images/snowleopard .png", "images/dead_snowleopard.png"])
    .run()
)