"""Sequence puzzle type."""
from ..puzzle_engine import PuzzleBase

PUZZLE_TYPE = "sequence"


class PuzzleType(PuzzleBase):
    """Validate a sequence of inputs."""

    def check_solution(self, player_input):
        expected = self.meta.solution or self.meta.data.get("sequence", [])
        if player_input == expected:
            self.mark_solved()
            return True
        return False
