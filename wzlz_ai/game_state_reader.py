"""
Game state reader for extracting complete game state from window capture.

This module provides high-level functions to extract all game state information:
- Board state (9x9 grid with ball colors)
- Current score
- High score
- Next balls preview
- Move count (if available)
"""

from typing import Optional, Tuple, List
import numpy as np
import cv2

from .game_state import GameState, BallColor, GameConfig
from .window_capture import WindowCapture, GameWindowConfig, extract_cell_colors


# Ball color samples (RGB values)
# These should be calibrated for your specific game/screen
DEFAULT_BALL_COLOR_SAMPLES = {
    BallColor.RED: np.array([200, 50, 50]),
    BallColor.GREEN: np.array([50, 200, 50]),
    BallColor.BLUE: np.array([50, 50, 200]),
    BallColor.BROWN: np.array([150, 100, 50]),
    BallColor.MAGENTA: np.array([200, 50, 200]),
    BallColor.YELLOW: np.array([200, 200, 50]),
    BallColor.CYAN: np.array([50, 200, 200]),
    BallColor.EMPTY: np.array([180, 180, 180]),  # Gray background
}


class GameStateReader:
    """Reads complete game state from the game window."""
    
    def __init__(self, 
                 config_file: str = 'game_window_config.json',
                 window_title: str = "五子连珠5.2",
                 color_samples: Optional[dict] = None):
        """
        Initialize game state reader.
        
        Args:
            config_file: Path to calibration configuration file
            window_title: Title of the game window
            color_samples: Custom ball color samples (RGB values)
        """
        self.window_capture = WindowCapture(window_title)
        self.config = GameWindowConfig(config_file)
        self.color_samples = color_samples or DEFAULT_BALL_COLOR_SAMPLES
        self.color_threshold = 80.0  # Maximum color distance for matching
        
        # Try to find window on initialization
        self.window_capture.find_window()
    
    def read_game_state(self, game_config: Optional[GameConfig] = None) -> Optional[GameState]:
        """
        Read complete game state from the window.
        
        Args:
            game_config: Game configuration (optional)
            
        Returns:
            GameState object or None if failed
        """
        # Ensure window is found
        if not self.window_capture.hwnd:
            if not self.window_capture.find_window():
                return None
        
        # Read all components
        board = self.read_board()
        if board is None:
            return None
        
        current_score = self.read_current_score()
        next_balls = self.read_next_balls()
        
        # Create game state
        if game_config is None:
            game_config = GameConfig()
        
        # Create state with read values
        state = GameState(
            board=board,
            score=current_score,
            next_balls=next_balls if next_balls else []
        )
        
        return state
    
    def read_board(self) -> Optional[np.ndarray]:
        """
        Read board state from the window.
        
        Returns:
            9x9 numpy array of BallColor values, or None if failed
        """
        if not self.config.board_rect:
            return None
        
        # Capture board region
        board_img = self.window_capture.capture_region(self.config.board_rect)
        if board_img is None:
            return None
        
        # Parse board
        return self._parse_board(board_img)
    
    def read_current_score(self) -> int:
        """
        Read current score from the window.
        
        Returns:
            Current score value (0 if failed)
        """
        if not self.config.current_score_rect:
            return 0
        
        # Capture score region
        score_img = self.window_capture.capture_region(self.config.current_score_rect)
        if score_img is None:
            return 0
        
        # Read score using OCR
        return self._read_score_ocr(score_img)
    
    def read_high_score(self) -> int:
        """
        Read high score from the window.
        
        Returns:
            High score value (0 if failed)
        """
        if not self.config.high_score_rect:
            return 0
        
        # Capture score region
        score_img = self.window_capture.capture_region(self.config.high_score_rect)
        if score_img is None:
            return 0
        
        # Read score using OCR
        return self._read_score_ocr(score_img)
    
    def read_next_balls(self) -> Optional[List[BallColor]]:
        """
        Read next balls preview from the window.
        
        Returns:
            List of 3 ball colors, or None if failed
        """
        if not self.config.next_balls_rect:
            return None
        
        # Capture next balls region
        next_balls_img = self.window_capture.capture_region(self.config.next_balls_rect)
        if next_balls_img is None:
            return None
        
        # Detect next balls
        return self._detect_next_balls(next_balls_img)
    
    def _parse_board(self, board_img: np.ndarray) -> np.ndarray:
        """
        Parse board image to detect ball positions.
        
        Args:
            board_img: Board image as numpy array (RGB)
            
        Returns:
            9x9 array of BallColor values
        """
        # Extract average colors from each cell
        cell_colors = extract_cell_colors(board_img, rows=9, cols=9)
        
        # Detect ball color for each cell
        board = np.zeros((9, 9), dtype=np.int8)
        
        for row in range(9):
            for col in range(9):
                avg_color = cell_colors[row, col]
                ball_color = self._detect_ball_color(avg_color)
                board[row, col] = ball_color
        
        return board
    
    def _detect_ball_color(self, avg_color: np.ndarray) -> BallColor:
        """
        Detect ball color from average cell color.
        
        Args:
            avg_color: Average RGB color of the cell
            
        Returns:
            Detected ball color
        """
        best_match = BallColor.EMPTY
        min_distance = float('inf')
        
        for ball_color, sample_color in self.color_samples.items():
            distance = np.linalg.norm(avg_color - sample_color)
            if distance < min_distance:
                min_distance = distance
                best_match = ball_color
        
        # If distance is too large, consider it empty
        if min_distance > self.color_threshold:
            return BallColor.EMPTY
        
        return best_match
    
    def _read_score_ocr(self, score_img: np.ndarray) -> int:
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
            
            # OCR (digits only)
            text = pytesseract.image_to_string(binary, config='--psm 7 digits')
            
            # Extract number
            digits = ''.join(filter(str.isdigit, text))
            if digits:
                return int(digits)
            return 0
        except:
            return 0
    
    def _detect_next_balls(self, next_balls_img: np.ndarray) -> List[BallColor]:
        """
        Detect next ball colors from preview region.
        
        Args:
            next_balls_img: Next balls preview image
            
        Returns:
            List of detected ball colors (3 balls)
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
            
            # Detect color (use higher threshold for next balls)
            ball_color = self._detect_ball_color(avg_color)
            next_balls.append(ball_color)
        
        return next_balls
    
    def calibrate_colors(self, board_img: np.ndarray, known_positions: dict) -> dict:
        """
        Calibrate ball color samples from a known board state.
        
        Args:
            board_img: Board image
            known_positions: Dict mapping (row, col) to BallColor
            
        Returns:
            Calibrated color samples
        """
        cell_colors = extract_cell_colors(board_img, rows=9, cols=9)
        
        calibrated_samples = {}
        
        for (row, col), ball_color in known_positions.items():
            avg_color = cell_colors[row, col]
            calibrated_samples[ball_color] = avg_color
        
        return calibrated_samples
    
    def set_color_samples(self, color_samples: dict):
        """Update ball color samples."""
        self.color_samples = color_samples
    
    def set_color_threshold(self, threshold: float):
        """Update color matching threshold."""
        self.color_threshold = threshold

