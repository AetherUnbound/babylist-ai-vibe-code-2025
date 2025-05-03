"""
Diaper Dungeons - Game Framework (Python 3.7, Pygame)
"""

import pygame
import sys
import csv
import random
import os
from datetime import datetime
from pygame.locals import *

# --- Configuration ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
LEVEL_DURATION = 12.0
DARK_PURPLE = (31, 27, 46)  # New background color

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
BLUE = (0, 0, 255)

# Game Phases
INSERT = "insert"
EXIT = "exit"

# Initialize Pygame
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Diaper Dungeons")
clock = pygame.time.Clock()

# Load assets
binky_full = pygame.image.load("assets/sprites/binky_full.png")
binky_empty = pygame.image.load("assets/sprites/binky_empty.png")
baby_sprites = {
    "left": pygame.transform.scale(pygame.image.load("assets/sprites/baby_left.png"), (40, 40)),
    "right": pygame.transform.scale(pygame.image.load("assets/sprites/baby_right.png"), (40, 40)),
    "forward": pygame.transform.scale(pygame.image.load("assets/sprites/baby_forward.png"), (40, 40))
}
alien_sprite = pygame.transform.scale(pygame.image.load("assets/sprites/alien.png"), (40, 40))
intro_image = pygame.transform.scale(pygame.image.load("assets/sprites/intro_image.png"), (SCREEN_WIDTH, SCREEN_HEIGHT))
instructions_image = pygame.transform.scale(pygame.image.load("assets/sprites/instructions_image.png"), (SCREEN_WIDTH, SCREEN_HEIGHT))

# Load bottle sprite
bottle_sprite = pygame.transform.scale(pygame.image.load("assets/sprites/bottle.png"), (40, 40))

def load_sound_safe(path):
    if not os.path.exists(path):
        print(f"Warning: Sound file not found: {path}")
        return None
    try:
        return pygame.mixer.Sound(path)
    except pygame.error:
        print(f"Warning: Could not load sound '{path}'")
        return None

giggle_sound = load_sound_safe("assets/sounds/giggle.wav")
poof_sound = load_sound_safe("assets/sounds/poof.wav")
beep_sound = load_sound_safe("assets/sounds/beep.wav")

