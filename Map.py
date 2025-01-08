import pygame, os
from Projectile import Projectile
from Player import Player
from Enemy import Enemy
import csv

COLS = 150
ROWS = 100
SCREEN_HEIGHT = 600
SCREEN_WIDTH = 800
TILE_SIZE = SCREEN_HEIGHT // 30
TILE_TYPES = 114
BG = (21, 20, 54)



class World:

    tile_list = []
    obstacle_list = []
    platform_group = pygame.sprite.Group()
    ladder_group = pygame.sprite.Group()
    key = pygame.sprite.Group()
    decoration_group = pygame.sprite.Group()
    closed_door = pygame.sprite.Group()
    destructible_group = pygame.sprite.Group()
    hazard_group = pygame.sprite.Group()

    SCROLL_THRESH = 370
    screen_scroll_x = 0
    screen_scroll_y = 0
    bg_scroll = 0

    player_group = pygame.sprite.Group()
    enemy_group = pygame.sprite.Group()
    entity_group = pygame.sprite.Group()

    def __init__(self):
        self.moving_left = False
        self.moving_right = False
        self.background = pygame.image.load('Assets/Background/Dungeon_brick_wall_grey.png').convert_alpha()
        self.scale = 1

        for x in range(TILE_TYPES):
            img = pygame.image.load(f'Assets/Map/{x}.png')
            img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
            World.tile_list.append(img)

        #create empty tile list
        world_data = []
        for row in range(ROWS):
            r = [-1] * COLS
            world_data.append(r)
        #load in level data and create world
        #edit this to implement more than one level
        with open('Assets/Map/Level2.csv', newline = '') as csvfile:
            reader = csv.reader(csvfile, delimiter = ',')
            for x, row in enumerate(reader):
                for y, tile in enumerate(row):
                    world_data[x][y] = int(tile)

        self.process_data(world_data)

    def draw_bg(self, screen):
        screen.fill(BG)
        screen.blit(self.background,(0,0))
                   
    def process_data(self, data):
        #iterate through each value in level data file
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = World.tile_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    if (tile >= 0 and tile <= 67) or tile == 75:
                        World.obstacle_list.append(tile_data)
                    if (tile == 86 or tile == 95):
                        door = Door(img, img_rect.x, img_rect.y)
                        World.closed_door.add(door)
                    if tile == 112:#create player
                        player = Player('player', img_rect.x + 100, img_rect.y - 20, self.scale, 5)
                        World.player_group.add(player)
                        World.entity_group.add(player)
                    if tile == 113:#create enemy
                        enemy = Enemy('enemy', img_rect.x, img_rect.y, self.scale, 5)
                        World.enemy_group.add(enemy)
                        World.entity_group.add(enemy)
                    if (tile >= 68 and tile <= 70) or (tile >= 79 and tile <= 81):
                        platform = Platform(img, img_rect.x, img_rect.y)
                        World.platform_group.add(platform)
                    if (tile == 71 or tile == 90):
                        ladder = Ladder(img, img_rect.x, img_rect.y)
                        World.ladder_group.add(ladder)
                    if tile == 76:
                        key = Key(img, img_rect.x, img_rect.y)
                        World.key.add(key)
                    if tile == 83 or tile == 84 or (tile >= 97 and tile <= 102):
                        decoration = Decoration(img, img_rect.x, img_rect.y)
                        World.decoration_group.add(decoration)
                    if tile == 85 or (tile >= 103 and tile <= 105):
                        destructible = Destructible(img, img_rect.x, img_rect.y)
                        World.destructible_group.add(destructible)
                    if tile >= 106 and tile <= 111:
                        hazard = Hazard(img, img_rect.x, img_rect.y)
                        World.hazard_group.add(hazard)



    
    def update(self):
        #update all relevant objects
        for tile in World.obstacle_list:
            tile[1][0] += World.screen_scroll_x
            tile[1][1] += World.screen_scroll_y
        for enemy in World.enemy_group:
            enemy.rect.x += World.screen_scroll_x
            enemy.rect.y += World.screen_scroll_y
        World.enemy_group.update(World.obstacle_list, World.platform_group, World.hazard_group)
        World.player_group.update()
        World.closed_door.update()
        World.platform_group.update()
        World.ladder_group.update()
        World.key.update()
        World.decoration_group.update()
        World.destructible_group.update()
        World.hazard_group.update()
        for proj in Projectile.projectile_group:
            proj.rect.x += World.screen_scroll_x
            proj.rect.y += World.screen_scroll_y
        Projectile.projectile_group.update(self.entity_group)
        for player in World.player_group:
            if player.alive and not player.damage:
                if player.dodging:
                    player.update_action('Dodging')#set dodging animation
                elif player.attacking:
                    player.update_action('Attack')#set attacking animation
                    player.cast()
                elif player.in_air:
                    player.update_action('Jumping') #set jumping animation
                elif self.moving_left or self.moving_right:
                    player.update_action('Running') #set running animation
                else:
                    player.update_action('Idle') #set idle animation
                player.move(self.moving_left, self.moving_right, World.obstacle_list, World.platform_group, World.ladder_group, World.key, World.hazard_group, World.closed_door, World.enemy_group)
                if player.dx != 0:
                    player.rect.x -= player.dx
                    World.screen_scroll_x = -player.dx
                else:
                    World.screen_scroll_x = 0
                    if player.rect.right > SCREEN_WIDTH - World.SCROLL_THRESH or player.rect.left < World.SCROLL_THRESH:
                        if player.rect.right > SCREEN_WIDTH - World.SCROLL_THRESH:
                            player.rect.x -= 4
                            World.screen_scroll_x = -4
                        else:
                            player.rect.x += 4
                            World.screen_scroll_x = 4
                    else:
                       World.screen_scroll_x = 0
                for door in World.closed_door:
                    if player.rect.x > door.rect.x:
                        return False, "You Win!"
            return not player.end, "You Died!"

             #   if player.rect.bottom > SCREEN_HEIGHT - World.SCROLL_THRESH or player.rect.top < World.SCROLL_THRESH:
              #      if player.dy != 0:
               #         player.rect.y -= player.dy
                #        World.screen_scroll_y = -player.dy
                 #   else:
                  #      if player.rect.bottom > SCREEN_HEIGHT - World.SCROLL_THRESH:
                   #         player.rect.y -= 3
                    #        World.screen_scroll_y = -3
                     #   else:
                      #      player.rect.y += 3
                       #     World.screen_scroll_y = 3
               # else:
                #    World.screen_scroll_y = 0


    def check_input(self, event):
        for player in World.player_group:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    self.moving_left = True
                if event.key == pygame.K_d:
                    self.moving_right = True
                if event.key == pygame.K_SPACE and player.alive == True:
                    player.jump = True
                    player.climb = False
                    player.climbing_up = False#jumping ladder glitch fix later
                if event.key == pygame.K_e and player.alive == True:
                    player.attacking = True
                if event.key == pygame.K_LSHIFT and player.alive == True:
                    player.dodging = True
                if event.key == pygame.K_w and player.climb == True:
                    player.climbing_up = True
                if event.key == pygame.K_s and player.climb == True:
                    player.climbing_down = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    self.moving_left = False
                if event.key == pygame.K_d:
                    self.moving_right = False
                if event.key == pygame.K_w:
                    player.climbing_up = False
                if event.key == pygame.K_s:
                    player.climbing_down = False


    def draw(self, screen):
        self.draw_bg(screen)
        #draw obstacles
        for tile in World.obstacle_list:
            screen.blit(tile[0], tile[1])
        World.platform_group.draw(screen)
        World.ladder_group.draw(screen)
        World.key.draw(screen)
        World.closed_door.draw(screen)
        World.decoration_group.draw(screen)
        World.destructible_group.draw(screen)
        World.hazard_group.draw(screen)
        World.enemy_group.draw(screen)
        World.player_group.draw(screen)
        Projectile.projectile_group.draw(screen)


class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y)

    def update(self):
        self.rect.x += World.screen_scroll_x
        self.rect.y += World.screen_scroll_y

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Hazard(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y)

    def update(self):
        self.rect.x += World.screen_scroll_x
        self.rect.y += World.screen_scroll_y

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Ladder(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y)

    def update(self):
        self.rect.x += World.screen_scroll_x
        self.rect.y += World.screen_scroll_y

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Key(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y)

    def update(self):
        self.rect.x += World.screen_scroll_x
        self.rect.y += World.screen_scroll_y

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Destructible(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y)

    def update(self):
        self.rect.x += World.screen_scroll_x
        self.rect.y += World.screen_scroll_y

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Platform(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y)

    def update(self):
        self.rect.x += World.screen_scroll_x
        self.rect.y += World.screen_scroll_y

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Door(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.open = False
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y)

    def update(self):
        self.rect.x += World.screen_scroll_x
        self.rect.y += World.screen_scroll_y
        if self.open:
            self.image = World.tile_list[96]

    def draw(self, screen):
        screen.blit(self.image, self.rect)


