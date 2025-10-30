"""
Complete manual calibration tool - lets you select all regions by clicking.
"""

import cv2
import numpy as np
import json

def select_rectangle(img, title, instruction):
    """Helper function to select a rectangle by clicking two corners."""
    img_display = img.copy()
    points = []
    
    def mouse_callback(event, x, y, flags, param):
        nonlocal img_display, points
        
        if event == cv2.EVENT_LBUTTONDOWN:
            if len(points) < 2:
                points.append((x, y))
                cv2.circle(img_display, (x, y), 3, (0, 255, 0), -1)
                
                if len(points) == 2:
                    cv2.rectangle(img_display, points[0], points[1], (0, 255, 0), 2)
                
                cv2.imshow(title, img_display)
        
        elif event == cv2.EVENT_RBUTTONDOWN:
            points.clear()
            img_display = img.copy()
            cv2.imshow(title, img_display)
    
    cv2.namedWindow(title)
    cv2.setMouseCallback(title, mouse_callback)
    cv2.imshow(title, img_display)
    
    print(f"\n{instruction}")
    print("  - Click TOP-LEFT corner, then BOTTOM-RIGHT corner")
    print("  - Right-click to reset")
    print("  - Press any key when done")
    
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    if len(points) == 2:
        x1, y1 = points[0]
        x2, y2 = points[1]
        x = min(x1, x2)
        y = min(y1, y2)
        w = abs(x2 - x1)
        h = abs(y2 - y1)
        return [x, y, w, h]
    
    return None

def main():
    print("="*70)
    print("COMPLETE MANUAL CALIBRATION TOOL")
    print("="*70)
    print("\nThis tool will guide you through selecting all regions:")
    print("  1. Game board (9x9 grid)")
    print("  2. High score (top-left)")
    print("  3. Current score (top-right)")
    print("  4. Next balls (top-center)")
    
    # Load screenshot
    try:
        img = cv2.imread('game_screenshot.png')
        if img is None:
            print("\n✗ Could not load game_screenshot.png")
            print("Please run: uv run python examples/capture_window.py")
            return
    except Exception as e:
        print(f"\n✗ Error loading screenshot: {e}")
        return
    
    print(f"\nScreenshot loaded: {img.shape[1]}×{img.shape[0]} pixels")
    input("\nPress Enter to start calibration...")
    
    # Step 1: Select board
    print("\n" + "="*70)
    print("STEP 1: SELECT GAME BOARD")
    print("="*70)
    board_rect = select_rectangle(img, "Select Game Board", 
                                   "Select the 9x9 game grid area")
    
    if not board_rect:
        print("\n✗ Board selection cancelled")
        return
    
    print(f"✓ Board: position=({board_rect[0]}, {board_rect[1]}), size={board_rect[2]}×{board_rect[3]}")
    print(f"  Cell size: {board_rect[2]/9:.1f}×{board_rect[3]/9:.1f} pixels")
    
    # Step 2: Select high score
    print("\n" + "="*70)
    print("STEP 2: SELECT HIGH SCORE REGION")
    print("="*70)
    high_score_rect = select_rectangle(img, "Select High Score", 
                                        "Select the HIGH SCORE number area (top-left)")
    
    if not high_score_rect:
        print("\n✗ High score selection cancelled")
        return
    
    print(f"✓ High score: position=({high_score_rect[0]}, {high_score_rect[1]}), size={high_score_rect[2]}×{high_score_rect[3]}")
    
    # Step 3: Select current score
    print("\n" + "="*70)
    print("STEP 3: SELECT CURRENT SCORE REGION")
    print("="*70)
    current_score_rect = select_rectangle(img, "Select Current Score", 
                                          "Select the CURRENT SCORE number area (top-right)")
    
    if not current_score_rect:
        print("\n✗ Current score selection cancelled")
        return
    
    print(f"✓ Current score: position=({current_score_rect[0]}, {current_score_rect[1]}), size={current_score_rect[2]}×{current_score_rect[3]}")
    
    # Step 4: Select next balls
    print("\n" + "="*70)
    print("STEP 4: SELECT NEXT BALLS REGION")
    print("="*70)
    next_balls_rect = select_rectangle(img, "Select Next Balls", 
                                        "Select the NEXT BALLS preview area (top-center)")
    
    if not next_balls_rect:
        print("\n✗ Next balls selection cancelled")
        return
    
    print(f"✓ Next balls: position=({next_balls_rect[0]}, {next_balls_rect[1]}), size={next_balls_rect[2]}×{next_balls_rect[3]}")
    
    # Show all regions together
    print("\n" + "="*70)
    print("REVIEW ALL REGIONS")
    print("="*70)
    
    img_review = img.copy()
    
    # Draw board
    x, y, w, h = board_rect
    cv2.rectangle(img_review, (x, y), (x+w, y+h), (0, 255, 0), 2)
    cv2.putText(img_review, "BOARD", (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    # Draw grid
    cell_w = w / 9
    cell_h = h / 9
    for i in range(10):
        x_line = int(x + i * cell_w)
        cv2.line(img_review, (x_line, y), (x_line, y+h), (255, 255, 0), 1)
        y_line = int(y + i * cell_h)
        cv2.line(img_review, (x, y_line), (x+w, y_line), (255, 255, 0), 1)
    
    # Draw high score
    x, y, w, h = high_score_rect
    cv2.rectangle(img_review, (x, y), (x+w, y+h), (255, 0, 0), 2)
    cv2.putText(img_review, "HIGH", (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)
    
    # Draw current score
    x, y, w, h = current_score_rect
    cv2.rectangle(img_review, (x, y), (x+w, y+h), (0, 0, 255), 2)
    cv2.putText(img_review, "CURRENT", (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
    
    # Draw next balls
    x, y, w, h = next_balls_rect
    cv2.rectangle(img_review, (x, y), (x+w, y+h), (255, 255, 0), 2)
    cv2.putText(img_review, "NEXT", (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)
    
    cv2.imshow('Review All Regions', img_review)
    print("\nReview all regions. Press any key to save, or ESC to cancel.")
    
    key = cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    if key == 27:  # ESC
        print("\n✗ Calibration cancelled")
        return
    
    # Save configuration
    config = {
        "window_title": "五子连珠5.2",
        "window_rect": [0, 0, img.shape[1], img.shape[0]],
        "board_rect": board_rect,
        "high_score_rect": high_score_rect,
        "current_score_rect": current_score_rect,
        "next_balls_rect": next_balls_rect,
        "cell_size": [board_rect[2]/9, board_rect[3]/9]
    }
    
    with open('game_window_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    # Also save the review image
    cv2.imwrite('calibration_review.png', img_review)
    
    print("\n" + "="*70)
    print("✓ CALIBRATION COMPLETE!")
    print("="*70)
    print(f"\nConfiguration saved to: game_window_config.json")
    print(f"Review image saved to: calibration_review.png")
    print("\nConfiguration:")
    print(f"  Board: {board_rect}")
    print(f"  High score: {high_score_rect}")
    print(f"  Current score: {current_score_rect}")
    print(f"  Next balls: {next_balls_rect}")
    print("\nNext steps:")
    print("  1. Run: uv run python examples/debug_grid_detection.py")
    print("     This will show detected balls and colors")
    print("  2. If grid is misaligned: uv run python examples/adjust_board_rect.py")

if __name__ == "__main__":
    main()