# --- Helper Classes ---
class LaserBeam(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = pygame.Surface((20, 5))
        self.image.fill(PURPLE)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction
        self.speed = 12
        
    def update(self):
        if self.direction == "left":
            self.rect.x -= self.speed
        elif self.direction == "right":
            self.rect.x += self.speed
        elif self.direction == "up":
            self.rect.y -= self.speed
        elif self.direction == "down":
            self.rect.y += self.speed
            
        # Remove if off screen
        if (self.rect.right < 0 or 
            self.rect.left > SCREEN_WIDTH or 
            self.rect.bottom < 0 or 
            self.rect.top > SCREEN_HEIGHT):
            self.kill()

class Bottle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = bottle_sprite
        self.rect = self.image.get_rect(center=(random.randint(40, SCREEN_WIDTH - 40), 
                                              random.randint(40, SCREEN_HEIGHT - 40)))
        self.spawn_time = pygame.time.get_ticks()
        self.duration = 5000  # 5 seconds

    def update(self):
        # Make bottle flash when it's about to disappear
        current_time = pygame.time.get_ticks()
        if current_time - self.spawn_time > self.duration:
            self.kill()
        
        # Make bottle flash when it's about to disappear
        if (self.duration - (current_time - self.spawn_time)) < 1000:  # Last second
            if int(current_time / 200) % 2 == 0:  # Flash every 200ms
                self.image.set_alpha(100)
            else:
                self.image.set_alpha(255)

class Baby(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = baby_sprites["forward"]
        self.rect = self.image.get_rect(center=(random.randint(40, SCREEN_WIDTH - 40), random.randint(40, SCREEN_HEIGHT - 40)))
        self.lives = 3
        self.invulnerable = False
        self.invulnerable_timer = 0
        self.facing = "forward"  # Track which direction baby is facing
        self.dd_pressed = False  # Track if 'd' key has been pressed once
        self.dd_time = 0  # Time when 'd' was first pressed
        self.speed = 5  # Base movement speed
        self.speed_boost = 0  # Additional speed
        self.speed_boost_timer = 0  # Timer for speed boost

    def update(self, keys, dt, lasers_group, bottles_group):
        if self.invulnerable:
            self.invulnerable_timer -= dt
            if self.invulnerable_timer <= 0:
                self.invulnerable = False
                
        # Update speed boost timer
        if self.speed_boost > 0:
            self.speed_boost_timer -= dt
            if self.speed_boost_timer <= 0:
                self.speed_boost = 0
        
        current_speed = self.speed + self.speed_boost
        
        # Detect movement and set direction
        if keys[K_h]:
            self.rect.x -= current_speed
            self.image = baby_sprites["left"]
            self.facing = "left"
        elif keys[K_l]:
            self.rect.x += current_speed
            self.image = baby_sprites["right"]
            self.facing = "right"
        elif keys[K_j]:
            self.rect.y += current_speed
            self.image = baby_sprites["forward"]
            self.facing = "down"
        elif keys[K_k]:
            self.rect.y -= current_speed
            self.image = baby_sprites["forward"]
            self.facing = "up"

        # Constrain to screen bounds
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            
        # Handle "dd" attack command
        if keys[K_d]:
            current_time = pygame.time.get_ticks()
            if not self.dd_pressed:
                # First 'd' press
                self.dd_pressed = True
                self.dd_time = current_time
            elif current_time - self.dd_time < 500:  # 500ms window to press 'd' twice
                # Second 'd' press - fire laser!
                self.dd_pressed = False
                self.fire_laser(lasers_group)
        else:
            # Reset if 'd' key released
            if self.dd_pressed and pygame.time.get_ticks() - self.dd_time > 500:
                self.dd_pressed = False
                
        # Handle "o" to pick up bottles
        bottles_hit = pygame.sprite.spritecollide(self, bottles_group, False)
        if bottles_hit and keys[K_o]:
            for bottle in bottles_hit:
                if self.lives < 3:
                    self.lives += 1
                else:
                    # Boost speed if already at max lives
                    self.speed_boost = 3
                    self.speed_boost_timer = 10.0  # 10 seconds of boost
                bottle.kill()
                if beep_sound:
                    beep_sound.play()
    
    def fire_laser(self, lasers_group):
        if self.facing == "left":
            laser = LaserBeam(self.rect.left, self.rect.centery, "left")
        elif self.facing == "right":
            laser = LaserBeam(self.rect.right, self.rect.centery, "right")
        elif self.facing == "up":
            laser = LaserBeam(self.rect.centerx, self.rect.top, "up")
        else:  # down/forward
            laser = LaserBeam(self.rect.centerx, self.rect.bottom, "down")
        
        lasers_group.add(laser)
        if poof_sound:
            poof_sound.play()
    
    def get_hit(self):
        if not self.invulnerable:
            self.lives -= 1
            self.invulnerable = True
            self.invulnerable_timer = 1.5  # 1.5 seconds of invulnerability
            return True
        return False

    def draw(self, surface):
        # Make the baby flash when invulnerable
        if self.invulnerable:
            if int(pygame.time.get_ticks() / 200) % 2 == 0:  # Flash every 200ms
                surface.blit(self.image, self.rect)
        else:
            surface.blit(self.image, self.rect)
            
        # Visual indicator for "d" pressed once
        if self.dd_pressed:
            pygame.draw.circle(surface, RED, (self.rect.centerx, self.rect.top - 10), 5)
            
        # Visual indicator for speed boost
        if self.speed_boost > 0:
            pygame.draw.circle(surface, GREEN, (self.rect.centerx, self.rect.top - 20), 5)

class Alien(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = alien_sprite
        self.rect = self.image.get_rect(center=(random.randint(50, 750), random.randint(50, 550)))
        self.velocity = [random.choice([-2, 2]), random.choice([-2, 2])]
        
    def update(self):
        # Always apply movement (instead of just when chasing/fleeing)
        self._bounce_within_screen()
        
    def _bounce_within_screen(self):
        # Apply velocity to position
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        
        # Bounce off screen edges
        if self.rect.left < 0:
            self.rect.left = 0
            self.velocity[0] = abs(self.velocity[0])  # Ensure positive X velocity
        elif self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            self.velocity[0] = -abs(self.velocity[0])  # Ensure negative X velocity
            
        if self.rect.top < 0:
            self.rect.top = 0
            self.velocity[1] = abs(self.velocity[1])  # Ensure positive Y velocity
        elif self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.velocity[1] = -abs(self.velocity[1])  # Ensure negative Y velocity

    def flee(self, target):
        # Calculate direction away from target
        dx = self.rect.x - target.rect.x
        dy = self.rect.y - target.rect.y
        distance = max(1, (dx ** 2 + dy ** 2) ** 0.5)
        
        # Adjust velocity based on flee direction (away from target)
        flee_speed = 3
        self.velocity[0] = int(flee_speed * dx / distance)
        self.velocity[1] = int(flee_speed * dy / distance)
        
        # Make sure velocity isn't zero
        if self.velocity[0] == 0:
            self.velocity[0] = random.choice([-1, 1])
        if self.velocity[1] == 0:
            self.velocity[1] = random.choice([-1, 1])

    def chase(self, target):
        # Calculate direction toward target
        dx = target.rect.x - self.rect.x
        dy = target.rect.y - self.rect.y
        distance = max(1, (dx ** 2 + dy ** 2) ** 0.5)
        
        # Adjust velocity based on chase direction (toward target)
        chase_speed = 3
        self.velocity[0] = int(chase_speed * dx / distance)
        self.velocity[1] = int(chase_speed * dy / distance)
        
        # Make sure velocity isn't zero
        if self.velocity[0] == 0:
            self.velocity[0] = random.choice([-1, 1])
        if self.velocity[1] == 0:
            self.velocity[1] = random.choice([-1, 1])

# --- Logger ---
def initialize_log():
    with open("data/logs.csv", mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["timestamp", "round", "phase", "event_type", "reason"])

def log_mistake(round_num, phase, event_type, reason):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("data/logs.csv", mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, round_num + 1, phase, event_type, reason])

# --- Timer Bar ---
def draw_binkies(surface, lives):
    for i in range(3):
        icon = binky_full if i < lives else binky_empty
        icon = pygame.transform.scale(icon, (30, 30))
        surface.blit(icon, (10 + i * 35, 10))

def draw_timer_bar(surface, time_left, total_time, phase):
    bar_width = int((time_left / total_time) * SCREEN_WIDTH)
    color = GREEN if time_left > 2.0 else RED
    pygame.draw.rect(surface, color, (0, SCREEN_HEIGHT - 20, bar_width, 20))
    if time_left <= 2.0:
        font = pygame.font.SysFont(None, 36)
        if phase == INSERT:
            msg = "PRESS 'x' TO DEFEND!"
        else:
            msg = "PRESS 'i' TO INSERT!"
        text = font.render(msg, True, RED)
        surface.blit(text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT - 60))

# --- Game Functions ---
def main_menu():
    font = pygame.font.SysFont(None, 48)
    played_beep = False
    while True:
        screen.fill(BLACK)
        screen.blit(intro_image, (0, 0))
        text = font.render("Press 'i' to start", True, WHITE)
        screen.blit(text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT - 100))
        pygame.display.flip()

        if beep_sound and not played_beep:
            beep_sound.play()
            played_beep = True
            
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_i:
                    show_instructions()
                    return

