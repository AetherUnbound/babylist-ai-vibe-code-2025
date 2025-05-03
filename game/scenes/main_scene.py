from ppb import Scene, Vector
import random
from game.objects.player import Player
from game.objects.tile import Tile

class MainScene(Scene):
    # Define constants for dungeon generation
    GRID_WIDTH = 32  # Reduced from 40 to ensure visibility
    GRID_HEIGHT = 24  # Reduced from 30 to ensure visibility
    MIN_ROOM_SIZE = 3
    MAX_ROOM_SIZE = 7  # Reduced from 8 to keep rooms proportional
    MAX_ROOMS = 12  # Reduced from 15 to prevent overcrowding
    
    # Set camera for the scene
    # This ensures everything is visible
    default_camera_position = Vector(0, 0)
    default_camera_zoom = 0.65  # More aggressive zoom to fit everything
    
    def __init__(self, **props):
        super().__init__(**props)
        
        # Initialize the dungeon grid with walls
        self.grid = [[True for _ in range(self.GRID_HEIGHT)] for _ in range(self.GRID_WIDTH)]
        
        # Generate the dungeon
        self.generate_dungeon()
        
        # Add tiles to the scene
        self.add_tiles()
        
        # Add player to the scene (on a random floor tile)
        player = Player()
        floor_positions = [(x, y) for x in range(self.GRID_WIDTH) for y in range(self.GRID_HEIGHT) 
                          if not self.grid[x][y]]
        if floor_positions:
            player_pos = random.choice(floor_positions)
            # grid_to_world already returns a Vector
            player.position = self.grid_to_world(player_pos[0], player_pos[1])
        self.add(player)
    
    def generate_dungeon(self):
        # List to keep track of room centers for connecting with corridors
        rooms = []
        
        # Generate random rooms
        for _ in range(self.MAX_ROOMS):
            # Random room size
            width = random.randint(self.MIN_ROOM_SIZE, self.MAX_ROOM_SIZE)
            height = random.randint(self.MIN_ROOM_SIZE, self.MAX_ROOM_SIZE)
            
            # Random room position
            x = random.randint(1, self.GRID_WIDTH - width - 1)
            y = random.randint(1, self.GRID_HEIGHT - height - 1)
            
            # Check if this room overlaps with any existing room
            overlaps = False
            room = {"x1": x, "y1": y, "x2": x + width, "y2": y + height}
            
            for other_room in rooms:
                if (room["x1"] <= other_room["x2"] and room["x2"] >= other_room["x1"] and
                    room["y1"] <= other_room["y2"] and room["y2"] >= other_room["y1"]):
                    overlaps = True
                    break
            
            if not overlaps:
                # Carve out this room
                self.create_room(room)
                
                # Store room center for corridor creation
                new_center = {
                    "x": (room["x1"] + room["x2"]) // 2,
                    "y": (room["y1"] + room["y2"]) // 2
                }
                
                # Connect to previous room
                if rooms:
                    prev_center = {
                        "x": (rooms[-1]["x1"] + rooms[-1]["x2"]) // 2,
                        "y": (rooms[-1]["y1"] + rooms[-1]["y2"]) // 2
                    }
                    
                    # Randomly decide horizontal-then-vertical or vertical-then-horizontal
                    if random.random() < 0.5:
                        self.create_horizontal_tunnel(prev_center["x"], new_center["x"], prev_center["y"])
                        self.create_vertical_tunnel(prev_center["y"], new_center["y"], new_center["x"])
                    else:
                        self.create_vertical_tunnel(prev_center["y"], new_center["y"], prev_center["x"])
                        self.create_horizontal_tunnel(prev_center["x"], new_center["x"], new_center["y"])
                
                rooms.append(room)
    
    def create_room(self, room):
        # Set all tiles in the room to floor
        for x in range(room["x1"], room["x2"]):
            for y in range(room["y1"], room["y2"]):
                if 0 <= x < self.GRID_WIDTH and 0 <= y < self.GRID_HEIGHT:
                    self.grid[x][y] = False
    
    def create_horizontal_tunnel(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            if 0 <= x < self.GRID_WIDTH and 0 <= y < self.GRID_HEIGHT:
                self.grid[x][y] = False
    
    def create_vertical_tunnel(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            if 0 <= x < self.GRID_WIDTH and 0 <= y < self.GRID_HEIGHT:
                self.grid[x][y] = False
    
    def add_tiles(self):
        # Add all tiles to the scene based on the grid
        # Ensure a 1-tile border around the edge to prevent cutoff
        border = 1
        for x in range(border, self.GRID_WIDTH - border):
            for y in range(border, self.GRID_HEIGHT - border):
                tile = Tile(is_wall=self.grid[x][y])
                tile.position = self.grid_to_world(x, y)
                self.add(tile)
    
    def grid_to_world(self, grid_x, grid_y):
        # Convert grid coordinates to world coordinates
        # Center the dungeon in the scene with proper scaling
        # The 0.5 offset centers each tile on its grid position
        world_x = grid_x - self.GRID_WIDTH / 2 + 0.5
        world_y = self.GRID_HEIGHT / 2 - grid_y - 0.5
        
        # Apply a slight scale factor to ensure everything fits
        # This matches our camera zoom setting
        return Vector(world_x, world_y)  # Return Vector instead of tuple