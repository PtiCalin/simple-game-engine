"""
Inventory Helper for DnD-style RPG
"""
class Item:
    def __init__(self, name, item_type, description, properties=None):
        self.name = name
        self.item_type = item_type  # e.g. weapon, armor, potion
        self.description = description
        self.properties = properties or {}

    def __repr__(self):
        return f"<Item {self.name} ({self.item_type})>"

class InventoryHelper:
    def __init__(self):
        self.items = []

    def add_item(self, name, item_type, description, properties=None):
        item = Item(name, item_type, description, properties)
        self.items.append(item)
        return item

    def get_item(self, name):
        for item in self.items:
            if item.name == name:
                return item
        return None

    def list_items(self, item_type=None):
        if item_type:
            return [i for i in self.items if i.item_type == item_type]
        return self.items
