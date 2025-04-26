import pygame, sys
from sys import exit
import math
from settings import *
from button import Button
import random
import os

preliminary_dir = dir_path = os.path.dirname(os.path.realpath(__file__))

pygame.init()

pygame.display.set_caption("Lockdown Zombie Simulator")
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
BG = pygame.transform.scale(pygame.image.load(preliminary_dir + "/Assets/Background/Background.png"), (1540, 810))

WIDTH, HEIGHT = screen.get_size()

def get_font(size):
    return pygame.font.Font(preliminary_dir + "/Assets/Fonts/font.ttf", size)

def play():
    shop_menu_open = False
    pygame.font.init()

    tilesX = math.ceil(WIDTH / 512)
    tilesY = math.ceil(HEIGHT / 288)

    background = pygame.image.load(preliminary_dir + "/Assets/Background/pixel_art_floor_board.jpg").convert()


    zombie_img = pygame.image.load(
        preliminary_dir + "/Assets/Character/Normal Zombie One.png").convert_alpha()
    zombie_img = pygame.transform.scale(zombie_img, (64, 64))
    zombie_img_2 = pygame.image.load(
        preliminary_dir + "/Assets/Character/Knight Zombie One.png").convert_alpha()
    zombie_img_2 = pygame.transform.scale(zombie_img_2, (64, 64))
    zombie_img_3 = pygame.image.load(
        preliminary_dir + "/Assets/Character/Gang Gang Zombie One.png").convert_alpha()
    zombie_img_3 = pygame.transform.scale(zombie_img_3, (64, 64))
    zombie_img_4 = pygame.image.load(
        preliminary_dir + "/Assets/Character/Boss One.png").convert_alpha()
    zombie_img_4 = pygame.transform.scale(zombie_img_4, (120, 120))


    # Setup
    zombies = []
    bullets = []
    coins = []

    zombie_spawn_cooldown = 5000  # 5 seconds between waves
    last_wave_time = 0
    base_zombie_speed = 2
    zombies_per_wave = 3
    wave_number = 0

    spawn_queue = []
    last_spawn_tick = 0
    spawn_delay = 800  # milliseconds between each zombie spawn

    # Player setup
    player_x, player_y = 400, 300
    player_speed = 5
    player_health = 100000
    player_coins = 0

    # Bullet setup
    bullet_speed = 10
    shoot_cooldown = 250  # milliseconds
    last_shot_time = 0

    # Font setup
    font = pygame.font.SysFont('simsun', 36)
    big_font = pygame.font.SysFont('simsun', 72)

    # Game state
    running = True
    game_over = False
    boss_message_timer = -3301

    # Define zombie types
    zombie_types = {
        "normal": {"hp": 2, "speed": 1.5, "color": (100, 255, 100)},
        "knight": {"hp": 3, "speed": 1.2, "color": (100, 100, 255)},
        "gang": {"hp": 1, "speed": 10, "color": (255, 100, 100)},
        "boss": {"hp": 20, "speed": 1.5, "color": (255, 255, 0)},
    }

    # Game loop
    while running:
        now = pygame.time.get_ticks()

        events = pygame.event.get()


        keys = pygame.key.get_pressed()

        if not game_over and not shop_menu_open:
            # Player movement
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                player_x -= player_speed
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                player_x += player_speed
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                player_y -= player_speed
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                player_y += player_speed

            for event in events:
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
                        bullets.append({"x": player_x + 64, "y": player_y + 32, "dx": dx, "dy": dy})
                        last_shot_time = now

            # Start new wave
            if now - last_wave_time > zombie_spawn_cooldown and not spawn_queue:
                for _ in range(zombies_per_wave):
                    spawn_queue.append(random.choice(["normal", "knight", "gang"]))
                if wave_number % 5 == 0 and wave_number != 0:
                    spawn_queue.append("boss")
                    boss_message_timer = now  # show boss message
                last_wave_time = now
                zombies_per_wave += 1
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
            bullets = [b for b in bullets if -1000 <= b["x"] <= 3000 and -1000 <= b["y"] <= 3000]

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
                if zombie['type'] == 'boss':
                    zombie_rect = pygame.Rect(zombie["x"], zombie["y"], 128, 128)
                else:
                    zombie_rect = pygame.Rect(zombie["x"], zombie["y"], 64, 64)
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
                player_rect = pygame.Rect(player_x-25, player_y-25, 64, 64)
                if zombie_rect.colliderect(player_rect):
                    if not zombie["first_hit"]:
                        if zombie["first_contact_time"] == 0:
                            zombie["first_contact_time"] = now
                        elif now - zombie["first_contact_time"] > 150:  # 0.5 sec delay
                            if zombie['type'] == 'normal':
                                player_health -= 3
                            elif zombie['type'] == 'knight':
                                player_health -= 7
                            elif zombie['type'] == 'gang':
                                player_health -= 7
                            elif zombie['type'] == 'boss':
                                player_health -= 15
                            zombie["last_attack"] = now
                            zombie["first_hit"] = True
                            if player_health <= 0:
                                player_health = 0
                                game_over = True
                    else:
                        if now - zombie["last_attack"] > 1000:  # 1 sec attack rate
                            if zombie['type'] == 'normal':
                                player_health -= 3
                            elif zombie['type'] == 'knight':
                                player_health -= 7
                            elif zombie['type'] == 'gang':
                                player_health -= 7
                            elif zombie['type'] == 'boss':
                                player_health -= 15
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
            player_rect = pygame.Rect(player_x, player_y + 25, 64,64)
            coins_to_remove = []
            for i, coin in enumerate(coins):
                coin_rect = pygame.Rect(coin["x"] - 5, coin["y"] - 5, 15, 15)
                if player_rect.colliderect(coin_rect):
                    player_coins += 1
                    coins_to_remove.append(i)

            for index in sorted(coins_to_remove, reverse=True):
                coins.pop(index)

        # Drawing
        for x in range(tilesX):
            for y in range(tilesY):
                screen.blit(background, (x * 512, y * 288))

        # Draw zombies
        for zombie in zombies:
            if zombie['type'] == 'normal':
                screen.blit(zombie_img, (zombie["x"], zombie["y"]))
            elif zombie['type'] == 'knight':
                screen.blit(zombie_img_2, (zombie["x"], zombie["y"]))
            elif zombie["type"] == 'gang':
                screen.blit(zombie_img_3, (zombie["x"], zombie["y"]))
            elif zombie["type"] == 'boss':
                screen.blit(zombie_img_4, (zombie["x"], zombie["y"]))
            hp_ratio = zombie["hp"] / zombie_types[zombie["type"]]["hp"]
            if zombie['type'] == 'boss':
                health_bar_width = 128
                pygame.draw.rect(screen, (255, 0, 0),
                                 (zombie["x"] + (70 - health_bar_width / 2), zombie["y"] - 10, health_bar_width, 5))
                pygame.draw.rect(screen, (0, 255, 0), (
                    zombie["x"] + (70 - health_bar_width / 2), zombie["y"] - 10, health_bar_width * hp_ratio, 5))
            else:
                health_bar_width = 64
                pygame.draw.rect(screen, (255, 0, 0),
                                 (zombie["x"] + (34 - health_bar_width / 2), zombie["y"] - 10, health_bar_width, 5))
                pygame.draw.rect(screen, (0, 255, 0), (
                    zombie["x"] + (34 - health_bar_width / 2), zombie["y"] - 10, health_bar_width * hp_ratio, 5))



        # Draw bullets
        for bullet in bullets:
            pygame.draw.circle(screen, (0, 0, 0), (int(bullet["x"]), int(bullet["y"])), 7)

        # Draw coins
        for coin in coins:
            pygame.draw.circle(screen, (255, 215, 0), (int(coin["x"]), int(coin["y"])), 6)

        # Draw player
        player_image = pygame.image.load(
            preliminary_dir + "/Assets/Character/MC.png").convert_alpha()
        player_image_2 = pygame.transform.scale(player_image, (80, 80))
        screen.blit(player_image_2, (player_x, player_y))

        # # Draw aiming line
        # if not game_over:
        #     mouse_x, mouse_y = pygame.mouse.get_pos()
        #     pygame.draw.line(screen, (255,255,255), (player_x+64, player_y+32), (mouse_x, mouse_y), 4)

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
                wave_number = 0
                zombies_per_wave = 3
                base_zombie_speed = 2
                spawn_queue.clear()
                last_wave_time = now
                game_over = False

        shop_button = Button(
            image=None,
            pos=(WIDTH - 80, HEIGHT - 50),  # Bottom right corner
            text_input="Shop",
            font=font,  # Use the font you already created
            base_color=(0, 0, 0),  # Black color
            hovering_color=(100, 100, 100)  # Gray when hovering
        )

        pygame.draw.rect(screen, (200, 200, 200), (WIDTH-120, HEIGHT-70, 80, 40))

        mouse_pos = pygame.mouse.get_pos()

        shop_button.changeColor(mouse_pos)

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if shop_button.checkForInput(mouse_pos):
                    shop_menu_open = not shop_menu_open

        shop_button.changeColor(pygame.mouse.get_pos())
        shop_button.update(screen)
        if shop_menu_open:
            pygame.draw.rect(screen, (200, 200, 200), (WIDTH // 2 - 500, HEIGHT // 2 - 250, 1000, 600))

            menu_text = font.render("Shop Menu", True, (0, 0, 0))
            screen.blit(menu_text, (WIDTH // 2 - menu_text.get_width() // 2, HEIGHT // 2 - 200))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()



def main_menu():
    while True:
        screen.blit(BG, (0, 0))

        MENU_MOUSE_POS = pygame.mouse.get_pos()

        MENU_TEXT = get_font(100).render("Zombie Slayer", True, "#781A05")
        MENU_RECT = MENU_TEXT.get_rect(center=(770, 100))

        PLAY_BUTTON = Button(image=pygame.image.load(preliminary_dir + "/Assets/Buttons/Play Rect.png"), pos=(770, 300),
                             text_input="PLAY", font=get_font(75), base_color="#781A05", hovering_color="White")
        QUIT_BUTTON = Button(image=pygame.image.load(preliminary_dir + "/Assets/Buttons/Quit Rect.png"), pos=(770, 600),
                             text_input="QUIT", font=get_font(75), base_color="#781A05", hovering_color="White")

        screen.blit(MENU_TEXT, MENU_RECT)

        for button in [PLAY_BUTTON, QUIT_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    play()
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()

main_menu()


