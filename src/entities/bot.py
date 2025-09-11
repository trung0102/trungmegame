import pygame
import random
import time
import json
from enum import Enum

BLUE = (49,43,240)


with open("settings.json", "r") as f:
    settings = json.load(f)
bot_setting = settings["bot"]
game_setting = settings["game"]
screen_width = game_setting["screen_width"]
screen_height = game_setting["screen_height"]

class PokemonState(Enum):
    APPEARING = 1
    ACTIVE = 2
    DISAPPEARING = 3
    CAPTURED = 4
    INACTIVE = 5
class PokemonName(Enum):
    PIKACHU = 1
    CHARIZARD_MEGA = 2
    CHARIZARD = 3
    PIDGEOT = 4
    CELEBI = 5
    def __str__(self):
        special_map = {
            "CHARIZARD_MEGA": "charizardmegaX_frame_",
            "PIKACHU": "pikachu",
            "CHARIZARD": "charizardframe_",
            "PIDGEOT": "pidgeot_frame_",
            "CELEBI": "celebi_frame_"
        }
        return special_map.get(self.name)
    
    def to_title(self):
        special_map = {
            "CHARIZARD_MEGA": "Charizard",
        }
        return special_map.get(self.name, self.name.capitalize())


def creatBot(speed, screen_height, screen_width):
    if random.random() <= 0.2:
        idx = random.randint(0,1)
        lnum = [(screen_width*(135/800),screen_height*(365/600)),(screen_width*(680/800),screen_height*(350/600))]
        return Pikachu(lnum[idx][0],lnum[idx][1],speed,screen_width)
    elif random.random() <= 0.4:
        return Charizard(900,random.randint(screen_height-200,screen_height-100),speed,screen_width)
    elif random.random() <= 0.6:
        return Celebi(900,random.randint(screen_height-200,screen_height-100),speed,screen_width)
    elif random.random() <= 0.8:
        return Pidgeot(800,random.randint(screen_height-200,screen_height-100),speed,screen_width)
    return CharizardMegaX(900,random.randint(screen_height-200,screen_height-100),speed,screen_width)    

