# 8-Bit Game Suite - Copilot Workspace Instructions

## 📚 Project Overview

This is a classic arcade-style game collection built in Python using `pygame`. It features a modular structure divided into core engine components and independent game scenes (Snake, Tic-Tac-Toe, Rock-Paper-Scissors).

## 🛠️ Stack & Dependencies

- **Language**: Python 3.12
- **Engine/Graphics**: `pygame`
- **Numerics**: `numpy`
- **Packaging**: `pyinstaller`
- **Testing**: `pytest`
- **Code Formatting**: `black`
- **Dependency Management**: `requirements.txt` / `pip`

## 🏗️ Architecture & Component Boundaries

- **`core/`**: Contains the foundational engine logic (`base_scene.py`, `scene_manager.py`, `settings.py`). Modifying these files affects all games. Treat these as reusable interfaces.
- **`scenes/`**: Contains individual game implementations (`menu.py`, `snake.py`, etc.). Each scene usually inherits from `BaseScene` (or similar found in `core/`).
- **`assets/`**: Put all fonts (`assets/fonts/`) and sounds (`assets/sounds/`) here. When loading assets, use paths relative to the project root.
- **`tests/`**: Unit tests go here (`test_rps.py`, `test_snake.py`, etc.). Tests should be runnable via `pytest`. Name all test files `test_*.py`.

## 🧑‍💻 Code Style & Conventions

1. **Formatting**: All files must be formatted using `black` before committing. 4-space indentation is enforced.
2. **Style**: Follow PEP 8 guidelines. Use type hints on all functions and classes.
3. **Naming**: `snake_case` for variables and functions, `PascalCase` for classes, `UPPER_CASE` for constants.
4. **Strings**: Prefer f-strings over `.format()` or `%` formatting.
5. **Functions**: Keep functions small and single-purpose. Add docstrings to all functions and classes.
6. **Avoid**: Global variables, bare `except` clauses, and deeply nested logic.
7. **Pygame conventions**:
    - Always call `pygame.quit()` on exit.
    - Use constants for screen dimensions and colors.
    - Manage game state appropriately in the scene classes.
    - Keep render (`draw`) logic separate from update (physics/mechanics) logic within scenes.
8. **Paths**: Always use relative paths safely (e.g. `import os` and `os.path.join`) when loading files like fonts or sounds, to ensure it works across platforms.
9. **Testing**: Add or update `pytest` cases in `tests/` whenever new mechanic logic is added. Avoid instantiating `pygame.display` in headless unit tests to prevent CI/local breaks.

## 🚀 Common Commands

- **Run the game**:
    ```bash
    python main.py
    ```
- **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
- **Run tests**:
    ```bash
    python -m pytest tests/
    ```
- **Format code**:
    ```bash
    python -m black .
    ```

## ⚠️ Potential Pitfalls

- **Window Initialization**: Wait to initialize the pygame display until `main.py` is running. This prevents scenes from inadvertently popping up windows when imported (e.g., during testing).
- **Environment**: If `pytest` fails with module not found, ensure you are running operations within the Python virtual environment (`venv`).
- **Python Version**: This project targets Python 3.12. Do not use syntax or features exclusive to 3.13+.
- **PyInstaller**: When packaging with `pyinstaller`, make sure all asset paths use `os.path.join` and are bundled correctly in the `.spec` file.
