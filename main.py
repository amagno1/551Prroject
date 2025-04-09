import pygame
from pygame import mixer
import random
import tkinter as tk
from tkinter import ttk
import os

# Init pygame and mixer
mixer.init()
pygame.init()

# Globals
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 750
KEY_WIDTH = 100
KEY_HEIGHT = 40
KEY_SPACING = 50
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

selected_color = (100, 200, 255)
selected_music = None
selected_music_label = None  # tkinter Label to show current song
MENU_MUSIC = "John Bartmann - Rainbow Boogie Space Funk.mp3"  # Path to menu music 

# Load button sprites 
def load_sprite(path):
    try:
        sprite = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(sprite, (KEY_WIDTH, KEY_HEIGHT))
    except Exception as e:
        print(f"Sprite load failed: {e}")
        return None

# Key button class
class Key:
    def __init__(self, x, y, color1, color2, key_code, sprite=None, label=""):
        self.x = x
        self.y = y
        self.color1 = color1
        self.color2 = color2
        self.key_code = key_code
        self.rect = pygame.Rect(self.x, self.y, KEY_WIDTH, KEY_HEIGHT)
        self.sprite = sprite
        self.label = label
        self.font = pygame.font.SysFont(None, 28)

    def draw(self, surface, is_pressed):
        if self.sprite:
            surface.blit(self.sprite, (self.x, self.y))
            if is_pressed:
                overlay = pygame.Surface((KEY_WIDTH, KEY_HEIGHT), pygame.SRCALPHA)
                overlay.fill((255, 255, 255, 100))
                surface.blit(overlay, (self.x, self.y))
        else:
            color = self.color1 if is_pressed else self.color2
            pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, WHITE, self.rect, 2)
        if self.label:
            text = self.font.render(self.label, True, WHITE)
            text_rect = text.get_rect(center=(self.x + KEY_WIDTH // 2, self.y + KEY_HEIGHT + 20))
            surface.blit(text, text_rect)

# Player class
class Player:
    def __init__(self, color):
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2 + 50
        self.width = 50
        self.height = 50
        self.default_color = color
        self.attack_color = (255, 50, 50)
        self.color = self.default_color
        self.original_pos = (self.x, self.y)
        self.move_offset = {
            pygame.K_a: (0, -80),
            pygame.K_d: (0, 60),
            pygame.K_f: (0, 0),
        }
        self.active_move = None
        self.move_timer = 0
        self.move_duration = 15

    def handle_keypress(self, key):
        if self.active_move:
            return
        dx, dy = 0, 0
        if key == pygame.K_s:
            dx = random.choice([-120, 120])
        elif key in self.move_offset:
            dx, dy = self.move_offset[key]
        self.x += dx
        self.y += dy
        if key == pygame.K_f:
            self.color = self.attack_color
        self.active_move = key
        self.move_timer = self.move_duration

    def update(self):
        if self.move_timer > 0:
            self.move_timer -= 1
            if self.move_timer == 0:
                self.x, self.y = self.original_pos
                self.color = self.default_color
                self.active_move = None

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))

def create_keys(sprites):
    keys = []
    config = [
        ((255, 0, 0), (200, 0, 0), pygame.K_a, "Jump"),
        ((0, 255, 0), (0, 200, 0), pygame.K_s, "Dodge"),
        ((0, 0, 255), (0, 0, 200), pygame.K_d, "Slide"),
        ((255, 255, 0), (200, 200, 0), pygame.K_f, "Attack"),
    ]
    total_width = 4 * KEY_WIDTH + 3 * KEY_SPACING
    start_x = (SCREEN_WIDTH - total_width) // 2
    y = 650
    for i, (c1, c2, code, label) in enumerate(config):
        x = start_x + i * (KEY_WIDTH + KEY_SPACING)
        keys.append(Key(x, y, c1, c2, code, sprite=sprites.get(code), label=label))
    return keys

def load_music_options():
    if not os.path.exists("music"):
        os.makedirs("music")
    return [f for f in os.listdir("music") if f.endswith((".mp3", ".wav"))]