class PatrollingBot:
    def __init__(self, x, y, speed, patrol_range, size, direction = 1, y_fly =0):
        self.x = x
        self.y = y - y_fly
        self.patrol_range = patrol_range
        self.speed = speed
        self.direction = direction  #1:phải, -1: trái
        self.state = PokemonState.APPEARING
        self.lastchange = 0
        self.dead_delay = 2
        self.size = size
        self.posball = None
        self.name = PokemonName.PIKACHU
        self.currframe = 0
        self.y_fly = y_fly
        self.y_spawn = self.y - 300
        self.x_despawn = -10000
        self.idle_probability = bot_setting["idle_probability"]
        self.turn_probability = bot_setting["turn_probability"]
        self.move_probability = bot_setting["move_probability"]
    
    def is_dead(self):
        if self.state == PokemonState.INACTIVE:
            if self.y > self.y_spawn: pos_x, pos_y = self.posball[0]
            ball = Ball(pos_x, pos_y, 10, self.y + self.size[1] + (self.y_fly - self.size[1] + 50), 20, 1) if self.y > self.y_spawn else None
            return (True, ball)
        else: return (False, None)
    
    def Spawn(self):
        pass

    def Despawn(self):
        pass
    
    def update_position(self):
        if self.state == PokemonState.APPEARING: #xuat hien
            return self.Spawn()
        if self.state == PokemonState.DISAPPEARING: #roi di
            return self.Despawn()
        # phatno
        now = time.time()
        if now - self.lastchange >= self.dead_delay and not self.lastchange == 0:
            self.state = PokemonState.INACTIVE
        # cap nhap vi tri
        if self.state == PokemonState.CAPTURED:
            return 
        self.x += self.speed * self.direction
        if self.x < 0:
            self.x = 0
            self.direction = 1
        elif self.x + self.size[0] > self.patrol_range:
            self.x = self.patrol_range - self.size[0]
            self.direction = -1

        # thay doi trang thai
        if self.direction:
            if random.random() > 1 - self.idle_probability:
                self.direction = 0
                self.currframe = 0
            if random.random() > 1- self.turn_probability:
                self.direction = -self.direction
        else:
            if random.random() > 1 - self.move_probability:
                self.currframe = 0
                self.direction = 1 if random.random() > 0.5 else -1
        # ve hang
        if self.x == self.x_despawn and random.random() < bot_setting["disappearing_probability"]:
            self.direction = -1 if self.x_despawn > screen_width/1.99 else 1
            self.state = PokemonState.DISAPPEARING
            return

    def handle_bot_click(self, mouse_pos):
        if self.state in [PokemonState.CAPTURED, PokemonState.INACTIVE]:
            return False
        if self.x <= mouse_pos[0] <= self.x + self.size[0] and self.y <= mouse_pos[1] <= self.y + self.size[1]:
            self.state = PokemonState.CAPTURED
            self.lastchange = time.time()
            self.direction = 0
            self.currframe = 0
            return True 
        else: return False        
        
    def draw(self, display, num = [(55,55),(80,80)]):
        # pygame.draw.rect(display,BLUE, (self.x, self.y, 200,200))
        self.draw_bot(display)
        listdisplay = self.draw_item(num)
        if not listdisplay: return
        if not self.posball: self.posball = self.get_position_ball()
        for i, img in enumerate(listdisplay):
            display.blit(img, self.posball[i])
    
    def draw_bot(self, display):
        if self.currframe < 2: display.blit(self.name, (self.x, self.y))
    
    def draw_item(self, num):
        if not self.state == PokemonState.CAPTURED:
            return
        listdisplay = []
        if self.currframe > 1 and self.currframe < 48:
            image_item = pygame.image.load(f"asset/Ballcapture/ballmo.png")
            image_item = pygame.transform.scale(image_item,(24,34))
            img_lightline = pygame.image.load(f"asset/Ballcapture/lightline2.png")
            img_lightline = pygame.transform.scale(img_lightline,num[0])
            listdisplay += [image_item, img_lightline]
            if self.currframe > 3:
                img_lightball = pygame.image.load(f"asset/Ballcapture/lightball2.png")
                img_lightball = pygame.transform.scale(img_lightball,num[1])
                img_lightball = pygame.transform.flip(img_lightball,True, False) 
                listdisplay.append(img_lightball)
        else:
            image_item = pygame.image.load(f"asset/Ballcapture/balldong.png")
            image_item = pygame.transform.scale(image_item,(20,20))
            listdisplay.append(image_item)
        return listdisplay

    def get_position_ball(self):
        return [(self.x + self.size[0] + 20, self.y - 30), (self.x + self.size[0] - 10, self.y - 24), (self.x - 10, self.y - 12)]

class FlyPokemon(PatrollingBot):
    def __init__(self, x, y, speed, patrol_range, size, direction=1, y_fly=0):
        super().__init__(x, y, speed, patrol_range, size, direction, y_fly)
        self.numframe = 0

    def Spawn(self):
        if self.x + self.size[0] > self.patrol_range or self.x - self.size[0] < 0:
            self.direction = 1 if self.x - self.size[0] < 0 else -1
            self.x += self.speed * self.direction
            self.currframe += 1
        else:
            self.state = PokemonState.ACTIVE

    def Despawn(self):
        pass

    def draw_bot(self, display):
        # pygame.draw.rect(display,BLUE, (self.x,self.y, self.size[0],self.size[1]))
        if self.state in [PokemonState.CAPTURED, PokemonState.INACTIVE]:
            if self.currframe >22: return
            if self.currframe < 2:
                image = pygame.image.load(f"asset/{self.name.to_title()}/{str(self.name)}0.png")
            else:
                image = pygame.image.load(f"asset/{self.name.to_title()}/{str(self.name)}0r.png")
                if self.size[0] > 50:
                    self.size = tuple(x-4 for x in self.size)
                    self.x += 2
                    self.y += 2
            image = pygame.transform.scale(image,(self.size[0],self.size[1]))
        else:
            image = pygame.image.load(f"asset/{self.name.to_title()}/{str(self.name)}{self.currframe % self.numframe}.png")
            if self.direction == 1:
                image = pygame.transform.flip(image,True, False)
            image = pygame.transform.scale(image,(self.size[0],self.size[1]))

        display.blit(image, (self.x, self.y))
        self.currframe += 1

