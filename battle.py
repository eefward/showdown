# (same imports & init)
import pygame
import random

pygame.init()
WIDTH, HEIGHT = 960, 640
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pokémon Showdown - Battle UI")

font = pygame.font.SysFont("arial", 20)
log_font = pygame.font.SysFont("consolas", 16)

# Colors
PLAYER_COLOR = (150, 200, 250)
ENEMY_COLOR = (250, 150, 150)
BUTTON_COLOR = (220, 220, 220)
BUTTON_BORDER = (50, 50, 50)
BG_COLOR = (230, 240, 255)
ACTIVE_HIGHLIGHT = (255, 255, 100)

# Classes
class Move:
    def __init__(self, name, power):
        self.name = name
        self.power = power

class Pokemon:
    def __init__(self, name, max_hp, moves, color):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.moves = moves
        self.color = color

    def is_fainted(self):
        return self.hp <= 0

    def take_damage(self, dmg):
        self.hp = max(0, self.hp - dmg)

    def heal(self, amount):
        self.hp = min(self.max_hp, self.hp + amount)

def flash_sprite(x, y, w=120, h=120, color=(255, 255, 255), times=3, delay=100):
    for _ in range(times):
        pygame.draw.rect(screen, color, (x, y, w, h))
        pygame.display.flip()
        pygame.time.delay(delay)
        draw_battle()
        pygame.time.delay(delay)

def bounce_sprite(x, y, color, times=3, dx=5, delay=50):
    for _ in range(times):
        pygame.draw.rect(screen, BG_COLOR, (x, y - dx, 120, 120))
        pygame.draw.rect(screen, color, (x, y - dx, 120, 120))
        pygame.display.flip()
        pygame.time.delay(delay)
        draw_battle()
        pygame.time.delay(delay)

def heal_animation(pokemon_rect):
    for alpha in range(0, 150, 30):
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        s.fill((0, 255, 0, alpha))
        screen.blit(s, pokemon_rect)
        pygame.display.flip()
        pygame.time.delay(50)
        draw_battle()

def switch_animation_out(x, y, color):
    for i in range(12):
        pygame.draw.rect(screen, BG_COLOR, (x - i*10, y, 120, 120))
        pygame.draw.rect(screen, color, (x - i*10, y, 120, 120))
        pygame.display.flip()
        pygame.time.delay(30)

def switch_animation_in(x, y, color):
    for i in reversed(range(12)):
        pygame.draw.rect(screen, BG_COLOR, (x - i*10, y, 120, 120))
        pygame.draw.rect(screen, color, (x - i*10, y, 120, 120))
        pygame.display.flip()
        pygame.time.delay(30)

def attack_animation(x, y, color):
    # Simple attack flash effect (same for player and opponent)
    for _ in range(5):
        pygame.draw.circle(screen, color, (x + 60, y + 60), 50)
        pygame.display.update()
        pygame.time.delay(100)
        pygame.draw.circle(screen, BG_COLOR, (x + 60, y + 60), 50)
        pygame.display.update()
        pygame.time.delay(100)


def faint_animation(x, y, color):
    # Faint animation (Pokemon slowly fades out)
    for i in range(255, 0, -5):  # Fade out effect
        pygame.draw.rect(screen, (i, i, i), (x, y, 120, 120))
        pygame.display.update()
        pygame.time.delay(50)
    pygame.draw.rect(screen, BG_COLOR, (x, y, 120, 120))  # Make it disappear
    pygame.display.update()


def opponent_attack_animation(x, y, target):
    # Opponent attacking animation (same as the player's attack)
    attack_animation(x, y, target.color)

def opponent_bounce_animation(x, y, target):
    # Opponent bouncing animation
    bounce_sprite(x, y, target.color)


# Helper
# Define all moves
FLAMETHROWER = Move("Flamethrower", 30)
FIRE_SPIN = Move("Fire Spin", 20)
ROAR = Move("Roar", 10)
SLASH = Move("Slash", 25)

WATER_GUN = Move("Water Gun", 25)
TACKLE = Move("Tackle", 20)
BITE = Move("Bite", 22)
HYDRO_PUMP = Move("Hydro Pump", 35)

VINE_WHIP = Move("Vine Whip", 28)
LEECH_SEED = Move("Leech Seed", 10)
RAZOR_LEAF = Move("Razor Leaf", 30)
HEADBUTT = Move("Headbutt", 22)

THUNDERBOLT = Move("Thunderbolt", 35)
QUICK_ATTACK = Move("Quick Attack", 20)
SPARK = Move("Spark", 25)
THUNDER = Move("Thunder", 40)

PSYCHIC = Move("Psychic", 35)
CONFUSION = Move("Confusion", 25)
PSYBEAM = Move("Psybeam", 30)
RECOVER = Move("Recover", 0)


