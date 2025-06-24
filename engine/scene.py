from dataclasses import dataclass
from typing import Optional


@dataclass
class Scene:
    """Simple representation of a scene loaded from YAML."""

    id: Optional[str]
    background: Optional[str]
    mode: str = "simple"
