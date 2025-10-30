# Contributing to Wzlz AI

Thank you for your interest in contributing to Wzlz AI! This document provides guidelines for contributing to the project.

## Development Setup

### Using uv (Recommended)

```bash
# Clone the repository
git clone https://github.com/gol2em/Wzlz.git
cd Wzlz

# Run tests (uv will automatically install dependencies)
uv run python tests/test_framework.py

# Run examples
uv run python examples/example_usage.py
```

### Using pip

```bash
# Clone the repository
git clone https://github.com/gol2em/Wzlz.git
cd Wzlz

# Install in development mode with all dependencies
pip install -e ".[game-client,dev]"

# Run tests
python tests/test_framework.py
```

## Project Structure

```
wzlz_ai/
├── wzlz_ai/           # Main package
│   ├── __init__.py
│   ├── game_state.py
│   ├── game_environment.py
│   └── game_client.py
├── examples/          # Usage examples
├── tests/             # Test suite
├── pyproject.toml     # Project configuration
└── README.md
```

## How to Contribute

### 1. Implement Game Rules

The most important contribution is implementing the matching logic:

**File**: `wzlz_ai/game_environment.py`  
**Function**: `SimulationEnvironment._check_and_remove_matches()`

See `examples/game_rules_template.py` for a template implementation.

### 2. Implement Image Recognition

For game client support:

**File**: `wzlz_ai/game_client.py`  
**Functions**:
- `_parse_board()` - Detect balls from screenshot
- `_read_score()` - Read score using OCR
- `_read_next_balls()` - Read next balls preview
- `auto_calibrate()` - Automatic window detection

### 3. Add ML Models

Create example ML models in `examples/`:
- Random baseline
- Heuristic-based agent
- Deep Q-Network (DQN)
- Policy Gradient
- Monte Carlo Tree Search (MCTS)

### 4. Improve Documentation

- Add more examples
- Improve docstrings
- Add tutorials
- Translate documentation

### 5. Add Tests

Add tests to `tests/`:
- Unit tests for new features
- Integration tests
- Performance benchmarks

## Code Style

This project uses:
- **Black** for code formatting
- **Ruff** for linting

Format your code before committing:

```bash
# With uv
uv run black wzlz_ai/ examples/ tests/
uv run ruff check wzlz_ai/ examples/ tests/

# With pip
black wzlz_ai/ examples/ tests/
ruff check wzlz_ai/ examples/ tests/
```

## Testing

Always run tests before submitting:

```bash
# Run all tests
uv run python tests/test_framework.py

# Or with pytest
uv run pytest tests/
```

## Submitting Changes

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes
4. Run tests to ensure everything works
5. Format your code with Black
6. Commit your changes: `git commit -m "Add your feature"`
7. Push to your fork: `git push origin feature/your-feature-name`
8. Create a Pull Request

## Pull Request Guidelines

- **Clear description**: Explain what your PR does and why
- **Tests**: Add tests for new features
- **Documentation**: Update docs if needed
- **Code quality**: Follow the code style guidelines
- **Small PRs**: Keep PRs focused on a single feature/fix

## Areas for Contribution

### High Priority
- [ ] Implement game matching logic
- [ ] Implement image recognition for game client
- [ ] Add example ML models
- [ ] Improve test coverage

### Medium Priority
- [ ] Add automatic calibration
- [ ] Add performance benchmarks
- [ ] Add visualization tools
- [ ] Add training utilities

### Low Priority
- [ ] Add more game rule variations
- [ ] Add replay system
- [ ] Add web interface
- [ ] Add cloud training support

## Questions?

If you have questions:
1. Check the [README](README.md)
2. Check the [QUICKSTART](QUICKSTART.md)
3. Check the [FRAMEWORK_DESIGN](FRAMEWORK_DESIGN.md)
4. Open an issue on GitHub

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

