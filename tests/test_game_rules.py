"""
Test game rules implementation.

This module tests the matching logic, scoring, and game rules.
"""

from wzlz_ai import SimulationEnvironment, GameConfig, GameState, Position, Move, BallColor
import numpy as np


def test_path_only_horizontal_vertical():
    """Test that paths can only be horizontal/vertical, not diagonal."""
    config = GameConfig()
    env = SimulationEnvironment(config, seed=42)
    state = env.reset()

    # Create a scenario where diagonal would be shorter but is blocked
    # Clear the board first
    for row in range(9):
        for col in range(9):
            state.set_cell(Position(row, col), BallColor.EMPTY)

    state.set_cell(Position(0, 0), BallColor.RED)

    # Block diagonal path with a ball at (1, 1)
    state.set_cell(Position(1, 1), BallColor.BLUE)

    env._current_state = state

    # Try to move to (2, 2) - should go around the obstacle
    path_exists, path = env.is_path_clear(Position(0, 0), Position(2, 2), state)

    print(f"Path exists: {path_exists}")
    print(f"Path length: {len(path) if path_exists else 0}")
    print(f"Path: {path if path_exists else 'None'}")

    # Path should exist but be longer than diagonal (which would be 3 steps)
    assert path_exists, "Path should exist going around obstacle"
    # Diagonal would be 3 steps, but we need to go around, so at least 5 steps
    assert len(path) >= 5, f"Path should be at least 5 steps (going around), got {len(path)}"

    # Verify path only uses horizontal/vertical moves
    for i in range(len(path) - 1):
        curr = path[i]
        next_pos = path[i + 1]
        row_diff = abs(next_pos.row - curr.row)
        col_diff = abs(next_pos.col - curr.col)

        # Only one of row_diff or col_diff should be 1, the other should be 0
        assert (row_diff == 1 and col_diff == 0) or (row_diff == 0 and col_diff == 1), \
            f"Path contains diagonal move from {curr} to {next_pos}"

    print("✓ Path only uses horizontal/vertical moves")


def test_game_mode_with_preview():
    """Test game mode with next ball preview."""
    config = GameConfig(show_next_balls=True)
    env = SimulationEnvironment(config, seed=42)

    state = env.reset()

    # Should have next balls preview
    assert len(state.next_balls) == 3, f"Should have 3 next balls, got {len(state.next_balls)}"
    print(f"✓ Mode with preview: next_balls = {[b.name for b in state.next_balls]}")


def test_game_mode_without_preview():
    """Test game mode without next ball preview."""
    config = GameConfig(show_next_balls=False)
    env = SimulationEnvironment(config, seed=42)

    state = env.reset()

    # Should NOT have next balls preview
    assert len(state.next_balls) == 0, f"Should have 0 next balls, got {len(state.next_balls)}"
    print("✓ Mode without preview: next_balls = []")


def test_horizontal_match():
    """Test horizontal line matching."""
    print("\n" + "="*60)
    print("Testing Horizontal Match (5 balls in a row)")
    print("="*60)
    
    config = GameConfig(rows=9, cols=9, match_length=5)
    env = SimulationEnvironment(config, seed=42)
    
    # Create a custom state with 5 red balls in a row
    state = GameState.create_empty(9, 9)
    for col in range(5):
        state.set_cell(Position(0, col), BallColor.RED)
    
    print("\nBefore matching:")
    print(state)

    # Check for matches
    removed, count = env._check_and_remove_matches(state, Position(0, 2))

    print(f"\n✓ Removed {count} balls")
    print(f"✓ Positions: {removed}")

    print("\nAfter matching:")
    print(state)
    
    assert count == 5, f"Expected 5 balls removed, got {count}"
    assert all(state.is_empty(Position(0, col)) for col in range(5)), "Balls not removed"
    print("✓ Horizontal match test passed!")


