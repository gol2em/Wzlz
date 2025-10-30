"""
Play a full game using the GameClientEnvironment.

This demonstrates:
1. Resetting the game
2. Playing until game over
3. Making random moves
4. Tracking score and moves
"""

import sys
from pathlib import Path
import random

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from wzlz_ai.game_state import GameConfig
from wzlz_ai.game_client import GameClientEnvironment


def print_board_summary(state, move_num=None):
    """Print a summary of the board state."""
    ball_count = 0
    for row in range(9):
        for col in range(9):
            if state.board[row, col] != 0:  # Not empty
                ball_count += 1
    
    if move_num is not None:
        print(f"\nMove {move_num}:")
    else:
        print("\nCurrent state:")
    print(f"  Balls: {ball_count}/81")
    print(f"  Score: {state.score}")
    print(f"  Game over: {state.game_over}")


def main():
    print("="*70)
    print("PLAY FULL GAME")
    print("="*70)
    print("\nThis will:")
    print("  1. Reset the game (F4)")
    print("  2. Play random moves until game over")
    print("  3. Show progress every 5 moves")
    
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
    
    # Reset the game
    print("\n" + "="*70)
    print("RESETTING GAME")
    print("="*70)
    
    state = env.reset()
    print("\n✓ Game reset!")
    print_board_summary(state)
    
    # Play the game
    print("\n" + "="*70)
    print("PLAYING GAME")
    print("="*70)
    print("\nMaking random moves until game over...")
    print("(Showing progress every 5 moves)")
    
    move_count = 0
    max_moves = 100  # Safety limit
    
    while not state.game_over and move_count < max_moves:
        # Get valid moves
        valid_moves = env.get_valid_moves(state)
        
        if len(valid_moves) == 0:
            print("\n✗ No valid moves available!")
            break
        
        # Pick a random move
        move = random.choice(valid_moves)
        
        # Execute the move
        result = env.execute_move(move)
        
        if result.success:
            move_count += 1
            state = result.new_state
            
            # Show progress every 5 moves
            if move_count % 5 == 0:
                print_board_summary(state, move_count)
        else:
            print(f"\n✗ Move {move_count + 1} failed: {result.error_message}")
            break
    
    # Game over
    print("\n" + "="*70)
    print("GAME OVER")
    print("="*70)
    
    final_state = env.get_state()
    
    print(f"\nFinal statistics:")
    print(f"  Total moves: {move_count}")
    print(f"  Final score: {final_state.score}")
    
    # Count final balls
    ball_count = 0
    for row in range(9):
        for col in range(9):
            if final_state.board[row, col] != 0:
                ball_count += 1
    
    print(f"  Final balls: {ball_count}/81")
    
    if final_state.game_over:
        print(f"  Status: Game Over (board full)")
    elif move_count >= max_moves:
        print(f"  Status: Stopped (reached {max_moves} move limit)")
    else:
        print(f"  Status: Stopped (no valid moves)")
    
    print("\n" + "="*70)
    print("COMPLETE!")
    print("="*70)
    print("\nThe GameClientEnvironment can now:")
    print("  ✓ Reset the game (env.reset())")
    print("  ✓ Read game state (env.get_state())")
    print("  ✓ Get valid moves (env.get_valid_moves())")
    print("  ✓ Execute moves (env.execute_move())")
    print("  ✓ Play full games until game over")
    print("\nReady for AI training! 🎯")


if __name__ == "__main__":
    main()

