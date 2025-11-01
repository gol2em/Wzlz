# Automated Memory Tracking Tool

## Overview

A new automated tool has been added to help discover memory addresses by passively tracking game state over time.

## What It Does

The `track_and_analyze_memory.py` script:

1. **Captures game state from screen** every 10 seconds
2. **Makes random moves automatically** to change game state (NEW!)
3. **Searches memory** for matching patterns
4. **Tracks consistency** of addresses across snapshots
5. **Analyzes memory structure** around discovered addresses
6. **Generates detailed report** with findings

## Key Features

### 🤖 Fully Automated (NEW: Auto-Play!)
- **No manual interaction required at all!**
- **Script plays the game for you** - makes random moves automatically
- Runs completely hands-free
- Just start it and walk away
- Automatically collects and analyzes data

### 📊 Deep Analysis
- Tracks address consistency over time
- Analyzes memory structure
- Identifies relationships between data
- Calculates offsets between board and score

### 📝 Detailed Reporting
- Console output with analysis
- JSON file with all raw data
- Memory dumps around key addresses
- Confidence scores for each finding

### 🎯 Smart Filtering
- Filters out false positives
- Prioritizes consistent addresses
- Cross-references board and score locations
- Identifies likely data structures

## Usage

### Basic Usage

```bash
# Start the game
# Run the script
uv run python examples/track_and_analyze_memory.py

# That's it! The script will:
# - Make random moves automatically
# - Capture snapshots every 10 seconds
# - Run for 1-2 minutes (or longer)
# - Press Ctrl+C when you want to stop and analyze
```

### What You'll Get

**Console Output**:
```
=== ANALYSIS RESULTS ===

--- Board Address Analysis ---
  ✓ LIKELY BOARD ADDRESS: 0x12AB3450

--- Score Address Analysis ---
  ✓ LIKELY SCORE ADDRESS: 0x12AB3500

--- Cross-Reference Analysis ---
  Offset: 176 bytes (0xB0)
  ✓ Addresses are close together - likely in same data structure!

--- Memory Structure Analysis ---
  Potential score at offset +176: 42 (0x12AB3500)
  Potential next balls at offset +260: [1, 3, 5] (0x12AB3554)
```

**JSON File** (`memory_analysis_results.json`):
- All snapshots with timestamps
- All candidate addresses with match counts
- Likely addresses with confidence scores
- Complete analysis results

## How It Works

### 1. Snapshot Collection

Every 10 seconds:
```
Screen Capture → Board State (9x9 grid)
              → Score Value
              ↓
Memory Scan  → Find all matching patterns
              → Record addresses
```

### 2. Pattern Analysis

After collection:
```
Board Candidates → Filter by consistency
                → Identify most stable address

Score Candidates → Filter by appearance count
                → Cross-reference with board
                → Identify likely address

Memory Structure → Analyze surrounding data
                → Find related values
                → Calculate offsets
```

### 3. Confidence Scoring

Addresses are scored by:
- **Consistency**: How often they match (%)
- **Stability**: Same address across snapshots
- **Proximity**: Distance from other game data
- **Validity**: Values make sense for game state

## Advantages Over Interactive Tool

| Feature | Tracking Tool | Interactive Tool |
|---------|--------------|------------------|
| User effort | Low (passive) | Medium (active) |
| Time required | 1-2 minutes | 5-10 minutes |
| Snapshots | Many (10+) | Few (2-3) |
| Analysis depth | Deep | Basic |
| Confidence | High (statistical) | Medium (manual) |
| Best for | Background analysis | Quick discovery |

## When to Use

### Use Tracking Tool When:
- ✓ You want hands-off discovery
- ✓ You're playing the game anyway
- ✓ You want detailed analysis
- ✓ You want high confidence results
- ✓ You have 1-2 minutes to spare

### Use Interactive Tool When:
- ✓ You want immediate results
- ✓ You want manual control
- ✓ You want step-by-step guidance
- ✓ You need quick verification

## Example Output

### Successful Discovery

```
Total snapshots: 10

Board Address Analysis:
  [1] 0x12AB3450 - matched 10/10 times (100.0%)
  ✓ LIKELY BOARD ADDRESS: 0x12AB3450

Score Address Analysis:
  [1] 0x12AB3500 - matched 8/10 times (80.0%)
  ✓ LIKELY SCORE ADDRESS: 0x12AB3500

Cross-Reference:
  Offset: 176 bytes
  ✓ Addresses are close together!

Memory Structure:
  Potential next balls at offset +260: [1, 3, 5]
```

### Uncertain Results

```
Total snapshots: 5

Board Address Analysis:
  [1] 0x12AB3450 - matched 3/5 times (60.0%)
  [2] 0x12AB3460 - matched 2/5 times (40.0%)
  ⚠ No consistent board address found

Recommendation: Collect more snapshots
```

## Tips for Best Results

### 1. Play Actively
- Make moves between snapshots
- Score points (change the score)
- Fill different parts of the board

### 2. Collect Enough Data
- Minimum: 5 snapshots
- Recommended: 10-15 snapshots
- More data = higher confidence

### 3. Vary Game State
- Don't just wait idle
- Make the board look different each snapshot
- Change the score value

### 4. Keep Game Visible
- Don't minimize the window
- Screen capture needs to read state
- Game can be in background but visible

## Integration

Once addresses are found:

```python
from wzlz_ai.memory_reader import GameMemoryReader

# Use discovered addresses
reader = GameMemoryReader()
reader.attach()
reader.board_address = 0x12AB3450  # From tracking
reader.score_address = 0x12AB3500  # From tracking

# Read game state
state = reader.read_game_state()
```

## Files Created

- **`memory_analysis_results.json`**: Complete analysis results
  - All snapshots with timestamps
  - All candidate addresses
  - Confidence scores
  - Memory structure analysis

## Troubleshooting

### No Addresses Found

**Causes**:
- Not enough snapshots
- Game state too similar
- Addresses changing dynamically

**Solutions**:
- Collect more snapshots (15-20)
- Make more moves between snapshots
- Try interactive tool instead

### Too Many Candidates

**This is normal!** The script filters by:
- Consistency (appears in multiple snapshots)
- Proximity (close to other game data)
- Validity (reasonable values)

### Addresses Change After Restart

**This is expected** for some games. Solutions:
- Re-run tracking after each restart
- Use pointer chains (advanced)
- Calculate offsets from base address

## Performance

- **Memory overhead**: Low (~10MB for analysis)
- **CPU usage**: Low (only during snapshots)
- **Disk usage**: ~1MB for JSON results
- **Time**: 1-2 minutes for good results

## Future Enhancements

Potential improvements:
- [ ] Automatic pointer chain discovery
- [ ] Real-time address verification
- [ ] Next balls address detection
- [ ] Move count address detection
- [ ] Automatic offset calculation
- [ ] Address stability prediction

## Conclusion

The tracking tool provides:
- ✓ **Automated discovery** - no manual interaction
- ✓ **High confidence** - statistical analysis
- ✓ **Deep insights** - memory structure analysis
- ✓ **Easy to use** - just run and play

Perfect for discovering memory addresses while playing the game naturally!

## See Also

- [TRACKING_GUIDE.md](examples/TRACKING_GUIDE.md) - Detailed usage guide
- [explore_memory.py](examples/explore_memory.py) - Interactive alternative
- [MEMORY_READING_GUIDE.md](docs/MEMORY_READING_GUIDE.md) - Complete documentation

