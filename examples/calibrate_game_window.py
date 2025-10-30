"""
Interactive calibration tool for the Wzlz game window.

This script helps you find and calibrate the game window positions for:
- Game board (9x9 grid)
- Score display
- Next balls preview
- Move counter

Since widget sizes are fixed, calibration only needs to be done once.
"""

import sys
import json
from pathlib import Path

try:
    import win32gui
    import win32ui
    import win32con
    from PIL import Image
    import numpy as np
    import cv2
except ImportError:
    print("Missing dependencies! Install with:")
    print("  pip install pywin32 pillow opencv-python")
    sys.exit(1)


def find_game_window():
    """Find the Wzlz game window."""
    print("\n" + "="*70)
    print("STEP 1: Find Game Window")
    print("="*70)
    
    def callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title:
                windows.append((hwnd, title))
        return True
    
    windows = []
    win32gui.EnumWindows(callback, windows)
    
    # Filter for game window
    game_windows = [(hwnd, title) for hwnd, title in windows 
                    if "五子连珠" in title or "wzlz" in title.lower()]
    
    if not game_windows:
        print("\n⚠ Game window not found!")
        print("Please make sure the game (五子连珠5.2) is running.")
        print("\nAll visible windows:")
        for i, (hwnd, title) in enumerate(windows[:20], 1):
            print(f"  {i}. {title}")
        return None
    
    if len(game_windows) == 1:
        hwnd, title = game_windows[0]
        print(f"\n✓ Found game window: {title}")
        return hwnd
    
    # Multiple windows found
    print("\nMultiple game windows found:")
    for i, (hwnd, title) in enumerate(game_windows, 1):
        print(f"  {i}. {title}")
    
    choice = int(input("\nSelect window number: ")) - 1
    return game_windows[choice][0]


def capture_window(hwnd):
    """Capture screenshot of a window."""
    # Get window rect
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    width = right - left
    height = bottom - top
    
    # Get window DC
    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()
    
    # Create bitmap
    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
    saveDC.SelectObject(saveBitMap)
    
    # Capture
    saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)
    
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


def find_board_in_image(img_array):
    """Find the game board in the screenshot using edge detection."""
    print("\n" + "="*70)
    print("STEP 2: Detect Game Board")
    print("="*70)
    
    # Convert to grayscale
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    
    # Edge detection
    edges = cv2.Canny(gray, 50, 150)
    
    # Find contours
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Find the largest rectangular contour (likely the board)
    board_contour = None
    max_area = 0
    
    for contour in contours:
        # Approximate contour to polygon
        epsilon = 0.02 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        
        # Check if it's roughly rectangular (4 corners)
        if len(approx) >= 4:
            area = cv2.contourArea(contour)
            if area > max_area:
                x, y, w, h = cv2.boundingRect(contour)
                # Check aspect ratio (board should be roughly square)
                aspect_ratio = float(w) / h
                if 0.8 < aspect_ratio < 1.2 and area > 10000:  # Minimum size
                    max_area = area
                    board_contour = (x, y, w, h)
    
    if board_contour:
        x, y, w, h = board_contour
        print(f"\n✓ Board detected at: ({x}, {y})")
        print(f"✓ Board size: {w}×{h} pixels")
        print(f"✓ Cell size: {w/9:.1f}×{h/9:.1f} pixels")
        return board_contour
    
    print("\n⚠ Could not auto-detect board. Manual calibration needed.")
    return None


