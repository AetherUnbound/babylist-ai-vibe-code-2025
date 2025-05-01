from ppb import Sprite, Image, Vector
from ppb.events import KeyPressed


class Player(Sprite):
    position = Vector(0, 0)  # Start position at the center
    image = Image("assets/player.png")  # Use Image resource class
    speed = 0.25  # Movement speed per key press
    
    def on_key_pressed(self, event: KeyPressed, signal):
        # Define movement vector based on key press
        movement = Vector(0, 0)
        
        # Vim-style movement controls
        if event.key == "k":  # Up
            movement = Vector(0, 1) * self.speed
        elif event.key == "j":  # Down
            movement = Vector(0, -1) * self.speed
        elif event.key == "h":  # Left
            movement = Vector(-1, 0) * self.speed
        elif event.key == "l":  # Right
            movement = Vector(1, 0) * self.speed
        else:
            return  # If not a movement key, exit early
        
        # Calculate new position
        new_position = self.position + movement
        
        # Check if we would hit a wall
        for wall in self.scene.get(kind=Sprite):
            if not hasattr(wall, 'is_wall') or not wall.is_wall:
                continue
                
            # Check if we're too close to a wall
            if (new_position - wall.position).length < 0.8:
                return  # Don't move if we hit a wall
        
        # Update position if no collision
        self.position = new_position