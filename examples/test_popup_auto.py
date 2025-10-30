"""
Automatic popup handling test.

This will automatically handle popups after a countdown,
so you don't need to press Enter in the terminal.
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
    print("AUTOMATIC POPUP HANDLING TEST")
    print("="*70)
    print("\nInstructions:")
    print("  1. Play the game until game over")
    print("  2. Wait for BOTH popups to appear:")
    print("     - Game over popup")
    print("     - High score popup (appears AFTER game over)")
    print("  3. Leave both popups showing")
    print()
    print("The script will automatically handle the popups after 5 seconds.")
    print("This way you don't need to press Enter in the terminal.")
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
        return
    
    print("✓ Game client calibrated")
    
    # Handle popups
    print("\n" + "="*70)
    print("HANDLING POPUPS")
    print("="*70)
    
    print("\nStep 1: Finding and focusing on game over popup...")
    popup = env._find_popup_window()
    if popup:
        print(f"  ✓ Found popup window (handle: {popup})")
    else:
        print("  ⚠ No popup window found")
    
    print("\nStep 2: Sending Enter to dismiss game over popup...")
    env._send_enter_to_window(popup)
    print("  ✓ Enter sent")
    
    print("\nStep 3: Waiting 0.8s for popup to close...")
    time.sleep(0.8)
    print("  ✓ Wait complete")
    
    print("\nStep 4: Finding and focusing on high score popup...")
    popup = env._find_popup_window()
    if popup:
        print(f"  ✓ Found popup window (handle: {popup})")
    else:
        print("  ⚠ No popup window found")
    
    print("\nStep 5: Sending Enter to dismiss high score popup...")
    env._send_enter_to_window(popup)
    print("  ✓ Enter sent")
    
    print("\nStep 6: Waiting 0.8s for popup to close...")
    time.sleep(0.8)
    print("  ✓ Wait complete")
    
    print("\nStep 7: Waiting for game to auto-restart...")
    time.sleep(1.0)
    print("  ✓ Wait complete")
    
    # Read state
    print("\n" + "="*70)
    print("CHECKING RESULT")
    print("="*70)
    
    try:
        state = env.get_state()
        ball_count = sum(1 for row in range(9) for col in range(9) if state.board[row, col] != 0)
        
        print(f"\nCurrent state:")
        print(f"  Balls: {ball_count}/81")
        print(f"  Score: {state.score}")
        
        if ball_count == 5:
            print("\n✓ SUCCESS! Game restarted correctly!")
            print("  - Game over popup was dismissed")
            print("  - High score popup was dismissed")
            print("  - Game auto-restarted with 5 balls")
        else:
            print(f"\n⚠ Game has {ball_count} balls (expected 5)")
            if ball_count > 5:
                print("  - Popups may not have been dismissed")
                print("  - Game may not have restarted")
            else:
                print("  - Unexpected state")
    except Exception as e:
        print(f"\n✗ Error reading state: {e}")
    
    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70)


if __name__ == "__main__":
    main()

