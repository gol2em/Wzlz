"""
Game client interface for interacting with the actual game window.

This module provides functionality to read the game state from the game window
and execute moves by simulating mouse clicks and keyboard input.
"""

from typing import List, Optional, Tuple, Dict
import numpy as np
import cv2
import time
import json
from pathlib import Path
import sys

# Add root directory to path for unified_capture
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import win32gui
    import win32api
    import win32con
    from unified_capture import capture_game_window, get_window_rect
except ImportError:
    print("Windows dependencies not installed!")
    print("Install with: uv pip install pywin32")
    raise

from wzlz_ai.game_state import GameState, Move, MoveResult, Position, BallColor, GameConfig
from wzlz_ai.game_environment import GameEnvironment


# Ball color samples (BGR format for OpenCV)
BALL_COLOR_SAMPLES = {
    BallColor.RED: np.array([50, 50, 200]),
    BallColor.GREEN: np.array([50, 200, 50]),
    BallColor.BLUE: np.array([200, 50, 50]),
    BallColor.BROWN: np.array([50, 100, 150]),
    BallColor.MAGENTA: np.array([200, 50, 200]),
    BallColor.YELLOW: np.array([50, 200, 200]),
    BallColor.CYAN: np.array([200, 200, 50]),
    BallColor.EMPTY: np.array([180, 180, 180]),
}


