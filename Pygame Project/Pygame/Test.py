import pygame
import math

# Initialize Pygame
pygame.init()

# Set up the screen
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Zombie Facing Player Example")

# Load player image
player_image = pygame.image.load("Pygame/Assets/Character/MC.png").convert_alpha()
player_image = pygame.transform.scale(player_image, (64, 64))
player_rect = player_image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

# Load zombie image
zombie_image = pygame.image.load("Pygame/Assets/Character/Normal Zombie One.png").convert_alpha()
zombie_image = pygame.transform.scale(zombie_image, (64, 64))


# Function to rotate the zombie image to face the player
def rotate_to_player(zombie_pos, player_pos):
    # Calculate the difference in coordinates
    dx = player_pos[0] - zombie_pos[0]
    dy = player_pos[1] - zombie_pos[1]

    # Calculate the angle to the player (in radians)
    angle = math.atan2(dy, dx)

    # Rotate the zombie image by the calculated angle (in degrees)
    rotated_zombie = pygame.transform.rotate(zombie_image, -math.degrees(angle))

    # Get the new rect for the rotated image and position it
    new_rect = rotated_zombie.get_rect(center=zombie_pos)

    return rotated_zombie, new_rect


# Main game loop
running = True
zombie_pos = (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 4)  # Initial zombie position

while running:
    screen.fill((0, 0, 0))  # Fill the screen with black

    # Get the player position (we can move it with the mouse here)
    mouse_x, mouse_y = pygame.mouse.get_pos()
    player_rect.center = (mouse_x, mouse_y)

    # Rotate the zombie to face the player
    rotated_zombie, zombie_rect = rotate_to_player(zombie_pos, player_rect.center)

    # Draw the player and zombie
    screen.blit(player_image, player_rect)
    screen.blit(rotated_zombie, zombie_rect)

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update the screen
    pygame.display.flip()

# Quit Pygame
pygame.quit()