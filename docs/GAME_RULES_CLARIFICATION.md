# Game Rules Clarification

This document clarifies the exact game rules based on the real game behavior.

## ✅ Confirmed Rules

### 1. Movement Rules

#### Path Restrictions
- ✅ **ONLY horizontal and vertical movement** (4 directions: up, down, left, right)
- ❌ **NO diagonal movement allowed**
- ✅ Path must be clear (no balls blocking the way)
- ✅ Uses BFS (Breadth-First Search) to find shortest valid path

**Example:**
```
Start: (0,0)
Goal:  (2,2)
Block: (1,1)

Invalid (diagonal):
  (0,0) → (1,1) → (2,2)  ❌ Diagonal moves not allowed

Valid (horizontal/vertical):
  (0,0) → (0,1) → (0,2) → (1,2) → (2,2)  ✓ Only H/V moves
```

**Code Implementation:**
```python
# BFS pathfinding with 4 directions only
for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:  # Right, Down, Left, Up
    next_pos = Position(current.row + dr, current.col + dc)
    # ... check if valid and continue
```

### 2. Ball Generation Rules

#### After Player Move
- ✅ If match occurs: **NO new balls added**
- ✅ If no match: **3 new balls added** to random empty positions

**Example:**
```
Move creates match:
  Before: R R R R . (4 red balls)
  Move:   R → position to complete line
  Result: Match! Remove 5 balls, earn 10 points
  New balls: NONE ✓

Move doesn't create match:
  Before: R . . . . (1 red ball)
  Move:   R → different position
  Result: No match
  New balls: 3 random balls added ✓
```

#### Auto-Match After Generation
- ✅ If new balls create a match: **Remove them, earn 0 points**
- ✅ This prevents luck-based scoring

**Example:**
```
Before move: R R R R . (4 red balls)
Move: B → somewhere else (no match)
New balls added: [R, G, B]
  If R lands at position 5: R R R R R (5 red balls)
  Result: Auto-match! Remove 5 balls, earn 0 points ✓
```

### 3. Game Modes

The game has **two modes** that affect difficulty:

#### Mode 1: With Next Ball Preview (Easier)
```python
config = GameConfig(show_next_balls=True)
```

- ✅ Shows colors of next 3 balls
- ✅ Allows strategic planning
- ✅ Can avoid placing balls where next balls will land
- ✅ Better for learning and training

**Display:**
```
Next balls: [RED, BLUE, GREEN]
Score: 42

Board:
R . . . . . . . .
. . . . . . . . .
...
```

#### Mode 2: Without Preview (Harder)
```python
config = GameConfig(show_next_balls=False)
```

