# Memory Tracking and Analysis Guide

This guide explains how to use the `track_and_analyze_memory.py` script to automatically discover memory addresses by tracking game state over time.

## Overview

The tracking script is an **automated alternative** to the interactive `explore_memory.py` tool. Instead of requiring manual interaction, it:

1. Automatically captures game state from screen every 10 seconds
2. **Makes random moves in the game** to ensure state changes naturally
3. Searches memory for matching patterns
4. Tracks which addresses consistently match across multiple snapshots
5. Analyzes memory structure to identify board and score locations
6. Generates a detailed analysis report

**NEW**: The script now includes **auto-play** functionality! It will automatically make 2 random moves between each snapshot, so you can just start it and let it run without any manual interaction.

## When to Use This Tool

### Use `track_and_analyze_memory.py` when:
- ✓ You want a **fully automated** approach (no manual moves needed!)
- ✓ You want to just start it and walk away
- ✓ You want to analyze memory structure over time
- ✓ You want detailed analysis of memory patterns
- ✓ You want the script to play the game for you

### Use `explore_memory.py` when:
- ✓ You want immediate, interactive results
- ✓ You want to manually verify addresses
- ✓ You need quick discovery (5-10 minutes)
- ✓ You want step-by-step guidance

## Prerequisites

1. **Game must be running** before starting the script
2. **Screen capture must be calibrated** - you need `game_window_config.json`
3. **Dependencies must be installed**: `uv pip install pymem pywin32`

## Usage

### Basic Usage

```bash
uv run python examples/track_and_analyze_memory.py
```

The script will:
1. Attach to the game process
2. Take snapshots every 10 seconds
3. Continue until you press Ctrl+C
4. Analyze all collected data
5. Save results to `memory_analysis_results.json`

### Recommended Workflow

1. **Start the script**:
   ```bash
   uv run python examples/track_and_analyze_memory.py
   ```

2. **Let it run automatically**:
   - The script will make random moves for you!
   - No need to touch the game
   - Just let it run for 1-2 minutes
   - The script captures snapshots and makes moves automatically

3. **Collect at least 5-10 snapshots**:
   - More snapshots = better analysis
   - Wait at least 1-2 minutes (6-12 snapshots)
   - Script makes 2 moves between each snapshot

4. **Stop and analyze**:
   - Press `Ctrl+C` to stop tracking
   - Script will automatically analyze all data
   - Results are saved to JSON file

**Note**: You can also disable auto-play and make moves manually if you prefer. Just modify the script to set `auto_play=False`.

## What the Script Does

### 1. Snapshot Collection

Every 10 seconds, the script:
- Reads board state from screen (9x9 grid)
- Reads score from screen
- Searches entire process memory for matching patterns
- Records all potential addresses

### 1.5. Auto-Play (NEW!)

Between snapshots, the script:
- Makes 2 random valid moves in the game
- Waits for animations to complete
- Ensures the game state changes naturally
- No manual interaction required!

### 2. Pattern Analysis

After collection, the script analyzes:

**Board Addresses**:
- Searches for 81 consecutive bytes matching the board
- Tracks which addresses appear consistently
- Identifies the most likely board address

**Score Addresses**:
- Searches for 4-byte integers matching the score
- Filters addresses that appear multiple times
- Identifies stable score addresses

**Memory Structure**:
- Examines memory around the board address
- Looks for related data (score, next balls, etc.)
- Calculates offsets between data structures

### 3. Results

The script outputs:

**Console Output**:
```
=== ANALYSIS RESULTS ===

Total snapshots: 8

--- Board Address Analysis ---
  Total unique addresses found: 1
  Top candidates (by consistency):
    [1] 0x12AB3450 - matched 8/8 times (100.0%)
  
  ✓ LIKELY BOARD ADDRESS: 0x12AB3450

--- Score Address Analysis ---
  Total unique addresses found: 234
  Consistent candidates (appeared 2+ times):
    [1] 0x12AB3500 - matched 6/8 times (75.0%)
    [2] 0x12AB3504 - matched 5/8 times (62.5%)
  
  ✓ LIKELY SCORE ADDRESS: 0x12AB3500

--- Cross-Reference Analysis ---
  Board address:  0x12AB3450
  Score address:  0x12AB3500
  Offset:         176 bytes (0xB0)
  ✓ Addresses are close together - likely in same data structure!

--- Memory Structure Analysis ---
  Analyzing memory around board address 0x12AB3450...
  
  Memory dump (showing 50 bytes before board):
    0x12AB3420: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
    0x12AB3430: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
    0x12AB3440: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
    0x12AB3450: 01 00 02 00 00 00 03 00 00 ...                   [BOARD STARTS]
  
  Looking for patterns:
    Potential score at offset +176: 42 (0x12AB3500)
    Potential next balls at offset +260: [1, 3, 5] (0x12AB3554)
```

