import pygame, os

SCREEN_WIDTH = 800

class Projectile(pygame.sprite.Sprite):

    projectile_group = pygame.sprite.Group()

    def __init__(self, x, y, direction, speed, scale):
        pygame.sprite.Sprite.__init__(self)
        self.spell_frame = 0
        self.spell_id = 0
        self.direction = direction
        self.spell_list = []
        spell_number = ['20']
        for spell in spell_number:
            #reset temporary list of images
            temp_list = []
            #count number of files in folder
            num_of_frames = len(os.listdir(f'Assets/Spell_Effects/C/{spell}_Components'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'Assets/Spell_Effects/C/{spell}_Components/{i}.png')
                img = pygame.transform.scale(img, (int(img.get_width() * scale),int(img.get_height() * scale)))
                img = pygame.transform.rotate(img, -90*direction)
                temp_list.append(img)
            self.spell_list.append(temp_list)
        self.image = self.spell_list[self.spell_id][self.spell_frame].convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.speed = speed

    def update(self, entity_list):
        #update spell animation
        self.image = self.spell_list[self.spell_id][self.spell_frame].convert_alpha()
        self.spell_frame += 1
        if self.spell_frame >= len(self.spell_list[self.spell_id]):
            self.spell_frame = 0
        #move spell
        self.rect.x += (self.direction * self.speed)
        #check if spell has gone off screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()

        for entity in entity_list:
            if pygame.sprite.spritecollide(entity, Projectile.projectile_group, False):
                if entity.alive:
                    entity.health -= 10
                    entity.update_action('Damage')
                    entity.damage = True
                    self.kill()

