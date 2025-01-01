import pygame
import random
import sys

# Initialize PyGame
pygame.init()

# Constants
TILE_SIZE = 20
CHUNK_SIZE = 16
RENDER_DISTANCE = 3
SCREEN_WIDTH, SCREEN_HEIGHT = TILE_SIZE * CHUNK_SIZE, TILE_SIZE * CHUNK_SIZE
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("2D Infinite Terrain with Steve")

# Colors
GRASS = (34, 139, 34)
DIRT = (139, 69, 19)
STONE = (105, 105, 105)
IRON = (192, 192, 192)
COAL = (54, 54, 54)
FLOWER = (255, 0, 255)
SKY = (135, 206, 235)
PLAYER_SKIN = (255, 220, 177)
PLAYER_SHIRT = (0, 0, 255)
PLAYER_PANTS = (0, 0, 139)

# Physics Constants
GRAVITY = 1
JUMP_STRENGTH = -15
PLAYER_SPEED = 5

# Game Clock
clock = pygame.time.Clock()

# Generate a chunk
def generate_chunk(chunk_x, chunk_y):
    random.seed(f"{chunk_x},{chunk_y}")
    chunk = []
    surface_height = CHUNK_SIZE // 2
    for y in range(CHUNK_SIZE):
        row = []
        for x in range(CHUNK_SIZE):
            if y > surface_height:
                tile = "stone" if random.random() > 0.8 else "dirt"
            elif y == surface_height:
                tile = "grass"
                if random.random() > 0.95:  # Add flowers occasionally
                    tile = "flower"
            else:
                tile = "sky"
            row.append(tile)
        chunk.append(row)

    # Add caves
    if random.random() > 0.7:  # 30% chance of cave in the chunk
        cave_x = random.randint(4, CHUNK_SIZE - 4)
        for y in range(surface_height + 2, CHUNK_SIZE - 2):
            for dx in range(-1, 2):
                if 0 <= cave_x + dx < CHUNK_SIZE:
                    chunk[y][cave_x + dx] = "sky"
            cave_x += random.choice([-1, 0, 1])
            cave_x = max(1, min(CHUNK_SIZE - 2, cave_x))  # Stay within bounds

    # Add resources
    for _ in range(3):  # Iron
        x, y = random.randint(0, CHUNK_SIZE - 1), random.randint(surface_height + 2, CHUNK_SIZE - 1)
        chunk[y][x] = "iron"
    for _ in range(5):  # Coal
        x, y = random.randint(0, CHUNK_SIZE - 1), random.randint(surface_height + 2, CHUNK_SIZE - 1)
        chunk[y][x] = "coal"

    return chunk

# Get ground level at a specific position
def get_ground_level(chunks, player_pos):
    chunk_x, chunk_y = player_pos[0] // CHUNK_SIZE, player_pos[1] // CHUNK_SIZE
    local_x = player_pos[0] % CHUNK_SIZE
    chunk = chunks.get((chunk_x, chunk_y))
    if not chunk:
        return SCREEN_HEIGHT // TILE_SIZE  # Default if chunk not loaded
    for y in range(CHUNK_SIZE):
        if chunk[y][local_x] in ["grass", "dirt", "stone"]:
            return y
    return SCREEN_HEIGHT // TILE_SIZE

# Render the world
def draw_world(chunks, offset_x, offset_y):
    for (chunk_x, chunk_y), chunk in chunks.items():
        for y, row in enumerate(chunk):
            for x, tile in enumerate(row):
                world_x = (chunk_x * CHUNK_SIZE + x - offset_x) * TILE_SIZE
                world_y = (chunk_y * CHUNK_SIZE + y - offset_y) * TILE_SIZE
                if 0 <= world_x < SCREEN_WIDTH and 0 <= world_y < SCREEN_HEIGHT:
                    color = SKY
                    if tile == "grass":
                        color = GRASS
                    elif tile == "dirt":
                        color = DIRT
                    elif tile == "stone":
                        color = STONE
                    elif tile == "iron":
                        color = IRON
                    elif tile == "coal":
                        color = COAL
                    elif tile == "flower":
                        color = FLOWER
                    pygame.draw.rect(screen, color, (world_x, world_y, TILE_SIZE, TILE_SIZE))

