"""
Test memory reading with known addresses.

This script demonstrates how to use the memory reader once you've
discovered the memory addresses using explore_memory.py.
"""

import time
import sys
from wzlz_ai.memory_reader import GameMemoryReader
from wzlz_ai.game_state import BallColor


def print_board(board):
    """Print board in a readable format."""
    color_symbols = {
        BallColor.EMPTY: '·',
        BallColor.RED: 'R',
        BallColor.GREEN: 'G',
        BallColor.BLUE: 'B',
        BallColor.BROWN: 'N',
        BallColor.MAGENTA: 'M',
        BallColor.YELLOW: 'Y',
        BallColor.CYAN: 'C',
    }
    
    print("  0 1 2 3 4 5 6 7 8")
    for i, row in enumerate(board):
        symbols = [color_symbols.get(BallColor(cell), '?') for cell in row]
        print(f"{i} {' '.join(symbols)}")


def main():
    """Main entry point."""
    # TODO: Replace these with your discovered addresses
    BOARD_ADDRESS = None  # e.g., 0x12345678
    SCORE_ADDRESS = None  # e.g., 0x87654321
    
    if BOARD_ADDRESS is None:
        print("Please run explore_memory.py first to find the memory addresses!")
        print("Then update BOARD_ADDRESS and SCORE_ADDRESS in this script.")
        sys.exit(1)
    
    # Initialize memory reader
    reader = GameMemoryReader()
    
    # Attach to game
    print("Attaching to game process...")
    if not reader.attach():
        print("Failed to attach to game process!")
        print("Make sure the game is running.")
        sys.exit(1)
    
    print("✓ Successfully attached to game!")
    
    # Set known addresses
    reader.board_address = BOARD_ADDRESS
    reader.score_address = SCORE_ADDRESS
    
    # Continuous reading loop
    print("\nReading game state from memory...")
    print("Press Ctrl+C to stop\n")
    
    try:
        while True:
            # Read game state
            state = reader.read_game_state()
            
            if state:
                print("\033[H\033[J")  # Clear screen
                print("=== Game State (from Memory) ===")
                print(f"Score: {state.score}")
                print("\nBoard:")
                print_board(state.board)
                print("\n(Updates every 0.5 seconds)")
            else:
                print("Failed to read game state")
            
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\n\nStopped.")


if __name__ == "__main__":
    main()

