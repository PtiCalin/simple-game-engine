"""Simple lockbox puzzle type."""
from ..puzzle_engine import PuzzleBase

PUZZLE_TYPE = "lockbox"


class PuzzleType(PuzzleBase):
    """A numeric lock that opens with the correct code."""

    def check_solution(self, player_input):
        code = str(self.meta.solution or self.meta.data.get("code", ""))
        if str(player_input) == code:
            self.mark_solved()
            return True
        return False