def test_vertical_match():
    """Test vertical line matching."""
    print("\n" + "="*60)
    print("Testing Vertical Match (5 balls in a column)")
    print("="*60)
    
    config = GameConfig(rows=9, cols=9, match_length=5)
    env = SimulationEnvironment(config, seed=42)
    
    # Create a custom state with 5 blue balls in a column
    state = GameState.create_empty(9, 9)
    for row in range(5):
        state.set_cell(Position(row, 0), BallColor.BLUE)
    
    print("\nBefore matching:")
    print(state)

    # Check for matches
    removed, count = env._check_and_remove_matches(state, Position(2, 0))

    print(f"\n✓ Removed {count} balls")
    print(f"✓ Positions: {removed}")

    print("\nAfter matching:")
    print(state)
    
    assert count == 5, f"Expected 5 balls removed, got {count}"
    assert all(state.is_empty(Position(row, 0)) for row in range(5)), "Balls not removed"
    print("✓ Vertical match test passed!")


def test_diagonal_match():
    """Test diagonal line matching."""
    print("\n" + "="*60)
    print("Testing Diagonal Match (5 balls diagonally)")
    print("="*60)
    
    config = GameConfig(rows=9, cols=9, match_length=5)
    env = SimulationEnvironment(config, seed=42)
    
    # Create a custom state with 5 green balls diagonally
    state = GameState.create_empty(9, 9)
    for i in range(5):
        state.set_cell(Position(i, i), BallColor.GREEN)
    
    print("\nBefore matching:")
    print(state)

    # Check for matches
    removed, count = env._check_and_remove_matches(state, Position(2, 2))

    print(f"\n✓ Removed {count} balls")
    print(f"✓ Positions: {removed}")

    print("\nAfter matching:")
    print(state)
    
    assert count == 5, f"Expected 5 balls removed, got {count}"
    assert all(state.is_empty(Position(i, i)) for i in range(5)), "Balls not removed"
    print("✓ Diagonal match test passed!")


def test_scoring():
    """Test scoring system (2 points per ball)."""
    print("\n" + "="*60)
    print("Testing Scoring System")
    print("="*60)
    
    config = GameConfig(rows=9, cols=9, match_length=5, initial_balls=0)
    env = SimulationEnvironment(config, seed=42)
    state = env.reset()
    
    # Manually create a setup where we can make a match
    # Place 4 red balls in a row
    for col in range(4):
        state.set_cell(Position(4, col), BallColor.RED)
    
    # Place a red ball that we'll move to complete the line
    state.set_cell(Position(3, 4), BallColor.RED)
    
    # Clear next_balls to prevent random balls from being added
    state.next_balls = []
    
    env._current_state = state
    
    print("\nBefore move:")
    print(state)
    print(f"Score: {state.score}")

    # Move the ball to complete the line
    move = Move(Position(3, 4), Position(4, 4))
    result = env.execute_move(move)

    print("\nAfter move:")
    print(result.new_state)
    print(f"Score: {result.new_state.score}")
    print(f"Points earned: {result.points_earned}")
    print(f"Balls removed: {len(result.balls_removed)}")
    
    assert result.success, "Move should succeed"
    assert len(result.balls_removed) == 5, f"Expected 5 balls removed, got {len(result.balls_removed)}"
    assert result.points_earned == 10, f"Expected 10 points (5 balls × 2), got {result.points_earned}"
    assert result.new_state.score == 10, f"Expected score 10, got {result.new_state.score}"
    print("✓ Scoring test passed!")


def test_no_points_for_auto_match():
    """Test that auto-matches after random generation give no points."""
    print("\n" + "="*60)
    print("Testing Auto-Match (No Points)")
    print("="*60)
    
    config = GameConfig(rows=9, cols=9, match_length=5, initial_balls=0)
    env = SimulationEnvironment(config, seed=123)
    state = env.reset()
    
    # Create a setup where random balls will complete a line
    # Place 4 red balls in a row, leaving one gap
    state.set_cell(Position(4, 0), BallColor.RED)
    state.set_cell(Position(4, 1), BallColor.RED)
    state.set_cell(Position(4, 2), BallColor.RED)
    state.set_cell(Position(4, 3), BallColor.RED)
    # Gap at Position(4, 4)
    
    # Place a ball to move (not creating a match)
    state.set_cell(Position(0, 0), BallColor.BLUE)
    
    # Set next_balls to include a RED ball that will fill the gap
    state.next_balls = [BallColor.RED, BallColor.GREEN, BallColor.BLUE]
    
    env._current_state = state
    
    print("\nBefore move:")
    print(state)
    print(f"Score: {state.score}")

    # Make a move that doesn't create a match
    move = Move(Position(0, 0), Position(0, 1))
    result = env.execute_move(move)

    print("\nAfter move:")
    print(result.new_state)
    print(f"Score: {result.new_state.score}")
    print(f"Points earned from move: {result.points_earned}")
    print(f"New balls added: {len(result.new_balls_added)}")
    print(f"Total balls removed: {len(result.balls_removed)}")
    
    # The move itself shouldn't earn points
    # If random balls create a match, still no points
    assert result.points_earned == 0, f"Expected 0 points from move, got {result.points_earned}"
    print("✓ Auto-match test passed!")


