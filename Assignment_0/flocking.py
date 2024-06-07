from enum import Enum, auto
import pygame as pg
from pygame.math import Vector2
from vi import Agent, Simulation
from vi.config import Config, dataclass, deserialize
import random


@deserialize
@dataclass
class FlockingConfig(Config):
    # You can change these for different starting weights
    alignment_weight: float = 1.5
    cohesion_weight: float = 0.5
    separation_weight: float = 100.0
    maximum_vel: float = 20
    leader_birds = 10
    to_mouse = 1

    # These should be left as is.
    delta_time: float = 0.5                                   # To learn more https://gafferongames.com/post/integration_basics/ 
    mass: int = 20                                            

    def weights(self) -> tuple[float, float, float]:
        return (self.alignment_weight, self.cohesion_weight, self.separation_weight)

class Bird(Agent):
    config: FlockingConfig

    def Alignment(self, neighbours):
        count = len(neighbours)

        total_v = Vector2(0, 0)
        for boid in neighbours:
            total_v += boid.move
        avg_v = total_v / count
        return avg_v  - self.move
    
    def Cohesion(self, neighbours):
        count = len(neighbours)

        total_p = Vector2(0, 0)
        for boid in neighbours:
            total_p += boid.pos
        avg_p = total_p / count
        
        return avg_p - self.pos
        # return avg_p - self.pos - self.move
    
    def Seperation(self, neighbours):
        count = len(neighbours)

        total_disp = Vector2(0, 0)
        for boid in neighbours:
            boid_pos = self.pos - boid.pos
            boid_pos = boid_pos.normalize() * (boid_pos.length() - 5)**(-2)

            total_disp += boid_pos
        avg_disp = total_disp / count
        return avg_disp
    
    def Force(self):
        neighbours = self.in_proximity_performance().collect_set()

        if len(neighbours) == 0:
            return Vector2(0, 0)

        a = self.Alignment(neighbours)
        s = self.Seperation(neighbours)
        c = self.Cohesion(neighbours)

        a_w, c_w, s_w = self.config.weights()

        total_force = a_w * a + s_w * s + c_w * c
        total_force = total_force / self.config.mass

        return total_force
    
    def maxVel(self):
        max_v = self.config.maximum_vel
        if self.move != Vector2(0, 0):
            self.move = self.move.normalize() * max_v

    def movement_flock(self):
        self.move += self.Force()
        self.maxVel()

    def movement_pos(self, pos):
        move = pos - self.pos
        self.move += move.normalize() * self.config.to_mouse

    def position(self):
        self.pos += self.move * self.config.delta_time

    def change_position(self):
        self.there_is_no_escape()

        self.movement_flock()
        # if self.id < self.config.leader_birds:
        # self.movement_pos(Vector2(pg.mouse.get_pos()))
        self.position()



class Selection(Enum):
    ALIGNMENT = auto()
    COHESION = auto()
    SEPARATION = auto()


class FlockingLive(Simulation):
    selection: Selection = Selection.ALIGNMENT
    config: FlockingConfig

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

        a, c, s = self.config.weights()
        print(f"A: {a:.1f} - C: {c:.1f} - S: {s:.1f}")


(
    FlockingLive(
        FlockingConfig(
            image_rotation=True,
            movement_speed=1,
            radius=50,
            seed=1,
        )
    )
    .batch_spawn_agents(50, Bird, images=["images/bird.png"])
    .run()
)
