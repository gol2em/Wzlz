"""
Memory reader for extracting game state directly from process memory.

This module provides tools to read the Wzlz game state from memory,
which is more reliable than screen capture and doesn't depend on resolution.
"""

from typing import Optional, List, Tuple, Dict
import struct
import numpy as np

try:
    import pymem
    import pymem.process
    PYMEM_AVAILABLE = True
except ImportError:
    PYMEM_AVAILABLE = False

from .game_state import BallColor, GameState, GameConfig


class MemoryPattern:
    """Represents a memory pattern to search for."""
    
    def __init__(self, pattern: bytes, mask: Optional[bytes] = None):
        """
        Initialize memory pattern.
        
        Args:
            pattern: Byte pattern to search for
            mask: Optional mask (b'x' = must match, b'?' = wildcard)
        """
        self.pattern = pattern
        self.mask = mask or b'x' * len(pattern)
    
    @classmethod
    def from_string(cls, pattern_str: str) -> 'MemoryPattern':
        """
        Create pattern from string like "48 8B ? ? 89 45".
        
        Args:
            pattern_str: Pattern string with hex bytes and ? for wildcards
            
        Returns:
            MemoryPattern object
        """
        parts = pattern_str.split()
        pattern = b''
        mask = b''
        
        for part in parts:
            if part == '?':
                pattern += b'\x00'
                mask += b'?'
            else:
                pattern += bytes.fromhex(part)
                mask += b'x'
        
        return cls(pattern, mask)


class MemoryScanner:
    """Scans process memory for patterns and values."""
    
    def __init__(self, process_name: str = "wzlz.exe"):
        """
        Initialize memory scanner.
        
        Args:
            process_name: Name of the game process
        """
        if not PYMEM_AVAILABLE:
            raise ImportError("pymem is required for memory reading. Install with: pip install pymem")
        
        self.process_name = process_name
        self.pm: Optional[pymem.Pymem] = None
        self.base_address: Optional[int] = None
    
    def attach(self) -> bool:
        """
        Attach to the game process.
        
        Returns:
            True if successfully attached, False otherwise
        """
        try:
            self.pm = pymem.Pymem(self.process_name)
            self.base_address = self.pm.base_address
            return True
        except Exception as e:
            print(f"Failed to attach to process '{self.process_name}': {e}")
            return False
    
    def scan_for_value(self, value: int, value_type: str = 'int32') -> List[int]:
        """
        Scan memory for a specific value.
        
        Args:
            value: Value to search for
            value_type: Type of value ('int8', 'int16', 'int32', 'int64', 'float', 'double')
            
        Returns:
            List of memory addresses where the value was found
        """
        if not self.pm:
            return []
        
        addresses = []
        
        # Convert value to bytes based on type
        type_map = {
            'int8': ('b', 1),
            'int16': ('h', 2),
            'int32': ('i', 4),
            'int64': ('q', 8),
            'float': ('f', 4),
            'double': ('d', 8),
        }
        
        if value_type not in type_map:
            return []
        
        fmt, size = type_map[value_type]
        search_bytes = struct.pack(fmt, value)
        
        # Scan readable memory regions
        for module in self.pm.list_modules():
            try:
                module_base = module.lpBaseOfDll
                module_size = module.SizeOfImage
                
                # Read module memory
                memory = self.pm.read_bytes(module_base, module_size)
                
                # Search for pattern
                offset = 0
                while offset < len(memory) - size:
                    if memory[offset:offset + size] == search_bytes:
                        addresses.append(module_base + offset)
                    offset += 1
                    
            except Exception:
                continue
        
        return addresses
    
    def filter_addresses(self, addresses: List[int], value: int, value_type: str = 'int32') -> List[int]:
        """
        Filter addresses that still contain the specified value.
        
        Args:
            addresses: List of addresses to check
            value: Expected value
            value_type: Type of value
            
        Returns:
            Filtered list of addresses
        """
        if not self.pm:
            return []
        
        type_map = {
            'int8': ('b', 1),
            'int16': ('h', 2),
            'int32': ('i', 4),
            'int64': ('q', 8),
            'float': ('f', 4),
            'double': ('d', 8),
        }
        
        fmt, size = type_map.get(value_type, ('i', 4))
        filtered = []
        
        for addr in addresses:
            try:
                data = self.pm.read_bytes(addr, size)
                current_value = struct.unpack(fmt, data)[0]
                if current_value == value:
                    filtered.append(addr)
            except Exception:
                continue
        
        return filtered
    
    def read_value(self, address: int, value_type: str = 'int32') -> Optional[int]:
        """
        Read a value from memory.
        
        Args:
            address: Memory address to read from
            value_type: Type of value to read
            
        Returns:
            Value at the address, or None if failed
        """
        if not self.pm:
            return None
        
        try:
            type_map = {
                'int8': self.pm.read_char,
                'int16': self.pm.read_short,
                'int32': self.pm.read_int,
                'int64': self.pm.read_longlong,
                'float': self.pm.read_float,
                'double': self.pm.read_double,
            }
            
            read_func = type_map.get(value_type)
            if read_func:
                return read_func(address)
        except Exception:
            pass
        
        return None
    
    def read_bytes(self, address: int, size: int) -> Optional[bytes]:
        """
        Read raw bytes from memory.
        
        Args:
            address: Memory address to read from
            size: Number of bytes to read
            
        Returns:
            Bytes read, or None if failed
        """
        if not self.pm:
            return None
        
        try:
            return self.pm.read_bytes(address, size)
        except Exception:
            return None
    
    def read_array(self, address: int, count: int, value_type: str = 'int8') -> Optional[List[int]]:
        """
        Read an array of values from memory.
        
        Args:
            address: Starting memory address
            count: Number of elements to read
            value_type: Type of each element
            
        Returns:
            List of values, or None if failed
        """
        type_map = {
            'int8': ('b', 1),
            'int16': ('h', 2),
            'int32': ('i', 4),
            'int64': ('q', 8),
        }
        
        fmt, size = type_map.get(value_type, ('b', 1))
        
        data = self.read_bytes(address, count * size)
        if data is None:
            return None
        
        try:
            return list(struct.unpack(f'{count}{fmt}', data))
        except Exception:
            return None


