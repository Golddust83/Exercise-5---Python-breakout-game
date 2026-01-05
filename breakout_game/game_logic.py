import os
import random
import pygame

from .config import SCREEN, BAT, BALL, BRICKS, ASSETS, AUDIO, RULES
from .resources import Resources
from .utils import clamp, reflect_ball_on_rect
from .objects.ball import Ball
from .objects.bricks import Brick
from .objects.bat import Bat


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(SCREEN.caption)

        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((SCREEN.width, SCREEN.height))

        # Audio init
        try:
            pygame.mixer.init()
        except pygame.error:
            pass

        self.res = Resources()

        self.brick_hit_sound = self.res.sound(ASSETS.brick_hit_sfx)
        self.bounce_sound = self.res.sound(ASSETS.bounce_sfx)
        if self.bounce_sound:
            self.bounce_sound.set_volume(AUDIO.bounce_volume)

        # Music init
        try:
            if os.path.exists(ASSETS.music_file):
                pygame.mixer.music.load(ASSETS.music_file)
                pygame.mixer.music.set_volume(AUDIO.music_volume)
                pygame.mixer.music.play(-1)
        except pygame.error:
            pass

        # Ball sprite image + size
        self.ball_image = self.res.image(ASSETS.ball_image_file)
        if self.ball_image:
            self.ball_size = self.ball_image.get_rect().size
        else:
            self.ball_size = BALL.fallback_size

        # Background
        self.background_img = self.res.background(ASSETS.bg_image)
        if self.background_img:
            self.background_img = pygame.transform.scale(
                self.background_img, (SCREEN.width, SCREEN.height)
            )

        self.font = pygame.font.SysFont(None, 32)
        self.big_font = pygame.font.SysFont(None, 64)

        self.bat = Bat()

        self.score = 0
        self.lives = RULES.start_lives
        self.balls = []
        self.bricks = self.bricks_layout()

        self.running = True
        self.game_over = False
        self.win = False

        self.launch_ball(self.bat.rect.centerx, self.bat.rect.top - 20)

    
    def launch_ball(self, centerx, centery, vx = None, vy = None):
        rect = pygame.Rect(0, 0, self.ball_size[0], self.ball_size[1])
        rect.center = (centerx, centery)

        if vx is None:
            vx = random.choice([-BALL.speed, BALL.speed])
        if vy is None:
            vy = -BALL.speed

        self.balls.append(Ball(rect, (vx, vy)))

    def bricks_layout(self):

        bricks_local = []

        grid_width = BRICKS.cols * BRICKS.width + (BRICKS.cols - 1) * BRICKS.gap
        base_start_x = (SCREEN.width - grid_width) // 2

        for row in range(BRICKS.rows):
            y = BRICKS.top_margin + row * (BRICKS.height + BRICKS.gap)
            shift = (row % 2) * (BRICKS.width // 2)

            for col in range(BRICKS.cols):
                x = base_start_x + shift + col * (BRICKS.width + BRICKS.gap)
                rect = pygame.Rect(x, y, BRICKS.width, BRICKS.height)

                if rect.right > SCREEN.width - BRICKS.side_margin:
                    continue

                if row < 2:
                    brick = Brick(rect, hits_left=3, points=120, kind="hard")
                else:
                    brick = Brick(rect, hits_left=2, points=60, kind="soft")

                if random.random() < BRICKS.power_chance and row >= 2:
                    brick.kind = "power"
                    brick.hits_left = 2
                    brick.points = 150

                bricks_local.append(brick)

        return bricks_local

    def reset_round(self):
        self.balls.clear()
        self.bat.rect.centerx = SCREEN.width // 2
        self.launch_ball(self.bat.rect.centerx, self.bat.rect.top - 20)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

                if (self.game_over or self.win) and event.key == pygame.K_r:
                    self.score = 0
                    self.lives = RULES.start_lives
                    self.bricks = self.bricks_layout()
                    self.game_over = False
                    self.win = False
                    self.reset_round()

    def update(self):
        keys = pygame.key.get_pressed()

        if not (self.game_over or self.win):
            self.bat.update(keys)

        if not (self.game_over or self.win):
            balls_to_remove = []

            for ball in self.balls:
                ball.update()

                # Walls
                if ball.rect.left <= 0:
                    ball.rect.left = 0
                    ball.vx = abs(ball.vx)
                    if self.bounce_sound:
                        self.bounce_sound.play()

                elif ball.rect.right >= SCREEN.width:
                    ball.rect.right = SCREEN.width
                    ball.vx = -abs(ball.vx)
                    if self.bounce_sound:
                        self.bounce_sound.play()

                if ball.rect.top <= 0:
                    ball.rect.top = 0
                    ball.vy = abs(ball.vy)
                    if self.bounce_sound:
                        self.bounce_sound.play()

                # Bottom (lost)
                if ball.rect.top > SCREEN.height:
                    balls_to_remove.append(ball)
                    continue

                # Bat bounce
                if ball.rect.colliderect(self.bat.rect) and ball.vy > 0:
                    ball.rect.bottom = self.bat.rect.top
                    offset = (ball.rect.centerx - self.bat.rect.centerx) / (self.bat.rect.width / 2)
                    ball.vx = clamp(ball.vx + offset * 3.5, -BALL.max_speed, BALL.max_speed)
                    ball.vy = -abs(ball.vy)
                    ball.speed_cap()
                    ball.can_hit_brick = True

                    if self.bounce_sound:
                        self.bounce_sound.play()

                # Bricks
                hit_brick = None
                for brick in self.bricks:
                    if ball.rect.colliderect(brick.rect):
                        hit_brick = brick
                        break

                if hit_brick:
                    was_moving_up = (ball.vy < 0)

                    ball.vx, ball.vy = reflect_ball_on_rect(
                        ball.rect, (ball.vx, ball.vy), hit_brick.rect
                    )

                    ball.rect.x += int(ball.vx)
                    ball.rect.y += int(ball.vy)

                    if RULES.force_ball_down_after_brick:
                        ball.vy = abs(ball.vy)

                    ball.speed_cap()

                    if ball.can_hit_brick and was_moving_up:
                        ball.can_hit_brick = False

                        if self.brick_hit_sound:
                            self.brick_hit_sound.play()

                        destroyed, points = hit_brick.hit()
                        self.score += points

                        if destroyed:
                            if hit_brick.kind == "power":
                                self.launch_ball(
                                    hit_brick.rect.centerx,
                                    hit_brick.rect.centery,
                                    vx = random.choice([-BALL.speed, BALL.speed]),
                                    vy = -BALL.speed
                                )
                            self.bricks.remove(hit_brick)

            for b in balls_to_remove:
                if b in self.balls:
                    self.balls.remove(b)

            if len(self.balls) == 0:
                self.lives -= 1
                if self.lives <= 0:
                    self.game_over = True
                else:
                    self.reset_round()

            if len(self.bricks) == 0:
                self.win = True

    def draw(self):
        if self.background_img:
            self.screen.blit(self.background_img, (0, 0))
        else:
            self.screen.fill((18, 18, 24))

        # Bricks draw
        for brick in self.bricks:
            brick.draw(self.screen)

        pygame.draw.rect(self.screen, (14, 237, 233), self.bat.rect, border_radius = 10)

        for ball in self.balls:
            if self.ball_image:
                self.screen.blit(self.ball_image, ball.rect)
            else:
                pygame.draw.ellipse(self.screen, (240, 240, 240), ball.rect)

        ui = self.font.render(
            f"Score: {self.score}    Lives: {self.lives}    Balls: {len(self.balls)}",
            True,
            (235, 235, 235)
        )
        self.screen.blit(ui, (18, 16))

        if self.game_over:
            msg = self.big_font.render("GAME OVER - You suck!", True, (237, 14, 14))
            sub = self.font.render("Press R to restart, ESC to quit", True, (230, 230, 230))
            self.screen.blit(msg, msg.get_rect(center=(SCREEN.width // 2, SCREEN.height // 2 + 30)))
            self.screen.blit(sub, sub.get_rect(center=(SCREEN.width // 2, SCREEN.height // 2 + 75)))

        if self.win:
            msg = self.big_font.render("Congrats, you won the game!", True, (120, 255, 160))
            sub = self.font.render("Press R to restart, ESC to quit", True, (230, 230, 230))
            self.screen.blit(msg, msg.get_rect(center=(SCREEN.width // 2, SCREEN.height // 2 + 30)))
            self.screen.blit(sub, sub.get_rect(center=(SCREEN.width // 2, SCREEN.height // 2 + 75)))

        pygame.display.flip()

    def run(self):

        while self.running:
            self.clock.tick(SCREEN.fps)
            self.handle_events()
            self.update()
            self.draw()

        pygame.quit()