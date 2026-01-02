import pygame
import random
from dataclasses import dataclass

"""
Breakout 

Features:

- Bat moved with arrow keys.
- Score + Lives shown on screen.
- Two brick types (different hit points + points).
- Powerup brick that spawns an extra ball (multi-ball).
- Each ball resolves at most ONE brick collision per update.
"""

# ----------------------------
# Config
# ----------------------------
pygame.mixer.init()

screen_width = 900
screen_height = 800
FPS = 120

BG = pygame.image.load("starsbg.png")

BAT_COLOR = (17, 242, 227)      # turquoise
BAT_SPEED = 9
BAT_W, BAT_H = 140, 18
BAT_Y_OFFSET = 60

BALL_SIZE = 16
BALL_SPEED_MIN = 4
BALL_SPEED_MAX = 6

TOP_WALL = 0
SIDE_WALL = 0

START_LIVES = 3

# Brick grid (different than the "standard" full rectangle)
BRICK_ROWS = 6
BRICK_COLS = 11
BRICK_W = 70
BRICK_H = 24
BRICK_GAP = 10
GRID_TOP = 80

# Brick types
COLOR_SOFT = (120, 205, 250)    # 1 hit, 10 points
COLOR_HARD = (250, 170, 70)     # 2 hits, 25 points
COLOR_POWER = (90, 235, 120)    # 1 hit, spawns extra ball, 15 points

# ----------------------------
# Helpers
# ----------------------------
def clamp(v, lo, hi):
    return lo if v < lo else hi if v > hi else v

def random_ball_velocity():
    # Avoid near-zero horizontal movement
    x = random.choice([-1, 1]) * random.randint(BALL_SPEED_MIN, BALL_SPEED_MAX)
    y = -random.randint(BALL_SPEED_MIN, BALL_SPEED_MAX)
    return x, y

# ----------------------------
# Game objects
# ----------------------------
class Sprite:
    def draw(self, surf: pygame.Surface) -> None:
        raise NotImplementedError

@dataclass
class Bat(Sprite):
    rect: pygame.Rect
    speed: int = BAT_SPEED

    def update(self, keys):
        dx = 0
        if keys[pygame.K_LEFT]:
            dx -= self.speed
        if keys[pygame.K_RIGHT]:
            dx += self.speed

        self.rect.x += dx
        self.rect.x = clamp(self.rect.x, 0, WIDTH - self.rect.w)

    def draw(self, surf):
        pygame.draw.rect(surf, BAT_COLOR, self.rect, border_radius=10)

@dataclass
class Ball(Sprite):
    rect: pygame.Rect
    vx: int
    vy: int

    def update_position(self):
        self.rect.x += self.vx
        self.rect.y += self.vy

    def draw(self, surf):
        pygame.draw.ellipse(surf, (255, 255, 255), self.rect)

@dataclass
class Brick(Sprite):
    rect: pygame.Rect
    hp: int
    points: int
    kind: str  # "soft" | "hard" | "power"
    alive: bool = True

    def color(self):
        if self.kind == "soft":
            return COLOR_SOFT
        if self.kind == "hard":
            # Darken a bit when damaged
            return (COLOR_HARD[0], COLOR_HARD[1] - 40, COLOR_HARD[2] - 40) if self.hp == 1 else COLOR_HARD
        if self.kind == "power":
            return COLOR_POWER
        return (200, 200, 200)

    def hit(self):
        self.hp -= 1
        if self.hp <= 0:
            self.alive = False
            return True  # destroyed
        return False

    def draw(self, surf):
        if not self.alive:
            return
        pygame.draw.rect(surf, self.color(), self.rect, border_radius=4)
        pygame.draw.rect(surf, (0, 0, 0), self.rect, 2, border_radius=4)

# ----------------------------
# Collision resolution
# ----------------------------
def bounce_off_walls(ball: Ball):
    # Left / right
    if ball.rect.left <= 0:
        ball.rect.left = 0
        ball.vx *= -1
    elif ball.rect.right >= WIDTH:
        ball.rect.right = WIDTH
        ball.vx *= -1

    # Top
    if ball.rect.top <= 0:
        ball.rect.top = 0
        ball.vy *= -1

def bounce_off_bat(ball: Ball, bat: Bat):
    if not ball.rect.colliderect(bat.rect):
        return

    # Put ball above bat to avoid "sticking"
    ball.rect.bottom = bat.rect.top - 1
    ball.vy = -abs(ball.vy)

    # Add some angle depending on where it hits the bat
    hit_pos = (ball.rect.centerx - bat.rect.centerx) / (bat.rect.w / 2)
    hit_pos = clamp(hit_pos, -1, 1)
    ball.vx = int(hit_pos * BALL_SPEED_MAX)
    if ball.vx == 0:
        ball.vx = random.choice([-1, 1]) * BALL_SPEED_MIN

