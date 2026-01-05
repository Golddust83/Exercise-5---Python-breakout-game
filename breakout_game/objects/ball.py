from .sprite import Sprite
from ..config import BALL
from ..utils import clamp


class Ball(Sprite):

    def __init__(self, rect, vel):
        self.rect = rect
        self.vx, self.vy = vel
        self.can_hit_brick = True

    def speed_cap(self):

        self.vx = clamp(self.vx, -BALL.max_speed, BALL.max_speed)
        self.vy = clamp(self.vy, -BALL.max_speed, BALL.max_speed)

    def update(self):
        
        self.rect.x += int(self.vx)
        self.rect.y += int(self.vy)