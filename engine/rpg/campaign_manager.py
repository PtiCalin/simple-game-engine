"""
Campaign Manager for DnD-style RPG
"""
class Campaign:
    def __init__(self, title, description, scenes=None, npcs=None, quests=None):
        self.title = title
        self.description = description
        self.scenes = scenes or []
        self.npcs = npcs or []
        self.quests = quests or []

    def add_scene(self, scene):
        self.scenes.append(scene)

    def add_npc(self, npc):
        self.npcs.append(npc)

    def add_quest(self, quest):
        self.quests.append(quest)

    def __repr__(self):
        return f"<Campaign {self.title} ({len(self.scenes)} scenes)>"

class CampaignManager:
    def __init__(self):
        self.campaigns = []

    def create_campaign(self, title, description, **kwargs):
        campaign = Campaign(title, description, **kwargs)
        self.campaigns.append(campaign)
        return campaign

    def get_campaign(self, title):
        for campaign in self.campaigns:
            if campaign.title == title:
                return campaign
        return None

    def list_campaigns(self):
        return self.campaigns