class GameMemoryReader:
    """High-level interface for reading Wzlz game state from memory."""
    
    def __init__(self, process_name: str = "wzlz.exe"):
        """
        Initialize game memory reader.
        
        Args:
            process_name: Name of the game process
        """
        self.scanner = MemoryScanner(process_name)
        self.board_address: Optional[int] = None
        self.score_address: Optional[int] = None
        self.next_balls_address: Optional[int] = None
    
    def attach(self) -> bool:
        """Attach to the game process."""
        return self.scanner.attach()
    
    def find_board_address(self, known_board: Optional[np.ndarray] = None) -> List[int]:
        """
        Find potential addresses for the game board.
        
        Args:
            known_board: Optional known board state to search for
            
        Returns:
            List of potential board addresses
        """
        if known_board is not None:
            # Search for the board pattern
            # The board is likely stored as 81 consecutive bytes (9x9 grid)
            candidates = []
            
            # Try to find sequences that match the board
            for module in self.scanner.pm.list_modules():
                try:
                    module_base = module.lpBaseOfDll
                    module_size = module.SizeOfImage
                    memory = self.scanner.pm.read_bytes(module_base, module_size)
                    
                    # Convert board to bytes
                    board_bytes = known_board.flatten().astype(np.int8).tobytes()
                    
                    # Search for exact match
                    offset = 0
                    while offset < len(memory) - 81:
                        if memory[offset:offset + 81] == board_bytes:
                            candidates.append(module_base + offset)
                        offset += 1
                        
                except Exception:
                    continue
            
            return candidates
        
        return []
    
    def find_score_address(self, known_score: int) -> List[int]:
        """
        Find potential addresses for the score.
        
        Args:
            known_score: Known score value
            
        Returns:
            List of potential score addresses
        """
        return self.scanner.scan_for_value(known_score, 'int32')
    
    def read_board(self, address: int) -> Optional[np.ndarray]:
        """
        Read board state from memory.
        
        Args:
            address: Memory address of the board
            
        Returns:
            9x9 numpy array of ball colors, or None if failed
        """
        data = self.scanner.read_array(address, 81, 'int8')
        if data is None:
            return None
        
        return np.array(data, dtype=np.int8).reshape(9, 9)
    
    def read_score(self, address: int) -> Optional[int]:
        """
        Read score from memory.
        
        Args:
            address: Memory address of the score
            
        Returns:
            Score value, or None if failed
        """
        return self.scanner.read_value(address, 'int32')
    
    def read_game_state(self, 
                       board_address: Optional[int] = None,
                       score_address: Optional[int] = None) -> Optional[GameState]:
        """
        Read complete game state from memory.
        
        Args:
            board_address: Memory address of the board (uses cached if None)
            score_address: Memory address of the score (uses cached if None)
            
        Returns:
            GameState object, or None if failed
        """
        if board_address is None:
            board_address = self.board_address
        if score_address is None:
            score_address = self.score_address
        
        if board_address is None:
            return None
        
        board = self.read_board(board_address)
        if board is None:
            return None
        
        score = 0
        if score_address is not None:
            score_val = self.read_score(score_address)
            if score_val is not None:
                score = score_val
        
        return GameState(
            board=board,
            score=score,
            next_balls=[],
            config=GameConfig()
        )

