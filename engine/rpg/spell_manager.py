"""
Spell Manager for DnD-style RPG
"""
class Spell:
    def __init__(self, name, level, school, description, effect=None):
        self.name = name
        self.level = level
        self.school = school
        self.description = description
        self.effect = effect or {}

    def __repr__(self):
        return f"<Spell {self.name} (Lv{self.level}, {self.school})>"

class SpellManager:
    def __init__(self):
        self.spells = []

    def add_spell(self, name, level, school, description, effect=None):
        spell = Spell(name, level, school, description, effect)
        self.spells.append(spell)
        return spell

    def get_spell(self, name):
        for spell in self.spells:
            if spell.name == name:
                return spell
        return None

    def list_spells(self, school=None, level=None):
        result = self.spells
        if school:
            result = [s for s in result if s.school == school]
        if level:
            result = [s for s in result if s.level == level]
        return result
