import socket
import pygame

# Set up the client
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("server_address", 12345))  # Connect to the server (replace with actual server IP)

# Initialize Pygame
pygame.init()

# Screen setup
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Online Multiplayer Game")

# Player variables
player_x, player_y = 100, 100
player_color = (255, 0, 0)  # Red for player

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Handle movement with keys (WASD)
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        player_y -= 5
    if keys[pygame.K_s]:
        player_y += 5
    if keys[pygame.K_a]:
        player_x -= 5
    if keys[pygame.K_d]:
        player_x += 5

    # Send player position to server
    message = f"PLAYER_POS {player_x} {player_y}"
    client.send(message.encode('utf-8'))

    # Receive the game state from the server (positions of all players)
    try:
        server_message = client.recv(1024).decode('utf-8')
        players_data = server_message.split()[1:]

        # Handle the positions of other players
        players = {}
        for i in range(0, len(players_data), 3):
            addr = players_data[i]
            x, y = int(players_data[i + 1]), int(players_data[i + 2])
            players[addr] = (x, y)

        # Drawing (clear the screen)
        screen.fill((0, 0, 0))  # Clear the screen

        # Draw the player (Red)
        pygame.draw.rect(screen, player_color, (player_x, player_y, 50, 50))

        # Draw other players (Blue)
        for addr, pos in players.items():
            if addr != str(client.getsockname()):
                pygame.draw.rect(screen, (0, 0, 255), (pos[0], pos[1], 50, 50))  # Blue for other players

        # Update the display
        pygame.display.flip()
    except Exception as e:
        print(f"Error receiving data: {e}")
        break

# Quit Pygame and close the connection
pygame.quit()
client.close()
