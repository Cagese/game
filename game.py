import pygame
import os
import random

from pygame.sprite import Sprite

pygame.init()


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Не удаётся загрузить:', name)
        raise SystemExit(message)
    image = image.convert_alpha()
    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    return image


class SpriteGroup(pygame.sprite.Group):

    def __init__(self):
        super().__init__()

    def get_event(self, event):
        for sprite in self:
            sprite.get_event(event)


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        obj.rect.x = self.dx
        obj.rect.y = self.dy

    def update(self, target):
        x,y = target.pos
        self.dx = x
        self.dy = y


def movement_to_direction(movement):
    if movement == [0, 1]: return 'up'
    if movement == [0, -1]: return 'down'
    if movement == [1, 0]: return 'left'
    if movement == [-1, 0]: return 'right'


class Player(Sprite):
    def __init__(self, pos_x, pos_y, movement=None, direction='down'):
        super().__init__(hero_group)
        if movement is None:
            movement = [0, 0]
        self.image = player_image
        self.movement = movement
        self.direction = 'down'
        self.rect = self.image.get_rect().move(pos_x - 120, pos_y - 120)
        self.pos = (pos_x - 120, pos_y - 120)
        self.step = 0

    def move(self, x, y):
        if sum(map(abs, self.movement)) == 0:
            player_animation(self, 'idle', 16)
        else:
            self.pos = (x, y)
            player_animation(self, 'walk', 16)
        self.update()


def player_animation(player, type_move, player_fps):
    player.step = (player.step + 1) % (player_fps * 4)
    if sum(map(abs, player.movement)) == 2:
        if player.movement[1] == 1:
            player.image = pygame.transform.scale(
                load_image(
                    f'player\Character without weapon\{type_move}\{type_move} up{player.step // player_fps + 1}.png'),
                (256, 256))
        else:
            player.image = pygame.transform.scale(
                load_image(
                    f'player\Character without weapon\{type_move}\{type_move} down{player.step // player_fps + 1}.png'),
                (256, 256))
    else:
        if sum(map(abs, player.movement)) != 0:
            player.direction = movement_to_direction(player.movement)
        player.image = pygame.transform.scale(
            load_image(
                f'player\Character without weapon\{type_move}\{type_move} {player.direction}{player.step // player_fps + 1}.png'),
            (256, 256))




def move(hero):
    speed = 5
    x, y = hero.pos
    movement = hero.movement
    x = movement[0] * speed + x
    y = movement[1] * speed + y
    hero.move(x, y)


def generate_background():
    background_rect = background.get_rect()
    x, y = hero.pos
    dx, dy = map_size
    for x in range(x - dx * 512, screen.get_width(), background_rect.width):
        for y in range(y - dy * 512, screen.get_height(), background_rect.height):
            screen.blit(background, (x, y))


screen_size = width, height = (1000, 800)
map_size = (100, 100)
screen = pygame.display.set_mode(screen_size)
clock = pygame.time.Clock()
sprite_group = SpriteGroup()
hero_group = SpriteGroup()
camera = Camera()
FPS = 60
running = True
background = load_image(f'ground/{random.randint(1, 6)}.png')
player_image = pygame.transform.scale(load_image('player/Character without weapon/idle/idle down1.png'), (256, 256))
hero = Player(width // 2, height // 2)



#Тестовый объект для проверки отресовки спрайтов с учётом камеры (можно удалить)
test = pygame.transform.scale(load_image('player/Character without weapon/idle/idle down1.png'), (256, 256))
test_obj = pygame.sprite.Sprite(sprite_group)
test_obj.image = test
test_obj.rect = test_obj.image.get_rect()





while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            keys = pygame.key.get_pressed()
            if event.key == pygame.K_w:
                hero.movement[1] = 1
            elif event.key == pygame.K_s:
                hero.movement[1] = -1
            elif event.key == pygame.K_a:
                hero.movement[0] = 1
            elif event.key == pygame.K_d:
                hero.movement[0] = -1
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_w:
                hero.movement[1] = 0
            elif event.key == pygame.K_s:
                hero.movement[1] = 0
            elif event.key == pygame.K_a:
                hero.movement[0] = 0
            elif event.key == pygame.K_d:
                hero.movement[0] = 0
    generate_background()
    move(hero)
    camera.update(hero)
    for sprite in sprite_group:
        camera.apply(sprite)
    sprite_group.draw(screen)
    hero_group.draw(screen)

    pygame.display.flip()
    clock.tick(FPS)
