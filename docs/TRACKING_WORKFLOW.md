# Memory Tracking Workflow

This document visualizes how the automated memory tracking tool works.

## High-Level Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                    User Actions                              │
│  1. Start game                                               │
│  2. Run track_and_analyze_memory.py                          │
│  3. Play game normally (1-2 minutes)                         │
│  4. Press Ctrl+C to stop                                     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Automated Tracking Process                      │
│                                                              │
│  Every 10 seconds:                                           │
│  ┌────────────────────────────────────────────────┐         │
│  │ 1. Screen Capture                              │         │
│  │    ├─ Read board (9x9 grid)                    │         │
│  │    ├─ Read score                               │         │
│  │    └─ Read next balls (if available)           │         │
│  └────────────────────────────────────────────────┘         │
│                      │                                       │
│                      ▼                                       │
│  ┌────────────────────────────────────────────────┐         │
│  │ 2. Memory Scan                                 │         │
│  │    ├─ Search for board pattern (81 bytes)     │         │
│  │    ├─ Search for score value (4 bytes)        │         │
│  │    └─ Record all matching addresses            │         │
│  └────────────────────────────────────────────────┘         │
│                      │                                       │
│                      ▼                                       │
│  ┌────────────────────────────────────────────────┐         │
│  │ 3. Store Snapshot                              │         │
│  │    ├─ Timestamp                                │         │
│  │    ├─ Board state                              │         │
│  │    ├─ Score value                              │         │
│  │    ├─ Board addresses found                    │         │
│  │    └─ Score addresses found                    │         │
│  └────────────────────────────────────────────────┘         │
│                                                              │
│  Repeat until Ctrl+C...                                      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Analysis Phase                             │
│                                                              │
│  ┌────────────────────────────────────────────────┐         │
│  │ 1. Board Address Analysis                      │         │
│  │    ├─ Count matches per address                │         │
│  │    ├─ Calculate consistency (%)                │         │
│  │    └─ Identify most stable address             │         │
│  └────────────────────────────────────────────────┘         │
│                      │                                       │
│                      ▼                                       │
│  ┌────────────────────────────────────────────────┐         │
│  │ 2. Score Address Analysis                      │         │
│  │    ├─ Filter addresses appearing 2+ times      │         │
│  │    ├─ Calculate consistency (%)                │         │
│  │    └─ Identify likely score address            │         │
│  └────────────────────────────────────────────────┘         │
│                      │                                       │
│                      ▼                                       │
│  ┌────────────────────────────────────────────────┐         │
│  │ 3. Cross-Reference Analysis                    │         │
│  │    ├─ Calculate offset between addresses       │         │
│  │    ├─ Check if addresses are nearby            │         │
│  │    └─ Validate data structure relationship     │         │
│  └────────────────────────────────────────────────┘         │
│                      │                                       │
│                      ▼                                       │
│  ┌────────────────────────────────────────────────┐         │
│  │ 4. Memory Structure Analysis                   │         │
│  │    ├─ Read memory around board address         │         │
│  │    ├─ Look for score nearby                    │         │
│  │    ├─ Look for next balls pattern              │         │
│  │    └─ Identify other game data                 │         │
│  └────────────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      Output                                  │
│                                                              │
│  Console:                                                    │
│  ├─ Analysis results                                         │
│  ├─ Likely addresses                                         │
│  ├─ Confidence scores                                        │
│  └─ Memory structure insights                                │
│                                                              │
│  JSON File (memory_analysis_results.json):                   │
│  ├─ All snapshots                                            │
│  ├─ All candidates                                           │
│  ├─ Analysis results                                         │
│  └─ Metadata                                                 │
└─────────────────────────────────────────────────────────────┘
```

## Detailed Snapshot Process

```
Time: T+0s
┌──────────────────┐
│  Screen Capture  │
│  Board: [1,0,2,  │
│         0,3,0,   │
│         ...]     │
│  Score: 42       │
└──────────────────┘
         │
         ▼
