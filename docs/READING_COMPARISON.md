# Game Reading: Image vs Memory

This document compares image-based and memory-based approaches for reading game state.

## Quick Comparison Table

| Feature | Image Reading | Memory Reading |
|---------|--------------|----------------|
| **Speed** | ~100-200ms | ~1-5ms |
| **Accuracy** | 95-99% | 100% |
| **Setup Time** | 1-2 hours | 30 min - 2 hours* |
| **Maintenance** | Low | Medium** |
| **Game Updates** | ✓ Still works | ⚠ May break |
| **Legal/Safe** | ✓ Yes | ✓ Yes (standalone) |
| **Complexity** | Low | Medium |
| **Background** | ✗ Needs visible window | ✓ Can run hidden |
| **Cross-platform** | ✓ Yes | ✗ Windows only |
| **Learning Value** | High | High |
| **Implementation** | ✓ Included | ✓ Included |

\* With the new automated exploration tool
\*\* Addresses may need to be rediscovered after game restarts

## Detailed Comparison

### Image-Based Reading

#### How It Works
1. Capture screenshot of game window
2. Divide into grid cells
3. Detect balls using computer vision
4. Read score using OCR
5. Return game state

#### Implementation Steps
```python
# 1. Calibrate (one-time setup)
python examples/setup_game_client.py

# 2. Implement detection
def _parse_board(screenshot):
    for each cell:
        detect ball color
    return board

# 3. Use it
state = game_client.get_state()
```

#### Pros
- ✅ **Easy to implement** - basic CV knowledge sufficient
- ✅ **Robust** - works across game versions
- ✅ **Safe** - no memory manipulation
- ✅ **Educational** - learn computer vision
- ✅ **Debuggable** - can see what AI sees
- ✅ **Portable** - works on any platform

#### Cons
- ❌ **Slower** - 100-200ms per read
- ❌ **Requires visible window** - can't minimize
- ❌ **Resolution dependent** - needs recalibration
- ❌ **Lighting sensitive** - affected by screen settings
- ❌ **Not 100% accurate** - ~95-99% accuracy

