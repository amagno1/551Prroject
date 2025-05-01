import pygame
import random

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 750
KEY_WIDTH = 100
KEY_HEIGHT = 40
WHITE = (255, 255, 255)

class Key:
    def __init__(self, x, y,  key_code, sprite, label=""):
        self.__x = x
        self.__y = y
        self.__key_code = key_code
        self.__rect = pygame.Rect(self.__x, self.__y, KEY_WIDTH, KEY_HEIGHT)
        self.__sprite = sprite
        self.__label = label
        self.__font = pygame.font.SysFont(None, 28)

    def draw(self, surface, is_pressed):
        if self.__sprite:
            surface.blit(self.__sprite, (self.__x, self.__y))
            if is_pressed:
                overlay = pygame.Surface((KEY_WIDTH, KEY_HEIGHT), pygame.SRCALPHA)
                overlay.fill((255, 255, 255, 100))
                surface.blit(overlay, (self.__x, self.__y))
        # else:
        #     color = self.__color1 if is_pressed else self.__color2
        #     pygame.draw.rect(surface, color, self.__rect)
        # pygame.draw.rect(surface, WHITE, self.__rect, 2)
        if self.__label:
            text = self.__font.render(self.__label, True, WHITE)
            text_rect = text.get_rect(center=(self.__x + KEY_WIDTH // 2, self.__y + KEY_HEIGHT + 20))
            surface.blit(text, text_rect)

    def get_X(self):
        return self.__x

    @property
    def key_code(self):
        return self.__key_code


class Player:
    def __init__(self, color, SCREEN_WIDTH, SCREEN_HEIGHT):
        self.__x = SCREEN_WIDTH // 2
        self.__y = SCREEN_HEIGHT // 2 + 50
        self.__width = 50
        self.__height = 50
        self.__default_color = color
        self.__attack_color = (255, 50, 50)
        self.__color = self.__default_color
        self.__original_pos = (self.__x, self.__y)
        self.__move_offset = {
            pygame.K_a: (0, -80),
            pygame.K_d: (0, 60),
            pygame.K_f: (0, 0),
        }
        self.__active_move = None
        self.__move_timer = 0
        self.__move_duration = 15
        self.__rect = pygame.Rect(self.__x, self.__y, self.__width, self.__height)
        self.__velocity = 10
        self.__is_jumping = False
        self.__jump_speed = 15
        self.__jump_count = 0
        self.__jump_height = 60

    def handle_keypress(self, key):
        if self.__active_move:
            return
        dx, dy = 0, 0
        if key == pygame.K_s:
            dx = random.choice([-200, 200])
        elif key in self.__move_offset:
            dx, dy = self.__move_offset[key]
        self.__x += dx
        self.__y += dy
        if key == pygame.K_f:
            self.__color = self.__attack_color
        self.__active_move = key
        self.__move_timer = self.__move_duration

    def update(self):
        self.__rect.topleft = (self.__x, self.__y)
        if self.__move_timer > 0:
            self.__move_timer -= 1
            if self.__move_timer == 0:
                self.__x, self.__y = self.__original_pos
                self.__color = self.__default_color
                self.__active_move = None

    def draw(self, surface):
        pygame.draw.rect(surface, self.__color, (self.__x, self.__y, self.__width, self.__height))

    def get_rect(self):
        return self.__rect

class FallingObject:
    def __init__(self, xMin, xMax):
        self.__radius = 20
        self.__color = (255, 100, 100)
        self.__x = random.randint(xMin, xMax - self.__radius)
        self.__y = -self.__radius
        self.__speed = random.randint(3, 6)
        self.__rect = pygame.Rect(self.__x, self.__y, self.__radius * 2, self.__radius * 2)

    def update(self):
        self.__y += self.__speed
        self.__rect.topleft = (self.__x, self.__y)

    def draw(self, surface):
        pygame.draw.circle(surface, self.__color, (self.__x, self.__y), self.__radius)

    def collides_with(self, player):
        px, py = player.rect.center
        distance = ((self.__x - px) ** 2 + (self.__y - py) ** 2) ** 0.5
        return distance < self.__radius + player.rect.width // 2  # approximate

    def get_y(self):
        return self.__y

    def get_radius(self):
        return self.__radius

    def get_rect(self):
        return self.__rect