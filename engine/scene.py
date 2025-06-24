from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List


@dataclass
class Scene:
    """Simple representation of a scene loaded from YAML."""

    id: Optional[str]
    background: Optional[str]
    mode: str = "simple"
    features: Dict[str, Any] = field(default_factory=dict)
    overlays: List[str] = field(default_factory=list)