def run_game():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Music Attack")

    sprite_paths = {
        pygame.K_a: "button_0.png",
        pygame.K_s: "button_1.png",
        pygame.K_d: "button_2.png",
        pygame.K_f: "button_3.png",
    }
    sprites = {k: load_sprite(path) for k, path in sprite_paths.items()}

    keys = create_keys(sprites)
    player = Player(selected_color)
    clock = pygame.time.Clock()

    if selected_music:
        mixer.music.load(os.path.join("music", selected_music))
        mixer.music.play()

    running = True
    while running:
        screen.fill(BLACK)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                mixer.music.stop()
                running = False
            elif event.type == pygame.KEYDOWN:
                player.handle_keypress(event.key)

        player.update()
        player.draw(screen)

        pressed = pygame.key.get_pressed()
        for key in keys:
            key.draw(screen, pressed[key.key_code])

        pygame.display.update()
        clock.tick(60)

    pygame.quit()

def show_tkinter_menu():
    global selected_color, selected_music, selected_music_label

    root = tk.Tk()
    root.title("Music Attack Launcher")

    window_width = SCREEN_WIDTH
    window_height = SCREEN_HEIGHT
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    root.configure(bg="black")

    # Start menu music
    menu_path = MENU_MUSIC if os.path.exists(MENU_MUSIC) else os.path.join("music", MENU_MUSIC)
    try:
        mixer.music.load(menu_path)
        mixer.music.play(-1)
    except Exception as e:
        print("❌ Menu music failed to load:", e)

    tk.Label(root, text="Music Attack", font=("Helvetica", 36), bg="black", fg="white").pack(pady=30)

    preview = tk.Canvas(root, width=60, height=60, bg="black", highlightthickness=0)
    preview.pack()
    preview_id = preview.create_rectangle(5, 5, 55, 55, fill="#64c8ff", outline="white")

    color_options = {
        "Blue": (100, 200, 255),
        "Red": (255, 100, 100),
        "Green": (100, 255, 100),
        "Yellow": (255, 255, 100)
    }
    selected = tk.StringVar(value="Blue")

    def update_color():
        global selected_color
        selected_color = color_options[selected.get()]
        hex_color = "#%02x%02x%02x" % selected_color
        preview.itemconfig(preview_id, fill=hex_color)

    tk.Label(root, text="Character Color", font=("Helvetica", 18), bg="black", fg="white").pack(pady=(20, 10))
    for name in color_options:
        tk.Radiobutton(root, text=name, variable=selected, value=name,
                       font=("Helvetica", 14), bg="black", fg="white",
                       selectcolor="gray20", command=update_color).pack(anchor="center")

    def open_music_popup():
        global selected_music, selected_music_label
        popup = tk.Toplevel(root)
        popup.title("Select Music")
        popup.geometry("300x300")
        popup.configure(bg="black")

        tk.Label(popup, text="Choose a song:", font=("Helvetica", 16), bg="black", fg="white").pack(pady=10)
        music_files = load_music_options()
        music_choice = tk.StringVar(value=selected_music if selected_music else "")

        for song in music_files:
            tk.Radiobutton(popup, text=song, variable=music_choice, value=song,
                           font=("Helvetica", 12), bg="black", fg="white",
                           selectcolor="gray20").pack(anchor="w", padx=20)

        def apply_choice():
            global selected_music
            selected_music = music_choice.get()
            if selected_music_label:
                selected_music_label.config(text=f"Selected: {selected_music}")
            popup.destroy()

        tk.Button(popup, text="Apply", font=("Helvetica", 12), command=apply_choice).pack(pady=20)

    tk.Label(root, text="Select Music", font=("Helvetica", 18), bg="black", fg="white").pack(pady=(30, 10))
    tk.Button(root, text="Choose Music", font=("Helvetica", 14), command=open_music_popup).pack(pady=5)
    selected_music_label = tk.Label(root, text="Selected: None", font=("Helvetica", 12), bg="black", fg="white")
    selected_music_label.pack()

    tk.Button(root, text="Start Game", font=("Helvetica", 20),
              command=lambda: [mixer.music.stop(), root.destroy(), run_game()]).pack(pady=30)
    tk.Button(root, text="Quit", font=("Helvetica", 16), command=root.quit).pack()

    root.mainloop()

# Launch the menu
show_tkinter_menu()