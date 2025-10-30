# Image Recognition Guide for Game Client

This guide explains how to implement image-based reading for the Wzlz game client.

## Overview

The image-based approach captures screenshots of the game window and uses computer vision to detect:
1. **Ball positions** - which cells contain balls
2. **Ball colors** - what color each ball is
3. **Score** - current game score (OCR)
4. **Next balls** - preview of upcoming balls

## Architecture

```
Game Window → Screenshot → Image Processing → Game State
                ↓
         [Board Area]
                ↓
    ┌───────────┴───────────┐
    ↓                       ↓
[Ball Detection]      [Color Recognition]
    ↓                       ↓
[Position + Color] → GameState object
```

## Step-by-Step Implementation

### Step 1: Calibration

First, you need to calibrate the game client to know where the board is:

```bash
# Run the setup wizard
uv run python examples/setup_game_client.py
```

This will help you:
- Find the game window position
- Measure the board rectangle
- Calculate cell size
- Sample ball colors

### Step 2: Ball Detection Methods

There are several approaches to detect balls:

#### Method 1: Color Matching (Simplest)

**Pros**: Fast, simple, works for solid colors
**Cons**: Sensitive to lighting, shadows, anti-aliasing

```python
def detect_ball_by_color(cell_image, color_samples):
    """Detect ball by matching center pixel color."""
    # Get center pixel
    h, w = cell_image.shape[:2]
    center_color = cell_image[h//2, w//2]
    
    # Find closest color match
    best_match = BallColor.EMPTY
    min_distance = float('inf')
    
    for ball_color, sample_rgb in color_samples.items():
        distance = np.linalg.norm(center_color - sample_rgb)
        if distance < min_distance:
            min_distance = distance
            best_match = ball_color
    
    # Threshold to determine if it's actually a ball
    if min_distance > 50:  # Adjust threshold
        return BallColor.EMPTY
    
    return best_match
```

#### Method 2: Circle Detection (More Robust)

**Pros**: Detects ball shape, less sensitive to color variations
**Cons**: Slower, needs parameter tuning

```python
import cv2

def detect_ball_by_shape(cell_image):
    """Detect ball using circle detection."""
    # Convert to grayscale
    gray = cv2.cvtColor(cell_image, cv2.COLOR_RGB2GRAY)
    
    # Detect circles
    circles = cv2.HoughCircles(
        gray,
        cv2.HOUGH_GRADIENT,
        dp=1,
        minDist=20,
        param1=50,
        param2=30,
        minRadius=5,
        maxRadius=30
    )
    
    if circles is not None:
        # Ball detected, now determine color
        return detect_color_from_circle(cell_image, circles[0])
    
    return BallColor.EMPTY
```

#### Method 3: Template Matching (Most Accurate)

**Pros**: Very accurate, handles variations well
**Cons**: Requires template images for each ball color

```python
def detect_ball_by_template(cell_image, templates):
    """Detect ball using template matching."""
    best_match = BallColor.EMPTY
    best_score = 0.0
    
    for ball_color, template in templates.items():
        # Match template
        result = cv2.matchTemplate(
            cell_image,
            template,
            cv2.TM_CCOEFF_NORMED
        )
        
        _, max_val, _, _ = cv2.minMaxLoc(result)
        
        if max_val > best_score:
            best_score = max_val
            best_match = ball_color
    
    # Threshold
    if best_score < 0.7:  # Adjust threshold
        return BallColor.EMPTY
    
    return best_match
```

#### Method 4: Machine Learning (Most Advanced)

**Pros**: Handles all variations, very accurate
**Cons**: Requires training data and model

```python
def detect_ball_by_ml(cell_image, model):
    """Detect ball using trained CNN classifier."""
    # Preprocess image
    img = cv2.resize(cell_image, (32, 32))
    img = img / 255.0
    img = np.expand_dims(img, axis=0)
    
    # Predict
    predictions = model.predict(img)
    ball_color = np.argmax(predictions)
    confidence = predictions[0][ball_color]
    
    if confidence < 0.8:
        return BallColor.EMPTY
    
    return BallColor(ball_color)
```

### Step 3: Implement _parse_board()

Here's a complete implementation using color matching:

