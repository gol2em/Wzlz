"""
Simple script to capture the game window.
Uses the unified capture method to ensure consistency.
"""

from unified_capture import capture_game_window


if __name__ == "__main__":
    window_title = "五子连珠5.2"
    
    print("="*70)
    print("CAPTURE GAME WINDOW")
    print("="*70)
    print(f"\nCapturing window: {window_title}")
    
    img = capture_game_window(window_title, bring_to_front=True)
    
    if img:
        img.save('game_screenshot.png')
        print(f"\n✓ Screenshot saved: game_screenshot.png")
        print(f"  Size: {img.width}×{img.height}")
    else:
        print("\n✗ Failed to capture window!")
        print("Make sure the game is running.")

