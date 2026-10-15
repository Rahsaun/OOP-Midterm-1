"""Simulation logic adapted from the uploaded Zombie Game.

Storage-specific code is deliberately absent from agents and game rules.
"""
from abc import ABC, abstractmethod
import math
import random

from storage import StateStorage


class Agent(ABC):
    """Base class holding shared movement and health state."""

    def __init__(self, x: float, y: float, speed: float, max_health: float = 100.0):
        self.x, self.y = float(x), float(y)
        self.speed = float(speed)
        self.max_health = float(max_health)
        self.health = float(max_health)
        self.alive = True

    def distance_to(self, other: "Agent") -> float:
        return math.hypot(self.x - other.x, self.y - other.y)

    def clamp_position(self, width: float, height: float) -> None:
        self.x = max(0.0, min(self.x, width))
        self.y = max(0.0, min(self.y, height))

    def move_towards(self, other: "Agent", arena: "SimulationPlayground") -> None:
        dx, dy = other.x - self.x, other.y - self.y
        distance = math.hypot(dx, dy)
        if distance:
            self.x += dx / distance * self.speed
            self.y += dy / distance * self.speed
        self.clamp_position(arena.width, arena.height)

    def move_away(self, other: "Agent", arena: "SimulationPlayground") -> None:
        dx, dy = self.x - other.x, self.y - other.y
        distance = math.hypot(dx, dy)
        if distance:
            self.x += dx / distance * self.speed
            self.y += dy / distance * self.speed
        self.clamp_position(arena.width, arena.height)

    def take_damage(self, amount: float) -> None:
        self.health = max(0.0, self.health - amount)
        self.alive = self.health > 0.0

    @abstractmethod
    def update(self, arena: "SimulationPlayground") -> None:
        pass

    def to_state(self) -> dict:
        """Convert an agent into JSON-compatible values, including subtype state."""
        result = {
            "type": type(self).__name__,
            "x": self.x, "y": self.y,
            "speed": self.speed, "health": self.health,
            "max_health": self.max_health, "alive": self.alive,
        }
        if isinstance(self, Human):
            result["perception_radius"] = self.perception_radius
        if isinstance(self, ArmedHuman):
            result.update(
                attack_range=self.attack_range, shot_damage=self.shot_damage,
                cooldown_max=self.cooldown_max, cooldown_timer=self.cooldown_timer,
            )
        if isinstance(self, Zombie):
            result.update(
                bite_range=self.bite_range, bite_damage=self.bite_damage,
                hunt_radius=self.hunt_radius,
            )
        return result


class Human(Agent):
    def __init__(self, x: float, y: float, speed: float = 2.4):
        super().__init__(x, y, speed)
        self.perception_radius = 25.0

    def update(self, arena: "SimulationPlayground") -> None:
        if not self.alive:
            return
        zombie = arena.nearest(self, arena.zombies, self.perception_radius)
        if zombie:
            self.move_away(zombie, arena)
        else:
            self.x += arena.rng.uniform(-1, 1) * self.speed * 0.4
            self.y += arena.rng.uniform(-1, 1) * self.speed * 0.4
            self.clamp_position(arena.width, arena.height)


class ArmedHuman(Human):
    def __init__(self, x: float, y: float, speed: float = 2.1):
        super().__init__(x, y, speed)
        self.attack_range = 35.0
        self.shot_damage = 45.0
        self.cooldown_max = 6
        self.cooldown_timer = 0

    def update(self, arena: "SimulationPlayground") -> None:
        if not self.alive:
            return
        self.cooldown_timer = max(0, self.cooldown_timer - 1)
        zombie = arena.nearest(self, arena.zombies, self.attack_range)
        if zombie and self.cooldown_timer == 0:
            zombie.take_damage(self.shot_damage)
            self.cooldown_timer = self.cooldown_max
        if zombie and self.distance_to(zombie) < self.perception_radius:
            self.move_away(zombie, arena)
        else:
            super().update(arena)


