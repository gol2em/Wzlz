"""
Template for implementing game matching logic.

Copy this code into game_environment.py, replacing the placeholder
_check_and_remove_matches() method in SimulationEnvironment class.
"""

from typing import List, Tuple
from wzlz_ai import GameState, Position, BallColor


def _check_and_remove_matches(self, state: GameState, pos: Position) -> Tuple[List[Position], int]:
    """
    Check for matches around a position and remove them.
    
    This function checks all four directions (horizontal, vertical, and two diagonals)
    for sequences of matching balls. If a sequence of match_length or more balls
    of the same color is found, those balls are removed and points are awarded.
    
    Args:
        state: Current game state
        pos: Position to check around
        
    Returns:
        Tuple of (removed_positions, points_earned)
    """
    color = state.get_cell(pos)
    
    # Can't match empty cells
    if color == BallColor.EMPTY:
        return [], 0
    
    all_removed = set()
    total_points = 0
    
    # Check all four directions
    directions = [
        [(0, 1), (0, -1)],   # Horizontal
        [(1, 0), (-1, 0)],   # Vertical
        [(1, 1), (-1, -1)],  # Diagonal \
        [(1, -1), (-1, 1)]   # Diagonal /
    ]
    
    for direction_pair in directions:
        # Find all matching balls in this line
        matching_positions = [pos]  # Start with the center position
        
        # Check both directions
        for dr, dc in direction_pair:
            current_row, current_col = pos.row, pos.col
            
            while True:
                current_row += dr
                current_col += dc
                current_pos = Position(current_row, current_col)
                
                # Stop if out of bounds
                if not state.is_valid_position(current_pos):
                    break
                
                # Stop if different color or empty
                if state.get_cell(current_pos) != color:
                    break
                
                # Add to matching positions
                matching_positions.append(current_pos)
        
        # If we have enough matches, remove them
        if len(matching_positions) >= self.config.match_length:
            all_removed.update(matching_positions)
            
            # Calculate points (you can adjust this formula)
            # Example: 5 balls = 10 points, 6 balls = 12 points, etc.
            points = len(matching_positions) * 2
            total_points += points
    
    # Remove the balls from the state
    removed_list = list(all_removed)
    for remove_pos in removed_list:
        state.set_cell(remove_pos, BallColor.EMPTY)
    
    return removed_list, total_points


# Example test code
if __name__ == "__main__":
    """Test the matching logic."""
    from wzlz_ai import GameState, GameConfig, SimulationEnvironment
    
    print("Testing matching logic...")
    
    # Test 1: Horizontal match
    print("\nTest 1: Horizontal match (5 red balls in a row)")
    state = GameState.create_empty(9, 9)
    for i in range(5):
        state.set_cell(Position(0, i), BallColor.RED)
    
    print("Before:")
    print(state)
    
    config = GameConfig()
    env = SimulationEnvironment(config)
    env._current_state = state
    
    # Check for matches at the middle position
    removed, points = env._check_and_remove_matches(state, Position(0, 2))
    
    print(f"\nRemoved {len(removed)} balls")
    print(f"Points: {points}")
    print("\nAfter:")
    print(state)
    
    assert len(removed) == 5, f"Expected 5 removed, got {len(removed)}"
    assert points > 0, "Expected points > 0"
    print("✓ Test 1 passed")
    
    # Test 2: Vertical match
    print("\n" + "="*60)
    print("Test 2: Vertical match (5 blue balls in a column)")
    state = GameState.create_empty(9, 9)
    for i in range(5):
        state.set_cell(Position(i, 0), BallColor.BLUE)
    
    print("Before:")
    print(state)
    
    env._current_state = state
    removed, points = env._check_and_remove_matches(state, Position(2, 0))
    
    print(f"\nRemoved {len(removed)} balls")
    print(f"Points: {points}")
    print("\nAfter:")
    print(state)
    
    assert len(removed) == 5, f"Expected 5 removed, got {len(removed)}"
    assert points > 0, "Expected points > 0"
    print("✓ Test 2 passed")
    
    # Test 3: Diagonal match
    print("\n" + "="*60)
    print("Test 3: Diagonal match (5 green balls)")
    state = GameState.create_empty(9, 9)
    for i in range(5):
        state.set_cell(Position(i, i), BallColor.GREEN)
    
    print("Before:")
    print(state)
    
    env._current_state = state
    removed, points = env._check_and_remove_matches(state, Position(2, 2))
    
    print(f"\nRemoved {len(removed)} balls")
    print(f"Points: {points}")
    print("\nAfter:")
    print(state)
    
    assert len(removed) == 5, f"Expected 5 removed, got {len(removed)}"
    assert points > 0, "Expected points > 0"
    print("✓ Test 3 passed")
    
    # Test 4: No match (only 4 balls)
    print("\n" + "="*60)
    print("Test 4: No match (only 4 balls)")
    state = GameState.create_empty(9, 9)
    for i in range(4):
        state.set_cell(Position(0, i), BallColor.RED)
    
    print("Before:")
    print(state)
    
    env._current_state = state
    removed, points = env._check_and_remove_matches(state, Position(0, 2))
    
    print(f"\nRemoved {len(removed)} balls")
    print(f"Points: {points}")
    
    assert len(removed) == 0, f"Expected 0 removed, got {len(removed)}"
    assert points == 0, "Expected 0 points"
    print("✓ Test 4 passed")
    
    # Test 5: Multiple matches (cross pattern)
    print("\n" + "="*60)
    print("Test 5: Multiple matches (horizontal + vertical)")
    state = GameState.create_empty(9, 9)
    # Horizontal line
    for i in range(5):
        state.set_cell(Position(2, i), BallColor.MAGENTA)
    # Vertical line (sharing center)
    for i in range(5):
        state.set_cell(Position(i, 2), BallColor.MAGENTA)
    
    print("Before:")
    print(state)
    
    env._current_state = state
    removed, points = env._check_and_remove_matches(state, Position(2, 2))
    
    print(f"\nRemoved {len(removed)} balls")
    print(f"Points: {points}")
    print("\nAfter:")
    print(state)
    
    # Should remove 9 balls (5 horizontal + 5 vertical - 1 shared)
    assert len(removed) == 9, f"Expected 9 removed, got {len(removed)}"
    assert points > 0, "Expected points > 0"
    print("✓ Test 5 passed")
    
    print("\n" + "="*60)
    print("ALL TESTS PASSED ✓")
    print("="*60)
    print("\nYou can now copy this implementation to game_environment.py")

