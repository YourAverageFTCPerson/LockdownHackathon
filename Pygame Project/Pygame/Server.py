import socket
import threading

# Set up the server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("0.0.0.0", 32653))  # Listen on all interfaces, port 12345
server.listen(5)
print("Server is listening...")

clients = []

# Store player positions
player_positions = {}

# Handle each client's connection
def handle_client(client_socket, client_addr):
    global player_positions
    player_positions[client_addr] = (100, 100)  # Default position for new players

    while True:
        try:
            msg = client_socket.recv(1024)
            if not msg:
                break

            # Handle client messages (for now, just player movement)
            message = msg.decode("utf-8")
            if message.startswith("PLAYER_POS"):
                _, x, y = message.split()
                player_positions[client_addr] = (int(x), int(y))  # Update position

            # Broadcast the updated game state to all clients
            broadcast_game_state()

        except Exception as e:
            print(f"Error with client {client_addr}: {e}")
            break

    # Remove client from list and clean up
    del player_positions[client_addr]
    clients.remove(client_socket)
    client_socket.close()

# Broadcast the updated game state (positions of all players)
def broadcast_game_state():
    for client in clients:
        try:
            state_message = "PLAYER_STATE " + " ".join([f"{addr} {pos[0]} {pos[1]}" for addr, pos in player_positions.items()])
            client.send(state_message.encode("utf-8"))
        except Exception as e:
            print(f"Error sending to client: {e}")

# Accept incoming connections
while True:
    client_socket, addr = server.accept()
    print(f"Connection from {addr}")
    clients.append(client_socket)
    threading.Thread(target=handle_client, args=(client_socket, addr)).start()