# Teams
# Player's team (manually assigned moves)
team1 = [
    Pokemon("Charizard", 120, [FLAMETHROWER, FIRE_SPIN, ROAR, SLASH], PLAYER_COLOR),
    Pokemon("Blastoise", 130, [WATER_GUN, HYDRO_PUMP, BITE, TACKLE], PLAYER_COLOR),
    Pokemon("Venusaur", 125, [VINE_WHIP, LEECH_SEED, RAZOR_LEAF, HEADBUTT], PLAYER_COLOR),
    Pokemon("Pikachu", 90, [THUNDERBOLT, SPARK, QUICK_ATTACK, THUNDER], PLAYER_COLOR),
    Pokemon("Alakazam", 100, [PSYCHIC, PSYBEAM, CONFUSION, RECOVER], PLAYER_COLOR),
    Pokemon("Machamp", 130, [HEADBUTT, SLASH, TACKLE, ROAR], PLAYER_COLOR)
]

# Enemy team (random for now — you can customize these too!)
team2 = [
    Pokemon("Gyarados", 140, [BITE, WATER_GUN, HYDRO_PUMP, ROAR], ENEMY_COLOR),
    Pokemon("Arcanine", 125, [FIRE_SPIN, SLASH, TACKLE, FLAMETHROWER], ENEMY_COLOR),
    Pokemon("Rhydon", 135, [HEADBUTT, ROAR, SLASH, TACKLE], ENEMY_COLOR),
    Pokemon("Gengar", 110, [CONFUSION, PSYBEAM, BITE, RECOVER], ENEMY_COLOR),
    Pokemon("Dragonite", 150, [THUNDER, ROAR, HEADBUTT, QUICK_ATTACK], ENEMY_COLOR),
    Pokemon("Snorlax", 160, [TACKLE, HEADBUTT, BITE, ROAR], ENEMY_COLOR)
]

# State
player_index = 0
enemy_index = 0
player_turn = True
game_over = False
battle_log = []

show_switch_menu = False
show_item_menu = False
medkits = 2

def log(text):
    if len(battle_log) >= 6:
        battle_log.pop(0)
    battle_log.append(text)

def draw_hp_bar(pokemon, x, y, w=200, h=20):
    ratio = pokemon.hp / pokemon.max_hp
    pygame.draw.rect(screen, (200, 0, 0), (x, y, w, h))
    pygame.draw.rect(screen, (0, 200, 0), (x, y, w * ratio, h))
    pygame.draw.rect(screen, (0, 0, 0), (x, y, w, h), 2)

