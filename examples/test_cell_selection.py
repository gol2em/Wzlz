"""
Test cell selection detection.

This will test if we can detect when a ball is selected (bouncing).
"""

import sys
from pathlib import Path
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from wzlz_ai.game_state import GameConfig
from wzlz_ai.game_client import GameClientEnvironment


def main():
    print("="*70)
    print("CELL SELECTION DETECTION TEST")
    print("="*70)
    print()
    print("This will test if we can detect when a ball is selected.")
    print()
    
    # Create environment
    config = GameConfig(show_next_balls=True)
    env = GameClientEnvironment(config)
    
    if not env.is_calibrated:
        print("\n✗ Game client not calibrated!")
        print("  Run: uv run python examples/manual_calibrate_all.py")
        return
    
    print("✓ Game client calibrated")
    print()
    
    # Get current state
    state = env.get_state()
    
    # Find a ball to test with
    ball_pos = None
    for row in range(9):
        for col in range(9):
            if state.board[row, col] != 0:
                ball_pos = (row, col)
                break
        if ball_pos:
            break
    
    if not ball_pos:
        print("✗ No balls found on the board!")
        return
    
    row, col = ball_pos
    print(f"Testing with ball at position ({row}, {col})")
    print()
    
    # Test 1: Check if ball is NOT selected initially
    print("="*70)
    print("TEST 1: Ball should NOT be selected initially")
    print("="*70)

    is_changing = env._is_cell_selected(row, col, debug=True)

    if is_changing:
        print(f"⚠ Ball at ({row}, {col}) is CHANGING (selected)")
        print("  This might be okay if a ball was already selected")
    else:
        print(f"✓ Ball at ({row}, {col}) is NOT changing (not selected)")

    print()
    
    # Test 2: Click on ball and check if it's selected
    print("="*70)
    print("TEST 2: Click on ball and check if it's selected")
    print("="*70)
    
    print(f"Clicking on ball at ({row}, {col})...")
    x, y = env._cell_to_screen_coords(row, col)

    # Click manually
    import win32api
    import win32con
    win32api.SetCursorPos((x, y))
    time.sleep(0.1)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
    time.sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)

    # Wait a bit for bounce to start (but not too long)
    time.sleep(0.2)

    print("Checking if ball is now selected...")
    is_changing = env._is_cell_selected(row, col, debug=True)

    if is_changing:
        print(f"✓ Ball at ({row}, {col}) is CHANGING (selected)")
        print("  Detection is working!")
    else:
        print(f"⚠ Ball at ({row}, {col}) is NOT changing")
        print("  Detection might not be working, or ball wasn't selected")

    print()

    # Test 3: Click again to deselect
    print("="*70)
    print("TEST 3: Click again to deselect")
    print("="*70)

    print(f"Clicking on ball at ({row}, {col}) again to deselect...")
    env._click_at(x, y)

    print("Waiting for deselection...")
    time.sleep(0.3)

    print("Checking if ball is now deselected...")
    is_changing = env._is_cell_selected(row, col, debug=True)

    if is_changing:
        print(f"⚠ Ball at ({row}, {col}) is still CHANGING")
        print("  Ball might still be selected")
    else:
        print(f"✓ Ball at ({row}, {col}) is NOT changing (deselected)")
        print("  Detection is working!")
    
    print()
    print("="*70)
    print("TEST COMPLETE")
    print("="*70)
    print()
    print("Summary:")
    print("  - If detection works, you should see:")
    print("    1. Ball NOT changing initially")
    print("    2. Ball CHANGING after click (selected)")
    print("    3. Ball NOT changing after second click (deselected)")


if __name__ == "__main__":
    main()

