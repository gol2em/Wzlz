"""
Debug grid detection to visualize cell boundaries and detected colors.

This script helps diagnose grid alignment issues by:
1. Showing the detected grid overlay on the board
2. Displaying average color for each cell
3. Showing detected ball colors
4. Allowing manual adjustment of grid parameters
"""

import sys
from pathlib import Path
import numpy as np
import cv2

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from wzlz_ai.window_capture import WindowCapture, GameWindowConfig, extract_cell_colors
from wzlz_ai import BallColor


# Ball color samples (RGB values)
BALL_COLOR_SAMPLES = {
    BallColor.RED: np.array([200, 50, 50]),
    BallColor.GREEN: np.array([50, 200, 50]),
    BallColor.BLUE: np.array([50, 50, 200]),
    BallColor.BROWN: np.array([150, 100, 50]),
    BallColor.MAGENTA: np.array([200, 50, 200]),
    BallColor.YELLOW: np.array([200, 200, 50]),
    BallColor.CYAN: np.array([50, 200, 200]),
    BallColor.EMPTY: np.array([180, 180, 180]),
}


def color_distance(color1: np.ndarray, color2: np.ndarray) -> float:
    """Calculate Euclidean distance between two colors."""
    return np.linalg.norm(color1 - color2)


def detect_ball_color(avg_color: np.ndarray, threshold: float = 80.0):
    """Detect ball color from average cell color."""
    best_match = BallColor.EMPTY
    min_distance = float('inf')
    
    for ball_color, sample_color in BALL_COLOR_SAMPLES.items():
        distance = color_distance(avg_color, sample_color)
        if distance < min_distance:
            min_distance = distance
            best_match = ball_color
    
    return best_match, min_distance


