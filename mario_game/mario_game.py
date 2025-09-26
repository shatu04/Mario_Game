import pygame
import sys
import random
import math

# Initialize Pygame
pygame.init()

# Game Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
FPS = 60

# Colors (RGB values)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
BROWN = (139, 69, 19)
SKY_BLUE = (135, 206, 235)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
GRAY = (128, 128, 128)
DARK_GREEN = (0, 128, 0)
PINK = (255, 192, 203)

# Physics
GRAVITY = 0.8
JUMP_STRENGTH = -15

class Player:
    def __init__(self, x, y):
        self.start_x = x
        self.start_y = y
        self.x = x
        self.y = y
        self.width = 40
        self.height = 60
        self.vel_x = 0
        self.vel_y = 0
        self.speed = 6
        self.on_ground = False
        self.color = RED
        self.invincible = False
        self.invincible_timer = 0
        
    def update(self):
        # Handle invincibility
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False
        
        # Handle input
        keys = pygame.key.get_pressed()
        
        # Reset horizontal velocity
        self.vel_x = 0
        
        # Move left and right
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel_x = -self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel_x = self.speed
            
        # Jump (only if on ground)
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]) and self.on_ground:
            self.vel_y = JUMP_STRENGTH
            self.on_ground = False
        
        # Apply gravity
        self.vel_y += GRAVITY
        
        # Update position
        self.x += self.vel_x
        self.y += self.vel_y
        
        # Keep player on screen (horizontal boundaries)
        if self.x < 0:
            self.x = 0
        elif self.x > SCREEN_WIDTH - self.width:
            self.x = SCREEN_WIDTH - self.width
            
        # Death pit (bottom of screen)
        if self.y > SCREEN_HEIGHT:
            return True  # Player died
            
        return False  # Player alive
    
    def reset_position(self):
        self.x = self.start_x
        self.y = self.start_y
        self.vel_x = 0
        self.vel_y = 0
        self.invincible = True
        self.invincible_timer = 120  # 2 seconds of invincibility
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def draw(self, screen):
        # Flicker effect when invincible
        if self.invincible and self.invincible_timer % 10 < 5:
            return
            
        # Draw Mario with more details
        # Main body
        pygame.draw.rect(screen, self.color, (self.x, self.y + 15, self.width, self.height - 15))
        # Hat
        pygame.draw.rect(screen, BLACK, (self.x + 5, self.y, self.width - 10, 20))
        # Hat logo
        pygame.draw.circle(screen, WHITE, (self.x + 20, self.y + 10), 6)
        pygame.draw.circle(screen, self.color, (self.x + 20, self.y + 10), 4)
        # Eyes
        pygame.draw.circle(screen, WHITE, (self.x + 12, self.y + 25), 5)
        pygame.draw.circle(screen, WHITE, (self.x + 28, self.y + 25), 5)
        pygame.draw.circle(screen, BLACK, (self.x + 14, self.y + 25), 2)
        pygame.draw.circle(screen, BLACK, (self.x + 30, self.y + 25), 2)
        # Mustache
        pygame.draw.ellipse(screen, BLACK, (self.x + 15, self.y + 32, 10, 6))
        # Buttons
        pygame.draw.circle(screen, YELLOW, (self.x + 20, self.y + 45), 3)

class Platform:
    def __init__(self, x, y, width, height, color=BROWN):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        # Add texture based on color
        if self.color == BROWN:
            for i in range(0, self.width, 20):
                pygame.draw.line(screen, BLACK, (self.x + i, self.y), (self.x + i, self.y + self.height), 2)
        elif self.color == GRAY:
            for i in range(0, self.width, 15):
                for j in range(0, self.height, 15):
                    pygame.draw.rect(screen, BLACK, (self.x + i, self.y + j, 2, 2))

