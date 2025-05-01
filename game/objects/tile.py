from ppb import Sprite, Image

class Tile(Sprite):
    size = 0.95  # Slightly smaller to prevent overlap issues
    
    def __init__(self, is_wall=True, **kwargs):
        super().__init__(**kwargs)
        self.is_wall = is_wall
        self.image = Image("assets/wall.png") if is_wall else Image("assets/floor.png")