class Zombie(Agent):
    def __init__(self, x: float, y: float, speed: float = 2.1, bite_damage: float = 40.0):
        super().__init__(x, y, speed, max_health=120.0)
        self.bite_range = 3.2
        self.bite_damage = bite_damage
        self.hunt_radius = 120.0

    def update(self, arena: "SimulationPlayground") -> None:
        if not self.alive:
            return
        self.take_damage(0.05)
        if not self.alive:
            return
        human = arena.nearest(self, arena.humans, self.hunt_radius)
        if human:
            if self.distance_to(human) <= self.bite_range:
                human.take_damage(self.bite_damage)
                self.health = min(self.max_health, self.health + 18.0)
                if not human.alive:
                    arena.new_zombies.append(Zombie(human.x, human.y))
            else:
                self.move_towards(human, arena)
        else:
            self.x += arena.rng.uniform(-1, 1) * self.speed
            self.y += arena.rng.uniform(-1, 1) * self.speed
            self.clamp_position(arena.width, arena.height)


AGENT_TYPES = {"Human": Human, "ArmedHuman": ArmedHuman, "Zombie": Zombie}


def agent_from_state(data: dict) -> Agent:
    agent_type = data["type"]
    if agent_type not in AGENT_TYPES:
        raise ValueError(f"Unsupported agent type: {agent_type}")
    agent = AGENT_TYPES[agent_type](data["x"], data["y"], data["speed"])
    for key, value in data.items():
        if key != "type":
            setattr(agent, key, value)
    return agent


class SimulationPlayground:
    """Owns live agents, environment settings and simulation ticks."""

    def __init__(self, width: float = 1200, height: float = 1200, seed: int = 42):
        self.width, self.height = float(width), float(height)
        self.humans: list[Human] = []
        self.zombies: list[Zombie] = []
        self.new_zombies: list[Zombie] = []
        self.tick_count = 0
        self.seed = seed
        self.rng = random.Random(seed)

    def populate(self, regular: int, armed: int, zombies: int) -> None:
        for _ in range(regular):
            self.humans.append(Human(self.rng.uniform(0, self.width), self.rng.uniform(0, self.height)))
        for _ in range(armed):
            self.humans.append(ArmedHuman(self.rng.uniform(0, self.width), self.rng.uniform(0, self.height)))
        for _ in range(zombies):
            self.zombies.append(Zombie(self.rng.uniform(0, self.width), self.rng.uniform(0, self.height)))

    @staticmethod
    def nearest(source: Agent, targets: list[Agent], radius: float):
        closest, distance = None, radius
        for agent in targets:
            if agent.alive and (d := source.distance_to(agent)) < distance:
                closest, distance = agent, d
        return closest

    def step(self) -> None:
        self.tick_count += 1
        self.new_zombies.clear()
        for human in self.humans:
            human.update(self)
        for zombie in self.zombies:
            zombie.update(self)
        self.zombies.extend(self.new_zombies)
        self.humans = [h for h in self.humans if h.alive]
        self.zombies = [z for z in self.zombies if z.alive]

    def to_state(self) -> dict:
        return {
            "version": 1,
            "environment": {"width": self.width, "height": self.height},
            "runtime": {"tick_count": self.tick_count, "seed": self.seed},
            "agents": {
                "humans": [human.to_state() for human in self.humans],
                "zombies": [zombie.to_state() for zombie in self.zombies],
            },
        }

    @classmethod
    def from_state(cls, state: dict) -> "SimulationPlayground":
        if state.get("version") != 1:
            raise ValueError("Unsupported snapshot version")
        environment, runtime, agents = state["environment"], state["runtime"], state["agents"]
        arena = cls(environment["width"], environment["height"], runtime["seed"])
        arena.tick_count = runtime["tick_count"]
        arena.humans = [agent_from_state(data) for data in agents["humans"]]
        arena.zombies = [agent_from_state(data) for data in agents["zombies"]]
        return arena


class SimulationController:
    """Coordinates saving/loading through an abstract storage contract."""

    def __init__(self, storage: StateStorage, simulation: SimulationPlayground | None = None):
        self.storage = storage
        self.simulation = simulation or SimulationPlayground()

    def save(self) -> None:
        self.storage.save_state(self.simulation.to_state())

    def load(self) -> bool:
        state = self.storage.load_state()
        if state is None:
            return False
        self.simulation = SimulationPlayground.from_state(state)
        return True

    def run(self, ticks: int) -> None:
        for _ in range(ticks):
            self.simulation.step()
