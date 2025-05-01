from ppb import GameEngine
from game.scenes.start_scene import StartScene

def main():
    # Start the game with the StartScene
    engine = GameEngine(first_scene=StartScene)
    engine.run()

if __name__ == "__main__":
    main()