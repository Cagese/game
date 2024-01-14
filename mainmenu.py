import random

import pygame

from game import main, load_image

pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512, devicename=None)
pygame.init()


def generate_background():
    background_rect = background.get_rect()
    x, y = background_pos
    dx, dy = map_size
    for x in range(x - dx * 512, screen.get_width(), background_rect.width):
        for y in range(y - dy * 512, screen.get_height(), background_rect.height):
            screen.blit(background, (x, y))


def generate_start_button(color):
    global start_buttonR, start_buttonS, start_button
    start_button_font = pygame.font.SysFont('Consolas', 80)
    start_button = start_button_font.render('Играть', True, color)
    start_buttonR = start_button.get_rect()
    start_buttonR.x = width // 2 - start_buttonR.w // 2
    start_buttonR.y = height // 2
    start_buttonS = pygame.Surface((start_buttonR.w, start_buttonR.h))


pygame.init()
map_size = (100, 100)
size = (256, 256)
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
screen_size = width, height = (pygame.display.get_surface().get_width(), pygame.display.get_surface().get_height())
background_pos = (width // 2, height // 2)
background_velocity = (random.choice([-1, 1]), random.choice([-1, 1]))
background = load_image(f'ground/{random.randint(1, 98)}.png')
generate_start_button((0, 0, 0))

name_font = pygame.font.SysFont('Consolas', 40)
name_text = name_font.render('Выживание: Нападение Нежити', True, (255, 0, 0))

pygame.mixer.music.load(f"data/sound/ambients/Ambient {random.randint(1, 10)}.ogg")
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.3)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        elif event.type == pygame.MOUSEMOTION:
            if start_buttonR.collidepoint(event.pos):
                generate_start_button((0, 255, 0))
            else:
                generate_start_button((255, 255, 255))
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and start_buttonR.collidepoint(event.pos):
                pygame.mixer.music.stop()
                background_velocity = (random.choice([-1, 1]), random.choice([-1, 1]))
                background = load_image(f'ground/{random.randint(1, 98)}.png')
                main()
                pygame.mixer.music.load(f"data/sound/ambients/Ambient {random.randint(1, 10)}.ogg")
                pygame.mixer.music.play(-1)
                pygame.mixer.music.set_volume(0.3)

    generate_background()
    background_pos = background_pos[0] + background_velocity[0], background_pos[1] + background_velocity[1]

    screen.blit(name_text, (width // 2 - name_text.get_width() // 2, height // 4))
    screen.blit(start_button, (start_buttonR.x, start_buttonR.y))

    pygame.display.flip()