def show_instructions():
    showing = True
    font = pygame.font.SysFont(None, 48)
    small_font = pygame.font.SysFont(None, 32)
    while showing:
        screen.fill(BLACK)
        screen.blit(instructions_image, (0, 0))
        
        # Add attack instructions
        text = font.render("Press 'dd' to attack in ATTACK MODE", True, WHITE)
        screen.blit(text, (SCREEN_WIDTH // 2 - 240, SCREEN_HEIGHT - 140))
        
        # Add bottle instructions
        bottle_text = small_font.render("Press 'o' to pick up bottles for extra lives", True, WHITE)
        screen.blit(bottle_text, (SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT - 100))
        
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                showing = False

def game_over_screen(score):
    font = pygame.font.SysFont(None, 64)
    small_font = pygame.font.SysFont(None, 36)
    showing = True
    while showing:
        screen.fill(BLACK)
        game_over_text = font.render("Game Over", True, RED)
        score_text = small_font.render(f"Aliens Defeated: {score}", True, WHITE)
        retry_text = small_font.render("Press 'r' to try again or 'q' to quit", True, WHITE)
        
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 80))
        screen.blit(score_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 20))
        screen.blit(retry_text, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 + 40))
        
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_r:
                    play_game()
                    return
                elif event.key == K_q:
                    pygame.quit()
                    sys.exit()

