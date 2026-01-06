from dataclasses import dataclass
from .objects.bricks import Brick


@dataclass
class Scoring:
    
    score: int = 0

    def add_for_brick_destroyed(self, brick: Brick) -> None:
        self.score += brick.points