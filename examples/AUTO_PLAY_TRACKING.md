# Auto-Play Memory Tracking

## Quick Start (Fully Automated!)

The tracking script now includes **auto-play** functionality - it will play the game for you!

### 1. Prerequisites

Make sure you have:
- ✓ Game running (五子连珠5.2)
- ✓ Screen capture calibrated (`game_window_config.json` exists)
- ✓ Dependencies installed: `uv pip install pymem pywin32`

### 2. Run the Script

```bash
uv run python examples/track_and_analyze_memory.py
```

### 3. Let It Run

The script will:
1. Attach to the game process
2. Take a snapshot of the current state
3. **Make 2 random moves** automatically
4. Wait 10 seconds
5. Repeat steps 2-4

**You don't need to do anything!** Just let it run for 1-2 minutes.

### 4. Stop and Analyze

Press `Ctrl+C` when you want to stop (after 5-10 snapshots).

The script will automatically:
- Analyze all collected data
- Identify likely board and score addresses
- Save results to `memory_analysis_results.json`

## Example Session

```
=== Memory Structure Analyzer with Auto-Play ===

This script will track the game state every 10 seconds and analyze
memory to find where the board and score are stored.

Auto-play is ENABLED - the script will make random moves between
snapshots to ensure the game state changes naturally.

Attempting to attach to process: wzlz.exe
✓ Successfully attached to game process!
  Base address: 0x400000
✓ Auto-play enabled - will make random moves between snapshots

=== Starting tracking... ===
Will take snapshots every 10 seconds
Will make 2 random moves between snapshots
Press Ctrl+C to stop and analyze

[14:30:00] Taking snapshot...
  Screen: Score=42, Balls=23
  Searching memory for board pattern...
    Found 1 potential board addresses
  Searching memory for score value...
    Found 234 potential score addresses
  ✓ Snapshot 1 captured

  Making 2 random moves...
    Making move: Move(Pos(2,3) -> Pos(5,7))
    ✓ Move successful!
    Making move: Move(Pos(1,1) -> Pos(4,4))
    ✓ Move successful!
  ✓ Made 2 moves

  Waiting 10 seconds for next snapshot...

[14:30:10] Taking snapshot...
  Screen: Score=52, Balls=25
  Searching memory for board pattern...
    Found 1 potential board addresses
  Searching memory for score value...
    Found 189 potential score addresses
  ✓ Snapshot 2 captured

  (2 snapshots collected - press Ctrl+C to analyze)

  Making 2 random moves...
    Making move: Move(Pos(0,0) -> Pos(0,8))
    ✓ Move successful!
    Making move: Move(Pos(3,3) -> Pos(6,6))
    ✓ Move successful!
  ✓ Made 2 moves

  Waiting 10 seconds for next snapshot...

[... continues ...]

^C
Stopping tracking...

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
  
  ✓ LIKELY SCORE ADDRESS: 0x12AB3500

✓ Results saved to memory_analysis_results.json

=== SUMMARY ===

✓ Board Address Found: 0x12AB3450
  Use this in your memory reader:
  reader.board_address = 0x12AB3450

✓ Score Address Found: 0x12AB3500
  Use this in your memory reader:
  reader.score_address = 0x12AB3500
```

## How Auto-Play Works

### Move Selection

The script:
1. Reads the current board state
2. Finds all balls and empty cells
3. Randomly selects a ball and an empty cell
4. Attempts to move the ball to the empty cell
5. If the move fails (no path), tries another random move
6. Makes up to 10 attempts to find a valid move

### Move Execution

For each move:
1. Clicks on the source ball (to select it)
2. Waits 0.3 seconds for bounce animation
3. Clicks on the destination cell
4. Waits 1.8 seconds for move + new balls animation
5. Handles any popups (game over, high score)

### Safety Features

- **Game reset detection**: If the game resets (game over), the script continues
- **Error handling**: If a move fails, the script tries another move
- **Timeout protection**: Only tries 10 moves before giving up
- **Animation delays**: Waits for all animations to complete

## Configuration

You can customize the auto-play behavior by editing the script:

```python
# In main() function:
INTERVAL = 10  # Seconds between snapshots
MOVES_PER_INTERVAL = 2  # Moves to make between snapshots

# To disable auto-play:
analyzer = MemoryAnalyzer(auto_play=False)
```

## Advantages of Auto-Play

### 1. Fully Hands-Free
- Start the script and walk away
- No need to manually make moves
- No need to watch the game

### 2. Consistent State Changes
- Makes moves at regular intervals
- Ensures board state changes between snapshots
- Ensures score changes (when matches occur)

### 3. Better Analysis
- More varied game states
- More data points for analysis
- Higher confidence in results

### 4. Time Efficient
- Collect data while doing other things
- No need to actively play the game
- Just check back after 1-2 minutes

## Troubleshooting

### "Could not initialize game client"

**Problem**: Auto-play failed to initialize

**Solutions**:
- Make sure `game_window_config.json` exists
- Run `examples/manual_calibrate_all.py` first
- Check that game window title matches ("五子连珠5.2")

**Fallback**: Script will continue without auto-play - you'll need to make moves manually

### "No moves made"

**Problem**: Script couldn't find valid moves

**Possible causes**:
- Board is full (game over)
- All balls are isolated (no valid paths)
- Screen capture failed

**Solutions**:
- Restart the game (press F4)
- Make a manual move to create space
- Check screen capture is working

### "Move successful!" but board didn't change

**Problem**: Move was executed but had no effect

**This is normal** if:
- The move was blocked by another ball
- The path was not clear
- The game rejected the move

**The script will try another move** automatically.

## Comparison: Auto-Play vs Manual

| Aspect | Auto-Play | Manual |
|--------|-----------|--------|
| **User Effort** | None | High |
| **Time Required** | 1-2 min | 1-2 min |
| **Attention Needed** | None | Constant |
| **State Variation** | Good | Excellent |
| **Reliability** | High | Very High |
| **Best For** | Hands-free discovery | Maximum control |

## Tips for Best Results

### 1. Let It Run Longer
- 10-15 snapshots is better than 5
- More data = higher confidence
- Takes only 2-3 minutes

### 2. Check Progress
- Watch the console output
- Make sure moves are being made
- Verify snapshots are captured

### 3. Restart If Needed
- If game gets stuck (full board), restart
- Press F4 in the game to restart
- Script will continue automatically

### 4. Verify Results
- After analysis, check the addresses
- Use `test_memory_reading.py` to verify
- Compare with screen capture

## Next Steps

After finding addresses:

1. **Test them**:
   ```bash
   uv run python examples/test_memory_reading.py
   ```

2. **Use in your code**:
   ```python
   from wzlz_ai.memory_reader import GameMemoryReader
   
   reader = GameMemoryReader()
   reader.attach()
   reader.board_address = 0x12AB3450  # From tracking
   reader.score_address = 0x12AB3500  # From tracking
   
   state = reader.read_game_state()
   ```

3. **Integrate with AI training**:
   - Use memory reading for fast state access
   - Train AI models with real game data
   - Achieve 10-100x speedup over screen capture

## See Also

- [TRACKING_GUIDE.md](TRACKING_GUIDE.md) - Complete tracking guide
- [README_MEMORY.md](README_MEMORY.md) - Memory reading overview
- [../docs/MEMORY_READING_GUIDE.md](../docs/MEMORY_READING_GUIDE.md) - Detailed documentation

