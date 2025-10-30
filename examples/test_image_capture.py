"""
Test image capture from the game window.

This script demonstrates how to:
1. Find and capture the game window
2. Load calibration data
3. Extract board state
4. Detect ball colors
5. Read score and next balls
"""

import sys
from pathlib import Path
import numpy as np
import cv2

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from wzlz_ai.window_capture import WindowCapture, GameWindowConfig, extract_cell_colors
from wzlz_ai import BallColor


# Define ball color samples (RGB values)
# These are approximate - you should calibrate these from your game
BALL_COLOR_SAMPLES = {
    BallColor.RED: np.array([200, 50, 50]),
    BallColor.GREEN: np.array([50, 200, 50]),
    BallColor.BLUE: np.array([50, 50, 200]),
    BallColor.BROWN: np.array([150, 100, 50]),
    BallColor.MAGENTA: np.array([200, 50, 200]),
    BallColor.YELLOW: np.array([200, 200, 50]),
    BallColor.CYAN: np.array([50, 200, 200]),
    BallColor.EMPTY: np.array([180, 180, 180]),  # Gray background
}


def color_distance(color1: np.ndarray, color2: np.ndarray) -> float:
    """Calculate Euclidean distance between two colors."""
    return np.linalg.norm(color1 - color2)


def detect_ball_color(avg_color: np.ndarray, threshold: float = 80.0) -> BallColor:
    """
    Detect ball color from average cell color.
    
    Args:
        avg_color: Average RGB color of the cell
        threshold: Maximum distance to consider a match
        
    Returns:
        Detected ball color
    """
    best_match = BallColor.EMPTY
    min_distance = float('inf')
    
    for ball_color, sample_color in BALL_COLOR_SAMPLES.items():
        distance = color_distance(avg_color, sample_color)
        if distance < min_distance:
            min_distance = distance
            best_match = ball_color
    
    # If distance is too large, consider it empty
    if min_distance > threshold:
        return BallColor.EMPTY
    
    return best_match


def parse_board(board_img: np.ndarray) -> np.ndarray:
    """
    Parse board image to detect ball positions.
    
    Args:
        board_img: Board image as numpy array (RGB)
        
    Returns:
        2D array of BallColor values
    """
    # Extract average colors from each cell
    cell_colors = extract_cell_colors(board_img, rows=9, cols=9)
    
    # Detect ball color for each cell
    board = np.zeros((9, 9), dtype=np.int8)
    
    for row in range(9):
        for col in range(9):
            avg_color = cell_colors[row, col]
            ball_color = detect_ball_color(avg_color)
            board[row, col] = ball_color
    
    return board


