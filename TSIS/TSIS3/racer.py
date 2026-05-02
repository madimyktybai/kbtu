import pygame
import random
import time
from persistence import save_score

pygame.init()

# ---------- РАЗМЕРЫ ЭКРАНА ----------
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 600

# шрифт для текста на экране
font = pygame.font.SysFont(None, 30)


def run_game():
    clock = pygame.time.Clock()

    # ---------- СЧЁТ ----------
    coins_collected = 0   # собранные монеты
    distance = 0          # пройденная дистанция
    score = 0             # итоговый счёт

    # ---------- СКОРОСТЬ ВРАГОВ ----------
    ENEMY_SPEED_BASE = 3
    ENEMY_SPEED = ENEMY_SPEED_BASE

    # ---------- ПАУЭР-АПЫ ----------
    active_power = None   # активное усиление
    power_timer = 0       # время активации

    # ---------- ЭФФЕКТЫ ----------
    freeze_until = 0      # время заморозки игрока
    spawn_lock_until = 0  # блок спавна после repair

    # создаём окно игры
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    # ---------- ВВОД ИМЕНИ ----------
    def get_player_name(screen):
        name = ""
        while True:
            screen.fill((20, 20, 20))  # фон

            # текст "Enter name"
            screen.blit(font.render("Enter name:", True, (255, 255, 255)), (150, 200))

            # текущее введённое имя
            screen.blit(font.render(name, True, (0, 255, 0)), (150, 250))

            pygame.display.update()

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return "Player"

                if e.type == pygame.KEYDOWN:

                    # Enter → сохранить имя
                    if e.key == pygame.K_RETURN:
                        return name if name else "Player"

                    # Backspace → удалить символ
                    elif e.key == pygame.K_BACKSPACE:
                        name = name[:-1]

                    # любой символ → добавить в строку
                    else:
                        name += e.unicode

    # ---------- ОЖИДАНИЕ СТАРТА ----------
    def wait_for_start(screen):
        while True:
            screen.fill((60, 60, 60))
            screen.blit(font.render("Press any key", True, (255, 255, 255)), (150, 300))
            pygame.display.update()

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return False
                if e.type == pygame.KEYDOWN:
                    return True

    # ---------- ИГРОК ----------
    class Player(pygame.sprite.Sprite):
        def __init__(self):
            super().__init__()

            # изображение игрока
            self.image = pygame.transform.scale(
                pygame.image.load("assets/bluecar.png"), (50, 50)
            )

            # позиция игрока
            self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, 500))

            self.speed = 5
            self.shield = False  # защита

        def update(self):

            # если игрок заморожен — ничего не делаем
            if time.time() < freeze_until:
                return

            keys = pygame.key.get_pressed()

            # ускорение при nitro
            spd = 7 if active_power == "nitro" else self.speed

            # управление
            if keys[pygame.K_a]:
                self.rect.x -= spd
            if keys[pygame.K_d]:
                self.rect.x += spd
            if keys[pygame.K_w]:
                self.rect.y -= spd
            if keys[pygame.K_s]:
                self.rect.y += spd

            # не даём выйти за экран
            self.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

    # ---------- ВРАГ ----------
    class Enemy(pygame.sprite.Sprite):
        def __init__(self, group):
            super().__init__()
            self.group = group

            self.image = pygame.transform.scale(
                pygame.image.load("assets/redcar.png"), (50, 50)
            )

            self.rect = self.image.get_rect()
            self.respawn()

        # появление врага заново
        def respawn(self):
            self.rect.x = random.randint(0, SCREEN_WIDTH - 50)
            self.rect.y = random.randint(-300, -50)

        # движение вниз
        def update(self):
            self.rect.y += ENEMY_SPEED

            # если ушёл вниз — заново появляется
            if self.rect.top > SCREEN_HEIGHT:
                self.respawn()

    class TrafficCar(Enemy):
        pass

    # ---------- МОНЕТА ----------
    class Coin(pygame.sprite.Sprite):
        def __init__(self):
            super().__init__()

            self.weight = random.randint(1, 3)  # ценность монеты

            size = 20 + self.weight * 5

            self.image = pygame.transform.scale(
                pygame.image.load("assets/coin.png"), (size, size)
            )

            self.rect = self.image.get_rect()
            self.rect.x = random.randint(0, SCREEN_WIDTH - size)
            self.rect.y = -size

        def update(self):
            self.rect.y += 3

            # если ушла за экран — удалить
            if self.rect.top > SCREEN_HEIGHT:
                self.kill()

    # ---------- ПРЕПЯТСТВИЕ ----------
    class Obstacle(pygame.sprite.Sprite):
        def __init__(self):
            super().__init__()

            # круг + иконка масла
            base = pygame.Surface((50, 50), pygame.SRCALPHA)
            pygame.draw.circle(base, (255, 0, 0, 80), (25, 25), 25)

            icon = pygame.transform.scale(
                pygame.image.load("assets/oil.png"), (40, 40)
            )

            base.blit(icon, (5, 5))

            self.image = base
            self.rect = self.image.get_rect()

            self.rect.x = random.randint(0, SCREEN_WIDTH - 50)
            self.rect.y = -50

        def update(self):
            self.rect.y += 4

            if self.rect.top > SCREEN_HEIGHT:
                self.kill()

    # ---------- ПАУЭР-АП ----------
    class PowerUp(pygame.sprite.Sprite):
        def __init__(self):
            super().__init__()

            self.type = random.choice(["nitro", "repair", "shield"])

            colors = {
                "nitro": (0, 255, 255, 80),
                "repair": (255, 255, 0, 80),
                "shield": (0, 255, 0, 80)
            }

            base = pygame.Surface((50, 50), pygame.SRCALPHA)
            pygame.draw.circle(base, colors[self.type], (25, 25), 25)

            icon = pygame.transform.scale(
                pygame.image.load(f"assets/{self.type}.png"), (30, 30)
            )

            base.blit(icon, (10, 10))

            self.image = base
            self.rect = self.image.get_rect()

            self.rect.x = random.randint(0, SCREEN_WIDTH - 50)
            self.rect.y = -50

            self.spawn_time = time.time()

        def update(self):
            self.rect.y += 3

            # исчезает через 6 секунд
            if time.time() - self.spawn_time > 6:
                self.kill()

    # ---------- ИНИЦИАЛИЗАЦИЯ ----------
    bg = pygame.transform.scale(
        pygame.image.load("assets/road.png"),
        (SCREEN_WIDTH, SCREEN_HEIGHT)
    )

    traffic = pygame.sprite.Group()
    coins = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()
    powerups = pygame.sprite.Group()

    player = Player()
    enemy = Enemy(traffic)

    all_sprites = pygame.sprite.Group(player, enemy)

    # имя игрока
    username = get_player_name(screen)

    # старт игры
    if not wait_for_start(screen):
        return

    running = True

    # ---------- ГЛАВНЫЙ ЦИКЛ ----------
    while running:
        now = time.time()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False

        # сложность растёт со временем
        ENEMY_SPEED = ENEMY_SPEED_BASE + distance * 0.01

        # можно ли спавнить объекты
        can_spawn = now > spawn_lock_until

        # ---------- СПАВН ----------
        if can_spawn:
            if len(coins) < 5 and random.randint(1, 90) == 1:
                c = Coin()
                coins.add(c)
                all_sprites.add(c)

            if len(obstacles) < 3 and random.randint(1, 250) == 1:
                o = Obstacle()
                obstacles.add(o)
                all_sprites.add(o)

            if len(traffic) < 4 and random.randint(1, 200) == 1:
                t = TrafficCar(traffic)
                traffic.add(t)
                all_sprites.add(t)

            if len(powerups) < 2 and random.randint(1, 300) == 1:
                p = PowerUp()
                powerups.add(p)
                all_sprites.add(p)

        # ---------- ОТРИСОВКА ----------
        screen.blit(bg, (0, 0))

        for s in list(all_sprites):
            s.update()
            screen.blit(s.image, s.rect)

        # ---------- СТОЛКНОВЕНИЯ ----------
        hit_enemy = pygame.sprite.collide_rect(player, enemy)
        hit_traffic = pygame.sprite.spritecollide(player, traffic, False)

        # если нет щита — конец игры
        if hit_enemy or hit_traffic:
            if player.shield:
                player.shield = False
                enemy.respawn()
            else:
                running = False

        # масло → замедление
        if pygame.sprite.spritecollide(player, obstacles, False):
            freeze_until = now + 0.7

        # монеты
        for c in pygame.sprite.spritecollide(player, coins, True):
            coins_collected += c.weight

        # пауэр-апы
        for p in pygame.sprite.spritecollide(player, powerups, True):
            active_power = p.type
            power_timer = now

            # repair → очистка карты
            if p.type == "repair":
                for group in [coins, obstacles, traffic, powerups]:
                    for sprite in group:
                        sprite.kill()

                enemy.respawn()
                freeze_until = 0
                spawn_lock_until = now + 1.5

            if p.type == "shield":
                player.shield = True

        # nitro отключение
        if active_power == "nitro" and now - power_timer > 6:
            active_power = None

        # щит визуально
        if player.shield:
            shield_img = pygame.transform.scale(
                pygame.image.load("assets/sphere.png"), (60, 60)
            )
            screen.blit(shield_img, (player.rect.x - 5, player.rect.y - 5))

        # ---------- СЧЁТ ----------
        distance += 0.03
        score = coins_collected * 10 + int(distance)

        screen.blit(font.render(f"Score: {score}", True, (255, 255, 255)), (10, 10))
        screen.blit(font.render(f"Dist: {int(distance)}", True, (255, 255, 255)), (10, 40))

        pygame.display.update()
        clock.tick(60)

    # сохранение результата
    save_score(username, score, distance)