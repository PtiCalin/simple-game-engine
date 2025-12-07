"""
Status Effects for RPG Characters and NPCs
"""
class StatusEffect:
    def __init__(self, name, description, duration=None, effect=None):
        self.name = name
        self.description = description
        self.duration = duration  # in turns or None for permanent
        self.effect = effect or {}

    def __repr__(self):
        return f"<StatusEffect {self.name} ({self.duration})>"

class StatusManager:
    def __init__(self):
        self.effects = []

    def add_effect(self, name, description, duration=None, effect=None):
        eff = StatusEffect(name, description, duration, effect)
        self.effects.append(eff)
        return eff

    def get_effect(self, name):
        for eff in self.effects:
            if eff.name == name:
                return eff
        return None

    def list_effects(self):
        return self.effects
