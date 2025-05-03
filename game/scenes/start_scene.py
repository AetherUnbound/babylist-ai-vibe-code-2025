from ppb import Scene, Image, Sprite
from ppb.events import ReplaceScene, KeyPressed
from ppb import Vector

class BackgroundSprite(Sprite):
    size = 20  # Large enough to cover the screen
    position = Vector(0, 0)  # Center of the screen
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.image = Image("assets/splash_screen.png")

class StartScene(Scene):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Add a background sprite instead of setting a background property
        self.add(BackgroundSprite())
        
    def on_key_pressed(self, event: KeyPressed, signal):
        # When any key is pressed, transition to the main game scene
        from game.scenes.main_scene import MainScene
        signal(ReplaceScene(MainScene))