def draw_battle():
    screen.fill(BG_COLOR)
    player = team1[player_index]
    enemy = team2[enemy_index]

    # Enemy
    pygame.draw.rect(screen, enemy.color, (600, 100, 120, 120))
    screen.blit(font.render(enemy.name, True, (0, 0, 0)), (600, 80))
    draw_hp_bar(enemy, 600, 230)

    # Player
    pygame.draw.rect(screen, player.color, (100, 300, 120, 120))
    screen.blit(font.render(player.name, True, (0, 0, 0)), (100, 280))
    draw_hp_bar(player, 100, 430)

    # Move buttons
    if not game_over and player_turn and not player.is_fainted() and not show_switch_menu and not show_item_menu:
        for i, move in enumerate(player.moves):
            x = 320 if i % 2 else 100
            y = 470 + (i // 2) * 50
            btn = pygame.Rect(x, y, 200, 40)
            pygame.draw.rect(screen, BUTTON_COLOR, btn)
            pygame.draw.rect(screen, BUTTON_BORDER, btn, 2)
            screen.blit(font.render(move.name, True, (0, 0, 0)), (x + 10, y + 10))

    # Switch box
    switch_rect = pygame.Rect(100, 580, 150, 40)
    pygame.draw.rect(screen, (200, 255, 200), switch_rect)
    pygame.draw.rect(screen, (0, 100, 0), switch_rect, 2)
    screen.blit(font.render("Switch Pokémon", True, (0, 0, 0)), (switch_rect.x + 5, switch_rect.y + 10))

    # Item box
    item_rect = pygame.Rect(700, 580, 150, 40)
    pygame.draw.rect(screen, (255, 255, 200), item_rect)
    pygame.draw.rect(screen, (100, 100, 0), item_rect, 2)
    screen.blit(font.render("Use Item", True, (0, 0, 0)), (item_rect.x + 30, item_rect.y + 10))

    # Battle log
    pygame.draw.rect(screen, (245, 245, 245), (600, 350, 320, 150))
    pygame.draw.rect(screen, (0, 0, 0), (600, 350, 320, 150), 2)
    for i, msg in enumerate(battle_log):
        screen.blit(log_font.render(msg, True, (0, 0, 0)), (610, 360 + i * 20))

    # Switch Menu
    if show_switch_menu:
        pygame.draw.rect(screen, (255, 255, 255), (150, 150, 660, 300))
        pygame.draw.rect(screen, (0, 0, 0), (150, 150, 660, 300), 3)
        screen.blit(font.render("Choose a Pokémon to switch in:", True, (0, 0, 0)), (160, 160))

        for i, p in enumerate(team1):
            if i == player_index:
                continue
            x = 160 + (i % 3) * 220
            y = 200 + (i // 3) * 100
            color = ACTIVE_HIGHLIGHT if not p.is_fainted() else (180, 180, 180)
            pygame.draw.rect(screen, color, (x, y, 200, 80))
            pygame.draw.rect(screen, (0, 0, 0), (x, y, 200, 80), 2)
            screen.blit(font.render(f"{p.name} ({p.hp}/{p.max_hp})", True, (0, 0, 0)), (x + 10, y + 25))

    # Item Menu
    if show_item_menu:
        pygame.draw.rect(screen, (255, 255, 255), (300, 200, 360, 160))
        pygame.draw.rect(screen, (0, 0, 0), (300, 200, 360, 160), 3)
        screen.blit(font.render(f"Medkits left: {medkits}", True, (0, 0, 0)), (320, 220))
        btn = pygame.Rect(320, 260, 300, 40)
        pygame.draw.rect(screen, (200, 255, 255), btn)
        pygame.draw.rect(screen, (0, 0, 0), btn, 2)
        screen.blit(font.render("Use Medkit (+30 HP)", True, (0, 0, 0)), (btn.x + 10, btn.y + 10))

    pygame.display.flip()

def ai_turn():
    global player_index, enemy_index
    player = team1[player_index]
    enemy = team2[enemy_index]

    if enemy.is_fainted():
        enemy_index += 1
        return

    move = random.choice(enemy.moves)
    log(f"{enemy.name} used {move.name}!")

    # Trigger opponent attack animation with bounce effect
    opponent_attack_animation(100, 300, player)  # Bounce on the player's Pokémon during opponent's attack

    player.take_damage(move.power)

    opponent_bounce_animation(100, 300, player)

    if player.is_fainted():
        log(f"{player.name} fainted!")
        faint_animation(100, 300, player.color)  # Trigger faint animation for player
        player_index += 1



# Main loop
running = True
while running:
    draw_battle()

    if player_index >= 6 or enemy_index >= 6:
        game_over = True
        log("You won!" if enemy_index >= 6 else "Enemy won!")
        draw_battle()
        continue

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
            mx, my = event.pos

            # 🧼 1. CLOSE item menu if you click outside of it
            if show_item_menu and not pygame.Rect(300, 200, 360, 160).collidepoint(mx, my):
                show_item_menu = False

            # 🧼 2. CLOSE switch menu if you click outside (optional!)
            if show_switch_menu and not pygame.Rect(150, 150, 660, 300).collidepoint(mx, my):
                show_switch_menu = False

            # Switch menu logic
            if show_switch_menu:
                for i, p in enumerate(team1):
                    if i == player_index or p.is_fainted(): continue
                    x = 160 + (i % 3) * 220
                    y = 200 + (i // 3) * 100
                    if x <= mx <= x + 200 and y <= my <= y + 80:
                        # Animate the switch
                        log(f"{team1[player_index].name} switched out!")
                        switch_animation_out(100, 300, team1[player_index].color)
                        player_index = i
                        log(f"{team1[player_index].name}, I choose you!")
                        switch_animation_in(100, 300, team1[player_index].color)
                        show_switch_menu = False
                        player_turn = False
                continue


            # Item menu logic
            if show_item_menu:
                if 320 <= mx <= 620 and 260 <= my <= 300:
                    if medkits > 0:
                        player = team1[player_index]
                        if player.hp == player.max_hp:
                            log("Already at full HP!")
                        else:
                            heal_animation(pygame.Rect(100, 300, 120, 120))
                            player.heal(30)
                            medkits -= 1
                            log(f"{player.name} healed 30 HP!")
                    else:
                        log("No medkits left!")
                    show_item_menu = False
                continue

            # Move clicks
            if player_turn and not show_item_menu and not show_switch_menu:
                for i, move in enumerate(team1[player_index].moves):
                    bx = 320 if i % 2 else 100
                    by = 470 + (i // 2) * 50
                    if bx <= mx <= bx + 200 and by <= my <= by + 40:
                        target = team2[enemy_index]
                        log(f"{team1[player_index].name} used {move.name}!")

                        # Use the same animation for the player's attack
                        attack_animation(600, 100, target.color)  # Animate attack (flash effect)
                        target.take_damage(move.power)
                        bounce_sprite(600, 100, target.color)    # Bounce effect on target

                        
                        if target.is_fainted():
                            log(f"{target.name} fainted!")
                            faint_animation(600, 100, target.color)  # Trigger faint animation for enemy
                            enemy_index += 1
                        player_turn = False


            # Switch button
            if 100 <= mx <= 250 and 580 <= my <= 620:
                show_switch_menu = True

            # Item button
            if 700 <= mx <= 850 and 580 <= my <= 620:
                show_item_menu = not show_item_menu  # ← toggles now

    if not player_turn and not game_over:
        pygame.time.delay(700)
        ai_turn()
        player_turn = True

pygame.quit()
