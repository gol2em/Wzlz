"""
Track game status every 10 seconds and analyze memory structure.

This script:
1. Reads game state from screen every 10 seconds
2. Scans memory for matching patterns
3. Analyzes memory structure to find grid and score locations
4. Builds a database of memory addresses and their patterns
5. Attempts to identify stable addresses for board and score
"""

import sys
import time
import json
import random
from typing import List, Dict, Optional, Tuple
import numpy as np
from datetime import datetime
from collections import defaultdict

try:
    from wzlz_ai.game_state_reader import GameStateReader
    from wzlz_ai.memory_reader import MemoryScanner
    from wzlz_ai.game_state import BallColor, Position, Move, GameConfig, GameState
    from wzlz_ai.game_client import GameClientEnvironment
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure all dependencies are installed:")
    print("  uv pip install pymem pywin32")
    sys.exit(1)


class MemoryAnalyzer:
    """Analyzes memory to find game state structure."""

    def __init__(self, process_name: str = "五子连珠.exe", window_title: str = "五子连珠5.2", auto_play: bool = True):
        """Initialize analyzer."""
        self.process_name = process_name
        self.window_title = window_title
        self.auto_play = auto_play

        # Initialize readers
        self.screen_reader = GameStateReader(window_title=window_title)
        self.memory_scanner = MemoryScanner(process_name)

        # Initialize game client environment for auto-play
        if self.auto_play:
            try:
                config = GameConfig()
                self.game_env = GameClientEnvironment(config)
                print("✓ Auto-play enabled - will make random moves between snapshots")
            except Exception as e:
                print(f"⚠ Could not initialize game client: {e}")
                print("  Auto-play disabled - you'll need to make moves manually")
                self.auto_play = False
                self.game_env = None
        else:
            self.game_env = None

        # Tracking data
        self.snapshots: List[Dict] = []
        self.board_candidates: Dict[int, int] = defaultdict(int)  # address -> match_count
        self.score_candidates: Dict[int, int] = defaultdict(int)  # address -> match_count

        # Game tracking
        self.reset_count = 0
        self.last_next_balls = None

        # Analysis results
        self.likely_board_address: Optional[int] = None
        self.likely_score_address: Optional[int] = None

    def attach(self) -> bool:
        """Attach to game process."""
        print(f"Attempting to attach to process: {self.process_name}")
        if self.memory_scanner.attach():
            print(f"✓ Successfully attached to game process!")
            print(f"  Base address: 0x{self.memory_scanner.base_address:X}")
            return True
        else:
            print(f"✗ Failed to attach to game process")
            return False

    def take_snapshot(self) -> Optional[Dict]:
        """Take a snapshot of current game state from screen and memory."""
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Taking snapshot...")

        # Read from screen
        state = self.screen_reader.read_game_state()
        if state is None:
            print("  ✗ Failed to read game state from screen")
            return None

        board = state.board
        score = state.score
        next_balls = state.next_balls

        # Read high score
        high_score = self.screen_reader.read_high_score()

        print(f"  Screen: Score={score}, High Score={high_score}, Balls={np.count_nonzero(board)}")
        print(f"  Next balls: {[ball.name for ball in next_balls] if next_balls else 'None'}")

        # Verify next_balls prediction from last snapshot
        if self.last_next_balls is not None and len(self.last_next_balls) > 0:
            print(f"  Last predicted next balls: {[ball.name for ball in self.last_next_balls]}")

        # Store current next_balls for next verification
        self.last_next_balls = next_balls

        # Search memory for board pattern
        print("  Searching memory for board pattern...")
        board_addresses = self._find_board_in_memory(board)
        print(f"    Found {len(board_addresses)} potential board addresses")

        # Search memory for score
        print("  Searching memory for score value...")
        score_addresses = self._find_score_in_memory(score)
        print(f"    Found {len(score_addresses)} potential score addresses")

        # Search memory for high score
        print("  Searching memory for high score value...")
        high_score_addresses = self._find_score_in_memory(high_score)
        print(f"    Found {len(high_score_addresses)} potential high score addresses")

        # Create snapshot
        snapshot = {
            'timestamp': datetime.now().isoformat(),
            'board': board.tolist(),
            'score': score,
            'high_score': high_score,
            'next_balls': [ball.value for ball in next_balls] if next_balls else [],
            'board_addresses': board_addresses,
            'score_addresses': score_addresses,
            'high_score_addresses': high_score_addresses,
        }

        self.snapshots.append(snapshot)

        # Update candidates
        for addr in board_addresses:
            self.board_candidates[addr] += 1
        for addr in score_addresses:
            self.score_candidates[addr] += 1

        print(f"  ✓ Snapshot {len(self.snapshots)} captured")

        return snapshot

    def _find_board_in_memory(self, board: np.ndarray) -> List[int]:
        """Find potential board addresses in memory."""
        addresses = []

        # Convert board to bytes (flatten and convert to int8)
        board_bytes = board.flatten().astype(np.int8).tobytes()

        # Search in each module
        try:
            for module in self.memory_scanner.pm.list_modules():
                try:
                    module_base = module.lpBaseOfDll
                    module_size = module.SizeOfImage

                    # Read module memory
                    memory = self.memory_scanner.pm.read_bytes(module_base, module_size)

                    # Search for exact match
                    offset = 0
                    while offset < len(memory) - 81:
                        if memory[offset:offset + 81] == board_bytes:
                            addresses.append(module_base + offset)
                        offset += 1

                except Exception:
                    continue
        except Exception as e:
            print(f"    Error scanning memory: {e}")

        return addresses

    def _find_score_in_memory(self, score: int) -> List[int]:
        """Find potential score addresses in memory."""
        if score == 0:
            # Don't search for 0, too many matches
            return []

        return self.memory_scanner.scan_for_value(score, 'int32')

    def analyze_patterns(self):
        """Analyze collected snapshots to identify patterns."""
        print("\n" + "=" * 80)
        print("ANALYSIS RESULTS")
        print("=" * 80)

        if len(self.snapshots) < 2:
            print("Not enough snapshots for analysis (need at least 2)")
            return

        print(f"\nTotal snapshots: {len(self.snapshots)}")

        # Analyze board addresses
        print("\n--- Board Address Analysis ---")
        self._analyze_board_addresses()

        # Analyze score addresses
        print("\n--- Score Address Analysis ---")
        self._analyze_score_addresses()

        # Cross-reference analysis
        print("\n--- Cross-Reference Analysis ---")
        self._cross_reference_analysis()

        # Memory structure analysis
        print("\n--- Memory Structure Analysis ---")
        self._analyze_memory_structure()

    def _analyze_board_addresses(self):
        """Analyze board address candidates."""
        if not self.board_candidates:
            print("  No board candidates found")
            return

        # Sort by match count
        sorted_candidates = sorted(
            self.board_candidates.items(),
            key=lambda x: x[1],
            reverse=True
        )

        print(f"  Total unique addresses found: {len(sorted_candidates)}")
        print(f"  Top candidates (by consistency):")

        for i, (addr, count) in enumerate(sorted_candidates[:10]):
            percentage = (count / len(self.snapshots)) * 100
            print(f"    [{i+1}] 0x{addr:X} - matched {count}/{len(self.snapshots)} times ({percentage:.1f}%)")

            if percentage >= 80:
                self.likely_board_address = addr

        if self.likely_board_address:
            print(f"\n  ✓ LIKELY BOARD ADDRESS: 0x{self.likely_board_address:X}")
        else:
            print(f"\n  ⚠ No consistent board address found (addresses may be changing)")

    def _analyze_score_addresses(self):
        """Analyze score address candidates."""
        if not self.score_candidates:
            print("  No score candidates found")
            return

        # Sort by match count
        sorted_candidates = sorted(
            self.score_candidates.items(),
            key=lambda x: x[1],
            reverse=True
        )

        print(f"  Total unique addresses found: {len(sorted_candidates)}")

        # Filter candidates that appear in multiple snapshots
        consistent_candidates = [(addr, count) for addr, count in sorted_candidates if count >= 2]

        if consistent_candidates:
            print(f"  Consistent candidates (appeared 2+ times):")
            for i, (addr, count) in enumerate(consistent_candidates[:20]):
                percentage = (count / len(self.snapshots)) * 100
                print(f"    [{i+1}] 0x{addr:X} - matched {count}/{len(self.snapshots)} times ({percentage:.1f}%)")

                if percentage >= 80:
                    self.likely_score_address = addr

        if self.likely_score_address:
            print(f"\n  ✓ LIKELY SCORE ADDRESS: 0x{self.likely_score_address:X}")
        else:
            print(f"\n  ⚠ No consistent score address found")
            print(f"     This is normal if score changed between snapshots")

    def _cross_reference_analysis(self):
        """Cross-reference board and score addresses."""
        if not self.likely_board_address or not self.likely_score_address:
            print("  Need both board and score addresses for cross-reference")
            return

        # Calculate offset between board and score
        offset = self.likely_score_address - self.likely_board_address
        print(f"  Board address:  0x{self.likely_board_address:X}")
        print(f"  Score address:  0x{self.likely_score_address:X}")
        print(f"  Offset:         {offset} bytes (0x{offset:X})")

        if abs(offset) < 10000:
            print(f"  ✓ Addresses are close together - likely in same data structure!")
        else:
            print(f"  ⚠ Addresses are far apart - may be in different structures")

    def _analyze_memory_structure(self):
        """Analyze memory structure around found addresses."""
        if not self.likely_board_address:
            print("  No board address to analyze")
            return

        print(f"  Analyzing memory around board address 0x{self.likely_board_address:X}...")

        # Read memory around board address
        try:
            # Read 200 bytes before and after
            start_addr = self.likely_board_address - 200
            memory = self.memory_scanner.read_bytes(start_addr, 481)  # 200 + 81 + 200

            if memory:
                print(f"\n  Memory dump (showing 50 bytes before board):")
                self._print_memory_dump(start_addr + 150, memory[150:231])

                # Look for patterns
                print(f"\n  Looking for patterns:")

                # Check if there are other arrays nearby
                board_start = 200
                board_end = 281

                # Check before board
                before = memory[:board_start]
                self._analyze_nearby_data(before, "before board", start_addr)

                # Check after board
                after = memory[board_end:]
                self._analyze_nearby_data(after, "after board", start_addr + board_end)

        except Exception as e:
            print(f"  Error reading memory: {e}")

    def _analyze_nearby_data(self, data: bytes, location: str, base_addr: int):
        """Analyze data near the board."""
        # Look for potential score (4-byte integers)
        for i in range(0, len(data) - 4, 4):
            value = int.from_bytes(data[i:i+4], 'little', signed=False)
            # Check if it could be a score (reasonable range)
            if 0 < value < 100000:
                addr = base_addr + i
                print(f"    Potential score at offset +{i}: {value} (0x{addr:X})")

        # Look for potential next balls (3 consecutive bytes in range 1-7)
        for i in range(len(data) - 3):
            if all(1 <= b <= 7 for b in data[i:i+3]):
                addr = base_addr + i
                balls = list(data[i:i+3])
                print(f"    Potential next balls at offset +{i}: {balls} (0x{addr:X})")

    def _print_memory_dump(self, start_addr: int, data: bytes):
        """Print memory dump in hex format."""
        for i in range(0, len(data), 16):
            addr = start_addr + i
            hex_str = ' '.join(f'{b:02X}' for b in data[i:i+16])
            ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data[i:i+16])
            print(f"    0x{addr:X}: {hex_str:<48} {ascii_str}")

    def save_results(self, filename: str = "memory_analysis_results.json"):
        """Save analysis results to file."""
        results = {
            'process_name': self.process_name,
            'window_title': self.window_title,
            'analysis_time': datetime.now().isoformat(),
            'snapshot_count': len(self.snapshots),
            'likely_board_address': f"0x{self.likely_board_address:X}" if self.likely_board_address else None,
            'likely_score_address': f"0x{self.likely_score_address:X}" if self.likely_score_address else None,
            'board_candidates': {f"0x{addr:X}": count for addr, count in self.board_candidates.items()},
            'score_candidates': {f"0x{addr:X}": count for addr, count in self.score_candidates.items()},
            'snapshots': self.snapshots,
        }

        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\n✓ Results saved to {filename}")

    def print_board(self, board: np.ndarray):
        """Print board in readable format."""
        color_symbols = {
            BallColor.EMPTY: '·',
            BallColor.RED: 'R',
            BallColor.GREEN: 'G',
            BallColor.BLUE: 'B',
            BallColor.BROWN: 'N',
            BallColor.MAGENTA: 'M',
            BallColor.YELLOW: 'Y',
            BallColor.CYAN: 'C',
        }

        print("  0 1 2 3 4 5 6 7 8")
        for i, row in enumerate(board):
            symbols = [color_symbols.get(BallColor(cell), '?') for cell in row]
            print(f"{i} {' '.join(symbols)}")

    def make_random_move(self) -> bool:
        """Make a random valid move in the game, prioritizing scoring moves."""
        if not self.auto_play or not self.game_env:
            return False

        try:
            # Bring window to front before making moves
            self.game_env._bring_window_to_front()

            # Read current state using game_env (same as test_full_game_with_reset.py)
            state = self.game_env.get_state()
            if state is None:
                return False

            # Count balls on board
            ball_count = sum(1 for row in range(9) for col in range(9) if state.board[row, col] != 0)

            # If no balls on board, start a new game
            if ball_count == 0:
                print(f"    ⚠ No balls on board, starting new game...")
                self.game_env.reset()
                self.reset_count += 1
                return True

            # Get valid moves using pathfinding
            valid_moves = self.game_env.get_valid_moves(state)

            if not valid_moves:
                print(f"    ⚠ No valid moves available (game over?)")
                # Try to reset the game
                self.game_env.reset()
                self.reset_count += 1
                return True

            # Find moves that create matches (score points)
            scoring_moves = self._find_scoring_moves(state, valid_moves)

            if scoring_moves:
                move = random.choice(scoring_moves)
                print(f"    Making SCORING move: {move} (will create match!)")
            else:
                # Pick a random valid move
                move = random.choice(valid_moves)
                print(f"    Making move: {move}")

            # Execute the move
            result = self.game_env.execute_move(move)

            if result and result.success:
                if result.points_earned > 0:
                    print(f"    ✓ Move successful! Scored {result.points_earned} points!")
                else:
                    print(f"    ✓ Move successful!")
                return True
            elif result is None:
                print(f"    ⚠ Game reset detected (popup dismissed)")
                self.reset_count += 1
                return True
            else:
                print(f"    ⚠ Move failed: {result.error_message if result else 'Unknown error'}")
                return False

        except Exception as e:
            print(f"    ✗ Error making move: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _find_scoring_moves(self, state: GameState, valid_moves: List[Move]) -> List[Move]:
        """Find moves that will create matches and score points."""
        from wzlz_ai.game_environment import SimulationEnvironment

        scoring_moves = []

        # Create a simulation environment to test moves
        sim_env = SimulationEnvironment(self.game_env.config)

        for move in valid_moves:
            # Clone the state
            test_state = state.clone()
            sim_env._current_state = test_state

            # Simulate the move
            result = sim_env.execute_move(move)

            # Check if this move scores points
            if result and result.success and result.points_earned > 0:
                scoring_moves.append(move)

        return scoring_moves



def main():
    """Main entry point."""
    print("=" * 80)
    print("Memory Structure Analyzer with Auto-Play")
    print("=" * 80)
    print()
    print("This script will track the game state every 10 seconds and analyze")
    print("memory to find where the board and score are stored.")
    print()
    print("Auto-play is ENABLED - the script will make random moves between")
    print("snapshots to ensure the game state changes naturally.")
    print()

    # Configuration
    INTERVAL = 10  # seconds
    MIN_SNAPSHOTS = 5
    MOVES_PER_INTERVAL = 2  # Number of moves to make between snapshots
    MAX_RESETS = 2  # Stop after this many game resets

    analyzer = MemoryAnalyzer(auto_play=True)

    # Attach to game
    if not analyzer.attach():
        print("\nMake sure the game is running and try again.")
        return

    print("\n" + "=" * 80)
    print("Starting tracking...")
    print(f"Will take snapshots every {INTERVAL} seconds")
    if analyzer.auto_play:
        print(f"Will make {MOVES_PER_INTERVAL} moves between snapshots (prioritizing scoring moves)")
        print(f"Will stop after {MAX_RESETS} game resets")
    print("Press Ctrl+C to stop and analyze")
    print("=" * 80)

    try:
        snapshot_count = 0
        while True:
            # Check if we've reached max resets
            if analyzer.reset_count >= MAX_RESETS:
                print(f"\n✓ Reached {MAX_RESETS} game resets - stopping data collection")
                break

            snapshot = analyzer.take_snapshot()

            if snapshot:
                snapshot_count += 1

                if snapshot_count >= MIN_SNAPSHOTS:
                    print(f"\n  ({snapshot_count} snapshots collected, {analyzer.reset_count} resets)")

            # Make random moves if auto-play is enabled
            if analyzer.auto_play and snapshot_count > 0:
                print(f"\n  Making {MOVES_PER_INTERVAL} moves...")
                moves_made = 0
                for i in range(MOVES_PER_INTERVAL):
                    if analyzer.make_random_move():
                        moves_made += 1
                        time.sleep(2)  # Wait for move animation

                    # Check if we've reached max resets during moves
                    if analyzer.reset_count >= MAX_RESETS:
                        print(f"\n✓ Reached {MAX_RESETS} game resets during moves")
                        break

                if moves_made > 0:
                    print(f"  ✓ Made {moves_made} moves")
                else:
                    print(f"  ⚠ No moves made (you may need to make moves manually)")

            # Check again before waiting
            if analyzer.reset_count >= MAX_RESETS:
                break

            # Wait for next snapshot
            wait_time = INTERVAL if analyzer.auto_play else INTERVAL
            print(f"\n  Waiting {wait_time} seconds for next snapshot...")
            time.sleep(wait_time)

    except KeyboardInterrupt:
        print("\n\nStopping tracking (interrupted by user)...")

    # Analyze results
    if len(analyzer.snapshots) >= 2:
        analyzer.analyze_patterns()
        analyzer.save_results()

        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)

        if analyzer.likely_board_address:
            print(f"\n✓ Board Address Found: 0x{analyzer.likely_board_address:X}")
            print(f"  Use this in your memory reader:")
            print(f"  reader.board_address = 0x{analyzer.likely_board_address:X}")

        if analyzer.likely_score_address:
            print(f"\n✓ Score Address Found: 0x{analyzer.likely_score_address:X}")
            print(f"  Use this in your memory reader:")
            print(f"  reader.score_address = 0x{analyzer.likely_score_address:X}")

        if not analyzer.likely_board_address and not analyzer.likely_score_address:
            print("\n⚠ No consistent addresses found.")
            print("  This could mean:")
            print("  - Addresses change on each game restart (need pointer chains)")
            print("  - Not enough snapshots collected")
            print("  - Game state didn't change enough between snapshots")
            print("\n  Try:")
            print("  - Restart the script and collect more snapshots")
            print("  - Make moves in the game between snapshots")
            print("  - Use the interactive explore_memory.py tool instead")
    else:
        print("\nNot enough snapshots collected for analysis")


if __name__ == "__main__":
    main()

