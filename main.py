from ppb import GameEngine
from game.scenes.start_scene import StartScene

def main():
    # Start the game with the StartScene
    engine = GameEngine(
        first_scene=StartScene,
        resolution=(800, 600),  # Set window size to 800x600 pixels
        title="Diaper Dungeon"  # Optional: Add a window title
    )
    engine.run()

if __name__ == "__main__":
    main()