"""
Unified window capture module for capturing game windows using Win32 API.

This module provides consistent window capture functionality across all scripts.
"""

import win32gui
import win32ui
import win32con
from ctypes import windll
from PIL import Image
import numpy as np


def get_window_rect(window_title: str):
    """
    Get the window rectangle (position and size).
    
    Args:
        window_title: Title of the window to find
        
    Returns:
        Tuple of (left, top, right, bottom) or None if window not found
    """
    hwnd = win32gui.FindWindow(None, window_title)
    if not hwnd:
        return None
    
    return win32gui.GetWindowRect(hwnd)


def capture_game_window(window_title: str, bring_to_front: bool = False):
    """
    Capture a game window using Win32 API.
    
    Args:
        window_title: Title of the window to capture
        bring_to_front: Whether to bring window to front before capturing
        
    Returns:
        numpy array (BGR format) of the captured window, or None if failed
    """
    # Find the window
    hwnd = win32gui.FindWindow(None, window_title)
    if not hwnd:
        print(f"Window '{window_title}' not found")
        return None
    
    # Bring to front if requested
    if bring_to_front:
        try:
            win32gui.SetForegroundWindow(hwnd)
        except:
            pass  # May fail if window is minimized or permissions issue
    
    # Get window dimensions
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    width = right - left
    height = bottom - top
    
    # Get window device context
    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()
    
    # Create bitmap
    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
    saveDC.SelectObject(saveBitMap)
    
    # Capture the window
    result = windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 3)
    
    if result == 0:
        # PrintWindow failed, try BitBlt
        saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)
    
    # Convert to numpy array
    bmpinfo = saveBitMap.GetInfo()
    bmpstr = saveBitMap.GetBitmapBits(True)
    
    img = np.frombuffer(bmpstr, dtype=np.uint8)
    img.shape = (height, width, 4)
    
    # Convert BGRA to BGR
    img = img[:, :, :3]
    
    # Clean up
    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)
    
    return img


def capture_window_region(window_title: str, region: tuple, bring_to_front: bool = False):
    """
    Capture a specific region of a window.
    
    Args:
        window_title: Title of the window to capture
        region: Tuple of (x, y, width, height) relative to window
        bring_to_front: Whether to bring window to front before capturing
        
    Returns:
        numpy array (BGR format) of the captured region, or None if failed
    """
    # Capture full window
    img = capture_game_window(window_title, bring_to_front)
    if img is None:
        return None
    
    # Extract region
    x, y, w, h = region
    return img[y:y+h, x:x+w]


def find_window(window_title: str):
    """
    Check if a window exists.
    
    Args:
        window_title: Title of the window to find
        
    Returns:
        True if window exists, False otherwise
    """
    hwnd = win32gui.FindWindow(None, window_title)
    return hwnd != 0


def list_windows():
    """
    List all visible windows.
    
    Returns:
        List of window titles
    """
    windows = []
    
    def callback(hwnd, extra):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title:
                windows.append(title)
    
    win32gui.EnumWindows(callback, None)
    return windows


if __name__ == "__main__":
    # Test the module
    print("Testing unified_capture module...")
    
    # List all windows
    print("\nAvailable windows:")
    for i, title in enumerate(list_windows()[:10], 1):
        print(f"  {i}. {title}")
    
    # Try to capture a specific window
    window_title = "五子连珠5.2"
    print(f"\nTrying to capture: {window_title}")
    
    if find_window(window_title):
        print(f"✓ Window found")
        
        rect = get_window_rect(window_title)
        if rect:
            print(f"  Position: ({rect[0]}, {rect[1]})")
            print(f"  Size: {rect[2]-rect[0]}×{rect[3]-rect[1]}")
        
        img = capture_game_window(window_title)
        if img is not None:
            print(f"✓ Captured: {img.shape[1]}×{img.shape[0]} pixels")
        else:
            print("✗ Capture failed")
    else:
        print(f"✗ Window not found")

