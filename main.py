import pygame
from pygame import mixer
import random
import tkinter as tk
from tkinter import ttk
import os
from gameClasses import Key, Player, FallingObject
from PIL import Image, ImageTk  

#Need to:
# - resize objects
# - make them smaller
# - able to be destroyed 
# - fall from middel

# Init pygame and mixer
mixer.init()
pygame.init()

# Globals
info = pygame.display.Info()
SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h

# Set up screen centered in the middle of the monitor
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Music Attack")

KEY_WIDTH = 100
KEY_HEIGHT = 40
KEY_SPACING = 50
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

selected_color = (100, 200, 255)
selected_music = None
selected_music_label = None
MENU_MUSIC = "John Bartmann - Rainbow Boogie Space Funk.mp3"
selected_sprite = None  # Store selected sprite path

# Load sprite
def load_sprite(path):
    try:
        sprite = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(sprite, (KEY_WIDTH, KEY_HEIGHT))
    except Exception as e:
        print(f"Sprite load failed: {e}")
        return None

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
    y = SCREEN_HEIGHT - 150  # Center buttons near the bottom
    for i, (c1, c2, code, label) in enumerate(config):
        x = start_x + i * (KEY_WIDTH + KEY_SPACING)
        keys.append(Key(x, y, code, sprite=sprites.get(code), label=label))
    return keys

def load_music_options():
    if not os.path.exists("music"):
        os.makedirs("music")
    return [f for f in os.listdir("music") if f.endswith((".mp3", ".wav"))]

