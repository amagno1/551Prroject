import pytest
import pygame
import os
import sys
from unittest.mock import MagicMock, patch

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import from main game file
from main import load_sprite, create_keys, load_music_options, run_game
from gameClasses import Key, Player, FallingObject

# Initialize pygame for testing
pygame.init()
pygame.display.set_mode((800, 600))

# Fixtures
@pytest.fixture
def mock_screen():
    return MagicMock()

@pytest.fixture
def test_key():
    mock_sprite = MagicMock()
    return Key(x=100, y=200, key_code=pygame.K_a, sprite=mock_sprite, label="Test")

@pytest.fixture
def test_player():
    with patch('pygame.image.load') as mock_load:
        # Create mock surfaces for sprites
        mock_surface = MagicMock()
        mock_surface.convert_alpha.return_value = mock_surface
        mock_load.return_value = mock_surface
        
        return Player(
            color=(100, 200, 255),
            front_sprite="test_front.png",
            back_sprite_1="test_back1.png",
            back_sprite_2="test_back2.png",
            screen_width=800,
            screen_height=600
        )

@pytest.fixture
def test_falling_object():
    return FallingObject(
        key_code=pygame.K_s,
        note_type="jump",
        key_x=300
    )

# Test Key class
class TestKey:
    def test_key_initialization(self, test_key):
        assert test_key.rect.x == 100
        assert test_key.rect.y == 200
        assert test_key.key_code == pygame.K_a
        assert test_key.label == "Test"
    
    def test_key_draw(self, test_key, mock_screen):
        test_key.draw(mock_screen, False)
        mock_screen.blit.assert_called_once()

# Test Player class
class TestPlayer:
    def test_player_initialization(self, test_player):
        assert test_player._Player__health == 100
        assert test_player.rect.width > 0
        assert test_player.rect.height > 0
    
    def test_player_movement(self, test_player):
        initial_y = test_player.rect.y
        test_player.update()
        assert test_player.rect.y == initial_y
        
        # Test keypress handling
        test_player.handle_keypress(pygame.K_LEFT)
        # Add assertions based on movement logic
    
    def test_player_draw(self, test_player, mock_screen):
        test_player.draw(mock_screen)
        assert mock_screen.blit.call_count >= 1

# Test GameFunctions
class TestGameFunctions:
    @patch('pygame.image.load')
    @patch('pygame.transform.scale')
    def test_load_sprite(self, mock_scale, mock_load):
        mock_surface = MagicMock()
        mock_load.return_value = mock_surface
        mock_scale.return_value = mock_surface
        
        sprite = load_sprite("test.png")
        assert sprite is not None
        mock_load.assert_called_once_with("test.png")
        mock_scale.assert_called_once_with(mock_surface, (100, 40))
    
    def test_create_keys(self):
        mock_sprites = {
            pygame.K_a: MagicMock(),
            pygame.K_s: MagicMock(),
            pygame.K_d: MagicMock(),
            pygame.K_f: MagicMock()
        }
        keys = create_keys(mock_sprites)
        assert len(keys) == 4
        assert all(isinstance(key, Key) for key in keys)
    
    @patch('os.listdir')
    def test_load_music_options(self, mock_listdir):
        mock_listdir.return_value = ["song1.mp3", "song2.wav", "invalid.txt"]
        options = load_music_options()
        assert len(options) == 2
        assert "song1.mp3" in options
        assert "invalid.txt" not in options

if __name__ == "__main__":
    pytest.main()
