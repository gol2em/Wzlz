# Game State Extraction Guide

This guide explains how to extract complete game state from the Wzlz game window.

## Overview

The game state extraction system can read all visible information from the game window:

| Information | Location | Method |
|-------------|----------|--------|
| **Board state** | Center (9×9 grid) | Color matching |
| **Current score** | Top-right | OCR (Tesseract) |
| **High score** | Top-left | OCR (Tesseract) |
| **Next balls** | Top-center | Color matching |

## Quick Start

### 1. Calibrate Window (One-time)

```bash
python examples/calibrate_game_window.py
```

This will:
- Find the game window
- Detect board position
- Identify score regions (high score and current score)
- Identify next balls region
- Save configuration to `game_window_config.json`

### 2. Read Game State

```python
from wzlz_ai import GameStateReader

# Initialize reader
reader = GameStateReader('game_window_config.json')

# Read complete game state
state = reader.read_game_state()

# Access state information
print(state)  # Board visualization
print(f"Current score: {state.score}")
print(f"High score: {reader.read_high_score()}")
print(f"Next balls: {state.next_balls}")
```

### 3. Test Extraction

```bash
python examples/read_game_state.py
```

This will display:
- Complete board state
- Ball counts by color
- Current score
- High score
- Next balls preview
- Game over status

## Architecture

```
Game Window
    ↓
[WindowCapture] - Win32 API capture
    ↓
[GameWindowConfig] - Region definitions
    ↓
[GameStateReader] - High-level extraction
    ↓
GameState object
```

## Components

### 1. WindowCapture

Low-level window capture using Win32 API.

```python
from wzlz_ai import WindowCapture

capture = WindowCapture("五子连珠5.2")
capture.find_window()

# Capture full window
screenshot = capture.capture()

# Capture specific region
board_img = capture.capture_region((x, y, w, h))
```

### 2. GameWindowConfig

Configuration for window regions.

```python
from wzlz_ai import GameWindowConfig

config = GameWindowConfig('game_window_config.json')

print(config.board_rect)          # (x, y, w, h)
print(config.high_score_rect)     # Top-left
print(config.current_score_rect)  # Top-right
print(config.next_balls_rect)     # Top-center
print(config.cell_size)           # (width, height)
```

### 3. GameStateReader

High-level game state extraction.

```python
from wzlz_ai import GameStateReader

reader = GameStateReader('game_window_config.json')

# Read complete state
state = reader.read_game_state()

# Read individual components
board = reader.read_board()
current_score = reader.read_current_score()
high_score = reader.read_high_score()
next_balls = reader.read_next_balls()
```

## Configuration File Format

**game_window_config.json:**

```json
{
  "window_title": "五子连珠5.2",
  "window_rect": [100, 100, 800, 600],
  "board_rect": [335, 260, 350, 350],
  "high_score_rect": [50, 95, 100, 30],
  "current_score_rect": [680, 95, 100, 30],
  "next_balls_rect": [400, 90, 120, 40],
  "cell_size": [38.9, 38.9]
}
```

**Field descriptions:**
- `window_title`: Title of the game window
- `window_rect`: Window position and size (for reference)
- `board_rect`: Board region (x, y, width, height)
- `high_score_rect`: High score region (top-left)
- `current_score_rect`: Current score region (top-right)
- `next_balls_rect`: Next balls preview region (top-center)
- `cell_size`: Size of each cell in pixels

## Extracted Game State

The `GameState` object contains:

```python
class GameState:
    board: np.ndarray          # 9×9 array of BallColor
    score: int                 # Current score
    next_balls: List[BallColor]  # Next 3 balls (or empty)
    config: GameConfig         # Game configuration
```

**Example:**

```python
state = reader.read_game_state()

# Board state
print(state.board[0, 0])  # BallColor.RED
print(state.board.shape)  # (9, 9)

# Score
print(state.score)  # 150

# Next balls
print(state.next_balls)  # [BallColor.RED, BallColor.BLUE, BallColor.GREEN]

# Game status
print(state.is_game_over())  # False
```

## Ball Color Detection

The system uses **color matching** to detect balls:

1. Extract average color from each cell (center 50%)
2. Calculate Euclidean distance to known ball colors
3. Choose closest match
4. If distance > threshold, consider empty

**Default color samples:**

```python
DEFAULT_BALL_COLOR_SAMPLES = {
    BallColor.RED: np.array([200, 50, 50]),
    BallColor.GREEN: np.array([50, 200, 50]),
    BallColor.BLUE: np.array([50, 50, 200]),
    BallColor.BROWN: np.array([150, 100, 50]),
    BallColor.MAGENTA: np.array([200, 50, 200]),
    BallColor.YELLOW: np.array([200, 200, 50]),
    BallColor.CYAN: np.array([50, 200, 200]),
    BallColor.EMPTY: np.array([180, 180, 180]),
}
```