class MovingPlatform(Platform):
    def __init__(self, x, y, width, height, speed, min_x, max_x):
        super().__init__(x, y, width, height, PURPLE)
        self.speed = speed
        self.min_x = min_x
        self.max_x = max_x
        self.direction = 1
    
    def update(self):
        self.x += self.speed * self.direction
        if self.x <= self.min_x or self.x >= self.max_x:
            self.direction *= -1

class Coin:
    def __init__(self, x, y, value=10):
        self.x = x
        self.y = y
        self.width = 25
        self.height = 25
        self.collected = False
        self.rotation = 0
        self.value = value
        self.bob_offset = 0
        self.start_y = y
    
    def update(self):
        self.rotation += 8
        self.bob_offset = math.sin(pygame.time.get_ticks() * 0.01) * 5
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y + self.bob_offset, self.width, self.height)
    
    def draw(self, screen):
        if not self.collected:
            y_pos = self.y + self.bob_offset
            # Draw spinning coin with glow effect
            pygame.draw.ellipse(screen, YELLOW, (self.x - 2, y_pos - 2, self.width + 4, self.height + 4))
            pygame.draw.ellipse(screen, ORANGE, (self.x, y_pos, self.width, self.height))
            pygame.draw.ellipse(screen, BLACK, (self.x + 3, y_pos + 3, self.width - 6, self.height - 6), 3)
            # Value indicator for special coins
            if self.value > 10:
                font = pygame.font.Font(None, 20)
                text = font.render(str(self.value), True, BLACK)
                screen.blit(text, (self.x + 5, y_pos + 5))

class Enemy:
    def __init__(self, x, y, speed=2, enemy_type="basic"):
        self.x = x
        self.y = y
        self.width = 35
        self.height = 35
        self.speed = speed
        self.direction = 1
        self.enemy_type = enemy_type
        self.patrol_distance = 100
        self.start_x = x
        
        if enemy_type == "basic":
            self.color = DARK_GREEN
        elif enemy_type == "fast":
            self.color = RED
            self.speed *= 1.5
            self.width = 30
            self.height = 30
        elif enemy_type == "jumper":
            self.color = BLUE
            self.vel_y = 0
            self.jump_timer = 0
    
    def update(self, platforms):
        if self.enemy_type == "jumper":
            # Jumping enemy logic
            self.vel_y += GRAVITY * 0.5
            self.y += self.vel_y
            
            # Jump occasionally
            self.jump_timer += 1
            if self.jump_timer > 120 and abs(self.vel_y) < 1:  # Jump every 2 seconds when on ground
                self.vel_y = -12
                self.jump_timer = 0
            
            # Ground collision for jumper
            for platform in platforms:
                if self.get_rect().colliderect(platform.get_rect()):
                    if self.vel_y > 0 and self.y < platform.y:
                        self.y = platform.y - self.height
                        self.vel_y = 0
        
        # Horizontal movement
        self.x += self.speed * self.direction
        
        # Patrol behavior - turn around after certain distance
        if abs(self.x - self.start_x) > self.patrol_distance:
            self.direction *= -1
        
        # Screen boundary collision
        if self.x <= 0 or self.x >= SCREEN_WIDTH - self.width:
            self.direction *= -1
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        
        # Different appearance based on type
        if self.enemy_type == "basic":
            # Basic enemy face
            pygame.draw.circle(screen, BLACK, (self.x + 10, self.y + 12), 3)
            pygame.draw.circle(screen, BLACK, (self.x + 25, self.y + 12), 3)
            pygame.draw.rect(screen, BLACK, (self.x + 12, self.y + 22, 10, 3))
        elif self.enemy_type == "fast":
            # Fast enemy with angry face
            pygame.draw.polygon(screen, BLACK, [(self.x + 8, self.y + 15), (self.x + 12, self.y + 8), (self.x + 16, self.y + 15)])
            pygame.draw.polygon(screen, BLACK, [(self.x + 18, self.y + 15), (self.x + 22, self.y + 8), (self.x + 26, self.y + 15)])
            pygame.draw.rect(screen, WHITE, (self.x + 10, self.y + 20, 12, 4))
        elif self.enemy_type == "jumper":
            # Jumper with spring-like appearance
            pygame.draw.circle(screen, WHITE, (self.x + 12, self.y + 12), 4)
            pygame.draw.circle(screen, WHITE, (self.x + 23, self.y + 12), 4)
            pygame.draw.circle(screen, BLACK, (self.x + 12, self.y + 12), 2)
            pygame.draw.circle(screen, BLACK, (self.x + 23, self.y + 12), 2)
            # Spring coils
            for i in range(3):
                y_offset = self.y + 25 + i * 3
                pygame.draw.line(screen, BLACK, (self.x + 5, y_offset), (self.x + 30, y_offset), 2)

