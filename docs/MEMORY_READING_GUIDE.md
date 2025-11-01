# Memory Reading Guide

This guide explains how to read the Wzlz game state directly from process memory, which is more reliable than screen capture and doesn't depend on screen resolution or window position.

## Overview

Memory reading works by:
1. Attaching to the game process
2. Scanning memory for known values (board state, score, etc.)
3. Finding stable memory addresses where game state is stored
4. Reading from those addresses in real-time

## Prerequisites

Install the required dependency:

```bash
pip install pymem
```

Or if using the project's optional dependencies:

```bash
pip install -e ".[game-client]"
pip install pymem
```

## Step 1: Find Memory Addresses

The first step is to discover where the game stores its state in memory. Use the interactive exploration tool:

```bash
python examples/explore_memory.py
```

### Interactive Process

1. **Start the Wzlz game** before running the script

2. **Attach to process**: The script will attempt to attach to the game process (default name: `wzlz.exe`)

3. **Use screen reader for comparison** (recommended): 
   - Answer 'y' when prompted
   - This will use your existing screen capture setup to compare with memory values
   - Make sure your `game_window_config.json` is properly calibrated

4. **Find board address**:
   - The script reads the current board from screen
   - Searches memory for matching 9x9 grid pattern
   - Shows potential addresses found

5. **Find score address**:
   - The script reads the current score from screen
   - Searches memory for matching score value
   - May find many candidates initially

6. **Filter score candidates** (if needed):
   - Make a move in the game that changes the score
   - Press Enter to re-scan
   - Candidates that don't match the new score are eliminated
   - Repeat until only a few candidates remain

7. **Verify addresses**:
   - The script will verify that memory values match screen values
   - Confirmed addresses are saved

8. **Save results**:
   - Addresses are saved to `memory_addresses.txt`
   - You can use these addresses for future sessions

### Example Session

```
=== Finding Board Address ===
Reading current board state from screen...
✓ Board read from screen:
  0 1 2 3 4 5 6 7 8
0 · · R · · · · · ·
1 · G · · · · · · ·
2 · · · · B · · · ·
...

Searching memory for matching board pattern...
✓ Found 1 potential board address(es):
  [0] 0x12AB3450

✓ Board address confirmed: 0x12AB3450

=== Finding Score Address ===
Reading current score from screen...
✓ Score read from screen: 42

Searching memory for matching score value...
✓ Found 234 potential score address(es)
  Too many candidates (234). Need to filter...

Filter score candidates? (y/n): y
Make a move in the game that changes the score...
Press Enter when ready to read new score from screen...

New score from screen: 52
Filtering candidates...
✓ Filtered from 234 to 12 candidates

Filter score candidates? (y/n): y
...
✓ Filtered from 12 to 1 candidates
✓ Score address confirmed: 0x12AB3500
```

## Step 2: Use Memory Reading

Once you have the addresses, you can use them to read game state in real-time.

### Option A: Test with the example script

Edit `examples/test_memory_reading.py` and set the discovered addresses:

```python
BOARD_ADDRESS = 0x12AB3450  # Your discovered address
SCORE_ADDRESS = 0x12AB3500  # Your discovered address
```

Then run:

```bash
python examples/test_memory_reading.py
```

This will continuously read and display the game state from memory.

### Option B: Integrate into your code

```python
from wzlz_ai.memory_reader import GameMemoryReader

# Initialize reader
reader = GameMemoryReader(process_name="wzlz.exe")

# Attach to game
if not reader.attach():
    print("Failed to attach to game")
    exit(1)

# Set known addresses (from exploration)
reader.board_address = 0x12AB3450
reader.score_address = 0x12AB3500

# Read game state
state = reader.read_game_state()

if state:
    print(f"Score: {state.score}")
    print(f"Board shape: {state.board.shape}")
    # Use state.board for your AI...
```

## Advantages of Memory Reading

1. **Resolution independent**: Works regardless of screen resolution or DPI scaling
2. **No calibration needed**: Once addresses are found, no manual calibration required
3. **Faster**: Direct memory access is faster than screen capture and image processing
4. **More reliable**: No issues with window position, overlapping windows, or visual effects
5. **Lower CPU usage**: No image processing overhead

## Troubleshooting

### "Failed to attach to process"

- Make sure the game is running
- Check that the process name is correct (use Task Manager to verify)
- Run the script as Administrator if needed

### "No matching board patterns found"

- Verify that screen reader is working correctly
- The board might be stored in a different format (e.g., as integers instead of bytes)
- Try searching for individual cell values instead

### Addresses change after game restart

This is common. The addresses might be:
- **Relative to base address**: Calculate offset from base address
- **Pointer-based**: Need to find pointer chains (more advanced)

For pointer chains, you may need to use Cheat Engine to find stable pointer paths.

### Memory reading works but values are wrong

- The game might use different encoding (e.g., 1-7 instead of 0-6 for colors)
- Try reading as different data types (int16, int32 instead of int8)
- The memory layout might be different than expected

## Advanced: Finding Addresses Without Screen Reader

If you don't have screen capture set up, you can still find addresses manually:

1. **Start with a known value**: 
   - Note your current score (e.g., 100)
   - Search for that value in memory
   - Make a move to change score
   - Filter for new value
   - Repeat until few candidates remain

2. **Use Cheat Engine** (external tool):
   - More powerful memory scanning
   - Can find pointer chains
   - Visual interface for exploration
   - Export addresses for use in Python

3. **Pattern scanning**:
   - Look for patterns in memory (e.g., 81 consecutive bytes for 9x9 grid)
   - Search for known sequences

## Next Steps

Once you have reliable memory reading:

1. **Create a hybrid reader**: Combine memory reading with screen capture as fallback
2. **Find next balls address**: Use similar technique to find preview balls
3. **Optimize performance**: Memory reading is fast enough for real-time AI training
4. **Handle address changes**: Implement pointer chain following if addresses change

## Notes

- Memory reading only works for standalone games without anti-cheat
- Addresses may change between game versions
- Some games use dynamic memory allocation (addresses change each run)
- For production use, consider finding pointer chains for stability

