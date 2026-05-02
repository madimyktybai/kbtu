import pygame
import json
from game import run_game
from db import get_leaderboard

pygame.init()

screen = pygame.display.set_mode((400,400))
font = pygame.font.SysFont(None, 28)

COLORS = [
    [0,200,0],
    [255,50,50],
    [50,150,255],
    [255,255,0]
]

def draw(t,x,y,c=(255,255,255)):
    screen.blit(font.render(t,True,c),(x,y))


def load_settings():
    try:
        return json.load(open("settings.json"))
    except:
        return {"snake_color":[0,200,0],"grid":True,"sound":False}

def save_settings(d):
    json.dump(d, open("settings.json","w"))

settings = load_settings()

state = "menu"
username = ""
game_data = None
color_index = 0

while True:

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            exit()

        if e.type == pygame.KEYDOWN:

            # ---------------- MENU ----------------
            if state == "menu":
                if e.key == pygame.K_1:
                    state = "input"
                if e.key == pygame.K_2:
                    state = "leaderboard"
                if e.key == pygame.K_3:
                    state = "settings"
                if e.key == pygame.K_4:
                    exit()

            # ---------------- INPUT ----------------
            elif state == "input":
                if e.key == pygame.K_RETURN:
                    game_data = run_game(username)
                    state = game_data[0]
                elif e.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                else:
                    username += e.unicode

            # ---------------- LEADERBOARD ----------------
            elif state == "leaderboard":
                if e.key == pygame.K_q:
                    state = "menu"

            # ---------------- SETTINGS ----------------
            elif state == "settings":

                if e.key == pygame.K_g:
                    settings["grid"] = not settings["grid"]

                # COLOR PICKER (ВОССТАНОВЛЕНО)
                if e.key in [pygame.K_1,pygame.K_2,pygame.K_3,pygame.K_4]:
                    color_index = e.key - pygame.K_1
                    settings["snake_color"] = COLORS[color_index]

                if e.key == pygame.K_RETURN:
                    save_settings(settings)
                    state = "menu"

            # ---------------- GAMEOVER ----------------
            elif state == "gameover":
                if e.key == pygame.K_r:
                    state = "input"
                    username = ""
                if e.key == pygame.K_q:
                    exit()

    # ---------------- DRAW ----------------
    screen.fill((0,0,0))

    if state == "menu":
        draw("1 - PLAY",140,120,(0,255,0))
        draw("2 - LEADERBOARD",110,160,(255,255,0))
        draw("3 - SETTINGS",120,200,(0,150,255))
        draw("4 - QUIT",140,240,(255,80,80))

    elif state == "input":
        draw("ENTER NAME:",120,120)
        draw(username,120,160)

    elif state == "leaderboard":
        draw("LEADERBOARD (Q to exit)",70,40,(255,255,0))

        data = get_leaderboard()
        y = 80
        for i,r in enumerate(data):
            draw(f"{i+1}. {r[0]} {r[1]} lvl:{r[2]}",30,y)
            y += 25

    elif state == "settings":
        draw("SETTINGS",160,40)

        draw("G - grid toggle",100,120)
        draw(f"Grid: {settings['grid']}",100,150)

        draw("1-4 - snake color",100,200)

        # COLOR UI (ВОССТАНОВЛЕНО ПОЛНОСТЬЮ)
        for i,c in enumerate(COLORS):
            pygame.draw.rect(screen,c,(100+i*40,250,30,30))
            if settings["snake_color"] == c:
                pygame.draw.rect(screen,(255,255,255),(100+i*40,250,30,30),2)

        draw("ENTER - SAVE & BACK",80,320)

    elif state == "gameover":
        _,score,level,best = game_data

        draw("GAME OVER",140,80,(255,0,0))
        draw(f"SCORE: {score}",120,140)
        draw(f"LEVEL: {level}",120,180)
        draw(f"BEST: {best}",120,220)

        draw("R - RESTART",120,280,(0,255,0))
        draw("Q - QUIT",120,310,(255,80,80))

    pygame.display.flip()