class PowerUp:
    def __init__(self, x, y, power_type="speed"):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 30
        self.collected = False
        self.power_type = power_type
        self.bob_offset = 0
        
    def update(self):
        self.bob_offset = math.sin(pygame.time.get_ticks() * 0.015) * 3
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y + self.bob_offset, self.width, self.height)
    
    def draw(self, screen):
        if not self.collected:
            y_pos = self.y + self.bob_offset
            if self.power_type == "speed":
                pygame.draw.rect(screen, BLUE, (self.x, y_pos, self.width, self.height))
                pygame.draw.polygon(screen, WHITE, [(self.x + 10, y_pos + 15), (self.x + 20, y_pos + 10), (self.x + 20, y_pos + 20)])
            elif self.power_type == "jump":
                pygame.draw.rect(screen, GREEN, (self.x, y_pos, self.width, self.height))
                pygame.draw.polygon(screen, WHITE, [(self.x + 15, y_pos + 5), (self.x + 10, y_pos + 20), (self.x + 20, y_pos + 20)])

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Super Mario Bros - 3 Levels")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Game state
        self.score = 0
        self.lives = 5
        self.current_level = 1
        self.game_over = False
        self.level_complete = False
        self.game_won = False
        
        # Fonts
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        
        # Power-up effects
        self.speed_boost_timer = 0
        self.jump_boost_timer = 0
        
        self.setup_level()
    
    def setup_level(self):
        """Setup the current level with appropriate difficulty"""
        # Create player at start position
        if self.current_level == 1:
            self.player = Player(50, SCREEN_HEIGHT - 150)
        else:
            self.player = Player(50, SCREEN_HEIGHT - 200)
        
        # Clear existing objects
        self.platforms = []
        self.moving_platforms = []
        self.coins = []
        self.enemies = []
        self.power_ups = []
        
        if self.current_level == 1:
            self.setup_level_1()  # Easy
        elif self.current_level == 2:
            self.setup_level_2()  # Medium
        elif self.current_level == 3:
            self.setup_level_3()  # Hard
    
    def setup_level_1(self):
        """Easy Level - Simple platforms and few enemies"""
        # Ground and basic platforms
        self.platforms = [
            Platform(0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50),  # Ground
            Platform(200, 550, 150, 20),
            Platform(450, 450, 150, 20),
            Platform(700, 350, 150, 20),
            Platform(300, 250, 100, 20),
            Platform(600, 150, 150, 20),
            Platform(850, 100, 100, 30),  # Final platform
        ]
        
        # Easy coins
        self.coins = [
            Coin(250, 520),
            Coin(500, 420),
            Coin(750, 320),
            Coin(330, 220),
            Coin(650, 120),
            Coin(880, 70),  # Bonus coin
            Coin(100, 500),
            Coin(570, 400),
        ]
        
        # Few basic enemies
        self.enemies = [
            Enemy(250, 530, 1.5, "basic"),
            Enemy(500, 430, 1, "basic"),
            Enemy(350, 230, 1, "basic"),
        ]
        
        # Power-ups
        self.power_ups = [
            PowerUp(750, 320, "speed"),
            PowerUp(650, 120, "jump"),
        ]
    
    def setup_level_2(self):
        """Medium Level - More complex layout with moving platforms"""
        # More complex platforms
        self.platforms = [
            Platform(0, SCREEN_HEIGHT - 50, 200, 50),  # Partial ground
            Platform(300, SCREEN_HEIGHT - 50, 400, 50),  # Partial ground
            Platform(800, SCREEN_HEIGHT - 50, 200, 50),  # Partial ground
            Platform(150, 550, 100, 20),
            Platform(400, 480, 120, 20),
            Platform(650, 400, 100, 20),
            Platform(200, 320, 80, 20),
            Platform(500, 250, 100, 20),
            Platform(750, 180, 120, 20),
            Platform(350, 100, 100, 20),
            Platform(850, 50, 100, 30, GRAY),  # Stone platform
        ]
        
        # Moving platforms
        self.moving_platforms = [
            MovingPlatform(250, 450, 80, 15, 1, 250, 350),
            MovingPlatform(600, 300, 80, 15, 1.5, 550, 700),
            MovingPlatform(100, 200, 60, 15, 2, 100, 250),
        ]
        
        # More coins with higher values
        self.coins = [
            Coin(180, 520),
            Coin(440, 450),
            Coin(680, 370),
            Coin(230, 290),
            Coin(530, 220),
            Coin(780, 150),
            Coin(380, 70),
            Coin(880, 20, 20),  # Bonus coin
            Coin(290, 420),  # On moving platform area
            Coin(640, 270),  # On moving platform area
        ]
        
        # Mix of enemy types
        self.enemies = [
            Enemy(180, 530, 2, "basic"),
            Enemy(440, 460, 2.5, "fast"),
            Enemy(530, 230, 1.5, "basic"),
            Enemy(780, 160, 1, "jumper"),
            Enemy(320, 490, 1.5, "basic"),
        ]
        
        # More power-ups
        self.power_ups = [
            PowerUp(680, 370, "speed"),
            PowerUp(380, 70, "jump"),
            PowerUp(230, 290, "speed"),
        ]
    
    def setup_level_3(self):
        """Hard Level - Complex layout with many obstacles"""
        # Complex platform layout
        self.platforms = [
            Platform(0, SCREEN_HEIGHT - 50, 150, 50),  # Small ground sections
            Platform(250, SCREEN_HEIGHT - 50, 100, 50),
            Platform(450, SCREEN_HEIGHT - 50, 150, 50),
            Platform(700, SCREEN_HEIGHT - 50, 100, 50),
            Platform(900, SCREEN_HEIGHT - 50, 100, 50),
            Platform(100, 580, 60, 15),
            Platform(300, 520, 80, 15),
            Platform(500, 460, 70, 15),
            Platform(750, 400, 60, 15),
            Platform(150, 440, 70, 15),
            Platform(400, 380, 60, 15),
            Platform(650, 320, 80, 15),
            Platform(200, 300, 60, 15),
            Platform(500, 240, 70, 15),
            Platform(800, 200, 80, 15),
            Platform(300, 160, 60, 15),
            Platform(600, 120, 70, 15),
            Platform(100, 80, 60, 15),
            Platform(850, 40, 100, 30, GRAY),  # Final platform
        ]
        
        # Multiple moving platforms
        self.moving_platforms = [
            MovingPlatform(350, 450, 60, 12, 2, 350, 450),
            MovingPlatform(550, 350, 60, 12, 2.5, 500, 600),
            MovingPlatform(250, 250, 60, 12, 1.5, 200, 350),
            MovingPlatform(700, 160, 60, 12, 2, 650, 750),
            MovingPlatform(400, 80, 60, 12, 1.8, 350, 500),
        ]
        
        # Many coins including high-value ones
        self.coins = [
            Coin(130, 550),
            Coin(330, 490),
            Coin(530, 430),
            Coin(780, 370),
            Coin(180, 410),
            Coin(430, 350),
            Coin(680, 290),
            Coin(230, 270),
            Coin(530, 210),
            Coin(830, 170),
            Coin(330, 130),
            Coin(630, 90),
            Coin(130, 50),
            Coin(880, 10, 50),  # High value coin
            Coin(380, 420),  # Moving platform area
            Coin(580, 320),  # Moving platform area
            Coin(280, 220),  # Moving platform area
        ]
        
        # Many enemies of all types
        self.enemies = [
            Enemy(130, 560, 2, "fast"),
            Enemy(330, 500, 1.5, "basic"),
            Enemy(530, 440, 2.5, "fast"),
            Enemy(180, 420, 1, "jumper"),
            Enemy(430, 360, 2, "basic"),
            Enemy(230, 280, 1.5, "jumper"),
            Enemy(530, 220, 2, "fast"),
            Enemy(330, 140, 1, "basic"),
            Enemy(630, 100, 1.5, "jumper"),
            Enemy(280, 510, 1.8, "basic"),  # Extra enemies
        ]
        
        # Lots of power-ups needed for hard level
        self.power_ups = [
            PowerUp(330, 490, "jump"),
            PowerUp(680, 290, "speed"),
            PowerUp(330, 130, "jump"),
            PowerUp(780, 370, "speed"),
            PowerUp(530, 210, "jump"),
        ]
    
    def handle_collisions(self):
        player_rect = self.player.get_rect()
        
        # Platform collisions (static)
        for platform in self.platforms:
            platform_rect = platform.get_rect()
            if player_rect.colliderect(platform_rect):
                if self.player.vel_y > 0 and self.player.y < platform.y:
                    self.player.y = platform.y - self.player.height
                    self.player.vel_y = 0
                    self.player.on_ground = True
        
        # Moving platform collisions
        for platform in self.moving_platforms:
            platform_rect = platform.get_rect()
            if player_rect.colliderect(platform_rect):
                if self.player.vel_y > 0 and self.player.y < platform.y:
                    self.player.y = platform.y - self.player.height
                    self.player.vel_y = 0
                    self.player.on_ground = True
                    # Move player with platform
                    self.player.x += platform.speed * platform.direction
        
        # Coin collection
        for coin in self.coins:
            if not coin.collected and player_rect.colliderect(coin.get_rect()):
                coin.collected = True
                self.score += coin.value
        
        # Power-up collection
        for power_up in self.power_ups:
            if not power_up.collected and player_rect.colliderect(power_up.get_rect()):
                power_up.collected = True
                self.score += 25
                if power_up.power_type == "speed":
                    self.speed_boost_timer = 300  # 5 seconds
                    self.player.speed = 10
                elif power_up.power_type == "jump":
                    self.jump_boost_timer = 300  # 5 seconds
        
        # Enemy collisions
        if not self.player.invincible:
            for enemy in self.enemies:
                if player_rect.colliderect(enemy.get_rect()):
                    self.lose_life()
                    return
        
        # Check level completion (reach right side)
        if self.player.x > SCREEN_WIDTH - 100:
            self.level_complete = True
    
    def lose_life(self):
        self.lives -= 1
        if self.lives <= 0:
            self.game_over = True
        else:
            self.player.reset_position()
    
    def next_level(self):
        if self.current_level < 3:
            self.current_level += 1
            self.level_complete = False
            self.setup_level()
        else:
            self.game_won = True
    
    def update(self):
        if self.game_over or self.game_won:
            return
        
        # Update power-up timers
        if self.speed_boost_timer > 0:
            self.speed_boost_timer -= 1
            if self.speed_boost_timer == 0:
                self.player.speed = 6
        
        if self.jump_boost_timer > 0:
            self.jump_boost_timer -= 1
        
        # Update game objects
        if self.player.update():  # Returns True if player died
            self.lose_life()
            return
        
        for platform in self.moving_platforms:
            platform.update()
        
        for coin in self.coins:
            coin.update()
        
        for power_up in self.power_ups:
            power_up.update()
        
        for enemy in self.enemies:
            enemy.update(self.platforms + self.moving_platforms)
        
        # Handle collisions
        self.handle_collisions()
        
        # Check level completion
        if self.level_complete:
            self.next_level()
    
    def draw_hud(self):
        # Background for HUD
        pygame.draw.rect(self.screen, BLACK, (0, 0, SCREEN_WIDTH, 80))
        pygame.draw.rect(self.screen, WHITE, (0, 0, SCREEN_WIDTH, 80), 2)
        
        # Score
        score_text = self.font_medium.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (20, 20))
        
        # Lives with heart symbols
        lives_text = self.font_medium.render(f"Lives: ", True, WHITE)
        self.screen.blit(lives_text, (20, 45))
        for i in range(self.lives):
            pygame.draw.polygon(self.screen, RED, [
                (120 + i*25, 55), (125 + i*25, 50), (130 + i*25, 50),
                (135 + i*25, 55), (132 + i*25, 65), (127 + i*25, 60),
                (122 + i*25, 65)
            ])
        
        # Level
        level_text = self.font_medium.render(f"Level: {self.current_level}", True, WHITE)
        self.screen.blit(level_text, (400, 20))
        
        # Level difficulty indicator
        difficulties = ["", "EASY", "MEDIUM", "HARD"]
        diff_colors = [WHITE, GREEN, YELLOW, RED]
        diff_text = self.font_small.render(difficulties[self.current_level], True, diff_colors[self.current_level])
        self.screen.blit(diff_text, (400, 45))
        
        # Power-up status
        if self.speed_boost_timer > 0:
            speed_text = self.font_small.render("SPEED BOOST!", True, BLUE)
            self.screen.blit(speed_text, (600, 20))
        
        if self.jump_boost_timer > 0:
            jump_text = self.font_small.render("JUMP BOOST!", True, GREEN)
            self.screen.blit(jump_text, (600, 45))
        
        # Instructions
        inst_text = self.font_small.render("Arrow Keys/WASD: Move | Space/Up/W: Jump | ESC: Quit", True, WHITE)
        self.screen.blit(inst_text, (20, 680))
    
    def draw(self):
        # Clear screen with appropriate background
        if self.current_level == 1:
            self.screen.fill(SKY_BLUE)
        elif self.current_level == 2:
            self.screen.fill((100, 150, 200))  # Darker blue
        else:
            self.screen.fill((80, 80, 120))  # Dark purple-blue
        
        # Draw clouds (more in easier levels)
        if self.current_level <= 2:
            cloud_positions = [(100, 120), (300, 100), (500, 130), (700, 110), (850, 140)]
            for i, (x, y) in enumerate(cloud_positions[:4 - self.current_level + 2]):
                pygame.draw.ellipse(self.screen, WHITE, (x, y, 60, 40))
                pygame.draw.ellipse(self.screen, WHITE, (x + 30, y - 10, 80, 50))
        
        # Draw platforms
        for platform in self.platforms:
            platform.draw(self.screen)
        
        for platform in self.moving_platforms:
            platform.draw(self.screen)
        
        # Draw coins
        for coin in self.coins:
            coin.draw(self.screen)
        
        # Draw power-ups
        for power_up in self.power_ups:
            power_up.draw(self.screen)
        
        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(self.screen)
        
        # Draw player
        self.player.draw(self.screen)
        
        # Draw HUD
        self.draw_hud()
        
        # Draw game over or win screen
        if self.game_over:
            self.draw_game_over()
        elif self.game_won:
            self.draw_victory()
        elif self.level_complete:
            self.draw_level_complete()
    
    def draw_game_over(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Game Over text
        game_over_text = self.font_large.render("GAME OVER", True, RED)
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 100))
        self.screen.blit(game_over_text, text_rect)
        
        # Final score
        score_text = self.font_medium.render(f"Final Score: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
        self.screen.blit(score_text, score_rect)
        
        # Level reached
        level_text = self.font_medium.render(f"Level Reached: {self.current_level}", True, WHITE)
        level_rect = level_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        self.screen.blit(level_text, level_rect)
        
        # Restart instruction
        restart_text = self.font_small.render("Press R to Restart or ESC to Quit", True, YELLOW)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 100))
        self.screen.blit(restart_text, restart_rect)
    
    def draw_victory(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Victory text with rainbow effect
        colors = [RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE]
        victory_text = "CONGRATULATIONS!"
        for i, letter in enumerate(victory_text):
            color = colors[i % len(colors)]
            letter_surface = self.font_large.render(letter, True, color)
            x_offset = i * 35
            self.screen.blit(letter_surface, (SCREEN_WIDTH//2 - 250 + x_offset, SCREEN_HEIGHT//2 - 150))
        
        # You Won text
        won_text = self.font_large.render("YOU WON!", True, YELLOW)
        won_rect = won_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
        self.screen.blit(won_text, won_rect)
        
        # Final score
        score_text = self.font_medium.render(f"Final Score: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        self.screen.blit(score_text, score_rect)
        
        # Completion message
        complete_text = self.font_medium.render("All 3 Levels Completed!", True, GREEN)
        complete_rect = complete_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
        self.screen.blit(complete_text, complete_rect)
        
        # Restart instruction
        restart_text = self.font_small.render("Press R to Play Again or ESC to Quit", True, YELLOW)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 150))
        self.screen.blit(restart_text, restart_rect)
    
    def draw_level_complete(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(150)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Level Complete text
        complete_text = self.font_large.render(f"LEVEL {self.current_level - 1} COMPLETE!", True, GREEN)
        complete_rect = complete_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
        self.screen.blit(complete_text, complete_rect)
        
        # Next level preview
        if self.current_level <= 3:
            next_text = self.font_medium.render(f"Get ready for Level {self.current_level}!", True, WHITE)
            next_rect = next_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            self.screen.blit(next_text, next_rect)
        
        # Continue instruction
        continue_text = self.font_small.render("Press SPACE to Continue", True, YELLOW)
        continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 100))
        self.screen.blit(continue_text, continue_rect)
    
    def restart_game(self):
        self.score = 0
        self.lives = 5
        self.current_level = 1
        self.game_over = False
        self.level_complete = False
        self.game_won = False
        self.speed_boost_timer = 0
        self.jump_boost_timer = 0
        self.setup_level()
    
    def run(self):
        while self.running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_r and (self.game_over or self.game_won):
                        self.restart_game()
                    elif event.key == pygame.K_SPACE and self.level_complete:
                        self.level_complete = False
                    # Special jump boost handling
                    elif (event.key == pygame.K_SPACE or event.key == pygame.K_UP or event.key == pygame.K_w):
                        if self.jump_boost_timer > 0 and self.player.on_ground:
                            self.player.vel_y = JUMP_STRENGTH * 1.3  # Enhanced jump
            
            # Update game
            self.update()
            
            # Draw everything
            self.draw()
            
            # Update display
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

# Run the game
if __name__ == "__main__":
    print("=== SUPER MARIO BROS - 3 LEVELS ===")
    print("CONTROLS:")
    print("- Arrow Keys or WASD: Move Mario")
    print("- Space/Up/W: Jump (hold for higher jumps with power-up)")
    print("- ESC: Quit game")
    print("- R: Restart (when game over)")
    print()
    print("LEVELS:")
    print("- Level 1 (Easy): Basic platforms, few enemies")
    print("- Level 2 (Medium): Moving platforms, mixed enemies") 
    print("- Level 3 (Hard): Complex layout, many obstacles")
    print()
    print("ITEMS:")
    print("- Yellow Coins: 10-50 points")
    print("- Blue Power-up: Speed boost")
    print("- Green Power-up: Jump boost")
    print()
    print("Starting game...")
    
    game = Game()
    game.run()