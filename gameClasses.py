import pygame
import random

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 750
KEY_WIDTH = 100
KEY_HEIGHT = 40
WHITE = (255, 255, 255)

class Key:
    def __init__(self, x, y, key_code, sprite, label=""):
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
    def __init__(self, color, front_sprite, back_sprite_1, back_sprite_2, screen_width, screen_height):
        self.__x = screen_width // 2
        self.__y = screen_height // 2 + 50
        self.__width = 50
        self.__height = 50
        self.__default_color = color
        self.__attack_color = (255, 50, 50)
        self.__color = self.__default_color
        self.__original_pos = (self.__x, self.__y)

        # Health initialization
        self.__health = 100  # Full health
        self.__max_health = 100
        self.__health_bar_width = 200  # Width of health bar
        self.__health_bar_height = 20  # Height of health bar

        # Load sprite images
        self.__front_sprite = pygame.image.load(front_sprite).convert_alpha()
        self.__back_sprite_1 = pygame.image.load(back_sprite_1).convert_alpha()
        self.__back_sprite_2 = pygame.image.load(back_sprite_2).convert_alpha()

        # Scale the sprites
        self.__front_sprite = pygame.transform.scale(self.__front_sprite, (self.__width, self.__height))
        self.__back_sprite_1 = pygame.transform.scale(self.__back_sprite_1, (self.__width, self.__height))
        self.__back_sprite_2 = pygame.transform.scale(self.__back_sprite_2, (self.__width, self.__height))

        # Initialize the sprite (default front sprite)
        self.__sprite = self.__front_sprite

        # Movement tracking
        self.__move_offset = {
            pygame.K_a: (0, -80),  # Jump
            pygame.K_d: (0, 60),   # Slide
            pygame.K_f: (0, 0),    # Attack
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

    # Getter for health
    def get_health(self):
        return self.__health

    # Setter for health
    def set_health(self, health):
        self.__health = health

    @property
    def rect(self):
        """Access the rect of the player"""
        return self.__rect

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
        surface.blit(self.__sprite, (self.__x, self.__y))
        self.draw_health_bar(surface)

    def set_back_sprite(self, back_sprite):
        """Switch the back sprite"""
        if back_sprite == 1:
            self.__sprite = self.__back_sprite_1
        else:
            self.__sprite = self.__back_sprite_2

    def get_rect(self):
        return self.__rect

    def draw_health_bar(self, surface):
        """Draw the health bar at the top-right corner of the screen"""
        # Position health bar in the top-right corner
        health_bar_x = SCREEN_WIDTH - self.__health_bar_width - 20  # 20 pixels from the right edge
        health_bar_y = 20  # 20 pixels from the top edge
        
        # Draw the background of the health bar (red)
        pygame.draw.rect(surface, (255, 0, 0), (health_bar_x, health_bar_y, self.__health_bar_width, self.__health_bar_height))
        
        # Draw the current health (green)
        health_width = (self.__health / self.__max_health) * self.__health_bar_width
        pygame.draw.rect(surface, (0, 255, 0), (health_bar_x, health_bar_y, health_width, self.__health_bar_height))

class FallingObject:
    def __init__(self, key_code, note_type, key_x):
        self.key_code = key_code
        self.note_type = note_type
        self.x = key_x
        self.y = -50  # Start above the screen
        self.speed = 5  # Adjust this value to change falling speed
        
        # Load appropriate image based on note type
        self.image = self._load_note_image()
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.x, self.y)
    
    def _load_note_image(self):
        """Load different images for different note types"""
        image_paths = {
            "jump": "spikes.png",
            "dodge": "wall.png",
            "slide": "bird_cropped.png",
            "attack": "enemy_cropped.png"
        }
        try:
            image = pygame.image.load(image_paths[self.note_type]).convert_alpha()
            return pygame.transform.scale(image, (50, 50))  # Resize if needed
        except:
            # Fallback if image loading fails
            surf = pygame.Surface((50, 50), pygame.SRCALPHA)
            color = {
                "jump": (255, 0, 0),    # Red
                "dodge": (0, 255, 0),    # Green
                "slide": (0, 0, 255),    # Blue
                "attack": (255, 255, 0)   # Yellow
            }.get(self.note_type, (255, 255, 255))
            pygame.draw.circle(surf, color, (25, 25), 25)
            return surf
    
    def update(self):
        """Update the object's position each frame"""
        self.y += self.speed
        self.rect.y = self.y
    
    def draw(self, screen):
        """Draw the object on the screen"""
        screen.blit(self.image, self.rect)
    
    def get_key_code(self):
        return self.key_code
