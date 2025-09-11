import pygame
import random
import time
import json
import os
from src.entities.bot import creatBot

with open("settings.json", "r") as f:
    settings = json.load(f)

game_setting = settings["game"]
screen_width = game_setting["screen_width"]
screen_height = game_setting["screen_height"]
FPS = game_setting["fps"]
bot_setting = settings["bot"]

pygame.init()
pygame.mixer.init() 

display = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()
pygame.display.set_caption("Catch 'em all")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
BLUE = (50, 100, 200)
GRAY = (100, 100, 100)
YELLOW = (255, 223, 0)

font_large = pygame.font.SysFont("Arial", 50, bold=True)
font_medium = pygame.font.SysFont("Arial", 30, bold=True)
font_small = pygame.font.SysFont("Arial", 24)
font_congrats = pygame.font.SysFont("Arial", 36, bold=True)

BACKGROUND_IMG = pygame.image.load("asset/background.png")
BACKGROUND_IMG = pygame.transform.scale(BACKGROUND_IMG,(screen_height*(914/609),screen_height))

try:
    pygame.mixer.music.load("asset/sound/background_sound.wav")
except pygame.error:
    print("Lỗi: Không tìm thấy file 'asset/sound/background_sound.wav'. Game sẽ không có nhạc nền.")

try:
    HIT_SOUND = pygame.mixer.Sound("asset/sound/hit_sound.wav")
    MISS_SOUND = pygame.mixer.Sound("asset/sound/miss_sound.wav")
except pygame.error:
    print("Lỗi: Không tìm thấy file hit_sound.wav hoặc miss_sound.wav. Game sẽ không có hiệu ứng âm thanh.")
    HIT_SOUND = pygame.mixer.Sound(buffer=b'')
    MISS_SOUND = pygame.mixer.Sound(buffer=b'')

GAME_STATE_MENU = "menu"
GAME_STATE_PLAYING = "playing"
GAME_STATE_GAME_OVER = "game_over"

current_state = GAME_STATE_MENU
GAME_DURATION = game_setting["duration"]
caught = 0
miss = 0
current_streak = 0
game_start_time = 0
listbots = []
listballs = []
current_frame = 0
lastspawn = 0
spawn_delay = game_setting["spawn_delay"]

HIGH_SCORE_FILE = "highscore.json"
is_new_high_score = False