class GroundPokemon(PatrollingBot):
    def __init__(self, x, y, speed, patrol_range, size, direction=1, y_fly=0):
        super().__init__(x, y, speed, patrol_range, size, direction, y_fly)
        self.y_spawn = self.y
        self.ydes = random.randint(screen_height-200,screen_height-100)
        self.direction = 1 if self.x < self.patrol_range/2 else -1

    def Spawn(self):
        if self.y < self.ydes:
            self.x += self.speed * self.direction
            self.y += 0.8
            self.currframe += 1
        else:
            self.x_despawn = self.x
            if random.random() < 1:
                self.direction = 0
                self.currframe = 0
            self.state = PokemonState.ACTIVE

    def Despawn(self):
        if self.y > self.y_spawn:
            self.x += self.speed * self.direction
            self.y -= 0.8
            self.currframe += 1
        else:
            self.state = PokemonState.INACTIVE

class Pikachu(GroundPokemon): 
    def __init__(self, x, y, speed, patrol_range,imageratio = 1):
        self.imageratio = imageratio
        super().__init__(x, y, speed, patrol_range, (50,50/self.imageratio))
        self.name = PokemonName.PIKACHU
    
    def draw_bot(self, display):
        # pygame.draw.rect(display,BLUE, (self.x,self.y, 50,50))
        image = pygame.image.load(f"asset/Pikachu/pikachu{int(self.currframe/2) % 4 + 1}.png")
        if self.direction == 0:
            image = pygame.image.load(f"asset/Pikachu/frame_{self.currframe % 112}.png")
        elif self.direction == -1:
            image = pygame.transform.flip(image,True, False)
        image = pygame.transform.scale(image,(self.size[0],self.size[1]))
        display.blit(image, (self.x, self.y))
        self.currframe += 1

class Charizard(FlyPokemon): 
    def __init__(self, x, y, speed, patrol_range, imageratio = 133/144):
        self.imageratio = imageratio
        super().__init__(x, y, speed, patrol_range, (200,200/self.imageratio), 1, 300)
        self.name = PokemonName.CHARIZARD
        self.position = (self.x, self.y)
        self.numframe = 47
    
    def draw(self, display, num=[(90, 90), (120, 120)]):
        return super().draw(display, num)
    
    def get_position_ball(self):
        return [(self.x + self.size[0] -30, self.y + 60), (self.x + self.size[0] - 100, self.y +55), (self.x +20, self.y +70)]

class Celebi(FlyPokemon): 
    def __init__(self, x, y, speed, patrol_range,imageratio = 67/65):
        self.imageratio = imageratio
        super().__init__(x, y, speed, patrol_range, (50,50/self.imageratio), 1, random.randint(0,300))
        self.name = PokemonName.CELEBI
        self.numframe = 76

class Pidgeot(FlyPokemon): 
    def __init__(self, x, y, speed, patrol_range,imageratio = 110/117):
        self.imageratio = imageratio
        super().__init__(x, y, speed, patrol_range, (80,80/self.imageratio), 1, 300)
        self.name = PokemonName.PIDGEOT
        self.numframe = 53

    def get_position_ball(self):
        return [(self.x + self.size[0], self.y - 25), (self.x + self.size[0] - 30, self.y - 20), (self.x, self.y)]

class CharizardMegaX(Charizard): 
    def __init__(self, x, y, speed, patrol_range):
        super().__init__(x, y, speed, patrol_range, 161/107)
        self.name = PokemonName.CHARIZARD_MEGA
        self.numframe = 64
    
    def get_position_ball(self):
        return [(self.x + self.size[0] -25, self.y -25), (self.x + self.size[0] - 95, self.y -30), (self.x +40, self.y +10)]


class Ball:
    def __init__(self, x, y, acceleration, patrol_range, size, direction = 1):
        self.x = x
        self.y = y
        self.patrol_range = patrol_range
        self.acceleration = acceleration
        self.direction = direction  #-1: lên, 1: xuống
        self.size = size
        self.currframe = 0
        self.maxheight = self.y
        self.lastchange = 0
        self.dead_delay = 2
    
    def is_dead(self):
        return time.time() - self.lastchange > self.dead_delay and not self.lastchange == 0


    def update_position(self):
        self.x += 0.3
        self.y += self.acceleration*self.direction
        if self.direction and self.patrol_range - self.size <= self.maxheight:
            self.direction = 0
            self.lastchange = time.time()
        elif self.y < self.maxheight:
            self.y = self.maxheight
            self.direction = - self.direction
        if self.y + self.size > self.patrol_range:
            self.y = self.patrol_range - self.size
            self.direction = - self.direction
            self.acceleration /=2
            self.maxheight += (self.patrol_range - self.maxheight)/2

    def draw(self, display):
        image = pygame.image.load(f"asset/Ballroi/ballroi_{self.currframe % 32}.png")
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