# Draw the player (Steve)
def draw_player(player_rect):
    # Head
    head_rect = pygame.Rect(player_rect.x + 4, player_rect.y, 12, 12)
    pygame.draw.rect(screen, PLAYER_SKIN, head_rect)
    # Body
    body_rect = pygame.Rect(player_rect.x + 4, player_rect.y + 12, 12, 16)
    pygame.draw.rect(screen, PLAYER_SHIRT, body_rect)
    # Legs
    leg_rect = pygame.Rect(player_rect.x + 4, player_rect.y + 28, 12, 12)
    pygame.draw.rect(screen, PLAYER_PANTS, leg_rect)

# Main game loop
def main():
    # Player attributes
    player_pos = [CHUNK_SIZE // 2 * TILE_SIZE, CHUNK_SIZE // 2 * TILE_SIZE]
    player_velocity = [0, 0]
    player_rect = pygame.Rect(player_pos[0], player_pos[1], TILE_SIZE, TILE_SIZE * 2)

    # Loaded chunks
    chunks = {}
    current_chunk = [0, 0]

    # Initial terrain generation
    for cx in range(current_chunk[0] - RENDER_DISTANCE, current_chunk[0] + RENDER_DISTANCE + 1):
        for cy in range(current_chunk[1] - RENDER_DISTANCE, current_chunk[1] + RENDER_DISTANCE + 1):
            chunks[(cx, cy)] = generate_chunk(cx, cy)

    # Place player on ground
    ground_y = get_ground_level(chunks, [CHUNK_SIZE // 2, CHUNK_SIZE // 2])
    player_pos[1] = ground_y * TILE_SIZE

    running = True
    while running:
        screen.fill(SKY)

        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player_velocity[1] == 0:  # Jump
                    player_velocity[1] = JUMP_STRENGTH

        # Movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            player_velocity[0] = -PLAYER_SPEED
        elif keys[pygame.K_d]:
            player_velocity[0] = PLAYER_SPEED
        else:
            player_velocity[0] = 0

        # Apply gravity
        player_velocity[1] += GRAVITY
        player_velocity[1] = min(player_velocity[1], 10)  # Terminal velocity

        # Update player position
        player_pos[0] += player_velocity[0]
        player_pos[1] += player_velocity[1]

        # Update chunk position
        new_chunk_x = player_pos[0] // (CHUNK_SIZE * TILE_SIZE)
        new_chunk_y = player_pos[1] // (CHUNK_SIZE * TILE_SIZE)
        if [new_chunk_x, new_chunk_y] != current_chunk:
            current_chunk = [new_chunk_x, new_chunk_y]

        # Load visible chunks
        for cx in range(current_chunk[0] - RENDER_DISTANCE, current_chunk[0] + RENDER_DISTANCE + 1):
            for cy in range(current_chunk[1] - RENDER_DISTANCE, current_chunk[1] + RENDER_DISTANCE + 1):
                if (cx, cy) not in chunks:
                    chunks[(cx, cy)] = generate_chunk(cx, cy)

        # Calculate render offsets
        offset_x = current_chunk[0] * CHUNK_SIZE
        offset_y = current_chunk[1] * CHUNK_SIZE
        draw_world(chunks, offset_x, offset_y)

        # Collision detection with ground
        ground_y = get_ground_level(chunks, [player_pos[0] // TILE_SIZE, player_pos[1] // TILE_SIZE])
        if player_pos[1] > ground_y * TILE_SIZE:
            player_pos[1] = ground_y * TILE_SIZE
            player_velocity[1] = 0

        # Update player rectangle
        player_rect.x, player_rect.y = player_pos[0] - offset_x * TILE_SIZE, player_pos[1] - offset_y * TILE_SIZE

        # Render player
        draw_player(player_rect)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
