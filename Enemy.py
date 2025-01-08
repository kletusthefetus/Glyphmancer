import pygame, os
import random
from Projectile import Projectile
from Entity import Entity


GRAVITY = 0.75

class Enemy(Entity):
    def __init__(self, char_type, x, y, scale, speed):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = 'enemy'
        self.speed = speed
        self.health = 100
        self.max_health = self.health
        self.jump_timer = random.randint(100,300)
        self.jump = False
        self.damage = False
        self.in_air = True
        self.attacking = False
        self.direction = 1
        self.dodging = False
        self.dx = 0
        self.dy = 0
        self.vel_y = 0
        self.vel_x = 0
        self.direction = 1
        self.flip = False
        self.animation_list = []
        self.action = 'Idle'
        self.frame_index = 0
        self.dict = {'Idle' : 0, 'Jump' : 1, 'Attack' : 2, 'Death' : 3, 'Damage' : 4}
        self.update_time = pygame.time.get_ticks()
        #load all animation types for players
        animation_types = ['Idle', 'Jump', 'Attack', 'Death', 'Damage']
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
        self.image = self.animation_list[self.dict.get(self.action)][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)

    def update(self, obstacle_list, platform_group, hazard_group):
        self.update_animation()
        self.jump_timer -= 1
        if self.jump_timer == 0:
            self.jump = True
            self.jump_timer = random.randint(100, 300)
            self.direction = -self.direction
            self.update_action('Jump')
        self.check_alive()
        self.dx = 0
        self.dy = 0
        self.ai()

        for tile in obstacle_list:
            #check for collision in the x direction
            if tile[1].colliderect(self.rect.x + self.dx + 12, self.rect.y + 15, self.image.get_width() - 12 - 12, self.image.get_height() - 15):
                self.dx = 0
            #check for collision in the y direction
            if tile[1].colliderect(self.rect.x + 12, self.rect.y + self.dy + 10 , self.image.get_width() - 12 - 12, self.image.get_height() - 15):
                #check if below the ground aka jumping
                if self.vel_y < 0:
                    self.vel_y = 0
                    self.dy = tile[1].bottom - self.rect.top
                #check if above the ground aka falling
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    self.dy = tile[1].top - (self.rect.bottom - 15)

        for platform in platform_group:
            if platform.rect.colliderect(self.rect.x + 12, self.rect.y + self.dy + 15, self.image.get_width() -24, self.image.get_height() - 15):
                if self.vel_y >= 0 and self.rect.y < (platform.rect.y - self.image.get_height()//2):
                    self.vel_y = 0
                    self.in_air = False
                    self.dy = platform.rect.top - self.rect.bottom

        self.rect.x += self.dx
        self.rect.y += self.dy



    def move(self, moving_left, moving_right):
        #assign movement variables
        if moving_left and self.in_air:
            self.dx = -self.speed
            self.flip = True
        if moving_right and self.in_air:
            self.dx = self.speed
            self.flip = False

        if self.jump and not self.in_air:
            self.vel_y = -11
            self.jump = False
            self.in_air = True

        #apply gravity
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y = 10
        self.dy += self.vel_y


    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.speed = 0
            self.update_action('Death')

    def ai(self):
        if self.alive:
            if self.direction == 1:
                ai_moving_right = True
            else:
                ai_moving_right = False
            ai_moving_left = not ai_moving_right
            self.move(ai_moving_left, ai_moving_right)


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
            if self.action == 'Damage':
                self.damage = False
            if self.action == 'Death':
                self.frame_index = len(self.animation_list[self.dict.get(self.action)]) - 1
                self.kill()
            else:
                self.frame_index = 0
            self.update_action('Idle')

    def draw(self, screen):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect) 