#### Best For
- ✓ Validating game rules
- ✓ Testing AI models
- ✓ Learning and experimentation
- ✓ Long-term projects (won't break)
- ✓ When speed isn't critical

### Memory-Based Reading

#### How It Works
1. Find game process in memory
2. Locate data structures (board, score, etc.)
3. Read memory addresses directly
4. Parse binary data
5. Return game state

#### Implementation Steps
```python
# 1. Install dependencies
pip install pymem

# 2. Discover addresses (automated tool)
python examples/explore_memory.py
# - Attach to game process
# - Use screen reader to compare values
# - Find and verify addresses
# - Save to file

# 3. Use memory reader
from wzlz_ai.memory_reader import GameMemoryReader

reader = GameMemoryReader(process_name="wzlz.exe")
reader.attach()
reader.board_address = 0x12AB3450  # From exploration
reader.score_address = 0x12AB3500  # From exploration

# 4. Read game state
state = reader.read_game_state()
```

#### Pros
- ✅ **Very fast** - <1ms per read
- ✅ **100% accurate** - direct data access
- ✅ **Background** - game can be minimized
- ✅ **No visual requirements** - works in any state
- ✅ **Efficient** - minimal CPU usage

#### Cons
- ❌ **Platform-specific** - Windows only
- ❌ **Game-specific** - may break with updates
- ❌ **Address instability** - may need rediscovery after restarts
- ❌ **Initial setup** - requires finding addresses first
- ❌ **Maintenance** - addresses may change with game updates

#### Best For
- ✓ Real-time performance requirements
- ✓ Fullscreen games
- ✓ When image recognition fails
- ✓ Short-term projects
- ✓ When you have reverse engineering skills

## Recommendation for Your Project

### NEW: Both Methods Now Available!

With the new automated memory exploration tool, both methods are now practical:

### Use Image Reading When:

1. **Starting out** - easier to understand and debug
2. **Long-term stability** - won't break with game updates
3. **Learning focus** - good practice for computer vision
4. **Cross-platform** - if you might switch OS

### Use Memory Reading When:

1. **Performance critical** - need 10-100x faster reads
2. **High-frequency training** - reading state thousands of times
3. **Background operation** - want to minimize/hide game window
4. **Accuracy critical** - need 100% reliable reads

### Recommended Approach: Start with Image, Add Memory Later

1. **Week 1**: Set up image reading
   - Get familiar with the framework
   - Validate game rules
   - Build initial AI

2. **Week 2+**: Add memory reading
   - Run `explore_memory.py` to find addresses
   - Use for high-performance training
   - Keep image reading as fallback

3. **Production**: Hybrid approach
   ```python
   # Try memory first, fall back to image
   if memory_reader.attach():
       state = memory_reader.read_game_state()
   else:
       state = image_reader.read_game_state()
   ```

## Hybrid Approach (Recommended)

The best strategy combines both:

### Phase 1: Development (Simulation)
```python
# Use simulation for fast training
sim_env = SimulationEnvironment(config, seed=42)
# Train AI here - millions of games
```

### Phase 2: Validation (Image Reading)
```python
# Use game client to validate rules
game_env = GameClientEnvironment(config)
# Play 100 games, verify scoring matches
```

### Phase 3: Testing (Both)
```python
# Test AI in both environments
sim_score = test_ai_in_simulation(ai_model)
game_score = test_ai_in_game(ai_model)
# Compare results
```

This gives you:
- ✓ Speed of simulation for training
- ✓ Accuracy of real game for validation
- ✓ Confidence that your AI works in both

## Implementation Roadmap

### Week 1: Image Reading Setup
- [ ] Run calibration wizard
- [ ] Implement basic color detection
- [ ] Test reading static boards
- [ ] Verify accuracy >95%

### Week 2: Move Execution
- [ ] Implement mouse clicking
- [ ] Test executing moves
- [ ] Verify state changes correctly

### Week 3: Validation
- [ ] Play 10 games manually
- [ ] Compare with simulation
- [ ] Verify scoring rules match
- [ ] Document any differences

### Week 4: Optimization (Optional)
- [ ] Improve detection accuracy
- [ ] Reduce reading time
- [ ] Add error handling
- [ ] Create automated tests

## Code Examples

### Image Reading (Simple)
```python
from wzlz_ai import GameClientEnvironment, GameConfig

# Setup
config = GameConfig()
env = GameClientEnvironment(config)
env.board_rect = (100, 100, 450, 450)
env.cell_size = (50, 50)

# Read state
state = env.get_state()
print(state)

# Execute move
move = Move(Position(0, 0), Position(0, 1))
result = env.execute_move(move)
```

### Memory Reading (Now Simple!)
```python
from wzlz_ai.memory_reader import GameMemoryReader

# Setup (one-time: run explore_memory.py to find addresses)
reader = GameMemoryReader(process_name="wzlz.exe")
reader.attach()

# Set discovered addresses
reader.board_address = 0x12AB3450
reader.score_address = 0x12AB3500

# Read state (fast!)
state = reader.read_game_state()
print(f"Score: {state.score}")
print(f"Board: {state.board}")
```

## Conclusion

**NEW: You now have both options available!**

### Quick Start Path

1. **Week 1**: Image reading
   - Easy setup and debugging
   - Learn the framework
   - Validate game rules

2. **Week 2**: Add memory reading
   - Run `explore_memory.py` (30 min)
   - Get 10-100x performance boost
   - Use for intensive training

### Recommended Strategy

```python
# Best of both worlds
class HybridGameReader:
    def __init__(self):
        self.memory_reader = GameMemoryReader()
        self.image_reader = GameStateReader()
        self.use_memory = self.memory_reader.attach()

    def read_state(self):
        if self.use_memory:
            state = self.memory_reader.read_game_state()
            if state:
                return state
        # Fallback to image
        return self.image_reader.read_game_state()
```

### Performance Tiers

- **Simulation**: Millions of games/hour (training)
- **Memory Reading**: Thousands of games/hour (validation)
- **Image Reading**: Hundreds of games/hour (testing)

### Getting Started

1. **Install**: `pip install pymem`
2. **Explore**: `python examples/explore_memory.py`
3. **Test**: `python examples/test_memory_reading.py`
4. **Integrate**: Use `GameMemoryReader` in your code

See [MEMORY_READING_GUIDE.md](MEMORY_READING_GUIDE.md) for detailed instructions!

