"""
Simple DnD-style Combat Engine
"""
from .character_manager import Character
from .dice_roller import roll_dice

class CombatEngine:
    def __init__(self, party, enemies):
        self.party = party  # list of Character
        self.enemies = enemies  # list of Character
        self.turn_order = self.determine_initiative()

    def determine_initiative(self):
        # Sort by DEX stat, descending
        all_combatants = self.party + self.enemies
        return sorted(all_combatants, key=lambda c: c.stats['DEX'], reverse=True)

    def attack(self, attacker, defender):
        # Roll d20 + STR for melee, DEX for ranged
        attack_roll, _, _ = roll_dice('1d20')
        attack_mod = attacker.stats['STR'] if attacker.char_class in ['Fighter', 'Barbarian'] else attacker.stats['DEX']
        total_attack = attack_roll + (attack_mod - 10) // 2
        # Simple AC check
        if total_attack >= defender.stats.get('AC', 10):
            damage, _, _ = roll_dice('1d8')
            defender.hp -= damage
            return True, damage
        return False, 0
