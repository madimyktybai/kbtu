import pygame
import math
import datetime
import os

pygame.init()

# ----------- Настройка окна -----------
WIDTH, HEIGHT = 900, 600
TOOLBAR_WIDTH = 200
DRAW_WIDTH = WIDTH - TOOLBAR_WIDTH

screen = pygame.display.set_mode((WIDTH, HEIGHT))
font = pygame.font.SysFont(None, 24)
clock = pygame.time.Clock()

# ----------- цвета -----------
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
DARK = (100, 100, 100)
BLACK = (0, 0, 0)

#палитра цветов
palette = [
    (0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255),
    (255, 255, 0), (255, 0, 255), (0, 255, 255), (128, 0, 128)
]

current_color = BLACK
mode = "brush"
brush_size = 5

#холст 
canvas = pygame.Surface((DRAW_WIDTH, HEIGHT))
canvas.fill(WHITE)

drawing = False
last_pos = None
start_pos = None

# ----------- текст режим -----------
text_mode = False
text_input = ""
text_pos = (0, 0)
text_font = pygame.font.SysFont(None, 32)

# ----------- кнопки -----------
buttons = {
    "brush": pygame.Rect(DRAW_WIDTH + 20, 50, 160, 30),
    "eraser": pygame.Rect(DRAW_WIDTH + 20, 90, 160, 30),
    "line": pygame.Rect(DRAW_WIDTH + 20, 130, 160, 30),
    "rect": pygame.Rect(DRAW_WIDTH + 20, 170, 160, 30),
    "circle": pygame.Rect(DRAW_WIDTH + 20, 210, 160, 30),
    "square": pygame.Rect(DRAW_WIDTH + 20, 250, 160, 30),
    "right_tri": pygame.Rect(DRAW_WIDTH + 20, 290, 160, 30),
    "eq_tri": pygame.Rect(DRAW_WIDTH + 20, 330, 160, 30),
    "rhombus": pygame.Rect(DRAW_WIDTH + 20, 370, 160, 30),
    "fill": pygame.Rect(DRAW_WIDTH + 20, 410, 160, 30),
    "text": pygame.Rect(DRAW_WIDTH + 20, 450, 160, 30)
}

