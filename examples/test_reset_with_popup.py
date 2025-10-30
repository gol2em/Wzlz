"""
Test reset when game over popup is already showing.

Instructions:
1. Manually play the game until it's over
2. Let the game over popup appear
3. Let the high score popup appear (if applicable)
4. Run this script - it will handle the popups and reset
"""

import sys
from pathlib import Path
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from wzlz_ai.game_state import GameConfig
from wzlz_ai.game_client import GameClientEnvironment


def main():
    print("="*70)
    print("TEST RESET WITH POPUP")
    print("="*70)
    print("\nInstructions:")
    print("  1. Manually play the game until game over")
    print("  2. Wait for BOTH popups to appear:")
    print("     - Game over popup")
    print("     - High score popup (appears AFTER game over)")
    print("  3. Leave both popups showing")
    print()
    print("The script will automatically call env.reset() after 5 seconds.")
    print("This will:")
    print("  - Find and dismiss game over popup (Enter)")
    print("  - Find and dismiss high score popup (Enter)")
    print("  - Game auto-restarts with 5 balls")
    print()

    # Countdown
    for i in range(5, 0, -1):
        print(f"Starting in {i} seconds...", end="\r")
        time.sleep(1)

    print("\nStarting now!                    ")
    
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
    
    # Reset the game (this will handle popups)
    print("\n" + "="*70)
    print("RESETTING GAME")
    print("="*70)

    print("\nCalling env.reset()...")
    print("This will:")
    print("  1. Find and send Enter to game over popup")
    print("  2. Wait 0.8s")
    print("  3. Find and send Enter to high score popup")
    print("  4. Wait 0.8s")
    print("  5. Wait 1.0s for game to auto-restart")
    print("  6. Read the new initial state")

    new_state = env.reset()
    
    # Check result
    print("\n" + "="*70)
    print("RESULT")
    print("="*70)
    
    ball_count = sum(1 for row in range(9) for col in range(9) if new_state.board[row, col] != 0)
    
    print(f"\nAfter reset:")
    print(f"  Balls: {ball_count}/81")
    print(f"  Score: {new_state.score}")
    print(f"  Game over: {new_state.game_over}")
    
    if ball_count == 5:
        print("\n✓ SUCCESS! Game reset correctly!")
        print("  - Game window was focused")
        print("  - Game over popup was dismissed (Enter)")
        print("  - High score popup was dismissed (Enter)")
        print("  - Game auto-restarted")
        print("  - New game started with 5 balls")
    else:
        print(f"\n✗ FAILED! Expected 5 balls, got {ball_count}")
        print("  - Popups may not have been dismissed correctly")
        print("  - Or game didn't auto-restart")
        print("  - Try running the test again")
    
    print("\n" + "="*70)
    print("TEST COMPLETE!")
    print("="*70)


if __name__ == "__main__":
    main()

