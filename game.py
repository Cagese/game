import pygame
import os
import random

from pygame.sprite import Sprite

pygame.init()


# используеться для загрузки изображений
# в случаи неправельной загрузки изображения
# генерируеться исключение не остонавливающее работу программы


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
        # наследование класса из pygame.sprite.Group
        super().__init__()

    def get_event(self, event):
        for sprite in self:
            sprite.get_event(event)


class Camera:
    def __init__(self):
        # задаём начальные координаты камеры
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        obj.rect.x = (-obj.pos[0] + self.dx)
        obj.rect.y = (-obj.pos[1] + self.dy)

    def update(self, target):
        # отслеживание передвижения и смешение камеры
        self.dx = target.pos_x + width // 2 - target.rect.w * 2
        self.dy = target.pos_y + height // 2 - target.rect.h * 2


# отслеживание нажатия клавиш и в какую сторону надо двигаться
def movement_to_direction(movement):
    if movement == [0, 1]:    return 'up'
    if movement == [0, -1]:   return 'down'
    if movement == [1, 0]:    return 'left'
    if movement == [-1, 0]:   return 'right'


class Player(Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(all_sprites, hero_group)
        self.image = player_image
        self.movement = [0, 0]
        self.direction = 'down'
        self.rect = self.image.get_rect().move(pos_x - size[0] // 2, pos_y - size[1] // 2)
        self.pos = (pos_x - size[0] // 2, pos_y - size[1] // 2)
        self.pos_x, self.pos_y = pos_x, pos_y
        self.step = 0

    def move(self, x, y, size_obj):
        if sum(map(abs, self.movement)) == 0:
            player_animation(self, 'idle', 'with sword and shield', 16, size_obj)
        else:
            self.pos = (x, y)
            self.pos_x, self.pos_y = (x, y)
            player_animation(self, 'walk', 'with sword and shield', 16, size_obj)

        self.update()


def player_animation(player, type_move, type_sprite, player_fps, size_obj):
    player.step = (player.step + 1) % (player_fps * 4)
    if sum(map(abs, player.movement)) == 2:
        if player.movement[1] == 1:
            player.image = pygame.transform.scale(
                load_image(
                    f'player\Character {type_sprite}\{type_move}\{type_move} up{player.step // player_fps + 1}.png'),
                size_obj)
        else:
            player.image = pygame.transform.scale(
                load_image(
                    f'player\Character {type_sprite}\{type_move}\{type_move} down{player.step // player_fps + 1}.png'),
                size_obj)
    else:
        if sum(map(abs, player.movement)) != 0:
            player.direction = movement_to_direction(player.movement)
        player.image = pygame.transform.scale(
            load_image(
                f'player\Character {type_sprite}\{type_move}\{type_move} {player.direction}{player.step // player_fps + 1}.png'),
            size_obj)


class Enemy(Sprite):
    def __init__(self):
        super().__init__(all_sprites, enemy_group)
        self.type = ['zombie', 'skeleton'][random.randint(0, 1)]
        self.image = pygame.transform.scale(load_image(f'enemy\skeleton\walk\left_walk1.png'),
                                            tuple(map(lambda x: x // 2, list(size))))
        self.movement = [0, 0]
        self.direction = 'down'
        self.pos_x, self.pos_y = ((hero.pos[0] + random.randint(20, 200) * random.choice([-1, 1])),
                                  (hero.pos[1] + random.randint(20, 200) * random.choice([-1, 1])))
        print(self.pos_x, self.pos_y, hero.pos)
        self.rect = self.image.get_rect().move(self.pos_x, self.pos_y)
        self.pos = (self.pos_x, self.pos_y)
        self.step = 0

    def move(self, speed):
        x1, y1 = self.pos
        x2, y2 = hero.pos
        x2, y2 = x2 - hero.rect.w, y2 - hero.rect.h
        if abs(x2 - x1) > 40:
            if x1 > x2:
                x1 -= speed
            else:
                x1 += speed
        if abs(y2 - y1) > 40:
            if y1 > y2:
                y1 -= speed
            else:
                y1 += speed
        self.pos = (x1, y1)


def move(size_obj):
    speed = 5
    x, y = hero.pos
    movement = hero.movement
    x = movement[0] * speed + x
    y = movement[1] * speed + y
    hero.move(x, y, size_obj)


def generate_background():
    background_rect = background.get_rect()
    x, y = hero.pos
    dx, dy = map_size
    for x in range(x - dx * 512, screen.get_width(), background_rect.width):
        for y in range(y - dy * 512, screen.get_height(), background_rect.height):
            screen.blit(background, (x, y))


map_size = (100, 100)
size = (256, 256)
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
screen_size = width, height = (pygame.display.get_surface().get_width(), pygame.display.get_surface().get_height())

clock = pygame.time.Clock()
all_sprites = SpriteGroup()
hero_group = SpriteGroup()
enemy_group = SpriteGroup()

FPS = 60
running = True
background = load_image(f'ground/{random.randint(1, 6)}.png')
player_image = pygame.transform.scale(load_image('player/Character without weapon/idle/idle down1.png'), (64, 64))
hero = Player(width // 2, height // 2)
camera = Camera()

# Тестовый объект для проверки отресовки спрайтов с учётом камеры (можно удалить)
# test = pygame.transform.scale(load_image('player/Character without weapon/idle/idle down1.png'), (64, 64))
# test_obj = pygame.sprite.Sprite(all_sprites)
# test_obj.image = test
# test_obj.rect = test_obj.image.get_rect()
test = 0

while running:
    test += 1
    if test % (60 * 2) == 0:
        Enemy()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_w:
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
    move(size)
    camera.update(hero)
    for sprite in enemy_group:
        sprite.move(3)
    for sprite in all_sprites:
        camera.apply(sprite)
    all_sprites.draw(screen)
    hero_group.draw(screen)

    pygame.display.flip()

    clock.tick(FPS)
