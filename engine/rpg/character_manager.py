"""
DnD-style Character Manager for PtiCalin Game Engine
"""

class Character:
    def __init__(self, name, race, char_class, level=1, stats=None, inventory=None, spells=None, quests=None):
        self.name = name
        self.race = race
        self.char_class = char_class
        self.level = level
        self.stats = stats or {
            'STR': 10, 'DEX': 10, 'CON': 10, 'INT': 10, 'WIS': 10, 'CHA': 10
        }
        self.inventory = inventory or []
        self.spells = spells or []
        self.quests = quests or []
        self.hp = self.max_hp()

    def max_hp(self):
        # Example: 10 + CON modifier per level
        return 10 + (self.stats['CON'] - 10) // 2 * self.level

    def add_item(self, item):
        self.inventory.append(item)

    def add_spell(self, spell):
        self.spells.append(spell)

    def add_quest(self, quest):
        self.quests.append(quest)

    def __repr__(self):
        return f"<Character {self.name} ({self.char_class} Lv{self.level})>"

class CharacterManager:
    def __init__(self):
        self.characters = []

    def create_character(self, name, race, char_class, **kwargs):
        char = Character(name, race, char_class, **kwargs)
        self.characters.append(char)
        return char

    def get_character(self, name):
        for char in self.characters:
            if char.name == name:
                return char
        return None

    def list_characters(self):
        return self.characters
