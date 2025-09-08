import pygame
import random
import time

RED = (255,0,   0)
GREEN = (78,165,56)
BLUE = (49,43,240)
YELLOW = (255, 255, 0)

PIKACHU_IMG = pygame.image.load("asset/pikachu.gif")
PIKACHU_IMG = pygame.transform.scale(PIKACHU_IMG, (50,50))

CHARIZARD_MEGA = pygame.image.load("asset/charizard-mega-x.png")
CHARIZARD_MEGA = pygame.transform.scale(CHARIZARD_MEGA, (300,300))

BULBASAUR = pygame.image.load("asset/bulbasaur.png")
BULBASAUR = pygame.transform.scale(BULBASAUR, (150,150))

CHARMANDER = pygame.image.load("asset/charmander.png")
CHARMANDER = pygame.transform.scale(CHARMANDER, (150,150))

class PatrollingBot:
    def __init__(self, x, y, speed, patrol_range):
        self.x = x
        self.y = y
        self.patrol_range = patrol_range
        self.speed = speed
        self.direction = 1  #1:phải, -1: trái
        self.color = GREEN
        self.lastchange = 0
        self.dead_delay = 2
        rand = random.random()
        if rand < 0.3:
            self.name = PIKACHU_IMG
            self.size = 50
        elif 0.3 <= rand < 0.6:
            self.name = CHARIZARD_MEGA
            self.size = 300
            self.direction = -1
            self.y -= 300
        elif 0.6 <= rand < 0.8:
            self.name = BULBASAUR
            self.size = 150
        else:
            self.name = CHARMANDER
            self.size = 150
    

    def is_dead(self):
        return True if self.color == RED else False
    
    def update_position(self):
        self.x += self.speed * self.direction
        if random.random() > 0.99995:
            self.direction = -self.direction
        if self.x < 0:
            self.x = 0
            self.direction = 1
        elif self.x > self.patrol_range - self.size:
            self.x = self.patrol_range - self.size
            self.direction = -1

        #phatno
        now = time.time()
        if now - self.lastchange >= self.dead_delay and not self.lastchange == 0:
            self.color = RED

    def handle_bot_click(self, mouse_pos):
        if not self.color == GREEN:
            return False
        if self.x <= mouse_pos[0] <= self.x + self.size and self.y <= mouse_pos[1] <= self.y + self.size:
            self.color = YELLOW
            self.speed = 0
            self.lastchange = time.time()
            return True 
        else: return False        
        
    def draw(self, display):
        # pygame.draw.rect(display, self.color, (self.x, self.y, self.size, self.size))
        display.blit(self.name, (self.x, self.y))