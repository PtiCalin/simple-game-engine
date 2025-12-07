"""
Serialization Helper for RPG Data
"""
import yaml
import json

def save_yaml_data(data, filepath):
    with open(filepath, 'w', encoding='utf-8') as f:
        yaml.safe_dump(data, f)

def save_json_data(data, filepath):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
