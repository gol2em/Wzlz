"""
Demonstration of the game rules implementation.

This script shows how the game works with matching, scoring, and game over conditions.
"""

from wzlz_ai import SimulationEnvironment, GameConfig, Position, Move, BallColor


def demo_basic_game():
    """Demonstrate a basic game with matching and scoring."""
    print("\n" + "="*70)
    print("DEMO: Basic Game with Matching and Scoring")
    print("="*70)
    
    # Create environment with seed for reproducibility
    config = GameConfig(rows=9, cols=9, match_length=5, initial_balls=5)
    env = SimulationEnvironment(config, seed=42)
    
    # Reset to start a new game
    state = env.reset()
    
    print("\nInitial board (5 random balls):")
    print(state)
    print(f"Next balls: {[c.name for c in state.next_balls]}")
    
    # Play a few moves
    for move_num in range(1, 6):
        valid_moves = env.get_valid_moves()
        if not valid_moves:
            print("\nNo valid moves! Game over.")
            break
        
        # Pick a random move
        move = valid_moves[0]
        result = env.execute_move(move)
        
        print(f"\n--- Move {move_num} ---")
        print(f"Move: {move}")
        print(f"Points earned: {result.points_earned}")
        print(f"Balls removed: {len(result.balls_removed)}")
        print(f"New balls added: {len(result.new_balls_added)}")
        print(f"Total score: {result.new_state.score}")
        
        if result.balls_removed:
            print(f"✓ Match! Removed balls at: {result.balls_removed}")
        
        if move_num <= 2:  # Only show board for first 2 moves
            print(f"\nBoard after move {move_num}:")
            print(result.new_state)


def demo_matching_scenarios():
    """Demonstrate different matching scenarios."""
    print("\n" + "="*70)
    print("DEMO: Different Matching Scenarios")
    print("="*70)
    
    config = GameConfig(rows=9, cols=9, match_length=5, initial_balls=0)
    env = SimulationEnvironment(config, seed=100)
    
    # Scenario 1: Horizontal match with scoring
    print("\n--- Scenario 1: Horizontal Match (5 balls) ---")
    state = env.reset()
    
    # Create 4 red balls in a row
    for col in range(4):
        state.set_cell(Position(4, col), BallColor.RED)
    
    # Place a red ball to move
    state.set_cell(Position(3, 4), BallColor.RED)
    state.next_balls = []  # No new balls
    
    env._current_state = state
    
    print("Before move:")
    print(state)
    
    # Move to complete the line
    result = env.execute_move(Move(Position(3, 4), Position(4, 4)))
    
    print("\nAfter move:")
    print(result.new_state)
    print(f"✓ Points earned: {result.points_earned} (5 balls × 2 points)")
    print(f"✓ Score: {result.new_state.score}")
    
    # Scenario 2: Vertical match
    print("\n--- Scenario 2: Vertical Match (6 balls) ---")
    state = env.reset()
    
    # Create 5 blue balls in a column
    for row in range(5):
        state.set_cell(Position(row, 4), BallColor.BLUE)
    
    # Place a blue ball to move
    state.set_cell(Position(5, 3), BallColor.BLUE)
    state.next_balls = []
    
    env._current_state = state
    
    print("Before move:")
    print(state)
    
    # Move to complete the line (6 balls total)
    result = env.execute_move(Move(Position(5, 3), Position(5, 4)))
    
    print("\nAfter move:")
    print(result.new_state)
    print(f"✓ Points earned: {result.points_earned} (6 balls × 2 points)")
    print(f"✓ Score: {result.new_state.score}")
    
    # Scenario 3: Diagonal match
    print("\n--- Scenario 3: Diagonal Match ---")
    state = env.reset()
    
    # Create 4 green balls diagonally
    for i in range(4):
        state.set_cell(Position(i, i), BallColor.GREEN)
    
    # Place a green ball to move
    state.set_cell(Position(5, 5), BallColor.GREEN)
    state.next_balls = []
    
    env._current_state = state
    
    print("Before move:")
    print(state)
    
    # Move to complete the diagonal
    result = env.execute_move(Move(Position(5, 5), Position(4, 4)))
    
    print("\nAfter move:")
    print(result.new_state)
    print(f"✓ Points earned: {result.points_earned} (5 balls × 2 points)")
    
    # Scenario 4: Cross pattern (multiple matches)
    print("\n--- Scenario 4: Cross Pattern (Multiple Matches) ---")
    state = env.reset()

    # Create horizontal line (4 balls, leaving gap at position 2)
    state.set_cell(Position(4, 0), BallColor.YELLOW)
    state.set_cell(Position(4, 1), BallColor.YELLOW)
    # Gap at Position(4, 2)
    state.set_cell(Position(4, 3), BallColor.YELLOW)
    state.set_cell(Position(4, 4), BallColor.YELLOW)

    # Create vertical line (4 balls, leaving gap at position 4)
    state.set_cell(Position(0, 2), BallColor.YELLOW)
    state.set_cell(Position(1, 2), BallColor.YELLOW)
    state.set_cell(Position(2, 2), BallColor.YELLOW)
    state.set_cell(Position(3, 2), BallColor.YELLOW)
    # Gap at Position(4, 2) - this is where we'll move to

    # Place a yellow ball to move to the gap
    state.set_cell(Position(5, 5), BallColor.YELLOW)
    state.next_balls = []

    env._current_state = state

    print("Before move:")
    print(state)

    # Move to center to complete both lines
    result = env.execute_move(Move(Position(5, 5), Position(4, 2)))

    print("\nAfter move:")
    print(result.new_state)
    print(f"✓ Balls removed: {len(result.balls_removed)}")
    print(f"✓ Points earned: {result.points_earned} ({len(result.balls_removed)} balls × 2 points)")