┌──────────────────┐
│  Memory Scan     │
│  Searching for:  │
│  - 81 bytes =    │
│    [1,0,2,0,3,0  │
│     ...]         │
│  - int32 = 42    │
└──────────────────┘
         │
         ▼
┌──────────────────┐
│  Results         │
│  Board found at: │
│  - 0x12AB3450    │
│  Score found at: │
│  - 0x12AB3500    │
│  - 0x12AB3504    │
│  - ... (200+)    │
└──────────────────┘

Time: T+10s
┌──────────────────┐
│  Screen Capture  │
│  Board: [1,0,2,  │
│         0,3,4,   │  ← Changed!
│         ...]     │
│  Score: 42       │  ← Same
└──────────────────┘
         │
         ▼
┌──────────────────┐
│  Memory Scan     │
│  Searching for:  │
│  - New board     │
│  - Score 42      │
└──────────────────┘
         │
         ▼
┌──────────────────┐
│  Results         │
│  Board found at: │
│  - 0x12AB3450 ✓  │  ← Same address!
│  Score found at: │
│  - 0x12AB3500 ✓  │  ← Still there
│  - 0x12AB3504    │
│  - ... (150+)    │  ← Fewer matches
└──────────────────┘

Time: T+20s
┌──────────────────┐
│  Screen Capture  │
│  Board: [1,0,2,  │
│         0,3,4,   │
│         5,...]   │  ← Changed!
│  Score: 52       │  ← Changed!
└──────────────────┘
         │
         ▼
┌──────────────────┐
│  Memory Scan     │
│  Searching for:  │
│  - New board     │
│  - Score 52      │
└──────────────────┘
         │
         ▼
┌──────────────────┐
│  Results         │
│  Board found at: │
│  - 0x12AB3450 ✓  │  ← Consistent!
│  Score found at: │
│  - 0x12AB3500 ✓  │  ← Still there!
│  - 0x12AB3508    │
│  - ... (180+)    │
└──────────────────┘
```

## Analysis Process

```
After collecting N snapshots:

┌─────────────────────────────────────────────────────────┐
│  Board Address Frequency Analysis                       │
│                                                          │
│  Address        │ Matches │ Percentage │ Confidence     │
│  ───────────────┼─────────┼────────────┼──────────────  │
│  0x12AB3450     │  10/10  │   100%     │ ✓ VERY HIGH   │
│  0x12AB3460     │   1/10  │    10%     │ ✗ LOW         │
│  0x12AB3470     │   0/10  │     0%     │ ✗ NONE        │
│                                                          │
│  Result: 0x12AB3450 is the board address                │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  Score Address Frequency Analysis                       │
│                                                          │
│  Address        │ Matches │ Percentage │ Confidence     │
│  ───────────────┼─────────┼────────────┼──────────────  │
│  0x12AB3500     │   8/10  │    80%     │ ✓ HIGH        │
│  0x12AB3504     │   5/10  │    50%     │ ~ MEDIUM      │
│  0x12AB3508     │   2/10  │    20%     │ ✗ LOW         │
│  0x12AB350C     │   1/10  │    10%     │ ✗ LOW         │
│  ... (200+)     │   1/10  │    10%     │ ✗ LOW         │
│                                                          │
│  Result: 0x12AB3500 is likely the score address         │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  Cross-Reference Validation                             │
│                                                          │
│  Board:  0x12AB3450                                     │
│  Score:  0x12AB3500                                     │
│  Offset: 0xB0 (176 bytes)                               │
│                                                          │
│  ✓ Addresses are close (< 1KB apart)                    │
│  ✓ Likely in same data structure                        │
│  ✓ Offset is reasonable for struct layout               │
└─────────────────────────────────────────────────────────┘
```

## Memory Structure Discovery

```
Reading memory around board address:

0x12AB3400: [padding/other data]
0x12AB3410: [padding/other data]
0x12AB3420: [padding/other data]
0x12AB3430: [padding/other data]
0x12AB3440: [padding/other data]
0x12AB3450: ┌─────────────────────────────┐
            │ BOARD (81 bytes)            │
            │ [1,0,2,0,3,4,5,0,0,         │
            │  0,0,0,6,0,0,0,0,0,         │
            │  ...]                       │
