# Quick Start Guide

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the examples:
```bash
python example_usage.py
```

## Basic Usage

### 1. Simulation Environment (Recommended for Training)

```python
from game_environment import SimulationEnvironment
from game_state import GameConfig

# Create environment
config = GameConfig(rows=9, cols=9, colors_count=7)
env = SimulationEnvironment(config, seed=42)

# Reset game
state = env.reset()
print(state)  # Shows the board

# Get valid moves
moves = env.get_valid_moves()
print(f"Found {len(moves)} valid moves")

# Execute a move
if moves:
    result = env.execute_move(moves[0])
    if result.success:
        print(f"Score: {result.new_state.score}")
```

### 2. Game Client Environment (For Real Game)

```python
from game_client import GameClientEnvironment
from game_state import GameConfig

# Create environment
config = GameConfig(rows=9, cols=9, colors_count=7)
env = GameClientEnvironment(config)

# Calibrate (measure these values from your game window)
env.calibrate(
    board_rect=(220, 145, 490, 490),  # (x, y, width, height)
    cell_size=54  # pixels per cell
)

# Read game state
state = env.get_state()

# Execute move (will click on game)
from game_state import Position, Move
move = Move(Position(3, 0), Position(7, 0))
result = env.execute_move(move)
```

## What You Need to Implement

### Priority 1: Game Rules (Required for Training)

Edit `game_environment.py`, find `_check_and_remove_matches()`:

```python
def _check_and_remove_matches(self, state: GameState, pos: Position) -> Tuple[List[Position], int]:
    """
    Check for matches around a position and remove them.
    
    TODO: Implement this!
    
    Steps:
    1. Check horizontal line through pos
    2. Check vertical line through pos
    3. Check both diagonals through pos
    4. If any line has >= match_length balls of same color:
       - Add those positions to removed list
       - Calculate points
    5. Remove balls from state
    6. Return (removed_positions, points)
    """
    # Your implementation here
    pass
```

### Priority 2: Image Recognition (Required for Real Game)

Edit `game_client.py`, find `_parse_board()`:

```python
def _parse_board(self, screenshot: np.ndarray) -> np.ndarray:
    """
    Parse screenshot to detect balls.
    
    TODO: Implement this!
    
    Steps:
    1. Divide screenshot into grid cells
    2. For each cell:
       - Check if there's a ball (color detection)
       - If yes, determine which color
       - Map to BallColor enum
    3. Return board array
    """
    # Your implementation here
    pass
```

### Priority 3: ML Model (Your Choice)

Create a new file `model.py`:

```python
class GameAI:
    def select_move(self, state, valid_moves):
        """
        Select best move given current state.
        
        Options:
        - Random (baseline)
        - Heuristic-based
        - Deep Q-Network (DQN)
        - Policy Gradient
        - Monte Carlo Tree Search (MCTS)
        """
        pass
    
    def learn(self, state, move, result):
        """
        Learn from experience.
        """
        pass
```

## Training Workflow

### Step 1: Test Simulation

```python
# Test that simulation works
env = SimulationEnvironment(config, seed=42)
state = env.reset()

for i in range(10):
    moves = env.get_valid_moves()
    if not moves:
        break
    result = env.execute_move(moves[0])
    print(f"Move {i+1}: Score = {result.new_state.score}")
```

### Step 2: Implement Game Rules

Implement `_check_and_remove_matches()` and test:

```python
# Create a test state with a known match
state = GameState.create_empty(9, 9)
# Manually place 5 red balls in a row
for i in range(5):
    state.set_cell(Position(0, i), BallColor.RED)

# Test matching
env = SimulationEnvironment(config)
env._current_state = state
removed, points = env._check_and_remove_matches(state, Position(0, 2))

print(f"Removed {len(removed)} balls")  # Should be 5
print(f"Points: {points}")  # Should be > 0
```

### Step 3: Train Your Model

```python
# Simple training loop
model = YourModel()
env = SimulationEnvironment(config)

for episode in range(1000):
    state = env.reset()
    episode_reward = 0
    
    while not env.is_game_over():
        moves = env.get_valid_moves()
        if not moves:
            break
        
        # Model selects move
        move = model.select_move(state, moves)
        
        # Execute
        result = env.execute_move(move)
        
        # Learn
        reward = result.points_earned
        model.learn(state, move, reward, result.new_state)
        
        episode_reward += reward
        state = result.new_state
    
    print(f"Episode {episode}: Reward = {episode_reward}")
```

### Step 4: Calibrate Game Client

1. Open the game
2. Measure the board position:
   - Take a screenshot
   - Find top-left corner of board (x, y)
   - Measure board width and height
   - Measure one cell size

3. Update calibration:
```python
env = GameClientEnvironment(config)
env.calibrate(
    board_rect=(x, y, width, height),
    cell_size=cell_pixels
)
```

### Step 5: Test on Real Game

```python
# Test reading state
state = env.get_state()
print(state)  # Should match what you see in game

# Test executing move
moves = env.get_valid_moves()
if moves:
    result = env.execute_move(moves[0])
    # Watch the game window - ball should move!
```

## Debugging Tips

### Simulation Not Working?
- Check that game rules are implemented
- Print the board state to visualize
- Use small board (5x5) for testing
- Set seed for reproducibility

### Game Client Not Working?
- Verify calibration values
- Test screen capture separately
- Check that game window is visible
- Disable game animations if possible
- Add longer delays between actions

### Model Not Learning?
- Start with random baseline
- Try simple heuristics first
- Visualize training progress
- Check reward signal
- Verify state representation

## Example: Random Agent

```python
import random
from game_environment import SimulationEnvironment
from game_state import GameConfig

config = GameConfig()
env = SimulationEnvironment(config, seed=42)

# Play one game
state = env.reset()
total_score = 0

while not env.is_game_over():
    moves = env.get_valid_moves()
    if not moves:
        break
    
    # Random move
    move = random.choice(moves)
    result = env.execute_move(move)
    
    if result.success:
        total_score = result.new_state.score
        print(f"Move: {move}, Score: {total_score}")

print(f"Game Over! Final Score: {total_score}")
```

## Next Steps

1. ✅ Run `example_usage.py` to see framework in action
2. ⬜ Implement `_check_and_remove_matches()` for game rules
3. ⬜ Test simulation with your rules
4. ⬜ Build a simple heuristic agent
5. ⬜ Implement image recognition for game client
6. ⬜ Calibrate and test game client
7. ⬜ Design your ML model
8. ⬜ Train on simulation
9. ⬜ Validate on real game
10. ⬜ Iterate and improve!

## Getting Help

Common issues and solutions:

**Q: How do I know if my game rules are correct?**
A: Compare simulation results with real game. Play the same moves in both and check if scores match.

**Q: How do I calibrate the game client?**
A: Use a screenshot tool to measure pixel positions. The board should be a perfect grid.

**Q: What ML algorithm should I use?**
A: Start simple (random, then heuristic), then try DQN or policy gradients.

**Q: How do I make training faster?**
A: Use simulation environment, vectorize operations, use GPU if applicable.

**Q: Can I modify the framework?**
A: Yes! It's designed to be extended. Add new features to GameState, new environment types, etc.

