"""Built-in puzzle type registry."""
from importlib import import_module
from pathlib import Path
from typing import Dict, Type

from ..puzzle_engine import PuzzleBase


def load_types() -> Dict[str, Type[PuzzleBase]]:
    """Dynamically import puzzle type modules and return a registry."""
    registry: Dict[str, Type[PuzzleBase]] = {}
    pkg_path = Path(__file__).parent
    for py in pkg_path.glob("*.py"):
        if py.stem.startswith("_") or py.stem == "__init__":
            continue
        module = import_module(f"engine.puzzle_types.{py.stem}")
        cls = getattr(module, "PuzzleType", None)
        name = getattr(module, "PUZZLE_TYPE", py.stem)
        if cls:
            registry[name] = cls
    return registry
