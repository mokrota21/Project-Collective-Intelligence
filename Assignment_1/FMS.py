from enum import Enum, auto
import pygame as pg
from pygame.math import Vector2
from vi import Agent, Simulation
from vi.config import Config, dataclass, deserialize
import random

COUNT = 100

@deserialize
@dataclass
class FMSConfig(Config):
    speed: float = 30.0
    p_join: float = 1.0
    p_leave: float = 1 / COUNT
    D: int = 100

def wander(self):
        if self.on_site_id() is not None:
            self.enter_site = Vector2(self.pos.x, self.pos.y)
            self.escape_site = None
            self.current = "Join"
            return

        movement = Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize() * self.config.speed
        self.move = movement
        self.pos += self.move
    
def join(self):
        if self.escape_site is not None:
            self.randomize_site()
            self.still_i = 0
            self.current = "Still"
            return

        self.move = self.move.normalize() * self.config.speed
        self.pos += self.move
        self.join_t += 1
        if not self.on_site():
            self.escape_site = self.pos - self.move

def still(self):
    leave = False
    if self.still_i % self.config.D == 0:
        leave = random.uniform(0.0, 1.0) < self.leave_prob()

    if leave:
        self.continue_movement()
        self.current = "Leave"
        return

def leave(self):
    if self.join_t == 0:
        self.current = "Wander"
        return
    
    self.move = self.move.normalize() * self.config.speed
    self.pos += self.move
    self.join_t -= 1
    

class Cockroach(Agent):
    config: FMSConfig
    in_site: bool = False
    last_site = None
    current = "Wander"
    functions = {"Wander": wander, "Join": join, "Still": still, "Leave": leave}
    join_t = 0
    still_i = 0
    enter_site = None
    escape_site = None

    def leave_prob(self):
        return self.in_proximity_performance().count() * self.config.p_leave

    def randomize_site(self):
        pos_v = self.escape_site - self.enter_site
        rand_l = random.uniform(0, pos_v.length())
        # rand_l = pos_v.length() / 2
        if pos_v.length()  != 0:
            rand_vector = pos_v.normalize() * rand_l
            # print(rand_vector, self.enter_site)
            self.pos = self.enter_site + rand_vector
        self.freeze_movement()

    def change_position(self):
        self.there_is_no_escape()

        self.functions[self.current](self)

        # self.move = Vector2(pg.mouse.get_pos()[0], pg.mouse.get_pos()[1]) - self.pos
        # self.pos += self.move
        # print(self.on_site_id())

        

class Selection(Enum):
    SPEED = auto()
    COHESION = auto()
    SEPARATION = auto()

class FMSLive(Simulation):
    tmp: int

config = FMSConfig(
            image_rotation=True,
            movement_speed=1,
            radius=50,
            seed=1,
        )
(
    FMSLive(
        config
    )
    .spawn_site("images/site1.png", config.window.as_tuple()[0] / 2, config.window.as_tuple()[0] / 2)
    .batch_spawn_agents(COUNT, Cockroach, images=["images/red.png"])
    .run()
)
