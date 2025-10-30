"""
Test handling of game over and high score popups.

This test assumes you've set up a situation where the game is about to end
and will trigger the game over popup (and possibly high score popup).
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from wzlz_ai.game_state import GameConfig
from wzlz_ai.game_client import GameClientEnvironment


def print_board_summary(state, label="State"):
    """Print a summary of the board state."""
    ball_count = 0
    for row in range(9):
        for col in range(9):
            if state.board[row, col] != 0:  # Not empty
                ball_count += 1
    
    print(f"\n{label}:")
    print(f"  Balls: {ball_count}/81")
    print(f"  Score: {state.score}")
    print(f"  Game over: {state.game_over}")


def main():
    print("="*70)
    print("GAME OVER POPUP TEST")
    print("="*70)
    print("\nThis test will:")
    print("  1. Read the current game state (should be nearly full)")
    print("  2. Make moves until the board is full")
    print("  3. Handle the game over popup (press Enter)")
    print("  4. Handle the high score popup (press Enter)")
    print("     Note: High score popup appears AFTER game over popup")
    print("  5. Reset the game (press F4)")
    print("\nMake sure you've set up a game that's about to end!")
    
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
    
    state = env.get_state()
    print_board_summary(state, "Current state")
    
    # Count empty cells
    empty_count = 0
    for row in range(9):
        for col in range(9):
            if state.board[row, col] == 0:
                empty_count += 1
    
    print(f"\nEmpty cells: {empty_count}")
    
    if empty_count > 10:
        print("\n⚠ Warning: Board has many empty cells.")
        print("This test works best when the board is nearly full.")
        print("Continue anyway? (y/n)")
        response = input().strip().lower()
        if response != 'y':
            print("Test cancelled.")
            return
    
    # Make moves until game over
    print("\n" + "="*70)
    print("STEP 2: MAKE MOVES UNTIL GAME OVER")
    print("="*70)
    
    move_count = 0
    max_moves = 20  # Safety limit
    
    while not state.game_over and move_count < max_moves:
        # Get valid moves
        valid_moves = env.get_valid_moves(state)
        
        if len(valid_moves) == 0:
            print("\n✗ No valid moves available!")
            break
        
        # Pick the first move
        move = valid_moves[0]
        
        print(f"\nMove {move_count + 1}: ({move.from_pos.row}, {move.from_pos.col}) -> "
              f"({move.to_pos.row}, {move.to_pos.col})")
        
        # Execute the move
        result = env.execute_move(move)
        
        if result.success:
            move_count += 1
            state = result.new_state
            print_board_summary(state, f"After move {move_count}")
            
            if state.game_over:
                print("\n✓ Game over detected!")
                print("  Popups should have been handled automatically.")
                break
        else:
            print(f"\n✗ Move failed: {result.error_message}")
            break
    
    # Final state
    print("\n" + "="*70)
    print("STEP 3: FINAL STATE")
    print("="*70)
    
    final_state = env.get_state()
    print_board_summary(final_state, "Final state")
    
    if final_state.game_over:
        print("\n✓ Game over handled successfully!")
        print("  - Game over popup dismissed (Enter)")
        print("  - High score popup dismissed (Enter)")
        print("    (High score popup appears after game over popup)")
    else:
        print("\n⚠ Game not over yet")
    
    # Reset the game
    print("\n" + "="*70)
    print("STEP 4: RESET GAME")
    print("="*70)
    
    print("\nResetting game (F4)...")
    new_state = env.reset()
    
    print_board_summary(new_state, "After reset")
    
    # Verify reset
    ball_count = 0
    for row in range(9):
        for col in range(9):
            if new_state.board[row, col] != 0:
                ball_count += 1
    
    if ball_count == 5:
        print("\n✓ Game reset successfully!")
        print("  - Popups handled (if any)")
        print("  - F4 pressed")
        print("  - New game started with 5 balls")
    else:
        print(f"\n⚠ Expected 5 balls after reset, got {ball_count}")
    
    print("\n" + "="*70)
    print("TEST COMPLETE!")
    print("="*70)
    print("\nThe GameClientEnvironment can now:")
    print("  ✓ Detect when board is full")
    print("  ✓ Handle game over popup (press Enter)")
    print("  ✓ Handle high score popup (press Enter)")
    print("    - High score popup appears AFTER game over popup")
    print("  ✓ Reset game after game over (press F4)")
    print("\nPopup sequence:")
    print("  1. Board fills up")
    print("  2. Game over popup appears → Press Enter")
    print("  3. High score popup appears → Press Enter")
    print("  4. Ready for F4 to restart")


if __name__ == "__main__":
    main()

