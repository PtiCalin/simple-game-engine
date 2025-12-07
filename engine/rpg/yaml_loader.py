"""
YAML Loader for RPG Data (Characters, Items, Spells, Quests, Campaigns)
"""
import yaml
import os

def load_yaml_data(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

# Example: load character data from YAML
# data = load_yaml_data('game/characters.yaml')
