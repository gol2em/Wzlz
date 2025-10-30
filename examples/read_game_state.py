"""
Read complete game state from the game window.

This script demonstrates how to extract all game state information:
- Board state (9x9 grid)
- Current score
- High score
- Next balls preview
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from wzlz_ai.game_state_reader import GameStateReader
from wzlz_ai import GameConfig


def main():
    """Main function."""
    print("\n" + "="*70)
    print("WZLZ GAME STATE READER")
    print("="*70)
    
    # Check if calibration exists
    config_file = Path('game_window_config.json')
    if not config_file.exists():
        print("\n⚠ Calibration file not found!")
        print("Please run: python examples/calibrate_game_window.py")
        return
    
    # Initialize reader
    print("\nInitializing game state reader...")
    reader = GameStateReader(str(config_file))
    
    if not reader.window_capture.hwnd:
        print("✗ Game window not found!")
        print("Please make sure the game (五子连珠5.2) is running.")
        return
    
    print("✓ Game window found")
    
    # Read complete game state
    print("\nReading game state...")
    state = reader.read_game_state()
    
    if state is None:
        print("✗ Failed to read game state!")
        return
    
    print("✓ Game state read successfully")
    
    # Display game state
    print("\n" + "="*70)
    print("CURRENT GAME STATE")
    print("="*70)
    
    # Board
    print("\nBoard:")
    print(state)
    
    # Count balls
    import numpy as np
    from wzlz_ai import BallColor
    
    ball_count = np.sum(state.board != BallColor.EMPTY)
    print(f"\nBalls on board: {ball_count}")
    
    # Count by color
    print("\nBalls by color:")
    for color in BallColor:
        if color == BallColor.EMPTY:
            continue
        count = np.sum(state.board == color)
        if count > 0:
            print(f"  {color.name}: {count}")
    
    # Score
    print(f"\nCurrent score: {state.score}")
    
    # High score
    high_score = reader.read_high_score()
    print(f"High score: {high_score}")
    
    # Next balls
    if state.next_balls:
        print(f"\nNext balls: {[b.name for b in state.next_balls]}")
    else:
        print("\nNext balls: Not available (game mode without preview)")
    
    # Game status
    print(f"\nGame over: {state.is_game_over()}")
    
    # Available moves
    print("\nChecking available moves...")
    has_moves = False
    move_count = 0
    
    # Sample a few positions to check if moves are possible
    for row in range(9):
        for col in range(9):
            if state.board[row, col] != BallColor.EMPTY:
                # Check if this ball can move anywhere
                from wzlz_ai import Position
                for target_row in range(9):
                    for target_col in range(9):
                        if state.board[target_row, target_col] == BallColor.EMPTY:
                            # Just check a few to see if moves exist
                            move_count += 1
                            has_moves = True
                            if move_count > 10:
                                break
                    if move_count > 10:
                        break
            if move_count > 10:
                break
        if move_count > 10:
            break
    
    if has_moves:
        print("✓ Moves are available")
    else:
        print("✗ No moves available (game over)")
    
    print("\n" + "="*70)
    print("GAME STATE EXTRACTION COMPLETE!")
    print("="*70)
    
    # Additional information
    print("\n📊 Summary:")
    print(f"  - Board: 9×9 grid with {ball_count} balls")
    print(f"  - Current score: {state.score}")
    print(f"  - High score: {high_score}")
    print(f"  - Next balls: {len(state.next_balls) if state.next_balls else 0}")
    print(f"  - Game over: {state.is_game_over()}")
    
    print("\n💡 Next steps:")
    print("  1. Verify the detected board matches the actual game")
    print("  2. If colors are wrong, calibrate color samples")
    print("  3. Use this state to validate game rules")
    print("  4. Execute moves and verify behavior")
    
    return state


if __name__ == "__main__":
    state = main()

