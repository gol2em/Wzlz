# Game Client Integration

This document describes how the game client integration works and how to use it for training.

## Overview

The `GameClientEnvironment` class provides a bridge between the actual game window and the training framework. It implements the same `GameEnvironment` interface as `SimulationEnvironment`, allowing you to use either environment interchangeably.

## Architecture

```
┌─────────────────────────────────────┐
│     Training Framework              │
│  (Uses GameEnvironment interface)   │
└──────────────┬──────────────────────┘
               │
       ┌───────┴────────┐
       │                │
┌──────▼──────┐  ┌──────▼──────────────┐
│ Simulation  │  │  GameClient         │
│ Environment │  │  Environment        │
└─────────────┘  └──────┬──────────────┘
                        │
                ┌───────┴────────┐
                │                │
         ┌──────▼──────┐  ┌──────▼──────┐
         │   Window    │  │   Mouse     │
         │   Capture   │  │   Control   │
         └─────────────┘  └─────────────┘
```

## Components

### 1. Window Capture (`unified_capture.py`)

Captures the game window using Windows `PrintWindow` API:

```python
from unified_capture import capture_game_window, get_window_rect

# Capture the window
img = capture_game_window("五子连珠5.2", bring_to_front=True)

# Get window position
window_rect = get_window_rect("五子连珠5.2")
```

**Key features:**
- Captures full window including title bar and borders
- Consistent across all scripts
- Works even when window is partially obscured

### 2. Calibration (`game_window_config.json`)

Manual calibration defines the regions of interest:

```json
{
  "window_title": "五子连珠5.2",
  "board_rect": [139, 42, 325, 320],
  "high_score_rect": [26, 13, 65, 18],
  "current_score_rect": [512, 14, 65, 17],
  "next_balls_rect": [249, 5, 106, 33]
}
```

**To calibrate:**
```bash
uv run python examples/manual_calibrate_all.py
```

### 3. Ball Detection

Uses color matching to detect balls:

```python
BALL_COLOR_SAMPLES = {
    BallColor.RED: np.array([50, 50, 200]),      # BGR
    BallColor.GREEN: np.array([50, 200, 50]),
    BallColor.BLUE: np.array([200, 50, 50]),
    BallColor.BROWN: np.array([50, 100, 150]),
    BallColor.MAGENTA: np.array([200, 50, 200]),
    BallColor.YELLOW: np.array([50, 200, 200]),
    BallColor.CYAN: np.array([200, 200, 50]),
    BallColor.EMPTY: np.array([180, 180, 180]),
}
```

**Detection process:**
1. Extract board region from captured image
2. Divide into 9×9 grid
3. Sample center 50% of each cell
4. Calculate average color
5. Find closest match using Euclidean distance

### 4. Mouse Control

Converts board coordinates to screen coordinates and simulates clicks:

```python
def _cell_to_screen_coords(row, col, board_rect, window_rect):
    # Calculate cell center in image coordinates
    cell_center_x = bx + (col + 0.5) * cell_w
    cell_center_y = by + (row + 0.5) * cell_h
    
    # Apply correction for window borders
    correction_x = cell_w * 0.33
    correction_y = cell_h * 1.5
    
    # Convert to screen coordinates
    screen_x = window_left + cell_center_x + correction_x
    screen_y = window_top + cell_center_y + correction_y
```

**Move execution:**
1. Deselect any selected ball (click twice on source)
2. Select the ball (click on source)
3. Wait for bounce animation (0.4s)
4. Click on target cell
5. Wait for move + new balls animation (1.8s)

**Game reset (with popup handling):**
1. Find and dismiss game over popup (Enter via PostMessage)
2. Wait 0.8s
3. Find and dismiss high score popup (Enter via PostMessage)
4. Wait 0.8s for game to auto-restart
5. Read initial state (5 balls)
6. If no popups, press F4 as fallback

## Usage

### Basic Usage

```python
from wzlz_ai.game_state import GameConfig
from wzlz_ai.game_client import GameClientEnvironment

# Create environment
config = GameConfig(show_next_balls=True)
env = GameClientEnvironment(config)

# Reset the game (handles popups automatically, or press F4)
state = env.reset()

# Get valid moves
moves = env.get_valid_moves(state)

# Execute a move
result = env.execute_move(moves[0])

if result.success:
    print(f"Move successful! New state: {result.new_state}")
```

### Training Integration

The `GameClientEnvironment` implements the same interface as `SimulationEnvironment`:

```python
# Can use either environment
env = SimulationEnvironment(config)  # For fast training
# OR
env = GameClientEnvironment(config)  # For validation

# Same interface for both
state = env.reset()
moves = env.get_valid_moves(state)
result = env.execute_move(moves[0])
```

## Testing

### Test Scripts

