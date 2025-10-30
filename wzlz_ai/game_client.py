"""
Game client interface for interacting with the actual game window.

This module provides functionality to read the game state from the game window
and execute moves by simulating mouse clicks and keyboard input.
"""

from typing import List, Optional, Tuple
import numpy as np
from PIL import ImageGrab
import pyautogui
import time

from wzlz_ai.game_state import GameState, Move, MoveResult, Position, BallColor, GameConfig
from wzlz_ai.game_environment import GameEnvironment


class GameClientEnvironment(GameEnvironment):
    """
    Game environment that interacts with the actual game client.
    
    This environment reads the game state from the game window using
    screen capture and OCR, and executes moves by simulating mouse clicks.
    """
    
    def __init__(self, config: GameConfig, window_title: str = "五子连珠5.2"):
        """
        Initialize the game client environment.
        
        Args:
            config: Game configuration
            window_title: Title of the game window
        """
        super().__init__(config)
        self.window_title = window_title
        self.window_rect: Optional[Tuple[int, int, int, int]] = None
        self.board_rect: Optional[Tuple[int, int, int, int]] = None
        self.cell_size: Optional[int] = None
        self._current_state = None
        
        # Calibration data
        self.is_calibrated = False
    
    def calibrate(self, board_rect: Tuple[int, int, int, int], 
                  cell_size: int) -> bool:
        """
        Calibrate the game client interface.
        
        Args:
            board_rect: Rectangle defining the board area (x, y, width, height)
            cell_size: Size of each cell in pixels
            
        Returns:
            True if calibration successful
        """
        self.board_rect = board_rect
        self.cell_size = cell_size
        self.is_calibrated = True
        return True
    
    def auto_calibrate(self) -> bool:
        """
        Attempt to automatically calibrate by detecting the game window.
        
        Returns:
            True if calibration successful
        """
        # TODO: Implement automatic window detection and calibration
        # This would involve:
        # 1. Finding the game window by title
        # 2. Detecting the board grid using image processing
        # 3. Calculating cell size and positions
        raise NotImplementedError("Auto-calibration not yet implemented")
    
    def reset(self) -> GameState:
        """
        Reset the game by clicking the new game button.
        
        Note: This requires knowing the position of the new game button.
        """
        if not self.is_calibrated:
            raise RuntimeError("Game client not calibrated. Call calibrate() first.")
        
        # TODO: Implement new game button click
        # For now, just read the current state
        self._current_state = self._read_game_state()
        return self._current_state.clone()
    
    def get_state(self) -> GameState:
        """Read and return the current game state from the game window."""
        if not self.is_calibrated:
            raise RuntimeError("Game client not calibrated. Call calibrate() first.")
        
        self._current_state = self._read_game_state()
        return self._current_state.clone()
    
    def execute_move(self, move: Move) -> MoveResult:
        """
        Execute a move by simulating mouse clicks.
        
        Args:
            move: The move to execute
            
        Returns:
            Result of the move execution
        """
        if not self.is_calibrated:
            raise RuntimeError("Game client not calibrated. Call calibrate() first.")
        
        # Get state before move
        state_before = self._read_game_state()
        
        # Click on source position
        from_x, from_y = self._position_to_screen_coords(move.from_pos)
        pyautogui.click(from_x, from_y)
        time.sleep(0.1)  # Small delay for game to register click
        
        # Click on target position
        to_x, to_y = self._position_to_screen_coords(move.to_pos)
        pyautogui.click(to_x, to_y)
        
        # Wait for animation to complete
        time.sleep(0.5)  # Adjust based on game animation speed
        
        # Read new state
        state_after = self._read_game_state()
        
        # Determine if move was successful by comparing states
        success = not np.array_equal(state_before.board, state_after.board)
        
        if success:
            # Calculate what changed
            balls_removed = self._find_removed_balls(state_before, state_after)
            new_balls_added = self._find_added_balls(state_before, state_after)
            points_earned = state_after.score - state_before.score
            
            self._current_state = state_after
            
            return MoveResult(
                success=True,
                new_state=state_after.clone(),
                balls_removed=balls_removed,
                points_earned=points_earned,
                new_balls_added=new_balls_added
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
    
    def _read_game_state(self) -> GameState:
        """
        Read the current game state from the game window.
        
        Returns:
            Current game state
        """
        # Capture the game board area
        screenshot = self._capture_board()
        
        # Parse the board to detect balls
        board = self._parse_board(screenshot)
        
        # Read score and next balls
        score = self._read_score()
        next_balls = self._read_next_balls()
        
        state = GameState(
            board=board,
            next_balls=next_balls,
            score=score
        )
        
        return state
    
    def _capture_board(self) -> np.ndarray:
        """Capture screenshot of the game board."""
        if self.board_rect is None:
            raise RuntimeError("Board rectangle not set")
        
        x, y, w, h = self.board_rect
        screenshot = ImageGrab.grab(bbox=(x, y, x + w, y + h))
        return np.array(screenshot)
    
    def _parse_board(self, screenshot: np.ndarray) -> np.ndarray:
        """
        Parse the screenshot to detect ball positions and colors.
        
        Args:
            screenshot: Screenshot of the game board
            
        Returns:
            2D array representing the board state
        """
        board = np.zeros((self.config.rows, self.config.cols), dtype=np.int8)
        
        # TODO: Implement actual image recognition
        # This would involve:
        # 1. Dividing the screenshot into cells
        # 2. For each cell, detecting if there's a ball
        # 3. If there's a ball, determining its color
        # 4. Mapping colors to BallColor enum values
        
        # For now, return empty board as placeholder
        return board
    
    def _read_score(self) -> int:
        """Read the current score from the game window."""
        # TODO: Implement OCR to read score
        # This would involve:
        # 1. Capturing the score area
        # 2. Using OCR (e.g., pytesseract) to read the number
        return 0
    
    def _read_next_balls(self) -> List[BallColor]:
        """Read the preview of next balls."""
        # TODO: Implement reading next balls preview
        # This would involve:
        # 1. Capturing the next balls preview area
        # 2. Detecting the colors of the preview balls
        return []
    
    def _position_to_screen_coords(self, pos: Position) -> Tuple[int, int]:
        """
        Convert board position to screen coordinates.
        
        Args:
            pos: Board position
            
        Returns:
            Screen coordinates (x, y)
        """
        if self.board_rect is None or self.cell_size is None:
            raise RuntimeError("Board not calibrated")
        
        x = self.board_rect[0] + pos.col * self.cell_size + self.cell_size // 2
        y = self.board_rect[1] + pos.row * self.cell_size + self.cell_size // 2
        
        return x, y
    
    def _find_removed_balls(self, state_before: GameState, 
                           state_after: GameState) -> List[Position]:
        """Find positions where balls were removed."""
        removed = []
        for row in range(self.config.rows):
            for col in range(self.config.cols):
                pos = Position(row, col)
                if (not state_before.is_empty(pos) and 
                    state_after.is_empty(pos)):
                    removed.append(pos)
        return removed
    
    def _find_added_balls(self, state_before: GameState,
                         state_after: GameState) -> List[Tuple[Position, BallColor]]:
        """Find positions where balls were added."""
        added = []
        for row in range(self.config.rows):
            for col in range(self.config.cols):
                pos = Position(row, col)
                if (state_before.is_empty(pos) and 
                    not state_after.is_empty(pos)):
                    color = state_after.get_cell(pos)
                    added.append((pos, color))
        return added

