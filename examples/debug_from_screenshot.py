"""
Debug grid detection using the saved screenshot.
This ensures we're debugging the exact same image used for calibration.
"""

import cv2
import numpy as np
import json
from pathlib import Path

# Ball color samples (RGB in OpenCV BGR format)
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


def main():
    print("="*70)
    print("DEBUG GRID DETECTION FROM SCREENSHOT")
    print("="*70)
    
    # Load screenshot
    if not Path('game_screenshot.png').exists():
        print("\n✗ game_screenshot.png not found!")
        print("Please run: uv run python examples/capture_window.py")
        return
    
    img = cv2.imread('game_screenshot.png')
    if img is None:
        print("\n✗ Failed to load game_screenshot.png")
        return
    
    print(f"\n✓ Loaded screenshot: {img.shape[1]}×{img.shape[0]} pixels")
    
    # Load configuration
    if not Path('game_window_config.json').exists():
        print("\n✗ game_window_config.json not found!")
        print("Please run: uv run python examples/manual_calibrate_all.py")
        return
    
    with open('game_window_config.json', 'r') as f:
        config = json.load(f)
    
    print("\n✓ Loaded configuration:")
    print(f"  Board: {config['board_rect']}")
    print(f"  High score: {config['high_score_rect']}")
    print(f"  Current score: {config['current_score_rect']}")
    print(f"  Next balls: {config['next_balls_rect']}")
    
    # Extract board region
    x, y, w, h = config['board_rect']
    print(f"\n📍 Extracting board from screenshot:")
    print(f"   Screenshot size: {img.shape[1]}×{img.shape[0]}")
    print(f"   Board rect: x={x}, y={y}, w={w}, h={h}")
    print(f"   Extracting: img[{y}:{y+h}, {x}:{x+w}]")

    board_img = img[y:y+h, x:x+w].copy()

    print(f"\n✓ Extracted board: {board_img.shape[1]}×{board_img.shape[0]} pixels")
    print(f"   Expected: {w}×{h} pixels")

    if board_img.shape[1] != w or board_img.shape[0] != h:
        print(f"\n⚠ WARNING: Extracted size doesn't match config!")
        print(f"   This might indicate an issue with the configuration.")
    
    # Calculate cell size
    cell_w = w / 9
    cell_h = h / 9
    print(f"  Cell size: {cell_w:.1f}×{cell_h:.1f} pixels")
    
    # Create visualization
    vis_img = board_img.copy()
    full_vis = img.copy()
    
    print("\n" + "="*70)
    print("ANALYZING CELLS")
    print("="*70)
    
    # Analyze each cell
    for row in range(9):
        for col in range(9):
            # Cell boundaries
            x1 = int(col * cell_w)
            y1 = int(row * cell_h)
            x2 = int((col + 1) * cell_w)
            y2 = int((row + 1) * cell_h)
            
            # Draw grid
            cv2.rectangle(vis_img, (x1, y1), (x2, y2), (0, 255, 255), 1)
            
            # Sample center 50% of cell to avoid borders
            sample_x1 = int(x1 + cell_w * 0.25)
            sample_y1 = int(y1 + cell_h * 0.25)
            sample_x2 = int(x2 - cell_w * 0.25)
            sample_y2 = int(y2 - cell_h * 0.25)
            
            # Get average color
            cell_region = board_img[sample_y1:sample_y2, sample_x1:sample_x2]
            if cell_region.size > 0:
                avg_color = np.mean(cell_region, axis=(0, 1))
                
                # Detect ball color
                ball_color, distance = detect_ball_color(avg_color)
                
                # Only show non-empty cells
                if ball_color != 'EMPTY' or distance < 50:
                    print(f"Cell ({row},{col}): {ball_color:8s} - BGR({int(avg_color[0]):3d},{int(avg_color[1]):3d},{int(avg_color[2]):3d}) - Distance: {distance:.1f}")
                    
                    # Draw marker
                    center_x = (x1 + x2) // 2
                    center_y = (y1 + y2) // 2
                    
                    if ball_color != 'EMPTY':
                        cv2.circle(vis_img, (center_x, center_y), 8, (0, 255, 0), 2)
                        cv2.putText(vis_img, ball_color[0], (center_x-5, center_y+5),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
    
    # Draw all regions on full image
    x, y, w, h = config['board_rect']
    cv2.rectangle(full_vis, (x, y), (x+w, y+h), (0, 255, 0), 2)
    cv2.putText(full_vis, "BOARD", (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    x, y, w, h = config['high_score_rect']
    cv2.rectangle(full_vis, (x, y), (x+w, y+h), (255, 0, 0), 2)
    cv2.putText(full_vis, "HIGH", (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)
    
    x, y, w, h = config['current_score_rect']
    cv2.rectangle(full_vis, (x, y), (x+w, y+h), (0, 0, 255), 2)
    cv2.putText(full_vis, "CURRENT", (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
    
    x, y, w, h = config['next_balls_rect']
    cv2.rectangle(full_vis, (x, y), (x+w, y+h), (255, 255, 0), 2)
    cv2.putText(full_vis, "NEXT", (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)
    
    # Save debug images
    cv2.imwrite('debug_board_grid.png', vis_img)
    cv2.imwrite('debug_full_regions.png', full_vis)
    
    print("\n✓ Debug images saved:")
    print("  - debug_board_grid.png (board with grid overlay)")
    print("  - debug_full_regions.png (full window with all regions)")
    
    # Show images
    print("\nDisplaying images...")
    print("Press any key to close...")

    # Show original screenshot with board rectangle for comparison
    img_with_rect = img.copy()
    x, y, w, h = config['board_rect']
    cv2.rectangle(img_with_rect, (x, y), (x+w, y+h), (0, 255, 0), 2)
    cv2.putText(img_with_rect, f"Board: {x},{y} {w}x{h}", (x, y-5),
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    cv2.imshow('1. Original Screenshot + Board Rect', img_with_rect)
    cv2.imshow('2. Extracted Board + Grid', vis_img)
    cv2.imshow('3. Full Regions', full_vis)

    # Color picker
    def mouse_callback(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            color = board_img[y, x]
            print(f"\nClicked at ({x},{y}): BGR({color[0]}, {color[1]}, {color[2]})")

    cv2.setMouseCallback('2. Extracted Board + Grid', mouse_callback)
    
    print("\n💡 TIP: Click on balls to see their actual BGR values")
    
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    print("\n" + "="*70)
    print("DEBUG COMPLETE!")
    print("="*70)
    print("\n📊 Next steps:")
    print("1. Check if grid aligns with balls in debug_board_grid.png")
    print("2. If misaligned: run 'uv run python examples/adjust_board_rect.py'")
    print("3. If colors wrong: update BALL_COLOR_SAMPLES with actual BGR values")
    print("4. Note: OpenCV uses BGR format, not RGB!")


if __name__ == "__main__":
    main()

