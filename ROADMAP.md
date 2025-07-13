# 📋 PtiCalin Game Engine – Roadmap

## 🟢 Phase 1 – Foundation & Architecture (Done)

✅ Done

- [x] Launcher System (main.py w/ config bootstrap)
- [x] SceneManager (YAML-driven, hotspots, transitions)
- [x] WorldManager (multi-region, metadata, start scenes)
- [x] AssetManager (caching, dynamic asset resolution)
- [x] GameState (flags, variables, save/load)
- [x] Engine Loop (scene stack, FPS clock, screen manager)
- [x] Core UI Overlay (text boxes, tooltips, hover labels)

---

## 🟡 Phase 2 – Storytelling & Puzzles

🛠️ Finetuning

- [x] PuzzleEngine (modular logic types)
- [x] DialogueEngine (branching, memory, flags)
- [x] NPCSystem (traits, personality, reactions)
- [x] InventorySystem (pickup, combine, use)
- [x] TimelineEngine (events, time loops, scheduling)
- [x] TriggerSystem (on_enter, on_solve, on_flag)
- [ ] Refactor PuzzleEngine to support YAML-based logic per type (e.g. `type: lockbox`)
- [ ] Enhance DialogueEngine with flag injection, memory branches, localization
- [ ] Merge TriggerSystem into unified Trigger + Timeline + GameState condition engine
- [ ] Expand InventorySystem to support crafting, enchanting, and tagging

---

## 🔵 Phase 3 – Worldbuilding & Editor Tools

🛠️ Finetuning

- [x] Region Editor UI (click-to-place hotspots)
- [x] Scene Builder (Obsidian/YAML companion + live preview)
- [x] Asset Inspector (visual layer manager + loader)
- [x] Debug Overlay (FPS, flags, region info)
- [x] Visual Condition Tester (simulate triggers)
- [x] DevMenu (scene teleport, reload, test puzzles)
- [ ] RegionEditorUX polish: drag accuracy, visual selection feedback
- [ ] Add Snap-to-grid, Zoom, Pan in SceneCanvas
- [ ] Add YAML live preview panel in Scene Builder
- [ ] DebugOverlay: Make togglable, color-coded states, tooltips
- [ ] Visual Trigger Tester: hover effects + click simulation in canvas
- [ ] DevMenu Plugin: Add teleport, flag toggle, scene reload buttons

---

## 🟣 Phase 4 – Polish & Publishing

🛠️ Finetuning

- [x] Multi-language Support (locales via YAML)
- [x] Title Menu / Save Slot System
- [x] Game Exporter (package to .exe, .app, or web)
- [x] Controller & Input Customization
- [x] Accessibility Settings
- [x] Performance Optimization (resource cleanup, framerate cap, caching)
- [ ] Refactor UIOverlay scaling for multi-resolution support
- [ ] Add autosave + multi-slot support to Save System
- [ ] Add input mapping panel (keys, controller, mobile)
- [ ] Add toggle font size / color contrast for accessibility
- [ ] Add export config tool (Windows, Mac, Web)
- [ ] Add startup language selector → loads from /lang/

## 🪄 Phase 5 – Creative UX & Sandbox Builder

🚧 Planned

- [ ] Create editor/gamebuilder_ui.py (canvas scaffold)
- [ ] Create ui/asset_browser.py (shows assets, library, drag-to-canvas)
- [ ] Create editor/scene_canvas.py (background, items, hotspots)
- [ ] Create editor/properties_panel.py (context config)
- [ ] Add editor/timeline.py for trigger/layer preview
- [ ] Add editor/theme_selector.py to change UI skin
- [ ] Create scene diff preview & YAML validator

## 📚 Built-In Asset Library

- [ ] Create /library/ folder and scaffold subtypes
- [ ] Add /library/library_index.yaml (tagged asset registry)
- [ ] Extend AssetManager with dual lookup (library + user)
- [ ] Create asset metadata viewer/editor
- [ ] Create asset preview (image + audio waveforms)

## 🧑‍🎨 User-Generated Asset Library

- [ ] Create /game/user_assets/ with YAML tracker
- [ ] Hook into drag-and-drop & import logic
- [ ] Auto-populate user_assets.yaml with metadata
- [ ] Create tagging UI (name, type, resolution, tags)
- [ ] Add “favorite” & “publish to shared lib” features

## 🌌 AI-Assisted Sandbox

- [ ] Create ai/ module scaffold (ai_image_gen.py, ai_audio_gen.py, etc)
- [ ] Add editor/sandbox_ui.py (tabs: image, audio, puzzle)
- [ ] Connect prompt → preview → save to user_assets/
- [ ] Add preset_prompts.yaml for creativity boost
- [ ] Add model selector (local/remote) for each tab
- [ ] Add AI “Surprise Me” logic + poetic prompt generator
