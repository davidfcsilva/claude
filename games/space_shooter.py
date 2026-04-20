
"""
Space Shooter - Arcade Game
A classic space shooter with multiple enemy types, power-ups, and intense action!
"""

import pygame
import random
import math
from typing import List, Optional, Tuple

# Initialize pygame
pygame.init()

# ============================================================================
# CONFIGURATION
# ============================================================================

# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 100, 255)
YELLOW = (255, 255, 50)
ORANGE = (255, 150, 50)
PURPLE = (200, 50, 255)
CYAN = (50, 255, 255)

# Player settings
PLAYER_SIZE = 40
PLAYER_SPEED = 5
PLAYER_MAX_HEALTH = 100
PLAYER_SHIELD = 50

# Bullet settings
BULLET_SPEED = 10
BULLET_COOLDOWN = 15  # frames between shots

# Enemy settings
ENEMY_TYPES = ['basic', 'fast', 'tank']
ENEMY_SPAWN_RATE = 60  # frames between spawns
ENEMY_BASE_SPEED = 2
BOSS_SIZE = 100

# Power-up settings
POWERUP_TYPES = ['spread_shot', 'rapid_fire', 'shield', 'bomb']
POWERUP_SPAWN_CHANCE = 0.02  # 2% chance per enemy killed

# ============================================================================
# CLASSES
# ============================================================================

class Particle(pygame.sprite.Sprite):
    """Particle for explosion effects"""

    def __init__(self, x: float, y: float, color: Tuple[int, int, int],
                 speed: float = 3, size: int = 4):
        super().__init__()
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        self.image.fill(color, SpecialDrawType=SpecialDrawType.POLY)
        self.rect = self.image.get_rect(center=(x, y))
        self.velocity = random.choice([1, -1]) * random.uniform(0.5, speed)
        self.life = random.uniform(0.5, 1.0)
        self.color = color

    def update(self):
        self.rect.centerx += self.velocity
        self.life -= 0.02
        self.image.set_alpha(self.life * 255)

    def draw(self, surface: pygame.Surface, pos):
        if self.life > 0:
            img = pygame.Surface((4, 4), pygame.SRCALPHA)
            img.fill(*self.color, SpecialDrawType=SpecialDrawType.POLY)
            img.set_alpha(int(self.life * 255))
            surface.blit(img, (pos[0], pos[1]))


class Bullet(pygame.sprite.Sprite):
    """Bullet for player and enemies"""

    def __init__(self, x: float, y: float, is_enemy: bool = False):
        super().__init__()
        self.is_enemy = is_enemy
        self.image = pygame.Surface((6, 10), pygame.SRCALPHA)
        if is_enemy:
            self.image.fill(RED, SpecialDrawType=SpecialDrawType.POLY)
        else:
            self.image.fill(CYAN, SpecialDrawType=SpecialDrawType.POLY)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = BULLET_SPEED if not is_enemy else -BULLET_SPEED // 2

    def update(self):
        if self.is_enemy:
            self.rect.y += self.speed * 0.3
        else:
            self.rect.y += self.speed

        # Remove if off screen
        if self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
            self.kill()

    def draw(self, surface: pygame.Surface, pos):
        surface.blit(self.image, pos)


class PowerUp(pygame.sprite.Sprite):
    """Power-up that appears when enemies are destroyed"""

    def __init__(self, x: float, y: float):
        super().__init__()
        self.type = random.choice(POWERUP_TYPES)
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)

        # Draw power-up icon
        border = pygame.draw.polygon(self.image, (255, 255, 255, 100), [(15, 0), (28, 25), (2, 25)])
        center = (15, 15)

        if self.type == 'spread_shot':
            self.image.fill(GREEN, SpecialDrawType=SpecialDrawType.POLY)
            pygame.draw.circle(self.image, WHITE, center, 8)
            # Draw three bullets
            for i in range(-1, 2):
                pygame.draw.line(self.image, WHITE, (15, 15), (15 + i*5, 5), 2)
            self.text = "S"
            self.color = GREEN

        elif self.type == 'rapid_fire':
            self.image.fill(ORANGE, SpecialDrawType=SpecialDrawType.POLY)
            pygame.draw.circle(self.image, WHITE, center, 8)
            # Draw fast pulse
            pygame.draw.circle(self.image, (255, 255, 255, 150), center, 3)
            self.text = "F"
            self.color = ORANGE

        elif self.type == 'shield':
            self.image.fill(YELLOW, SpecialDrawType=SpecialDrawType.POLY)
            pygame.draw.circle(self.image, WHITE, center, 8)
            # Draw shield icon
            pygame.draw.circle(self.image, (255, 255, 255, 100), center, 5)
            self.text = "S"
            self.color = YELLOW

        else:  # bomb
            self.image.fill(PURPLE, SpecialDrawType=SpecialDrawType.POLY)
            pygame.draw.circle(self.image, WHITE, center, 8)
            self.text = "B"
            self.color = PURPLE

        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 2

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

    def draw(self, surface: pygame.Surface, pos):
        surface.blit(self.image, pos)
        font = pygame.font.Font(None, 20)
        text = font.render(self.text, True, WHITE)
        text_rect = text.get_rect(center=pos)
        surface.blit(text, text_rect)


