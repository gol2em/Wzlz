"""
Test popup detection.

This will help us understand if popups are being detected correctly.
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
    print("POPUP DETECTION TEST")
    print("="*70)
    print("\nThis will check if popups are detected correctly.")
    print()
    print("Test 1: No popup (normal game)")
    print("  Make sure the game is running normally (no popups)")
    print()
    
    input("Press Enter when game is running normally...")
    
    # Create environment
    config = GameConfig(show_next_balls=True)
    env = GameClientEnvironment(config)
    
    if not env.is_calibrated:
        print("\n✗ Game client not calibrated!")
        return
    
    print("\nChecking for popup...")
    popup = env._find_popup_window()
    
    if popup:
        print(f"  ⚠ Popup detected (handle: {popup})")
        import win32gui
        try:
            title = win32gui.GetWindowText(popup)
            class_name = win32gui.GetClassName(popup)
            rect = win32gui.GetWindowRect(popup)
            width = rect[2] - rect[0]
            height = rect[3] - rect[1]
            print(f"  Title: '{title}'")
            print(f"  Class: {class_name}")
            print(f"  Size: {width}x{height}")
        except:
            pass
    else:
        print("  ✓ No popup detected (correct!)")
    
    print("\n" + "="*70)
    print("Test 2: With popup (game over)")
    print("  Play until game over and let BOTH popups appear")
    print()
    
    input("Press Enter when both popups are showing...")
    
    print("\nChecking for popup...")
    popup = env._find_popup_window()
    
    if popup:
        print(f"  ✓ Popup detected (handle: {popup})")
        import win32gui
        try:
            title = win32gui.GetWindowText(popup)
            class_name = win32gui.GetClassName(popup)
            rect = win32gui.GetWindowRect(popup)
            width = rect[2] - rect[0]
            height = rect[3] - rect[1]
            print(f"  Title: '{title}'")
            print(f"  Class: {class_name}")
            print(f"  Size: {width}x{height}")
        except:
            pass
        
        print("\nAttempting to dismiss popup...")
        env._send_enter_to_window(popup)
        print("  ✓ Enter sent to first popup")
        
        time.sleep(0.8)
        
        print("\nChecking for second popup...")
        popup2 = env._find_popup_window()
        
        if popup2:
            print(f"  ✓ Second popup detected (handle: {popup2})")
            try:
                title = win32gui.GetWindowText(popup2)
                class_name = win32gui.GetClassName(popup2)
                rect = win32gui.GetWindowRect(popup2)
                width = rect[2] - rect[0]
                height = rect[3] - rect[1]
                print(f"  Title: '{title}'")
                print(f"  Class: {class_name}")
                print(f"  Size: {width}x{height}")
            except:
                pass
            
            print("\nAttempting to dismiss second popup...")
            env._send_enter_to_window(popup2)
            print("  ✓ Enter sent to second popup")
            
            time.sleep(1.0)
            
            print("\nChecking game state...")
            state = env.get_state()
            ball_count = sum(1 for row in range(9) for col in range(9) if state.board[row, col] != 0)
            print(f"  Balls: {ball_count}")
            
            if ball_count == 5:
                print("\n✓ SUCCESS! Game restarted with 5 balls")
            else:
                print(f"\n⚠ Game has {ball_count} balls (expected 5)")
        else:
            print("  ⚠ No second popup detected")
    else:
        print("  ✗ No popup detected (should have detected it!)")
    
    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70)


if __name__ == "__main__":
    main()

