"""
Test live game state detection and make a move.
This script will:
1. Capture the current game state
2. Find a ball to move (e.g., blue ball)
3. Click on the ball
4. Click on an empty cell
5. Capture the game state again to verify the move
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


def print_board(board):
    """Print the board in a readable format."""
    print("\n  ", end="")
    for col in range(9):
        print(f"{col:3d}", end="")
    print()
    
    for row in range(9):
        print(f"{row} ", end="")
        for col in range(9):
            cell = board[row][col]
            if cell == 'EMPTY':
                print("  .", end="")
            else:
                print(f"{cell[0]:3s}", end="")
        print()


def cell_to_screen_coords(row, col, board_rect, window_screen_rect):
    """
    Convert board cell coordinates to screen coordinates.

    Args:
        row, col: Cell position on the 9x9 board
        board_rect: [x, y, w, h] - Board position relative to captured image (includes title bar)
        window_screen_rect: (left, top, right, bottom) - Window position on screen

    Returns:
        (screen_x, screen_y) - Absolute screen coordinates
    """
    bx, by, bw, bh = board_rect  # Board position in captured image
    window_left, window_top, window_right, window_bottom = window_screen_rect

    cell_w = bw / 9
    cell_h = bh / 9

    # Center of the cell relative to the captured image (top-left corner)
    cell_center_x = bx + (col + 0.5) * cell_w
    cell_center_y = by + (row + 0.5) * cell_h

    # Apply correction based on observed offset
    # The mouse is 1.5 cells too high and 1/3 cell too left
    # This suggests the window border/title bar offset
    correction_x = cell_w * 0.33  # Move right by 1/3 cell
    correction_y = cell_h * 1.5   # Move down by 1.5 cells

    # Convert to screen coordinates
    # The captured image starts at window_left, window_top
    screen_x = window_left + cell_center_x + correction_x
    screen_y = window_top + cell_center_y + correction_y

    return int(screen_x), int(screen_y)


def click_at(x, y, description="", wait_before_click=False):
    """Click at screen coordinates."""
    if description:
        print(f"  Clicking {description} at screen ({x}, {y})")

    # Move mouse to position
    win32api.SetCursorPos((x, y))
    time.sleep(0.15)

    if wait_before_click:
        input(f"  Mouse is at ({x}, {y}). Press Enter to click...")

    # Click
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
    time.sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
    time.sleep(0.15)


def main():
    print("="*70)
    print("LIVE GAME STATE DETECTION AND MOVE TEST")
    print("="*70)
    
    # Load configuration
    if not Path('game_window_config.json').exists():
        print("\n✗ game_window_config.json not found!")
        print("Please run: uv run python examples/manual_calibrate_all.py")
        return
    
    with open('game_window_config.json', 'r') as f:
        config = json.load(f)
    
    print("\n✓ Loaded configuration")

    window_title = config['window_title']

    # Get window position
    window_rect = get_window_rect(window_title)
    if not window_rect:
        print(f"\n✗ Window '{window_title}' not found!")
        print("Please make sure the game is running.")
        return

    print(f"\n✓ Found window at: {window_rect}")
    
    # Step 1: Capture initial state
    print("\n" + "="*70)
    print("STEP 1: CAPTURE INITIAL STATE")
    print("="*70)

    # Capture full window
    img = capture_game_window(window_title, bring_to_front=True)
    if img is None:
        print("\n✗ Failed to capture window!")
        return

    # Extract board region
    x, y, w, h = config['board_rect']
    img_np = np.array(img)
    board_img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
    board_img_bgr = board_img_bgr[y:y+h, x:x+w]
    
    board_state = read_board_state(board_img_bgr)
    
    print("\nInitial board state:")
    print_board(board_state)
    
    # Save initial state image
    cv2.imwrite('state_before_move.png', board_img_bgr)
    print("\n✓ Saved: state_before_move.png")
    
    # Step 2: Find any ball to move
    print("\n" + "="*70)
    print("STEP 2: FIND BALL TO MOVE")
    print("="*70)

    # Find all balls on the board
    balls = []
    for row in range(9):
        for col in range(9):
            if board_state[row][col] != 'EMPTY':
                balls.append((row, col, board_state[row][col]))

    if not balls:
        print("\n✗ No balls found on the board!")
        print("Please make sure there are balls on the board.")
        return

    print(f"\n✓ Found {len(balls)} balls on the board:")
    for row, col, color in balls:
        print(f"  ({row}, {col}): {color}")

    # Use the first ball
    ball_pos = (balls[0][0], balls[0][1])
    ball_color = balls[0][2]

    print(f"\n✓ Will move {ball_color} ball at: ({ball_pos[0]}, {ball_pos[1]})")
    
    # Step 3: Find an empty cell to move to
    print("\n" + "="*70)
    print("STEP 3: FIND EMPTY CELL")
    print("="*70)
    
    # Try to find an empty cell nearby
    target_pos = None
    for row in range(9):
        for col in range(9):
            if board_state[row][col] == 'EMPTY':
                target_pos = (row, col)
                break
        if target_pos:
            break
    
    if not target_pos:
        print("\n✗ No empty cell found!")
        return
    
    print(f"\n✓ Found empty cell at: ({target_pos[0]}, {target_pos[1]})")
    
    # Step 4: Make the move
    print("\n" + "="*70)
    print("STEP 4: MAKE THE MOVE")
    print("="*70)

    print(f"\nMoving {ball_color} ball from ({ball_pos[0]}, {ball_pos[1]}) to ({target_pos[0]}, {target_pos[1]})")

    # Calculate screen coordinates
    print(f"\nDebug info:")
    print(f"  Window rect (screen): {window_rect}")
    print(f"  Board rect (relative to window): {config['board_rect']}")
    print(f"  Ball cell: ({ball_pos[0]}, {ball_pos[1]})")
    print(f"  Target cell: ({target_pos[0]}, {target_pos[1]})")

    ball_x, ball_y = cell_to_screen_coords(ball_pos[0], ball_pos[1],
                                            config['board_rect'], window_rect)
    target_x, target_y = cell_to_screen_coords(target_pos[0], target_pos[1],
                                                config['board_rect'], window_rect)

    print(f"  Ball screen coords: ({ball_x}, {ball_y})")
    print(f"  Target screen coords: ({target_x}, {target_y})")

    # Step 4a: Test - move mouse to position and wait for user confirmation
    print("\nStep 4a: TESTING COORDINATES...")
    print("  Moving mouse to ball position. Check if it's correct!")
    click_at(ball_x, ball_y, f"{ball_color} ball at cell ({ball_pos[0]}, {ball_pos[1]})", wait_before_click=True)
    time.sleep(0.3)

    print("\n  Moving mouse to target position. Check if it's correct!")
    click_at(target_x, target_y, f"target cell at ({target_pos[0]}, {target_pos[1]})", wait_before_click=True)
    time.sleep(0.3)

    # Step 4b: Ensure no ball is selected
    print("\nStep 4b: Ensuring no ball is selected...")
    print("  Clicking ball once to select (if not already selected)...")
    click_at(ball_x, ball_y, f"{ball_color} ball (first click)")
    time.sleep(0.3)

    print("  Clicking ball again to deselect...")
    click_at(ball_x, ball_y, f"{ball_color} ball (deselect)")
    time.sleep(0.3)

    # Step 4c: Click on the ball to select it (it will start bouncing)
    print(f"\nStep 4c: Selecting {ball_color} ball...")
    click_at(ball_x, ball_y, f"{ball_color} ball")

    # Wait for ball to start bouncing
    print("  Waiting for ball to start bouncing...")
    time.sleep(0.5)

    # Step 4d: Click on target cell to move
    print(f"\nStep 4d: Moving to target cell...")
    click_at(target_x, target_y, "target cell")

    print("\n✓ Move executed!")

    # Wait for move animation
    print("\nWaiting for move animation to complete...")
    time.sleep(1.0)

    # Wait for new balls to spawn (if any)
    print("Waiting for new balls to spawn...")
    time.sleep(0.8)
    
    # Step 5: Capture state after move
    print("\n" + "="*70)
    print("STEP 5: CAPTURE STATE AFTER MOVE")
    print("="*70)

    # Capture full window again
    img_after = capture_game_window(window_title, bring_to_front=False)
    if img_after is None:
        print("\n✗ Failed to capture window!")
        return

    # Extract board region
    x, y, w, h = config['board_rect']
    img_after_np = np.array(img_after)
    board_img_after_bgr = cv2.cvtColor(img_after_np, cv2.COLOR_RGB2BGR)
    board_img_after_bgr = board_img_after_bgr[y:y+h, x:x+w]
    board_state_after = read_board_state(board_img_after_bgr)
    
    print("\nBoard state after move:")
    print_board(board_state_after)
    
    # Save after state image
    cv2.imwrite('state_after_move.png', board_img_after_bgr)
    print("\n✓ Saved: state_after_move.png")
    
    # Step 6: Verify the move
    print("\n" + "="*70)
    print("STEP 6: VERIFY THE MOVE")
    print("="*70)
    
    # Check if ball moved
    old_cell = board_state_after[ball_pos[0]][ball_pos[1]]
    new_cell = board_state_after[target_pos[0]][target_pos[1]]

    print(f"\nOld position ({ball_pos[0]}, {ball_pos[1]}): {old_cell}")
    print(f"New position ({target_pos[0]}, {target_pos[1]}): {new_cell}")

    if new_cell == ball_color:
        print(f"\n✅ SUCCESS! {ball_color} ball moved to target position!")
    else:
        print("\n⚠ Move may not have completed as expected.")
        print("   This could be due to:")
        print("   - Invalid move (path blocked)")
        print("   - Animation still in progress")
        print("   - New balls spawned after the move")
        print("   - Ball was eliminated in a match")
    
    print("\n" + "="*70)
    print("TEST COMPLETE!")
    print("="*70)
    print("\nCheck the saved images:")
    print("  - state_before_move.png")
    print("  - state_after_move.png")


if __name__ == "__main__":
    main()