# ----------- UI -----------
def draw_ui():
    #фон панели
    pygame.draw.rect(screen, (220, 220, 220), (DRAW_WIDTH, 0, TOOLBAR_WIDTH, HEIGHT))
    pygame.draw.line(screen, DARK, (DRAW_WIDTH, 490), (WIDTH, 490), 4)

    #кнопки инструментов
    for tool, rect in buttons.items():
        pygame.draw.rect(screen, DARK if mode == tool else GRAY, rect)

        text = font.render(tool.replace("_", " ").capitalize(), True, BLACK)
        screen.blit(text, (rect.x + 5, rect.y + 5))

    #подпись палитры
    start_y = 500
    label = font.render("Select Color:", True, BLACK)
    screen.blit(label, (DRAW_WIDTH + 20, start_y))

    #сами квадратики цветов
    for i, color in enumerate(palette):
        rect = pygame.Rect(
            DRAW_WIDTH + 20 + (i % 4) * 40,
            start_y + 30 + (i // 4) * 40,
            35, 35
        )

        pygame.draw.rect(screen, color, rect)

        # обводка у выбранного цвета
        if current_color == color:
            pygame.draw.rect(screen, BLACK, rect, 2)


# ----------- flood fill -----------
def flood_fill(surface, x, y, new_color):
    width, height = surface.get_size()

    #цвет который был под курсором (его и будем заменять)
    target_color = surface.get_at((x, y))

    #если уже такой цвет — ничего не делаем
    if target_color == new_color:
        return

    #список пикселей которые надо обработать
    pixels = [(x, y)]

    #обычный flood fill
    while pixels:
        cx, cy = pixels.pop()

        #защита от выхода за экран
        if cx < 0 or cy < 0 or cx >= width or cy >= height:
            continue

        #если цвет уже не тот — значит это граница
        if surface.get_at((cx, cy)) != target_color:
            continue

        #красим пиксель
        surface.set_at((cx, cy), new_color)

        #добавляем соседей (влево, вправо, вверх, вниз)
        pixels.append((cx + 1, cy))
        pixels.append((cx - 1, cy))
        pixels.append((cx, cy + 1))
        pixels.append((cx, cy - 1))


# ----------- основной цикл -----------
running = True
while running:
    mx, my = pygame.mouse.get_pos()

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        # -------- клавиши --------
        if event.type == pygame.KEYDOWN:

            #размер кисти
            if event.key == pygame.K_1:
                brush_size = 2
            elif event.key == pygame.K_2:
                brush_size = 5
            elif event.key == pygame.K_3:
                brush_size = 10

            #сохранение картинки Ctrl + S
            if event.key == pygame.K_s and pygame.key.get_pressed()[pygame.K_LCTRL]:
                now = datetime.datetime.now()
                filename = now.strftime("canvas_%Y-%m-%d_%H-%M-%S.png")

                #сохранение пнг
                path = os.path.join(os.path.dirname(__file__), filename)

                pygame.image.save(canvas, path)
                print("Saved:", path)

            # -------- ввод текста --------
            if text_mode:

                if event.key == pygame.K_RETURN:
                    # фиксируем текст на canvas
                    rendered = text_font.render(text_input, True, current_color)
                    canvas.blit(rendered, text_pos)

                    text_mode = False
                    text_input = ""

                elif event.key == pygame.K_ESCAPE:
                    text_mode = False
                    text_input = ""

                elif event.key == pygame.K_BACKSPACE:
                    text_input = text_input[:-1]

                else:
                    #добавляем символ
                    text_input += event.unicode

        # -------- мышка нажата --------
        if event.type == pygame.MOUSEBUTTONDOWN:

            #кнопки
            for tool, rect in buttons.items():
                if rect.collidepoint(event.pos):
                    mode = tool

            #заливка
            if mode == "fill" and mx < DRAW_WIDTH:
                flood_fill(canvas, mx, my, current_color)

            #включение текста
            if mode == "text" and mx < DRAW_WIDTH:
                text_mode = True
                text_input = ""
                text_pos = (mx, my)

            #выбор цвета
            start_y = 500
            for i, color in enumerate(palette):
                rect = pygame.Rect(
                    DRAW_WIDTH + 20 + (i % 4) * 40,
                    start_y + 30 + (i // 4) * 40,
                    35, 35
                )

                if rect.collidepoint(event.pos):
                    current_color = color

            #старт рисования
            if mx < DRAW_WIDTH:
                drawing = True

                if mode in ["brush", "eraser"]:
                    last_pos = (mx, my)

                elif mode == "line":
                    start_pos = (mx, my)

                #фигуры
                if mode == "rect":
                    pygame.draw.rect(canvas, current_color, (mx, my, 80, 50), brush_size)

                elif mode == "square":
                    pygame.draw.rect(canvas, current_color, (mx, my, 50, 50), brush_size)

                elif mode == "circle":
                    pygame.draw.circle(canvas, current_color, (mx, my), 30, brush_size)

                elif mode == "right_tri":
                    pygame.draw.polygon(canvas, current_color,
                        [(mx, my), (mx, my + 50), (mx + 50, my + 50)], brush_size)

                elif mode == "eq_tri":
                    h = int((math.sqrt(3)/2) * 50)
                    pygame.draw.polygon(canvas, current_color,
                        [(mx, my), (mx - 25, my + h), (mx + 25, my + h)], brush_size)

                elif mode == "rhombus":
                    pygame.draw.polygon(canvas, current_color,
                        [(mx, my - 30), (mx + 20, my), (mx, my + 30), (mx - 20, my)], brush_size)

        # -------- отпускание мыши --------
        if event.type == pygame.MOUSEBUTTONUP:

            #линия рисуется только после отпускания
            if mode == "line" and start_pos:
                pygame.draw.line(canvas, current_color, start_pos, (mx, my), brush_size)
                start_pos = None

            drawing = False
            last_pos = None

        # -------- движение мыши --------
        if event.type == pygame.MOUSEMOTION and drawing and mx < DRAW_WIDTH:

            if last_pos:

                #кисть
                if mode == "brush":
                    pygame.draw.line(canvas, current_color, last_pos, (mx, my), brush_size)

                #ластик
                elif mode == "eraser":
                    pygame.draw.line(canvas, WHITE, last_pos, (mx, my), brush_size)

            last_pos = (mx, my)

    # -------- render --------
    screen.fill(GRAY)
    screen.blit(canvas, (0, 0))

    #preview текста
    if text_mode:
        preview = text_font.render(text_input, True, current_color)
        screen.blit(preview, text_pos)

    draw_ui()

    pygame.display.update()
    clock.tick(60)

pygame.quit()