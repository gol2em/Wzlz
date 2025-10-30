"""
Interactive tool to manually adjust the board rectangle.

This tool allows you to fine-tune the board region by:
1. Showing the current board rectangle
2. Allowing arrow key adjustments
3. Showing grid overlay in real-time
4. Saving the adjusted configuration
"""

import sys
from pathlib import Path
import numpy as np
import cv2
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from wzlz_ai.window_capture import WindowCapture, GameWindowConfig


def draw_grid_overlay(img: np.ndarray, offset_x: int = 0, offset_y: int = 0) -> np.ndarray:
    """Draw 9x9 grid overlay on image."""
    vis_img = img.copy()
    h, w = vis_img.shape[:2]
    
    cell_w = w / 9
    cell_h = h / 9
    
    # Draw grid
    for i in range(10):
        x = int(i * cell_w + offset_x)
        y = int(i * cell_h + offset_y)
        
        # Vertical lines
        if 0 <= x < w:
            cv2.line(vis_img, (x, 0), (x, h), (0, 255, 0), 1)
        
        # Horizontal lines
        if 0 <= y < h:
            cv2.line(vis_img, (0, y), (w, y), (0, 255, 0), 1)
    
    # Draw row/col numbers
    for i in range(9):
        x = int((i + 0.5) * cell_w + offset_x)
        y = int((i + 0.5) * cell_h + offset_y)
        
        if 0 <= x < w:
            cv2.putText(vis_img, str(i), (x - 5, 15),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)
        if 0 <= y < h:
            cv2.putText(vis_img, str(i), (5, y + 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)
    
    return vis_img


def main():
    """Main adjustment function."""
    print("\n" + "="*70)
    print("BOARD RECTANGLE ADJUSTMENT TOOL")
    print("="*70)
    
    # Check if calibration exists
    config_file = Path('game_window_config.json')
    if not config_file.exists():
        print("\n⚠ Calibration file not found!")
        print("Please run: python examples/calibrate_game_window.py")
        return
    
    # Load configuration
    print("\nLoading calibration...")
    with open(config_file, 'r', encoding='utf-8') as f:
        config_data = json.load(f)
    
    board_rect = list(config_data['board_rect'])
    print(f"✓ Current board rect: {board_rect}")
    
    # Initialize window capture
    print("\nFinding game window...")
    capture = WindowCapture()
    
    if not capture.find_window():
        print("✗ Game window not found!")
        return
    
    print("✓ Game window found")
    
    # Capture full window
    print("\nCapturing window...")
    full_img = capture.capture()
    
    if full_img is None:
        print("✗ Failed to capture window!")
        return
    
    print(f"✓ Captured window: {full_img.shape[1]}×{full_img.shape[0]}")
    
    # Interactive adjustment
    print("\n" + "="*70)
    print("INTERACTIVE ADJUSTMENT")
    print("="*70)
    print("\nControls:")
    print("  Arrow keys: Move board region (1 pixel)")
    print("  Shift + Arrow keys: Move board region (10 pixels)")
    print("  W/S: Adjust height (+/- 1 pixel)")
    print("  A/D: Adjust width (+/- 1 pixel)")
    print("  Shift + W/S: Adjust height (+/- 10 pixels)")
    print("  Shift + A/D: Adjust width (+/- 10 pixels)")
    print("  R: Reset to original")
    print("  Space: Save and exit")
    print("  Q/Esc: Exit without saving")
    
    original_rect = board_rect.copy()
    
    cv2.namedWindow('Board Adjustment', cv2.WINDOW_NORMAL)
    
    while True:
        # Extract current board region
        x, y, w, h = board_rect
        board_img = full_img[y:y+h, x:x+w]
        
        # Draw grid overlay
        vis_img = draw_grid_overlay(board_img)
        
        # Add info text
        info_text = f"Rect: ({x}, {y}, {w}, {h}) | Cell: ({w/9:.1f}, {h/9:.1f})"
        cv2.putText(vis_img, info_text, (10, vis_img.shape[0] - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Show image
        cv2.imshow('Board Adjustment', cv2.cvtColor(vis_img, cv2.COLOR_RGB2BGR))
        
        # Handle key press
        key = cv2.waitKey(1) & 0xFF
        
        # Check for modifiers (Shift)
        step = 1
        if cv2.waitKey(1) & 0xFF == 225:  # Shift key
            step = 10
        
        # Arrow keys (special keys in OpenCV)
        if key == 81 or key == 2:  # Left arrow
            board_rect[0] -= step
        elif key == 83 or key == 3:  # Right arrow
            board_rect[0] += step
        elif key == 82 or key == 0:  # Up arrow
            board_rect[1] -= step
        elif key == 84 or key == 1:  # Down arrow
            board_rect[1] += step
        
        # Width/Height adjustment
        elif key == ord('a') or key == ord('A'):
            board_rect[2] -= (10 if key == ord('A') else 1)
        elif key == ord('d') or key == ord('D'):
            board_rect[2] += (10 if key == ord('D') else 1)
        elif key == ord('w') or key == ord('W'):
            board_rect[3] -= (10 if key == ord('W') else 1)
        elif key == ord('s') or key == ord('S'):
            board_rect[3] += (10 if key == ord('S') else 1)
        
        # Reset
        elif key == ord('r') or key == ord('R'):
            board_rect = original_rect.copy()
            print("Reset to original")
        
        # Save
        elif key == ord(' '):
            print(f"\nSaving new board rect: {board_rect}")
            config_data['board_rect'] = board_rect
            config_data['cell_size'] = [board_rect[2] / 9, board_rect[3] / 9]
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            print("✓ Configuration saved!")
            break
        
        # Quit
        elif key == ord('q') or key == ord('Q') or key == 27:  # Esc
            print("\nExiting without saving")
            break
        
        # Ensure valid bounds
        board_rect[0] = max(0, min(board_rect[0], full_img.shape[1] - board_rect[2]))
        board_rect[1] = max(0, min(board_rect[1], full_img.shape[0] - board_rect[3]))
        board_rect[2] = max(50, min(board_rect[2], full_img.shape[1] - board_rect[0]))
        board_rect[3] = max(50, min(board_rect[3], full_img.shape[0] - board_rect[1]))
    
    cv2.destroyAllWindows()
    
    print("\n" + "="*70)
    print("ADJUSTMENT COMPLETE!")
    print("="*70)
    
    print("\n📊 Next steps:")
    print("1. Run debug tool to verify grid alignment:")
    print("   python examples/debug_grid_detection.py")
    print("2. Test game state reading:")
    print("   python examples/read_game_state.py")


if __name__ == "__main__":
    main()

