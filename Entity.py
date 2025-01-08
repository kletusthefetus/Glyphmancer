import pygame, os
from Projectile import Projectile

GRAVITY = 0.75

class Entity(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.health = 100
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
        self.action = 0
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        if char_type == 'player':
            #load all animation types for players
            animation_types = ['Idle', 'Running', 'Jumping', 'Attack', 'Dodging', 'Death']
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
            self.image = self.animation_list[self.action][self.frame_index]
        elif char_type == 'enemy':
           #load all animation types for players
            animation_types = ['Idle', 'Jump', 'Attack']
            for animation in animation_types:
                #reset temporary list of images
                temp_list = []
                #count number of files in folder
                num_of_frames = len(os.listdir(f'Assets/Enemies/BlueBlue/{animation}'))
                for i in range(num_of_frames):
                    img = pygame.image.load(f'Assets/Enemies/BlueBlue/{animation}/{i}.png')
                    img = pygame.transform.scale(img, (int(img.get_width() * scale),int(img.get_height() * scale)))
                    temp_list.append(img)
                self.animation_list.append(temp_list)
            self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)

    def update(self):
        self.update_animation()
        #update cooldown
        if self.cast_cooldown > 0:
            self.cast_cooldown -= 1

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.speed = 0


    def move(self, moving_left, moving_right):
        #reset movement variables
        dx = 0
        dy = 0

        #assign movement variables
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        if self.jump and not self.in_air:
            self.vel_y = -11
            self.jump = False
            self.in_air = True

        if self.dodging:
            dx = self.speed * 2 * self.direction

        #apply gravity
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y

        #check collision with floor
        if self.rect.bottom + dy > 400:
            dy = 400 - self.rect.bottom
            self.in_air = False

        #update rectangle position
        self.rect.x += dx
        self.rect.y += dy

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
            spell = Projectile(self.rect.centerx + (self.rect.size[0]*1.3 * self.direction), self.rect.centery, self.direction, 10, 2)
            Projectile.projectile_group.add(spell)

    def update_animation(self):
        #update animation
        ANIMATION_COOLDOWN = 150

        if self.action == 3:
            ANIMATION_COOLDOWN = 30
        #update animation frame
        self.image = self.animation_list[self.action][self.frame_index]
        #check if enough time has passed since the last update
        if (pygame.time.get_ticks() - self.update_time) > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:#stop attacking after animation is finished
                self.attacking = False
            if self.action == 4:#stop dodging after animation is finished
                self.dodging = False
            self.frame_index = 0

    def draw(self, screen):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect) 