def bounce_off_bricks_one_per_update(ball: Ball, bricks: list[Brick]):
    """
    Ensures each ball can only hit ONE brick per update.
    """
    # Find a single collided brick (first match)
    for brick in bricks:
        if brick.alive and ball.rect.colliderect(brick.rect):
            # Determine whether to flip x or y by checking overlap depth
            overlap_left = ball.rect.right - brick.rect.left
            overlap_right = brick.rect.right - ball.rect.left
            overlap_top = ball.rect.bottom - brick.rect.top
            overlap_bottom = brick.rect.bottom - ball.rect.top
            min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)

            if min_overlap == overlap_left:
                ball.rect.right = brick.rect.left
                ball.vx *= -1
            elif min_overlap == overlap_right:
                ball.rect.left = brick.rect.right
                ball.vx *= -1
            elif min_overlap == overlap_top:
                ball.rect.bottom = brick.rect.top
                ball.vy *= -1
            else:
                ball.rect.top = brick.rect.bottom
                ball.vy *= -1

            destroyed = brick.hit()
            return brick, destroyed
    return None, False

# ----------------------------
# Level builder (different grid pattern)
# ----------------------------
def build_bricks():
    bricks: list[Brick] = []
    grid_w = BRICK_COLS * BRICK_W + (BRICK_COLS - 1) * BRICK_GAP
    start_x = (WIDTH - grid_w) // 2

    for r in range(BRICK_ROWS):
        # Stagger every other row for a different look
        row_offset = (BRICK_W // 2) if (r % 2 == 1) else 0
        for c in range(BRICK_COLS):
            x = start_x + c * (BRICK_W + BRICK_GAP) + row_offset
            y = GRID_TOP + r * (BRICK_H + BRICK_GAP)

            # Keep bricks inside bounds when staggered
            if x < 10 or x + BRICK_W > WIDTH - 10:
                continue

            rect = pygame.Rect(x, y, BRICK_W, BRICK_H)

            # Pattern:
            # - top 2 rows = hard
            # - some power bricks sprinkled
            # - rest soft
            if r < 2:
                bricks.append(Brick(rect, hp=2, points=25, kind="hard"))
            else:
                if (r + c) % 9 == 0:
                    bricks.append(Brick(rect, hp=1, points=15, kind="power"))
                else:
                    bricks.append(Brick(rect, hp=1, points=10, kind="soft"))
    return bricks

# ----------------------------
# Main
# ----------------------------
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Breakout")
    clock = pygame.time.Clock()

    font = pygame.font.SysFont("comicsans", 30, True)
    big_font = pygame.font.SysFont("comicsans", 64, True)

    bat = Bat(pygame.Rect(WIDTH // 2 - BAT_W // 2, HEIGHT - BAT_Y_OFFSET, BAT_W, BAT_H))
    bricks = build_bricks()

    score = 0
    lives = START_LIVES
    running = True
    game_over = False
    won = False

    # Ball handling
    balls: list[Ball] = []

    def serve_ball():
        vx, vy = random_ball_velocity()
        b = Ball(pygame.Rect(bat.rect.centerx - BALL_SIZE // 2, bat.rect.top - BALL_SIZE - 2, BALL_SIZE, BALL_SIZE), vx, vy)
        balls.append(b)

    def reset_to_single_ball():
        balls.clear()
        serve_ball()

    reset_to_single_ball()

    while running:
        dt = clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if game_over and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                # Restart
                score = 0
                lives = START_LIVES
                bricks = build_bricks()
                bat.rect.x = WIDTH // 2 - BAT_W // 2
                game_over = False
                won = False
                reset_to_single_ball()

        keys = pygame.key.get_pressed()
        if not game_over:
            bat.update(keys)

            # Update balls
            for ball in list(balls):
                ball.update_position()
                bounce_off_walls(ball)
                bounce_off_bat(ball, bat)

                hit_brick, destroyed = bounce_off_bricks_one_per_update(ball, bricks)
                if hit_brick is not None and destroyed:
                    score += hit_brick.points
                    # Multiball power brick: spawn a new ball from the destroyed brick
                    if hit_brick.kind == "power":
                        vx, vy = random_ball_velocity()
                        balls.append(Ball(pygame.Rect(hit_brick.rect.centerx - BALL_SIZE // 2,
                                                     hit_brick.rect.centery - BALL_SIZE // 2,
                                                     BALL_SIZE, BALL_SIZE), vx, vy))

                # Ball fell below bottom => remove it
                if ball.rect.top > HEIGHT:
                    balls.remove(ball)

            # If all balls are gone => lose a life and serve again
            if len(balls) == 0:
                lives -= 1
                if lives <= 0:
                    game_over = True
                    won = False
                else:
                    reset_to_single_ball()

            # Win condition
            if all(not b.alive for b in bricks):
                game_over = True
                won = True

        # Draw
        screen.fill(BG_COLOR)

        for b in bricks:
            b.draw(screen)
        bat.draw(screen)
        for ball in balls:
            ball.draw(screen)

        hud = font.render(f"Score: {score}    Lives: {lives}    Balls: {len(balls)}", True, (240, 240, 240))
        screen.blit(hud, (20, 20))

        if game_over:
            msg = "You won!" if won else "Game over"
            t = big_font.render(msg, True, (255, 255, 255))
            screen.blit(t, (WIDTH // 2 - t.get_width() // 2, HEIGHT // 2 - 80))

            t2 = font.render("Press SPACE to restart", True, (220, 220, 220))
            screen.blit(t2, (WIDTH // 2 - t2.get_width() // 2, HEIGHT // 2))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
