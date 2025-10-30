"""
Test live capture and compare with manual calibration.
Uses the unified capture method.
"""

import cv2
import numpy as np
import json
from pathlib import Path

from unified_capture import capture_game_window


def main():
    print("="*70)
    print("TEST LIVE CAPTURE")
    print("="*70)
    
    window_title = "五子连珠5.2"
    
    # Load manual calibration
    if not Path('game_window_config.json').exists():
        print("\n✗ game_window_config.json not found!")
        print("Please run: uv run python examples/manual_calibrate_all.py")
        return
    
    with open('game_window_config.json', 'r') as f:
        config = json.load(f)
    
    print("\n✓ Loaded manual calibration:")
    print(f"  Board: {config['board_rect']}")
    print(f"  High score: {config['high_score_rect']}")
    print(f"  Current score: {config['current_score_rect']}")
    print(f"  Next balls: {config['next_balls_rect']}")
    
    # Capture live
    print("\n" + "="*70)
    print("CAPTURING LIVE WINDOW")
    print("="*70)

    img = capture_game_window(window_title, bring_to_front=True)

    if img is None:
        return
    
    # Save live capture
    img.save('live_capture.png')
    print(f"\n✓ Saved live capture to: live_capture.png")
    
    # Convert to numpy
    img_np = np.array(img)
    img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
    
    # Draw all regions on the live capture
    vis_img = img_bgr.copy()
    
    # Draw board
    x, y, w, h = config['board_rect']
    cv2.rectangle(vis_img, (x, y), (x+w, y+h), (0, 255, 0), 2)
    cv2.putText(vis_img, "BOARD", (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    # Draw grid
    cell_w = w / 9
    cell_h = h / 9
    for i in range(10):
        x_line = int(x + i * cell_w)
        cv2.line(vis_img, (x_line, y), (x_line, y+h), (255, 255, 0), 1)
        y_line = int(y + i * cell_h)
        cv2.line(vis_img, (x, y_line), (x+w, y_line), (255, 255, 0), 1)
    
    # Draw high score
    x, y, w, h = config['high_score_rect']
    cv2.rectangle(vis_img, (x, y), (x+w, y+h), (255, 0, 0), 2)
    cv2.putText(vis_img, "HIGH", (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)
    
    # Draw current score
    x, y, w, h = config['current_score_rect']
    cv2.rectangle(vis_img, (x, y), (x+w, y+h), (0, 0, 255), 2)
    cv2.putText(vis_img, "CURRENT", (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
    
    # Draw next balls
    x, y, w, h = config['next_balls_rect']
    cv2.rectangle(vis_img, (x, y), (x+w, y+h), (255, 255, 0), 2)
    cv2.putText(vis_img, "NEXT", (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)
    
    # Save visualization
    cv2.imwrite('live_capture_with_regions.png', vis_img)
    print("✓ Saved visualization to: live_capture_with_regions.png")
    
    # Show the image
    cv2.imshow('Live Capture with Manual Calibration', vis_img)
    print("\nPress any key to close...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    print("\n" + "="*70)
    print("COMPLETE!")
    print("="*70)
    print("\nFiles saved:")
    print("  - live_capture.png")
    print("  - live_capture_with_regions.png")
    print("\nCheck if the regions align correctly with the live capture!")
    print("If they do, the manual calibration works with live capture.")
    print("If not, you may need to recalibrate.")


if __name__ == "__main__":
    main()

