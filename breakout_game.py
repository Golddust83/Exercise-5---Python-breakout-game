import os
import random
import pygame

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

pygame.init() 

pygame.display.set_caption("Breakout game")

clock = pygame.time.Clock()

WIDTH, HEIGHT = 900, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
FPS = 120

BAT_W, BAT_H = 120, 20
BAT_SPEED = 9

BALL_SPEED = 4  # base speed magnitude
BALL_MAX_SPEED = 6

BRICK_W, BRICK_H = 80, 50
BRICK_GAP = 6
TOP_MARGIN = 50
SIDE_MARGIN = 10

ROWS = 7
COLS = 10  # BRICK_W + gap must fit within WIDTH with margins

# File names (must be in same folder or provide paths)
BG_IMAGE = "starsbg.png"
BALL_IMAGE_FILE = "ChatGPT Image ball_small1.png"
BRICK_HIT_SFX = "bullet.mp3"
BOUNCE_SFX = "hit.mp3"
MUSIC_FILE = "music.mp3"



# ---------- Helpers ----------
def clamp(value, low, high):
    # Force value to stay between low and high
    return max(low, min(high, value))


def safe_load_sound(path):
    try:
        if os.path.exists(path):
            return pygame.mixer.Sound(path)
    except pygame.error:
        pass
    return None


def safe_load_image(path):
    try:
        if os.path.exists(path):
            return pygame.image.load(path).convert_alpha()
    except pygame.error:
        pass
    return None

def safe_load_background(path):
    try:
        if os.path.exists(path):
            return pygame.image.load(path).convert()
    except pygame.error:
        pass
    return None

def reflect_ball_on_rect(ball_rect, vel, obstacle_rect):
    """
    Reflect velocity based on which side we hit more.
    Works well for axis-aligned rectangles.
    """
    vx, vy = vel
    overlap_left = ball_rect.right - obstacle_rect.left
    overlap_right = obstacle_rect.right - ball_rect.left
    overlap_top = ball_rect.bottom - obstacle_rect.top
    overlap_bottom = obstacle_rect.bottom - ball_rect.top

    min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)

    if min_overlap == overlap_left:
        ball_rect.right = obstacle_rect.left
        vx = -abs(vx)
    elif min_overlap == overlap_right:
        ball_rect.left = obstacle_rect.right
        vx = abs(vx)
    elif min_overlap == overlap_top:
        ball_rect.bottom = obstacle_rect.top
        vy = -abs(vy)
    else:
        ball_rect.top = obstacle_rect.bottom
        vy = abs(vy)

    return (vx, vy)


# ---------- Game objects ----------
class Brick:
    def __init__(self, rect, hits_left = 1, points = 50, kind = "soft"):
        self.rect = rect
        self.hits_left = hits_left
        self.points = points
        self.kind = kind  # "soft", "hard", "power"

    def color(self):
        if self.kind == "hard":
            return (67, 60, 200)
        if self.kind == "power":
            return (184, 134, 11)
        return (169, 42, 189)  # soft


class Ball:
    def __init__(self, rect, vel):
        self.rect = rect
        self.vx, self.vy = vel
        self.can_hit_brick = True

    def speed_cap(self):
        self.vx = clamp(self.vx, - BALL_MAX_SPEED, BALL_MAX_SPEED)
        self.vy = clamp(self.vy, - BALL_MAX_SPEED, BALL_MAX_SPEED)

    def update(self):
        self.rect.x += int(self.vx)
        self.rect.y += int(self.vy)


