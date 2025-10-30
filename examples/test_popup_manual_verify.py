"""
Manual verification test for popup handling.

This will pause at each step so you can verify what's happening.
"""

import sys
from pathlib import Path
import time
import win32api

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def press_enter():
    """Press Enter key using keyboard events."""
    VK_RETURN = 0x0D
    win32api.keybd_event(VK_RETURN, 0, 0, 0)
    time.sleep(0.05)
    win32api.keybd_event(VK_RETURN, 0, 2, 0)  # KEYEVENTF_KEYUP


def main():
    print("="*70)
    print("MANUAL POPUP VERIFICATION TEST")
    print("="*70)
    print("\nThis test will help us understand what's happening.")
    print()
    print("Setup:")
    print("  1. Play the game until game over")
    print("  2. Wait for game over popup to appear")
    print("  3. DO NOT dismiss it - leave it showing")
    print()
    
    input("Press Enter when game over popup is showing...")
    
    print("\n" + "="*70)
    print("TEST 1: DISMISS GAME OVER POPUP")
    print("="*70)
    
    print("\nThe game over popup should be showing now.")
    print("I will press Enter using keyboard events.")
    print()
    input("Press Enter to continue...")
    
    print("\nPressing Enter now...")
    press_enter()
    
    print("\nDid the game over popup close? (y/n)")
    response = input().strip().lower()
    
    if response != 'y':
        print("\n✗ Game over popup did NOT close!")
        print("This means keyboard events aren't reaching the popup.")
        print("\nPossible solutions:")
        print("  1. Make sure no other window has focus")
        print("  2. Try clicking on the popup first")
        print("  3. The popup might need a mouse click instead of Enter")
        return
    
    print("\n✓ Game over popup closed!")
    
    print("\n" + "="*70)
    print("TEST 2: WAIT FOR HIGH SCORE POPUP")
    print("="*70)
    
    print("\nWaiting 1 second for high score popup to appear...")
    time.sleep(1.0)
    
    print("\nDid the high score popup appear? (y/n)")
    response = input().strip().lower()
    
    if response != 'y':
        print("\n⚠ High score popup did NOT appear")
        print("Maybe you didn't beat the high score?")
        print("Or the game already restarted?")
        
        print("\nDid the game restart with 5 balls? (y/n)")
        response = input().strip().lower()
        
        if response == 'y':
            print("\n✓ SUCCESS! Game restarted after game over popup")
            print("  (No high score popup needed)")
        else:
            print("\n✗ Game did not restart")
        return
    
    print("\n✓ High score popup appeared!")
    
    print("\n" + "="*70)
    print("TEST 3: DISMISS HIGH SCORE POPUP")
    print("="*70)
    
    print("\nThe high score popup should be showing now.")
    print("I will press Enter using keyboard events.")
    print()
    input("Press Enter to continue...")
    
    print("\nPressing Enter now...")
    press_enter()
    
    print("\nDid the high score popup close? (y/n)")
    response = input().strip().lower()
    
    if response != 'y':
        print("\n✗ High score popup did NOT close!")
        return
    
    print("\n✓ High score popup closed!")
    
    print("\n" + "="*70)
    print("TEST 4: CHECK GAME RESTART")
    print("="*70)
    
    print("\nWaiting 1 second for game to restart...")
    time.sleep(1.0)
    
    print("\nDid the game restart with 5 balls? (y/n)")
    response = input().strip().lower()
    
    if response == 'y':
        print("\n✓ SUCCESS! Complete popup sequence works:")
        print("  1. Game over popup → Enter → Closed")
        print("  2. High score popup → Enter → Closed")
        print("  3. Game auto-restarted with 5 balls")
    else:
        print("\n✗ Game did not restart correctly")
        print("How many balls are on the board?")
        ball_count = input("Enter number: ").strip()
        print(f"\nGame has {ball_count} balls (expected 5)")
    
    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70)


if __name__ == "__main__":
    main()