class GameClientEnvironment(GameEnvironment):
    """
    Game environment that interacts with the actual game client.

    This environment reads the game state from the game window using
    screen capture and color detection, and executes moves by simulating mouse clicks.
    """

    def __init__(self, config: GameConfig, window_title: str = "五子连珠5.2",
                 config_file: str = "game_window_config.json"):
        """
        Initialize the game client environment.

        Args:
            config: Game configuration
            window_title: Title of the game window
            config_file: Path to calibration config file
        """
        super().__init__(config)
        self.window_title = window_title
        self.config_file = config_file
        self.window_config: Optional[Dict] = None
        self._current_state = None

        # Load calibration
        self.is_calibrated = self._load_calibration()
    
    def _load_calibration(self) -> bool:
        """Load calibration from config file."""
        config_path = Path(self.config_file)
        if not config_path.exists():
            print(f"Warning: Calibration file {self.config_file} not found!")
            print("Run examples/manual_calibrate_all.py to create it.")
            return False

        try:
            with open(config_path, 'r') as f:
                self.window_config = json.load(f)
            return True
        except Exception as e:
            print(f"Error loading calibration: {e}")
            return False

    def _color_distance(self, color1: np.ndarray, color2: np.ndarray) -> float:
        """Calculate Euclidean distance between two colors."""
        return np.linalg.norm(color1.astype(float) - color2.astype(float))

    def _detect_ball_color(self, avg_color: np.ndarray) -> BallColor:
        """Detect ball color from average cell color."""
        best_match = BallColor.EMPTY
        min_distance = float('inf')

        for color_enum, sample_color in BALL_COLOR_SAMPLES.items():
            distance = self._color_distance(avg_color, sample_color)
            if distance < min_distance:
                min_distance = distance
                best_match = color_enum

        return best_match

    def _read_board_from_image(self, board_img: np.ndarray) -> np.ndarray:
        """Read board state from board image."""
        h, w = board_img.shape[:2]
        cell_w = w / 9
        cell_h = h / 9

        board = np.full((9, 9), BallColor.EMPTY, dtype=object)

        for row in range(9):
            for col in range(9):
                # Sample center 50% of cell
                x1 = int(col * cell_w + cell_w * 0.25)
                y1 = int(row * cell_h + cell_h * 0.25)
                x2 = int((col + 1) * cell_w - cell_w * 0.25)
                y2 = int((row + 1) * cell_h - cell_h * 0.25)

                cell_region = board_img[y1:y2, x1:x2]
                if cell_region.size > 0:
                    avg_color = np.mean(cell_region, axis=(0, 1))
                    board[row, col] = self._detect_ball_color(avg_color)

        return board
    
    def _capture_board_image(self) -> Optional[np.ndarray]:
        """Capture the board region from the game window."""
        img = capture_game_window(self.window_title, bring_to_front=False)
        if img is None:
            return None

        x, y, w, h = self.window_config['board_rect']
        img_np = np.array(img)
        board_img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
        board_img_bgr = board_img_bgr[y:y+h, x:x+w]

        return board_img_bgr

    def _read_game_state(self) -> GameState:
        """Read the current game state from the window."""
        board_img = self._capture_board_image()
        if board_img is None:
            raise RuntimeError(f"Failed to capture window '{self.window_title}'")

        board = self._read_board_from_image(board_img)

        # Convert BallColor enums to int8 for GameState
        board_int = np.zeros((9, 9), dtype=np.int8)
        for row in range(9):
            for col in range(9):
                board_int[row, col] = board[row, col].value

        # Read score and next_balls using calibrated regions
        score = self._read_current_score()
        next_balls = self._read_next_balls()

        # Create game state
        state = GameState(
            board=board_int,
            score=score,
            next_balls=next_balls if next_balls else []
        )

        return state

    def _read_current_score(self) -> int:
        """Read current score from the window using calibrated region."""
        if 'current_score_rect' not in self.window_config:
            return 0

        try:
            # Capture full window
            img = capture_game_window(self.window_title, bring_to_front=False)
            if img is None:
                return 0

            # Extract score region (img is BGR from unified_capture)
            x, y, w, h = self.window_config['current_score_rect']
            score_img = img[y:y+h, x:x+w]

            # Use OCR to read score
            return self._read_score_ocr(score_img)
        except Exception as e:
            return 0

    def _read_next_balls(self) -> List[int]:
        """Read next balls preview from the window using calibrated region."""
        if 'next_balls_rect' not in self.window_config:
            return []

        try:
            # Capture full window
            img = capture_game_window(self.window_title, bring_to_front=False)
            if img is None:
                return []

            # Extract next balls region (img is BGR from unified_capture)
            x, y, w, h = self.window_config['next_balls_rect']
            next_balls_img = img[y:y+h, x:x+w]

            # Detect next balls
            next_balls = self._detect_next_balls(next_balls_img)

            # Convert BallColor enums to int values
            return [ball.value for ball in next_balls]
        except Exception as e:
            return []

    def _read_score_ocr(self, score_img: np.ndarray) -> int:
        """Read score from score region using simple pattern matching."""
        # For now, return 0 as placeholder
        # TODO: Implement OCR or template matching
        return 0

    def _detect_next_balls(self, next_balls_img: np.ndarray) -> List[BallColor]:
        """Detect next ball colors from preview region."""
        # Divide into 3 regions (3 balls)
        h, w = next_balls_img.shape[:2]
        ball_width = w // 3

        next_balls = []

        for i in range(3):
            x1 = i * ball_width
            x2 = (i + 1) * ball_width
            ball_region = next_balls_img[:, x1:x2]

            # Get average color (BGR)
            avg_color = np.mean(ball_region, axis=(0, 1))

            # Detect color
            ball_color = self._detect_ball_color(avg_color)
            next_balls.append(ball_color)

        return next_balls

    def _bring_window_to_front(self):
        """Bring the game window to front and ensure it's focused."""
        hwnd = win32gui.FindWindow(None, self.window_title)
        if hwnd:
            try:
                if win32gui.IsIconic(hwnd):
                    win32gui.ShowWindow(hwnd, 9)  # SW_RESTORE
                    time.sleep(0.2)

                # Try to set foreground window
                # This may fail due to Windows restrictions, but that's okay
                try:
                    win32gui.SetForegroundWindow(hwnd)
                except:
                    # If SetForegroundWindow fails, try alternative method
                    win32gui.ShowWindow(hwnd, 5)  # SW_SHOW
                    win32gui.SetActiveWindow(hwnd)

                time.sleep(0.3)
                return True
            except Exception as e:
                # Even if we can't bring to front, continue
                # The user might have the window focused already
                time.sleep(0.3)
                return True
        return False

    def _has_popup(self) -> bool:
        """
        Check if there's a popup window (game over or high score).

        Popups in this game are typically child windows or dialogs.
        We can detect them by checking if the main window has focus but
        is not responding to normal input.

        Returns:
            True if a popup is detected
        """
        # Try to find common popup window titles
        # Game over popup might have title like "游戏结束" or similar
        # High score popup might have title like "排行榜" or similar

        # For now, we'll use a simple heuristic:
        # If we can't capture the board properly, there might be a popup
        # This is a placeholder - you may need to adjust based on actual popup titles

        # Alternative: Just always try to dismiss popups after moves
        # since pressing Enter when there's no popup does nothing
        return True  # Conservative approach: always try

    def _handle_popups(self):
        """
        Handle game over and high score popups by pressing Enter twice.

        Pressing Enter does nothing during normal gameplay, so it's safe to
        always press it. If there's a popup, it gets dismissed.
        """
        VK_RETURN = 0x0D

        # First Enter - dismiss game over popup (if present)
        win32api.keybd_event(VK_RETURN, 0, 0, 0)
        time.sleep(0.05)
        win32api.keybd_event(VK_RETURN, 0, 2, 0)  # KEYEVENTF_KEYUP
        time.sleep(0.8)

        # Second Enter - dismiss high score popup (if present)
        win32api.keybd_event(VK_RETURN, 0, 0, 0)
        time.sleep(0.05)
        win32api.keybd_event(VK_RETURN, 0, 2, 0)  # KEYEVENTF_KEYUP
        time.sleep(0.8)

    def reset(self) -> GameState:
        """
        Reset the game.

        If there are popups (game over, high score), dismiss them by pressing Enter.
        The popups already have focus, so we just press Enter directly.
        After popups are dismissed, the game auto-restarts.

        If there are no popups, press F4 to manually restart.

        The popup sequence is:
        1. Game over popup appears (has focus automatically)
        2. Press Enter → dismisses game over popup
        3. High score popup appears (has focus automatically)
        4. Press Enter → dismisses high score popup
        5. Game auto-restarts with 5 balls

        Returns:
            Initial game state after reset
        """
        if not self.is_calibrated:
            raise RuntimeError("Game client not calibrated. Run examples/manual_calibrate_all.py first.")

        # Try to handle popups first (in case game is already over)
        # DON'T bring window to front - popups already have focus
        # Just press Enter twice to dismiss both popups
        self._handle_popups()

        # Wait for game to auto-restart after popups
        time.sleep(1.0)

        # Read state to check if game restarted
        try:
            state = self._read_game_state()
            ball_count = sum(1 for row in range(9) for col in range(9) if state.board[row, col] != 0)

            # If we have 5 balls, game restarted successfully
            if ball_count == 5:
                self._current_state = state
                return self._current_state.clone()
        except:
            pass

        # If popups didn't restart the game, use F4
        # Now we need to focus on the game window
        self._bring_window_to_front()

        # Press F4 using keyboard events
        VK_F4 = 0x73
        win32api.keybd_event(VK_F4, 0, 0, 0)
        time.sleep(0.05)
        win32api.keybd_event(VK_F4, 0, 2, 0)  # KEYEVENTF_KEYUP

        # Wait for game to reset
        time.sleep(1.0)

        # Read the new initial state
        self._current_state = self._read_game_state()
        return self._current_state.clone()

    def get_state(self) -> GameState:
        """Read and return the current game state from the game window."""
        if not self.is_calibrated:
            raise RuntimeError("Game client not calibrated. Run examples/manual_calibrate_all.py first.")

        self._current_state = self._read_game_state()
        return self._current_state.clone()
    
    def _cell_to_screen_coords(self, row: int, col: int) -> Tuple[int, int]:
        """Convert board cell coordinates to screen coordinates."""
        board_rect = self.window_config['board_rect']
        window_rect = get_window_rect(self.window_title)

        if not window_rect:
            raise RuntimeError(f"Window '{self.window_title}' not found")

        bx, by, bw, bh = board_rect
        window_left, window_top, window_right, window_bottom = window_rect

        cell_w = bw / 9
        cell_h = bh / 9

        # Center of the cell
        cell_center_x = bx + (col + 0.5) * cell_w
        cell_center_y = by + (row + 0.5) * cell_h

        # Apply correction (from test_live_move.py)
        correction_x = cell_w * 0.33
        correction_y = cell_h * 1.5

        screen_x = window_left + cell_center_x + correction_x
        screen_y = window_top + cell_center_y + correction_y

        return int(screen_x), int(screen_y)

    def _click_at(self, x: int, y: int):
        """Click at screen coordinates."""
        win32api.SetCursorPos((x, y))
        time.sleep(0.1)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
        time.sleep(0.05)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
        time.sleep(0.1)

    def _is_cell_selected(self, row: int, col: int, debug: bool = False) -> bool:
        """
        Check if a cell has a selected ball (bouncing).

        A selected ball bounces, which causes the cell image to change between frames.
        We capture the cell rapidly several times and check if any images differ.
        If the cell is not selected, all captures should be exactly the same.

        Args:
            row: Row index (0-8)
            col: Column index (0-8)
            debug: If True, print debug information

        Returns:
            True if cell has a selected ball (bouncing), False otherwise
        """
        # Capture cell image rapidly multiple times
        images = []
        for i in range(5):
            img = self._get_cell_image(row, col)
            if img is None:
                return False
            images.append(img)
            time.sleep(0.02)  # Very short delay (20ms) for rapid capture

        # Compare all pairs of images
        max_diff = 0
        for i in range(len(images)):
            for j in range(i + 1, len(images)):
                # Calculate pixel-wise difference
                diff = np.abs(images[i].astype(float) - images[j].astype(float))
                mean_diff = np.mean(diff)
                max_diff = max(max_diff, mean_diff)

                if debug:
                    print(f"  Image {i} vs {j}: mean diff = {mean_diff:.2f}")

        if debug:
            print(f"  Max difference: {max_diff:.2f}")

        # If max difference is above threshold, the cell is changing (ball is bouncing)
        # If not selected, all images should be identical (diff = 0)
        # Threshold should be low since we're looking for any change
        return max_diff > 2.0  # Adjust if needed

    def _get_cell_image(self, row: int, col: int) -> Optional[np.ndarray]:
        """
        Get the image of a cell.

        Args:
            row: Row index (0-8)
            col: Column index (0-8)

        Returns:
            Cell image (BGR), or None if failed
        """
        # Capture the board
        img = self._capture_board_image()
        if img is None:
            return None

        h, w = img.shape[:2]
        cell_h = h / 9
        cell_w = w / 9

        # Get cell region
        y1 = int(row * cell_h)
        y2 = int((row + 1) * cell_h)
        x1 = int(col * cell_w)
        x2 = int((col + 1) * cell_w)

        cell_img = img[y1:y2, x1:x2]

        return cell_img

    def _get_cell_color(self, row: int, col: int) -> np.ndarray:
        """
        Get the average color of a cell.

        Args:
            row: Row index (0-8)
            col: Column index (0-8)

        Returns:
            Average BGR color of the cell
        """
        cell_img = self._get_cell_image(row, col)
        if cell_img is None:
            return np.array([0, 0, 0])

        # Get average color
        avg_color = np.mean(cell_img, axis=(0, 1))

        return avg_color

    def execute_move(self, move: Move) -> MoveResult:
        """
        Execute a move by simulating mouse clicks.

        Simple logic:
        1. Click on source ball (always selects it, regardless of previous state)
        2. Click on destination

        After each move, presses Enter twice to dismiss any popups that might appear.
        If the ball count drops to 5, the game has reset (popup was dismissed).

        Args:
            move: The move to execute

        Returns:
            Result of the move execution, or None if game reset occurred
        """
        if not self.is_calibrated:
            raise RuntimeError("Game client not calibrated. Run examples/manual_calibrate_all.py first.")

        # Get state before move
        state_before = self._read_game_state()
        ball_count_before = sum(1 for row in range(9) for col in range(9) if state_before.board[row, col] != 0)

        # Get screen coordinates
        from_x, from_y = self._cell_to_screen_coords(move.from_pos.row, move.from_pos.col)
        to_x, to_y = self._cell_to_screen_coords(move.to_pos.row, move.to_pos.col)

        # Click on source ball to select it
        self._click_at(from_x, from_y)
        time.sleep(0.3)  # Wait for bounce animation

        # Click on destination to move
        self._click_at(to_x, to_y)

        # Wait for move animation + new balls
        time.sleep(1.8)

        # Press Enter twice to dismiss any popups
        # If there's no popup, pressing Enter does nothing during gameplay
        # If there's a popup, this dismisses it
        VK_RETURN = 0x0D

        # First Enter - dismiss game over popup (if present)
        win32api.keybd_event(VK_RETURN, 0, 0, 0)
        time.sleep(0.05)
        win32api.keybd_event(VK_RETURN, 0, 2, 0)  # KEYEVENTF_KEYUP
        time.sleep(0.8)

        # Second Enter - dismiss high score popup (if present)
        win32api.keybd_event(VK_RETURN, 0, 0, 0)
        time.sleep(0.05)
        win32api.keybd_event(VK_RETURN, 0, 2, 0)  # KEYEVENTF_KEYUP
        time.sleep(0.8)

        # Read new state
        state_after = self._read_game_state()
        ball_count_after = sum(1 for row in range(9) for col in range(9) if state_after.board[row, col] != 0)

        # Check if game reset (ball count dropped to 5)
        if ball_count_before > 50 and ball_count_after == 5:
            # Game over popup appeared and was dismissed, game restarted
            self._current_state = state_after
            return None  # Signal that game reset occurred

        # Determine if move was successful by comparing states
        success = not np.array_equal(state_before.board, state_after.board)

        if success:
            self._current_state = state_after

            return MoveResult(
                success=True,
                new_state=state_after.clone(),
                balls_removed=[],  # TODO: Calculate
                points_earned=0,  # TODO: Read from screen
                new_balls_added=[]  # TODO: Calculate
            )
        else:
            return MoveResult(
                success=False,
                error_message="Move was not executed by the game"
            )
    
    def get_valid_moves(self, state: Optional[GameState] = None) -> List[Move]:
        """
        Get valid moves by analyzing the current state.
        
        Note: This uses the same pathfinding logic as simulation,
        but operates on the state read from the game client.
        """
        if state is None:
            state = self.get_state()
        
        # Use the same logic as simulation environment
        from wzlz_ai.game_environment import SimulationEnvironment
        sim_env = SimulationEnvironment(self.config)
        sim_env._current_state = state
        return sim_env.get_valid_moves(state)
    
    def is_path_clear(self, from_pos: Position, to_pos: Position,
                     state: Optional[GameState] = None) -> Tuple[bool, List[Position]]:
        """Check if path is clear using simulation logic."""
        if state is None:
            state = self.get_state()

        from wzlz_ai.game_environment import SimulationEnvironment
        sim_env = SimulationEnvironment(self.config)
        sim_env._current_state = state
        return sim_env.is_path_clear(from_pos, to_pos, state)

