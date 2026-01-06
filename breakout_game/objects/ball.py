import pygame

from .sprite import Sprite
from ..config import BALL
from ..utils import clamp


class Ball(Sprite):

    def __init__(self, rect: pygame.Rect, vel: tuple[float, float]):

        super().__init__(rect)
        self.vx, self.vy = vel
        self.can_hit_brick = True

    def speed_cap(self) -> None:

        self.vx = clamp(self.vx, -BALL.max_speed, BALL.max_speed)
        self.vy = clamp(self.vy, -BALL.max_speed, BALL.max_speed)

    def update(self, **kwargs) -> None:

        self.rect.x += int(self.vx)
        self.rect.y += int(self.vy)

    def draw(self, surface: pygame.Surface, *, image=None, **kwargs) -> None:

        if image:
            surface.blit(image, self.rect)
        else:
            pygame.draw.ellipse(surface, (227, 11, 126), self.rect)