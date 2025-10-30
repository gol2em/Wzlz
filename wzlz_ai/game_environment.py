"""
Abstract game environment interface and implementations.

This module provides the interface for interacting with the game,
supporting both simulation-based training and real game client interaction.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
import numpy as np

from wzlz_ai.game_state import GameState, Move, MoveResult, Position, BallColor, GameConfig


class GameEnvironment(ABC):
    """
    Abstract base class for game environments.
    
    This interface allows switching between simulation-based training
    (fast, with controlled randomness) and real game client interaction
    (accurate, but slower).
    """
    
    def __init__(self, config: GameConfig):
        """
        Initialize the game environment.
        
        Args:
            config: Game configuration
        """
        self.config = config
        self._current_state: Optional[GameState] = None
    
    @abstractmethod
    def reset(self) -> GameState:
        """
        Reset the game to initial state.
        
        Returns:
            Initial game state
        """
        pass
    
    @abstractmethod
    def get_state(self) -> GameState:
        """
        Get the current game state.
        
        Returns:
            Current game state
        """
        pass
    
    @abstractmethod
    def execute_move(self, move: Move) -> MoveResult:
        """
        Execute a move in the game.
        
        Args:
            move: The move to execute
            
        Returns:
            Result of the move execution
        """
        pass
    
    @abstractmethod
    def get_valid_moves(self, state: Optional[GameState] = None) -> List[Move]:
        """
        Get all valid moves from the current or specified state.
        
        Args:
            state: Game state to analyze (uses current state if None)
            
        Returns:
            List of valid moves
        """
        pass
    
    @abstractmethod
    def is_path_clear(self, from_pos: Position, to_pos: Position, 
                     state: Optional[GameState] = None) -> Tuple[bool, List[Position]]:
        """
        Check if there's a clear path between two positions.
        
        Args:
            from_pos: Starting position
            to_pos: Target position
            state: Game state to check (uses current state if None)
            
        Returns:
            Tuple of (path_exists, path_positions)
        """
        pass
    
    def is_game_over(self, state: Optional[GameState] = None) -> bool:
        """
        Check if the game is over.
        
        Args:
            state: Game state to check (uses current state if None)
            
        Returns:
            True if game is over
        """
        if state is None:
            state = self.get_state()
        
        # Game is over if there are no valid moves
        return len(self.get_valid_moves(state)) == 0
    
    @property
    def current_state(self) -> GameState:
        """Get the current game state."""
        return self.get_state()


class SimulationEnvironment(GameEnvironment):
    """
    Simulation-based game environment for efficient training.
    
    This environment implements the game rules internally and uses
    controlled randomness for reproducibility and efficiency.
    """
    
    def __init__(self, config: GameConfig, seed: Optional[int] = None):
        """
        Initialize the simulation environment.
        
        Args:
            config: Game configuration
            seed: Random seed for reproducibility
        """
        super().__init__(config)
        self.rng = np.random.RandomState(seed)
        self._current_state = None
    
    def reset(self) -> GameState:
        """Reset the game to initial state."""
        # Create empty board
        state = GameState.create_empty(self.config.rows, self.config.cols)
        
        # Add initial balls
        self._add_random_balls(state, self.config.initial_balls)
        
        # Generate next balls preview
        state.next_balls = self._generate_next_balls()
        
        self._current_state = state
        return state.clone()
    
    def get_state(self) -> GameState:
        """Get the current game state."""
        if self._current_state is None:
            return self.reset()
        return self._current_state.clone()
    
    def execute_move(self, move: Move) -> MoveResult:
        """Execute a move in the simulation."""
        state = self._current_state
        
        # Validate move
        if not state.is_valid_position(move.from_pos) or not state.is_valid_position(move.to_pos):
            return MoveResult(success=False, error_message="Invalid position")
        
        if state.is_empty(move.from_pos):
            return MoveResult(success=False, error_message="No ball at source position")
        
        if not state.is_empty(move.to_pos):
            return MoveResult(success=False, error_message="Target position is occupied")
        
        # Check if path is clear
        path_exists, path = self.is_path_clear(move.from_pos, move.to_pos, state)
        if not path_exists:
            return MoveResult(success=False, error_message="No clear path to target")
        
        # Create new state
        new_state = state.clone()
        new_state.move_count += 1
        
        # Move the ball
        ball_color = new_state.get_cell(move.from_pos)
        new_state.set_cell(move.to_pos, ball_color)
        new_state.set_cell(move.from_pos, BallColor.EMPTY)

        # Check for matches at destination (earns 2 points per ball)
        balls_removed, num_removed = self._check_and_remove_matches(new_state, move.to_pos)
        points_earned = num_removed * 2  # 2 points per ball

        # Add new balls if no match was made
        new_balls_added = []
        if not balls_removed:
            new_balls_added = self._add_next_balls(new_state)
            # Check for matches from newly added balls (no points earned)
            auto_removed, _ = self._check_all_matches(new_state)
            balls_removed.extend(auto_removed)
            # Note: auto_removed balls don't earn points

        # Update score (only from player's move matches, not auto-matches)
        new_state.score += points_earned
        
        # Generate next balls
        new_state.next_balls = self._generate_next_balls()
        
        # Check if game is over
        new_state.game_over = self.is_game_over(new_state)
        
        self._current_state = new_state
        
        return MoveResult(
            success=True,
            new_state=new_state.clone(),
            balls_removed=balls_removed,
            points_earned=points_earned,
            new_balls_added=new_balls_added,
            path=path
        )
    
    def get_valid_moves(self, state: Optional[GameState] = None) -> List[Move]:
        """Get all valid moves from the current state."""
        if state is None:
            state = self._current_state
        
        valid_moves = []
        occupied = state.get_occupied_positions()
        empty = state.get_empty_positions()
        
        # For each ball, find all reachable empty positions
        for from_pos in occupied:
            for to_pos in empty:
                path_exists, _ = self.is_path_clear(from_pos, to_pos, state)
                if path_exists:
                    valid_moves.append(Move(from_pos, to_pos))
        
        return valid_moves
    
    def is_path_clear(self, from_pos: Position, to_pos: Position,
                     state: Optional[GameState] = None) -> Tuple[bool, List[Position]]:
        """Check if there's a clear path using BFS."""
        if state is None:
            state = self._current_state
        
        # BFS to find path
        from collections import deque
        
        queue = deque([(from_pos, [from_pos])])
        visited = {from_pos}
        
        while queue:
            current, path = queue.popleft()
            
            if current == to_pos:
                return True, path
            
            # Check all 4 directions
            for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                next_pos = Position(current.row + dr, current.col + dc)
                
                if (state.is_valid_position(next_pos) and 
                    next_pos not in visited and
                    (state.is_empty(next_pos) or next_pos == to_pos)):
                    
                    visited.add(next_pos)
                    queue.append((next_pos, path + [next_pos]))
        
        return False, []
    
    def _generate_next_balls(self) -> List[BallColor]:
        """Generate the next set of balls."""
        valid_colors = BallColor.get_valid_colors()[:self.config.colors_count]
        return [BallColor(self.rng.choice(valid_colors)) 
                for _ in range(self.config.balls_per_turn)]
    
    def _add_random_balls(self, state: GameState, count: int) -> List[Tuple[Position, BallColor]]:
        """Add random balls to empty positions."""
        empty_positions = state.get_empty_positions()
        
        if len(empty_positions) < count:
            count = len(empty_positions)
        
        if count == 0:
            return []
        
        selected_positions = self.rng.choice(len(empty_positions), count, replace=False)
        valid_colors = BallColor.get_valid_colors()[:self.config.colors_count]
        
        added_balls = []
        for idx in selected_positions:
            pos = empty_positions[idx]
            color = BallColor(self.rng.choice(valid_colors))
            state.set_cell(pos, color)
            added_balls.append((pos, color))
        
        return added_balls
    
    def _add_next_balls(self, state: GameState) -> List[Tuple[Position, BallColor]]:
        """Add the previewed next balls to the board."""
        empty_positions = state.get_empty_positions()
        
        if len(empty_positions) < len(state.next_balls):
            # Not enough space, add what we can
            count = len(empty_positions)
        else:
            count = len(state.next_balls)
        
        if count == 0:
            return []
        
        selected_positions = self.rng.choice(len(empty_positions), count, replace=False)
        
        added_balls = []
        for i, idx in enumerate(selected_positions):
            pos = empty_positions[idx]
            color = state.next_balls[i]
            state.set_cell(pos, color)
            added_balls.append((pos, color))
        
        return added_balls
    
    def _check_and_remove_matches(self, state: GameState, pos: Position) -> Tuple[List[Position], int]:
        """
        Check for matches around a position and remove them.

        Checks all 4 directions (horizontal, vertical, and 2 diagonals) for lines
        of 5 or more balls of the same color. Returns all matched positions.

        Args:
            state: Current game state
            pos: Position to check around (can be None to check entire board)

        Returns:
            Tuple of (list of positions to remove, number of balls removed)
        """
        if pos is None:
            # Check entire board for matches
            return self._check_all_matches(state)

        color = state.get_cell(pos)
        if color == BallColor.EMPTY:
            return [], 0

        all_matches = set()

        # Define 4 directions: horizontal, vertical, diagonal-right, diagonal-left
        directions = [
            (0, 1),   # Horizontal
            (1, 0),   # Vertical
            (1, 1),   # Diagonal (top-left to bottom-right)
            (1, -1),  # Diagonal (top-right to bottom-left)
        ]

        for dr, dc in directions:
            line = self._get_line_in_direction(state, pos, dr, dc, color)
            if len(line) >= self.config.match_length:
                all_matches.update(line)

        # Remove matched balls
        if all_matches:
            for match_pos in all_matches:
                state.set_cell(match_pos, BallColor.EMPTY)

        return list(all_matches), len(all_matches)

    def _get_line_in_direction(self, state: GameState, pos: Position,
                               dr: int, dc: int, color: BallColor) -> List[Position]:
        """
        Get all consecutive balls of the same color in a given direction.

        Args:
            state: Current game state
            pos: Starting position
            dr: Row direction (-1, 0, or 1)
            dc: Column direction (-1, 0, or 1)
            color: Color to match

        Returns:
            List of positions forming a line in both directions
        """
        line = [pos]

        # Check in positive direction
        r, c = pos.row + dr, pos.col + dc
        while (0 <= r < state.rows and 0 <= c < state.cols and
               state.board[r, c] == color):
            line.append(Position(r, c))
            r += dr
            c += dc

        # Check in negative direction
        r, c = pos.row - dr, pos.col - dc
        while (0 <= r < state.rows and 0 <= c < state.cols and
               state.board[r, c] == color):
            line.append(Position(r, c))
            r -= dr
            c -= dc

        return line

    def _check_all_matches(self, state: GameState) -> Tuple[List[Position], int]:
        """
        Check the entire board for matches.
        Used after adding random balls to check for automatic eliminations.

        Returns:
            Tuple of (list of positions to remove, number of balls removed)
        """
        all_matches = set()

        # Check each occupied position
        for row in range(state.rows):
            for col in range(state.cols):
                pos = Position(row, col)
                color = state.get_cell(pos)

                if color == BallColor.EMPTY:
                    continue

                # Check all 4 directions from this position
                directions = [
                    (0, 1),   # Horizontal
                    (1, 0),   # Vertical
                    (1, 1),   # Diagonal (top-left to bottom-right)
                    (1, -1),  # Diagonal (top-right to bottom-left)
                ]

                for dr, dc in directions:
                    line = self._get_line_in_direction(state, pos, dr, dc, color)
                    if len(line) >= self.config.match_length:
                        all_matches.update(line)

        # Remove matched balls
        if all_matches:
            for match_pos in all_matches:
                state.set_cell(match_pos, BallColor.EMPTY)

        return list(all_matches), len(all_matches)

