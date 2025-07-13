"""Item matching puzzle."""
from ..puzzle_engine import PuzzleBase

PUZZLE_TYPE = "match_items"


class PuzzleType(PuzzleBase):
    """Match items to their correct slots."""

    def check_solution(self, player_input):
        expected = self.meta.solution or self.meta.data.get("matches", {})
        if player_input == expected:
            self.mark_solved()
            return True
        return False
