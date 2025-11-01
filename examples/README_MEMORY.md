# Memory Reading Examples

This directory contains examples for reading the Wzlz game state directly from process memory.

## Quick Start

### 1. Install Dependencies

```bash
uv pip install pymem pywin32
```

Or install with the optional dependency group:

```bash
uv pip install -e ".[memory-reading]"
```

### 2. Find Memory Addresses

You have two options:

#### Option A: Automated Tracking (Recommended for beginners)

```bash
uv run python examples/track_and_analyze_memory.py
```

This will:
- Automatically track game state every 10 seconds
- Collect multiple snapshots while you play
- Analyze patterns to find stable addresses
- Generate detailed analysis report
- Save results to `memory_analysis_results.json`

**Advantages**: Hands-off, detailed analysis, works while you play

#### Option B: Interactive Exploration (Faster)

```bash
uv run python examples/explore_memory.py
```

This will:
- Interactively guide you through discovery
- Require manual input at each step
- Find addresses in 5-10 minutes
- Save addresses to `memory_addresses.txt`

**Advantages**: Faster, more control, immediate feedback

### 3. Test Memory Reading

Once you have the addresses, update `test_memory_reading.py` with your discovered addresses and run:

```bash
uv run python examples/test_memory_reading.py
```

This will continuously read and display the game state from memory in real-time.

## Files

- **`track_and_analyze_memory.py`**: Automated tracking and analysis tool (NEW!)
- **`explore_memory.py`**: Interactive tool to discover memory addresses
- **`test_memory_reading.py`**: Simple example of reading game state from known addresses
- **`find_game_process.py`**: Helper to identify the game process name
- **`TRACKING_GUIDE.md`**: Detailed guide for the tracking tool

## Process Name

The default process name is `wzlz.exe`. If your game executable has a different name, you can specify it:

```python
reader = GameMemoryReader(process_name="your_game.exe")
```

To find the process name:
1. Open Task Manager (Ctrl+Shift+Esc)
2. Go to Details tab
3. Find your game process
4. Note the exact name (including .exe)

## Troubleshooting

### Permission Errors

If you get permission errors, try:
1. Run the script as Administrator
2. Disable antivirus temporarily (it may block memory access)

### Process Not Found

Make sure:
1. The game is running before you start the script
2. The process name is correct
3. You're using the correct executable name (check Task Manager)

### Addresses Don't Work After Restart

Some games use dynamic memory allocation. If addresses change:
1. Re-run `explore_memory.py` to find new addresses
2. Look for patterns in address offsets
3. Consider using Cheat Engine to find pointer chains (advanced)

## Comparison of Tools

| Tool | Best For | Time | Interaction | Detail |
|------|----------|------|-------------|--------|
| `track_and_analyze_memory.py` | Background analysis | 1-2 min | Automated | High |
| `explore_memory.py` | Quick discovery | 5-10 min | Interactive | Medium |
| `find_game_process.py` | Finding process name | 1 min | Interactive | N/A |
| `test_memory_reading.py` | Testing addresses | Continuous | None | N/A |

## See Also

- [TRACKING_GUIDE.md](TRACKING_GUIDE.md) - Guide for automated tracking tool
- [Memory Reading Guide](../docs/MEMORY_READING_GUIDE.md) - Detailed documentation
- [Game State Extraction](../docs/GAME_STATE_EXTRACTION.md) - Screen capture alternative
- [Memory Reading Quickstart](../MEMORY_READING_QUICKSTART.md) - 5-minute quick start

