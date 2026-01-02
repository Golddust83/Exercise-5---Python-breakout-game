"""
How to run this program:

PS C:\KAU\Exercise 5 - Python breakout game> cd "C:\KAU\Exercise 5 - Python breakout game\Game"
PS C:\KAU\Exercise 5 - Python breakout game\Game> python first_game.py
"""

import pygame
import sys

pygame.init()

screen_width = 500
screen_height = 480

win = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("First game")

clock = pygame.time.Clock()

bullet_sound = pygame.mixer.Sound('bullet.mp3')
hit_sound = pygame.mixer.Sound('hit.mp3')
music = pygame.mixer.music.load('music.mp3')

bullet_sound.play()
pygame.mixer.music.play(-1)

score = 0

walk_right = [pygame.image.load('R1.png'), pygame.image.load('R2.png'), pygame.image.load('R3.png'), pygame.image.load('R4.png'), pygame.image.load('R5.png'), pygame.image.load('R6.png'), pygame.image.load('R7.png'), pygame.image.load('R8.png'), pygame.image.load('R9.png')]
walk_left = [pygame.image.load('L1.png'), pygame.image.load('L2.png'), pygame.image.load('L3.png'), pygame.image.load('L4.png'), pygame.image.load('L5.png'), pygame.image.load('L6.png'), pygame.image.load('L7.png'), pygame.image.load('L8.png'), pygame.image.load('L9.png')]
bg = pygame.image.load('bg.jpg')