class Enemy(pygame.sprite.Sprite):
    """Enemy spaceship"""

    def __init__(self, enemy_type: str, x: int, y: int = None, is_boss: bool = False):
        super().__init__()
        self.enemy_type = enemy_type
        self.is_boss = is_boss
        self.x = x
        self.y = y or random.randint(50, SCREEN_HEIGHT - 100)

        # Calculate width based on type
        if enemy_type == 'basic':
            self.width = 40
            self.height = 35
            self.speed = random.uniform(ENEMY_BASE_SPEED, ENEMY_BASE_SPEED * 1.2)
            self.health = 2
            self.points = 100
            self.color = RED
        elif enemy_type == 'fast':
            self.width = 35
            self.height = 30
            self.speed = random.uniform(ENEMY_BASE_SPEED * 1.5, ENEMY_BASE_SPEED * 2)
            self.health = 1
            self.points = 150
            self.color = YELLOW
        elif enemy_type == 'tank':
            self.width = 50
            self.height = 45
            self.speed = random.uniform(ENEMY_BASE_SPEED * 0.5, ENEMY_BASE_SPEED * 0.8)
            self.health = 5
            self.points = 250
            self.color = ORANGE
        elif enemy_type == 'boss':
            self.width = BOSS_SIZE
            self.height = BOSS_SIZE
            self.speed = random.uniform(0.5, 1.0)
            self.health = 50
            self.points = 5000
            self.color = PURPLE
        else:
            return  # Skip this enemy

        # Create enemy sprite
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        # Draw enemy shape
        points = [(0, 0), (self.width, 0), (self.width - 5, self.height), (5, self.height)]
        pygame.draw.polygon(self.image, self.color, points)
        self.rect = self.image.get_rect(midbottom=(self.x, self.y))

        # Boss has health bar
        if self.is_boss:
            self.health_bar_rect = pygame.Rect(
                self.rect.left - 10, self.rect.bottom + 10, self.rect.width + 20, 15
            )

    def update(self):
        if self.is_boss:
            # Boss moves across screen
            self.rect.x += self.speed
            if self.rect.right > SCREEN_WIDTH or self.rect.left < 0:
                self.speed *= -1
        else:
            # Regular enemies move down
            self.rect.y += self.speed
            # Slight horizontal movement
            self.rect.x += math.sin(self.y / 50) * 1

        if self.rect.bottom > SCREEN_HEIGHT:
            self.kill()

    def draw(self, surface: pygame.Surface, pos):
        surface.blit(self.image, pos)

        # Draw health bar if not basic
        if self.enemy_type != 'basic':
            bar_height = 5
            bar_width = self.rect.width
            hp_ratio = self.health / self.max_health
            bar_color = GREEN if hp_ratio > 0.5 else RED if hp_ratio > 0.2 else (255, 0, 0)
            pygame.draw.rect(surface, (0, 0, 0),
                           (pos[0], pos[1] + self.rect.height, bar_width, bar_height))
            pygame.draw.rect(surface, bar_color,
                           (pos[0], pos[1] + self.rect.height,
                            int(bar_width * hp_ratio), bar_height))

    def take_damage(self, damage: int) -> int:
        """Take damage and return remaining health"""
        self.health -= damage
        if self.health <= 0:
            self.kill()
        return max(0, self.health)

    @property
    def max_health(self):
        if self.is_boss:
            return 50
        elif self.enemy_type == 'tank':
            return 5
        elif self.enemy_type == 'fast':
            return 1
        return 2