```python
def _parse_board(self, screenshot: np.ndarray) -> np.ndarray:
    """Parse screenshot to detect balls."""
    board = np.zeros((self.config.rows, self.config.cols), dtype=np.int8)
    
    cell_w, cell_h = self.cell_size
    
    for row in range(self.config.rows):
        for col in range(self.config.cols):
            # Extract cell region
            x1 = int(col * cell_w)
            y1 = int(row * cell_h)
            x2 = int((col + 1) * cell_w)
            y2 = int((row + 1) * cell_h)
            
            cell_image = screenshot[y1:y2, x1:x2]
            
            # Detect ball color
            ball_color = self._detect_ball_color(cell_image)
            board[row, col] = ball_color
    
    return board

def _detect_ball_color(self, cell_image: np.ndarray) -> BallColor:
    """Detect ball color in a cell."""
    # Get center region (avoid edges)
    h, w = cell_image.shape[:2]
    center_region = cell_image[
        h//4:3*h//4,
        w//4:3*w//4
    ]
    
    # Calculate average color
    avg_color = np.mean(center_region, axis=(0, 1))
    
    # Match against known colors
    best_match = BallColor.EMPTY
    min_distance = float('inf')
    
    for ball_color, sample_rgb in self.color_samples.items():
        distance = np.linalg.norm(avg_color - sample_rgb)
        if distance < min_distance:
            min_distance = distance
            best_match = ball_color
    
    # Threshold
    if min_distance > 50:
        return BallColor.EMPTY
    
    return best_match
```

### Step 4: Score Reading (OCR)

Use Tesseract OCR to read the score:

```python
import pytesseract

def _read_score(self) -> int:
    """Read score using OCR."""
    if self.score_rect is None:
        return 0
    
    # Capture score area
    x, y, w, h = self.score_rect
    screenshot = ImageGrab.grab(bbox=(x, y, x + w, y + h))
    
    # Preprocess for OCR
    img = np.array(screenshot)
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    
    # Threshold to get black text on white background
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    
    # OCR
    text = pytesseract.image_to_string(
        binary,
        config='--psm 7 digits'  # Single line of digits
    )
    
    # Parse number
    try:
        score = int(''.join(filter(str.isdigit, text)))
        return score
    except:
        return 0
```

## Testing and Validation

### Test 1: Static Board Reading

```python
# Test reading a static board
env = GameClientEnvironment(config)
env.board_rect = (100, 100, 450, 450)
env.cell_size = (50, 50)

state = env.get_state()
print(state)
```

### Test 2: Compare with Simulation

```python
# Play same moves in both environments
sim_env = SimulationEnvironment(config, seed=42)
game_env = GameClientEnvironment(config)

# Reset both
sim_state = sim_env.reset()
game_state = game_env.get_state()

# Compare boards
if np.array_equal(sim_state.board, game_state.board):
    print("✓ Boards match!")
else:
    print("✗ Boards differ!")
    print("Simulation:", sim_state)
    print("Game:", game_state)
```

### Test 3: Execute Move and Verify

```python
# Execute move in game
move = Move(Position(0, 0), Position(0, 1))

# Read state before
state_before = game_env.get_state()

# Execute move (clicks on game)
result = game_env.execute_move(move)

# Read state after
state_after = game_env.get_state()

# Verify move was executed
if state_after.move_count == state_before.move_count + 1:
    print("✓ Move executed successfully!")
else:
    print("✗ Move may have failed")
```

## Troubleshooting

### Issue: Colors not detected correctly

**Solutions:**
- Recalibrate color samples
- Increase color matching threshold
- Use average color instead of center pixel
- Try different color space (HSV instead of RGB)

### Issue: Balls detected in empty cells

**Solutions:**
- Increase detection threshold
- Add shape detection (circles)
- Check for minimum color saturation

### Issue: OCR reading wrong numbers

**Solutions:**
- Improve image preprocessing (threshold, denoise)
- Use different OCR config (--psm parameter)
- Manually verify score area is correct

### Issue: Slow performance

**Solutions:**
- Reduce screenshot resolution
- Cache color samples
- Use faster detection method
- Only read when needed (not every frame)

## Recommended Workflow

1. **Start Simple**: Use color matching first
2. **Calibrate**: Run setup wizard to get accurate positions
3. **Test Static**: Read a static board and verify manually
4. **Test Dynamic**: Execute a few moves and verify
5. **Validate Rules**: Play full games and compare with simulation
6. **Optimize**: If too slow, switch to faster methods

## Next Steps

After implementing image recognition:

1. **Validate Game Rules**: Play games and verify scoring matches your implementation
2. **Collect Data**: Record game states for training
3. **Train AI**: Use the game client to test your trained models
4. **Benchmark**: Compare AI performance in simulation vs real game

## Alternative: Hybrid Approach

For best results, consider a hybrid approach:

- **Training**: Use simulation (fast, controlled)
- **Validation**: Use game client (accurate, real)
- **Testing**: Use both to ensure consistency

This gives you the speed of simulation with the accuracy of the real game!