def run_game():
    # Set up the screen and clock
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

    # Create the player object
    front_sprite = "processed_sprites/chr1_fr1_no_border.gif"
    back_sprite_1 = "processed_sprites/chr1_bk1_no_border.gif"
    back_sprite_2 = "processed_sprites/chr1_bk2_no_border.gif"
    player = Player(selected_color, front_sprite, back_sprite_1, back_sprite_2, SCREEN_WIDTH, SCREEN_HEIGHT)

    clock = pygame.time.Clock()

    # Load the background image for the game
    background_image_path = "path.png"
    background_image = pygame.image.load(background_image_path).convert()
    background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

    # Load music
    if selected_music:
        music_path = os.path.join("music", selected_music)
        try:
            mixer.music.load(music_path)
            mixer.music.set_volume(1.0)
            mixer.music.play()
        except Exception as e:
            print("Music playback failed:", e)

    # Create the falling objects
    falling_objects = []
    object_spawn_timer = 0
    object_spawn_interval = 120
    beat_interval = 500
    last_beat_time = pygame.time.get_ticks()

    score = 0
    running = True

    while running:
        # Draw the background image first
        screen.blit(background_image, (0, 0))

        # Update falling objects and draw them
        font = pygame.font.SysFont("Arial", 36)
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (20, 20))

        object_spawn_timer += 1
        if object_spawn_timer >= object_spawn_interval:
            falling_objects.append(FallingObject(keys[random.randint(0, 3)].key_code, random.choice(["jump", "dodge", "slide", "attack"])))
            object_spawn_timer = 0

        for obj in falling_objects:
            obj.update()
            obj.draw(screen)

        # Remove objects that fall off the screen
        falling_objects = [obj for obj in falling_objects if obj.get_y() < SCREEN_HEIGHT + obj.get_radius()]

        # Check for beat timing and spawn new objects
        current_time = pygame.time.get_ticks()
        if current_time - last_beat_time >= beat_interval:
            falling_objects.append(FallingObject(keys[random.randint(0, 3)].key_code, random.choice(["jump", "dodge", "slide", "attack"])))
            last_beat_time = current_time

        # Check if the player presses the correct key while the object is in range
        pressed = pygame.key.get_pressed()  # Get the keys that are pressed
        for obj in falling_objects[:]:
            obj.update()
            obj.draw(screen)

            if obj.collides_with(player):  # Check if the object is within the player's range
                if pressed[obj.get_key_code()]:  # Check if the correct key is pressed
                    falling_objects.remove(obj)  # Remove the object from the list
                    score += 10  # Increase score when the correct key is pressed

        # Draw the player health bar
        player.draw_health_bar(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                mixer.music.stop()
                running = False
            elif event.type == pygame.KEYDOWN:
                player.handle_keypress(event.key)

        player.update()
        player.draw(screen)

        for key in keys:
            key.draw(screen, pressed[key.key_code])

        pygame.display.update()
        clock.tick(60)

    pygame.quit()

def show_tkinter_menu():
    global selected_color, selected_music, selected_music_label, selected_sprite

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

    # Load and set the background image for the menu screen using Pillow
    background_image_path = "backg.jpg"  # Replace with the correct path to your background image
    background_image = Image.open(background_image_path)  # Open the image using Pillow
    background_image = background_image.resize((SCREEN_WIDTH, SCREEN_HEIGHT), Image.Resampling.LANCZOS)  # Resize to fit the screen

    # Convert the image to a format Tkinter can handle
    background_image_tk = ImageTk.PhotoImage(background_image)

    # Add background image as a Label widget
    background_label = tk.Label(root, image=background_image_tk)
    background_label.place(x=0, y=0, relwidth=1, relheight=1)  # Set the background to fill the window
    background_label.image = background_image_tk  # Keep a reference to avoid garbage collection

    # Menu music loading
    menu_path = MENU_MUSIC if os.path.exists(MENU_MUSIC) else os.path.join("music", MENU_MUSIC)
    try:
        mixer.music.load(menu_path)
        mixer.music.play(-1)
    except Exception as e:
        print("Menu music failed to load:", e)

    tk.Label(root, text="Music Attack", font=("Helvetica", 36), bg="black", fg="white").pack(pady=30)

    # Preview Canvas for character selection
    preview = tk.Canvas(root, width=120, height=120, bg="black", highlightthickness=0)
    preview.pack(pady=30)

    # Define sprite data (sprite paths for each character)
    sprite_data = {
        "Character 1": "processed_sprites/bmg3_fr1_no_border.gif",
        "Character 2": "processed_sprites/ftr1_fr1_no_border.gif",
        "Character 3": "processed_sprites/gsd1_fr1_no_border.gif",
        "Character 4": "processed_sprites/chr1_fr1_no_border.gif"
    }

    # To keep the selected sprite updated and shown in preview
    def update_sprite(character_name):
        global selected_sprite
        selected_sprite = sprite_data[character_name]
        
        # Ensure the preview canvas is cleared before adding the new image
        preview.delete("all")
        
        # Load and display the selected sprite in the preview
        image = tk.PhotoImage(file=selected_sprite)  # Load the selected sprite
        preview.create_image(60, 60, image=image)  # Place the sprite in the preview
        preview.image = image  # Keep reference to prevent garbage collection

    # Create labels for character selection (bullet points with sprite)
    for character_name in sprite_data:
        frame = tk.Frame(root, bg="black")
        frame.pack(pady=5)
        
        # Load sprite and show as a label next to the character's name
        img = tk.PhotoImage(file=sprite_data[character_name])  # Load the character's front sprite
        sprite_label = tk.Label(frame, image=img, bg="black")
        sprite_label.image = img  # Keep reference to avoid garbage collection
        sprite_label.pack(side="left")
        
        # Character name label next to the sprite
        name_label = tk.Label(frame, text=character_name, font=("Helvetica", 12), bg="black", fg="white")
        name_label.pack(side="left")

        # Bind click event to update selected sprite when clicked
        sprite_label.bind("<Button-1>", lambda event, name=character_name: update_sprite(name))

    def start_game():
        global selected_music
        selected_music = song_dropdown.get()  # Get selected music file
        mixer.music.stop()
        root.destroy()  # Close Tkinter menu and start the game
        run_game()

    # Song selection
    tk.Label(root, text="Select Music", font=("Helvetica", 18), bg="black", fg="white").pack(pady=(30, 10))
    song_list = load_music_options()  # List of music files
    song_dropdown = ttk.Combobox(root, values=song_list, state="readonly")
    song_dropdown.set(song_list[0] if song_list else "")  # Default song
    song_dropdown.pack(pady=10)

    # Start Game and Exit buttons
    tk.Button(root, text="Start Game", font=("Helvetica", 20), command=start_game).pack(pady=30)
    tk.Button(root, text="Exit", font=("Helvetica", 16), command=root.quit).pack()

    # Run the Tkinter menu
    root.mainloop()

# Launch the menu
show_tkinter_menu()
