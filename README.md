# 8-Bit Game Suite

A classic arcade-style game collection built with Python. This suite features a retro 8-bit aesthetic and includes three beloved mini-games you can play right from your computer!

## Games Included
- **Snake**: The classic grow-as-you-eat survival game.
- **Tic-Tac-Toe**: A strategic logic game against a friend or the computer.
- **Rock, Paper, Scissors**: Test your luck in this timeless hand game.

## Features
- Classic 8-bit style graphics (custom fonts and sounds)
- Intuitive Menu and Scene-based navigation
- Modular codebase for easy addition of new games
- Unit tests to ensure smooth gameplay

## Installation

1. Clone or download the repository to your local machine.
2. Ensure you have Python installed.
3. Install the required dependencies:
`bash
pip install -r requirements.txt
`

## Usage

Start the game suite by running the main entry point:
`bash
python main.py
`

## Project Structure
- assets/: Contains custom 8-bit fonts and sound effects.
- core/: Base engine logic (\base_scene.py\, \scene_manager.py\, \settings.py\).
- scenes/: Individual game implementations (\menu.py\, \snake.py\, \	ictactoe.py\, \
ps.py\).
- 	ests/: Automated test suite.