1. **Test window capture:**
   ```bash
   uv run python examples/capture_window.py
   ```

2. **Test multiple moves:**
   ```bash
   uv run python examples/test_multiple_moves.py
   ```

3. **Test environment integration:**
   ```bash
   uv run python examples/test_game_client_env.py
   ```

4. **Test game reset (F4):**
   ```bash
   uv run python examples/test_game_reset.py
   ```

5. **Test popup handling (game over + high score):**
   ```bash
   uv run python examples/test_popup_auto.py
   # OR
   uv run python examples/test_reset_with_popup.py
   ```

6. **Run unit tests:**
   ```bash
   uv run pytest tests/ -v
   ```

### Verification

All tests pass:
- ✅ 17 unit tests (game rules and framework)
- ✅ Multiple move execution test (5 consecutive moves)
- ✅ Environment integration test

## Popup Handling

### Game Over Sequence

When the board fills up (81 balls), the game shows popups:

1. **Game over popup** appears first
2. **High score popup** appears after (if high score is beaten)
3. After dismissing both popups, game auto-restarts with 5 balls

### How Popup Handling Works

The `reset()` method automatically handles these popups:

```python
# When game is over with popups showing
state = env.reset()
# Popups are automatically dismissed, game restarts
```

**Implementation details:**

1. **Finding popups:** Uses `win32gui.EnumChildWindows()` to find popup windows, or `win32gui.GetForegroundWindow()` if popup is a top-level window

2. **Sending Enter key:** Uses `win32gui.PostMessage()` to send Enter key directly to the popup window
   - **Why PostMessage?** It sends the key event directly to the window without requiring focus
   - This solves the focus problem: when you run a script from terminal, the terminal steals focus
   - PostMessage bypasses this and sends the key directly to the target window

3. **Sequence:**
   ```python
   # Find game over popup
   popup = self._find_popup_window()
   # Send Enter to it (no focus needed)
   win32gui.PostMessage(popup, WM_KEYDOWN, VK_RETURN, 0)
   win32gui.PostMessage(popup, WM_KEYUP, VK_RETURN, 0)
   # Wait for popup to close
   time.sleep(0.8)
   # Repeat for high score popup
   ```

4. **Fallback:** If no popups are found, the method falls back to pressing F4 to manually restart

### Testing Popup Handling

```bash
# Automatic test (no manual input needed)
uv run python examples/test_popup_auto.py

# Reset test (tests the full reset() method)
uv run python examples/test_reset_with_popup.py
```

**Setup for testing:**
1. Play the game until board fills up (81 balls)
2. Wait for both popups to appear
3. Run the test script
4. Script will automatically dismiss popups and verify game restarted

## Limitations

### Current Limitations

1. **Score reading:** Not implemented yet (returns 0)
2. **Next balls reading:** Not implemented yet (returns empty list)
3. **Windows only:** Uses Windows-specific APIs

### Future Improvements

1. **OCR for score:** Use pytesseract to read score from screen
2. **Next balls detection:** Apply color matching to next balls preview
3. **Auto-calibration:** Detect regions automatically using image processing
4. **Cross-platform:** Support macOS and Linux

## Coordinate System

### Important Notes

1. **Calibration coordinates** are relative to the captured image (includes title bar)
2. **Screen coordinates** are absolute positions on the screen
3. **Correction factors** account for window borders and title bar

### Coordinate Conversion

```
Image coordinates (from calibration):
  - Origin: Top-left of captured window image
  - board_rect: [x, y, w, h] relative to image

Screen coordinates (for mouse clicks):
  - Origin: Top-left of screen
  - Calculated: window_pos + image_pos + correction
```

## Troubleshooting

### Mouse clicks in wrong position

1. Check calibration: `uv run python examples/manual_calibrate_all.py`
2. Verify window is not resized
3. Check correction factors in `_cell_to_screen_coords()`

### Ball detection errors

1. Check color samples match your game
2. Verify lighting/theme settings
3. Adjust detection threshold if needed

### Window not found

1. Ensure game is running
2. Check window title matches exactly: "五子连珠5.2"
3. Try bringing window to front manually

## Performance

- **Capture time:** ~150ms per frame
- **Detection time:** ~50ms for full board
- **Move execution:** ~2.2s (including animations)
- **Total cycle:** ~2.4s per move

This is sufficient for validation and demonstration, though too slow for large-scale training (use `SimulationEnvironment` for that).

## Next Steps

1. **Implement score reading** using OCR
2. **Implement next balls detection** using color matching
3. **Create training pipeline** that uses both environments:
   - Train on `SimulationEnvironment` (fast)
   - Validate on `GameClientEnvironment` (real game)
4. **Add logging and metrics** for training progress
5. **Implement AI agent** (e.g., DQN, PPO, or Monte Carlo Tree Search)

