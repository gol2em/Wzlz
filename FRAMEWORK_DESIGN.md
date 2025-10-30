# Game AI Training Framework Design

## Overview

This framework provides a flexible architecture for training AI models to play the ball matching game (五子连珠). It supports two modes of operation:

1. **Simulation Mode**: Fast, efficient training with controlled randomness
2. **Game Client Mode**: Accurate interaction with the actual game for validation

## Architecture

### Core Components

```
┌─────────────────────────────────────────────────────────┐
│                    Your ML Model                        │
│              (to be implemented)                        │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│              GameEnvironment (Abstract)                 │
│  - reset()                                              │
│  - get_state() -> GameState                            │
│  - execute_move(Move) -> MoveResult                    │
│  - get_valid_moves() -> List[Move]                     │
└─────────────────────────────────────────────────────────┘
           │                              │
           ▼                              ▼
┌──────────────────────┐    ┌──────────────────────────┐
│ SimulationEnvironment│    │ GameClientEnvironment    │
│                      │    │                          │
│ - Fast training      │    │ - Real game interaction  │
│ - Controlled random  │    │ - Screen capture         │
│ - Reproducible       │    │ - Mouse automation       │
└──────────────────────┘    └──────────────────────────┘
```

### Data Structures

#### GameState
Represents the complete state of the game:
- `board`: 2D numpy array (rows × cols)
- `next_balls`: Preview of upcoming balls
- `score`: Current score
- `move_count`: Number of moves made
- `game_over`: Game status

#### Position
Represents a board position:
- `row`: Row index
- `col`: Column index

#### Move
Represents a move action:
- `from_pos`: Source position
- `to_pos`: Target position

#### MoveResult
Result of executing a move:
- `success`: Whether move succeeded
- `new_state`: Resulting game state
- `balls_removed`: Positions of removed balls
- `points_earned`: Points from this move
- `new_balls_added`: Newly added balls
- `path`: Path taken by the ball

## Usage Patterns

### Pattern 1: Pure Simulation Training

```python
from game_environment import SimulationEnvironment
from game_state import GameConfig

# Configure game
config = GameConfig(rows=9, cols=9, colors_count=7)

# Create environment
env = SimulationEnvironment(config, seed=42)

# Training loop
for episode in range(1000):
    state = env.reset()
    
    while not env.is_game_over():
        # Your model selects move
        valid_moves = env.get_valid_moves()
        move = your_model.select_move(state, valid_moves)
        
        # Execute move
        result = env.execute_move(move)
        
        # Train your model
        your_model.learn(state, move, result)
```

### Pattern 2: Game Client Interaction

```python
from game_client import GameClientEnvironment
from game_state import GameConfig

# Configure game
config = GameConfig(rows=9, cols=9, colors_count=7)

# Create client environment
env = GameClientEnvironment(config)

# Calibrate (one-time setup)
env.calibrate(
    board_rect=(220, 145, 490, 490),  # x, y, width, height
    cell_size=54  # pixels per cell
)

# Read current state
state = env.get_state()

# Get valid moves
valid_moves = env.get_valid_moves()

# Execute move (will click on game window)
move = your_model.select_move(state, valid_moves)
result = env.execute_move(move)
```

### Pattern 3: Hybrid Approach (Recommended)

```python
# Train on simulation (fast)
sim_env = SimulationEnvironment(config, seed=42)
for episode in range(10000):
    # Fast training...
    pass

# Validate on real game (accurate)
client_env = GameClientEnvironment(config)
client_env.calibrate(...)

# Test trained model on real game
state = client_env.get_state()
moves = client_env.get_valid_moves()
move = trained_model.select_move(state, moves)
result = client_env.execute_move(move)
```

## Key Design Decisions

### 1. Abstract Environment Interface

The `GameEnvironment` abstract class allows seamless switching between simulation and real game:

**Benefits:**
- Same code works for both training and deployment
- Easy to test models in simulation before real game
- Can compare simulation vs reality to improve accuracy

### 2. Immutable State Pattern

`GameState.clone()` creates deep copies:

**Benefits:**
- Safe state exploration (tree search, Monte Carlo)
- No side effects when simulating moves
- Easy to implement undo/redo

### 3. Separate Randomness Control

Simulation environment uses `np.random.RandomState` with seed:

