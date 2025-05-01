from ppb import Scene, Image
from ppb.events import ReplaceScene

class StartScene(Scene):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Background will be our splash screen
        self.background = Image("assets/splash-screen.png")
        
    def on_key_pressed(self, event, signal):
        # When any key is pressed, transition to the main game scene
        from game.scenes.main_scene import MainScene
        signal(ReplaceScene(MainScene))