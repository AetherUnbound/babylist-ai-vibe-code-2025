from ppb import GameEngine
from game.scenes.main_scene import MainScene

if __name__ == "__main__":
    engine = GameEngine(MainScene)
    engine.run()