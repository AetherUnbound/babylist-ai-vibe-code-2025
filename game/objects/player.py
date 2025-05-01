from ppb import Sprite, Image


class Player(Sprite):
    position = (0, 0)  # Start position at the center
    image = Image("assets/player.png")  # Use Image resource class