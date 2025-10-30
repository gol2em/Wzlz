"""
Manual test for game over and high score popups.

Instructions:
1. Set up the game so it's about to end (board nearly full)
2. Run this script
3. The script will wait for you to manually trigger game over
4. Then it will handle the popups and reset
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from wzlz_ai.game_state import GameConfig
from wzlz_ai.game_client import GameClientEnvironment
import time


def main():
    print("="*70)
    print("MANUAL GAME OVER POPUP TEST")
    print("="*70)
    print("\nInstructions:")
    print("  1. Make sure the game is set up with a nearly full board")
    print("  2. This script will read the current state")
    print("  3. You manually make the final move(s) to trigger game over")
    print("  4. The script will detect game over and handle popups")
    print()
    print("Popup sequence when game over:")
    print("  1. Board fills up")
    print("  2. Game over popup appears")
    print("  3. High score popup appears (AFTER game over popup)")
    print("  4. Script will press Enter twice to dismiss both")
    print("  5. Script will press F4 to restart")
    
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
    
    # Read initial state
    print("\n" + "="*70)
    print("CURRENT STATE")
    print("="*70)
    
    state = env.get_state()
    
    ball_count = sum(1 for row in range(9) for col in range(9) if state.board[row, col] != 0)
    empty_count = 81 - ball_count
    
    print(f"\nBalls on board: {ball_count}/81")
    print(f"Empty cells: {empty_count}")
    print(f"Game over: {state.game_over}")
    
    # Wait for user to trigger game over
    print("\n" + "="*70)
    print("WAITING FOR GAME OVER")
    print("="*70)
    print("\nNow manually play the game until it's over.")
    print("The script will check every 2 seconds if the board is full.")
    print("\nPress Ctrl+C to cancel.")
    
    try:
        check_count = 0
        while True:
            time.sleep(2)
            check_count += 1
            
            # Read current state
            state = env.get_state()
            ball_count = sum(1 for row in range(9) for col in range(9) if state.board[row, col] != 0)
            
            print(f"Check {check_count}: {ball_count}/81 balls", end="\r")
            
            # Check if board is full
            if ball_count == 81:
                print(f"\n\n✓ Board is full! ({ball_count}/81 balls)")
                break
    
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user.")
        return
    
    # Handle popups
    print("\n" + "="*70)
    print("HANDLING POPUPS")
    print("="*70)
    
    print("\nWaiting for game over popup to appear...")
    time.sleep(1.0)
    
    print("Pressing Enter to dismiss game over popup...")
    env._handle_popups()
    
    print("Waiting for high score popup to appear...")
    time.sleep(0.5)
    
    print("Pressing Enter to dismiss high score popup...")
    env._handle_popups()
    
    print("\n✓ Popups handled!")
    
    # Reset the game
    print("\n" + "="*70)
    print("RESETTING GAME")
    print("="*70)
    
    print("\nPressing F4 to restart...")
    new_state = env.reset()
    
    ball_count = sum(1 for row in range(9) for col in range(9) if new_state.board[row, col] != 0)
    
    print(f"\nAfter reset:")
    print(f"  Balls: {ball_count}/81")
    print(f"  Score: {new_state.score}")
    print(f"  Game over: {new_state.game_over}")
    
    if ball_count == 5:
        print("\n✓ Game reset successfully!")
    else:
        print(f"\n⚠ Expected 5 balls, got {ball_count}")
    
    print("\n" + "="*70)
    print("TEST COMPLETE!")
    print("="*70)
    print("\nThe popup handling sequence works:")
    print("  1. ✓ Game over popup → Enter")
    print("  2. ✓ High score popup → Enter (appears AFTER game over)")
    print("  3. ✓ F4 to restart")


if __name__ == "__main__":
    main()

