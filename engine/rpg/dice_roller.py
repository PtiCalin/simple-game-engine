"""
Dice Roller for DnD-style RPG
"""
import random

def roll_dice(dice_str):
    """
    Roll dice in NdM format, e.g. '2d6+1'
    Returns total and breakdown.
    """
    import re
    match = re.match(r"(\d+)d(\d+)([+-]\d+)?", dice_str)
    if not match:
        raise ValueError("Invalid dice format")
    n, m, mod = match.groups()
    n, m = int(n), int(m)
    mod = int(mod) if mod else 0
    rolls = [random.randint(1, m) for _ in range(n)]
    total = sum(rolls) + mod
    return total, rolls, mod
