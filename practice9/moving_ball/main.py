import pygame

# 1. Инициализация
pygame.init()

# Настройки окна
W, H = 800, 600
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Moving Ball Game")

# Цвета
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# Параметры шара
ball_radius = 25
# Начальная позиция — центр экрана
x = W // 2
y = H // 2
speed = 20

clock = pygame.time.Clock()
running = True

while running:
    # 2. Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        # Обработка нажатий клавиш
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                # Проверяем: если шаг вверх не выведет край шара за 0
                if y - speed >= ball_radius:
                    y -= speed
                    
            elif event.key == pygame.K_DOWN:
                # Проверяем: если шаг вниз не выведет край за высоту H
                if y + speed <= H - ball_radius:
                    y += speed
                    
            elif event.key == pygame.K_LEFT:
                if x - speed >= ball_radius:
                    x -= speed
                    
            elif event.key == pygame.K_RIGHT:
                if x + speed <= W - ball_radius:
                    x += speed

    # 3. Отрисовка
    screen.fill(WHITE) # Белый фон
    
    # Рисуем красный круг (где, цвет, (координаты), радиус)
    pygame.draw.circle(screen, RED, (x, y), ball_radius)

    pygame.display.flip()
    
    # Ограничение FPS
    clock.tick(60)

pygame.quit()