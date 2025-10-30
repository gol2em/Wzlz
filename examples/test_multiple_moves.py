"""
Test multiple moves to verify the game client integration works reliably.
"""

import sys
from pathlib import Path
import time
import json
import cv2
import numpy as np
import win32gui
import win32api
import win32con

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from unified_capture import capture_game_window, get_window_rect

# Ball color samples (BGR format for OpenCV)
BALL_COLOR_SAMPLES = {
    'RED': np.array([50, 50, 200]),
    'GREEN': np.array([50, 200, 50]),
    'BLUE': np.array([200, 50, 50]),
    'BROWN': np.array([50, 100, 150]),
    'MAGENTA': np.array([200, 50, 200]),
    'YELLOW': np.array([50, 200, 200]),
    'CYAN': np.array([200, 200, 50]),
    'EMPTY': np.array([180, 180, 180]),
}


def color_distance(color1, color2):
    """Calculate Euclidean distance between two colors."""
    return np.linalg.norm(color1.astype(float) - color2.astype(float))


def detect_ball_color(avg_color, threshold=80.0):
    """Detect ball color from average cell color."""
    best_match = 'EMPTY'
    min_distance = float('inf')
    
    for color_name, sample_color in BALL_COLOR_SAMPLES.items():
        distance = color_distance(avg_color, sample_color)
        if distance < min_distance:
            min_distance = distance
            best_match = color_name
    
    return best_match, min_distance


def read_board_state(board_img):
    """Read the board state from the board image."""
    h, w = board_img.shape[:2]
    cell_w = w / 9
    cell_h = h / 9
    
    board = []
    
    for row in range(9):
        row_data = []
        for col in range(9):
            # Sample center 50% of cell
            x1 = int(col * cell_w + cell_w * 0.25)
            y1 = int(row * cell_h + cell_h * 0.25)
            x2 = int((col + 1) * cell_w - cell_w * 0.25)
            y2 = int((row + 1) * cell_h - cell_h * 0.25)
            
            cell_region = board_img[y1:y2, x1:x2]
            if cell_region.size > 0:
                avg_color = np.mean(cell_region, axis=(0, 1))
                ball_color, distance = detect_ball_color(avg_color)
                row_data.append(ball_color)
            else:
                row_data.append('EMPTY')
        
        board.append(row_data)
    
    return board


def cell_to_screen_coords(row, col, board_rect, window_screen_rect):
    """Convert board cell coordinates to screen coordinates."""
    bx, by, bw, bh = board_rect
    window_left, window_top, window_right, window_bottom = window_screen_rect
    
    cell_w = bw / 9
    cell_h = bh / 9
    
    # Center of the cell
    cell_center_x = bx + (col + 0.5) * cell_w
    cell_center_y = by + (row + 0.5) * cell_h
    
    # Apply correction
    correction_x = cell_w * 0.33
    correction_y = cell_h * 1.5
    
    screen_x = window_left + cell_center_x + correction_x
    screen_y = window_top + cell_center_y + correction_y
    
    return int(screen_x), int(screen_y)


def click_at(x, y):
    """Click at screen coordinates."""
    win32api.SetCursorPos((x, y))
    time.sleep(0.1)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
    time.sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
    time.sleep(0.1)


def capture_state(window_title, config):
    """Capture current game state."""
    img = capture_game_window(window_title, bring_to_front=False)
    if img is None:
        return None
    
    x, y, w, h = config['board_rect']
    img_np = np.array(img)
    board_img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
    board_img_bgr = board_img_bgr[y:y+h, x:x+w]
    
    return read_board_state(board_img_bgr)


def make_move(from_pos, to_pos, config, window_rect):
    """Make a move in the game."""
    from_row, from_col = from_pos
    to_row, to_col = to_pos
    
    from_x, from_y = cell_to_screen_coords(from_row, from_col, config['board_rect'], window_rect)
    to_x, to_y = cell_to_screen_coords(to_row, to_col, config['board_rect'], window_rect)
    
    # Deselect any selected ball
    click_at(from_x, from_y)
    time.sleep(0.2)
    click_at(from_x, from_y)
    time.sleep(0.2)
    
    # Select and move
    click_at(from_x, from_y)
    time.sleep(0.4)
    click_at(to_x, to_y)
    time.sleep(1.8)  # Wait for move + new balls


def main():
    print("="*70)
    print("MULTIPLE MOVES TEST")
    print("="*70)
    
    # Load config
    if not Path('game_window_config.json').exists():
        print("\n✗ game_window_config.json not found!")
        return
    
    with open('game_window_config.json', 'r') as f:
        config = json.load(f)
    
    window_title = config['window_title']
    window_rect = get_window_rect(window_title)
    
    if not window_rect:
        print(f"\n✗ Window '{window_title}' not found!")
        return
    
    print(f"\n✓ Found window")
    
    # Test multiple moves
    num_moves = 5
    print(f"\nTesting {num_moves} moves...")
    
    for i in range(num_moves):
        print(f"\n{'='*70}")
        print(f"MOVE {i+1}/{num_moves}")
        print(f"{'='*70}")
        
        # Capture state
        board = capture_state(window_title, config)
        if board is None:
            print("✗ Failed to capture state")
            break
        
        # Find a ball to move
        balls = []
        for row in range(9):
            for col in range(9):
                if board[row][col] != 'EMPTY':
                    balls.append((row, col, board[row][col]))
        
        if not balls:
            print("✗ No balls found!")
            break
        
        # Find an empty cell
        empty_cells = []
        for row in range(9):
            for col in range(9):
                if board[row][col] == 'EMPTY':
                    empty_cells.append((row, col))
        
        if not empty_cells:
            print("✗ No empty cells!")
            break
        
        # Pick first ball and first empty cell
        from_pos = (balls[0][0], balls[0][1])
        to_pos = empty_cells[0]
        ball_color = balls[0][2]
        
        print(f"Moving {ball_color} from {from_pos} to {to_pos}")
        
        # Make the move
        make_move(from_pos, to_pos, config, window_rect)
        
        # Verify
        board_after = capture_state(window_title, config)
        if board_after:
            print(f"✓ Move {i+1} completed")
        else:
            print(f"✗ Failed to capture state after move")
            break
        
        time.sleep(0.5)
    
    print("\n" + "="*70)
    print("TEST COMPLETE!")
    print("="*70)


if __name__ == "__main__":
    main()

