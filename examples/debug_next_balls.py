"""Debug script to check next balls detection."""

import sys
from pathlib import Path
import numpy as np
import cv2

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from wzlz_ai.game_client import GameClientEnvironment
from unified_capture import capture_game_window
from wzlz_ai.game_state import GameConfig, BallColor

def main():
    print("="*70)
    print("NEXT BALLS DEBUG")
    print("="*70)
    
    # Create game config with next balls enabled
    config = GameConfig(show_next_balls=True)
    
    # Create game client environment
    env = GameClientEnvironment(config)
    
    if not env.is_calibrated:
        print("\n✗ Game client not calibrated!")
        return
    
    print("✓ Game client calibrated")
    
    # Read state
    state = env.get_state()
    
    print(f"\nCurrent state:")
    print(f"  Score: {state.score}")
    print(f"  Next balls (raw): {state.next_balls}")
    
    if state.next_balls:
        colors = [BallColor(c).name for c in state.next_balls]
        print(f"  Next balls (names): {colors}")
    else:
        print(f"  Next balls: None/Empty")
    
    # Capture and save next balls region for inspection (using unified_capture - returns BGR)
    img = capture_game_window(env.window_title, bring_to_front=False)
    if img is None:
        print("\n✗ Failed to capture window")
        return

    print(f"\n✓ Captured window")
    print(f"  Image type: {type(img)}")
    print(f"  Image shape: {img.shape if hasattr(img, 'shape') else 'N/A'}")

    # Create a copy with marked regions (img is already BGR format)
    img_marked = img.copy()

    # Draw board region (GREEN)
    x, y, w, h = env.window_config['board_rect']
    cv2.rectangle(img_marked, (x, y), (x+w, y+h), (0, 255, 0), 2)
    cv2.putText(img_marked, 'BOARD', (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

    # Draw high score region (RED)
    x, y, w, h = env.window_config['high_score_rect']
    cv2.rectangle(img_marked, (x, y), (x+w, y+h), (0, 0, 255), 2)
    cv2.putText(img_marked, 'HIGH', (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)

    # Draw current score region (BLUE)
    x, y, w, h = env.window_config['current_score_rect']
    cv2.rectangle(img_marked, (x, y), (x+w, y+h), (255, 0, 0), 2)
    cv2.putText(img_marked, 'SCORE', (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)

    # Draw next balls region (YELLOW)
    x, y, w, h = env.window_config['next_balls_rect']
    cv2.rectangle(img_marked, (x, y), (x+w, y+h), (0, 255, 255), 2)
    cv2.putText(img_marked, 'NEXT', (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)

    # Save both versions (already BGR, no conversion needed)
    cv2.imwrite('debug_full_window.png', img)
    cv2.imwrite('debug_full_window_marked.png', img_marked)
    print(f"  Saved full window to: debug_full_window.png")
    print(f"  Saved marked window to: debug_full_window_marked.png")

    # Extract and save high score region (already BGR)
    x, y, w, h = env.window_config['high_score_rect']
    high_score_img = img[y:y+h, x:x+w]
    cv2.imwrite('debug_high_score_region.png', high_score_img)
    print(f"\n✓ Saved high score region to: debug_high_score_region.png")
    print(f"  Region size: {high_score_img.shape}")
    print(f"  Region rect: x={x}, y={y}, w={w}, h={h}")

    # Extract and save current score region (already BGR)
    x, y, w, h = env.window_config['current_score_rect']
    current_score_img = img[y:y+h, x:x+w]
    cv2.imwrite('debug_current_score_region.png', current_score_img)
    print(f"\n✓ Saved current score region to: debug_current_score_region.png")
    print(f"  Region size: {current_score_img.shape}")
    print(f"  Region rect: x={x}, y={y}, w={w}, h={h}")
    print(f"  Detected score: {state.score}")

    # Extract next balls region (already BGR)
    x, y, w, h = env.window_config['next_balls_rect']
    next_balls_img = img[y:y+h, x:x+w]

    # Save for inspection
    cv2.imwrite('debug_next_balls_region.png', next_balls_img)
    print(f"\n✓ Saved next balls region to: debug_next_balls_region.png")
    print(f"  Region size: {next_balls_img.shape}")
    print(f"  Region rect: x={x}, y={y}, w={w}, h={h}")
    
    # Analyze each ball (from BGR image)
    ball_width = w // 3
    print(f"\n  Ball width: {ball_width} pixels")

    for i in range(3):
        x1 = i * ball_width
        x2 = (i + 1) * ball_width
        ball_region = next_balls_img[:, x1:x2]

        # Get average color (BGR)
        avg_color = np.mean(ball_region, axis=(0, 1))

        print(f"\n  Ball {i+1}:")
        print(f"    Region: x={x1} to x={x2}")
        print(f"    Average BGR: {avg_color}")

        # Detect color
        ball_color = env._detect_ball_color(avg_color)
        print(f"    Detected: {ball_color.name}")
    
    print("\n" + "="*70)
    print("Check the saved image to see if the region is correct!")
    print("="*70)

if __name__ == "__main__":
    main()

