"""
Debug test for popup handling.

This will show you exactly what's happening step by step.
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
    print("POPUP HANDLING DEBUG TEST")
    print("="*70)
    print("\nInstructions:")
    print("  1. Play the game until game over")
    print("  2. Let BOTH popups appear:")
    print("     - Game over popup")
    print("     - High score popup (appears AFTER game over)")
    print("  3. Press Enter here when BOTH popups are showing")
    print()
    
    input("Press Enter when both popups are visible...")
    
    # Create game config
    config = GameConfig(show_next_balls=True)
    
    # Create game client environment
    print("\nInitializing GameClientEnvironment...")
    env = GameClientEnvironment(config)
    
    if not env.is_calibrated:
        print("\n✗ Game client not calibrated!")
        return
    
    print("✓ Game client calibrated")
    
    # Manual popup handling with debug output
    print("\n" + "="*70)
    print("STEP-BY-STEP POPUP HANDLING")
    print("="*70)

    print("\nIMPORTANT: Popups already have focus!")
    print("Windows automatically focuses on popups and won't let you")
    print("focus on the main window until popups are dismissed.")
    print("So we just press Enter directly - no need to focus window.")

    print("\nStep 1: Pressing Enter (dismiss game over popup)...")
    print("  (Game over popup already has focus)")
    import win32api
    VK_RETURN = 0x0D
    win32api.keybd_event(VK_RETURN, 0, 0, 0)
    time.sleep(0.05)
    win32api.keybd_event(VK_RETURN, 0, 2, 0)  # KEYEVENTF_KEYUP
    print("  ✓ Enter sent")

    print("\nStep 2: Waiting 0.8s for popup to close...")
    time.sleep(0.8)
    print("  ✓ Wait complete")
    print("  (High score popup should now appear and have focus)")

    print("\nStep 3: Pressing Enter again (dismiss high score popup)...")
    win32api.keybd_event(VK_RETURN, 0, 0, 0)
    time.sleep(0.05)
    win32api.keybd_event(VK_RETURN, 0, 2, 0)  # KEYEVENTF_KEYUP
    print("  ✓ Enter sent")

    print("\nStep 4: Waiting 0.8s for popup to close...")
    time.sleep(0.8)
    print("  ✓ Wait complete")

    print("\nStep 5: Waiting for game to auto-restart...")
    time.sleep(1.0)
    print("  ✓ Wait complete")
    
    # Read state
    print("\n" + "="*70)
    print("READING STATE")
    print("="*70)
    
    try:
        state = env.get_state()
        ball_count = sum(1 for row in range(9) for col in range(9) if state.board[row, col] != 0)
        
        print(f"\nCurrent state:")
        print(f"  Balls: {ball_count}/81")
        print(f"  Score: {state.score}")
        
        if ball_count == 5:
            print("\n✓ SUCCESS! Game restarted with 5 balls")
            print("  Popups were handled correctly!")
        else:
            print(f"\n⚠ Game has {ball_count} balls (expected 5)")
            print("  Possible issues:")
            print("  - Popups weren't dismissed")
            print("  - Game didn't auto-restart")
            print("  - Need to manually click on the popups?")
    except Exception as e:
        print(f"\n✗ Error reading state: {e}")
    
    print("\n" + "="*70)
    print("DEBUG COMPLETE")
    print("="*70)


if __name__ == "__main__":
    main()

