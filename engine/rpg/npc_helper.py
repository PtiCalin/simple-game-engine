"""
NPC Helper for DnD-style RPG
"""
class NPC:
    def __init__(self, name, traits=None, personality=None, dialogue=None):
        self.name = name
        self.traits = traits or {}
        self.personality = personality or "Neutral"
        self.dialogue = dialogue or []

    def add_dialogue(self, line):
        self.dialogue.append(line)

    def __repr__(self):
        return f"<NPC {self.name} ({self.personality})>"

class NPCHelper:
    def __init__(self):
        self.npcs = []

    def add_npc(self, name, traits=None, personality=None, dialogue=None):
        npc = NPC(name, traits, personality, dialogue)
        self.npcs.append(npc)
        return npc

    def get_npc(self, name):
        for npc in self.npcs:
            if npc.name == name:
                return npc
        return None

    def list_npcs(self):
        return self.npcs
