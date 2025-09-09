import pygame
import random
import time
import json

RED = (255,0,   0)
GREEN = (78,165,56)
BLUE = (49,43,240)
YELLOW = (255, 255, 0)

with open("settings.json", "r") as f:
    settings = json.load(f)
bot_setting = settings["bot"]


def creatBot(speed, screen_height, screen_width):
    if random.random() <= 0.5:
        return Pikachu(random.randint(50, screen_width-50),random.randint(screen_height-200,screen_height-100),speed,screen_width)
    else:
        return Charizard(900,random.randint(screen_height-200,screen_height-100),speed,screen_width)

class PatrollingBot:
    def __init__(self, x, y, speed, patrol_range, size, direction = 1):
        self.x = x
        self.y = y
        self.patrol_range = patrol_range
        self.speed = speed
        self.direction = direction  #1:phải, -1: trái
        self.color = GREEN
        self.lastchange = 0
        self.dead_delay = 2
        self.size = size
        self.name = CHARIZARD_MEGA
        self.currframe = 0
        self.idle_probability = bot_setting["idle_probability"]
        self.turn_probability = bot_setting["turn_probability"]
        self.move_probability = bot_setting["move_probability"]
        # rand = random.random()
        # if rand < 0.3:
        #     self.name = PIKACHU_IMG
        #     self.size = 50
        # elif 0.3 <= rand < 0.6:
        #     self.name = CHARIZARD_MEGA
        #     self.size = 300
        #     self.direction = -1
        #     self.y -= 300
        # elif 0.6 <= rand < 0.8:
        #     self.name = BULBASAUR
        #     self.size = 150
        # else:
        #     self.name = CHARMANDER
        #     self.size = 150
    

    def is_dead(self):
        return True if self.color == RED else False
    
    def update_position(self):
        self.x += self.speed * self.direction
        if self.direction:
            if random.random() > 1 - self.idle_probability:
                self.direction = 0
                self.currframe = 0
            if random.random() > 1- self.turn_probability:
                self.direction = -self.direction
        else:
            if not self.color == YELLOW and random.random() > 1 - self.move_probability:
                self.currframe = 0
                self.direction = 1 if random.random() > 0.5 else -1
        if self.x < 0 - self.size:
            self.x = 0
            self.direction = 1
        elif self.x > self.patrol_range + self.size:
            self.x = self.patrol_range + self.size
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
            self.lastchange = time.time()
            self.direction = 0
            return True 
        else: return False        
        
    def draw(self, display):
        # pygame.draw.rect(display, self.color, (self.x, self.y, self.size, self.size))
        display.blit(self.name, (self.x, self.y))

class Pikachu(PatrollingBot): 
    def __init__(self, x, y, speed, patrol_range):
        super().__init__(x, y, speed, patrol_range, 50)
        self.currframe = 0
        # self.list_frame = list_frame_pikachu
    
    def draw(self, display):
        image = pygame.image.load(f"asset/Pikachu/pikachu{self.currframe % 4 + 1}.png")
        if self.direction == 0:
            image = pygame.image.load(f"asset/Pikachu/frame_{self.currframe % 112}.png")
        elif self.direction == -1:
            image = pygame.transform.flip(image,True, False)
        image = pygame.transform.scale(image,(self.size,self.size))
        display.blit(image, (self.x, self.y))
        self.currframe += 1

class Charizard(PatrollingBot): 
    def __init__(self, x, y, speed, patrol_range):
        super().__init__(x, y-300, speed, patrol_range-200, 200)
        self.currframe = 0
    
    def draw(self, display):
        image = pygame.image.load(f"asset/Charizard/charizardframe_{self.currframe % 47}.png")
        if self.direction == 1:
            image = pygame.transform.flip(image,True, False)
        image = pygame.transform.scale(image,(self.size,self.size))
        display.blit(image, (self.x, self.y))
        self.currframe += 1
        

CHARIZARD_MEGA = pygame.image.load("asset/charizard-mega-x.png")
CHARIZARD_MEGA = pygame.transform.scale(CHARIZARD_MEGA, (300,300))

BULBASAUR = pygame.image.load("asset/bulbasaur.png")
BULBASAUR = pygame.transform.scale(BULBASAUR, (150,150))

CHARMANDER = pygame.image.load("asset/charmander.png")
CHARMANDER = pygame.transform.scale(CHARMANDER, (150,150))