import pygame
import os
import random
import math

pygame.font.init()
pygame.mixer.init()

WIDTH, HEIGHT = 900, 500
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("React in Space")
pygame_icon = pygame.image.load(os.path.join('Assets', 'spaceship_yellow.png'))
pygame.display.set_icon(pygame_icon)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

BORDER = pygame.Rect(WIDTH//2 - 5, 0, 10, HEIGHT)

BULLET_HIT_SOUND = pygame.mixer.Sound('Assets/Grenade+1.mp3')
BULLET_FIRE_SOUND = pygame.mixer.Sound('Assets/Gun+Silencer.mp3')

WINNER_FONT = pygame.font.SysFont('comicsans', 100)
SCORE_FONT = pygame.font.SysFont('comicsans', 30)

FPS = 60
VEL = 5
BULLET_VEL = 7
MAX_BULLETS = 3
SPACESHIP_WIDTH, SPACESHIP_HEIGHT = 55, 40

YELLOW_HIT = pygame.USEREVENT + 1
RED_HIT = pygame.USEREVENT + 2
TARGET_HIT = pygame.USEREVENT + 3

class Spaceship:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.width = img.get_width()
        self.height = img.get_height()

class Target:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Particle:
    def __init__(self, x, y, color, vel):
        self.x = x
        self.y = y
        self.color = color
        self.radius = random.randint(2, 5)
        self.vel = vel
        self.life = 20  # Number of frames the particle will exist

    def draw(self, win):
        pygame.draw.circle(win, self.color, (self.x, self.y), self.radius)

    def move(self):
        self.x += self.vel[0]
        self.y += self.vel[1]
        self.life -= 1

def draw_window(red, yellow, red_bullets, yellow_bullets, red_score, yellow_score, target, particles):
    WIN.fill(BLACK)
    pygame.draw.rect(WIN, WHITE, BORDER)

    red_score_text = SCORE_FONT.render(
        "Score: " + str(red_score), 1, WHITE)
    yellow_score_text = SCORE_FONT.render(
        "Score: " + str(yellow_score), 1, WHITE)
    WIN.blit(red_score_text, (WIDTH - red_score_text.get_width() - 10, 40))
    WIN.blit(yellow_score_text, (10, 40))

    WIN.blit(YELLOW_SPACESHIP, (yellow.x, yellow.y))
    WIN.blit(RED_SPACESHIP, (red.x, red.y))

    for bullet in red_bullets:
        pygame.draw.rect(WIN, RED, bullet)

    for bullet in yellow_bullets:
        pygame.draw.rect(WIN, YELLOW, bullet)

    pygame.draw.circle(WIN, WHITE, (target.x, target.y), 30)

    for particle in particles:
        particle.draw(WIN)

    pygame.display.update()

def yellow_handle_movement(keys_pressed, yellow):
    if keys_pressed[pygame.K_z] and yellow.y - VEL > 0:  # UP
        yellow.y -= VEL
    if keys_pressed[pygame.K_s] and yellow.y + VEL + yellow.height < HEIGHT - 15:  # DOWN
        yellow.y += VEL

def red_handle_movement(keys_pressed, red):
    if keys_pressed[pygame.K_UP] and red.y - VEL > 0:  # UP
        red.y -= VEL
    if keys_pressed[pygame.K_DOWN] and red.y + VEL + red.height < HEIGHT - 15:  # DOWN
        red.y += VEL

def handle_bullets(yellow_bullets, red_bullets, yellow, red, target, scores, particles):
    red_score, yellow_score = scores

    for bullet in yellow_bullets:
        bullet.x += BULLET_VEL
        if target.y - 30 < bullet.y < target.y + 30 and target.x - 30 < bullet.x < target.x + 30:
            pygame.event.post(pygame.event.Event(TARGET_HIT))
            yellow_bullets.remove(bullet)
            yellow_score += 100
            emit_particles(target.x, target.y, particles, (BULLET_VEL, 0))
        elif bullet.x > WIDTH:
            yellow_bullets.remove(bullet)

    for bullet in red_bullets:
        bullet.x -= BULLET_VEL
        if target.y - 30 < bullet.y < target.y + 30 and target.x - 30 < bullet.x < target.x + 30:
            pygame.event.post(pygame.event.Event(TARGET_HIT))
            red_bullets.remove(bullet)
            red_score += 100
            emit_particles(target.x, target.y, particles, (-BULLET_VEL, 0))
        elif bullet.x < 0:
            red_bullets.remove(bullet)

    scores[0] = red_score
    scores[1] = yellow_score

def emit_particles(x, y, particles, bullet_vel):
    for _ in range(50):
        angle = random.uniform(0, math.pi * 2)  # Random angle in radians
        vel = (math.cos(angle) * random.randint(1, 5), math.sin(angle) * random.randint(1, 5))
        particle = Particle(x, y, (random.randint(200, 255), random.randint(0, 100), 0), vel)
        particles.append(particle)

def move_particles(particles):
    for particle in particles:
        particle.move()

        if particle.life <= 0:
            particles.remove(particle)

def game_loop():
    yellow = Spaceship(10, HEIGHT//2, YELLOW_SPACESHIP)
    red = Spaceship(WIDTH -50, HEIGHT//2, RED_SPACESHIP)

    red_bullets = []
    yellow_bullets = []

    red_score = 0
    yellow_score = 0

    target = Target(WIDTH//2, random.randint(0, HEIGHT))

    scores = [red_score, yellow_score]

    particles = []

    clock = pygame.time.Clock()
    run = True
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == TARGET_HIT:
                target.y = random.randint(0, HEIGHT)

        keys_pressed = pygame.key.get_pressed()

        yellow_handle_movement(keys_pressed, yellow)
        red_handle_movement(keys_pressed, red)

        if keys_pressed[pygame.K_e] and len(yellow_bullets) < MAX_BULLETS:
            bullet = pygame.Rect(yellow.x + yellow.width, yellow.y + yellow.height//2 - 2, 10, 5)
            yellow_bullets.append(bullet)
            #BULLET_FIRE_SOUND.play()

        if keys_pressed[pygame.K_p] and len(red_bullets) < MAX_BULLETS:
            bullet = pygame.Rect(red.x, red.y + red.height//2 - 2, 10, 5)
            red_bullets.append(bullet)
            #BULLET_FIRE_SOUND.play()

        handle_bullets(yellow_bullets, red_bullets, yellow, red, target, scores, particles)
        move_particles(particles)

        draw_window(red, yellow, red_bullets, yellow_bullets,  scores[0], scores[1], target, particles)

    pygame.quit()

if __name__ == "__main__":
    YELLOW_SPACESHIP_IMAGE = pygame.image.load(os.path.join('Assets', 'spaceship_yellow.png'))
    YELLOW_SPACESHIP = pygame.transform.rotate(pygame.transform.scale(YELLOW_SPACESHIP_IMAGE, (SPACESHIP_WIDTH, SPACESHIP_HEIGHT)), 90)

    RED_SPACESHIP_IMAGE = pygame.image.load(os.path.join('Assets', 'spaceship_red.png'))
    RED_SPACESHIP = pygame.transform.rotate(pygame.transform.scale(RED_SPACESHIP_IMAGE, (SPACESHIP_WIDTH, SPACESHIP_HEIGHT)), 270)

    game_loop()
