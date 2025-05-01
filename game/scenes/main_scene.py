from ppb import Scene
from game.objects.player import Player

class MainScene(Scene):
    def __init__(self, **props):
        super().__init__(**props)
        self.add(Player())  # Add player to the scene