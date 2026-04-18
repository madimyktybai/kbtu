import pygame
import os

# 1. Инициализация Pygame и Микшера (для звука)
pygame.init()
pygame.mixer.init()

# 2. Настройки окна и шрифта
W, H = 600, 400
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("My Pygame Music Player")
font = pygame.font.SysFont("Arial", 28)
small_font = pygame.font.SysFont("Arial", 20)

# 3. Загрузка плейлиста (автоматически ищет .mp3 и .wav в папке music/)
import os

# Получаем путь к папке, где лежит сам скрипт main.py
current_dir = os.path.dirname(__file__)
music_dir = os.path.join(current_dir, "music")

playlist = []
if os.path.exists(music_dir):
    for file in os.listdir(music_dir):
        if file.endswith(".mp3") or file.endswith(".wav"):
            playlist.append(os.path.join(music_dir, file))

current_track = 0
is_playing = False

def play_current_track():
    """Функция для запуска текущего трека по индексу"""
    if playlist:
        pygame.mixer.music.load(playlist[current_track])
        pygame.mixer.music.play()
        return True
    return False

# 4. Главный цикл
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        # ОБРАБОТКА НАЖАТИЙ КЛАВИШ
        elif event.type == pygame.KEYDOWN:
            
            # Q = Quit (Выход)
            if event.key == pygame.K_q:
                running = False
                
            # P = Play/Pause (Играть/Пауза)
            elif event.key == pygame.K_p:
                if is_playing:
                    pygame.mixer.music.pause()
                    is_playing = False
                else:
                    # Если трек на паузе - снимаем с паузы. Если вообще не запущен - запускаем.
                    if pygame.mixer.music.get_pos() > 0:
                        pygame.mixer.music.unpause()
                    else:
                        play_current_track()
                    is_playing = True
                    
            # S = Stop (Стоп)
            elif event.key == pygame.K_s:
                pygame.mixer.music.stop()
                is_playing = False
                
            # N = Next track (Следующий)
            elif event.key == pygame.K_n:
                if playlist:
                    current_track = (current_track + 1) % len(playlist) # Идем по кругу
                    play_current_track()
                    is_playing = True
                    
            # B = Previous (Назад)
            elif event.key == pygame.K_b:
                if playlist:
                    current_track = (current_track - 1) % len(playlist)
                    play_current_track()
                    is_playing = True

    # 5. Отрисовка интерфейса (UI)
    screen.fill((30, 30, 30)) # Темно-серый фон
    
    if playlist:
        # Показываем название текущего файла
        track_name = os.path.basename(playlist[current_track])
        text_title = font.render(f"Now: {track_name}", True, (0, 255, 100))
        
        # Статус
        status_text = "Playing" if is_playing else "Paused/Stopped"
        text_status = font.render(f"Status: {status_text}", True, (255, 200, 0))
    else:
        text_title = font.render("ERROR: No music found in 'music/' folder!", True, (255, 50, 50))
        text_status = font.render("Status: Empty", True, (150, 150, 150))

    # Вывод текста на экран
    screen.blit(text_title, (20, 30))
    screen.blit(text_status, (20, 70))
    
    # Вывод инструкций управления
    instructions = [
        "Controls:",
        "[P] - Play / Pause",
        "[S] - Stop",
        "[N] - Next Track",
        "[B] - Previous Track",
        "[Q] - Quit"
    ]
    
    y_pos = 150
    for line in instructions:
        inst_surf = small_font.render(line, True, (200, 200, 200))
        screen.blit(inst_surf, (20, y_pos))
        y_pos += 30

    pygame.display.flip()

pygame.quit()