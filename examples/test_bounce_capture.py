"""
Test if we can capture different frames of a bouncing ball.

This will click on a ball and then rapidly capture the cell multiple times
to see if we can detect the bouncing animation.
"""

import sys
from pathlib import Path
import time
import cv2

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from wzlz_ai.game_state import GameConfig
from wzlz_ai.game_client import GameClientEnvironment


def main():
    print("="*70)
    print("BOUNCE CAPTURE TEST")
    print("="*70)
    print()
    print("This will capture a bouncing ball multiple times to see if we")
    print("can detect the animation.")
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
    
    # Click on ball to select it
    print("Clicking on ball to select it...")
    x, y = env._cell_to_screen_coords(row, col)
    env._click_at(x, y)
    
    print("Waiting for bounce animation to start...")
    time.sleep(0.3)
    
    # Capture the cell rapidly multiple times
    print("\nCapturing cell rapidly 10 times...")
    images = []
    for i in range(10):
        img = env._get_cell_image(row, col)
        if img is not None:
            images.append(img)
            # Save image
            cv2.imwrite(f"bounce_frame_{i}.png", img)
            print(f"  Frame {i}: saved to bounce_frame_{i}.png")
        time.sleep(0.02)  # 20ms delay
    
    print()
    print(f"Captured {len(images)} frames")
    
    # Compare all frames
    print("\nComparing frames...")
    max_diff = 0
    max_pair = (0, 0)
    
    for i in range(len(images)):
        for j in range(i + 1, len(images)):
            import numpy as np
            diff = np.abs(images[i].astype(float) - images[j].astype(float))
            mean_diff = np.mean(diff)
            
            if mean_diff > max_diff:
                max_diff = mean_diff
                max_pair = (i, j)
            
            if mean_diff > 0:
                print(f"  Frame {i} vs {j}: mean diff = {mean_diff:.2f}")
    
    print()
    if max_diff > 0:
        print(f"✓ Detected changes! Max difference: {max_diff:.2f}")
        print(f"  Between frames {max_pair[0]} and {max_pair[1]}")
        print(f"  Check bounce_frame_{max_pair[0]}.png and bounce_frame_{max_pair[1]}.png")
    else:
        print("⚠ No changes detected!")
        print("  All frames are identical")
        print("  This means either:")
        print("    1. The ball is not bouncing")
        print("    2. The capture is returning cached images")
        print("    3. The bouncing animation is too subtle to detect")
    
    print()
    print("="*70)
    print("TEST COMPLETE")
    print("="*70)


if __name__ == "__main__":
    main()

