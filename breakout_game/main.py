"""
Start game with terminal: python -m breakout_game.main
"""

from .game_logic import Game


def main():
    Game().run()


if __name__ == "__main__":
    main()