**JSON File** (`memory_analysis_results.json`):
```json
{
  "process_name": "wzlz.exe",
  "analysis_time": "2025-10-30T14:30:00",
  "snapshot_count": 8,
  "likely_board_address": "0x12AB3450",
  "likely_score_address": "0x12AB3500",
  "board_candidates": {
    "0x12AB3450": 8
  },
  "score_candidates": {
    "0x12AB3500": 6,
    "0x12AB3504": 5
  },
  "snapshots": [...]
}
```

## Understanding the Results

### Board Address Confidence

- **100% match rate**: Excellent! Address is stable
- **80-99% match rate**: Good, likely correct
- **50-79% match rate**: Uncertain, may need more snapshots
- **<50% match rate**: Unreliable, addresses may be changing

### Score Address Confidence

Score addresses are trickier because:
- Score changes frequently during gameplay
- Many memory locations might temporarily hold the score value
- Need to see the same address across multiple different scores

**Good signs**:
- Address appears in 50%+ of snapshots
- Address is close to board address (within a few hundred bytes)
- Address value changes when score changes

### Memory Structure Insights

The script analyzes memory around the board to find:

1. **Score location**: Usually within 100-500 bytes of board
2. **Next balls**: Often stored as 3 consecutive bytes (values 1-7)
3. **Other game data**: Move count, high score, etc.

## Tips for Best Results

### 1. Vary Game State

Between snapshots, try to:
- Make different moves
- Score points (change the score)
- Fill different parts of the board
- This helps filter out false positives

### 2. Collect Enough Data

- **Minimum**: 5 snapshots
- **Recommended**: 10-15 snapshots
- **Ideal**: 20+ snapshots for high confidence

### 3. Keep Game State Visible

- Don't minimize the game window
- Keep the game in focus (or at least visible)
- Screen capture needs to read the current state

### 4. Let Score Change

- If score stays at 0, score addresses won't be found
- Make moves that score points
- Vary the score between snapshots

## Troubleshooting

### "Failed to attach to game process"

**Problem**: Can't access game memory

**Solutions**:
- Make sure game is running
- Check process name is correct (use `find_game_process.py`)
- Run script as Administrator
- Disable antivirus temporarily

### "Failed to read game state from screen"

**Problem**: Screen capture not working

**Solutions**:
- Make sure `game_window_config.json` exists and is calibrated
- Run `examples/manual_calibrate_all.py` first
- Check that game window is visible
- Verify window title matches

### "No consistent addresses found"

**Problem**: Addresses change between snapshots

**Possible causes**:
1. **Dynamic memory allocation**: Game allocates memory differently each time
2. **Not enough snapshots**: Need more data points
3. **Game state too similar**: Board didn't change enough

**Solutions**:
- Collect more snapshots (20+)
- Make more moves between snapshots
- Restart game and try again
- Use pointer chains (advanced - requires Cheat Engine)

### "Too many score candidates"

**Problem**: Hundreds of addresses match the score

**This is normal!** The script filters by consistency:
- Only addresses appearing 2+ times are considered
- Addresses appearing in 50%+ snapshots are prioritized
- Cross-reference with board address helps

## Comparison with Interactive Tool

| Feature | track_and_analyze_memory.py | explore_memory.py |
|---------|----------------------------|-------------------|
| **Interaction** | Automated | Manual |
| **Time Required** | 1-2 minutes | 5-10 minutes |
| **Snapshots** | Many (10+) | Few (2-3) |
| **Analysis Depth** | Deep | Basic |
| **User Effort** | Low (passive) | Medium (interactive) |
| **Best For** | Background analysis | Quick discovery |

## Using the Results

Once you have the addresses, use them in your code:

```python
from wzlz_ai.memory_reader import GameMemoryReader

# Initialize reader
reader = GameMemoryReader(process_name="wzlz.exe")
reader.attach()

# Set discovered addresses (from analysis)
reader.board_address = 0x12AB3450
reader.score_address = 0x12AB3500

# Read game state
state = reader.read_game_state()
print(f"Score: {state.score}")
print(f"Board: {state.board}")
```

## Advanced: Analyzing the JSON Output

The JSON file contains all raw data for further analysis:

```python
import json

# Load results
with open('memory_analysis_results.json', 'r') as f:
    results = json.load(f)

# Analyze snapshots
for snapshot in results['snapshots']:
    print(f"Time: {snapshot['timestamp']}")
    print(f"Score: {snapshot['score']}")
    print(f"Board addresses found: {len(snapshot['board_addresses'])}")
    print(f"Score addresses found: {len(snapshot['score_addresses'])}")
```

## Next Steps

After finding addresses:

1. **Verify addresses**: Use `test_memory_reading.py` to verify they work
2. **Test stability**: Restart game and check if addresses change
3. **Integrate**: Use in your AI training code
4. **Document**: Save addresses for future use

## See Also

- [explore_memory.py](explore_memory.py) - Interactive discovery tool
- [test_memory_reading.py](test_memory_reading.py) - Test discovered addresses
- [MEMORY_READING_GUIDE.md](../docs/MEMORY_READING_GUIDE.md) - Complete guide
- [MEMORY_READING_QUICKSTART.md](../MEMORY_READING_QUICKSTART.md) - Quick start