# ---------- Main ----------
def main():  
    
    # Mixer setup (sound/music)
    try:
        pygame.mixer.init()
    except pygame.error:
        pass

    brick_hit_sound = safe_load_sound(BRICK_HIT_SFX)
    bounce_sound = safe_load_sound(BOUNCE_SFX)
    if bounce_sound:
        bounce_sound.set_volume(0.2)

    # Background music (loop)
    try:
        if os.path.exists(MUSIC_FILE):
            pygame.mixer.music.load(MUSIC_FILE)
            pygame.mixer.music.set_volume(0.1)
            pygame.mixer.music.play(-1)
    except pygame.error:
        pass

    # Ball sprite
    ball_image = safe_load_image(BALL_IMAGE_FILE)
    if ball_image:
        ball_size = ball_image.get_rect().size
    else:
        ball_size = (15, 15)

    # Background
    background_img = safe_load_background(BG_IMAGE)
    if background_img:
        background_img = pygame.transform.scale(
            background_img, (WIDTH, HEIGHT))

    font = pygame.font.SysFont(None, 32)
    big_font = pygame.font.SysFont(None, 64)

    bat_rect = pygame.Rect(WIDTH // 2 - BAT_W // 2, HEIGHT - 55, BAT_W, BAT_H)

    score = 0
    lives = 5

    balls = []

    def launch_ball(centerx, centery, vx = None, vy = None):
        rect = pygame.Rect(0, 0, ball_size[0], ball_size[1])
        rect.center = (centerx, centery)
        if vx is None:
            vx = random.choice([- BALL_SPEED, BALL_SPEED])
        if vy is None:
            vy = - BALL_SPEED
        balls.append(Ball(rect, (vx, vy)))

    launch_ball(bat_rect.centerx, bat_rect.top - 20)

    def bricks_layout():
        bricks_local = []

        grid_width = COLS * BRICK_W + (COLS - 1) * BRICK_GAP

        base_start_x = (WIDTH - grid_width) // 2

        for row in range(ROWS):
            y = TOP_MARGIN + row * (BRICK_H + BRICK_GAP)
            shift = (row % 2) * (BRICK_W // 2)

            for col in range(COLS):
                x = base_start_x + shift + col * (BRICK_W + BRICK_GAP)
                rect = pygame.Rect(x, y, BRICK_W, BRICK_H)

                if rect.right > WIDTH - SIDE_MARGIN:
                    continue

                if row < 2:
                    brick = Brick(rect, hits_left = 3, points = 120, kind = "hard")
                else:
                    brick = Brick(rect, hits_left = 2, points = 60, kind = "soft")

                if random.random() < 0.10 and row >= 2:
                    brick.kind = "power"
                    brick.hits_left = 2
                    brick.points = 150

                bricks_local.append(brick)

        return bricks_local

    bricks = bricks_layout()

    def reset_round():
        balls.clear()
        bat_rect.centerx = WIDTH // 2
        launch_ball(bat_rect.centerx, bat_rect.top - 20)

    running = True    
    game_over = False
    win = False

    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if (game_over or win) and event.key == pygame.K_r:
                    score = 0
                    lives = 5
                    bricks = bricks_layout()
                    game_over = False
                    win = False
                    reset_round()

        keys = pygame.key.get_pressed()

        if not (game_over or win):
            if keys[pygame.K_LEFT]:
                bat_rect.x -= BAT_SPEED
            if keys[pygame.K_RIGHT]:
                bat_rect.x += BAT_SPEED
            bat_rect.x = clamp(bat_rect.x, 0, WIDTH - bat_rect.width)

        if not (game_over or win):
            balls_to_remove = []
            for ball in balls:
                ball.update()

                # Walls
                if ball.rect.left <= 0:
                    ball.rect.left = 0
                    ball.vx = abs(ball.vx)
                    if bounce_sound:
                        bounce_sound.play()
                elif ball.rect.right >= WIDTH:
                    ball.rect.right = WIDTH
                    ball.vx = - abs(ball.vx)
                    if bounce_sound:
                        bounce_sound.play()

                if ball.rect.top <= 0:
                    ball.rect.top = 0
                    ball.vy = abs(ball.vy)
                    if bounce_sound:
                        bounce_sound.play()

                # Bottom (ball lost)
                if ball.rect.top > HEIGHT:
                    balls_to_remove.append(ball)
                    continue

                # Bat
                if ball.rect.colliderect(bat_rect) and ball.vy > 0:
                    ball.rect.bottom = bat_rect.top
                    offset = (ball.rect.centerx - bat_rect.centerx) / (bat_rect.width / 2)
                    ball.vx = clamp(ball.vx + offset * 3.5, - BALL_MAX_SPEED, BALL_MAX_SPEED)
                    ball.vy = -abs(ball.vy)
                    ball.speed_cap()
                    ball.can_hit_brick = True

                    if bounce_sound:
                        bounce_sound.play()

                # Bricks (solid always, but only 1 "counting" hit per bat bounce)
                hit_brick = None
                
                for brick in bricks:
                    if ball.rect.colliderect(brick.rect):
                        hit_brick = brick
                        break

                if hit_brick:
                    was_moving_up = (ball.vy < 0)

                    # Always bounce off bricks (even when "locked")
                    ball.vx, ball.vy = reflect_ball_on_rect(
                    ball.rect, (ball.vx, ball.vy), hit_brick.rect
                    )

                    # Push ball slightly away to prevent repeated collision
                    ball.rect.x += int(ball.vx)
                    ball.rect.y += int(ball.vy)

                    # OPTIONAL: force the ball to go downward after touching any brick
                    ball.vy = abs(ball.vy)

                    ball.speed_cap()

                    # Only the first brick hit after a bat bounce should "count"
                    if ball.can_hit_brick and was_moving_up:
                        ball.can_hit_brick = False

                        if brick_hit_sound:
                            brick_hit_sound.play()

                        hit_brick.hits_left -= 1

                        if hit_brick.hits_left <= 0:
                            score += hit_brick.points

                            if hit_brick.kind == "power":
                                launch_ball(
                                    hit_brick.rect.centerx,
                                    hit_brick.rect.centery,
                                    vx = random.choice([-BALL_SPEED, BALL_SPEED]),
                                    vy = -BALL_SPEED
                                    )

                            bricks.remove(hit_brick)
                        
                        else:
                            score += 20

            for b in balls_to_remove:
                if b in balls:
                    balls.remove(b)

            if len(balls) == 0:
                lives -= 1
                if lives <= 0:
                    game_over = True
                else:
                    reset_round()

            if len(bricks) == 0:
                win = True

        # Draw
        if background_img:
            screen.blit(background_img, (0, 0))
        else:
            screen.fill((18, 18, 24))

        for brick in bricks:
            pygame.draw.rect(screen, brick.color(), brick.rect, border_radius = 6)
            if brick.kind == "hard" and brick.hits_left > 1:
                inner = brick.rect.inflate(-12, -12)
                pygame.draw.rect(screen, (255, 210, 170), inner, width = 2, border_radius = 6)

        pygame.draw.rect(screen, (14, 237, 233), bat_rect, border_radius = 10)

        for ball in balls:
            if ball_image:
                screen.blit(ball_image, ball.rect)
            else:
                pygame.draw.ellipse(screen, (240, 240, 240), ball.rect)

        ui = font.render(f"Score: {score}    Lives: {lives}    Balls: {len(balls)}", True, (235, 235, 235))
        screen.blit(ui, (18, 16))

        if game_over:
            msg = big_font.render("GAME OVER - You suck!", True, (237, 14, 14))
            sub = font.render("Press R to restart, ESC to quit", True, (230, 230, 230))
            screen.blit(msg, msg.get_rect(center = (WIDTH // 2, HEIGHT // 2 + 30)))
            screen.blit(sub, sub.get_rect(center = (WIDTH // 2, HEIGHT // 2 + 75)))

        if win:
            msg = big_font.render("Congrats, you won the game!", True, (120, 255, 160))
            sub = font.render("Press R to restart, ESC to quit", True, (230, 230, 230))
            screen.blit(msg, msg.get_rect(center = (WIDTH // 2, HEIGHT // 2 + 30)))
            screen.blit(sub, sub.get_rect(center = (WIDTH // 2, HEIGHT // 2 + 75)))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()