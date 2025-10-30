"""
Capture live window and auto-detect regions based on visual characteristics.

Visual characteristics:
- Grid background: Gray
- Score regions: Black background with white numbers
- Next balls preview: Gray background (same as grid)
"""

import cv2
import numpy as np
import win32gui
import win32ui
import win32con
from PIL import Image
import time
import json


def capture_window_live(window_title):
    """Capture the game window live."""
    hwnd = win32gui.FindWindow(None, window_title)
    
    if not hwnd:
        print(f"✗ Window '{window_title}' not found!")
        return None, None
    
    # Bring window to front
    if win32gui.IsIconic(hwnd):
        win32gui.ShowWindow(hwnd, 9)  # SW_RESTORE
    
    win32gui.SetForegroundWindow(hwnd)
    time.sleep(0.5)
    
    # Get window dimensions
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    width = right - left
    height = bottom - top
    
    print(f"✓ Found window: {window_title}")
    print(f"  Position: ({left}, {top})")
    print(f"  Size: {width}×{height}")
    
    # Capture window
    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()
    
    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
    saveDC.SelectObject(saveBitMap)
    
    # Use PrintWindow to capture
    import ctypes
    result = ctypes.windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 3)
    
    # Convert to PIL Image
    bmpinfo = saveBitMap.GetInfo()
    bmpstr = saveBitMap.GetBitmapBits(True)
    img = Image.frombuffer(
        'RGB',
        (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
        bmpstr, 'raw', 'BGRX', 0, 1
    )
    
    # Cleanup
    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)
    
    return img, (left, top, width, height)


def detect_gray_regions(img):
    """Detect gray regions (grid and next balls preview)."""
    img_np = np.array(img)
    img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

    # Convert to HSV for better color detection
    img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)

    # Gray has low saturation
    # Define range for gray color (low saturation, medium-high value)
    # Adjusted to capture lighter grays
    lower_gray = np.array([0, 0, 150])
    upper_gray = np.array([180, 60, 210])

    mask_gray = cv2.inRange(img_hsv, lower_gray, upper_gray)

    # Also try direct BGR color matching for the specific gray (170, 170, 170)
    lower_gray_bgr = np.array([150, 150, 150])
    upper_gray_bgr = np.array([190, 190, 190])
    mask_gray_bgr = cv2.inRange(img_bgr, lower_gray_bgr, upper_gray_bgr)

    # Combine both masks
    mask_gray = cv2.bitwise_or(mask_gray, mask_gray_bgr)

    return mask_gray


def detect_black_regions(img):
    """Detect black regions (score backgrounds)."""
    img_np = np.array(img)
    img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
    
    # Convert to HSV
    img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    
    # Black has low value
    lower_black = np.array([0, 0, 0])
    upper_black = np.array([180, 255, 50])
    
    mask_black = cv2.inRange(img_hsv, lower_black, upper_black)
    
    return mask_black


def find_largest_contour(mask, min_area=1000):
    """Find the largest contour in a mask."""
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return None

    # Filter by area and find largest
    valid_contours = [c for c in contours if cv2.contourArea(c) > min_area]

    if not valid_contours:
        return None

    largest = max(valid_contours, key=cv2.contourArea)
    return cv2.boundingRect(largest)


def find_square_region(mask, min_area=10000, aspect_ratio_range=(0.8, 1.2)):
    """Find the largest square-ish region (for the 9x9 grid)."""
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return None

    # Filter by area and aspect ratio (should be roughly square)
    valid_contours = []
    for c in contours:
        area = cv2.contourArea(c)
        if area > min_area:
            x, y, w, h = cv2.boundingRect(c)
            aspect_ratio = w / h if h > 0 else 0
            if aspect_ratio_range[0] <= aspect_ratio <= aspect_ratio_range[1]:
                valid_contours.append(c)

    if not valid_contours:
        return None

    largest = max(valid_contours, key=cv2.contourArea)
    return cv2.boundingRect(largest)


def find_horizontal_region(mask, min_area=500, max_height=50, y_max=None):
    """Find horizontal regions (for next balls preview - 3 cells wide, 1 cell tall)."""
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return None

    # Filter by area, aspect ratio (wider than tall), and position (top area)
    valid_contours = []
    for c in contours:
        area = cv2.contourArea(c)
        if area > min_area:
            x, y, w, h = cv2.boundingRect(c)
            # Should be wider than tall
            if w > h and h < max_height:
                # Should be in top area if y_max specified
                if y_max is None or y < y_max:
                    valid_contours.append((c, x, y, w, h))

    if not valid_contours:
        return None

    # Sort by area and return largest
    valid_contours.sort(key=lambda item: cv2.contourArea(item[0]), reverse=True)
    return valid_contours[0][1:]  # Return (x, y, w, h)


