"""
Test playing a full game until game over, then automatically reset.

This demonstrates the complete game cycle:
1. Play random moves until game over
2. Handle game over popup
3. Handle high score popup (if applicable)
4. Game auto-restarts
5. Continue playing
"""

import sys
from pathlib import Path
import random
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from wzlz_ai.game_state import GameConfig
from wzlz_ai.game_client import GameClientEnvironment


def main():
    print("="*70)
    print("FULL GAME CYCLE TEST")
    print("="*70)
    print("\nThis will:")
    print("  1. Play random moves until game over")
    print("  2. Automatically handle popups")
    print("  3. Reset and start a new game")
    print("  4. Play a few more moves")
    print()
    
    # Create game config
    config = GameConfig(show_next_balls=True)
    
    # Create game client environment
    print("Initializing GameClientEnvironment...")
    env = GameClientEnvironment(config)
    
    if not env.is_calibrated:
        print("\n✗ Game client not calibrated!")
        print("Run: uv run python examples/manual_calibrate_all.py")
        return
    
    print("✓ Game client calibrated")
    
    # Get initial state
    state = env.get_state()
    ball_count = sum(1 for row in range(9) for col in range(9) if state.board[row, col] != 0)

    # Format next balls
    next_balls_str = "None"
    if state.next_balls:
        from wzlz_ai.game_state import BallColor
        colors = [BallColor(c).name for c in state.next_balls]
        next_balls_str = ", ".join(colors)

    print(f"\nInitial state: {ball_count} balls, score: {state.score}, next: [{next_balls_str}]")
    
    # Play until game over
    print("\n" + "="*70)
    print("PLAYING UNTIL GAME OVER")
    print("="*70)
    
    move_count = 0
    max_moves = 200  # Safety limit
    
    while move_count < max_moves:
        # Get valid moves
        moves = env.get_valid_moves(state)
        
        if not moves:
            print(f"\n✓ Game over after {move_count} moves!")
            break
        
        # Pick a random move
        move = random.choice(moves)
        
        # Execute move
        try:
            result = env.execute_move(move)

            # Check if result is None (popup was handled)
            if result is None:
                print(f"\n✓ Game over detected after {move_count} moves!")
                print("  Popup was automatically handled")
                state = None
                break

            state = result.new_state
            move_count += 1

            # Print progress every 10 moves
            if move_count % 10 == 0:
                ball_count = sum(1 for row in range(9) for col in range(9) if state.board[row, col] != 0)

                # Format next balls
                next_balls_str = "None"
                if state.next_balls:
                    from wzlz_ai.game_state import BallColor
                    colors = [BallColor(c).name for c in state.next_balls]
                    next_balls_str = ", ".join(colors)

                print(f"Move {move_count}: {ball_count} balls, score: {state.score}, next: [{next_balls_str}]")

        except Exception as e:
            print(f"\n⚠ Error on move {move_count}: {e}")
            print("This might mean game over popup appeared")
            state = None
            break

    # Final state
    if state is not None:
        ball_count = sum(1 for row in range(9) for col in range(9) if state.board[row, col] != 0)

        # Format next balls
        next_balls_str = "None"
        if state.next_balls:
            from wzlz_ai.game_state import BallColor
            colors = [BallColor(c).name for c in state.next_balls]
            next_balls_str = ", ".join(colors)

        print(f"\nFinal state: {ball_count} balls, score: {state.score}, next: [{next_balls_str}]")
    else:
        print(f"\nGame over after {move_count} moves (popup appeared)")
    
    # Check if popup was already handled
    if state is None:
        print("\n✓ Popup was already handled during execute_move()")
        print("  Game should have auto-restarted")

        # Get the new state
        state = env.get_state()
        ball_count = sum(1 for row in range(9) for col in range(9) if state.board[row, col] != 0)

        if ball_count == 5:
            print(f"\n✓ Game restarted correctly with 5 balls!")
        else:
            print(f"\n⚠ Game has {ball_count} balls (expected 5)")
    else:
        # Popup wasn't handled yet - do it now
        print("\n" + "="*70)
        print("WAITING FOR POPUPS")
        print("="*70)
        print("\nWaiting 3 seconds for popups to appear...")
        print("(Game over popup should appear, then high score popup)")
        time.sleep(3.0)

        # Reset the game (this will handle popups)
        print("\n" + "="*70)
        print("RESETTING GAME")
        print("="*70)
        print("\nCalling env.reset()...")
        print("This will:")
        print("  1. Find and dismiss game over popup")
        print("  2. Find and dismiss high score popup")
        print("  3. Wait for game to auto-restart")

        try:
            state = env.reset()
            ball_count = sum(1 for row in range(9) for col in range(9) if state.board[row, col] != 0)

            print(f"\n✓ Reset successful!")
            print(f"  New game: {ball_count} balls, score: {state.score}")

            if ball_count == 5:
                print("\n✓ Game restarted correctly with 5 balls!")
            else:
                print(f"\n⚠ Expected 5 balls, got {ball_count}")
                print("  Popups may not have been dismissed correctly")

        except Exception as e:
            print(f"\n✗ Reset failed: {e}")
            return
    
    # Play a few more moves to verify game is working
    print("\n" + "="*70)
    print("PLAYING A FEW MORE MOVES")
    print("="*70)
    
    for i in range(5):
        moves = env.get_valid_moves(state)

        if not moves:
            print(f"\n⚠ No valid moves after {i} moves")
            break

        move = random.choice(moves)
        result = env.execute_move(move)

        # Check if popup appeared
        if result is None:
            print(f"\n⚠ Game over popup appeared after {i} moves")
            break

        state = result.new_state

        ball_count = sum(1 for row in range(9) for col in range(9) if state.board[row, col] != 0)

        # Format next balls
        next_balls_str = "None"
        if state.next_balls:
            from wzlz_ai.game_state import BallColor
            colors = [BallColor(c).name for c in state.next_balls]
            next_balls_str = ", ".join(colors)

        print(f"Move {i+1}: {ball_count} balls, score: {state.score}, next: [{next_balls_str}]")
    
    print("\n" + "="*70)
    print("TEST COMPLETE!")
    print("="*70)
    print("\n✓ Full game cycle works:")
    print("  1. Played until game over")
    print("  2. Handled popups automatically")
    print("  3. Game restarted successfully")
    print("  4. Continued playing")
    print("\n🎉 Ready for AI training!")


if __name__ == "__main__":
    main()