class player(object):

    def __init__(self, x, y, width, height):
        
        self.x = x
        self.y = y
        self.width = width    # width of the character/object
        self.height = height   # height of the character/object
        self.vel = 5
        self.isJump = False
        self.jump_count = 10
        self.left = False
        self.right = False
        self.walk_count = 0
        self.standing = True
        self.hitbox = (self.x + 17, self.y + 11, 29, 52)

    def draw(self, win):

        if self.walk_count + 1 >= 27:
            self.walk_count = 0

        if not (self.standing):

            if self.left:
                win.blit(walk_left[self.walk_count // 3], (self.x, self.y))
                self.walk_count += 1

            elif self.right:
                win.blit(walk_right[self.walk_count // 3], (self.x, self.y))
                self.walk_count += 1

        else:
            if self.right:
                win.blit(walk_right[0], (self.x, self.y))
            
            else:
                win.blit(walk_left[0], (self.x, self.y))
        self.hitbox = (self.x + 17, self.y + 11, 29, 52)
        # pygame.draw.rect(win, (255, 0, 0), self.hitbox, 2)

    def hit(self):

        self.isJump = False
        self.jump_count = 10
        self.x = 60
        self.y = 410
        self.walk_count = 0
        font_1 = pygame.font.SysFont("comicsans", 100)
        text = font_1.render("- 5 points!", 1, (255, 0, 0))
        win.blit(text, ((screen_width / 2) - (text.get_width() / 2), 200))
        pygame.display.update()
        
        i = 0

        while i < 300:

            pygame.time.delay(10)
            i += 1

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    i = 301
                    pygame.quit()

class projectile(object):

    def __init__(self, x, y, radius, color, facing):
        self.x = x
        self.y = y
        self.radius = radius    
        self.color = color
        self.facing = facing
        self.vel = 8 * facing
        
    def draw(self, win):

        pygame.draw.circle(win, self.color, (self.x, self.y), self.radius)

class enemy(object):

    walk_right = [pygame.image.load('R1E.png'), pygame.image.load('R2E.png'), pygame.image.load('R3E.png'), pygame.image.load('R4E.png'), pygame.image.load('R5E.png'), pygame.image.load('R6E.png'), pygame.image.load('R7E.png'), pygame.image.load('R8E.png'), pygame.image.load('R9E.png'), pygame.image.load('R10E.png'), pygame.image.load('R11E.png')]
    walk_left = [pygame.image.load('L1E.png'), pygame.image.load('L2E.png'), pygame.image.load('L3E.png'), pygame.image.load('L4E.png'), pygame.image.load('L5E.png'), pygame.image.load('L6E.png'), pygame.image.load('L7E.png'), pygame.image.load('L8E.png'), pygame.image.load('L9E.png'), pygame.image.load('L10E.png'), pygame.image.load('L11E.png')]
    
    def __init__(self, x, y, width, height, end):

        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.end = end
        self.path = [self.x, self.end]  # This will define where our enemy starts and finishes their path. 
        self.walk_count = 0
        self.vel = 3
        self.hitbox = (self.x + 17, self.y + 2, 31, 57)
        self.health = 10
        self.visible = True

    def draw(self, win):

        self.move()

        if self.visible:

            if self.walk_count + 1 >= 33: # Since we have 11 images for each animtion our upper bound is 33. 
                                 # We will show each image for 3 frames. 3 x 11 = 33.
                self.walk_count = 0
        
            if self.vel > 0: # If we are moving to the right we will display our walkRight images
                win.blit(self.walk_right[self.walk_count // 3], (self.x, self.y))
                self.walk_count += 1

            else:  # Otherwise we will display the walkLeft images
                win.blit(self.walk_left[self.walk_count // 3], (self.x, self.y))
                self.walk_count += 1

            pygame.draw.rect(win, (255, 0, 0), (self.hitbox[0], self.hitbox[1] - 20, 50, 10))
            pygame.draw.rect(win, (0, 128, 0), (self.hitbox[0], self.hitbox[1] - 20, 50 - ((50/10) * (10 - self.health)), 10))
            self.hitbox = (self.x + 17, self.y + 2, 31, 57)
            # pygame.draw.rect(win, (255, 0, 0), self.hitbox, 2)

    def move(self):

        if self.vel > 0:  # If we are moving right

            if self.x + self.vel < self.path[1]: # If we have not reached the furthest right point on our path.
                self.x += self.vel

            else: # Change direction and move back the other way
                self.vel = self.vel * -1
                self.walk_count = 0

        else: # If we are moving left
            if self.x - self.vel > self.path[0]: # If we have not reached the furthest left point on our path
                self.x += self.vel

            else:  # Change direction
                self.vel = self.vel * -1
                self.walk_count = 0

    def hit(self):

        hit_sound.play()
        if self.health > 0:
            self.health -= 1

        else: 
            self.visible = False 

def redraw_game_window():

    win.blit(bg, (0, 0))
    text = font.render("Score: " + str(score), 1, (0, 0, 0))
    win.blit(text, (350, 10))
    man.draw(win)
    goblin.draw(win)

    for bullet in bullets:
        bullet.draw(win)

    pygame.display.update()

# Main loop
font = pygame.font.SysFont("comicsans", 30, True)
man = player(300, 410, 64, 64)
goblin = enemy(100, 410, 64, 64, 450)
shoot_loop = 0
bullets = []

running = True

while running:

    clock.tick(27)

    if goblin.visible == True: 

        if man.hitbox[1] < goblin.hitbox[1] + goblin.hitbox[3] and man.hitbox[1] + man.hitbox[3] > goblin.hitbox[1]:
            if man.hitbox[0] + man.hitbox[2] > goblin.hitbox[0] and man.hitbox[0] < goblin.hitbox[0] + goblin.hitbox[2]:
                man.hit()
                score -= 5

    if shoot_loop > 0:
        shoot_loop += 1
    
    if shoot_loop > 3:
        shoot_loop = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False 

    for bullet in bullets:
        if bullet.y - bullet.radius < goblin.hitbox[1] + goblin.hitbox[3] and bullet.y + bullet.radius > goblin.hitbox[1]:
            if bullet.x + bullet.radius > goblin.hitbox[0] and bullet.x - bullet.radius < goblin.hitbox[0] + goblin.hitbox[2]:
                goblin.hit()
                score += 1
                bullets.pop(bullets.index(bullet))
        if bullet.x < 500 and bullet.x > 0:
             bullet.x += bullet.vel
        else: 
            bullets.pop(bullets.index(bullet))

    keys = pygame.key.get_pressed()

    if keys[pygame.K_SPACE] and shoot_loop == 0:
        bullet_sound.play()
        if man.left:
          facing = -1

        else:
            facing = 1

        if len(bullets) < 5:
            bullets.append(projectile(round(man.x + man.width // 2), round(man.y + man.height // 2), 6, (0, 0, 0), facing))

        shoot_loop = 1

    if keys[pygame.K_LEFT] and man.x > man.vel:

        man.x -= man.vel
        man.left = True
        man.right = False
        man.standing = False

    elif keys[pygame.K_RIGHT] and man.x < screen_width - man.width - man.vel:

        man.x += man.vel
        man.left = False
        man.right = True
        man.standing = False

    else:
        man.standing = True
        man.walk_count = 0

    if not (man.isJump):

        if keys[pygame.K_UP]:
            man.isJump = True
            man.right = False
            man.left = False
            man.walk_count = 0

    else:
        if man.jump_count >= -10:
            neg = 1

            if man.jump_count < 0:
                neg = -1
            man.y -= (man.jump_count ** 2) * 0.5 * neg
            man.jump_count -= 1

        else:
            man.isJump = False
            man.jump_count = 10

    redraw_game_window()

pygame.quit()
sys.exit()