import pygame
import random
import json
from db import save_game, get_best_score
from config import WIDTH, HEIGHT, CELL

def load_settings():
    try:
        return json.load(open("settings.json"))
    except:
        return {"snake_color":[0,200,0],"grid":True,"sound":False}


def random_pos(exclude):
    while True:
        p = (random.randrange(0, WIDTH, CELL),
             random.randrange(0, HEIGHT, CELL))
        if p not in exclude:
            return p


def run_game(username):

    settings = load_settings()

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)

    snake = [(100,100),(80,100)]
    direction = (CELL,0)
    next_dir = direction

    BUFF_COLORS = {
        "speed": (255, 255, 0),      # ярко-жёлтый
        "slow": (255, 140, 0),      # мутно-оранжевый
        "shield": (0, 200, 255)     # голубой
    }

    COLORS = {
    "snake": (0, 220, 0),
    "food": (255, 50, 50),
    "poison": (120, 0, 0),
    "obstacle": (120, 120, 120),
    "power": (255, 255, 0)
    }

    POWER_COLORS = {
    "speed": (255, 255, 0),     # жёлтый
    "slow": (255, 140, 0),      # оранжевый
    "shield": (0, 200, 255)    # голубой
    }

    buff_text = ""
    buff_end = 0

    score = 0
    level = 1
    last_level = -1

    best = get_best_score(username)

    food = random_pos(snake)
    poison = random_pos(snake+[food])

    obstacles = []

    power = None
    power_type = None

    active_power = None
    power_end = 0

    # --- BUFF SYSTEM ---
    buff_text = ""
    buff_end = 0

    # --- SHIELD ---
    shield_active = False

    # --- SPEED DELAY SYSTEM ---
    pending_speed = False
    speed_trigger_time = 0

    def gen_obstacles():
        obs = []
        head = snake[0]

        def safe(p):
            return abs(p[0]-head[0]) > CELL*3 or abs(p[1]-head[1]) > CELL*3

        for _ in range(5):
            while True:
                p = random_pos(snake+obs+[food,poison])
                if safe(p):
                    obs.append(p)
                    break

        return obs

    running = True

    while running:

        now = pygame.time.get_ticks()

        # ACTIVATE DELAYED SPEED
        if pending_speed and now >= speed_trigger_time:
            active_power = "speed"
            power_end = now + 6000
            buff_text = "SPEED"
            buff_end = power_end
            pending_speed = False

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return ("menu",)

            if e.type == pygame.KEYDOWN:
                nd = None
                if e.key == pygame.K_w: nd = (0,-CELL)
                if e.key == pygame.K_s: nd = (0,CELL)
                if e.key == pygame.K_a: nd = (-CELL,0)
                if e.key == pygame.K_d: nd = (CELL,0)

                if nd and nd != (-direction[0], -direction[1]):
                    next_dir = nd

        direction = next_dir
        head = (snake[0][0]+direction[0], snake[0][1]+direction[1])

        # COLLISION
        if head in snake or head in obstacles:
            if shield_active:
                shield_active = False
            else:
                break

        if head[0]<0 or head[1]<0 or head[0]>=WIDTH or head[1]>=HEIGHT:

            if shield_active:
                shield_active = False  # щит спасает 1 раз
                # телепорт обратно внутрь поля
                head = (
                    max(0, min(head[0], WIDTH - CELL)),
                    max(0, min(head[1], HEIGHT - CELL))
                )
                snake[0] = head
            else:
                break

        snake.insert(0, head)

        # FOOD
        if head == food:
            score += 1
            food = random_pos(snake+obstacles+[poison])

        elif head == poison:
            score = max(0, score - 1)   # ❗ минус очко
            snake = snake[:-2] if len(snake)>2 else []
            poison = random_pos(snake+obstacles+[food])
            if len(snake)<=1:
                break
        else:
            snake.pop()

        # LEVEL
        if score % 5 == 0 and score != last_level:
            level += 1
            last_level = score

            if level >= 3:
                obstacles = gen_obstacles()
            
        
        if power and now - power_spawn_time > 8000:
            power = None
            power_type = None

        # POWER SPAWN
        if not power and not active_power:
            power = random_pos(snake+obstacles+[food,poison])
            power_type = random.choice(["speed","slow","shield"])
            power_spawn_time = now   # ⏳ запоминаем время появления

        #
        if power and head == power:

            if power_type == "speed":
                pending_speed = True
                speed_trigger_time = now + 1000
                buff_text = "SPEED"
                buff_end = now + 6000

            elif power_type == "slow":
                active_power = "slow"
                power_end = now + 6000
                buff_text = "SLOW"
                buff_end = power_end

            elif power_type == "shield":
                shield_active = True
                buff_text = "SHIELD"
                buff_end = now + 6000

            power = None

        # EXPIRE BUFFS
        if active_power and now > power_end:
            active_power = None


        # CLEAR BUFF TEXT WHEN EXPIRED
        if buff_text and now > buff_end:
            buff_text = ""

        # SPEED
        base = 8 + score // 10

        if active_power == "speed":
            speed_now = 10
        elif active_power == "slow":
            speed_now = 5
        else:
            speed_now = base

        # DRAW
        screen.fill((0,0,0))

        if settings["grid"]:
            for x in range(0,WIDTH,CELL):
                pygame.draw.line(screen,(40,40,40),(x,0),(x,HEIGHT))

        for s in snake:
            pygame.draw.rect(screen,settings["snake_color"],(s[0],s[1],CELL,CELL))

        pygame.draw.rect(screen, COLORS["food"], (food[0], food[1], CELL, CELL))
        pygame.draw.rect(screen, COLORS["poison"], (poison[0], poison[1], CELL, CELL))

        for o in obstacles:
            pygame.draw.rect(screen, COLORS["obstacle"], (o[0], o[1], CELL, CELL))

        if power:
            color = POWER_COLORS.get(power_type, (255,255,255))
            pygame.draw.rect(screen, color, (power[0], power[1], CELL, CELL))

        # HUD TOP
        screen.blit(font.render(f"Score: {score}",True,(255,255,255)),(10,10))

        # HUD TOP LEFT
        x, y = 10, 10

        screen.blit(font.render(f"Score: {score}",True,(255,255,255)),(x,y))
        y += 20

        screen.blit(font.render(f"Best: {best}",True,(255,255,0)),(x,y))
        y += 20

        
        y += 20

        shield_text = "YES" if shield_active else "NO"
        screen.blit(font.render(f"Shield: {shield_text}",True,(255,255,255)),(x,y))

        # BUFF WITH TIMER
        if buff_text:
            remaining = max(0, (buff_end - now) // 1000)
            color = BUFF_COLORS.get(buff_text.lower(), (255,255,255))

            screen.blit(
                font.render(f"{buff_text} ({remaining}s)", True, color),
                (10, 50)
            )

        # INCOMING SPEED WARNING
        if pending_speed:
            warn = font.render("INCOMING SPEED", True, (255,0,0))
            screen.blit(warn,(WIDTH//2 - 80, 10))

        pygame.display.flip()
        clock.tick(speed_now)

    save_game(username,score,level)
    return ("gameover",score,level,best)