"""
Wzlz AI - Framework for training AI models to play the ball matching game.

This package provides a flexible framework for training AI models to play
the ball matching game (五子连珠) with support for both simulation-based
training and real game client interaction.
"""

from wzlz_ai.game_state import (
    GameState,
    GameConfig,
    Position,
    Move,
    MoveResult,
    BallColor,
)

from wzlz_ai.game_environment import (
    GameEnvironment,
    SimulationEnvironment,
)

try:
    from wzlz_ai.game_client import GameClientEnvironment
except ImportError:
    # Game client dependencies not installed
    GameClientEnvironment = None

__version__ = "0.1.0"

__all__ = [
    "GameState",
    "GameConfig",
    "Position",
    "Move",
    "MoveResult",
    "BallColor",
    "GameEnvironment",
    "SimulationEnvironment",
    "GameClientEnvironment",
]