def visualize_detection(board_img: np.ndarray, board: np.ndarray) -> np.ndarray:
    """
    Visualize ball detection on the board image.
    
    Args:
        board_img: Original board image
        board: Detected board state
        
    Returns:
        Annotated image
    """
    vis_img = board_img.copy()
    h, w = vis_img.shape[:2]
    cell_h = h / 9
    cell_w = w / 9
    
    # Draw grid
    for i in range(10):
        x = int(i * cell_w)
        y = int(i * cell_h)
        cv2.line(vis_img, (x, 0), (x, h), (255, 255, 0), 1)
        cv2.line(vis_img, (0, y), (w, y), (255, 255, 0), 1)
    
    # Draw detected balls
    for row in range(9):
        for col in range(9):
            ball_color = BallColor(board[row, col])
            if ball_color != BallColor.EMPTY:
                center_x = int((col + 0.5) * cell_w)
                center_y = int((row + 0.5) * cell_h)
                
                # Draw circle
                cv2.circle(vis_img, (center_x, center_y), 5, (0, 255, 0), -1)
                
                # Draw label
                label = ball_color.name[0]  # First letter
                cv2.putText(vis_img, label, (center_x - 5, center_y + 5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
    
    return vis_img


def read_score_ocr(score_img: np.ndarray) -> int:
    """
    Read score from score region using OCR.
    
    Args:
        score_img: Score region image
        
    Returns:
        Score value (0 if failed to read)
    """
    try:
        import pytesseract
        
        # Preprocess for OCR
        gray = cv2.cvtColor(score_img, cv2.COLOR_RGB2GRAY)
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        
        # OCR
        text = pytesseract.image_to_string(binary, config='--psm 7 digits')
        
        # Extract number
        score = int(''.join(filter(str.isdigit, text)))
        return score
    except:
        return 0


def detect_next_balls(next_balls_img: np.ndarray) -> list:
    """
    Detect next ball colors from preview region.
    
    Args:
        next_balls_img: Next balls preview image
        
    Returns:
        List of detected ball colors
    """
    # Divide into 3 regions (3 balls)
    h, w = next_balls_img.shape[:2]
    ball_width = w // 3
    
    next_balls = []
    
    for i in range(3):
        x1 = i * ball_width
        x2 = (i + 1) * ball_width
        ball_region = next_balls_img[:, x1:x2]
        
        # Get average color
        avg_color = np.mean(ball_region, axis=(0, 1))
        
        # Detect color
        ball_color = detect_ball_color(avg_color, threshold=100.0)
        next_balls.append(ball_color)
    
    return next_balls


def main():
    """Main test function."""
    print("\n" + "="*70)
    print("WZLZ IMAGE CAPTURE TEST")
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
    
    if not config.is_valid():
        print("✗ Invalid configuration!")
        return
    
    print("✓ Configuration loaded")
    print(f"  Board: {config.board_rect}")
    print(f"  Score: {config.score_rect}")
    print(f"  Next balls: {config.next_balls_rect}")
    print(f"  Cell size: {config.cell_size}")
    
    # Initialize window capture
    print("\nFinding game window...")
    capture = WindowCapture()
    
    if not capture.find_window():
        print("✗ Game window not found!")
        print("Please make sure the game (五子连珠5.2) is running.")
        return
    
    print("✓ Game window found")
    
    # Capture window
    print("\nCapturing window...")
    screenshot = capture.capture()
    
    if screenshot is None:
        print("✗ Failed to capture window!")
        return
    
    print(f"✓ Captured {screenshot.shape[1]}×{screenshot.shape[0]} screenshot")
    
    # Extract regions
    print("\nExtracting regions...")
    
    # Board
    board_img = capture.capture_region(config.board_rect)
    print(f"✓ Board: {board_img.shape[1]}×{board_img.shape[0]}")
    
    # Score
    score_img = capture.capture_region(config.score_rect)
    print(f"✓ Score: {score_img.shape[1]}×{score_img.shape[0]}")
    
    # Next balls
    next_balls_img = capture.capture_region(config.next_balls_rect)
    print(f"✓ Next balls: {next_balls_img.shape[1]}×{next_balls_img.shape[0]}")
    
    # Parse board
    print("\nDetecting balls...")
    board = parse_board(board_img)
    
    # Count balls
    ball_count = np.sum(board != BallColor.EMPTY)
    print(f"✓ Detected {ball_count} balls on the board")
    
    # Print board
    print("\nDetected board state:")
    for row in range(9):
        row_str = []
        for col in range(9):
            ball_color = BallColor(board[row, col])
            if ball_color == BallColor.EMPTY:
                row_str.append('.')
            else:
                row_str.append(ball_color.name[0])
        print(' '.join(row_str))
    
    # Detect next balls
    print("\nDetecting next balls...")
    next_balls = detect_next_balls(next_balls_img)
    print(f"✓ Next balls: {[b.name for b in next_balls]}")
    
    # Read score (if pytesseract available)
    print("\nReading score...")
    try:
        score = read_score_ocr(score_img)
        print(f"✓ Score: {score}")
    except:
        print("⚠ OCR not available (install pytesseract)")
    
    # Visualize detection
    print("\nGenerating visualization...")
    vis_img = visualize_detection(board_img, board)
    
    # Save results
    cv2.imwrite('board_capture.png', cv2.cvtColor(board_img, cv2.COLOR_RGB2BGR))
    cv2.imwrite('board_detection.png', cv2.cvtColor(vis_img, cv2.COLOR_RGB2BGR))
    cv2.imwrite('score_capture.png', cv2.cvtColor(score_img, cv2.COLOR_RGB2BGR))
    cv2.imwrite('next_balls_capture.png', cv2.cvtColor(next_balls_img, cv2.COLOR_RGB2BGR))
    
    print("\n✓ Results saved:")
    print("  - board_capture.png")
    print("  - board_detection.png")
    print("  - score_capture.png")
    print("  - next_balls_capture.png")
    
    print("\n" + "="*70)
    print("TEST COMPLETE!")
    print("="*70)
    print("\nNext steps:")
    print("1. Review the detection results in the saved images")
    print("2. If colors are wrong, calibrate BALL_COLOR_SAMPLES")
    print("3. Integrate with GameClientEnvironment")


if __name__ == "__main__":
    main()

