import pygame
import random

"""
How to run this program:

PS C:\KAU\Exercise 5 - Python breakout game> cd "C:\KAU\Exercise 5 - Python breakout game\Game"
PS C:\KAU\Exercise 5 - Python breakout game\Game> python first_game.py
"""

pygame.init()

screen_width = 900
screen_height = 800

bg = pygame.image.load("starsbg.png")
win = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Breakout game")

brick_hit_sound = pygame.mixer.Sound("bullet.mp3")
bounce_sound = pygame.mixer.Sound("hit.mp3")
bounce_sound.set_volume(.2)
bg_music = pygame.mixer.Sound("music.mp3")
pygame.mixer.music.play(-1)

ball = pygame.image.load("ChatGPT Image ball_small1.png")

clock = pygame.time.Clock()

gameover = False
score = 0

class Bat(object):
    def __init__(self, x, y, w, h, color):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.color = color
        self.xx = self.x + self.w
        self.yy = self.y + self.h

    def draw(self, win):
        pygame.draw.rect(win, self.color, [self.x, self.y, self.w, self.h])

class Ball(object):
    def __init__(self, x, y, w, h, color):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.color = color
        self.xx = self.x + self.w
        self.yy = self.y + self.h
        self.x_vel = random.choice([2, 3, 4, -2, -3, -4])
        self.y_vel = random.randint(3, 4)
    
    def draw(self, win):
        # something with draw ball?

     def move(self):
        self.x += self.x_vel
        self.y += self.y_vel
        self.xx = self.x + self.w
        self.yy = self.y + self.h

class Brick(object):
    def __init__(self, x, y, w, h, color):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.color = color
        self.xx = self.x + self.w
        self.yy = self.y + self.h
        self.visible = True
        
    def draw(self, win):
        if self.visible:
            pygame.draw.rect(win, self.color, [self.x, self.y, self.w, self.h])

bricks = []

def init():

    global bricks 
    bricks = []   
    for i in range (6):
        for j in range (10):
            bricks.append(Brick((10 + j) * 79, (50 + i) * 35, 70, 25, (120, 205, 250)))

def redraw_game_window():
    win.blit(bg, (0, 0))
    player.draw(win)
    ball.draw(win)

    for b in bricks:
        b.draw(win)

    font = pygame.font.SysFont("comicsans", 50)
    
    if gameover:
        
        message = "Congrats, you won the game!" if not bricks else "You suck!"
        resText = font.render(message, True, (255, 255, 255))
        win.blit(resText, ((sw // 2 - resText.get_width() // 2), sh // 2 - resText.get_height() // 2))
        play_again_text = font.render("Press space to play again!", 1, (255, 255, 255))
        win.blit(play_again_text, ((sw // 2 - play_again_text.get_width() // 2), sh // 2 + 30))

    pygame.display.update()

player = Bat((sw / 2) - 50, sh - 100, 100, 20, (17, 242, 227))
####ball = Ball((sw / 2) - 10, sh - 200, 20, 20, (255, 255, 255))
init()

running = True

while running:

    clock.tick(100)

    if not gameover:

        ball.move()

        ###############if pygame.mouse.get_pos()[0] - player.w // 2 < 0:
            player.x = 0

        ##########elif pygame.mouse.get_pos()[0] + player.w // 2 > sw:
            player.x = sw - player.w

        ##########else:
            player.x = pygame.mouse.get_pos()[0] - player.w // 2

        if (ball.x >= player.x and ball.x <= player.x + player.w) or (ball.x + ball.w >= player.x and ball.x + ball.w <= player.x + player.w):
            if (ball.y + ball.h >= player.y) and (ball.y + ball.h <= player.y + player.h):
                ball.y_vel *= -1
                bounce_sound.play()

        # Right wall
        if ball.x + ball.w >= sw:
            bounce_sound.play()
            ball.x_vel = 0   # Stop sideways
            ball.y_vel = 3   # Start dropping faster downwards

        # Left wall
        if ball.x <= 0:
            bounce_sound.play()
            ball.x_vel = 0
            ball.y_vel = 3

        # Ceiling
        if ball.y <= 0:
            bounce_sound.play()
            ball *= -1

        for brick in bricks:
            if (ball.x >= brick.x and ball.x <= brick.x + brick.w) or (ball.x + ball.w >= brick.x and ball.x + ball.w <= brick.x + brick.w):
                if (ball.y >= brick.y) and (ball.y <= brick.y + brick.h) or (ball.y + ball.h >= brick.y) and (ball.y + ball.h <= brick.y + brick.h):
                    brick.visible = False
                    bricks.pop(bricks.index(brick))
                    ball.y_vel *= -1
                    brick_hit_sound.play()

        if ball.y > screen_height:
            gameover = True

    keys = pygame.key.get_pressed()

    if len(bricks) == 0:
        won = True
        gameover = True

    if gameover:
        if keys[pygame.K_SPACE]:
            won = False
            gameover = False
            ball = Ball((sw / 2) - 10, sh - 200, 20, 20, (255, 255, 255))
            bricks.clear()
            init()

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

    redraw_game_window()

pygame.quit()        