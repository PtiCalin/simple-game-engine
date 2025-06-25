# 🔧 simple-game-engine

> A modular point-and-click adventure engine written in Python.

Simple Game Engine is built to support surreal, story-rich games inspired by
Rusty Lake, A Little to the Left, Frog Detective, Tangle Tower, Outer Wilds and
more. It focuses on smooth interactions, seamless modularity and expansive
possibilities.

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status: WIP](https://img.shields.io/badge/status-in_progress-yellow.svg)](#)
[![Pull Requests Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](./.github/pull_request_template.md)
[![GitHub Discussions](https://img.shields.io/badge/💬-Discussions-blueviolet?logo=github)](https://github.com/your-username/simple-game-engine/discussions)

</div>

---

## 🌟 Key Features

- Scene manager with interactive hotspots
- YAML-based item, character, and puzzle logic
- Inventory and contextual action systems
- Persistent ``GameState`` for flags and progress
- Modular dialogue engine with branching paths
- Timeline system for synced events and time loops
- Support for character traits, interaction effects, and narrative memory

## 🧠 Goals

- Total creative freedom
- Extensible for visual scripting or modding
- Engine + toolkit for building games that are weird, personal and beautiful

---

## 🚀 Getting Started

Clone this repo and install dependencies:

```bash
git clone https://github.com/your-username/simple-game-engine.git
cd simple-game-engine
pip install -r requirements.txt
```

### 🛠 Run the Demo

```bash
python main.py  # or your preferred dev command
```

### ⏱ Timeline Events

Scenes can schedule delayed actions:

```yaml
scene:
  id: intro
  features:
    time_loop: true

events:
  - trigger: delay
    time: 30  # seconds
    action: set_flag
    flag: door_closed
```

---

## 🤝 Contributing

We welcome bug reports, feature ideas and pull requests!

- [🐛 Bug Reports](./.github/ISSUE_TEMPLATE/bug.yml)
- [🌟 Feature Requests](./.github/ISSUE_TEMPLATE/feature-request.yml)
- [📦 Pull Requests](./.github/pull_request_template.md)

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to get started.
Join us in [💬 GitHub Discussions](https://github.com/your-username/simple-game-engine/discussions) to share ideas.

---

## 📜 License

Distributed under the [MIT License](LICENSE).  
You are free to fork, remix, and share — just be kind.
