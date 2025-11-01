"""
Interactive memory exploration tool for finding game state in memory.

This tool helps you discover where the game stores its state in memory
by performing iterative scans and filtering.

Usage:
    1. Start the Wzlz game
    2. Run this script
    3. Follow the interactive prompts to find memory addresses
"""

import sys
import time
from typing import List, Optional
import numpy as np

try:
    from wzlz_ai.memory_reader import GameMemoryReader, MemoryScanner
    from wzlz_ai.game_state_reader import GameStateReader
    from wzlz_ai.game_state import BallColor
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure pymem is installed: pip install pymem")
    sys.exit(1)


class MemoryExplorer:
    """Interactive tool for exploring game memory."""
    
    def __init__(self, process_name: str = "wzlz.exe"):
        """Initialize memory explorer."""
        self.process_name = process_name
        self.memory_reader = GameMemoryReader(process_name)
        self.screen_reader: Optional[GameStateReader] = None
        
        # Candidate addresses
        self.board_candidates: List[int] = []
        self.score_candidates: List[int] = []
        
        # Confirmed addresses
        self.board_address: Optional[int] = None
        self.score_address: Optional[int] = None
    
    def attach_to_game(self) -> bool:
        """Attach to the game process."""
        print(f"Attempting to attach to process: {self.process_name}")
        if self.memory_reader.attach():
            print("✓ Successfully attached to game process!")
            print(f"  Base address: 0x{self.memory_reader.scanner.base_address:X}")
            return True
        else:
            print("✗ Failed to attach to game process")
            print(f"  Make sure the game is running and the process name is correct")
            return False
    
    def init_screen_reader(self, window_title: str = "五子连珠5.2") -> bool:
        """Initialize screen reader for comparison."""
        try:
            self.screen_reader = GameStateReader(window_title=window_title)
            print(f"✓ Screen reader initialized for window: {window_title}")
            return True
        except Exception as e:
            print(f"✗ Failed to initialize screen reader: {e}")
            return False
    
    def find_board_by_screen_comparison(self) -> bool:
        """Find board address by comparing with screen capture."""
        if not self.screen_reader:
            print("Screen reader not initialized")
            return False
        
        print("\n=== Finding Board Address ===")
        print("Reading current board state from screen...")
        
        board = self.screen_reader.read_board()
        if board is None:
            print("✗ Failed to read board from screen")
            return False
        
        print("✓ Board read from screen:")
        self._print_board(board)
        
        print("\nSearching memory for matching board pattern...")
        candidates = self.memory_reader.find_board_address(board)
        
        if not candidates:
            print("✗ No matching board patterns found in memory")
            return False
        
        print(f"✓ Found {len(candidates)} potential board address(es):")
        for i, addr in enumerate(candidates):
            print(f"  [{i}] 0x{addr:X}")
        
        self.board_candidates = candidates
        
        if len(candidates) == 1:
            self.board_address = candidates[0]
            print(f"\n✓ Board address confirmed: 0x{self.board_address:X}")
            return True
        
        return True
    
    def find_score_by_screen_comparison(self) -> bool:
        """Find score address by comparing with screen capture."""
        if not self.screen_reader:
            print("Screen reader not initialized")
            return False
        
        print("\n=== Finding Score Address ===")
        print("Reading current score from screen...")
        
        score = self.screen_reader.read_current_score()
        print(f"✓ Score read from screen: {score}")
        
        print("\nSearching memory for matching score value...")
        candidates = self.memory_reader.find_score_address(score)
        
        if not candidates:
            print("✗ No matching score values found in memory")
            return False
        
        print(f"✓ Found {len(candidates)} potential score address(es)")
        
        if len(candidates) > 100:
            print(f"  Too many candidates ({len(candidates)}). Need to filter...")
            self.score_candidates = candidates
            return True
        
        for i, addr in enumerate(candidates[:20]):  # Show first 20
            print(f"  [{i}] 0x{addr:X}")
        
        if len(candidates) > 20:
            print(f"  ... and {len(candidates) - 20} more")
        
        self.score_candidates = candidates
        return True
    
    def filter_score_candidates(self) -> bool:
        """Filter score candidates by waiting for score to change."""
        if not self.score_candidates:
            print("No score candidates to filter")
            return False
        
        print("\n=== Filtering Score Candidates ===")
        print("Make a move in the game that changes the score...")
        input("Press Enter when ready to read new score from screen...")
        
        new_score = self.screen_reader.read_current_score()
        print(f"New score from screen: {new_score}")
        
        print("Filtering candidates...")
        filtered = self.memory_reader.scanner.filter_addresses(
            self.score_candidates, new_score, 'int32'
        )
        
        print(f"✓ Filtered from {len(self.score_candidates)} to {len(filtered)} candidates")
        
        if len(filtered) <= 10:
            for i, addr in enumerate(filtered):
                print(f"  [{i}] 0x{addr:X}")
        
        self.score_candidates = filtered
        
        if len(filtered) == 1:
            self.score_address = filtered[0]
            print(f"\n✓ Score address confirmed: 0x{self.score_address:X}")
            return True
        
        return len(filtered) > 0
    
    def verify_board_address(self, address: int) -> bool:
        """Verify a board address by reading and comparing."""
        print(f"\nVerifying board address: 0x{address:X}")
        
        # Read from memory
        mem_board = self.memory_reader.read_board(address)
        if mem_board is None:
            print("✗ Failed to read board from memory")
            return False
        
        print("Board from memory:")
        self._print_board(mem_board)
        
        # Compare with screen if available
        if self.screen_reader:
            screen_board = self.screen_reader.read_board()
            if screen_board is not None:
                if np.array_equal(mem_board, screen_board):
                    print("✓ Memory board matches screen board!")
                    return True
                else:
                    print("✗ Memory board does NOT match screen board")
                    return False
        
        return True
    
    def verify_score_address(self, address: int) -> bool:
        """Verify a score address by reading and comparing."""
        print(f"\nVerifying score address: 0x{address:X}")
        
        # Read from memory
        mem_score = self.memory_reader.read_score(address)
        if mem_score is None:
            print("✗ Failed to read score from memory")
            return False
        
        print(f"Score from memory: {mem_score}")
        
        # Compare with screen if available
        if self.screen_reader:
            screen_score = self.screen_reader.read_current_score()
            if mem_score == screen_score:
                print("✓ Memory score matches screen score!")
                return True
            else:
                print(f"✗ Memory score ({mem_score}) does NOT match screen score ({screen_score})")
                return False
        
        return True
    
    def save_addresses(self, filename: str = "memory_addresses.txt"):
        """Save discovered addresses to file."""
        with open(filename, 'w') as f:
            if self.board_address:
                f.write(f"board_address=0x{self.board_address:X}\n")
            if self.score_address:
                f.write(f"score_address=0x{self.score_address:X}\n")
            
            if self.board_candidates:
                f.write(f"\nboard_candidates=\n")
                for addr in self.board_candidates:
                    f.write(f"  0x{addr:X}\n")
            
            if self.score_candidates:
                f.write(f"\nscore_candidates=\n")
                for addr in self.score_candidates[:50]:  # Save first 50
                    f.write(f"  0x{addr:X}\n")
        
        print(f"\n✓ Addresses saved to {filename}")
    
    def _print_board(self, board: np.ndarray):
        """Print board in a readable format."""
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
    
    def run_interactive(self):
        """Run interactive exploration session."""
        print("=" * 60)
        print("Wzlz Memory Explorer")
        print("=" * 60)
        
        # Step 1: Attach to process
        if not self.attach_to_game():
            return
        
        print("\n" + "=" * 60)
        
        # Step 2: Initialize screen reader (optional but recommended)
        use_screen = input("Use screen reader for comparison? (y/n): ").lower() == 'y'
        if use_screen:
            self.init_screen_reader()
        
        # Step 3: Find board address
        print("\n" + "=" * 60)
        if use_screen and self.screen_reader:
            self.find_board_by_screen_comparison()
        
        # Step 4: Find score address
        if use_screen and self.screen_reader:
            self.find_score_by_screen_comparison()
            
            # Filter if too many candidates
            while len(self.score_candidates) > 10:
                if input("\nFilter score candidates? (y/n): ").lower() == 'y':
                    if not self.filter_score_candidates():
                        break
                else:
                    break
        
        # Step 5: Verify addresses
        print("\n" + "=" * 60)
        print("=== Verification ===")
        
        if self.board_candidates:
            if len(self.board_candidates) == 1:
                self.verify_board_address(self.board_candidates[0])
                self.board_address = self.board_candidates[0]
            else:
                print(f"\nMultiple board candidates found. Testing each...")
                for addr in self.board_candidates:
                    if self.verify_board_address(addr):
                        self.board_address = addr
                        break
        
        if self.score_candidates and len(self.score_candidates) <= 10:
            for addr in self.score_candidates:
                if self.verify_score_address(addr):
                    self.score_address = addr
                    break
        
        # Step 6: Save results
        print("\n" + "=" * 60)
        print("=== Results ===")
        if self.board_address:
            print(f"✓ Board address: 0x{self.board_address:X}")
        if self.score_address:
            print(f"✓ Score address: 0x{self.score_address:X}")
        
        if self.board_address or self.score_address:
            if input("\nSave addresses to file? (y/n): ").lower() == 'y':
                self.save_addresses()


def main():
    """Main entry point."""
    explorer = MemoryExplorer()
    explorer.run_interactive()


if __name__ == "__main__":
    main()

