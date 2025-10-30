"""
Interactive setup tool for game client calibration.

This script helps you:
1. Find the game window
2. Calibrate board position and cell size
3. Detect ball colors
4. Test reading the game state

Run this before using the game client to validate game rules.
"""

import numpy as np
from PIL import ImageGrab, Image
import time
import sys

try:
    import pyautogui
    import cv2
except ImportError:
    print("Missing dependencies! Install with:")
    print("  pip install -e \".[game-client]\"")
    print("  or: pip install pillow pyautogui opencv-python")
    sys.exit(1)

from wzlz_ai import GameClientEnvironment, GameConfig, BallColor


def find_game_window():
    """Help user find the game window position."""
    print("\n" + "="*70)
    print("STEP 1: Find Game Window")
    print("="*70)
    print("\nInstructions:")
    print("1. Open the game (五子连珠5.2)")
    print("2. Position the game window where you want it")
    print("3. Move your mouse to the TOP-LEFT corner of the game board")
    print("4. Press Enter when ready...")
    
    input()
    
    print("\nMove mouse to TOP-LEFT corner of the board and press Enter...")
    input()
    
    x1, y1 = pyautogui.position()
    print(f"✓ Top-left corner: ({x1}, {y1})")
    
    print("\nNow move mouse to BOTTOM-RIGHT corner of the board and press Enter...")
    input()
    
    x2, y2 = pyautogui.position()
    print(f"✓ Bottom-right corner: ({x2}, {y2})")
    
    width = x2 - x1
    height = y2 - y1
    
    print(f"\n✓ Board rectangle: ({x1}, {y1}, {width}, {height})")
    print(f"✓ Board size: {width}×{height} pixels")
    
    # Calculate cell size
    cell_width = width / 9
    cell_height = height / 9
    
    print(f"✓ Cell size: {cell_width:.1f}×{cell_height:.1f} pixels")
    
    return (x1, y1, width, height), (cell_width, cell_height)


def capture_and_show_board(board_rect):
    """Capture and display the game board."""
    print("\n" + "="*70)
    print("STEP 2: Capture Board Screenshot")
    print("="*70)
    
    x, y, w, h = board_rect
    
    print(f"\nCapturing board at ({x}, {y}, {w}, {h})...")
    screenshot = ImageGrab.grab(bbox=(x, y, x + w, y + h))
    
    # Save screenshot
    screenshot.save("board_screenshot.png")
    print("✓ Saved to: board_screenshot.png")
    
    # Show screenshot
    try:
        screenshot.show()
        print("✓ Screenshot displayed (close the image window to continue)")
    except:
        print("✓ Screenshot saved (couldn't display automatically)")
    
    return np.array(screenshot)


def detect_ball_colors(screenshot, cell_size):
    """Help user identify ball colors."""
    print("\n" + "="*70)
    print("STEP 3: Detect Ball Colors")
    print("="*70)
    
    cell_w, cell_h = cell_size
    
    print("\nWe need to identify the RGB colors of each ball type.")
    print("Look at the screenshot and identify cells with balls.")
    print("\nFor each ball color, we'll sample the center pixel.")
    
    color_samples = {}
    
    print("\nLet's sample some ball colors...")
    print("Enter cell positions (row, col) for each color, or 'done' to finish.")
    print("Example: 0,0 for top-left cell")
    
    while True:
        user_input = input("\nEnter cell position (row,col) or 'done': ").strip()
        
        if user_input.lower() == 'done':
            break
        
        try:
            row, col = map(int, user_input.split(','))
            
            # Calculate center of cell
            center_x = int(col * cell_w + cell_w / 2)
            center_y = int(row * cell_h + cell_h / 2)
            
            # Get color at center
            color = screenshot[center_y, center_x]
            
            print(f"  Cell ({row},{col}) center: RGB{tuple(color)}")
            
            # Ask for color name
            color_name = input("  What color is this ball? (R/G/B/N/M/Y/C or 'empty'): ").strip().upper()
            
            if color_name in ['R', 'G', 'B', 'N', 'M', 'Y', 'C']:
                color_map = {
                    'R': 'RED', 'G': 'GREEN', 'B': 'BLUE', 'N': 'BROWN',
                    'M': 'MAGENTA', 'Y': 'YELLOW', 'C': 'CYAN'
                }
                color_samples[color_map[color_name]] = tuple(color)
                print(f"  ✓ Saved {color_map[color_name]}: RGB{tuple(color)}")
            elif color_name == 'EMPTY':
                color_samples['EMPTY'] = tuple(color)
                print(f"  ✓ Saved EMPTY: RGB{tuple(color)}")
        
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    print(f"\n✓ Collected {len(color_samples)} color samples:")
    for name, rgb in color_samples.items():
        print(f"  {name}: RGB{rgb}")
    
    return color_samples


