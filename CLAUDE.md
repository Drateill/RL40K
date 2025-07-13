# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Warhammer 40K-themed roguelike game built with Python and Pygame. The game features a player fighting waves of enemies with a morality system, experience progression, and various weapon types.

## Development Commands

### Running the Game
```bash
# Install dependencies first
pip install -r requirements.txt

# Run the main game
python3 main.py
```

### Debugging and Development
```bash
# Run with Python's verbose mode to see import details
python3 -v main.py

# Run with debug output (if DEBUG_MODE is enabled in constants.py)
python3 main.py

# Check code structure and imports
python3 -c "import src.core.game_engine; print('Engine loads successfully')"
```

### Dependencies
- pygame>=2.1.0 - Core game framework for graphics, sound, and input
- numpy>=1.21.0 - Mathematical operations and array handling

### Testing
- Currently no automated test framework is configured
- Manual testing is done by running `python3 main.py`
- The `tests/` directory exists but contains only `__init__.py`

## Architecture

### Core Engine Structure
The game uses a modular architecture centered around:

1. **GameEngine** (`src/core/game_engine.py`) - Main game loop, handles initialization, events, updates, and rendering
2. **SceneManager** (`src/core/scene_manager.py`) - Manages different game states/screens with scene stacking support
3. **Constants** (`src/core/constants.py`) - All game configuration values centralized

### Module Organization

#### `/src/core/` - Engine Foundation
- `game_engine.py` - Main game loop and Pygame initialization
- `scene_manager.py` - Scene switching and state management  
- `constants.py` - Game constants (dimensions, colors, gameplay values)

#### `/src/scenes/` - Game States
- `base_scene.py` - Abstract base class for all scenes
- `game_scene.py` - Main gameplay scene

#### `/src/systems/` - Game Logic Systems
- `entity_manager.py` - Entity lifecycle management
- `collision_system.py` - Physics and collision detection

#### `/src/world/` - World Generation & Management
- `world_generator.py` - Procedural world generation
- `level_manager.py` - Level progression and wave management
- `spawn_system.py` - Enemy and item spawning
- `environment_effects.py` - Environmental gameplay effects

#### Root Level Game Components
- `player.py` - Player character and controls
- `enemies/` - Enemy types (base, basic, special, bosses)
- `bullet.py` - Projectile system
- `items.py` - Collectible items and powerups
- `experience_system.py` - Character progression
- `morality_system.py` - Warhammer 40K faith/corruption mechanics
- `sound_system.py` - Audio management
- `ui_manager.py` - User interface
- `camera.py` - Camera and viewport management
- `pathfinding.py` - AI movement algorithms

### Key Game Systems

1. **Scene-Based Architecture**: Uses SceneManager for different game states
2. **Entity Management**: Centralized entity lifecycle through systems
3. **Morality System**: Faith vs Corruption mechanics affecting gameplay
4. **Wave-Based Combat**: Progressive enemy waves with boss encounters
5. **Experience System**: Level progression with ability unlocks
6. **Audio System**: Comprehensive sound management with multiple channels

### Asset Structure
- `assets/sounds/` - Game audio files
- `assets/textures/` - Visual assets
- `assets/fonts/` - Typography files

### Entry Point
The game starts from `main.py` which initializes the GameEngine and handles basic error cases. The GameEngine creates the scene manager and starts with the main GameScene.

## Development Patterns

### Code Architecture Principles
1. **Separation of Concerns**: Game logic is separated into distinct systems (collision, entities, world generation)
2. **Scene-Based Flow**: All game states are managed through the SceneManager with a scene hierarchy
3. **Entity-Component Pattern**: Entities are managed centrally with specialized systems for different behaviors
4. **Configuration Centralization**: All constants are defined in `src/core/constants.py` for easy modification

### File Organization
- **Root-level files**: Legacy game components that integrate with the new `/src` structure
- **`/src` directory**: New modular architecture with proper separation of concerns
- **Mixed architecture**: Project is in transition - some functionality exists in both root and `/src`

### Key Considerations for Development
1. **Dual File Structure**: Some components like `world_generator.py` exist both at root and in `/src/world/` - prefer `/src` versions
2. **Import Paths**: Main entry point adds `/src` to Python path for cleaner imports
3. **French Comments**: Codebase contains French language comments and print statements
4. **Constants Usage**: Modify gameplay parameters through `src/core/constants.py` rather than hardcoding values
5. **Asset Management**: All assets are organized in `/assets` with subdirectories for different types

### Audio System
- Multiple sound libraries used (`sounds/`, `/assets/sounds/`)
- Comprehensive sound system with volume controls for different categories
- Multiple audio packs included (Free Pack, Scifi Guns, ShootingSound)

### Migration Notes
- `migrate_structure.py` suggests ongoing codebase restructuring
- Legacy files in root directory are being migrated to `/src` structure
- Some duplicate functionality may exist during transition