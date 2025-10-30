# Ball Matching Game AI Framework

A flexible framework for training AI models to play the ball matching game (五子连珠5.2). Supports both fast simulation-based training and accurate game client interaction.

## 🎯 Features

- **Dual Environment Support**
  - 🚀 **Simulation Mode**: Fast training with controlled randomness (~10,000 moves/sec)
  - 🎮 **Game Client Mode**: Interact with actual game for validation (~1-2 moves/sec)

- **Clean Architecture**
  - Abstract interface for easy switching between environments
  - Immutable state pattern for safe exploration
  - Reproducible training with seed control

- **ML-Ready**
  - Feature vector extraction for neural networks
  - Support for any RL algorithm (DQN, Policy Gradient, MCTS, etc.)
  - Easy integration with PyTorch, TensorFlow, etc.

## 📁 Project Structure

```
.
├── game_state.py           # Core data structures (GameState, Move, Position, etc.)
├── game_environment.py     # Abstract interface + SimulationEnvironment
├── game_client.py          # GameClientEnvironment for real game interaction
├── example_usage.py        # Comprehensive usage examples
├── test_framework.py       # Framework tests (run this first!)
├── requirements.txt        # Python dependencies
├── QUICKSTART.md          # Quick start guide
├── FRAMEWORK_DESIGN.md    # Detailed design documentation
└── README.md              # This file
```

## 🚀 Quick Start

### 1. Test the Framework

```bash
python test_framework.py
```

You should see:
```
============================================================
ALL TESTS PASSED ✓
============================================================
```

### 2. Try Simulation Training

```python
from game_environment import SimulationEnvironment
from game_state import GameConfig

# Create environment
config = GameConfig(rows=9, cols=9, colors_count=7)
env = SimulationEnvironment(config, seed=42)

# Play a game
state = env.reset()
print(state)  # Visualize the board

# Get valid moves
moves = env.get_valid_moves()
print(f"Found {len(moves)} valid moves")

# Execute a move
result = env.execute_move(moves[0])
print(f"Score: {result.new_state.score}")
```

### 3. Install Full Dependencies (for Game Client)

```bash
pip install -r requirements.txt
```

### 4. See More Examples

```bash
python example_usage.py
```

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Step-by-step guide to get started
- **[FRAMEWORK_DESIGN.md](FRAMEWORK_DESIGN.md)** - Detailed architecture and design decisions

## 🎮 Game Client Setup

To interact with the actual game:

1. Open the game (五子连珠5.2)
2. Measure the board position and cell size
3. Calibrate the client:

```python
from game_client import GameClientEnvironment
from game_state import GameConfig

config = GameConfig()
env = GameClientEnvironment(config)

# Calibrate with your measurements
env.calibrate(
    board_rect=(220, 145, 490, 490),  # (x, y, width, height)
    cell_size=54  # pixels per cell
)

# Read game state
state = env.get_state()

# Execute moves (will click on game window)
moves = env.get_valid_moves()
result = env.execute_move(moves[0])
```

## 🔧 What You Need to Implement

### Priority 1: Game Rules ⚠️

The matching logic is not yet implemented. You need to complete:

**File**: `game_environment.py`  
**Function**: `SimulationEnvironment._check_and_remove_matches()`

This function should:
1. Check for horizontal, vertical, and diagonal matches
2. Remove matched balls (5+ in a row)
3. Calculate and return points

### Priority 2: Image Recognition (for Game Client)

**File**: `game_client.py`  
**Functions**:
- `_parse_board()` - Detect balls from screenshot
- `_read_score()` - Read score using OCR
- `_read_next_balls()` - Read next balls preview

### Priority 3: Your ML Model

Create your own model to select moves. Options:
- Random baseline
- Heuristic-based
- Deep Q-Network (DQN)
- Policy Gradient
- Monte Carlo Tree Search (MCTS)

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│         Your ML Model               │
│    (select_move, learn)             │
└─────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│      GameEnvironment (Abstract)     │
│  - reset()                          │
│  - get_state() -> GameState         │
│  - execute_move(Move) -> MoveResult │
│  - get_valid_moves() -> List[Move]  │
└─────────────────────────────────────┘
         │                    │
         ▼                    ▼
┌──────────────────┐  ┌──────────────────┐
│ Simulation       │  │ GameClient       │
│ Environment      │  │ Environment      │
│                  │  │                  │
│ • Fast           │  │ • Accurate       │
│ • Reproducible   │  │ • Real game      │
│ • Training       │  │ • Validation     │
└──────────────────┘  └──────────────────┘
```

## 💡 Usage Patterns

### Pattern 1: Pure Simulation (Fastest)

```python
env = SimulationEnvironment(config, seed=42)

for episode in range(1000):
    state = env.reset()
    while not env.is_game_over():
        moves = env.get_valid_moves()
        move = your_model.select_move(state, moves)
        result = env.execute_move(move)
        your_model.learn(state, move, result)
```

### Pattern 2: Hybrid (Recommended)

```python
# Train on simulation (fast)
sim_env = SimulationEnvironment(config)
# ... train your model ...

# Validate on real game (accurate)
client_env = GameClientEnvironment(config)
client_env.calibrate(...)
# ... test your model on real game ...
```

## 🧪 Testing

Run the test suite:

```bash
python test_framework.py
```

Tests cover:
- ✅ GameState creation and manipulation
- ✅ SimulationEnvironment functionality
- ✅ Move execution
- ✅ State representation
- ✅ Reproducibility
- ✅ Game loop

## 📊 Performance

| Environment | Speed | Accuracy | Use Case |
|------------|-------|----------|----------|
| Simulation | ~10,000 moves/sec | Depends on rules | Training |
| Game Client | ~1-2 moves/sec | 100% (real game) | Validation |

## 🎯 Roadmap

- [x] Core framework
- [x] Simulation environment
- [x] Game client interface
- [x] Documentation
- [ ] Game matching logic (your task)
- [ ] Image recognition (your task)
- [ ] Example ML models (your task)

## 🤝 Contributing

This is your project! Feel free to:
- Modify the framework to suit your needs
- Add new environment types
- Implement different game rules
- Experiment with ML algorithms

## 📝 License

This framework is provided as-is for your use.

## 🆘 Troubleshooting

**Q: Tests fail with import errors?**  
A: Make sure you're in the project directory and Python can find the modules.

**Q: Game client not working?**  
A: First implement the image recognition functions, then calibrate carefully.

**Q: How do I know if my game rules are correct?**  
A: Compare simulation results with the real game. Play identical moves in both.

**Q: What ML algorithm should I use?**  
A: Start with random/heuristic baselines, then try DQN or policy gradients.

## 📖 Further Reading

- See `QUICKSTART.md` for step-by-step instructions
- See `FRAMEWORK_DESIGN.md` for architecture details
- See `example_usage.py` for code examples
- Run `test_framework.py` to verify everything works

---

**Ready to train your AI?** Start with `python test_framework.py` and then check out `QUICKSTART.md`!