def load_high_score():
    if os.path.exists(HIGH_SCORE_FILE):
        try:
            with open(HIGH_SCORE_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {'caught': 0, 'miss': 0, 'accuracy': 0.0}

def save_high_score(score_data):
    with open(HIGH_SCORE_FILE, 'w') as f:
        json.dump(score_data, f, indent=4)

high_score = load_high_score()


def draw_menu():
    display.blit(BACKGROUND_IMG, (0, 0))
    
    title_text = font_large.render("Catch 'em all", True, WHITE)
    title_rect = title_text.get_rect(center=(screen_width / 2, screen_height / 2 - 100))
    display.blit(title_text, title_rect)

    start_button_rect = pygame.Rect(screen_width / 2 - 100, screen_height / 2, 200, 50)
    pygame.draw.rect(display, GREEN, start_button_rect, border_radius=10)
    
    start_text = font_medium.render("START", True, WHITE)
    start_text_rect = start_text.get_rect(center=start_button_rect.center)
    display.blit(start_text, start_text_rect)

    return start_button_rect

def draw_game_ui():
    global current_frame
    accuracy = (caught / (caught + miss) * 100) if (caught + miss) > 0 else 0
    elapsed_time = time.time() - game_start_time
    remaining_time = max(0, GAME_DURATION - elapsed_time)
    panel = pygame.Surface((screen_width, 80))
    panel.set_alpha(150)
    panel.fill(BLACK)
    display.blit(panel, (0, 0))
    stats_text = (
        f"Caught: {caught} | "
        f"Miss: {miss} | "
        f"Accuracy: {accuracy:.1f}% | "
        f"Streak: {current_streak}"
    )
    game_stats = font_small.render(stats_text, True, WHITE)
    image = pygame.image.load(f"asset/Ballxoay/ballxoay_{current_frame % 40}.png")
    current_frame += 1
    image = pygame.transform.scale(image,(50,50))
    display.blit(image,(15,15))
    display.blit(game_stats, (80, 26))
    time_text = font_medium.render(f"Time: {int(remaining_time)}", True, WHITE)
    time_rect = time_text.get_rect(topright=(screen_width - 20, 22))
    display.blit(time_text, time_rect)

def draw_game_over():
    display.blit(BACKGROUND_IMG, (0, 0))
    
    # Lớp phủ mờ
    overlay = pygame.Surface((screen_width, screen_height))
    overlay.set_alpha(180)
    overlay.fill(BLACK)
    display.blit(overlay, (0, 0))

    center_x = screen_width / 2
    center_y = screen_height / 2

    title_text = font_large.render("Time's Up!", True, WHITE)
    title_rect = title_text.get_rect(center=(center_x, center_y - 200))
    display.blit(title_text, title_rect)

    your_score_title = font_medium.render("Your Score", True, WHITE)
    your_score_rect = your_score_title.get_rect(center=(center_x, center_y - 130))
    display.blit(your_score_title, your_score_rect)
    
    current_accuracy = (caught / (caught + miss) * 100) if (caught + miss) > 0 else 0
    current_stats_text = f"Caught: {caught} | Miss: {miss} | Acc: {current_accuracy:.1f}%"
    current_stats_render = font_small.render(current_stats_text, True, WHITE)
    current_stats_rect = current_stats_render.get_rect(center=(center_x, center_y - 90))
    display.blit(current_stats_render, current_stats_rect)

    high_score_title = font_medium.render("High Score", True, WHITE)
    high_score_rect = high_score_title.get_rect(center=(center_x, center_y - 30))
    display.blit(high_score_title, high_score_rect)
    
    high_score_stats_text = f"Caught: {high_score['caught']} | Miss: {high_score['miss']} | Acc: {high_score['accuracy']:.1f}%"
    high_score_stats_render = font_small.render(high_score_stats_text, True, GRAY)
    high_score_stats_rect = high_score_stats_render.get_rect(center=(center_x, center_y + 10))
    display.blit(high_score_stats_render, high_score_stats_rect)
    
    if is_new_high_score:
        congrats_text = font_congrats.render("Chúc Mừng! Kỷ lục mới!", True, YELLOW)
        congrats_rect = congrats_text.get_rect(center=(center_x, center_y + 80))
        display.blit(congrats_text, congrats_rect)

    instructions_text = font_small.render("Press 'R' to Restart or 'ESC' for Menu", True, WHITE)
    instructions_rect = instructions_text.get_rect(center=(center_x, center_y + 150))
    display.blit(instructions_text, instructions_rect)

def reset_game():
    global caught, miss, current_streak, game_start_time, listbots, lastspawn, is_new_high_score
    caught = 0
    miss = 0
    current_streak = 0
    game_start_time = time.time()
    listbots = []
    lastspawn = time.time()
    is_new_high_score = False

running = True
while running:
    now = time.time()
    display.fill(WHITE)

    for event in pygame.event.get():
        # print(pygame.mouse.get_pos())
        if event.type == pygame.QUIT:
            running = False

        if current_state == GAME_STATE_MENU:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Kiểm tra click vào nút start_button
                if start_button.collidepoint(event.pos):
                    reset_game()
                    current_state = GAME_STATE_PLAYING
                    pygame.mixer.music.play(-1)
        
        elif current_state == GAME_STATE_PLAYING:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                is_clicked = False
                for bot in listbots:
                    if bot.handle_bot_click(pygame.mouse.get_pos()):
                        HIT_SOUND.play()
                        caught += 1
                        current_streak += 1
                        is_clicked = True
                        break
                if not is_clicked:
                    MISS_SOUND.play()
                    miss += 1
                    current_streak = 0
        
        elif current_state == GAME_STATE_GAME_OVER:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    reset_game()
                    current_state = GAME_STATE_PLAYING
                    pygame.mixer.music.play(-1)
                elif event.key == pygame.K_ESCAPE:
                    current_state = GAME_STATE_MENU

    if current_state == GAME_STATE_MENU:
        start_button = draw_menu()

    elif current_state == GAME_STATE_PLAYING:
        display.blit(BACKGROUND_IMG, (0, 0))

        if len(listbots) < bot_setting["quantity"] and now - lastspawn > spawn_delay and random.random() > 1 - game_setting["spawn_probability"]:
            listbots.append(creatBot(bot_setting["speed"], screen_height, screen_width))
            lastspawn = now

        def bot_is_dead(bot):
            bot_is_dead, ball = bot.is_dead()
            if ball:
                listballs.append(ball)
            return not bot_is_dead
        
        listbots = list(filter(bot_is_dead, listbots))
        listbots.sort(key=lambda b: b.y and b.name.value, reverse=True)
        listballs = list(filter(lambda x: not  x.is_dead(), listballs))
        
        for bot in listbots[::-1]:
            bot.update_position()
            bot.draw(display)
        
        for ball in listballs[::-1]:
            ball.update_position()
            ball.draw(display)

        ######################################################
        # pygame.draw.rect(display,BLUE, (300, 200, 200,133))    
        # image = pygame.image.load(f"asset/Ballcapture/xuathien.png")
        # image = pygame.transform.scale(image,(500,500))
        # image = pygame.transform.flip(image,False, True)
        # display.blit(image, (300,0))
        # image = pygame.image.load(f"asset/Rayquaza/rayquazamega_frame_0w.png")
        # image = pygame.transform.scale(image,(272,292))
        # display.blit(image, (350,190))

        # image_item = pygame.image.load(f"asset/Ballcapture/ballmo.png")
        # image_item = pygame.transform.scale(image_item,(24,34))
        # display.blit(image_item, (440, 260)) 

        # image_item = pygame.image.load(f"asset/Ballcapture/lightline.png")
        # image_item = pygame.transform.scale(image_item,(120,120))
        # display.blit(image_item, (340, 250))

        # image_item = pygame.image.load(f"asset/Ballcapture/tron1.png")
        # image_item = pygame.transform.scale(image_item,(180,180))
        # image_item = pygame.transform.flip(image_item,True, False)
        # display.blit(image_item, (220, 290))

        # image_item = pygame.image.load(f"asset/Ballcapture/lightball3.png")
        # image_item = pygame.transform.scale(image_item,(160,160))
        # image_item = pygame.transform.flip(image_item,True, False)
        # display.blit(image_item, (345, 245))
        ######################################################
        draw_game_ui()

        if now - game_start_time >= GAME_DURATION:
            pygame.mixer.music.stop()
            
            if caught > high_score['caught']:
                is_new_high_score = True
                high_score['caught'] = caught
                high_score['miss'] = miss
                high_score['accuracy'] = (caught / (caught + miss) * 100) if (caught + miss) > 0 else 0
                save_high_score(high_score)
            
            current_state = GAME_STATE_GAME_OVER
    
    elif current_state == GAME_STATE_GAME_OVER:
        draw_game_over()

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()