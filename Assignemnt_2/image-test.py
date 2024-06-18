import random
import pygame as pg
from pygame.math import Vector2
from vi import Agent, Simulation
from vi.config import Config, dataclass, deserialize

# Number of agents
NUM_SNOW_LEOPARDS = 20
NUM_SHEEP = 50
GRASS_PATCHES = 30

@dataclass
class MyConfig(Config):
    speed: float = 1.0  # Reduced speed for slower movement
    D: int = 100
    alive_image_interval: int = 100  # Interval for switching images
    dead_probability: float = 0.01  # Probability to switch to dead image

# Function to make agents move randomly
def random_movement(agent):
    movement = Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize() * agent.config.speed
    agent.move = movement
    agent.pos += agent.move

class SnowLeopard(Agent):
    config: MyConfig
    
    def update(self, frame_count):
        random_movement(self)
        # Switch images based on probability and interval
        if frame_count % self.config.alive_image_interval == 0:
            if random.random() < self.config.dead_probability:
                self.change_image(1)  # Switch to dead image
            else:
                self.change_image(0)  # Switch to alive image

class Sheep(Agent):
    config: MyConfig
    
    def update(self, frame_count):
        random_movement(self)
        # Switch images based on probability and interval
        if frame_count % self.config.alive_image_interval == 0:
            if random.random() < self.config.dead_probability:
                self.change_image(1)  # Switch to dead image
            else:
                self.change_image(0)  # Switch to alive image

class Grass(Agent):
    config: MyConfig

class CustomSimulation(Simulation):
    def __init__(self, config: MyConfig):
        super().__init__(config)
        self.frame_count = 0

    def before_update(self):
        self.frame_count += 1

    def tick(self):
        super().tick()
        for agent in self._all.sprites():
            if isinstance(agent, (SnowLeopard, Sheep)):
                agent.update(self.frame_count)

def run_simulation():
    config = MyConfig(
        image_rotation=True,
        movement_speed=0.5,  # Slower movement
        radius=50,
        seed=1,
    )
    
    simulation = (
        CustomSimulation(config)
        .batch_spawn_agents(NUM_SNOW_LEOPARDS, SnowLeopard, images=["images/snowleopard.png", "images/dead_snowleopard.png"])
        .batch_spawn_agents(NUM_SHEEP, Sheep, images=["images/sheep.png", "images/dead_sheep.png"])
    )
    
    # Randomly place grass on the screen
    for _ in range(GRASS_PATCHES):  # Number of grass patches
        x = random.randint(0, config.window.width)
        y = random.randint(0, config.window.height)
        simulation.spawn_agent(Grass, images=["images/grass.png"]).pos = Vector2(x, y)
    
    simulation.run()

if __name__ == "__main__":
    run_simulation()
