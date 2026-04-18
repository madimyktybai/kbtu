import pygame
import datetime

pygame.init()
W, H = 829, 836
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Mickey's Clock")
clock = pygame.time.Clock()

bg_raw = pygame.image.load('images/main-clock.png').convert_alpha()
bg = pygame.transform.scale(bg_raw, (W, H))

h_min_raw = pygame.image.load('images/right-hand.png').convert_alpha()
h_sec_raw = pygame.image.load('images/left-hand.png').convert_alpha()

# Здесь мы задаем реальный размер рук в пикселях (Ширина, Высота)
hand_min = pygame.transform.scale(h_min_raw, (120, 350))
hand_sec = pygame.transform.scale(h_sec_raw, (80, 420))

def blit_rotate_center(surf, image, center, angle):
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center=center)
    surf.blit(rotated_image, new_rect)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    now = datetime.datetime.now()
    
    # Углы. Если руки "смотрят" не туда, добавь к углу +90 или -90
    sec_angle = -now.second * 6
    min_angle = -(now.minute * 6 + now.second / 10)

    screen.fill((255, 255, 255))
    screen.blit(bg, (0, 0))

    center_pos = (W // 2, H // 2)

    blit_rotate_center(screen, hand_min, center_pos, min_angle)
    blit_rotate_center(screen, hand_sec, center_pos, sec_angle)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()