import pygame

pygame.init()

font = pygame.font.SysFont(None, 40)


def main_menu():
    screen = pygame.display.set_mode((500, 600))

    while True:
        screen.fill((0, 0, 0))

        play = font.render("PLAY", True, (255, 255, 255))
        quit_btn = font.render("QUIT", True, (255, 255, 255))

        screen.blit(play, (150, 200))
        screen.blit(quit_btn, (150, 300))

        pygame.display.update()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return "quit"  # возвращаем сигнал выйти

            if event.type == pygame.MOUSEBUTTONDOWN:

                x, y = pygame.mouse.get_pos()

                # Проверяем, попал ли клик по кнопкам
                # Проверка по X (общая для обеих кнопок)
                if 150 < x < 250:

                    # Если клик в области кнопки PLAY
                    if 200 < y < 250:
                        return "play"

                    # Если клик в области кнопки QUIT
                    if 300 < y < 350:
                        return "quit"