import pygame, os
from Entity import Entity
from Projectile import Projectile
from Player import Player
from Enemy import Enemy
from Map import World
from Button import Button
import csv

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
BG = pygame.image.load('Assets/Background/Main_MenuBG.png').convert_alpha()
pygame.display.set_caption('Glyphmancer')
start_btn = pygame.image.load('Assets/Button/Button01.png').convert_alpha()
exit_btn = pygame.image.load('Assets/Button/ExitButton.png').convert_alpha()
start_btn_pushed = pygame.image.load('Assets/Button/Button02.png').convert_alpha()

#set frame rate
clock = pygame.time.Clock()
FPS = 60

x = 200
y = 300
scale = 2
Level = 1

COLOR = (0, 255, 0)


#define game variables
GRAVITY = 0.75

run = True

start_game = False

world = World()

startButton = Button(SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 - 200, start_btn, start_btn_pushed, 8)
exitButton = Button(SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 - 50, exit_btn, exit_btn, 8)

while(run):
    
    clock.tick(FPS)
    if not start_game:
        screen.blit(BG, (0,0))
        if startButton.draw(screen):
            start_game = True
        if exitButton.draw(screen):
            run = False
    else:
        #update & draw groups
        run , msg = world.update()
        world.draw(screen)
        

    for event in pygame.event.get():
            world.check_input(event)
            if event.type == pygame.QUIT:
                run = False
            #keyboard presses
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False

    pygame.display.update()
print(msg)
