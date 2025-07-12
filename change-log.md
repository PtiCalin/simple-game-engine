# 📖 Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

- Added ``GameState`` module to track persistent flags, inventory, clues and
  unlocked scenes.
- Hotspots now support an optional ``condition`` field for conditional
  interactions.
- Added ``TimelineEngine`` to schedule delay-based events that modify ``GameState``.
- Added ``WorldManager`` to handle world loading and state management.
- Added ``AssetManager`` for caching images and music.
- Worlds now use a YAML format loaded by ``WorldManager``.

## [0.1.0] - 2024-01-01

- Initial documentation and project scaffold