- ✅ Next ball colors are hidden
- ✅ More challenging
- ✅ Requires different strategy (can't plan ahead)
- ✅ More realistic for AI training (partial observability)

**Display:**
```
Next balls: ???
Score: 42

Board:
R . . . . . . . .
. . . . . . . . .
...
```

### 4. Scoring Rules

#### Player Move Match
- ✅ **2 points per ball** removed
- ✅ Only when match occurs immediately after player's move

**Examples:**
```
5 balls matched:  5 × 2 = 10 points ✓
7 balls matched:  7 × 2 = 14 points ✓
9 balls matched:  9 × 2 = 18 points ✓ (cross pattern)
```

#### Auto-Match (After Random Generation)
- ✅ **0 points** earned
- ✅ Balls are still removed
- ✅ Prevents luck-based scoring

**Example:**
```
Move doesn't match: 0 points
3 balls added: [R, R, R]
If they form a line: Remove them, 0 points ✓
```

### 5. Matching Rules

#### Match Criteria
- ✅ **Minimum 5 balls** of same color
- ✅ **4 directions**: horizontal, vertical, diagonal-right, diagonal-left
- ✅ Can match more than 5 (6, 7, 8, 9, etc.)
- ✅ Multiple matches can occur simultaneously (cross pattern)

**Directions:**
```
Horizontal:      → (0, 1)
Vertical:        ↓ (1, 0)
Diagonal-right:  ↘ (1, 1)
Diagonal-left:   ↙ (1, -1)
```

**Note:** Matching can be diagonal, but **movement cannot**!

### 6. Game Over Condition

Game ends when:
- ✅ Board is full (no empty cells), AND
- ✅ No valid moves possible

**Example:**
```
Board full but can still move:
  R R R R R R R R R
  R R R R R R R R R
  R R R R R R R R .  ← One empty cell
  Game over: False ✓ (can still move)

Board completely full:
  R R R R R R R R R
  R R R R R R R R R
  R R R R R R R R R
  Game over: True ✓ (no moves possible)
```

## 🔧 Implementation Details

### Configuration
```python
from wzlz_ai import GameConfig

# Standard game (with preview)
config = GameConfig(
    rows=9,
    cols=9,
    colors_count=7,
    match_length=5,
    balls_per_turn=3,
    initial_balls=5,
    show_next_balls=True  # Show preview
)

# Hard mode (no preview)
config_hard = GameConfig(
    show_next_balls=False  # Hide preview
)
```

### Testing Movement Rules
```python
from wzlz_ai import SimulationEnvironment, Position

env = SimulationEnvironment(config, seed=42)
state = env.reset()

# Test pathfinding
path_exists, path = env.is_path_clear(
    Position(0, 0),
    Position(2, 2),
    state
)

# Verify path only uses horizontal/vertical moves
for i in range(len(path) - 1):
    curr = path[i]
    next_pos = path[i + 1]
    row_diff = abs(next_pos.row - curr.row)
    col_diff = abs(next_pos.col - curr.col)
    
    # Only one should be 1, the other should be 0
    assert (row_diff == 1 and col_diff == 0) or \
           (row_diff == 0 and col_diff == 1)
```

### Testing Game Modes
```python
# Mode with preview
env1 = SimulationEnvironment(GameConfig(show_next_balls=True))
state1 = env1.reset()
assert len(state1.next_balls) == 3  # Has preview

# Mode without preview
env2 = SimulationEnvironment(GameConfig(show_next_balls=False))
state2 = env2.reset()
assert len(state2.next_balls) == 0  # No preview
```

## 📊 Summary Table

| Rule | Behavior | Implementation |
|------|----------|----------------|
| **Movement** | Horizontal/Vertical only | BFS with 4 directions |
| **Matching** | 4 directions (including diagonal) | Check all 4 directions |
| **New Balls** | 3 after move (if no match) | Add only if no match |
| **Auto-Match** | Remove, 0 points | Check after adding balls |
| **Player Match** | Remove, 2 points/ball | Check after move |
| **Preview Mode** | Show/hide next balls | `show_next_balls` flag |
| **Game Over** | Board full + no moves | Check empty cells |

## ✅ Verification

All rules have been implemented and tested:

```bash
# Run all tests
uv run python tests/test_game_rules.py

# Test specific rules
python -c "
from tests.test_game_rules import *
test_path_only_horizontal_vertical()  # ✓ Movement rules
test_game_mode_with_preview()         # ✓ Preview mode
test_game_mode_without_preview()      # ✓ No preview mode
test_horizontal_match()               # ✓ Matching
test_scoring()                        # ✓ Scoring
test_auto_match()                     # ✓ Auto-match
"
```

## 🎯 Key Differences from Initial Understanding

| Aspect | Initial | Corrected |
|--------|---------|-----------|
| Movement | Thought diagonal allowed | ❌ Only H/V allowed |
| Ball generation | Always 3 balls | ✓ Only if no match |
| Game modes | Single mode | ✓ Two modes (with/without preview) |

## 🚀 Next Steps

Now that the rules are clarified and implemented:

1. ✅ **Rules are correct** - verified with tests
2. ✅ **Two game modes** - implemented and tested
3. ✅ **Movement restrictions** - only horizontal/vertical
4. ⏭️ **Validate with real game** - use image recognition to verify
5. ⏭️ **Train AI models** - use correct rules for training

The framework is now ready for accurate AI training! 🎉