def test_longer_match():
    """Test matching more than 5 balls."""
    print("\n" + "="*60)
    print("Testing Longer Match (7 balls)")
    print("="*60)
    
    config = GameConfig(rows=9, cols=9, match_length=5)
    env = SimulationEnvironment(config, seed=42)
    
    # Create a custom state with 7 yellow balls in a row
    state = GameState.create_empty(9, 9)
    for col in range(7):
        state.set_cell(Position(4, col), BallColor.YELLOW)
    
    print("\nBefore matching:")
    print(state)

    # Check for matches
    removed, count = env._check_and_remove_matches(state, Position(4, 3))

    print(f"\n✓ Removed {count} balls")
    print(f"✓ Positions: {removed}")

    print("\nAfter matching:")
    print(state)
    
    assert count == 7, f"Expected 7 balls removed, got {count}"
    print("✓ Longer match test passed!")


def test_multiple_matches():
    """Test multiple matches at once (cross pattern)."""
    print("\n" + "="*60)
    print("Testing Multiple Matches (Cross Pattern)")
    print("="*60)
    
    config = GameConfig(rows=9, cols=9, match_length=5)
    env = SimulationEnvironment(config, seed=42)
    
    # Create a cross pattern with cyan balls
    state = GameState.create_empty(9, 9)
    
    # Horizontal line
    for col in range(5):
        state.set_cell(Position(4, col), BallColor.CYAN)
    
    # Vertical line (overlapping at center)
    for row in range(5):
        state.set_cell(Position(row, 2), BallColor.CYAN)
    
    print("\nBefore matching:")
    print(state)

    # Check for matches at the center
    removed, count = env._check_and_remove_matches(state, Position(4, 2))

    print(f"\n✓ Removed {count} balls")
    print(f"✓ Positions: {removed}")

    print("\nAfter matching:")
    print(state)
    
    # Should remove 9 unique balls (5 horizontal + 5 vertical - 1 overlap)
    assert count == 9, f"Expected 9 balls removed, got {count}"
    print("✓ Multiple matches test passed!")


def test_game_over():
    """Test game over condition."""
    print("\n" + "="*60)
    print("Testing Game Over Condition")
    print("="*60)
    
    config = GameConfig(rows=3, cols=3, match_length=5, initial_balls=0)
    env = SimulationEnvironment(config, seed=42)
    state = env.reset()
    
    # Fill the board except one cell
    for row in range(3):
        for col in range(3):
            if row != 2 or col != 2:
                state.set_cell(Position(row, col), BallColor.RED)
    
    env._current_state = state
    
    print("\nBoard (almost full):")
    print(state)

    is_over = env.is_game_over(state)
    print(f"Game over: {is_over}")

    # Should not be game over yet (one valid move exists)
    assert not is_over, "Game should not be over with valid moves"

    # Fill the last cell
    state.set_cell(Position(2, 2), BallColor.BLUE)
    env._current_state = state

    print("\nBoard (completely full):")
    print(state)

    is_over = env.is_game_over(state)
    print(f"Game over: {is_over}")
    
    # Should be game over now
    assert is_over, "Game should be over when board is full"
    print("✓ Game over test passed!")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("GAME RULES TESTS")
    print("="*60)
    
    test_horizontal_match()
    test_vertical_match()
    test_diagonal_match()
    test_scoring()
    test_no_points_for_auto_match()
    test_longer_match()
    test_multiple_matches()
    test_game_over()
    
    print("\n" + "="*60)
    print("ALL GAME RULES TESTS PASSED ✓")
    print("="*60)
    print("\nGame rules implementation is complete and working correctly!")

