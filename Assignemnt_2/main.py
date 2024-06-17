from FMS import FMSPriority
from random import uniform
from enum import Enum, auto
import pygame as pg
from pygame.math import Vector2
from vi import Agent, Simulation
from vi.config import Config, dataclass, deserialize

LEO_COUNT = 10

# Leopard
@deserialize
@dataclass
class LeopardConfig(Config):
    speed_wander: float = 1.0
    nat_death: float = (10000) ** -1
    rot_timer: int = 1000
    hunt_timer: int = 100
    hunt_speed: float = 3.0
    eat_timer: int = 3

    still_weight: float = 0.01
    walk_weight: float = 0.01
    eat_weight: float = 0.4

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


class WanderLeo():
    def __init__(self, config):
        self.config = config

    def do(ag):
        # print((1 - ag.E) ** 2)
        ag.move = Vector2(uniform(-1, 1), uniform(-1, 1)).normalize() * config.speed_wander * uniform(0, (1 - ag.E) ** 2)
        ag.E = ag.E - config.still_weight - config.walk_weight
        if ag.E < 0:
            ag.E = 0
        return

    def switch(ag):
        return

    def prob(ag):
        prey = ag.in_proximity_accuracy().without_distance().filter_kind(Sheep).first()
        ag.current_prey = prey
        hunt_p = [HuntLeo, int(prey is not None) * 0.99]
        nat_death_p = [DieLeo, max(config.nat_death, int(ag.E == 0))]
        wander_p = [WanderLeo, 1.0]

        print(nat_death_p)

        return [nat_death_p, hunt_p, wander_p]

class HuntLeo():
    def __init__(self, config):
        self.config = config

    def do(ag):
        prey_move = ag.current_prey.pos - ag.pos
        prey_move = prey_move.normalize() * config.hunt_speed
        ag.move = prey_dir
        ag.E -= config.still_weight + config.walk_weight

    def switch(ag):
        ag.hunt_timer = config.hunt_timer

    def prob(ag):
        nat_death_p = [DieLeo, max(config.nat_death, ag.E == 0)]
        hunt_p = [HuntLeo, ag.hunt_timer > 0]
        wander_p = [WanderLeo, 1.0]

        return [nat_death_p, hunt_p, wander_p]

class EatLeo():
    def __init__(self, config):
        self.config = config

    def do(self, ag):
        ag.move = 0
        ag.E += config.eat_gain / config.eat_timer
        ag.eat_timer -= 1

    def switch(self, ag):
        ag.eat_timer = config.eat_timer

    def prob(self, ag):
        nat_death_p = [DieLeo, max(config.nat_death, ag.E == 0)]
        eat_p = [EatLeo, ag.eat_timer == 0]
        wander_p = [WanderLeo, 1]

        return [nat_death_p, eat_p, wander_p]

class DieLeo():
    def do(self, ag):
        ag.move = 0
        ag.rot_timer -= 1
        if ag.death_timer == 0:
            ag.kill()
    
    def switch(self, ag):
        return
    
    def prob(self, ag):
        return


class Leopard(Agent, FMSPriority):
    config = LeopardConfig()
    current_action = WanderLeo
    E: float = 1.0

    eat_timer = config.eat_timer
    death_timer = config.rot_timer
    hunt_timer = config.hunt_timer
        
    current_prey = None


    def manage_E(self):
        if self.current_action != Eat:
            E -= config.still_weight
        else:
            E += eat_weight
        self.E -= config.walk_weight * self.move

    def change_position(self):
        # print(self.E, self.current_action)
        # self.there_is_no_escape()
        self.do()
        self.pos += self.move

# Sheep
# @deserialize
# @dataclass
# class SheepConfig(Config):
#     speed_wander: float = 10.0
#     nat_death: float = (10000) ** -1
#     eaten_timer: int = 3

# def die_hunted(ag):
#     ag.move = 0
#     ag.eaten_timer -= 1
#     if ag.eaten_timer == 0:
#         ag.kill()

# class Sheep(Agent, FMSPriority):
#     config: SheepConfig
#     eaten_timer = config.eaten_timer


class FMSLive(Simulation):
    tmp: int

config = LeopardConfig(
            image_rotation=True,
            movement_speed=1,
            radius=50,
            seed=1,
        )
(
    FMSLive(
        config
    )
    # .spawn_site("images/circle2.png", config.window.as_tuple()[0] / 4, config.window.as_tuple()[0] / 4)
    # .spawn_site("images/site1.png", config.window.as_tuple()[0] / 4 * 3, config.window.as_tuple()[0] / 4)
    .batch_spawn_agents(LEO_COUNT, Leopard, images=["images/red.png"])
    .run()
)