from ppb import BaseScene
from game.objects.player import Player

class MainScene(BaseScene):
    def __init__(self, **props):
        super().__init__(**props)
        self.add(Player())  # Add player to the scene