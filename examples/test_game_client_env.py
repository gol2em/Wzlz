"""
Test the GameClientEnvironment integration with the training framework.

This demonstrates how to use the GameClientEnvironment to interact with
the actual game window using the same interface as SimulationEnvironment.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from wzlz_ai.game_state import GameConfig
from wzlz_ai.game_client import GameClientEnvironment


def print_board(board):
    """Print the board in a readable format."""
    color_symbols = {
        'RED': 'R',
        'GREEN': 'G',
        'BLUE': 'B',
        'BROWN': 'N',
        'MAGENTA': 'M',
        'YELLOW': 'Y',
        'CYAN': 'C',
        'EMPTY': '.'
    }
    
    print("\n  ", end="")
    for col in range(9):
        print(f"{col} ", end="")
    print()
    
    for row in range(9):
        print(f"{row} ", end="")
        for col in range(9):
            cell = board[row][col]
            if hasattr(cell, 'value'):
                symbol = color_symbols.get(cell.value, '?')
            else:
                symbol = color_symbols.get(cell, '?')
            print(f"{symbol} ", end="")
        print()


def main():
    print("="*70)
    print("GAME CLIENT ENVIRONMENT TEST")
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
    print("READING CURRENT STATE")
    print("="*70)
    
    state = env.get_state()
    print("\nCurrent board:")
    print_board(state.board)
    
    # Get valid moves
    print("\n" + "="*70)
    print("GETTING VALID MOVES")
    print("="*70)
    
    valid_moves = env.get_valid_moves(state)
    print(f"\nFound {len(valid_moves)} valid moves")
    
    if len(valid_moves) > 0:
        # Show first 5 moves
        print("\nFirst 5 moves:")
        for i, move in enumerate(valid_moves[:5]):
            print(f"  {i+1}. Move from ({move.from_pos.row}, {move.from_pos.col}) "
                  f"to ({move.to_pos.row}, {move.to_pos.col})")
    
    # Execute a move
    if len(valid_moves) > 0:
        print("\n" + "="*70)
        print("EXECUTING MOVE")
        print("="*70)
        
        move = valid_moves[0]
        print(f"\nExecuting move: ({move.from_pos.row}, {move.from_pos.col}) -> "
              f"({move.to_pos.row}, {move.to_pos.col})")
        
        result = env.execute_move(move)
        
        if result.success:
            print("\n✓ Move executed successfully!")
            print("\nBoard after move:")
            print_board(result.new_state.board)
        else:
            print(f"\n✗ Move failed: {result.error_message}")
    
    print("\n" + "="*70)
    print("TEST COMPLETE!")
    print("="*70)
    print("\nThe GameClientEnvironment is now ready for training!")
    print("You can use it just like SimulationEnvironment:")
    print("  - env.get_state() - Read current state")
    print("  - env.get_valid_moves() - Get all valid moves")
    print("  - env.execute_move(move) - Execute a move")
    print("  - env.reset() - Reset the game (reads current state)")


if __name__ == "__main__":
    main()

