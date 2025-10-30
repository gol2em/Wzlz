# Game Reading: Image vs Memory

This document compares image-based and memory-based approaches for reading game state.

## Quick Comparison Table

| Feature | Image Reading | Memory Reading |
|---------|--------------|----------------|
| **Speed** | ~100-200ms | <1ms |
| **Accuracy** | 95-99% | 100% |
| **Setup Time** | 1-2 hours | 1-2 days |
| **Maintenance** | Low | High |
| **Game Updates** | ✓ Still works | ✗ Breaks |
| **Legal/Safe** | ✓ Yes | ⚠ Gray area |
| **Complexity** | Low | High |
| **Background** | ✗ Needs visible window | ✓ Can run hidden |
| **Cross-platform** | ✓ Yes | ✗ Windows only |
| **Learning Value** | High | Medium |

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
# 1. Reverse engineer (complex)
# - Use Cheat Engine or similar
# - Find board array in memory
# - Find score variable
# - Document memory layout

# 2. Implement reader
import ctypes
from ctypes import wintypes

def read_memory(process_handle, address, size):
    buffer = ctypes.create_string_buffer(size)
    ctypes.windll.kernel32.ReadProcessMemory(
        process_handle, address, buffer, size, None
    )
    return buffer.raw

# 3. Parse data
board_data = read_memory(handle, board_address, 81)
board = parse_board_data(board_data)
```

#### Pros
- ✅ **Very fast** - <1ms per read
- ✅ **100% accurate** - direct data access
- ✅ **Background** - game can be minimized
- ✅ **No visual requirements** - works in any state
- ✅ **Efficient** - minimal CPU usage

#### Cons
- ❌ **Complex** - requires reverse engineering
- ❌ **Game-specific** - breaks with updates
- ❌ **Platform-specific** - Windows only (usually)
- ❌ **Legal concerns** - may violate ToS
- ❌ **Anti-cheat** - may be detected
- ❌ **Time-consuming** - days to weeks of work
- ❌ **Maintenance** - needs updates when game updates

#### Best For
- ✓ Real-time performance requirements
- ✓ Fullscreen games
- ✓ When image recognition fails
- ✓ Short-term projects
- ✓ When you have reverse engineering skills

## Recommendation for Your Project

### Use Image Reading Because:

1. **Your Goal**: Validate game rules and train AI
   - Speed: 100-200ms is acceptable for validation
   - You're not playing competitively in real-time

2. **Maintainability**: 
   - Won't break when game updates
   - Easy to fix if something changes

3. **Learning**:
   - Good practice for computer vision
   - Transferable skills to other projects

4. **Time Investment**:
   - 1-2 hours to get working
   - vs 1-2 days for memory reading

5. **Safety**:
   - No legal/ethical concerns
   - No risk of anti-cheat detection

### When to Consider Memory Reading:

Only if you encounter these issues:
- Image recognition accuracy <90%
- Need >10 moves/second
- Game runs fullscreen only
- Have experience with reverse engineering

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

### Memory Reading (Complex)
```python
import ctypes
from ctypes import wintypes

# Find process
process = find_process("wzlz.exe")
handle = open_process(process.pid)

# Read board (example addresses - need to find these)
BOARD_ADDRESS = 0x12345678
board_data = read_memory(handle, BOARD_ADDRESS, 81)

# Parse board
board = np.frombuffer(board_data, dtype=np.uint8).reshape(9, 9)

# Read score
SCORE_ADDRESS = 0x87654321
score_data = read_memory(handle, SCORE_ADDRESS, 4)
score = int.from_bytes(score_data, 'little')
```

## Conclusion

**For your project, start with image reading:**

1. ✅ Faster to implement (hours vs days)
2. ✅ More maintainable (won't break)
3. ✅ Sufficient speed (100-200ms is fine)
4. ✅ Safer and legal
5. ✅ Better learning experience

**Only consider memory reading if:**
- Image reading fails (<90% accuracy)
- You need real-time performance (>10 moves/sec)
- You have reverse engineering experience
- You're willing to maintain it

**Best approach:**
- Use **simulation** for training (fast, controlled)
- Use **image reading** for validation (accurate enough)
- Focus on building great AI, not perfect reading

The goal is to train AI to play the game, not to build the perfect game reader. Image reading is good enough for that purpose!