def play_game():
    initialize_log()
    baby = Baby()
    aliens = pygame.sprite.Group([Alien() for _ in range(3)])
    lasers = pygame.sprite.Group()
    bottles = pygame.sprite.Group()
    phase = INSERT
    round_num = 0
    timer = LEVEL_DURATION
    last_sound_time = 0
    aliens_defeated = 0
    phase_switch_warning = False
    
    # Game timing variables
    last_bottle_spawn = 0
    last_alien_spawn = 0
    bottle_spawn_interval = 10000  # 10 seconds
    alien_spawn_interval = 15000   # 15 seconds initially
    
    # Font for UI
    font = pygame.font.SysFont(None, 36)
    small_font = pygame.font.SysFont(None, 24)

    while round_num < 4 and baby.lives > 0:
        dt = clock.tick(FPS) / 1000
        timer -= dt
        current_time = pygame.time.get_ticks()

        # Get keyboard input
        keys = pygame.key.get_pressed()
        
        # Update game objects
        baby.update(keys, dt, lasers, bottles)
        lasers.update()
        bottles.update()
        
        # Update all aliens (they'll always move)
        for alien in aliens:
            alien.update()

        # Check for events
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and timer <= 2.0:
                if phase == INSERT and event.key == K_x:
                    phase = EXIT
                    timer = LEVEL_DURATION
                    phase_switch_warning = False
                    continue
                elif phase == EXIT and event.key == K_i:
                    phase = INSERT
                    timer = LEVEL_DURATION
                    phase_switch_warning = False
                    continue
            if event.type == KEYDOWN:
                if phase == INSERT and event.key == K_d:
                    # Single 'd' press is handled in Baby class
                    pass
                if phase == EXIT and event.key == K_x:
                    log_mistake(round_num, phase, "keypress", "Wrong phase switch")

        # Spawn bottles occasionally
        if current_time - last_bottle_spawn > bottle_spawn_interval:
            last_bottle_spawn = current_time
            bottles.add(Bottle())
            
        # Spawn more aliens over time
        if current_time - last_alien_spawn > alien_spawn_interval:
            last_alien_spawn = current_time
            # Make aliens spawn more frequently as game progresses
            alien_spawn_interval = max(5000, alien_spawn_interval - 1000)
            
            # Don't let aliens get too numerous
            if len(aliens) < 5 + round_num:
                new_alien = Alien()
                # Make sure it doesn't spawn on the baby
                while pygame.sprite.collide_rect(new_alien, baby):
                    new_alien.rect.center = (random.randint(50, 750), random.randint(50, 550))
                aliens.add(new_alien)

        # Handle phase behavior
        screen.fill(DARK_PURPLE)  # New background color

        # In INSERT phase, aliens flee from baby
        if phase == INSERT:
            for alien in aliens:
                alien.flee(baby)
        # In EXIT phase, aliens chase baby
        elif phase == EXIT:
            for alien in aliens:
                alien.chase(baby)
                if baby.rect.colliderect(alien.rect):
                    if baby.get_hit():  # Only play sound if actually hit (not during invulnerability)
                        log_mistake(round_num, phase, "collision", "Hit by alien")
                        if giggle_sound:
                            giggle_sound.play()
                        if baby.lives == 0:
                            game_over_screen(aliens_defeated)
                            return
        
        # Handle laser collisions with aliens
        # Only allow attacks in INSERT (attack) mode
        if phase == INSERT:
            for laser in lasers:
                alien_hit = pygame.sprite.spritecollide(laser, aliens, True)
                if alien_hit:
                    laser.kill()
                    aliens_defeated += len(alien_hit)
                    if giggle_sound:
                        giggle_sound.play()
                    
                    # Add a new alien if we're below the target count
                    if len(aliens) < 3 + round_num:
                        new_alien = Alien()
                        # Make sure it doesn't spawn on the baby
                        while pygame.sprite.collide_rect(new_alien, baby):
                            new_alien.rect.center = (random.randint(50, 750), random.randint(50, 550))
                        aliens.add(new_alien)

        # Lose life if timer runs out without switching phases
        if timer <= 0 and not phase_switch_warning:
            phase_switch_warning = True
            baby.get_hit()
            if giggle_sound:
                giggle_sound.play()
            if baby.lives == 0:
                game_over_screen(aliens_defeated)
                return
            timer = LEVEL_DURATION
            round_num += 1
            if round_num >= 4:
                game_over_screen(aliens_defeated)
                return

        # Draw everything
        aliens.draw(screen)
        lasers.draw(screen)
        bottles.draw(screen)
        baby.draw(screen)
        
        # UI elements
        draw_binkies(screen, baby.lives)
        draw_timer_bar(screen, timer, LEVEL_DURATION, phase)
        
        # Game mode indicator
        mode_text = "ATTACK MODE" if phase == INSERT else "DEFEND MODE"
        mode_color = RED if phase == INSERT else GREEN
        mode_render = font.render(mode_text, True, mode_color)
        screen.blit(mode_render, (SCREEN_WIDTH // 2 - 100, 10))
        
        # Score display
        score_text = small_font.render(f"Aliens Defeated: {aliens_defeated}", True, WHITE)
        screen.blit(score_text, (SCREEN_WIDTH - 180, 10))
        
        # Vim command hints
        if phase == INSERT:
            vim_text = small_font.render("Type 'dd' to attack", True, YELLOW)
            screen.blit(vim_text, (SCREEN_WIDTH - 180, 40))
            
        bottle_text = small_font.render("Press 'o' near bottles", True, YELLOW)
        screen.blit(bottle_text, (SCREEN_WIDTH - 180, 70))
        
        # Display speed boost status if active
        if baby.speed_boost > 0:
            boost_text = small_font.render(f"Speed Boost: {baby.speed_boost_timer:.1f}s", True, GREEN)
            screen.blit(boost_text, (SCREEN_WIDTH - 180, 100))
        
        pygame.display.flip()

    # If we've completed all rounds successfully
    if baby.lives > 0:
        victory_screen(aliens_defeated)
    else:
        game_over_screen(aliens_defeated)

def victory_screen(score):
    font = pygame.font.SysFont(None, 64)
    small_font = pygame.font.SysFont(None, 36)
    showing = True
    while showing:
        screen.fill((50, 100, 50))  # Green background for victory
        victory_text = font.render("Victory!", True, YELLOW)
        score_text = small_font.render(f"Aliens Defeated: {score}", True, WHITE)
        retry_text = small_font.render("Press 'r' to play again or 'q' to quit", True, WHITE)
        
        screen.blit(victory_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 80))
        screen.blit(score_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 20))
        screen.blit(retry_text, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 + 40))
        
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_r:
                    play_game()
                    return
                elif event.key == K_q:
                    pygame.quit()
                    sys.exit()

# --- Main Entry Point ---
if __name__ == '__main__':
    main_menu()
    play_game()
    pygame.quit()
