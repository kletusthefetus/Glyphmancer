import pygame, os
from Projectile import Projectile
from Entity import Entity

GRAVITY = 0.75

class Player(Entity):
    def __init__(self, char_type, x, y, scale, speed):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.damage = False
        self.invincibility = 30
        self.invincible = False
        self.char_type = char_type
        self.speed = speed
        self.health = 100
        self.climb = False
        self.key = False
        self.dx = 0
        self.end = False
        self.dy = 0
        self.scale = scale
        self.climbing_up = False
        self.climbing_down = False
        self.max_health = self.health
        self.cast_cooldown = 0
        self.jump = False
        self.in_air = True
        self.attacking = False
        self.dodging = False
        self.vel_y = 0
        self.vel_x = 0
        self.direction = 1
        self.flip = False
        self.animation_list = []
        self.action = 'Idle'
        self.frame_index = 0
        self.dict = {'Idle' : 0, 'Running' : 1, 'Jumping' : 2, 'Attack' : 3, 'Dodging' : 4, 'Death' : 5, 'Damage' : 6}
        self.update_time = pygame.time.get_ticks()
        #load all animation types for players
        animation_types = ['Idle', 'Running', 'Jumping', 'Attack', 'Dodging', 'Death', 'Damage']
        for animation in animation_types:
            #reset temporary list of images
            temp_list = []
            #count number of files in folder
            num_of_frames = len(os.listdir(f'Assets/Character/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'Assets/Character/{animation}/{i}.png')
                img = pygame.transform.scale(img, (int(img.get_width() * scale),int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)
        self.image = self.animation_list[self.dict.get(self.action)][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        #adjust for smaller box
        self.width = self.image.get_width() - 24

    def update(self):
        if self.dodging:
            self.invicible = True
        self.update_animation()
        self.check_alive()
        #update cooldown
        if self.cast_cooldown > 0:
            self.cast_cooldown -= 1

        if self.invincible:
            self.invincibility -= 1
            if self.invincibility == 0:
                self.invincible = False

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.speed = 0
            self.update_action('Death')


    def move(self, moving_left, moving_right, obstacle_list, platform_group, ladder_group, key, hazard_group, closed_door, enemy_group):
        #reset movement variables
        screen_scroll = 0
        self.dx = 0
        self.dy = 0

        #assign movement variables
        if moving_left:
            self.dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            self.dx = self.speed
            self.flip = False
            self.direction = 1

        if self.climbing_up:
            self.dy = -self.speed
        if self.climbing_down:
            self.dy = self.speed

        if self.jump and not self.in_air:
            self.vel_y = -11
            self.jump = False
            self.in_air = True

        if self.dodging:
            self.dx = self.speed * 2 * self.direction

        #apply gravity
        if not self.climb:
            self.vel_y += GRAVITY
            if self.vel_y > 10:
                self.vel_y = 10
            self.dy += self.vel_y

        for door in closed_door:
            if not self.key:
                if door.rect.colliderect(self.rect.x + self.dx + 12, self.rect.y, self.width, self.image.get_height()):
                    self.dx = 0
                if door.rect.colliderect(self.rect.x + 12, self.rect.y + self.dy, self.width, self.image.get_height()):
                    if self.vel_y >= 0 and self.rect.y < (door.rect.y - self.image.get_height()//2):
                        self.vel_y = 0
                        self.in_air = False
                        self.dy = door.rect.top - self.rect.bottom
            else:
                door.open = True

        for hazard in hazard_group:
            if hazard.rect.colliderect(self.rect.x + self.dx + 12, self.rect.y, self.width, self.image.get_height()):
                self.dx = 0
                if not self.invincible:
                    self.health -= 15
                    self.damage = True
                    self.invicible = True
                    self.update_action('Damage')
            if hazard.rect.colliderect(self.rect.x + 12, self.rect.y + self.dy, self.width, self.image.get_height()):
                if self.vel_y >= 0 and self.rect.y < (hazard.rect.y - self.image.get_height()//2):
                    self.vel_y = 0
                    self.in_air = False
                    self.dy = hazard.rect.top - self.rect.bottom
                    if not self.invincible:
                        self.health -= 15
                        self.damage = True
                        self.invincible = True
                        self.update_action('Damage')

        for tile in obstacle_list:
            #check for collision in the x direction
            if tile[1].colliderect(self.rect.x + self.dx + 12, self.rect.y, self.width, self.image.get_height()):
                self.dx = 0
            #check for collision in the y direction
            if tile[1].colliderect(self.rect.x + 12, self.rect.y + self.dy, self.width, self.image.get_height()):
                #check if below the ground aka jumping
                if self.vel_y < 0:
                    self.vel_y = 0
                    self.dy = tile[1].bottom - self.rect.top
                #check if above the ground aka falling
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    self.dy = tile[1].top - self.rect.bottom

        for platform in platform_group:
            if platform.rect.colliderect(self.rect.x + 12, self.rect.y + self.dy, self.width, self.image.get_height()):
                if self.vel_y >= 0 and self.rect.y < (platform.rect.y - self.image.get_height()//2):
                    self.vel_y = 0
                    self.in_air = False
                    self.dy = platform.rect.top - self.rect.bottom

        for enemy in enemy_group:
            #check for collision in the x direction
            if enemy.rect.colliderect(self.rect.x + self.dx + 12, self.rect.y, self.width, self.image.get_height()):
                if not self.invincible:
                    self.health -= 15
                    self.damage = True
                    self.invicible = True
                    self.update_action('Damage')
            #check for collision in the y direction
            elif enemy.rect.colliderect(self.rect.x + 12, self.rect.y + self.dy, self.width, self.image.get_height()):
                if not self.invincible:
                    self.health -= 15
                    self.damage = True
                    self.invicible = True
                    self.update_action('Damage')

        if pygame.sprite.spritecollideany(self, ladder_group, collided = None):
            self.climb = True
        else:
            self.climb = False

        if pygame.sprite.spritecollideany(self, key, collided = None):
            self.key = True
            key.empty()

        #update rectangle position
        if self.alive:
            self.rect.x += self.dx
            self.rect.y += self.dy


    def update_action(self, new_action):
        #check if the new action is separate from the last one
        if new_action != self.action:
            self.action = new_action
            #update animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def cast(self):
        if self.cast_cooldown == 0:
            self.cast_cooldown = 20
            spell = Projectile(self.rect.centerx + (self.rect.size[0]*1.3 * self.direction), self.rect.centery, self.direction, 10, self.scale)
            Projectile.projectile_group.add(spell)

    def update_animation(self):
        #update animation
        ANIMATION_COOLDOWN = 150

        if self.action == 'Attack':
            ANIMATION_COOLDOWN = 30
        #update animation frame
        self.image = self.animation_list[self.dict.get(self.action)][self.frame_index]
        self.image = pygame.transform.flip(self.image, self.flip, False)
        #check if enough time has passed since the last update
        if (pygame.time.get_ticks() - self.update_time) > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        if self.frame_index >= len(self.animation_list[self.dict.get(self.action)]):
            if self.action == 'Attack':#stop attacking after animation is finished
                self.attacking = False
            if self.action == 'Dodging':#stop dodging after animation is finished
                self.dodging = False
                self.invincible = False
            if self.action == 'Damage':
                self.damage = False
                self.invincibility = 30      
            if self.action == 'Death':#stop death animation after it is finished
                self.frame_index = len(self.animation_list[self.dict.get(self.action)]) - 1
                self.end = True
            else:
                self.frame_index = 0

    def draw(self, screen):
        screen.blit(self.image, self.rect) 

