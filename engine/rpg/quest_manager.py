"""
Quest Manager for DnD-style RPG
"""
class Quest:
    def __init__(self, title, description, status='active', rewards=None):
        self.title = title
        self.description = description
        self.status = status  # active, completed, failed
        self.rewards = rewards or []

    def complete(self):
        self.status = 'completed'

    def fail(self):
        self.status = 'failed'

    def __repr__(self):
        return f"<Quest {self.title} ({self.status})>"

class QuestManager:
    def __init__(self):
        self.quests = []

    def add_quest(self, title, description, **kwargs):
        quest = Quest(title, description, **kwargs)
        self.quests.append(quest)
        return quest

    def get_quest(self, title):
        for quest in self.quests:
            if quest.title == title:
                return quest
        return None

    def list_quests(self, status=None):
        if status:
            return [q for q in self.quests if q.status == status]
        return self.quests
