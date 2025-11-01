# Quick Start - Auto-Play Memory Tracking (with uv)

## 🚀 Super Quick Start

```bash
# 1. Install dependencies
uv pip install pymem pywin32

# 2. Start the game (五子连珠5.2)

# 3. Run the auto-play tracking script
uv run python examples/track_and_analyze_memory.py

# 4. Wait 1-2 minutes, then press Ctrl+C

# Done! Check memory_analysis_results.json for addresses
```

## 📋 Prerequisites

- ✅ Game running (五子连珠5.2)
- ✅ Screen capture calibrated (run `uv run python examples/manual_calibrate_all.py` first)
- ✅ Dependencies installed (`uv pip install pymem pywin32`)

## 🎮 What Happens

The script will:
1. ✅ Attach to game process
2. ✅ Take snapshot of game state
3. ✅ **Make 2 random moves automatically** (NEW!)
4. ✅ Wait 10 seconds
5. ✅ Repeat steps 2-4
6. ✅ Analyze all data when you press Ctrl+C

**You don't need to do anything!** Just let it run.

## 📊 Expected Output

```
=== Memory Structure Analyzer with Auto-Play ===

✓ Successfully attached to game process!
✓ Auto-play enabled - will make random moves between snapshots

[14:30:00] Taking snapshot...
  ✓ Snapshot 1 captured

  Making 2 random moves...
    Making move: Move(Pos(2,3) -> Pos(5,7))
    ✓ Move successful!
    Making move: Move(Pos(1,1) -> Pos(4,4))
    ✓ Move successful!
  ✓ Made 2 moves

  Waiting 10 seconds for next snapshot...

[... continues for 1-2 minutes ...]

^C
Stopping tracking...

=== ANALYSIS RESULTS ===

✓ LIKELY BOARD ADDRESS: 0x12AB3450
✓ LIKELY SCORE ADDRESS: 0x12AB3500

✓ Results saved to memory_analysis_results.json
```

## 🎯 Using the Results

```python
from wzlz_ai.memory_reader import GameMemoryReader

reader = GameMemoryReader()
reader.attach()

# Use discovered addresses
reader.board_address = 0x12AB3450  # From analysis
reader.score_address = 0x12AB3500  # From analysis

# Read game state
state = reader.read_game_state()
print(f"Score: {state.score}")
print(f"Board: {state.board}")
```

## 🔧 All Commands (with uv)

```bash
# Install dependencies
uv pip install pymem pywin32

# Calibrate screen capture (first time only)
uv run python examples/manual_calibrate_all.py

# Auto-play tracking (recommended)
uv run python examples/track_and_analyze_memory.py

# Interactive exploration (alternative)
uv run python examples/explore_memory.py

# Test discovered addresses
uv run python examples/test_memory_reading.py

# Find game process name
uv run python examples/find_game_process.py
```

## ⚙️ Configuration

Edit `examples/track_and_analyze_memory.py`:

```python
# In main() function:
INTERVAL = 10              # Seconds between snapshots
MOVES_PER_INTERVAL = 2     # Moves to make between snapshots

# To disable auto-play:
analyzer = MemoryAnalyzer(auto_play=False)
```

## 🐛 Troubleshooting

### "Failed to attach to game process"
```bash
# Check if game is running
uv run python examples/find_game_process.py

# Run as Administrator if needed
```

### "Failed to read game state from screen"
```bash
# Calibrate screen capture first
uv run python examples/manual_calibrate_all.py
```

### "Could not initialize game client"
```bash
# Make sure game_window_config.json exists
# Run calibration:
uv run python examples/manual_calibrate_all.py
```

### "No moves made"
- Game might be full (restart with F4)
- Make a manual move to create space
- Check that screen capture is working

## 📚 Documentation

- **Quick Start**: `examples/AUTO_PLAY_TRACKING.md`
- **Complete Guide**: `examples/TRACKING_GUIDE.md`
- **Overview**: `TRACKING_TOOL_SUMMARY.md`
- **Memory Reading**: `docs/MEMORY_READING_GUIDE.md`

## 💡 Tips

1. **Let it run longer** - 10-15 snapshots is better than 5
2. **Check progress** - Watch console output to verify moves are being made
3. **Restart if stuck** - Press F4 in game if board gets full
4. **Verify results** - Use `test_memory_reading.py` to verify addresses

## 🎉 That's It!

The script is fully automated. Just:
1. Start the game
2. Run the script with `uv run python examples/track_and_analyze_memory.py`
3. Wait 1-2 minutes
4. Press Ctrl+C
5. Use the discovered addresses!

No manual moves, no interaction, no hassle! 🚀

