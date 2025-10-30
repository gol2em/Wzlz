"""
Simple test to verify the framework works without external dependencies.
"""

from wzlz_ai import GameState, GameConfig, Position, Move, BallColor
from wzlz_ai import SimulationEnvironment


def test_game_state():
    """Test GameState creation and manipulation."""
    print("Testing GameState...")
    
    # Create empty state
    state = GameState.create_empty(9, 9)
    assert state.rows == 9
    assert state.cols == 9
    assert state.score == 0
    
    # Test position operations
    pos = Position(3, 4)
    assert state.is_empty(pos)
    
    # Set a ball
    state.set_cell(pos, BallColor.RED)
    assert not state.is_empty(pos)
    assert state.get_cell(pos) == BallColor.RED
    
    # Test cloning
    cloned = state.clone()
    cloned.score = 100
    assert state.score == 0  # Original unchanged
    assert cloned.score == 100
    
    print("✓ GameState tests passed")


def test_simulation_environment():
    """Test SimulationEnvironment."""
    print("\nTesting SimulationEnvironment...")
    
    config = GameConfig(rows=9, cols=9, colors_count=7)
    env = SimulationEnvironment(config, seed=42)
    
    # Test reset
    state = env.reset()
    assert state.rows == 9
    assert state.cols == 9
    
    # Should have initial balls
    occupied = state.get_occupied_positions()
    assert len(occupied) == config.initial_balls
    
    # Should have next balls preview
    assert len(state.next_balls) == config.balls_per_turn
    
    print(f"✓ Initial state has {len(occupied)} balls")
    print(f"✓ Next balls: {[b.name for b in state.next_balls]}")
    
    # Test valid moves
    moves = env.get_valid_moves()
    print(f"✓ Found {len(moves)} valid moves")
    
    # Test pathfinding
    if len(occupied) > 0 and len(state.get_empty_positions()) > 0:
        from_pos = occupied[0]
        to_pos = state.get_empty_positions()[0]
        
        path_exists, path = env.is_path_clear(from_pos, to_pos)
        print(f"✓ Path from {from_pos} to {to_pos}: {path_exists}")
    
    print("✓ SimulationEnvironment tests passed")


def test_move_execution():
    """Test executing moves."""
    print("\nTesting move execution...")
    
    config = GameConfig(rows=9, cols=9, colors_count=7)
    env = SimulationEnvironment(config, seed=42)
    
    state = env.reset()
    initial_score = state.score
    
    # Get and execute a valid move
    moves = env.get_valid_moves()
    
    if moves:
        move = moves[0]
        print(f"Executing move: {move}")
        
        result = env.execute_move(move)
        
        assert result.success
        assert result.new_state is not None
        print(f"✓ Move executed successfully")
        print(f"  Points earned: {result.points_earned}")
        print(f"  Balls removed: {len(result.balls_removed)}")
        print(f"  New balls added: {len(result.new_balls_added)}")
        print(f"  Path length: {len(result.path)}")
    else:
        print("⚠ No valid moves available")
    
    print("✓ Move execution tests passed")


def test_game_loop():
    """Test a simple game loop."""
    print("\nTesting game loop...")
    
    config = GameConfig(rows=9, cols=9, colors_count=7)
    env = SimulationEnvironment(config, seed=42)
    
    state = env.reset()
    
    max_moves = 5
    for i in range(max_moves):
        moves = env.get_valid_moves()
        
        if not moves:
            print(f"Game over after {i} moves")
            break
        
        # Execute first valid move
        result = env.execute_move(moves[0])
        
        if result.success:
            print(f"Move {i+1}: Score = {result.new_state.score}, "
                  f"Valid moves = {len(env.get_valid_moves())}")
    
    print("✓ Game loop tests passed")


def test_state_representation():
    """Test state representation and features."""
    print("\nTesting state representation...")
    
    state = GameState.create_empty(9, 9)
    
    # Add some balls
    state.set_cell(Position(0, 0), BallColor.RED)
    state.set_cell(Position(1, 1), BallColor.BLUE)
    state.set_cell(Position(2, 2), BallColor.GREEN)
    
    # Test string representation
    print("\nBoard visualization:")
    print(state)
    
    # Test feature vector
    features = state.to_feature_vector()
    print(f"\n✓ Feature vector shape: {features.shape}")
    assert features.shape == (9, 9, len(BallColor))
    
    # Test position queries
    empty = state.get_empty_positions()
    occupied = state.get_occupied_positions()
    print(f"✓ Empty positions: {len(empty)}")
    print(f"✓ Occupied positions: {len(occupied)}")
    assert len(empty) + len(occupied) == 81
    
    print("✓ State representation tests passed")


def test_reproducibility():
    """Test that same seed produces same results."""
    print("\nTesting reproducibility...")
    
    config = GameConfig(rows=9, cols=9, colors_count=7)
    
    # Create two environments with same seed
    env1 = SimulationEnvironment(config, seed=42)
    env2 = SimulationEnvironment(config, seed=42)
    
    state1 = env1.reset()
    state2 = env2.reset()
    
    # Should have identical initial states
    import numpy as np
    assert np.array_equal(state1.board, state2.board)
    assert state1.next_balls == state2.next_balls
    
    print("✓ Same seed produces identical states")
    
    # Execute same moves
    moves1 = env1.get_valid_moves()
    moves2 = env2.get_valid_moves()
    
    if moves1 and moves2:
        result1 = env1.execute_move(moves1[0])
        result2 = env2.execute_move(moves2[0])
        
        assert np.array_equal(result1.new_state.board, result2.new_state.board)
        print("✓ Same moves produce identical results")
    
    print("✓ Reproducibility tests passed")


if __name__ == "__main__":
    print("=" * 60)
    print("FRAMEWORK TESTS")
    print("=" * 60)
    
    try:
        test_game_state()
        test_simulation_environment()
        test_move_execution()
        test_state_representation()
        test_reproducibility()
        test_game_loop()
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED ✓")
        print("=" * 60)
        print("\nFramework is working correctly!")
        print("\nNext steps:")
        print("1. Implement game matching logic in game_environment.py")
        print("2. Install dependencies: pip install -r requirements.txt")
        print("3. Implement image recognition in game_client.py")
        print("4. Build your ML model")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()

