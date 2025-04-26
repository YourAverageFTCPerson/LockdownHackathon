import pygame
import math
import random

pygame.init()

# Window setup
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

# Load zombie sprite
zombie_img = pygame.image.load(r"C:\Users\shujianzhai\.vscode\Codes\Scrapyardprojects\Arts\zombie 1.png").convert_alpha()
zombie_img = pygame.transform.scale(zombie_img, (32, 32))

# Setup
zombies = []
bullets = []
coins = []

zombie_spawn_cooldown = 5000  # 5 seconds between waves
last_wave_time = 0
base_zombie_speed = 3
zombies_per_wave = 3
wave_number = 0

spawn_queue = []
last_spawn_tick = 0
spawn_delay = 800  # milliseconds between each zombie spawn

# Player setup
player_x, player_y = 400, 300
player_speed = 5
player_health = 100
player_coins = 0

# Bullet setup
bullet_speed = 10
shoot_cooldown = 250 
last_shot_time = 0

# Font setup
font = pygame.font.SysFont(None, 36)
big_font = pygame.font.SysFont(None, 72)

# Game state
running = True
game_over = False
boss_message_timer = 0

# Define zombie types
zombie_types = {
    "normal": {"hp": 2, "speed": 2, "color": (100, 255, 100)},
    "knight": {"hp": 3, "speed": 2, "color": (100, 100, 255)},
    "gang": {"hp": 1, "speed": 10, "color": (255, 100, 100)},
    "boss": {"hp": 20, "speed": 0.6, "color": (255, 255, 0)},
}

