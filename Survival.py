import pygame
import random
import sys

# Initialize PyGame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Falling Blocks Survival")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PLAYER_COLOR = (0, 0, 255)
BLOCK_COLOR = (255, 0, 0)

# Game clock
clock = pygame.time.Clock()

# Player settings
player_width, player_height = 50, 10
player_x = WIDTH // 2 - player_width // 2
player_y = HEIGHT - 50
player_speed = 7

# Block settings
blocks = []
block_width, block_height = 40, 40
block_speed = 5
block_spawn_rate = 1000  # Milliseconds between spawns

# Score
score = 0
font = pygame.font.Font(None, 36)

# Timer for block spawn
pygame.time.set_timer(pygame.USEREVENT, block_spawn_rate)

# Main game loop
def main():
    global player_x, score, block_speed

    running = True

    while running:
        screen.fill(WHITE)

        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.USEREVENT:
                spawn_block()

        # Keys
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] and player_x < WIDTH - player_width:
            player_x += player_speed

        # Draw player
        pygame.draw.rect(screen, PLAYER_COLOR, (player_x, player_y, player_width, player_height))

        # Move and draw blocks
        for block in blocks[:]:
            block['y'] += block_speed
            pygame.draw.rect(screen, BLOCK_COLOR, (block['x'], block['y'], block_width, block_height))

            # Check collision
            if (
                player_x < block['x'] + block_width and
                player_x + player_width > block['x'] and
                player_y < block['y'] + block_height and
                player_y + player_height > block['y']
            ):
                running = False  # End game on collision

            # Remove blocks off screen
            if block['y'] > HEIGHT:
                blocks.remove(block)

        # Update score
        score += 1
        score_text = font.render(f"Score: {score // 10}", True, BLACK)
        screen.blit(score_text, (10, 10))

        # Increase difficulty
        if score % 500 == 0:  # Every 500 points, increase speed
            block_speed += 1

        # Update display
        pygame.display.flip()
        clock.tick(60)

    game_over_screen()

# Spawn block
def spawn_block():
    x = random.randint(0, WIDTH - block_width)
    blocks.append({'x': x, 'y': -block_height})

# Game over screen
def game_over_screen():
    screen.fill(WHITE)
    draw_text("Game Over!", WIDTH // 2, HEIGHT // 2 - 50, BLACK, center=True)
    draw_text("Press R to Replay or Q to Quit", WIDTH // 2, HEIGHT // 2 + 50, BLACK, center=True)
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    main()  # Restart the game
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

# Draw text helper
def draw_text(text, x, y, color=BLACK, center=False):
    text_surface = font.render(text, True, color)
    if center:
        rect = text_surface.get_rect(center=(x, y))
        screen.blit(text_surface, rect)
    else:
        screen.blit(text_surface, (x, y))

if __name__ == "__main__":
    main()