def main():
    print("="*70)
    print("LIVE CAPTURE AND AUTO-DETECTION")
    print("="*70)
    
    window_title = "五子连珠5.2"
    
    # Step 1: Capture live window
    print("\n" + "="*70)
    print("STEP 1: CAPTURE LIVE WINDOW")
    print("="*70)
    
    img, window_rect = capture_window_live(window_title)
    
    if img is None:
        print("\n✗ Failed to capture window!")
        return
    
    # Save the live capture
    img.save('live_capture.png')
    print(f"\n✓ Saved live capture to: live_capture.png")
    print(f"  Size: {img.width}×{img.height}")
    
    # Convert to numpy for processing
    img_np = np.array(img)
    img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
    
    # Step 2: Detect gray regions (grid + next balls)
    print("\n" + "="*70)
    print("STEP 2: DETECT GRAY REGIONS")
    print("="*70)

    mask_gray = detect_gray_regions(img)
    cv2.imwrite('debug_gray_mask_raw.png', mask_gray)
    print("✓ Saved raw gray mask to: debug_gray_mask_raw.png")

    # Apply morphological closing to connect nearby gray regions (cells)
    # This will merge the individual cells into one board region
    kernel = np.ones((5, 5), np.uint8)
    mask_gray_closed = cv2.morphologyEx(mask_gray, cv2.MORPH_CLOSE, kernel, iterations=2)
    cv2.imwrite('debug_gray_mask.png', mask_gray_closed)
    print("✓ Saved processed gray mask to: debug_gray_mask.png")

    # Debug: find all contours in processed gray mask
    contours_gray, _ = cv2.findContours(mask_gray_closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    print(f"\nFound {len(contours_gray)} gray contours after morphological closing:")
    for i, c in enumerate(contours_gray[:10]):  # Show first 10
        x, y, w, h = cv2.boundingRect(c)
        area = cv2.contourArea(c)
        aspect = w/h if h > 0 else 0
        print(f"  {i}: pos=({x},{y}) size={w}×{h} area={area:.0f} aspect={aspect:.2f}")

    # Find the square-ish region (should be the 9x9 board)
    # Relax aspect ratio a bit since the board might not be perfectly square
    board_rect = find_square_region(mask_gray_closed, min_area=10000, aspect_ratio_range=(0.8, 1.3))

    if board_rect:
        print(f"✓ Detected board region (9x9 grid): {board_rect}")
        x, y, w, h = board_rect
        print(f"  Aspect ratio: {w/h:.2f} (should be ~1.0 for square)")
    else:
        print("✗ Could not detect board region")

    # Find horizontal region for next balls (should be above the board)
    next_balls_rect = None
    if board_rect:
        # Look for horizontal regions above the board (use raw mask, not closed)
        next_balls_rect = find_horizontal_region(mask_gray, min_area=500,
                                                  max_height=50, y_max=board_rect[1])
        if next_balls_rect:
            print(f"✓ Detected next balls preview: {next_balls_rect}")
            x, y, w, h = next_balls_rect
            print(f"  Aspect ratio: {w/h:.2f} (should be ~3.0 for 3 cells)")
        else:
            print("⚠ Could not detect next balls preview")
    
    # Step 3: Detect black regions (scores)
    print("\n" + "="*70)
    print("STEP 3: DETECT BLACK REGIONS (SCORES)")
    print("="*70)
    
    mask_black = detect_black_regions(img)
    cv2.imwrite('debug_black_mask.png', mask_black)
    print("✓ Saved black mask to: debug_black_mask.png")
    
    # Find all black regions
    contours, _ = cv2.findContours(mask_black, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    black_regions = [cv2.boundingRect(c) for c in contours if cv2.contourArea(c) > 200]
    
    print(f"✓ Found {len(black_regions)} black regions")
    for i, rect in enumerate(black_regions):
        print(f"  Region {i}: {rect}")
    
    # Step 4: Visualize all detected regions
    print("\n" + "="*70)
    print("STEP 4: VISUALIZE DETECTED REGIONS")
    print("="*70)
    
    vis_img = img_bgr.copy()
    
    # Draw board
    if board_rect:
        x, y, w, h = board_rect
        cv2.rectangle(vis_img, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.putText(vis_img, "BOARD (auto)", (x, y-5), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Draw grid
        cell_w = w / 9
        cell_h = h / 9
        for i in range(10):
            x_line = int(x + i * cell_w)
            cv2.line(vis_img, (x_line, y), (x_line, y+h), (255, 255, 0), 1)
            y_line = int(y + i * cell_h)
            cv2.line(vis_img, (x, y_line), (x+w, y_line), (255, 255, 0), 1)
    
    # Draw next balls preview
    if next_balls_rect:
        x, y, w, h = next_balls_rect
        cv2.rectangle(vis_img, (x, y), (x+w, y+h), (255, 255, 0), 2)
        cv2.putText(vis_img, "NEXT BALLS (auto)", (x, y-5),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)

    # Draw black regions (scores)
    for i, (x, y, w, h) in enumerate(black_regions):
        cv2.rectangle(vis_img, (x, y), (x+w, y+h), (255, 0, 0), 2)
        cv2.putText(vis_img, f"BLACK {i}", (x, y-5),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)
    
    cv2.imwrite('debug_detected_regions.png', vis_img)
    print("✓ Saved visualization to: debug_detected_regions.png")
    
    # Show the image
    cv2.imshow('Detected Regions', vis_img)
    print("\nPress any key to continue...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    # Step 5: Try to identify specific regions
    print("\n" + "="*70)
    print("STEP 5: IDENTIFY SPECIFIC REGIONS")
    print("="*70)
    
    if not board_rect:
        print("✗ Cannot proceed without board detection")
        return
    
    bx, by, bw, bh = board_rect
    
    # Sort black regions by position
    # High score should be on the left, current score on the right
    left_regions = [r for r in black_regions if r[0] < bx]
    right_regions = [r for r in black_regions if r[0] > bx + bw]
    
    high_score_rect = None
    current_score_rect = None
    
    if left_regions:
        # Find the one closest to board height
        left_regions.sort(key=lambda r: abs(r[1] - by))
        high_score_rect = left_regions[0]
        print(f"✓ High score (left): {high_score_rect}")
    
    if right_regions:
        # Find the one closest to board height
        right_regions.sort(key=lambda r: abs(r[1] - by))
        current_score_rect = right_regions[0]
        print(f"✓ Current score (right): {current_score_rect}")
    
    # Step 6: Save configuration
    print("\n" + "="*70)
    print("STEP 6: SAVE CONFIGURATION")
    print("="*70)

    if not all([board_rect, high_score_rect, current_score_rect, next_balls_rect]):
        print("⚠ Not all regions detected. Manual calibration may be needed.")
        print("\nDetected:")
        print(f"  Board: {board_rect}")
        print(f"  High score: {high_score_rect}")
        print(f"  Current score: {current_score_rect}")
        print(f"  Next balls: {next_balls_rect}")

        if not next_balls_rect:
            print("\n💡 TIP: Next balls preview might not be visible in current game state")
            print("   You can manually set it later if needed")
        return
    
    config = {
        "window_title": window_title,
        "window_rect": list(window_rect),
        "board_rect": list(board_rect),
        "high_score_rect": list(high_score_rect) if high_score_rect else [0, 0, 0, 0],
        "current_score_rect": list(current_score_rect) if current_score_rect else [0, 0, 0, 0],
        "next_balls_rect": list(next_balls_rect) if next_balls_rect else [0, 0, 0, 0],
        "cell_size": [board_rect[2]/9, board_rect[3]/9]
    }
    
    with open('game_window_config_auto.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✓ Configuration saved to: game_window_config_auto.json")
    print("\nConfiguration:")
    print(f"  Board: {board_rect}")
    print(f"  High score: {high_score_rect}")
    print(f"  Current score: {current_score_rect}")
    print(f"  Next balls: {next_balls_rect}")
    print(f"  Cell size: {board_rect[2]/9:.1f}×{board_rect[3]/9:.1f}")
    
    print("\n" + "="*70)
    print("COMPLETE!")
    print("="*70)
    print("\nFiles saved:")
    print("  - live_capture.png (the captured window)")
    print("  - debug_gray_mask.png (gray regions mask)")
    print("  - debug_black_mask.png (black regions mask)")
    print("  - debug_detected_regions.png (visualization)")
    print("  - game_window_config_auto.json (auto-detected config)")
    print("\nNext step:")
    print("  Compare live_capture.png with game_screenshot.png")
    print("  If they match, you can use the auto-detected config!")


if __name__ == "__main__":
    main()