class Player(pygame.sprite.Sprite):
    """Player spaceship"""

    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE), pygame.SRCALPHA)
        # Draw spaceship shape
        points = [
            (0, PLAYER_SIZE),
            (PLAYER_SIZE // 2 - 5, 0),
            (PLAYER_SIZE, PLAYER_SIZE)
        ]
        pygame.draw.polygon(self.image, BLUE, points)
        # Draw cockpit
        pygame.draw.circle(self.image, WHITE, (PLAYER_SIZE // 2, PLAYER_SIZE // 2), 5)
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80))

        self.health = PLAYER_MAX_HEALTH
        self.shield = 0
        self.shield_timer = 0
        self.shoot_timer = 0
        self.shoot_delay = BULLET_COOLDOWN
        self.weapons = {'spread_shot': 0, 'rapid_fire': 0}
        self.score = 0
        self.level = 1

    def update(self):
        self.shoot_timer += 1
        if self.shoot_timer >= max(self.shoot_delay, 10):
            self.shoot_timer = 0
            return True  # Ready to shoot
        return False

    def draw(self, surface: pygame.Surface, pos):
        surface.blit(self.image, pos)

        # Draw health bar
        if self.health < PLAYER_MAX_HEALTH:
            bar_height = 5
            hp_ratio = self.health / PLAYER_MAX_HEALTH
            pygame.draw.rect(surface, (0, 0, 0),
                           (pos[0], pos[1] - 8, PLAYER_SIZE, bar_height))
            pygame.draw.rect(surface, GREEN,
                           (pos[0], pos[1] - 8, int(PLAYER_SIZE * hp_ratio), bar_height))

        # Draw shield if active
        if self.shield > 0:
            shield_color = BLUE if self.shield > PLAYER_SHIELD // 2 else CYAN
            pygame.draw.circle(surface, shield_color,
                             (int(pos[0] + PLAYER_SIZE/2), int(pos[1] + PLAYER_SIZE/2)),
                             PLAYER_SIZE // 2 - 2)

        # Draw weapon indicators
        if self.weapons['spread_shot'] > 0:
            pygame.draw.circle(surface, YELLOW, (pos[0], pos[1] - 25), 3)
        if self.weapons['rapid_fire'] > 0:
            pygame.draw.circle(surface, ORANGE, (pos[0] - 15, pos[1] - 25), 3)

        # Draw score
        font = pygame.font.Font(None, 24)
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        surface.blit(score_text, (10, 10))

    def shoot(self, all_sprites: pygame.sprite.Group) -> Optional[Bullet]:
        """Shoot bullet(s)"""
        if self.shoot_timer >= self.shoot_delay:
            self.shoot_timer = 0
            all_sprites.add(Bullet(
                self.rect.centerx, self.rect.centery - 20, is_enemy=False
            ))

            # Rapid fire: shoot multiple bullets
            if self.weapons['rapid_fire'] > 0:
                for i in range(3):
                    angle = i - 1
                    bullet = Bullet(self.rect.centerx, self.rect.centery - 20, is_enemy=False)
                    bullet.velocity_x = math.sin(math.radians(angle * 60)) * 5
                    bullet.velocity_y = -10
                    all_sprites.add(bullet)

            return True

        return False

    def activate_powerup(self, powerup_type: str):
        """Activate a power-up"""
        if powerup_type == 'spread_shot':
            self.weapons['spread_shot'] = 300  # 5 seconds at 60fps
        elif powerup_type == 'rapid_fire':
            self.shoot_delay = 5
            self.weapons['rapid_fire'] = 300
        elif powerup_type == 'shield':
            self.shield = PLAYER_SHIELD
            self.shield_timer = 600  # 10 seconds
        elif powerup_type == 'bomb':
            self.score += 500  # Bomb points


class Explosion(pygame.sprite.Sprite):
    """Explosion effect"""

    def __init__(self, x: float, y: float, size: int = 10):
        super().__init__()
        self.image = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        self.particles = []
        for _ in range(random.randint(8, 15)):
            color = random.choice([RED, ORANGE, YELLOW])
            self.particles.append(Particle(x, y, color, speed=2, size=3))

    def update(self):
        for p in self.particles:
            p.update()
            p.draw(self.image, (self.rect.centerx - 10, self.rect.centery - 10))

        if not self.particles:
            self.kill()


class Boss(pygame.sprite.Sprite):
    """Boss enemy"""

    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((BOSS_SIZE, BOSS_SIZE), pygame.SRCALPHA)
        # Draw boss shape
        pygame.draw.rect(self.image, PURPLE, (0, 0, BOSS_SIZE, BOSS_SIZE))
        pygame.draw.circle(self.image, RED, (BOSS_SIZE // 2, BOSS_SIZE // 2), BOSS_SIZE // 3)
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, -150))
        self.health = 50
        self.max_health = 50
        self.speed = 0.5
        self.points = 5000
        self.bullet_cooldown = 0

    def update(self, player: Player, all_sprites: pygame.sprite.Group):
        self.rect.y += self.speed
        if self.rect.bottom > SCREEN_HEIGHT:
            self.kill()

        # Boss shooting
        if self.bullet_cooldown <= 0:
            # Shoot multiple bullets
            for i in range(3):
                bullet = Bullet(self.rect.centerx + (i-1)*20, self.rect.centery, is_enemy=True)
                all_sprites.add(bullet)
                bullet.velocity_x = random.uniform(-3, 3)
            self.bullet_cooldown = 120

        self.bullet_cooldown -= 1

    def draw(self, surface: pygame.Surface, pos):
        """Draw boss"""
        surface.blit(self.image, pos)
        # Draw health bar
        bar_height = 8
        hp_ratio = self.health / self.max_health
        pygame.draw.rect(surface, (0, 0, 0),
                         (pos[0], pos[1] - 10, BOSS_SIZE, bar_height))
        pygame.draw.rect(surface, (255, 50, 50),
                         (pos[0], pos[1] - 10, int(BOSS_SIZE * hp_ratio), bar_height))


class Game:
    """Main game class"""

    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Space Shooter - Defend the Galaxy!")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        # Game states
        self.state = 'menu'  # menu, playing, game_over

        # Game over settings
        self.game_over = False

    def run(self):
        """Main game loop"""
        while True:
            # Handle events
            for event in pygame.event.get():
                self.handle_event(event)

            # Update and draw
            self.update()
            self.draw()

            # Cap FPS
            self.clock.tick(FPS)

    def draw(self):
        """Draw all sprites"""
        self.screen.fill(BLACK)
        for sprite in self.all_sprites:
            sprite.draw(self.screen, sprite.rect.topleft)
        pygame.display.flip()

    def handle_event(self, event: pygame.event.Event):
        """Handle pygame events"""
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if event.type == pygame.KEYDOWN:
            if self.state == 'menu':
                if event.key == pygame.K_SPACE:
                    self.start_game()
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()

            elif self.state == 'playing':
                if event.key == pygame.K_ESCAPE:
                    self.state = 'menu'
                elif event.key == pygame.K_r and self.game_over:
                    self.start_game()

            elif self.state == 'game_over':
                if event.key == pygame.K_SPACE:
                    self.start_game()
                elif event.key == pygame.K_ESCAPE:
                    self.state = 'menu'

    def start_game(self):
        """Start or restart the game"""
        # Initialize game objects
        self.player = Player()
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.explosions = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()

        # Add player
        self.all_sprites.add(self.player)
        self.bullets.add(self.player)

        # Reset game state
        self.player.health = PLAYER_MAX_HEALTH
        self.player.shield = 0
        self.player.score = 0
        self.player.level = 1
        self.player.weapons = {'spread_shot': 0, 'rapid_fire': 0}

        self.game_over = False
        self.state = 'playing'

    def spawn_enemy(self):
        """Spawn an enemy based on game level"""
        if random.random() < 0.3 + (self.player.level * 0.05):
            # Spawn boss every few levels
            if self.player.level > 0 and random.random() < 0.05:
                self.enemies.add(Boss())
            else:
                # Spawn regular enemy
                enemy_type = random.choice(ENEMY_TYPES)
                enemy = Enemy(enemy_type, x=random.randint(50, SCREEN_WIDTH - 50))
                self.enemies.add(enemy)
                self.all_sprites.add(enemy)

    def update(self):
        """Update game state"""
        if self.state == 'playing' and not self.game_over:
            # Player
            ready_to_shoot = self.player.update()

            # Bullets
            for bullet in self.bullets:
                bullet.draw(self.screen, bullet.rect.topleft)

            # Spawn enemies
            self.spawn_enemy()

            # Powerups
            for powerup in self.powerups:
                powerup.update()
                powerup.draw(self.screen, powerup.rect.topleft)

            # Explosions
            for explosion in self.explosions:
                explosion.update()

            # Enemies
            for enemy in self.enemies:
                enemy.draw(self.screen, enemy.rect.topleft)

            # Check collisions
            self.check_collisions()

            # Check for level up
            if self.player.score >= self.player.level * 1000:
                self.player.level += 1

    def check_collisions(self):
        """Check all collisions"""
        # Player bullets hit enemies
        for bullet in self.bullets:
            # Iterate through all enemies to find collisions
            for enemy in self.enemies:
                if bullet.rect.colliderect(enemy.rect):
                    damage = 1
                    enemy.take_damage(damage)
                    bullet.kill()

                    # Spawn explosion
                    explosion = Explosion(
                        enemy.rect.centerx, enemy.rect.centery,
                        size=enemy.width if enemy.enemy_type != 'basic' else 6
                    )
                    self.explosions.add(explosion)
                    self.all_sprites.add(explosion)

                        # Chance for power-up
                    if random.random() < POWERUP_SPAWN_CHANCE:
                        powerup = PowerUp(
                            enemy.rect.centerx, enemy.rect.centery
                        )
                        self.powerups.add(powerup)
                        self.all_sprites.add(powerup)

                        # Enemy died
                        if enemy.health <= 0:
                            points = enemy.points * (1 + (self.player.level - 1) // 5)
                            self.player.score += points
                            self.player.health = min(
                                PLAYER_MAX_HEALTH, self.player.health + 10
                            )
                            explosion = Explosion(
                                enemy.rect.centerx, enemy.rect.centery,
                                size=enemy.width if enemy.enemy_type == "tank" else 8
                            )
                            self.explosions.add(explosion)
                            self.all_sprites.add(explosion)

                            # Remove from groups
                            if enemy.enemy_type == 'boss':
                                self.game_over = True
                                self.state = 'game_over'

    def draw(self):
        """Draw game elements"""
        self.screen.fill(BLACK)

        if self.state == 'menu':
            self.draw_menu()
        elif self.state == 'game_over':
            self.draw_game_over()

        pygame.display.flip()

    def draw_menu(self):
        """Draw main menu"""
        title = self.font.render("SPACE SHOOTER", True, CYAN)
        self.screen.blit(title, (250, 100))

        instructions = [
            "Controls:",
            "W/S - Move Up/Down",
            "A/D - Rotate Left/Right",
            "Space - Shoot",
            "R - Restart",
            "",
            "Power-ups:",
            "S - Shield",
            "F - Rapid Fire",
            "",
            "Press SPACE to start!",
        ]

        for i, text in enumerate(instructions):
            color = WHITE if i % 2 == 0 else self.grey
            rendered = self.font.render(text, True, color)
            self.screen.blit(rendered, (170, 250 + i * 25))

        # Draw demo player and bullets
        demo_player = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.polygon(demo_player, BLUE, [(0, 40), (20, 5), (40, 40)])
        self.screen.blit(demo_player, (320, 150))

        pygame.draw.line(self.screen, CYAN, (350, 140), (350, 110), 3)
        pygame.draw.line(self.screen, CYAN, (350, 130), (380, 125), 2)

    def draw_game_over(self):
        """Draw game over screen"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        title = self.font.render("GAME OVER", True, RED)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title, title_rect)

        # Show score
        score_text = self.font.render(f"Final Score: {self.player.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 230))
        self.screen.blit(score_text, score_rect)

        # Show level
        level_text = self.font.render(f"Level Reached: {self.player.level}", True, WHITE)
        level_rect = level_text.get_rect(center=(SCREEN_WIDTH // 2, 280))
        self.screen.blit(level_text, level_rect)

        # Instructions
        instructions = [
            "Press SPACE to restart",
            "or ESC for main menu",
        ]

        for i, text in enumerate(instructions):
            rendered = self.font.render(text, True, WHITE)
            rect = rendered.get_rect(center=(SCREEN_WIDTH // 2, 380 + i * 30))
            self.screen.blit(rendered, rect)

    @property
    def grey(self):
        return (100, 100, 100)


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point"""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