0x12AB34A1: └─────────────────────────────┘
0x12AB34A2: [padding - 94 bytes]
0x12AB3500: ┌─────────────────────────────┐
            │ SCORE (4 bytes)             │
            │ 0x34000000 (52 in decimal)  │
0x12AB3504: └─────────────────────────────┘
0x12AB3505: [padding - 75 bytes]
0x12AB3550: ┌─────────────────────────────┐
            │ NEXT BALLS? (3 bytes)       │
            │ [1, 3, 5]                   │
0x12AB3553: └─────────────────────────────┘
0x12AB3554: [other data...]

Discovered Structure:
┌──────────────────────────────────────┐
│  Game State Structure                │
│  ─────────────────────────────────   │
│  +0x00:  Board[81]      (81 bytes)   │
│  +0x51:  Padding        (94 bytes)   │
│  +0xB0:  Score          (4 bytes)    │
│  +0xB4:  Padding        (75 bytes)   │
│  +0x100: NextBalls[3]   (3 bytes)    │
│  ...                                 │
└──────────────────────────────────────┘
```

## Decision Tree

```
Start
  │
  ├─ Attach to process?
  │   ├─ Yes → Continue
  │   └─ No  → Error: Game not running
  │
  ├─ Screen capture working?
  │   ├─ Yes → Continue
  │   └─ No  → Error: Calibrate screen capture
  │
  ├─ Collect snapshots (10s intervals)
  │   │
  │   ├─ Snapshot 1: Board found? Score found?
  │   ├─ Snapshot 2: Same addresses?
  │   ├─ Snapshot 3: Still consistent?
  │   └─ ... Continue until Ctrl+C
  │
  ├─ Analyze board addresses
  │   │
  │   ├─ 100% match rate?
  │   │   └─ ✓ High confidence
  │   ├─ 80-99% match rate?
  │   │   └─ ✓ Good confidence
  │   ├─ 50-79% match rate?
  │   │   └─ ~ Medium confidence
  │   └─ <50% match rate?
  │       └─ ✗ Low confidence
  │
  ├─ Analyze score addresses
  │   │
  │   ├─ Multiple snapshots with same address?
  │   │   └─ ✓ Likely correct
  │   ├─ Address near board?
  │   │   └─ ✓ Increases confidence
  │   └─ Address far from board?
  │       └─ ~ May still be correct
  │
  └─ Output results
      ├─ Console: Human-readable analysis
      └─ JSON: Machine-readable data
```

## Success Criteria

```
High Confidence Result:
  ✓ Board address: 100% match rate
  ✓ Score address: 80%+ match rate
  ✓ Addresses are nearby (<1KB apart)
  ✓ Memory structure makes sense
  ✓ 10+ snapshots collected

Medium Confidence Result:
  ~ Board address: 80-99% match rate
  ~ Score address: 50-79% match rate
  ~ Addresses may be far apart
  ~ 5-9 snapshots collected

Low Confidence Result:
  ✗ Board address: <80% match rate
  ✗ Score address: <50% match rate
  ✗ Inconsistent results
  ✗ <5 snapshots collected
  → Recommendation: Collect more data
```

## Comparison with Interactive Tool

```
Tracking Tool (Automated):
┌─────────────────────────────────────┐
│ Start → Play → Wait → Stop → Done  │
│  (1-2 minutes, passive)             │
└─────────────────────────────────────┘

Interactive Tool (Manual):
┌─────────────────────────────────────┐
│ Start → Scan → Filter → Verify →   │
│ Filter → Verify → Done              │
│  (5-10 minutes, active)             │
└─────────────────────────────────────┘
```

## Conclusion

The tracking tool provides a fully automated way to discover memory addresses by:
1. Passively collecting data while you play
2. Statistically analyzing patterns
3. Identifying stable addresses
4. Providing high-confidence results

Perfect for users who want a hands-off approach to memory discovery!

