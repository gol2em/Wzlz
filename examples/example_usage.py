"""
Example usage of the game framework.

This demonstrates how to use both simulation and game client environments.
"""

from wzlz_ai import GameState, GameConfig, Position, Move, BallColor
from wzlz_ai import SimulationEnvironment, GameClientEnvironment


def example_simulation():
    """Example of using the simulation environment for training."""
    print("=" * 60)
    print("SIMULATION ENVIRONMENT EXAMPLE")
    print("=" * 60)
    
    # Create configuration
    config = GameConfig(
        rows=9,
        cols=9,
        colors_count=7,
        match_length=5,
        balls_per_turn=3,
        initial_balls=3
    )
    
    # Create simulation environment with fixed seed for reproducibility
    env = SimulationEnvironment(config, seed=42)
    
    # Reset to get initial state
    state = env.reset()
    print("\nInitial State:")
    print(state)
    
    # Get valid moves
    valid_moves = env.get_valid_moves()
    print(f"\nNumber of valid moves: {len(valid_moves)}")
    
    if valid_moves:
        # Execute first valid move
        move = valid_moves[0]
        print(f"\nExecuting move: {move}")
        
        result = env.execute_move(move)
        
        if result.success:
            print(f"Move successful!")
            print(f"Points earned: {result.points_earned}")
            print(f"Balls removed: {len(result.balls_removed)}")
            print(f"New balls added: {len(result.new_balls_added)}")
            print(f"\nNew State:")
            print(result.new_state)
        else:
            print(f"Move failed: {result.error_message}")
    
    # Demonstrate state cloning and manipulation
    print("\n" + "=" * 60)
    print("STATE MANIPULATION EXAMPLE")
    print("=" * 60)
    
    state = env.get_state()
    cloned_state = state.clone()
    
    print(f"Original state score: {state.score}")
    print(f"Cloned state score: {cloned_state.score}")
    
    # Modify cloned state
    cloned_state.score = 999
    print(f"\nAfter modifying clone:")
    print(f"Original state score: {state.score}")
    print(f"Cloned state score: {cloned_state.score}")
    
    # Feature vector for ML
    features = state.to_feature_vector()
    print(f"\nFeature vector shape: {features.shape}")


def example_game_client():
    """Example of using the game client environment."""
    print("\n" + "=" * 60)
    print("GAME CLIENT ENVIRONMENT EXAMPLE")
    print("=" * 60)
    
    # Create configuration
    config = GameConfig(
        rows=9,
        cols=9,
        colors_count=7,
        match_length=5,
        balls_per_turn=3
    )
    
    # Create game client environment
    env = GameClientEnvironment(config, window_title="五子连珠5.2")
    
    print("\nGame client environment created.")
    print("Before using, you need to calibrate:")
    print("  env.calibrate(board_rect=(x, y, width, height), cell_size=pixels)")
    print("\nExample:")
    print("  env.calibrate(board_rect=(220, 145, 490, 490), cell_size=54)")
    print("\nThen you can:")
    print("  state = env.get_state()  # Read current game state")
    print("  moves = env.get_valid_moves()  # Get valid moves")
    print("  result = env.execute_move(move)  # Execute a move")


def example_training_loop():
    """Example of a simple training loop."""
    print("\n" + "=" * 60)
    print("TRAINING LOOP EXAMPLE")
    print("=" * 60)
    
    config = GameConfig(rows=9, cols=9, colors_count=7)
    env = SimulationEnvironment(config, seed=42)
    
    # Simple random agent
    num_games = 3
    
    for game_num in range(num_games):
        print(f"\n--- Game {game_num + 1} ---")
        state = env.reset()
        
        moves_made = 0
        max_moves = 10  # Limit moves for demo
        
        while not env.is_game_over() and moves_made < max_moves:
            valid_moves = env.get_valid_moves()
            
            if not valid_moves:
                break
            
            # Random move selection
            import random
            move = random.choice(valid_moves)
            
            result = env.execute_move(move)
            
            if result.success:
                moves_made += 1
                print(f"Move {moves_made}: {move} -> Score: {result.new_state.score}")
        
        final_state = env.get_state()
        print(f"Game over! Final score: {final_state.score}, Moves: {moves_made}")


def example_state_analysis():
    """Example of analyzing game states."""
    print("\n" + "=" * 60)
    print("STATE ANALYSIS EXAMPLE")
    print("=" * 60)
    
    config = GameConfig(rows=9, cols=9, colors_count=7)
    env = SimulationEnvironment(config, seed=42)
    state = env.reset()
    
    # Analyze the state
    print(f"Board dimensions: {state.rows}x{state.cols}")
    print(f"Empty positions: {len(state.get_empty_positions())}")
    print(f"Occupied positions: {len(state.get_occupied_positions())}")
    
    # Show occupied positions with colors
    print("\nOccupied positions:")
    for pos in state.get_occupied_positions():
        color = state.get_cell(pos)
        print(f"  {pos}: {color.name}")
    
    # Test pathfinding
    occupied = state.get_occupied_positions()
    empty = state.get_empty_positions()
    
    if occupied and empty:
        from_pos = occupied[0]
        to_pos = empty[0]
        
        path_exists, path = env.is_path_clear(from_pos, to_pos)
        print(f"\nPath from {from_pos} to {to_pos}:")
        print(f"  Exists: {path_exists}")
        if path_exists:
            print(f"  Length: {len(path)}")
            print(f"  Path: {' -> '.join(str(p) for p in path)}")


def example_hybrid_approach():
    """
    Example of hybrid approach: train on simulation, validate on real game.
    """
    print("\n" + "=" * 60)
    print("HYBRID APPROACH EXAMPLE")
    print("=" * 60)
    
    config = GameConfig(rows=9, cols=9, colors_count=7)
    
    # Train on simulation
    print("\n1. Training on simulation (fast)...")
    sim_env = SimulationEnvironment(config, seed=42)
    
    # Simulate training
    for episode in range(3):
        state = sim_env.reset()
        print(f"  Episode {episode + 1}: Initial state has {len(state.get_occupied_positions())} balls")
    
    print("\n2. Validation on real game (accurate)...")
    client_env = GameClientEnvironment(config)
    
    print("  To validate on real game:")
    print("  - Calibrate the client: client_env.calibrate(...)")
    print("  - Read game state: state = client_env.get_state()")
    print("  - Use trained model to select move")
    print("  - Execute on real game: client_env.execute_move(move)")
    print("  - Compare results with simulation predictions")


if __name__ == "__main__":
    # Run all examples
    example_simulation()
    example_game_client()
    example_state_analysis()
    example_training_loop()
    example_hybrid_approach()
    
    print("\n" + "=" * 60)
    print("EXAMPLES COMPLETE")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Implement the matching logic in SimulationEnvironment._check_and_remove_matches()")
    print("2. Implement image recognition in GameClientEnvironment._parse_board()")
    print("3. Build your ML model using the GameState.to_feature_vector() method")
    print("4. Train using SimulationEnvironment for speed")
    print("5. Validate using GameClientEnvironment for accuracy")

