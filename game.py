import pygame
from src.entities.bot import PatrollingBot, creatBot
import random
import time
import json

with open("settings.json", "r") as f:
    settings = json.load(f)

game_setting = settings["game"]
screen_width = game_setting["screen_width"]
screen_height = game_setting["screen_height"]
FPS = game_setting["fps"]
bot_setting = settings["bot"]

pygame.init()

display = pygame.display.set_mode((screen_width,screen_height))
clock = pygame.time.Clock()
#ngang-doc
pygame.display.set_caption("Game")

WHITE = (255,255,255)
RED = (255,0,0)
BLUE = (49,43,240)
BLACK = (0,0,0)
BACKGROUND_IMG = pygame.image.load("asset/background.png")


running = True
listbots = []
lastspawn = 0
spawn_delay = game_setting["spawn_delay"]
font = pygame.font.SysFont("Arial",30)
hit = 0
miss = 0

while running:
    now = time.time()
    display.fill(WHITE)
    display.blit(BACKGROUND_IMG, (0,0))

    if len(listbots) < bot_setting["quantity"] and now - lastspawn > spawn_delay and random.random() > 1 - game_setting["spawn_probability"]:
        listbots.append(creatBot(bot_setting["speed"],screen_height,screen_width))
        lastspawn = now

    listbots = list(filter(lambda x: not x.is_dead(), listbots))
    for bot in listbots[::-1]:
        bot.update_position()
        bot.draw(display)

    #In diem so
    texthits = font.render(str(hit) + "/" + str(miss), True, BLACK)
    pygame.draw.rect(display,BLUE,(10,10,25,25))
    display.blit(texthits, (45,5))


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                is_clicked = False
                for bot in listbots:
                    is_clicked = bot.handle_bot_click(pygame.mouse.get_pos())
                    if is_clicked:
                        hit += 1
                        break
                if not is_clicked:
                    miss += 1


    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()