def generate_config_code(board_rect, cell_size, color_samples):
    """Generate Python code for the configuration."""
    print("\n" + "="*70)
    print("STEP 4: Generate Configuration Code")
    print("="*70)
    
    x, y, w, h = board_rect
    cell_w, cell_h = cell_size
    
    code = f'''
# Game Client Configuration
# Copy this code to your script

from wzlz_ai import GameClientEnvironment, GameConfig

# Board position and size
board_rect = ({x}, {y}, {w}, {h})
cell_size = ({cell_w:.1f}, {cell_h:.1f})

# Ball color RGB values (sample from center of each ball)
color_map = {{
'''
    
    for name, rgb in color_samples.items():
        code += f"    '{name}': {rgb},\n"
    
    code += '''}

# Create game client
config = GameConfig(rows=9, cols=9)
env = GameClientEnvironment(config)
env.board_rect = board_rect
env.cell_size = cell_size

# Use color_map for ball detection
# You'll need to implement color matching in _parse_board()
'''
    
    print(code)
    
    # Save to file
    with open("game_client_config.py", "w") as f:
        f.write(code)
    
    print("\n✓ Configuration saved to: game_client_config.py")
    
    return code


def test_ball_detection(screenshot, cell_size, color_samples):
    """Test ball detection on the screenshot."""
    print("\n" + "="*70)
    print("STEP 5: Test Ball Detection")
    print("="*70)
    
    if not color_samples:
        print("⚠ No color samples collected. Skipping test.")
        return
    
    cell_w, cell_h = cell_size
    
    print("\nDetecting balls on the board...")
    
    detected_board = []
    
    for row in range(9):
        row_str = []
        for col in range(9):
            # Get center of cell
            center_x = int(col * cell_w + cell_w / 2)
            center_y = int(row * cell_h + cell_h / 2)
            
            # Get color at center
            pixel_color = tuple(screenshot[center_y, center_x])
            
            # Find closest matching color
            best_match = 'EMPTY'
            min_distance = float('inf')
            
            for name, sample_color in color_samples.items():
                # Calculate color distance (Euclidean in RGB space)
                distance = sum((a - b) ** 2 for a, b in zip(pixel_color, sample_color)) ** 0.5
                
                if distance < min_distance:
                    min_distance = distance
                    best_match = name
            
            # Use threshold to determine if it's a ball or empty
            if best_match == 'EMPTY' or min_distance > 50:  # Threshold
                row_str.append('.')
            else:
                row_str.append(best_match[0])  # First letter
        
        detected_board.append(' '.join(row_str))
    
    print("\nDetected board:")
    for row in detected_board:
        print(row)
    
    print("\n✓ Detection test complete!")
    print("⚠ Note: This is a simple color matching test.")
    print("   For better accuracy, you'll need to implement proper image recognition.")


def main():
    """Main setup wizard."""
    print("\n" + "="*70)
    print("WZLZ AI - GAME CLIENT SETUP WIZARD")
    print("="*70)
    print("\nThis wizard will help you set up the game client to read from the game.")
    print("\nPrerequisites:")
    print("  ✓ Game (五子连珠5.2) is installed and running")
    print("  ✓ Game window is visible on screen")
    print("  ✓ Dependencies installed: pip install -e \".[game-client]\"")
    
    input("\nPress Enter to start...")
    
    # Step 1: Find game window
    board_rect, cell_size = find_game_window()
    
    # Step 2: Capture screenshot
    screenshot = capture_and_show_board(board_rect)
    
    # Step 3: Detect colors
    color_samples = detect_ball_colors(screenshot, cell_size)
    
    # Step 4: Generate config
    config_code = generate_config_code(board_rect, cell_size, color_samples)
    
    # Step 5: Test detection
    test_ball_detection(screenshot, cell_size, color_samples)
    
    print("\n" + "="*70)
    print("SETUP COMPLETE!")
    print("="*70)
    print("\nNext steps:")
    print("1. Review the generated configuration in 'game_client_config.py'")
    print("2. Implement proper ball detection in 'wzlz_ai/game_client.py'")
    print("3. Test reading game state with the game client")
    print("4. Execute moves and validate game rules")
    
    print("\nRecommended approach for ball detection:")
    print("  • Use color matching with tolerance")
    print("  • Or use template matching (cv2.matchTemplate)")
    print("  • Or use circle detection (cv2.HoughCircles)")
    print("  • Or train a simple CNN classifier")


if __name__ == "__main__":
    main()

