"""
Manual calibration tool for game window.
This is a simpler version that lets you click on the board corners.
"""

import cv2
import numpy as np
from PIL import Image
import json

def main():
    print("="*70)
    print("MANUAL CALIBRATION TOOL")
    print("="*70)
    
    # Load the screenshot
    try:
        img = cv2.imread('game_screenshot.png')
        if img is None:
            print("\n✗ Could not load game_screenshot.png")
            print("Please run: uv run python examples/capture_window.py")
            return
    except Exception as e:
        print(f"\n✗ Error loading screenshot: {e}")
        return
    
    print("\nInstructions:")
    print("1. Click on the TOP-LEFT corner of the game board (where the grid starts)")
    print("2. Click on the BOTTOM-RIGHT corner of the game board (where the grid ends)")
    print("3. The board should be the 9x9 grid area")
    print("4. Press any key when done to save")
    print("5. Press ESC to cancel")
    print("6. Right-click to reset")
    
    img_display = img.copy()
    points = []
    
    def mouse_callback(event, x, y, flags, param):
        nonlocal img_display, points
        
        if event == cv2.EVENT_LBUTTONDOWN:
            if len(points) < 2:
                points.append((x, y))
                # Draw point
                cv2.circle(img_display, (x, y), 5, (0, 255, 0), -1)
                
                if len(points) == 1:
                    cv2.putText(img_display, "TOP-LEFT", (x+10, y), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                elif len(points) == 2:
                    cv2.putText(img_display, "BOTTOM-RIGHT", (x+10, y), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    # Draw rectangle
                    cv2.rectangle(img_display, points[0], points[1], (0, 255, 0), 2)
                    
                    # Draw grid overlay
                    x1, y1 = points[0]
                    x2, y2 = points[1]
                    w = abs(x2 - x1)
                    h = abs(y2 - y1)
                    cell_w = w / 9
                    cell_h = h / 9
                    
                    for i in range(10):
                        # Vertical lines
                        x_line = int(min(x1, x2) + i * cell_w)
                        cv2.line(img_display, (x_line, min(y1, y2)), (x_line, max(y1, y2)), (255, 255, 0), 1)
                        # Horizontal lines
                        y_line = int(min(y1, y2) + i * cell_h)
                        cv2.line(img_display, (min(x1, x2), y_line), (max(x1, x2), y_line), (255, 255, 0), 1)
                
                cv2.imshow('Manual Calibration', img_display)
        
        elif event == cv2.EVENT_RBUTTONDOWN:
            # Right click to reset
            points.clear()
            img_display = img.copy()
            cv2.imshow('Manual Calibration', img_display)
    
    cv2.namedWindow('Manual Calibration')
    cv2.setMouseCallback('Manual Calibration', mouse_callback)
    cv2.imshow('Manual Calibration', img_display)
    
    print("\nWaiting for clicks... (Right-click to reset)")
    
    key = cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    if key == 27:  # ESC
        print("\n✗ Calibration cancelled")
        return
    
    if len(points) != 2:
        print("\n✗ Need exactly 2 points!")
        return
    
    # Calculate board rectangle
    x1, y1 = points[0]
    x2, y2 = points[1]
    x = min(x1, x2)
    y = min(y1, y2)
    w = abs(x2 - x1)
    h = abs(y2 - y1)
    
    print(f"\n✓ Board position: ({x}, {y})")
    print(f"✓ Board size: {w}×{h} pixels")
    print(f"✓ Cell size: {w/9:.1f}×{h/9:.1f} pixels")
    
    # Now let's detect the score regions
    print("\n" + "="*70)
    print("DETECTING SCORE REGIONS")
    print("="*70)
    
    # Assume scores are above the board
    # High score is on the left, current score is on the right
    # Let's use reasonable defaults based on typical layout
    
    # High score region (top-left area)
    high_score_x = 50
    high_score_y = max(0, y - 170)  # Above the board
    high_score_w = 100
    high_score_h = 30
    
    # Current score region (top-right area)
    current_score_x = x + w - 150
    current_score_y = max(0, y - 170)
    current_score_w = 100
    current_score_h = 30
    
    # Next balls region (top-center)
    next_balls_x = x + w // 2 - 60
    next_balls_y = max(0, y - 170)
    next_balls_w = 120
    next_balls_h = 40
    
    # Show the regions
    img_regions = img.copy()
    cv2.rectangle(img_regions, (x, y), (x+w, y+h), (0, 255, 0), 2)
    cv2.putText(img_regions, "BOARD", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    cv2.rectangle(img_regions, (high_score_x, high_score_y), 
                 (high_score_x+high_score_w, high_score_y+high_score_h), (255, 0, 0), 2)
    cv2.putText(img_regions, "HIGH SCORE", (high_score_x, high_score_y-10), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
    
    cv2.rectangle(img_regions, (current_score_x, current_score_y), 
                 (current_score_x+current_score_w, current_score_y+current_score_h), (0, 0, 255), 2)
    cv2.putText(img_regions, "CURRENT SCORE", (current_score_x, current_score_y-10), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    
    cv2.rectangle(img_regions, (next_balls_x, next_balls_y), 
                 (next_balls_x+next_balls_w, next_balls_y+next_balls_h), (255, 255, 0), 2)
    cv2.putText(img_regions, "NEXT BALLS", (next_balls_x, next_balls_y-10), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
    
    cv2.imshow('Detected Regions', img_regions)
    print("\nShowing detected regions...")
    print("Press any key if this looks correct, or ESC to cancel")
    
    key = cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    if key == 27:  # ESC
        print("\n✗ Calibration cancelled")
        return
    
    # Save configuration
    config = {
        "window_title": "五子连珠5.2",
        "window_rect": [0, 0, img.shape[1], img.shape[0]],
        "board_rect": [x, y, w, h],
        "high_score_rect": [high_score_x, high_score_y, high_score_w, high_score_h],
        "current_score_rect": [current_score_x, current_score_y, current_score_w, current_score_h],
        "next_balls_rect": [next_balls_x, next_balls_y, next_balls_w, next_balls_h],
        "cell_size": [w/9, h/9]
    }
    
    with open('game_window_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("\n" + "="*70)
    print("✓ CALIBRATION COMPLETE!")
    print("="*70)
    print(f"\nConfiguration saved to: game_window_config.json")
    print("\nNext steps:")
    print("1. Run: uv run python examples/debug_grid_detection.py")
    print("   This will show you the grid overlay and detected balls")
    print("2. If the grid is misaligned, run: uv run python examples/adjust_board_rect.py")
    print("   This will let you fine-tune the board position")

if __name__ == "__main__":
    main()

