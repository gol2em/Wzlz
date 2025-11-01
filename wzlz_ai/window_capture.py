"""
Windows-specific window capture utilities for the Wzlz game.

This module provides efficient window capture using Win32 APIs.
"""

from typing import Tuple, Optional
import json
from pathlib import Path
import numpy as np

try:
    import win32gui
    import win32ui
    import win32con
    from PIL import Image
    import cv2
except ImportError:
    print("Windows capture dependencies not installed!")
    print("Install with: pip install pywin32 pillow opencv-python")
    raise


class WindowCapture:
    """Captures screenshots from a specific window using Win32 APIs."""
    
    def __init__(self, window_title: str = "五子连珠5.2"):
        """
        Initialize window capture.
        
        Args:
            window_title: Title of the window to capture
        """
        self.window_title = window_title
        self.hwnd: Optional[int] = None
        self.window_rect: Optional[Tuple[int, int, int, int]] = None
        
    def find_window(self) -> bool:
        """
        Find the game window by title.
        
        Returns:
            True if window found
        """
        def callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if self.window_title in title:
                    windows.append(hwnd)
            return True
        
        windows = []
        win32gui.EnumWindows(callback, windows)
        
        if windows:
            self.hwnd = windows[0]
            self.window_rect = win32gui.GetWindowRect(self.hwnd)
            return True
        
        return False
    
    def capture(self) -> Optional[np.ndarray]:
        """
        Capture the current window content.

        Returns:
            Screenshot as numpy array (BGR format for OpenCV), or None if failed
        """
        if not self.hwnd:
            if not self.find_window():
                return None
        
        try:
            # Get window dimensions
            left, top, right, bottom = win32gui.GetWindowRect(self.hwnd)
            width = right - left
            height = bottom - top
            
            # Get window DC
            hwndDC = win32gui.GetWindowDC(self.hwnd)
            mfcDC = win32ui.CreateDCFromHandle(hwndDC)
            saveDC = mfcDC.CreateCompatibleDC()
            
            # Create bitmap
            saveBitMap = win32ui.CreateBitmap()
            saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
            saveDC.SelectObject(saveBitMap)
            
            # Capture
            saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)

            # Convert to numpy array (BGR format to match unified_capture.py)
            bmpinfo = saveBitMap.GetInfo()
            bmpstr = saveBitMap.GetBitmapBits(True)

            img = np.frombuffer(bmpstr, dtype=np.uint8)
            img.shape = (height, width, 4)

            # Convert BGRA to BGR (drop alpha channel)
            img = img[:, :, :3]

            # Cleanup
            win32gui.DeleteObject(saveBitMap.GetHandle())
            saveDC.DeleteDC()
            mfcDC.DeleteDC()
            win32gui.ReleaseDC(self.hwnd, hwndDC)

            return img
            
        except Exception as e:
            print(f"Capture failed: {e}")
            return None
    
    def capture_region(self, rect: Tuple[int, int, int, int]) -> Optional[np.ndarray]:
        """
        Capture a specific region of the window.
        
        Args:
            rect: (x, y, width, height) relative to window
            
        Returns:
            Screenshot of region as numpy array (RGB)
        """
        full_capture = self.capture()
        if full_capture is None:
            return None
        
        x, y, w, h = rect
        return full_capture[y:y+h, x:x+w]


class GameWindowConfig:
    """Configuration for game window regions."""

    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration.

        Args:
            config_file: Path to JSON configuration file
        """
        self.board_rect: Optional[Tuple[int, int, int, int]] = None
        self.high_score_rect: Optional[Tuple[int, int, int, int]] = None  # Top-left
        self.current_score_rect: Optional[Tuple[int, int, int, int]] = None  # Top-right
        self.next_balls_rect: Optional[Tuple[int, int, int, int]] = None
        self.cell_size: Optional[Tuple[float, float]] = None

        if config_file:
            self.load(config_file)
    
    def load(self, config_file: str) -> bool:
        """
        Load configuration from JSON file.

        Args:
            config_file: Path to configuration file

        Returns:
            True if loaded successfully
        """
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.board_rect = tuple(data['board_rect'])
            self.high_score_rect = tuple(data.get('high_score_rect', data.get('score_rect')))
            self.current_score_rect = tuple(data.get('current_score_rect', [0, 0, 0, 0]))
            self.next_balls_rect = tuple(data['next_balls_rect'])
            self.cell_size = tuple(data['cell_size'])

            return True
        except Exception as e:
            print(f"Failed to load config: {e}")
            return False
    
    def save(self, config_file: str) -> bool:
        """
        Save configuration to JSON file.

        Args:
            config_file: Path to configuration file

        Returns:
            True if saved successfully
        """
        try:
            data = {
                'board_rect': self.board_rect,
                'high_score_rect': self.high_score_rect,
                'current_score_rect': self.current_score_rect,
                'next_balls_rect': self.next_balls_rect,
                'cell_size': self.cell_size
            }

            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            return True
        except Exception as e:
            print(f"Failed to save config: {e}")
            return False
    
    def is_valid(self) -> bool:
        """Check if configuration is valid."""
        return all([
            self.board_rect is not None,
            self.high_score_rect is not None,
            self.current_score_rect is not None,
            self.next_balls_rect is not None,
            self.cell_size is not None
        ])


def detect_board_grid(img: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
    """
    Detect the game board grid in an image.
    
    Args:
        img: Screenshot as numpy array (RGB)
        
    Returns:
        Board rectangle (x, y, width, height) or None
    """
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    
    # Edge detection
    edges = cv2.Canny(gray, 50, 150)
    
    # Find contours
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Find the largest square-ish contour
    best_rect = None
    max_area = 0
    
    for contour in contours:
        # Get bounding rectangle
        x, y, w, h = cv2.boundingRect(contour)
        area = w * h
        
        # Check if it's roughly square and large enough
        aspect_ratio = float(w) / h if h > 0 else 0
        if 0.8 < aspect_ratio < 1.2 and area > 10000:
            if area > max_area:
                max_area = area
                best_rect = (x, y, w, h)
    
    return best_rect


def extract_cell_colors(board_img: np.ndarray, rows: int = 9, cols: int = 9) -> np.ndarray:
    """
    Extract average colors from each cell in the board.
    
    Args:
        board_img: Board image as numpy array (RGB)
        rows: Number of rows
        cols: Number of columns
        
    Returns:
        Array of shape (rows, cols, 3) with average RGB colors
    """
    h, w = board_img.shape[:2]
    cell_h = h / rows
    cell_w = w / cols
    
    colors = np.zeros((rows, cols, 3), dtype=np.float32)
    
    for row in range(rows):
        for col in range(cols):
            # Get cell region (center 50% to avoid borders)
            y1 = int(row * cell_h + cell_h * 0.25)
            y2 = int((row + 1) * cell_h - cell_h * 0.25)
            x1 = int(col * cell_w + cell_w * 0.25)
            x2 = int((col + 1) * cell_w - cell_w * 0.25)
            
            cell_region = board_img[y1:y2, x1:x2]
            
            # Calculate average color
            avg_color = np.mean(cell_region, axis=(0, 1))
            colors[row, col] = avg_color
    
    return colors

