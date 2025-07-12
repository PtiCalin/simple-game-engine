# Project Roadmap

## 🧠 Vision: The PtiCalin Engine
"Light like a whisper, powerful like a storm.
Flexible for artists, fast for builders, and magical for players."

## 🌳 HIGH-LEVEL DEVELOPMENT ROADMAP

### 🟢 PHASE 1 – Foundation & Architecture (CORE)
│
├── ✅ Launcher System (main.py w/ config bootstrap)
├── ✅ SceneManager (YAML-driven, hotspots, transitions)
├── ✅ WorldManager (multi-region, metadata, start scenes)
├── ✅ AssetManager (caching, dynamic asset resolution)
├── ☑ GameState (flags, variables, save/load)
├── ☑ Engine Loop (scene stack, FPS clock, screen manager)
└── ☑ Core UI Overlay (text boxes, tooltips, hover labels)

### 🟡 PHASE 2 – Storytelling & Puzzles (GAME LOGIC)
│
├── 🧩 PuzzleEngine (modular logic types)
├── 💬 DialogueEngine (branching, memory, flags)
├── 🧠 NPCSystem (traits, personality, reactions)
├── 🎒 InventorySystem (pickup, combine, use)
├── 🔁 TimelineEngine (events, time loops, scheduling)
└── 🔥 TriggerSystem (on_enter, on_solve, on_flag)

### 🔵 PHASE 3 – Worldbuilding & Editor Tools (CREATOR MODE)
│
├── 🗺️ Region Editor UI (click-to-place hotspots)
├── 🧱 Scene Builder (Obsidian/YAML companion + live preview)
├── 🎨 Asset Inspector (visual layer manager + loader)
├── 🧰 Debug Overlay (FPS, flags, region info)
├── 💡 Visual Condition Tester (simulate triggers)
└── ⚙️ DevMenu (scene teleport, reload, test puzzles)

### 🟣 PHASE 4 – Polish & Publishing (RELEASE)
│
├── 🌐 Multi-language Support (locales via YAML)
├── 🌟 Title Menu / Save Slot System
├── 📦 Game Exporter (package to .exe, .app, or web)
├── 🎮 Controller & Input Customization
├── 🌈 Accessibility Settings
└── 🚀 Performance Optimization (resource cleanup, framerate cap, caching)

## 🧩 KEY MODULE SNAPSHOT

| Category | Module | Status |
| --- | --- | --- |
| 🧠 Core | SceneManager | ✅ Built |
| 🗺️ World | WorldManager | 🔧 Coding now |
| 🖼️ Assets | AssetManager | 🔧 In dev |
| 🔐 Game State | GameState | 🟡 Prototype soon |
| 🧩 Puzzles | PuzzleEngine | 🟡 Next |
| 💬 Dialogue | DialogueEngine | 🟡 Planned |
| 🎭 Characters | NPCSystem | ⬜ Future |
| 🕰️ Time | TimelineEngine | ⬜ Future |
| 🛠️ Creator UX | RegionEditorUI | ⬜ Later |
| 🎮 Deployment | GameExporter | ⬜ Final phase |

## 🧙‍♂️ PtiCalin Design Principles

| Principle | What It Means for the Engine |
| --- | --- |
| ✨ Lightweight | Minimal dependencies, fast launch, <100ms input-to-frame latency |
| 🧩 Modular | Each system optional & plug-play (like VaultOS subplugins) |
| 🌈 Friendly | YAML-first, minimal syntax, UI feedback for creators |
| 🔁 Extensible | Easily add new triggers, conditions, puzzle types, visuals |
| 🎯 Focused | Core gameplay loop is clear, smooth, easy to scale |
| 🔥 Stylized | Clean fonts, parallax vibes, optional shaderFX later |

## 🎯 Immediate Next Tasks

| Priority | Feature | Dev Action |
| --- | --- | --- |
| 🟢 | Finalize WorldManager | Write logic, load world metadata |
| 🟢 | Build AssetManager | Add caching + fallback handling |
| 🟡 | Create GameState | Add flag setting/checking & save file |
| 🟡 | Define puzzle schema in YAML | Start with 3 puzzle types |
| 🟡 | Create DialogueEngine stub | Support one character + 3 choices |
| 🔵 | Write scene.yaml sample files | Showcase: region entry + dialogue trigger |

