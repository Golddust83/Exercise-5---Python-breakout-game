import os
import random
import pygame

from .config import SCREEN, BALL, BRICKS, ASSETS, AUDIO, RULES
from .resources import Resources
from .state import GameState
from .scoring import Scoring
from .collision import CollisionSystem

from .objects.ball import Ball
from .objects.bricks import Brick
from .objects.bat import Bat


class Game:

    def __init__(self):

        pygame.init()
        pygame.display.set_caption(SCREEN.caption)

        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((SCREEN.width, SCREEN.height))

        # Composition: Game "has" these helper objects
        self.res = Resources()
        self.scoring = Scoring(score = 0)

        # Audio init (safe)
        try:
            pygame.mixer.init()
        except pygame.error:
            pass

        self.brick_hit_sound = self.res.sound(ASSETS.brick_hit_sfx)
        self.bounce_sound = self.res.sound(ASSETS.bounce_sfx)
        if self.bounce_sound:
            self.bounce_sound.set_volume(AUDIO.bounce_volume)

        # Delegation: collisions handled by CollisionSystem
        self.collision = CollisionSystem(
            bounce_sound = self.bounce_sound,
            brick_hit_sound = self.brick_hit_sound
        )

        # Music init (safe)
        try:
            if os.path.exists(ASSETS.music_file):
                pygame.mixer.music.load(ASSETS.music_file)
                pygame.mixer.music.set_volume(AUDIO.music_volume)
                pygame.mixer.music.play(-1)
        except pygame.error:
            pass

        # Load images
        self.ball_image = self.res.image(ASSETS.ball_image_file)

        if self.ball_image:
            self.ball_size = self.ball_image.get_rect().size
        else:
            self.ball_size = BALL.fallback_size

        self.background_img = self.res.background(ASSETS.bg_image)

        if self.background_img:
            self.background_img = pygame.transform.scale(
                self.background_img, (SCREEN.width, SCREEN.height)
            )

        # Fonts
        self.font = pygame.font.SysFont(None, 32)
        self.big_font = pygame.font.SysFont(None, 64)

        # Objects (instances) + Collections
        self.bat = Bat()
        self.balls: list[Ball] = []
        self.bricks: list[Brick] = self.bricks_layout()

        # Polymorphism demo list: contains different Sprite subclasses
        self.sprites = []

        self.lives = RULES.start_lives
        self.state = GameState.PLAYING
        self.running = True

        self.launch_ball(self.bat.rect.centerx, self.bat.rect.top - 20)
        self.rebuild_sprite_list()

    @property

    def score(self) -> int:        
        return self.scoring.score

    # Polymorphism setup 
    def rebuild_sprite_list(self) -> None:
        self.sprites = [self.bat] + self.bricks + self.balls

    # ---------- Factory methods ----------
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
                    brick = Brick(rect, hits_left = 3, points = 120, kind = "hard")
                else:
                    brick = Brick(rect, hits_left = 2, points = 60, kind = "soft")

                if random.random() < BRICKS.power_chance and row >= 2:
                    brick.kind = "power"
                    brick.hits_left = 3
                    brick.points = 150

                bricks_local.append(brick)

        return bricks_local

    # Game flow
    def reset_round(self):

        self.balls.clear()
        self.bat.rect.centerx = SCREEN.width // 2
        self.launch_ball(self.bat.rect.centerx, self.bat.rect.top - 20)
        self.rebuild_sprite_list()

    def restart_game(self):

        self.scoring.score = 0
        self.lives = RULES.start_lives
        self.bricks = self.bricks_layout()
        self.balls.clear()
        self.state = GameState.PLAYING
        self.launch_ball(self.bat.rect.centerx, self.bat.rect.top - 20)
        self.rebuild_sprite_list()

    def handle_events(self):

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

                if self.state in (GameState.LOST, GameState.WON) and event.key == pygame.K_r:
                    self.restart_game()

    def update(self):

        keys = pygame.key.get_pressed()

        if self.state != GameState.PLAYING:
            return

        # Polymorphism: update different object types via same method name
        for s in self.sprites:
            s.update(keys = keys)

        balls_to_remove: list[Ball] = []

        # Collisions + rules (delegation)
        for ball in self.balls:

            if self.collision.handle_walls_and_bottom(ball):
                balls_to_remove.append(ball)
                continue

            self.collision.handle_bat(ball, self.bat)

            hit_brick = self.collision.handle_bricks(ball, self.bricks)

            if hit_brick:
                destroyed = hit_brick.hit()

                if destroyed:
                    self.scoring.add_for_brick_destroyed(hit_brick)

                    # Power brick effect: extra ball
                    if hit_brick.kind == "power":
                        self.launch_ball(
                            hit_brick.rect.centerx,
                            hit_brick.rect.centery,
                            vx = random.choice([-BALL.speed, BALL.speed]),
                            vy = -BALL.speed
                        )

                    self.bricks.remove(hit_brick)

        # Remove lost balls
        for b in balls_to_remove:

            if b in self.balls:
                self.balls.remove(b)

        # Lives/state checks
        if len(self.balls) == 0:
            self.lives -= 1

            if self.lives <= 0:
                self.state = GameState.LOST
            else:
                self.reset_round()

        if len(self.bricks) == 0:
            self.state = GameState.WON

        # Keep polymorphism list in sync with collections
        self.rebuild_sprite_list()

    def draw(self):

        if self.background_img:
            self.screen.blit(self.background_img, (0, 0))
        else:
            self.screen.fill((18, 18, 24))

        # Polymorphism: draw different object types via same method name
        for s in self.sprites:
            s.draw(self.screen, image = self.ball_image)

        ui = self.font.render(
            f"Score: {self.score}    Lives: {self.lives}    Balls: {len(self.balls)}",
            True, (235, 235, 235)
        )
        self.screen.blit(ui, (18, 16))

        if self.state == GameState.LOST:

            msg = self.big_font.render("GAME OVER - You suck!", True, (237, 14, 14))
            sub = self.font.render("Press R to restart, ESC to quit", True, (255, 255, 255))
            self.screen.blit(msg, msg.get_rect(center=(SCREEN.width // 2, SCREEN.height // 2 + 30)))
            self.screen.blit(sub, sub.get_rect(center=(SCREEN.width // 2, SCREEN.height // 2 + 75)))

        if self.state == GameState.WON:
            
            msg = self.big_font.render("Congrats, you won the game!", True, (120, 255, 160))
            sub = self.font.render("Press R to restart, ESC to quit", True, (255, 255, 255))
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