**Calibrating colors:**

```python
# Option 1: Set custom samples
reader.set_color_samples({
    BallColor.RED: np.array([210, 45, 45]),
    # ... other colors
})

# Option 2: Calibrate from known board
calibrated = reader.calibrate_colors(
    board_img,
    known_positions={
        (0, 0): BallColor.RED,
        (1, 1): BallColor.BLUE,
        # ... other known positions
    }
)
reader.set_color_samples(calibrated)
```

## Score Reading (OCR)

The system uses **Tesseract OCR** to read scores:

1. Capture score region
2. Convert to grayscale
3. Apply binary threshold
4. Run OCR with digit-only mode
5. Extract numeric value

**Requirements:**
- Install pytesseract: `pip install pytesseract`
- Install Tesseract: https://github.com/UB-Mannheim/tesseract/wiki

**If OCR fails:**
- Returns 0
- Check Tesseract is installed
- Verify score region is correct
- Try adjusting threshold values

## Performance

| Operation | Time | Notes |
|-----------|------|-------|
| Window capture | 10-20ms | Win32 API |
| Board parsing | 5-10ms | Color matching |
| Score OCR (each) | 50-100ms | Tesseract |
| Next balls | 1-2ms | Color matching |
| **Total** | **~150ms** | Acceptable for validation |

## Usage Examples

### Example 1: Read and Display State

```python
from wzlz_ai import GameStateReader

reader = GameStateReader()
state = reader.read_game_state()

print(state)  # Visual board
print(f"Score: {state.score}")
print(f"High score: {reader.read_high_score()}")
```

### Example 2: Monitor Game Progress

```python
import time
from wzlz_ai import GameStateReader

reader = GameStateReader()

while True:
    state = reader.read_game_state()
    if state:
        print(f"Score: {state.score}, Balls: {np.sum(state.board != 0)}")
    time.sleep(1)  # Update every second
```

### Example 3: Validate Game Rules

```python
from wzlz_ai import GameStateReader, SimulationEnvironment

reader = GameStateReader()
sim_env = SimulationEnvironment()

# Read initial state from game
real_state = reader.read_game_state()

# Set simulation to match
sim_env.state = real_state.clone()

# Execute move in both
move = Move(Position(0, 0), Position(0, 1))

real_result = execute_move_in_game(move)  # Click in game
sim_result = sim_env.execute_move(move)

# Compare results
assert real_result.score_gained == sim_result.score_gained
```

### Example 4: Collect Training Data

```python
from wzlz_ai import GameStateReader
import time

reader = GameStateReader()
training_data = []

while True:
    state = reader.read_game_state()
    if state:
        # Record state
        training_data.append({
            'board': state.board.copy(),
            'score': state.score,
            'timestamp': time.time()
        })
    
    time.sleep(0.5)
```

## Troubleshooting

### Issue: Window not found

**Solution:**
- Ensure game is running
- Check window title matches exactly
- Try `win32gui.EnumWindows()` to list all windows

### Issue: Wrong colors detected

**Solution:**
- Calibrate color samples using actual game colors
- Adjust color threshold: `reader.set_color_threshold(100.0)`
- Check lighting/screen settings

### Issue: OCR reading wrong scores

**Solution:**
- Verify score regions are correct
- Check Tesseract is installed
- Try adjusting preprocessing thresholds
- Use template matching instead

### Issue: Next balls not detected

**Solution:**
- Check game mode (some modes don't show next balls)
- Verify next_balls_rect is correct
- Calibrate colors for next balls region

## Best Practices

1. **Calibrate once** - Save configuration and reuse
2. **Validate detection** - Compare with known states
3. **Handle errors** - Window might close, minimize, etc.
4. **Use appropriate timing** - Don't capture too frequently
5. **Test thoroughly** - Try different game states

## Integration with Game Client

After extracting game state, you can:

1. **Validate game rules** - Compare with simulation
2. **Train AI models** - Use real game data
3. **Test strategies** - Execute moves and observe results
4. **Collect statistics** - Track performance over time

## Next Steps

1. ✅ Run calibration: `python examples/calibrate_game_window.py`
2. ✅ Test extraction: `python examples/read_game_state.py`
3. ✅ Calibrate colors if needed
4. ⏭️ Integrate with GameClientEnvironment
5. ⏭️ Validate game rules with real game
6. ⏭️ Execute moves and verify behavior

The game state extraction system is ready to use! 🎉

