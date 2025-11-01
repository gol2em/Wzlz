# Memory Reading Quick Start

Fast guide to get memory reading working in 5 minutes.

## Step 1: Install (30 seconds)

```bash
pip install pymem
```

## Step 2: Find Process (1 minute)

```bash
python examples/find_game_process.py
```

Choose option 3 to search for 'wzlz'. Note the process name (e.g., `wzlz.exe`).

## Step 3: Discover Addresses (2 minutes)

1. **Start the game** and make sure it's visible
2. **Make sure your screen capture is calibrated** (you need `game_window_config.json`)
3. Run:

```bash
python examples/explore_memory.py
```

4. Follow the prompts:
   - Answer `y` to use screen reader
   - Wait for board address to be found
   - Wait for score address to be found
   - If too many score candidates, make a move and filter
   - Save addresses when prompted

## Step 4: Test (1 minute)

1. Open `examples/test_memory_reading.py`
2. Update these lines with your discovered addresses:

```python
BOARD_ADDRESS = 0x12AB3450  # Replace with your address
SCORE_ADDRESS = 0x12AB3500  # Replace with your address
```

3. Run:

```bash
python examples/test_memory_reading.py
```

You should see the game state updating in real-time!

## Step 5: Use in Your Code

```python
from wzlz_ai.memory_reader import GameMemoryReader

# Initialize
reader = GameMemoryReader(process_name="wzlz.exe")
reader.attach()

# Set addresses (from exploration)
reader.board_address = 0x12AB3450
reader.score_address = 0x12AB3500

# Read game state
state = reader.read_game_state()

# Use it!
print(f"Score: {state.score}")
print(f"Board shape: {state.board.shape}")
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Failed to attach" | Make sure game is running, try as Administrator |
| "No patterns found" | Verify screen reader works, check calibration |
| Addresses change | Re-run exploration after each game restart |
| Import error | Install pymem: `pip install pymem` |

## Next Steps

- Read [MEMORY_READING_GUIDE.md](docs/MEMORY_READING_GUIDE.md) for details
- Read [MEMORY_READING_SUMMARY.md](MEMORY_READING_SUMMARY.md) for overview
- Integrate with your AI training code

## Why Memory Reading?

- ✓ **10-100x faster** than screen capture
- ✓ **No calibration** needed (after finding addresses)
- ✓ **Resolution independent**
- ✓ **More reliable**
- ✓ **Lower CPU usage**

Perfect for AI training where you need to read game state thousands of times per second!