# Game loop
while running:
    now = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
            if now - last_shot_time > shoot_cooldown:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                dx = mouse_x - player_x
                dy = mouse_y - player_y
                distance = math.hypot(dx, dy)
                if distance != 0:
                    dx /= distance
                    dy /= distance
                bullets.append({"x": player_x, "y": player_y, "dx": dx, "dy": dy})
                last_shot_time = now

    keys = pygame.key.get_pressed()

    if not game_over:
        # Player movement
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player_x += player_speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            player_y -= player_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            player_y += player_speed

        # Start new wave
        if now - last_wave_time > zombie_spawn_cooldown and not spawn_queue:
            for _ in range(zombies_per_wave):
                spawn_queue.append(random.choice(["normal", "knight", "gang"]))
            if wave_number % 5 == 0:
                spawn_queue.append("boss")
                boss_message_timer = now  # show boss message
            last_wave_time = now
            zombies_per_wave += 3
            base_zombie_speed += 0.05
            wave_number += 1

        # Spawn zombies one by one
        if spawn_queue and now - last_spawn_tick > spawn_delay:
            spawn_type = spawn_queue.pop(0)
            x = random.choice([random.randint(-100, -40), random.randint(800, 840)])
            y = random.choice([random.randint(-100, -40), random.randint(600, 640)])
            zombies.append({
                "x": x, "y": y,
                "type": spawn_type,
                "hp": zombie_types[spawn_type]["hp"],
                "speed": zombie_types[spawn_type]["speed"],
                "last_attack": 0,
                "first_contact_time": 0,
                "first_hit": False
            })
            last_spawn_tick = now

        # Update bullets
        for bullet in bullets:
            bullet["x"] += bullet["dx"] * bullet_speed
            bullet["y"] += bullet["dy"] * bullet_speed

        # Remove off-screen bullets
        bullets = [b for b in bullets if 0 <= b["x"] <= 800 and 0 <= b["y"] <= 600]

        for zombie in zombies:
            dx = player_x - zombie["x"]
            dy = player_y - zombie["y"]
            distance = math.hypot(dx, dy)

            if distance > 20:  # If not too close, keep moving
                if distance != 0:
                    dx /= distance
                    dy /= distance
                zombie["x"] += dx * zombie["speed"]
                zombie["y"] += dy * zombie["speed"]
            else:
            # If very close, stop moving into the player
                pass 

        # Handle bullet-zombie collisions
        bullets_to_remove = []
        zombies_to_remove = []

        for i, zombie in enumerate(zombies):
            zombie_rect = pygame.Rect(zombie["x"], zombie["y"], 32, 32)
            for j, bullet in enumerate(bullets):
                bullet_rect = pygame.Rect(bullet["x"] - 5, bullet["y"] - 5, 10, 10)
                if zombie_rect.colliderect(bullet_rect):
                    zombie["hp"] -= 1
                    bullets_to_remove.append(j)
                    if zombie["hp"] <= 0:
                        zombies_to_remove.append(i)
                        coins.append({"x": zombie["x"] + 16, "y": zombie["y"] + 16})
                    break

        # Handle zombie-player collisions
        for i, zombie in enumerate(zombies):
            zombie_rect = pygame.Rect(zombie["x"], zombie["y"], 32, 32)
            player_rect = pygame.Rect(player_x - 15, player_y - 15, 30, 30)
            if zombie_rect.colliderect(player_rect):
                if not zombie["first_hit"]:
                    if zombie["first_contact_time"] == 0:
                        zombie["first_contact_time"] = now
                    elif now - zombie["first_contact_time"] > 200:  # 0.5 sec delay
                        player_health -= 5
                        zombie["last_attack"] = now
                        zombie["first_hit"] = True
                        if player_health <= 0:
                            player_health = 0
                            game_over = True
                else:
                    if now - zombie["last_attack"] > 1000:  # 1 sec attack rate
                        player_health -= 5
                        zombie["last_attack"] = now
                        if player_health <= 0:
                            player_health = 0
                            game_over = True
            else:
                zombie["first_hit"] = False
                zombie["first_contact_time"] = 0

        # Remove dead zombies and bullets
        for index in sorted(zombies_to_remove, reverse=True):
            if index < len(zombies):
                zombies.pop(index)
        for index in sorted(bullets_to_remove, reverse=True):
            if index < len(bullets):
                bullets.pop(index)

        # Collect coins
        player_rect = pygame.Rect(player_x - 15, player_y - 15, 30, 30)
        coins_to_remove = []
        for i, coin in enumerate(coins):
            coin_rect = pygame.Rect(coin["x"] - 5, coin["y"] - 5, 10, 10)
            if player_rect.colliderect(coin_rect):
                player_coins += 1
                coins_to_remove.append(i)

        for index in sorted(coins_to_remove, reverse=True):
            coins.pop(index)

    # Drawing
    screen.fill((30, 30, 30))

    # Draw zombies
    for zombie in zombies:
        screen.blit(zombie_img, (zombie["x"], zombie["y"]))
        hp_ratio = zombie["hp"] / zombie_types[zombie["type"]]["hp"]
        pygame.draw.rect(screen, (255, 0, 0), (zombie["x"], zombie["y"] - 10, 32, 5))
        pygame.draw.rect(screen, (0, 255, 0), (zombie["x"], zombie["y"] - 10, 32 * hp_ratio, 5))

    # Draw bullets
    for bullet in bullets:
        pygame.draw.circle(screen, (0, 255, 255), (int(bullet["x"]), int(bullet["y"])), 5)

    # Draw coins
    for coin in coins:
        pygame.draw.circle(screen, (255, 215, 0), (int(coin["x"]), int(coin["y"])), 6)

    # Draw player
    pygame.draw.circle(screen, (255, 0, 0), (player_x, player_y), 15)

    # Draw aiming line
    if not game_over:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        pygame.draw.line(screen, (255, 255, 0), (player_x, player_y), (mouse_x, mouse_y), 2)

    # Draw HUD
    health_text = font.render(f"Health: {player_health}", True, (255, 255, 255))
    wave_text = font.render(f"Wave: {wave_number}", True, (255, 255, 0))
    coins_text = font.render(f"Coins: {player_coins}", True, (255, 215, 0))
    screen.blit(health_text, (10, 10))
    screen.blit(wave_text, (10, 50))
    screen.blit(coins_text, (10, 90))

    # Boss announcement
    if now - boss_message_timer < 3000:  # Show for 3 seconds
        boss_text = big_font.render("⚠️ BOSS APPROACHING ⚠️", True, (255, 0, 0))
        screen.blit(boss_text, (screen.get_width() // 2 - boss_text.get_width() // 2, 200))

    # Game over screen
    if game_over:
        over_text = big_font.render("GAME OVER", True, (255, 0, 0))
        restart_text = font.render("Press R to Restart", True, (255, 255, 255))

        screen.blit(over_text, (screen.get_width() // 2 - over_text.get_width() // 2, 200))
        screen.blit(restart_text, (screen.get_width() // 2 - restart_text.get_width() // 2, 280))

        if keys[pygame.K_r]:
            zombies.clear()
            bullets.clear()
            coins.clear()
            player_x, player_y = 400, 300
            player_health = 100
            player_coins = 0
            wave_number = 1
            zombies_per_wave = 3
            base_zombie_speed = 1.2
            spawn_queue.clear()
            last_wave_time = now
            game_over = False

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
