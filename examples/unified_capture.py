"""
Unified window capture utility - use this for all capture operations.
This ensures consistent capture across all scripts.
"""

import win32gui
import win32ui
import win32con
from PIL import Image
import time
import ctypes


def capture_game_window(window_title="五子连珠5.2", bring_to_front=True):
    """
    Capture the game window using PrintWindow API.
    This is the UNIFIED capture method - all scripts should use this.
    
    Args:
        window_title: Title of the window to capture
        bring_to_front: Whether to bring window to front before capture
        
    Returns:
        PIL Image or None if failed
    """
    hwnd = win32gui.FindWindow(None, window_title)
    
    if not hwnd:
        print(f"✗ Window '{window_title}' not found!")
        return None
    
    # Bring window to front if requested
    if bring_to_front:
        if win32gui.IsIconic(hwnd):
            win32gui.ShowWindow(hwnd, 9)  # SW_RESTORE
        
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.5)
    
    # Get window dimensions
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    width = right - left
    height = bottom - top
    
    # Capture window
    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()
    
    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
    saveDC.SelectObject(saveBitMap)
    
    # Use PrintWindow to capture the full window with decorations
    # Flag 3 = PW_RENDERFULLCONTENT | PW_CLIENTONLY
    result = ctypes.windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 3)
    
    # Convert to PIL Image
    bmpinfo = saveBitMap.GetInfo()
    bmpstr = saveBitMap.GetBitmapBits(True)
    img = Image.frombuffer(
        'RGB',
        (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
        bmpstr, 'raw', 'BGRX', 0, 1
    )
    
    # Cleanup
    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)
    
    return img


def get_window_rect(window_title="五子连珠5.2"):
    """
    Get the window rectangle (screen coordinates).
    
    Returns:
        (left, top, right, bottom) or None if window not found
    """
    hwnd = win32gui.FindWindow(None, window_title)
    
    if not hwnd:
        return None
    
    return win32gui.GetWindowRect(hwnd)


if __name__ == "__main__":
    # Test the unified capture
    print("Testing unified capture...")
    img = capture_game_window()
    
    if img:
        img.save('test_unified_capture.png')
        print(f"✓ Captured: {img.width}×{img.height}")
        print("✓ Saved to: test_unified_capture.png")
    else:
        print("✗ Capture failed!")

