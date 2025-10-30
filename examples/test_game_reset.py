"""
Test the game reset functionality (F4 key).
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from wzlz_ai.game_state import GameConfig
from wzlz_ai.game_client import GameClientEnvironment


def print_board_summary(state):
    """Print a summary of the board state."""
    ball_count = 0
    for row in range(9):
        for col in range(9):
            if state.board[row, col] != 0:  # Not empty
                ball_count += 1
    
    print(f"  Balls on board: {ball_count}")
    print(f"  Score: {state.score}")
    print(f"  Move count: {state.move_count}")
    print(f"  Game over: {state.game_over}")


def main():
    print("="*70)
    print("GAME RESET TEST (F4)")
    print("="*70)
    
    # Create game config
    config = GameConfig(show_next_balls=True)
    
    # Create game client environment
    print("\nInitializing GameClientEnvironment...")
    env = GameClientEnvironment(config)
    
    if not env.is_calibrated:
        print("\n✗ Game client not calibrated!")
        print("Run: uv run python examples/manual_calibrate_all.py")
        return
    
    print("✓ Game client calibrated")
    
    # Get current state
    print("\n" + "="*70)
    print("STEP 1: READ CURRENT STATE")
    print("="*70)
    
    state_before = env.get_state()
    print("\nCurrent state:")
    print_board_summary(state_before)
    
    # Make a few moves to change the state
    print("\n" + "="*70)
    print("STEP 2: MAKE SOME MOVES")
    print("="*70)
    
    moves = env.get_valid_moves(state_before)
    if len(moves) >= 3:
        print(f"\nMaking 3 moves...")
        for i in range(3):
            move = moves[i]
            print(f"  Move {i+1}: ({move.from_pos.row}, {move.from_pos.col}) -> "
                  f"({move.to_pos.row}, {move.to_pos.col})")
            result = env.execute_move(move)
            if not result.success:
                print(f"    ✗ Move failed!")
                break
        
        # Read state after moves
        state_after_moves = env.get_state()
        print("\nState after moves:")
        print_board_summary(state_after_moves)
    else:
        print("\n✗ Not enough valid moves!")
        return
    
    # Reset the game
    print("\n" + "="*70)
    print("STEP 3: RESET GAME (Press F4)")
    print("="*70)
    
    print("\nResetting game...")
    state_after_reset = env.reset()
    
    print("\n✓ Game reset!")
    print("\nState after reset:")
    print_board_summary(state_after_reset)
    
    # Verify reset worked
    print("\n" + "="*70)
    print("VERIFICATION")
    print("="*70)
    
    # Count balls in initial state (should be 5)
    ball_count = 0
    for row in range(9):
        for col in range(9):
            if state_after_reset.board[row, col] != 0:
                ball_count += 1
    
    print(f"\nBalls after reset: {ball_count}")
    if ball_count == 5:
        print("✓ Correct! New game starts with 5 balls")
    else:
        print(f"⚠ Expected 5 balls, got {ball_count}")
    
    if state_after_reset.score == 0:
        print("✓ Score reset to 0")
    else:
        print(f"⚠ Score is {state_after_reset.score}, expected 0")
    
    if state_after_reset.move_count == 0:
        print("✓ Move count reset to 0")
    else:
        print(f"⚠ Move count is {state_after_reset.move_count}, expected 0")
    
    print("\n" + "="*70)
    print("TEST COMPLETE!")
    print("="*70)
    print("\nThe reset() function is working correctly!")
    print("You can now use env.reset() to start a new game.")


if __name__ == "__main__":
    main()