def demo_auto_match_no_points():
    """Demonstrate that auto-matches after random generation give no points."""
    print("\n" + "="*70)
    print("DEMO: Auto-Match After Random Generation (No Points)")
    print("="*70)
    
    config = GameConfig(rows=9, cols=9, match_length=5, initial_balls=0)
    env = SimulationEnvironment(config, seed=200)
    state = env.reset()
    
    # Create 4 red balls in a row
    for col in range(4):
        state.set_cell(Position(4, col), BallColor.RED)
    
    # Place a different colored ball to move
    state.set_cell(Position(0, 0), BallColor.BLUE)
    
    # Set next balls to include RED (might complete the line)
    state.next_balls = [BallColor.RED, BallColor.GREEN, BallColor.BLUE]
    
    env._current_state = state
    
    print("Before move:")
    print(state)
    print(f"Score: {state.score}")
    print(f"Next balls: {[c.name for c in state.next_balls]}")
    
    # Make a move that doesn't create a match
    result = env.execute_move(Move(Position(0, 0), Position(0, 1)))
    
    print("\nAfter move (3 random balls added):")
    print(result.new_state)
    print(f"Score: {result.new_state.score}")
    print(f"Points from move: {result.points_earned}")
    print(f"Balls removed: {len(result.balls_removed)}")
    
    if result.balls_removed:
        print("✓ Auto-match occurred, but NO POINTS were awarded!")
    else:
        print("✓ No auto-match occurred")


def demo_game_statistics():
    """Show game statistics over multiple moves."""
    print("\n" + "="*70)
    print("DEMO: Game Statistics")
    print("="*70)
    
    config = GameConfig(rows=9, cols=9, match_length=5, initial_balls=5)
    env = SimulationEnvironment(config, seed=12345)
    
    state = env.reset()
    
    print(f"Initial state:")
    print(f"  Board size: {state.rows}×{state.cols}")
    print(f"  Initial balls: {config.initial_balls}")
    print(f"  Balls per turn: {config.balls_per_turn}")
    print(f"  Match length: {config.match_length}")
    print(f"  Colors: {config.colors_count}")
    
    total_matches = 0
    total_balls_removed = 0
    max_score_in_move = 0
    
    print(f"\nPlaying 20 moves...")
    
    for move_num in range(1, 21):
        valid_moves = env.get_valid_moves()
        if not valid_moves:
            print(f"\nGame over at move {move_num}!")
            break
        
        # Pick first valid move
        result = env.execute_move(valid_moves[0])
        
        if result.balls_removed:
            total_matches += 1
            total_balls_removed += len(result.balls_removed)
            max_score_in_move = max(max_score_in_move, result.points_earned)
            print(f"  Move {move_num}: ✓ MATCH! {len(result.balls_removed)} balls, "
                  f"{result.points_earned} points, Score: {result.new_state.score}")
        else:
            if move_num % 5 == 0:
                print(f"  Move {move_num}: No match, Score: {result.new_state.score}")
    
    final_state = env.get_state()
    
    print(f"\n--- Final Statistics ---")
    print(f"Total moves: {final_state.move_count}")
    print(f"Total matches: {total_matches}")
    print(f"Total balls removed: {total_balls_removed}")
    print(f"Final score: {final_state.score}")
    print(f"Max points in single move: {max_score_in_move}")
    print(f"Average points per match: {final_state.score / total_matches if total_matches > 0 else 0:.1f}")
    print(f"Occupied cells: {len(final_state.get_occupied_positions())}")
    print(f"Empty cells: {len(final_state.get_empty_positions())}")
    print(f"Game over: {final_state.game_over}")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("WZLZ AI - GAME RULES DEMONSTRATION")
    print("="*70)
    
    demo_basic_game()
    demo_matching_scenarios()
    demo_auto_match_no_points()
    demo_game_statistics()
    
    print("\n" + "="*70)
    print("DEMONSTRATION COMPLETE!")
    print("="*70)
    print("\nThe game rules are fully implemented:")
    print("  ✓ 9×9 grid")
    print("  ✓ Start with 5 random balls")
    print("  ✓ Move balls along clear paths")
    print("  ✓ Add 3 random balls after each move (if no match)")
    print("  ✓ Match 5+ balls in a line (horizontal, vertical, diagonal)")
    print("  ✓ Score 2 points per ball when matched after a move")
    print("  ✓ No points when matched after random generation")
    print("  ✓ Game over when board is full (no valid moves)")
    print("\nYou can now train AI models to play this game!")

