from .config import SCREEN, BALL, RULES
from .utils import clamp, reflect_ball_on_rect
from .objects.ball import Ball
from .objects.bat import Bat
from .objects.bricks import Brick


class CollisionSystem:

    """
    Game delegates collision handling to this class.
    """    
    def __init__(self, bounce_sound = None, brick_hit_sound = None):
        self.bounce_sound = bounce_sound
        self.brick_hit_sound = brick_hit_sound

    def _play(self, sound):
        if sound:
            sound.play()

    def handle_walls_and_bottom(self, ball: Ball) -> bool:

        if ball.rect.left <= 0:
            ball.rect.left = 0
            ball.vx = abs(ball.vx)
            self._play(self.bounce_sound)

        elif ball.rect.right >= SCREEN.width:
            ball.rect.right = SCREEN.width
            ball.vx = -abs(ball.vx)
            self._play(self.bounce_sound)

        if ball.rect.top <= 0:
            ball.rect.top = 0
            ball.vy = abs(ball.vy)
            self._play(self.bounce_sound)

        return ball.rect.top > SCREEN.height

    def handle_bat(self, ball: Ball, bat: Bat) -> None:

        if ball.rect.colliderect(bat.rect) and ball.vy > 0:
            ball.rect.bottom = bat.rect.top

            offset = (ball.rect.centerx - bat.rect.centerx) / (bat.rect.width / 2)
            ball.vx = clamp(ball.vx + offset * 3.5, -BALL.max_speed, BALL.max_speed)
            ball.vy = -abs(ball.vy)

            ball.speed_cap()
            ball.can_hit_brick = True
            self._play(self.bounce_sound)

    def handle_bricks(self, ball: Ball, bricks: list[Brick]) -> Brick | None:

        """
        Return the brick that counts as a hit (or None).
        Applies:
        - reflection
        - optional force down after brick
        - one-counted-hit per bat bounce (via ball.can_hit_brick)
        """

        hit_brick = None
        for brick in bricks:
            if ball.rect.colliderect(brick.rect):
                hit_brick = brick
                break

        if not hit_brick:
            return None

        was_moving_up = (ball.vy < 0)

        ball.vx, ball.vy = reflect_ball_on_rect(ball.rect, (ball.vx, ball.vy), hit_brick.rect)

        # push away slightly to avoid repeated collisions
        ball.rect.x += int(ball.vx)
        ball.rect.y += int(ball.vy)

        if RULES.force_ball_down_after_brick:
            ball.vy = abs(ball.vy)

        ball.speed_cap()

        if ball.can_hit_brick and was_moving_up:
            ball.can_hit_brick = False
            self._play(self.brick_hit_sound)
            return hit_brick

        return None