from enum import Enum, auto
import pygame as pg
from pygame.math import Vector2
from vi import Agent, Simulation
from vi.config import Config, dataclass, deserialize
import random

RADIUS = 200

@deserialize
@dataclass
class FMSConfig(Config):
    speed: float = 15.0
    p_join: float = 0.8
    p_leave: float = 0.4
    t_join: float = RADIUS / speed
    t_leave: float = RADIUS * 2
    
class Cockroach(Agent):
    config: FMSConfig
    
    def change_position(self):
        self.there_is_no_escape()
        movement = Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize() * self.config.speed
        self.move = movement
        self.pos += self.move

class Selection(Enum):
    SPEED = auto()
    COHESION = auto()
    SEPARATION = auto()

class FMSLive(Simulation):
    selection: Selection = Selection.ALIGNMENT
    config: FMSConfig

    def handle_event(self, by: float):
        if self.selection == Selection.ALIGNMENT:
            self.config.alignment_weight += by
        elif self.selection == Selection.COHESION:
            self.config.cohesion_weight += by
        elif self.selection == Selection.SEPARATION:
            self.config.separation_weight += by
        

    def before_update(self):
        super().before_update()

        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_UP:
                    self.handle_event(by=0.1)
                elif event.key == pg.K_DOWN:
                    self.handle_event(by=-0.1)
                elif event.key == pg.K_1:
                    self.selection = Selection.ALIGNMENT
                elif event.key == pg.K_2:
                    self.selection = Selection.COHESION
                elif event.key == pg.K_3:
                    self.selection = Selection.SEPARATION

(
    FMSLive(
        FMSConfig(
            image_rotation=True,
            movement_speed=1,
            radius=RADIUS,
            seed=1,
        )
    )
    .batch_spawn_agents(50, Cockroach, images=["images/green.png"])
    .run()
)