**Benefits:**
- Reproducible training runs
- Deterministic debugging
- Controlled curriculum learning

### 4. Lazy Game Rules Implementation

Matching logic is separated (to be implemented):

**Benefits:**
- Framework works without complete rules
- Easy to experiment with rule variations
- Can implement incrementally

## Implementation Roadmap

### Phase 1: Core Framework ✓
- [x] Game state representation
- [x] Environment interface
- [x] Simulation environment
- [x] Game client interface

### Phase 2: Game Rules (Your Task)
- [ ] Implement `_check_and_remove_matches()` in SimulationEnvironment
  - Detect horizontal matches
  - Detect vertical matches
  - Detect diagonal matches
  - Calculate points
  - Remove matched balls

### Phase 3: Game Client (Your Task)
- [ ] Implement `_parse_board()` for image recognition
  - Detect ball presence in each cell
  - Classify ball colors
  - Handle edge cases (animations, etc.)
- [ ] Implement `_read_score()` using OCR
- [ ] Implement `_read_next_balls()` for preview
- [ ] Implement `auto_calibrate()` for automatic setup

### Phase 4: ML Model (Your Task)
- [ ] Design model architecture
- [ ] Implement state encoding
- [ ] Implement move selection policy
- [ ] Implement learning algorithm
- [ ] Training loop with experience replay

## File Structure

```
.
├── game_state.py           # Core data structures
├── game_environment.py     # Abstract interface + Simulation
├── game_client.py          # Game client interaction
├── example_usage.py        # Usage examples
├── requirements.txt        # Dependencies
└── FRAMEWORK_DESIGN.md     # This file
```

## Extending the Framework

### Adding New Environment Types

```python
class YourCustomEnvironment(GameEnvironment):
    def reset(self) -> GameState:
        # Your implementation
        pass
    
    def get_state(self) -> GameState:
        # Your implementation
        pass
    
    def execute_move(self, move: Move) -> MoveResult:
        # Your implementation
        pass
    
    def get_valid_moves(self, state=None) -> List[Move]:
        # Your implementation
        pass
    
    def is_path_clear(self, from_pos, to_pos, state=None):
        # Your implementation
        pass
```

### Adding State Features

Extend `GameState.to_feature_vector()` to include:
- Distance to nearest ball of each color
- Potential match opportunities
- Board density
- Next balls information

### Adding Move Heuristics

Create helper functions to evaluate moves:
```python
def evaluate_move(state: GameState, move: Move) -> float:
    # Your heuristic
    pass
```

## Performance Considerations

### Simulation Environment
- **Speed**: ~10,000 moves/second (without matching logic)
- **Memory**: ~1KB per state
- **Parallelization**: Easy (independent environments)

### Game Client Environment
- **Speed**: ~1-2 moves/second (limited by game animations)
- **Latency**: 100-500ms per screen capture
- **Accuracy**: Depends on image recognition quality

## Testing Strategy

1. **Unit Tests**: Test individual components
2. **Integration Tests**: Test environment interactions
3. **Simulation Tests**: Verify game rules
4. **Client Tests**: Verify screen reading accuracy
5. **End-to-End Tests**: Full training runs

## Common Pitfalls

1. **Forgetting to clone states**: Always use `state.clone()` before modifications
2. **Not checking move validity**: Always validate moves before execution
3. **Ignoring game client timing**: Add delays for animations
4. **Hardcoding positions**: Use calibration for flexibility
5. **Not handling edge cases**: Empty board, full board, no valid moves

## Next Steps

1. Run `example_usage.py` to see the framework in action
2. Implement the matching logic in `game_environment.py`
3. Calibrate and test the game client
4. Design your ML model
5. Start training!

## Questions to Consider

1. **Randomness**: How random is the game's ball generation?
   - Test by playing many games and analyzing distributions
   - Compare with your simulation

2. **Scoring**: What's the exact scoring formula?
   - 5 balls = ? points
   - 6 balls = ? points
   - Multiple matches in one turn?

3. **Special Rules**: Are there any special mechanics?
   - Power-ups?
   - Obstacles?
   - Time limits?

4. **Optimal Strategy**: What makes a good move?
   - Immediate matches vs. setup for future matches
   - Board control vs. score maximization
   - Risk vs. reward