def manual_board_calibration(img):
    """Manual board calibration using mouse clicks."""
    print("\n" + "="*70)
    print("STEP 2b: Manual Board Calibration")
    print("="*70)
    print("\nInstructions:")
    print("1. A window will open showing the game screenshot")
    print("2. Click on the TOP-LEFT corner of the board")
    print("3. Click on the BOTTOM-RIGHT corner of the board")
    print("4. Press any key to confirm")
    
    img_array = np.array(img)
    img_display = img_array.copy()
    
    points = []
    
    def mouse_callback(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            points.append((x, y))
            cv2.circle(img_display, (x, y), 5, (0, 255, 0), -1)
            cv2.imshow('Calibration', img_display)
            
            if len(points) == 2:
                # Draw rectangle
                cv2.rectangle(img_display, points[0], points[1], (0, 255, 0), 2)
                cv2.imshow('Calibration', img_display)
    
    cv2.namedWindow('Calibration')
    cv2.setMouseCallback('Calibration', mouse_callback)
    cv2.imshow('Calibration', img_display)
    
    print("\nClick on the board corners...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    if len(points) == 2:
        x1, y1 = points[0]
        x2, y2 = points[1]
        x = min(x1, x2)
        y = min(y1, y2)
        w = abs(x2 - x1)
        h = abs(y2 - y1)
        
        print(f"\n✓ Board position: ({x}, {y})")
        print(f"✓ Board size: {w}×{h} pixels")
        print(f"✓ Cell size: {w/9:.1f}×{h/9:.1f} pixels")
        
        return (x, y, w, h)
    
    return None


def detect_score_regions(img_array, board_rect):
    """Detect high score (top-left) and current score (top-right) regions."""
    print("\n" + "="*70)
    print("STEP 3: Detect Score Regions")
    print("="*70)

    # Get image dimensions
    img_h, img_w = img_array.shape[:2]
    board_x, board_y, board_w, board_h = board_rect

    # High score region (top-left, above board)
    high_score_x = 20
    high_score_y = 60
    high_score_w = 100
    high_score_h = 40

    # Current score region (top-right, above board)
    current_score_x = img_w - 120
    current_score_y = 60
    current_score_w = 100
    current_score_h = 40

    print(f"\n✓ High score region (top-left): ({high_score_x}, {high_score_y}, {high_score_w}, {high_score_h})")
    print(f"✓ Current score region (top-right): ({current_score_x}, {current_score_y}, {current_score_w}, {current_score_h})")

    return (high_score_x, high_score_y, high_score_w, high_score_h), \
           (current_score_x, current_score_y, current_score_w, current_score_h)


def detect_next_balls_region(img_array, board_rect):
    """Detect next balls preview region (top-center)."""
    print("\n" + "="*70)
    print("STEP 4: Detect Next Balls Region")
    print("="*70)
    
    # Next balls are in the center-top area
    board_x, board_y, board_w, board_h = board_rect
    
    # Estimate next balls region (center-top)
    next_x = board_x + board_w // 2 - 60
    next_y = 60
    next_w = 120
    next_h = 40
    
    print(f"\n✓ Next balls region: ({next_x}, {next_y}, {next_w}, {next_h})")
    
    return (next_x, next_y, next_w, next_h)


def save_calibration(hwnd, board_rect, high_score_rect, current_score_rect, next_balls_rect, window_rect):
    """Save calibration data to file."""
    print("\n" + "="*70)
    print("STEP 5: Save Calibration")
    print("="*70)

    calibration = {
        'window_title': win32gui.GetWindowText(hwnd),
        'window_rect': window_rect,
        'board_rect': board_rect,
        'high_score_rect': high_score_rect,
        'current_score_rect': current_score_rect,
        'next_balls_rect': next_balls_rect,
        'cell_size': (board_rect[2] / 9, board_rect[3] / 9)
    }

    # Save to file
    config_file = Path('game_window_config.json')
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(calibration, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Calibration saved to: {config_file}")
    print("\nCalibration data:")
    print(json.dumps(calibration, indent=2, ensure_ascii=False))

    return calibration


def main():
    """Main calibration workflow."""
    print("\n" + "="*70)
    print("WZLZ GAME WINDOW CALIBRATION")
    print("="*70)
    print("\nThis tool will help you calibrate the game window for image capture.")
    print("\nPrerequisites:")
    print("  ✓ Game (五子连珠5.2) is running")
    print("  ✓ Game window is visible")
    print("  ✓ Dependencies installed")
    
    input("\nPress Enter to start...")
    
    # Step 1: Find game window
    hwnd = find_game_window()
    if not hwnd:
        return
    
    # Capture window
    print("\nCapturing window...")
    img, window_rect = capture_window(hwnd)
    img_array = np.array(img)
    
    # Save screenshot for reference
    img.save('game_screenshot.png')
    print(f"✓ Screenshot saved to: game_screenshot.png")
    
    # Step 2: Find board
    board_rect = find_board_in_image(img_array)
    
    if not board_rect:
        # Manual calibration
        board_rect = manual_board_calibration(img)
        if not board_rect:
            print("\n✗ Calibration failed!")
            return
    
    # Step 3: Detect score regions
    high_score_rect, current_score_rect = detect_score_regions(img_array, board_rect)

    # Step 4: Detect next balls region
    next_balls_rect = detect_next_balls_region(img_array, board_rect)

    # Step 5: Save calibration
    calibration = save_calibration(hwnd, board_rect, high_score_rect, current_score_rect, next_balls_rect, window_rect)
    
    # Visualize calibration
    print("\n" + "="*70)
    print("CALIBRATION COMPLETE!")
    print("="*70)
    
    # Draw rectangles on image
    vis_img = img_array.copy()
    board_x, board_y, board_w, board_h = board_rect
    high_score_x, high_score_y, high_score_w, high_score_h = high_score_rect
    current_score_x, current_score_y, current_score_w, current_score_h = current_score_rect
    next_x, next_y, next_w, next_h = next_balls_rect

    cv2.rectangle(vis_img, (board_x, board_y), (board_x + board_w, board_y + board_h), (0, 255, 0), 2)
    cv2.rectangle(vis_img, (high_score_x, high_score_y), (high_score_x + high_score_w, high_score_y + high_score_h), (255, 0, 0), 2)
    cv2.rectangle(vis_img, (current_score_x, current_score_y), (current_score_x + current_score_w, current_score_y + current_score_h), (255, 165, 0), 2)
    cv2.rectangle(vis_img, (next_x, next_y), (next_x + next_w, next_y + next_h), (0, 0, 255), 2)

    # Add labels
    cv2.putText(vis_img, "High Score", (high_score_x, high_score_y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
    cv2.putText(vis_img, "Current Score", (current_score_x, current_score_y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 165, 0), 1)
    cv2.putText(vis_img, "Next Balls", (next_x, next_y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
    cv2.putText(vis_img, "Board", (board_x, board_y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    
    # Draw grid on board
    cell_w = board_w / 9
    cell_h = board_h / 9
    for i in range(10):
        x = int(board_x + i * cell_w)
        y = int(board_y + i * cell_h)
        cv2.line(vis_img, (x, board_y), (x, board_y + board_h), (255, 255, 0), 1)
        cv2.line(vis_img, (board_x, y), (board_x + board_w, y), (255, 255, 0), 1)
    
    cv2.imwrite('calibration_result.png', cv2.cvtColor(vis_img, cv2.COLOR_RGB2BGR))
    print("\n✓ Calibration visualization saved to: calibration_result.png")
    
    print("\nNext steps:")
    print("1. Review 'calibration_result.png' to verify the regions")
    print("2. If incorrect, run this script again")
    print("3. Use 'game_window_config.json' with the game client")
    print("4. Run 'python examples/test_image_capture.py' to test")


if __name__ == "__main__":
    main()

