# 🎮 game-engine

> A handcrafted point-and-click engine for narrative games, puzzles, surreal adventures, and story experiments — built from scratch in Python.

`game-engine` is a modular, lightweight game engine for 2D point-and-click adventures. Inspired by games like **A Little to the Left**, **Rusty Lake**, **Ace Attorney**, and **Outer Wilds**, it's designed to be flexible, extensible, and totally under your creative control.

No dependencies on Unity, Godot, or any bloated middleware — just Python, PyGame, and deeply human design.

---

## ✨ Features (WIP)

- 🧭 **Scene Manager** – Room transitions, interaction zones, layered backgrounds
- 🧩 **Puzzle Logic** – Customizable item interactions, object states, environment triggers
- 🗃️ **YAML-Driven** – Game logic, items, dialogues, scenes, and timelines authored in human-readable formats
- 🎒 **Inventory System** – Collect, combine, and use items with context-sensitive feedback
- 💬 **Dialogue Engine** – Branching conversations, memory-aware options, emotional logic
- ⏳ **Timeline Engine** – Event synchronization, time loops, reactive world logic
- 🧠 **Character Traits** – NPCs with complex states, personalities, and dynamic interactions
- 🛠️ **Engine-Editor Split** – Clean separation between runtime and creative toolkit (planned)

---

## 🧠 Inspirations

> This engine is built with love for:
> - A Little to the Left  
> - The Cube Collection  
> - Rusty Lake series  
> - Frog Detective  
> - Ace Attorney  
> - Escape Academy  
> - Outer Wilds  
> - Potion Craft  
> - Tangle Tower  
> - The Secret of Monkey Island  
> - ...and every game that felt a little weird, personal, or magical ✨

---

## 🛠️ Tech Stack

- **Language**: Python 3.11+
- **Renderer**: PyGame
- **Data**: YAML-based modular game definitions
- **Style**: Pure Python, no GUI frameworks or editors (yet)

---

## 🚀 Getting Started

> You'll need Python 3.11+ and pip installed.

```bash
git clone https://github.com/yourusername/game-engine.git
cd game-engine
pip install -r requirements.txt
python main.py
```

✨ First demo loads a single room with one object and a small dialogue scene (in progress)

## 📁 Project Structure

game-engine/
├── engine/          # Core engine logic (scene manager, UI, etc)
├── game/            # Game data: scenes, items, characters
│   ├── scenes/
│   ├── items/
│   ├── dialogue/
│   └── timeline/
├── ui/              # Inventory bar, contextual menus, etc
├── assets/          # Images, audio, fonts
├── main.py          # Game launcher
└── config.yaml      # Global config

## 💡 Vision

This project isn’t just an engine. It’s an invitation to tell surreal, beautiful stories in playable form — and to build the exact tools you wish you had as a kid.

You can fork it, remix it, turn it into a framework, or just build your own strange little game.

## 📚 Related Projects
Some repos that inspired or informed this work:

- Droggelbecher/Grail
- ThomasTheSpaceFox/Desutezeoid
- bladecoder/bladecoder-adventure-engine
- rpgboss/rpgboss

## 🧵 Topics
python pygame game-engine point-and-click narrative-games dialogue-engine puzzle-game
interactive-fiction modular-system open-source yaml-driven time-loop experimental-games surreal-games

## 🐣 Status
🚧 Actively being built. Early prototyping phase.
Expect magic, messiness, and many commits at 2am.

## 🧙‍♂️ Creator
Charlie Bouchard — LinkedIn · GitHub
✨ Making vaults, stories, and software that hug you back.

## ☕ Support
If you like this project, consider dropping a star ⭐ or buying me a tea: buymeacoffee.com/pticalin

## 📜 License
MIT — use it, fork it, break it, rebuild it.
