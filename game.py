import pygame
import os
import random
from PIL import Image

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
    if movement == [0, 1]:
        return 'up'
    if movement == [0, -1]:
        return 'down'
    if movement == [1, 0]:
        return 'left'
    if movement == [-1, 0]:
        return 'right'


class Player(Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(all_sprites, hero_group)
        self.image = player_image
        self.rect = self.image.get_rect().move(pos_x - size[0] // 2, pos_y - size[1] // 2)

        self.movement = [0, 0]
        self.direction = 'down'
        self.pos = (pos_x - size[0] // 2, pos_y - size[1] // 2)
        self.pos_x, self.pos_y = pos_x, pos_y

        self.hitboxes = []
        self.is_attack = False
        self.immunity = 0
        self.max_hp = 100
        self.hp = 100
        self.xp = 0
        self.reg = 0.01
        self.strength = 25

        self.step = 0

    def update_hitboxes(self):
        base_hitbox = self.rect.copy().move(size[0] // 2 - 32, size[1] // 2 - 32)
        up_hitbox = base_hitbox.copy().move(0, -5)
        up_hitbox.h = 16

        down_hitbox = base_hitbox.copy().move(0, 5)
        down_hitbox.y += down_hitbox.h - 16
        down_hitbox.h = 16

        left_hitbox = base_hitbox.copy().move(-5, 0)
        left_hitbox.w = 16

        right_hitbox = base_hitbox.copy().move(5, 0)
        right_hitbox.x += right_hitbox.w - 16
        right_hitbox.w = 16

        self.hitboxes = list(zip([up_hitbox, down_hitbox, left_hitbox, right_hitbox], ['up', 'down', 'left', 'right'],
                                 [(0, -10), (0, 10), (-10, 0), (10, 0)]))
        if debug:
            pygame.draw.rect(screen, pygame.Color('yellow'), up_hitbox, width=5)
            pygame.draw.rect(screen, pygame.Color('blue'), down_hitbox, width=5)
            pygame.draw.rect(screen, pygame.Color('green'), left_hitbox, width=5)
            pygame.draw.rect(screen, pygame.Color('purple'), right_hitbox, width=5)

    def take_damage(self, damage):
        if self.immunity <= 0:
            self.hp -= damage
            if self.hp <= 0:
                self.kill()
            self.immunity = 2
            self.immunity_start_time = counter
        else:
            if self.immunity_start_time + self.immunity <= counter:
                self.immunity = 0

    def attack(self):
        attack_hitbox = self.rect.copy().move(size[0] // 2 - 32, size[1] // 2 - 32)
        for i in self.hitboxes:
            if self.direction == i[1]:
                attack_hitbox = i[0].copy().move(tuple(map(lambda x: x * 2, i[2])))
        if debug:
            pygame.draw.rect(screen, pygame.Color('red'), attack_hitbox, width=5)
        for enemy in enemy_group:
            if attack_hitbox.colliderect(enemy.hitbox):
                enemy.take_damage(self.strength)

    def move(self, x, y, size_obj):
        self.update_hitboxes()

        if self.hp > 0:
            healthbar = self.hitboxes[0][0].copy()
            healthbar.h = 5
            healthbar.y -= 10
            healthbar_background = healthbar.copy()
            healthbar_background.h = 5
            healthbar.w = self.rect.w * (self.hp / self.max_hp)
            pygame.draw.rect(screen, (128, 128, 128), healthbar_background)
            pygame.draw.rect(screen, (255, 0, 0), healthbar)
        if self.xp > 100:
            self.xp -= 100
            global choice_upgrade
            choice_upgrade = True
        if self.hp != self.max_hp:
            self.hp += self.reg
        if self.hp > self.max_hp:
            self.hp = self.max_hp

        if self.is_attack:
            player_animation(self, 'attack', 'with sword and shield', 8, size_obj)
            self.attack()
            return 0

        if sum(map(abs, self.movement)) == 0:
            player_animation(self, 'idle', 'with sword and shield', 16, size_obj)
        else:
            self.pos = (x, y)
            self.pos_x, self.pos_y = (x, y)
            player_animation(self, 'walk', 'with sword and shield', 16, size_obj)


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
        self.dead = False
        self.type = ['zombie', 'skeleton'][random.randint(0, 1)]
        self.size = tuple(map(lambda x: x // 2, list(size)))
        self.image = pygame.transform.scale(load_image(f'enemy\{self.type}\walk\left_walk1.png'),
                                            self.size)
        self.last_update = pygame.time.get_ticks()

        self.direction = 'left'
        self.pos_x, self.pos_y = ((hero.pos[0] + random.randint(200, 500) * random.choice([-1, 1])),
                                  (hero.pos[1] + random.randint(200, 500) * random.choice([-1, 1])))
        self.rect = self.image.get_rect().move(self.pos_x, self.pos_y)
        self.pos = (self.pos_x, self.pos_y)

        global enemy_max_health
        self.max_hp = enemy_max_health
        self.hp = enemy_max_health
        self.dead = False
        self.show_healthbar = False
        self.immunity = 0

        self.update_hitbox()
        self.step = 0

    def take_damage(self, damage):
        if self.immunity <= 0:
            self.hp -= damage
            if self.hp <= 0:
                self.dead = True
            self.show_healthbar = True
            self.immunity = 1
            self.immunity_start_time = counter
        else:
            if self.immunity_start_time + self.immunity <= counter:
                self.immunity = 0

    def attack(self):
        if self.type == 'skeleton':
            enemy_animation(self, 'attack', 120, 4)
        elif self.type == 'zombie':
            enemy_animation(self, 'attack', 120, 8)
        hero.take_damage(enemy_strength)

    def update_hitbox(self):
        self.hitbox = self.rect.copy()
        self.hitbox.x += self.hitbox.w // 4
        self.hitbox.w //= 2

    def move(self, speed):
        self.update_hitbox()

        if debug:
            pygame.draw.rect(screen, (0, 0, 0), self.hitbox, width=5)

        if self.dead:
            if self.type == 'skeleton':
                if not (self.step % 5 + 1 == 5):
                    enemy_animation(self, 'dead', 120, 5)
                else:
                    hero.xp += 100
                    self.kill()
            elif self.type == 'zombie':
                if not (self.step % 8 + 1 == 8):
                    enemy_animation(self, 'dead', 120, 8)
                else:
                    hero.xp += 100
                    self.kill()
            return 0

        if self.show_healthbar and self.hp > 0:
            healthbar = self.rect.copy()
            healthbar.h = 5
            healthbar_background = self.rect.copy()
            healthbar_background.h = 5
            healthbar.w = self.rect.w * (self.hp / self.max_hp)
            pygame.draw.rect(screen, (128, 128, 128), healthbar_background)
            pygame.draw.rect(screen, (255, 0, 0), healthbar)

        for i in hero.hitboxes:
            if self.hitbox.colliderect(i[0]):
                self.attack()
                return 0

        if len(pygame.sprite.spritecollide(self, enemy_group, False)) != 1:
            speed = random.randint(0, speed)

        x1, y1 = self.pos
        x2, y2 = hero.pos
        x2, y2 = x2 - hero.rect.w, y2 - hero.rect.h

        def Ox():
            nonlocal x1, x2, y1, y2, speed
            if abs(x2 - x1) > 40:
                if x1 > x2:
                    self.direction = 'right'
                    x1 -= speed
                else:
                    self.direction = 'left'
                    x1 += speed
            return x1

        def Oy():
            nonlocal x1, x2, y1, y2, speed
            if abs(y2 - y1) > 40:
                if y1 > y2:
                    y1 -= speed
                else:
                    y1 += speed
            return y1

        if random.randint(0, 1):
            Ox()
        else:
            Oy()
        enemy_animation(self, 'walk', 120, 6)
        self.pos = (x1, y1)


def enemy_animation(enemy, type_move, enemy_tick, sprite_count):
    now = pygame.time.get_ticks()
    if now - enemy.last_update > enemy_tick:
        enemy.last_update = now
        enemy.step = (enemy.step + 1) % sprite_count

    direction = enemy.direction
    enemy.image = pygame.transform.scale(
        load_image(f'enemy\{enemy.type}\{type_move}\{direction}_{type_move}{enemy.step % sprite_count + 1}.png'),
        enemy.size)


class Gui_book(Sprite):
    def __init__(self):
        super().__init__(GUI_group)
        self.size = size
        self.image = pygame.transform.scale_by(load_image(f'GUI\Book.png'),8)

        self.rect = self.image.get_rect().move(self.image.get_width()//4,
                                               self.image.get_height()//4)
        self.hp_rect = self.rect.copy()
        self.hp_rect.w //=2
        self.att_rect = self.hp_rect.copy()
        self.att_rect.x += self.hp_rect.w


def move(size_obj):
    speed = 8
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
pygame.time.set_timer(pygame.USEREVENT, 1000)

all_sprites = SpriteGroup()
hero_group = SpriteGroup()
enemy_group = SpriteGroup()
GUI_group = SpriteGroup()

FPS = 60
running = True
background = load_image(f'ground/{random.randint(1, 98)}.png')
player_image = pygame.transform.scale(load_image('player/Character without weapon/idle/idle down1.png'), (64, 64))
hero = Player(width // 2, height // 2)
camera = Camera()

debug = True

counter = 0
counter_font = pygame.font.SysFont('Consolas', 60)
stat_font = pygame.font.SysFont('Consolas', 40)

enemy_max_health = 100
enemy_strength = 10
difficulty = 20

choice_upgrade = False
book = Gui_book()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.USEREVENT and not choice_upgrade:
            counter += 1
            if counter % 30 == 0:
                enemy_max_health *= 1 + (difficulty*1.5) / 100
                enemy_strength *= 1 + (difficulty*1.5) / 100
            if counter % 2 == 0 and len(enemy_group) <= 100:
                Enemy()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and choice_upgrade:
                if book.hp_rect.collidepoint(event.pos):
                    hero.max_hp *= 1 + difficulty/100
                    hero.reg *= 1 + difficulty/100
                elif book.att_rect.collidepoint(event.pos):
                    hero.strength *= 1 + difficulty/100
                choice_upgrade = False
            if event.button == 1:
                hero.is_attack = True
            elif event.button == 3:
                print('right')
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                hero.is_attack = False
            elif event.button == 3:
                print('right')
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
    for sprite in all_sprites:
        camera.apply(sprite)
    screen.blit(counter_font.render(str(counter), True, (155, 0, 0, 100)), (width // 2 - 16, height // 4))
    all_sprites.draw(screen)
    screen.blit(stat_font.render(f'max hp:{str(round(hero.max_hp))} hp reg:{str(round(hero.reg * 100))} att:{str(round(hero.strength))}', True, (255, 255, 255)), (10, 0))

    if not choice_upgrade:
        move(size)
        camera.update(hero)
        for sprite in enemy_group:

            sprite.move(5)
    else:
        GUI_group.draw(screen)




    pygame.display.flip()
    clock.tick(FPS)