def visualize_grid_detection(board_img: np.ndarray, board_rect: tuple) -> np.ndarray:
    """
    Visualize grid detection with detailed information.
    
    Args:
        board_img: Board image
        board_rect: Board rectangle (x, y, w, h)
        
    Returns:
        Annotated image
    """
    vis_img = board_img.copy()
    h, w = vis_img.shape[:2]
    
    print(f"\nBoard image size: {w}×{h}")
    print(f"Board rect: {board_rect}")
    
    # Calculate cell size
    cell_w = w / 9
    cell_h = h / 9
    
    print(f"Cell size: {cell_w:.2f}×{cell_h:.2f}")
    
    # Extract cell colors
    cell_colors = extract_cell_colors(board_img, rows=9, cols=9)
    
    # Draw grid and analyze each cell
    print("\n" + "="*70)
    print("CELL ANALYSIS")
    print("="*70)
    
    for row in range(9):
        for col in range(9):
            # Cell boundaries
            x1 = int(col * cell_w)
            y1 = int(row * cell_h)
            x2 = int((col + 1) * cell_w)
            y2 = int((row + 1) * cell_h)
            
            # Draw grid lines
            cv2.rectangle(vis_img, (x1, y1), (x2, y2), (255, 255, 0), 1)
            
            # Get average color
            avg_color = cell_colors[row, col]
            
            # Detect ball color
            ball_color, distance = detect_ball_color(avg_color)
            
            # Draw cell center
            center_x = int((col + 0.5) * cell_w)
            center_y = int((row + 0.5) * cell_h)
            
            if ball_color != BallColor.EMPTY:
                # Draw detected ball
                cv2.circle(vis_img, (center_x, center_y), 8, (0, 255, 0), 2)
                
                # Draw label
                label = ball_color.name[0]
                cv2.putText(vis_img, label, (center_x - 8, center_y + 5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                
                # Print info
                print(f"Cell ({row},{col}): {ball_color.name:8s} - "
                      f"RGB({avg_color[0]:3.0f},{avg_color[1]:3.0f},{avg_color[2]:3.0f}) - "
                      f"Distance: {distance:.1f}")
            
            # Draw row/col labels
            if col == 0:
                cv2.putText(vis_img, str(row), (5, center_y + 5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)
            if row == 0:
                cv2.putText(vis_img, str(col), (center_x - 5, 15),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)
    
    return vis_img


def show_color_samples(board_img: np.ndarray):
    """Show actual colors from the board for calibration."""
    print("\n" + "="*70)
    print("COLOR CALIBRATION HELPER")
    print("="*70)
    print("\nClick on balls in the image to see their RGB values.")
    print("Use these values to update BALL_COLOR_SAMPLES.")
    print("Press 'q' to quit.\n")
    
    clicked_colors = []
    
    def mouse_callback(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            if 0 <= y < board_img.shape[0] and 0 <= x < board_img.shape[1]:
                color = board_img[y, x]
                print(f"Clicked at ({x}, {y}): RGB({color[0]}, {color[1]}, {color[2]})")
                clicked_colors.append(color)
    
    cv2.namedWindow('Color Picker')
    cv2.setMouseCallback('Color Picker', mouse_callback)
    cv2.imshow('Color Picker', cv2.cvtColor(board_img, cv2.COLOR_RGB2BGR))
    
    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
    
    cv2.destroyAllWindows()
    
    if clicked_colors:
        print("\nClicked colors:")
        for i, color in enumerate(clicked_colors):
            print(f"  {i+1}. RGB({color[0]}, {color[1]}, {color[2]})")


def main():
    """Main debug function."""
    print("\n" + "="*70)
    print("GRID DETECTION DEBUG TOOL")
    print("="*70)
    
    # Check if calibration exists
    config_file = Path('game_window_config.json')
    if not config_file.exists():
        print("\n⚠ Calibration file not found!")
        print("Please run: python examples/calibrate_game_window.py")
        return
    
    # Load configuration
    print("\nLoading calibration...")
    config = GameWindowConfig(str(config_file))
    
    if not config.board_rect:
        print("✗ Invalid configuration!")
        return
    
    print("✓ Configuration loaded")
    print(f"  Board rect: {config.board_rect}")
    
    # Initialize window capture
    print("\nFinding game window...")
    capture = WindowCapture()
    
    if not capture.find_window():
        print("✗ Game window not found!")
        return
    
    print("✓ Game window found")
    
    # Capture board
    print("\nCapturing board...")
    board_img = capture.capture_region(config.board_rect)
    
    if board_img is None:
        print("✗ Failed to capture board!")
        return
    
    print(f"✓ Captured board: {board_img.shape[1]}×{board_img.shape[0]}")
    
    # Visualize grid detection
    print("\nAnalyzing grid...")
    vis_img = visualize_grid_detection(board_img, config.board_rect)
    
    # Save results
    cv2.imwrite('debug_board_raw.png', cv2.cvtColor(board_img, cv2.COLOR_RGB2BGR))
    cv2.imwrite('debug_grid_overlay.png', cv2.cvtColor(vis_img, cv2.COLOR_RGB2BGR))
    
    print("\n✓ Debug images saved:")
    print("  - debug_board_raw.png (raw board capture)")
    print("  - debug_grid_overlay.png (grid overlay with labels)")
    
    # Show images
    print("\nDisplaying images...")
    print("Press any key to continue to color picker...")
    
    cv2.imshow('Raw Board', cv2.cvtColor(board_img, cv2.COLOR_RGB2BGR))
    cv2.imshow('Grid Overlay', cv2.cvtColor(vis_img, cv2.COLOR_RGB2BGR))
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    # Color picker
    show_color_samples(board_img)
    
    print("\n" + "="*70)
    print("DEBUG COMPLETE!")
    print("="*70)
    
    print("\n📊 Next steps:")
    print("1. Check debug_grid_overlay.png to see if grid aligns with balls")
    print("2. If grid is misaligned:")
    print("   - Re-run calibration: python examples/calibrate_game_window.py")
    print("   - Manually adjust board_rect in game_window_config.json")
    print("3. If colors are wrong:")
    print("   - Use the color picker to get actual RGB values")
    print("   - Update BALL_COLOR_SAMPLES in your code")
    print("4. If brown balls not detected:")
    print("   - Check the RGB values of brown balls")
    print("   - Adjust BALL_COLOR_SAMPLES[BallColor.BROWN]")
    print("   - Try increasing color threshold")


if __name__ == "__main__":
    main()

