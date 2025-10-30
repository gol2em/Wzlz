# Game Rules Implementation

This document describes the complete game rules implementation for the Wzlz (五子连珠) ball matching game.

## Game Overview

Wzlz is a puzzle game played on a 9×9 grid where the player moves colored balls to create lines of 5 or more matching balls.

## Game Modes

The game has **two modes**:

1. **Mode 1: With Next Ball Preview** (`show_next_balls=True`)
   - Shows the colors of the next 3 balls that will be added
   - Allows strategic planning
   - Easier difficulty

2. **Mode 2: Without Preview** (`show_next_balls=False`)
   - Next ball colors are hidden
   - More challenging
   - Requires different strategy

## Complete Rules

### 1. Board Setup
- **Grid Size**: 9×9 cells
- **Initial State**: 5 randomly placed balls at game start
- **Ball Colors**: 7 different colors (Red, Green, Blue, Brown, Magenta, Yellow, Cyan)

### 2. Gameplay

#### Moving Balls
- A move consists of selecting a ball and moving it to an empty cell
- The ball can only move along a **clear path** (no other balls blocking the way)
- Pathfinding uses BFS (Breadth-First Search) to find valid paths
- **Movement is ONLY horizontal and vertical** (4 directions: up, down, left, right)
- **NO diagonal movement allowed**

#### After Each Move
1. **Check for matches** at the destination position
2. If a match is found:
   - Remove all matched balls
   - Award **2 points per ball** removed
   - Do NOT add new balls
3. If NO match is found:
   - Add **3 random balls** to empty positions
   - Check if the new balls create any matches
   - If auto-matches occur, remove them but award **0 points**

### 3. Matching Rules

#### Match Criteria
- **Minimum Length**: 5 balls of the same color
- **Directions**: 4 possible directions
  - Horizontal (left-right)
  - Vertical (up-down)
  - Diagonal (top-left to bottom-right)
  - Diagonal (top-right to bottom-left)

#### Match Detection
- Checks in both directions from a position
- Can match more than 5 balls (6, 7, 8, etc.)
- Multiple matches can occur simultaneously (e.g., cross pattern)
- All matched balls are removed at once

### 4. Scoring System

#### Points Earned
- **Player Move Match**: 2 points per ball
  - When a move creates a match, each removed ball earns 2 points
  - Example: 5 balls matched = 10 points
  - Example: 7 balls matched = 14 points
  - Example: Cross pattern (9 balls) = 18 points

- **Auto-Match (Random Generation)**: 0 points
  - When random balls create a match, no points are awarded
  - This prevents luck-based scoring

### 5. Game Over Condition

The game ends when:
- The board is full (no empty cells), AND
- No valid moves are possible

A valid move requires:
1. A ball to move (source position occupied)
2. An empty destination
3. A clear path between source and destination

## Implementation Details

### Core Functions

#### `_check_and_remove_matches(state, pos)`
- Checks all 4 directions from a position
- Returns list of positions to remove and count
- Removes balls from the state

#### `_get_line_in_direction(state, pos, dr, dc, color)`
- Scans in both positive and negative directions
- Returns all consecutive balls of the same color
- Used by match detection

#### `_check_all_matches(state)`
- Scans entire board for matches
- Used after adding random balls
- Returns all matched positions

#### `execute_move(move)`
1. Validates the move
2. Moves the ball
3. Checks for matches (2 points per ball)
4. If no match, adds 3 random balls
5. Checks for auto-matches (0 points)
6. Updates score and state

### Configuration

```python
GameConfig(
    rows=9,                  # Board height
    cols=9,                  # Board width
    colors_count=7,          # Number of different colors
    match_length=5,          # Minimum balls to match
    balls_per_turn=3,        # Balls added after each move
    initial_balls=5,         # Starting balls
    show_next_balls=True     # Show next ball preview (game mode)
)
```

**Game Modes:**
```python
# Mode 1: With preview (easier)
config_easy = GameConfig(show_next_balls=True)

# Mode 2: Without preview (harder)
config_hard = GameConfig(show_next_balls=False)
```

## Testing

### Test Coverage

The implementation includes comprehensive tests:

1. **Horizontal Match Test**: 5 balls in a row
2. **Vertical Match Test**: 5 balls in a column
3. **Diagonal Match Test**: 5 balls diagonally
4. **Scoring Test**: Verify 2 points per ball
5. **Auto-Match Test**: Verify 0 points for random matches
6. **Longer Match Test**: 7+ balls in a line
7. **Multiple Match Test**: Cross pattern (9 balls)
8. **Game Over Test**: Full board detection

### Running Tests

```bash
# Run game rules tests
uv run python tests/test_game_rules.py

# Run framework tests
uv run python tests/test_framework.py

# Run demonstration
uv run python examples/demo_game_rules.py
```

## Example Scenarios

### Scenario 1: Simple Horizontal Match
```
Before:
. . . . . . . . .
. . . . . . . . .
. . . . . . . . .
. . . . R . . . .
R R R R . . . . .

Move: Pos(3,4) -> Pos(4,4)

After:
. . . . . . . . .
. . . . . . . . .
. . . . . . . . .
. . . . . . . . .
. . . . . . . . .

Points: 10 (5 balls × 2)
```

### Scenario 2: Cross Pattern
```
Before:
. . Y . . . . . .
. . Y . . . . . .
. . Y . . . . . .
. . Y . . . . . .
Y Y . Y Y . . . .
. . . . . Y . . .

Move: Pos(5,5) -> Pos(4,2)

After:
. . . . . . . . .
. . . . . . . . .
. . . . . . . . .
. . . . . . . . .
. . . . . . . . .
. . . . . . . . .

Points: 18 (9 balls × 2)
```

### Scenario 3: Auto-Match (No Points)
```
Before move:
. . . . . . . . .
B . . . . . . . .
. . . . . . . . .
R R R R . . . . .

Move: Pos(1,0) -> Pos(1,1) (no match)
Add 3 random balls: [R, G, B]

If R lands at Pos(3,4):
After:
. B . . . . . . .
. . . . . . . . .
. . . . . . . . .
. . . . . . . . .  <- R R R R R removed

Points: 0 (auto-match)
```

## Strategy Tips

For AI training, consider:

1. **Prioritize Matches**: Moves that create matches earn points
2. **Plan Ahead**: Consider where random balls might land
3. **Avoid Filling Board**: Keep space for new balls
4. **Create Multiple Matches**: Cross patterns earn more points
5. **Long Lines**: Longer matches earn more points (6+ balls)

## Next Steps

Now that the game rules are implemented, you can:

1. **Train AI Models**: Use reinforcement learning, MCTS, or other algorithms
2. **Implement Heuristics**: Create rule-based strategies
3. **Benchmark Performance**: Compare different approaches
4. **Optimize**: Improve the AI's decision-making

The framework is ready for AI development!

