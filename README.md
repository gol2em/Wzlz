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
├── wzlz_ai/                # Main package
│   ├── __init__.py
│   ├── game_state.py       # Core data structures
│   ├── game_environment.py # Simulation environment
│   └── game_client.py      # Game client interface
├── examples/               # Usage examples
│   ├── example_usage.py
│   └── game_rules_template.py
├── tests/                  # Test suite
│   └── test_framework.py
├── pyproject.toml          # Project configuration
├── README.md               # This file
├── QUICKSTART.md          # Quick start guide
└── FRAMEWORK_DESIGN.md    # Detailed design documentation
```

## 🚀 Quick Start

### Installation

#### Using uv (Recommended)

```bash
# Clone the repository
git clone https://github.com/gol2em/Wzlz.git
cd Wzlz

# Run tests (uv will automatically install dependencies)
uv run python tests/test_framework.py
```

#### Using pip

```bash
# Clone the repository
git clone https://github.com/gol2em/Wzlz.git
cd Wzlz

# Install the package
pip install -e .

# Or with game client support
pip install -e ".[game-client]"

# Run tests
python tests/test_framework.py
```

You should see:
```
============================================================
ALL TESTS PASSED ✓
============================================================
```

### Basic Usage

```python
from wzlz_ai import SimulationEnvironment, GameConfig

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

### See More Examples

```bash
# With uv
uv run python examples/example_usage.py

# With pip
python examples/example_usage.py
```

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Step-by-step guide to get started
- **[FRAMEWORK_DESIGN.md](FRAMEWORK_DESIGN.md)** - Detailed architecture and design decisions

## 🎮 Game Client Integration

The framework now includes full integration with the actual game window!

### Setup

1. **Install dependencies:**
   ```bash
   uv pip install pywin32 opencv-python pillow
   ```

2. **Calibrate the game window:**
   ```bash
   uv run python examples/manual_calibrate_all.py
   ```
   This creates `game_window_config.json` with the board and UI regions.

3. **Use the GameClientEnvironment:**
   ```python
   from wzlz_ai import GameClientEnvironment, GameConfig

   config = GameConfig(show_next_balls=True)
   env = GameClientEnvironment(config)

   # Reset the game (press F4)
   state = env.reset()

   # Get valid moves
   moves = env.get_valid_moves(state)

   # Execute a move (will click on game window)
   result = env.execute_move(moves[0])
   ```

### Test Scripts

```bash
# Test window capture
uv run python examples/capture_window.py

# Test multiple moves
uv run python examples/test_multiple_moves.py

# Test environment integration
uv run python examples/test_game_client_env.py

# Test game reset (F4)
uv run python examples/test_game_reset.py

# Play a full game
uv run python examples/play_full_game.py
```

### Features

✅ **Window capture** - Captures game window using Windows API
✅ **Ball detection** - Detects balls using color matching
✅ **Mouse control** - Simulates clicks to make moves
✅ **Game reset** - Presses F4 to restart the game
✅ **Full game loop** - Can play complete games until game over

See [docs/GAME_CLIENT_INTEGRATION.md](docs/GAME_CLIENT_INTEGRATION.md) for detailed documentation.

## ✅ Current Status

**Complete:**
- ✅ Core game state and rules (17/17 tests passing)
- ✅ Simulation environment (fast training)
- ✅ Game client environment (real game interaction)
- ✅ Window capture and calibration
- ✅ Ball detection using color matching
- ✅ Mouse control for moves
- ✅ Game reset (F4)
- ✅ Full game loop support

**In Progress:**
- 🚧 Score reading from screen (OCR)
- 🚧 Next balls preview detection
- 🚧 AI agent implementation

## 🤖 Next Steps: AI Training

Create your own AI agent to play the game. Options:
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

