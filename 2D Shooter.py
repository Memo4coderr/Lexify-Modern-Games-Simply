import pygame
import random
import math
import sys

# Initialize PyGame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Top-Down Shooter with Waves")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PLAYER_COLOR = (0, 0, 255)
ENEMY_COLOR = (255, 0, 0)
BULLET_COLOR = (0, 255, 0)
BOSS_COLOR = (255, 165, 0)

# Game clock
clock = pygame.time.Clock()

# Player settings
player_size = 40
player_x, player_y = WIDTH // 2, HEIGHT // 2
player_speed = 5

# Bullet settings
bullets = []
bullet_speed = 10

# Enemy settings
enemies = []
enemy_speed = 2

# Boss settings
boss = None
boss_health = 0
boss_speed = 1

# Wave settings
wave = 1
wave_active = True
enemies_remaining = 0

# Score
score = 0
font = pygame.font.Font(None, 36)

# Spawn enemy
def spawn_enemy():
    side = random.choice(["top", "bottom", "left", "right"])
    if side == "top":
        x = random.randint(0, WIDTH)
        y = 0
    elif side == "bottom":
        x = random.randint(0, WIDTH)
        y = HEIGHT
    elif side == "left":
        x = 0
        y = random.randint(0, HEIGHT)
    else:  # "right"
        x = WIDTH
        y = random.randint(0, HEIGHT)
    enemies.append({'x': x, 'y': y})

# Spawn boss
def spawn_boss():
    global boss, boss_health
    boss = {'x': WIDTH // 2, 'y': HEIGHT // 4}
    boss_health = 10 + wave * 5  # Boss gets more health as waves progress

# Display text
def draw_text(text, x, y, color=BLACK, center=False):
    text_surface = font.render(text, True, color)
    if center:
        rect = text_surface.get_rect(center=(x, y))
        screen.blit(text_surface, rect)
    else:
        screen.blit(text_surface, (x, y))

# Endgame screen
def endgame_screen():
    screen.fill(WHITE)
    draw_text("YOU WON!", WIDTH // 2, HEIGHT // 2 - 50, BLACK, center=True)
    draw_text("Press R to Replay or Q to Quit", WIDTH // 2, HEIGHT // 2 + 50, BLACK, center=True)
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True  # Replay
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
        clock.tick(60)

# Main game loop
def main():
    global wave, wave_active, enemies_remaining, boss, boss_health, score

    running = True
    player_rect = pygame.Rect(player_x, player_y, player_size, player_size)

    while running:
        screen.fill(WHITE)

        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if wave_active and len(enemies) < enemies_remaining:
                spawn_enemy()

        # Player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            player_rect.y -= player_speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            player_rect.y += player_speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            player_rect.x -= player_speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            player_rect.x += player_speed

        # Bullet shooting
        if keys[pygame.K_SPACE]:
            if len(bullets) < 10:  # Limit bullets on screen
                mouse_x, mouse_y = pygame.mouse.get_pos()
                dx, dy = mouse_x - player_rect.centerx, mouse_y - player_rect.centery
                distance = math.sqrt(dx**2 + dy**2)
                bullets.append({
                    'x': player_rect.centerx,
                    'y': player_rect.centery,
                    'dx': dx / distance,
                    'dy': dy / distance
                })

        # Draw player
        pygame.draw.rect(screen, PLAYER_COLOR, player_rect)

        # Move and draw bullets
        for bullet in bullets[:]:
            bullet['x'] += bullet['dx'] * bullet_speed
            bullet['y'] += bullet['dy'] * bullet_speed
            pygame.draw.circle(screen, BULLET_COLOR, (int(bullet['x']), int(bullet['y'])), 5)

            # Remove bullets off screen
            if bullet['x'] < 0 or bullet['x'] > WIDTH or bullet['y'] < 0 or bullet['y'] > HEIGHT:
                bullets.remove(bullet)

        # Move and draw enemies
        for enemy in enemies[:]:
            dx, dy = player_rect.centerx - enemy['x'], player_rect.centery - enemy['y']
            distance = math.sqrt(dx**2 + dy**2)
            enemy['x'] += dx / distance * enemy_speed
            enemy['y'] += dy / distance * enemy_speed
            pygame.draw.circle(screen, ENEMY_COLOR, (int(enemy['x']), int(enemy['y'])), 20)

            # Check collision with player
            if player_rect.collidepoint(enemy['x'], enemy['y']):
                running = False  # End game

            # Check collision with bullets
            for bullet in bullets[:]:
                if math.hypot(bullet['x'] - enemy['x'], bullet['y'] - enemy['y']) < 20:
                    enemies.remove(enemy)
                    bullets.remove(bullet)
                    score += 1
                    break

        # Boss logic
        if boss:
            dx, dy = player_rect.centerx - boss['x'], player_rect.centery - boss['y']
            distance = math.sqrt(dx**2 + dy**2)
            boss['x'] += dx / distance * boss_speed
            boss['y'] += dy / distance * boss_speed
            pygame.draw.circle(screen, BOSS_COLOR, (int(boss['x']), int(boss['y'])), 40)

            # Check collision with bullets
            for bullet in bullets[:]:
                if math.hypot(bullet['x'] - boss['x'], bullet['y'] - boss['y']) < 40:
                    bullets.remove(bullet)
                    boss_health -= 1
                    if boss_health <= 0:
                        boss = None
                        wave += 1
                        if wave > 10:
                            if endgame_screen():
                                main()
                            else:
                                pygame.quit()
                                sys.exit()
                        wave_active = True
                        enemies_remaining = wave * 5

        # Display score and wave
        draw_text(f"Score: {score}", 10, 10)
        draw_text(f"Wave: {wave}", 10, 40)

        # Check if wave is complete
        if wave_active and not enemies and not boss:
            wave_active = False
            spawn_boss()

        # Update display
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    wave = 1
    wave_active = True
    enemies_remaining = wave * 5
    main()
