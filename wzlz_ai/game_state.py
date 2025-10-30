"""
Core game state representation for the ball matching game.

This module defines the data structures to represent the current state
and possible future states of the game.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Tuple, Set
from enum import IntEnum
import numpy as np
from copy import deepcopy


class BallColor(IntEnum):
    """Enumeration of possible ball colors."""
    EMPTY = 0
    RED = 1
    GREEN = 2
    BLUE = 3
    BROWN = 4
    MAGENTA = 5
    YELLOW = 6
    CYAN = 7
    
    @classmethod
    def get_valid_colors(cls) -> List['BallColor']:
        """Get list of valid ball colors (excluding EMPTY)."""
        return [color for color in cls if color != cls.EMPTY]


@dataclass
class Position:
    """Represents a position on the game board."""
    row: int
    col: int
    
    def __hash__(self):
        return hash((self.row, self.col))
    
    def __eq__(self, other):
        if not isinstance(other, Position):
            return False
        return self.row == other.row and self.col == other.col
    
    def to_tuple(self) -> Tuple[int, int]:
        """Convert to tuple representation."""
        return (self.row, self.col)
    
    def __repr__(self):
        return f"Pos({self.row},{self.col})"


@dataclass
class Move:
    """Represents a move in the game."""
    from_pos: Position
    to_pos: Position
    
    def __repr__(self):
        return f"Move({self.from_pos} -> {self.to_pos})"


@dataclass
class GameState:
    """
    Represents the complete state of the game at a given point in time.
    
    Attributes:
        board: 2D numpy array representing the game board (rows x cols)
        next_balls: List of colors that will appear after the next move
        score: Current game score
        move_count: Number of moves made so far
        game_over: Whether the game has ended
    """
    board: np.ndarray
    next_balls: List[BallColor] = field(default_factory=list)
    score: int = 0
    move_count: int = 0
    game_over: bool = False
    
    def __post_init__(self):
        """Validate the game state after initialization."""
        if self.board.dtype != np.int8:
            self.board = self.board.astype(np.int8)
    
    @classmethod
    def create_empty(cls, rows: int = 9, cols: int = 9) -> 'GameState':
        """Create an empty game state with the specified dimensions."""
        board = np.zeros((rows, cols), dtype=np.int8)
        return cls(board=board)
    
    @property
    def rows(self) -> int:
        """Get number of rows in the board."""
        return self.board.shape[0]
    
    @property
    def cols(self) -> int:
        """Get number of columns in the board."""
        return self.board.shape[1]
    
    def get_cell(self, pos: Position) -> BallColor:
        """Get the ball color at a specific position."""
        return BallColor(self.board[pos.row, pos.col])
    
    def set_cell(self, pos: Position, color: BallColor) -> None:
        """Set the ball color at a specific position."""
        self.board[pos.row, pos.col] = int(color)
    
    def is_empty(self, pos: Position) -> bool:
        """Check if a position is empty."""
        return self.get_cell(pos) == BallColor.EMPTY
    
    def is_valid_position(self, pos: Position) -> bool:
        """Check if a position is within board bounds."""
        return 0 <= pos.row < self.rows and 0 <= pos.col < self.cols
    
    def get_empty_positions(self) -> List[Position]:
        """Get all empty positions on the board."""
        empty_positions = []
        for row in range(self.rows):
            for col in range(self.cols):
                pos = Position(row, col)
                if self.is_empty(pos):
                    empty_positions.append(pos)
        return empty_positions
    
    def get_occupied_positions(self) -> List[Position]:
        """Get all positions with balls."""
        occupied_positions = []
        for row in range(self.rows):
            for col in range(self.cols):
                pos = Position(row, col)
                if not self.is_empty(pos):
                    occupied_positions.append(pos)
        return occupied_positions
    
    def clone(self) -> 'GameState':
        """Create a deep copy of this game state."""
        return GameState(
            board=self.board.copy(),
            next_balls=self.next_balls.copy(),
            score=self.score,
            move_count=self.move_count,
            game_over=self.game_over
        )
    
    def to_feature_vector(self) -> np.ndarray:
        """
        Convert game state to a feature vector for ML models.
        
        Returns:
            Flattened representation of the board with one-hot encoding for colors.
        """
        # One-hot encode the board
        num_colors = len(BallColor)
        features = np.zeros((self.rows, self.cols, num_colors), dtype=np.float32)
        
        for row in range(self.rows):
            for col in range(self.cols):
                color = self.board[row, col]
                features[row, col, color] = 1.0
        
        return features
    
    def __repr__(self):
        """String representation of the game state."""
        lines = [f"GameState(score={self.score}, moves={self.move_count})"]
        lines.append(f"Next balls: {[c.name for c in self.next_balls]}")
        
        # Create a visual representation of the board
        color_symbols = {
            BallColor.EMPTY: '.',
            BallColor.RED: 'R',
            BallColor.GREEN: 'G',
            BallColor.BLUE: 'B',
            BallColor.BROWN: 'N',
            BallColor.MAGENTA: 'M',
            BallColor.YELLOW: 'Y',
            BallColor.CYAN: 'C',
        }
        
        for row in range(self.rows):
            row_str = ' '.join(color_symbols[BallColor(self.board[row, col])] 
                              for col in range(self.cols))
            lines.append(row_str)
        
        return '\n'.join(lines)


@dataclass
class GameConfig:
    """Configuration for the game."""
    rows: int = 9
    cols: int = 9
    colors_count: int = 7  # Number of different ball colors
    match_length: int = 5  # Number of balls needed to match
    balls_per_turn: int = 3  # Number of new balls added each turn
    initial_balls: int = 5  # Number of balls at game start
    show_next_balls: bool = True  # Whether to show preview of next balls (game mode)

    def validate(self) -> bool:
        """Validate the configuration."""
        if self.rows <= 0 or self.cols <= 0:
            return False
        if self.colors_count < 3 or self.colors_count > len(BallColor.get_valid_colors()):
            return False
        if self.match_length < 3:
            return False
        if self.balls_per_turn < 1:
            return False
        return True


@dataclass
class MoveResult:
    """
    Result of executing a move.
    
    Attributes:
        success: Whether the move was successful
        new_state: The resulting game state after the move
        balls_removed: Positions of balls that were removed due to matching
        points_earned: Points earned from this move
        new_balls_added: Positions where new balls were added
        path: The path taken by the ball (for visualization)
    """
    success: bool
    new_state: Optional[GameState] = None
    balls_removed: List[Position] = field(default_factory=list)
    points_earned: int = 0
    new_balls_added: List[Tuple[Position, BallColor]] = field(default_factory=list)
    path: List[Position] = field(default_factory=list)
    error_message: str = ""
    
    @property
    def is_valid(self) -> bool:
        """Check if the move result is valid."""
        return self.success and self.new_state is not None

