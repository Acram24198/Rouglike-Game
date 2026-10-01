from random import randint
from pyscript import document


# ==========================================
# PLAYER
# ==========================================

name = ""

max_health = 100
health = max_health

max_mana = 50
mana = max_mana

max_damage = 15
heal_rate = 20


# ==========================================
# ENEMIES
# ==========================================

enemies = [
    ["Goblin", 75, 15],
    ["Skeleton", 100, 18],
    ["Orc", 125, 22],
    ["Dark Knight", 175, 28],
    ["Dragon", 250, 35]
]

enemy_number = 0

enemy_name = ""
enemy_hp = 0
enemy_max_dmg = 0


# ==========================================
# HTML HELPERS
# ==========================================

def display(text):
    document.querySelector("#game").innerText = text


def controls(html):
    document.querySelector("#controls").innerHTML = html


# ==========================================
# START SCREEN
# ==========================================

def show_start():

    display("""
========================
      LAKELAND RPG
========================

Enter your name to begin.
""")

    controls("""
        <input id="nameInput" placeholder="Your name">
        <button py-click="start_game">START</button>
    """)


# ==========================================
# START GAME
# ==========================================

def start_game(event=None):

    global name

    name = document.querySelector("#nameInput").value.strip()

    if not name:
        name = "Player"

    start_enemy()


# ==========================================
# LOAD ENEMY
# ==========================================

def start_enemy():

    global enemy_name
    global enemy_hp
    global enemy_max_dmg

    enemy = enemies[enemy_number]

    enemy_name = enemy[0]
    enemy_hp = enemy[1]
    enemy_max_dmg = enemy[2]

    show_combat(
        f"You encounter a {enemy_name}!"
    )


# ==========================================
# COMBAT SCREEN
# ==========================================

def show_combat(message=""):

    display(f"""
========================
       {name}
========================

HP:        {max(health, 0)}/{max_health}
Mana:      {mana}/{max_mana}
Damage:    1-{max_damage}
Heal Rate: 1-{heal_rate}


========================
       {enemy_name}
========================

HP:        {max(enemy_hp, 0)}
Damage:    1-{enemy_max_dmg}


{message}
""")

    controls("""
        <button py-click="attack">ATTACK</button>
        <button py-click="heal">HEAL (10 MANA)</button>
    """)


# ==========================================
# ATTACK
# ==========================================

def attack(event=None):

    global enemy_hp
    global health

    damage = randint(1, max_damage)

    enemy_hp -= damage

    message = (
        f"You attack the {enemy_name}!\n"
        f"You deal {damage} damage!"
    )

    # Enemy defeated
    if enemy_hp <= 0:

        show_upgrade(
            f"You defeated the {enemy_name}!"
        )

        return

    # Enemy retaliates
    enemy_damage = randint(1, enemy_max_dmg)

    health -= enemy_damage

    message += (
        f"\n\nThe {enemy_name} attacks you "
        f"for {enemy_damage} damage!"
    )

    if health <= 0:

        game_over()

        return

    show_combat(message)


# ==========================================
# HEAL
# ==========================================

def heal(event=None):

    global health
    global mana

    if mana < 10:

        show_combat(
            "You don't have enough mana!"
        )

        return

    mana -= 10

    healing = randint(1, heal_rate)

    health += healing

    if health > max_health:
        health = max_health

    message = f"You heal {healing} HP!"

    # Enemy retaliates
    enemy_damage = randint(1, enemy_max_dmg)

    health -= enemy_damage

    message += (
        f"\n\nThe {enemy_name} attacks you "
        f"for {enemy_damage} damage!"
    )

    if health <= 0:

        game_over()

        return

    show_combat(message)


# ==========================================
# UPGRADE SCREEN
# ==========================================

def show_upgrade(message=""):

    new_mana = round(max_mana * 1.25)
    new_damage = round(max_damage * 1.15)
    new_heal = round(heal_rate * 1.25)

    display(f"""
{message}

========================
    CHOOSE AN UPGRADE
========================

MAX MANA +25%
{max_mana} -> {new_mana}

MAX DAMAGE +15%
{max_damage} -> {new_damage}

HEAL RATE +25%
{heal_rate} -> {new_heal}
""")

    controls("""
        <button py-click="upgrade_mana">
            MANA +25%
        </button>

        <button py-click="upgrade_damage">
            DAMAGE +15%
        </button>

        <button py-click="upgrade_heal">
            HEALING +25%
        </button>
    """)


# ==========================================
# MANA UPGRADE
# ==========================================

def upgrade_mana(event=None):

    global max_mana
    global mana

    max_mana = round(max_mana * 1.25)

    mana = max_mana

    next_enemy()


# ==========================================
# DAMAGE UPGRADE
# ==========================================

def upgrade_damage(event=None):

    global max_damage
    global mana

    max_damage = round(max_damage * 1.15)

    mana = max_mana

    next_enemy()


# ==========================================
# HEAL UPGRADE
# ==========================================

def upgrade_heal(event=None):

    global heal_rate
    global mana

    heal_rate = round(heal_rate * 1.25)

    mana = max_mana

    next_enemy()


# ==========================================
# NEXT ENEMY
# ==========================================

def next_enemy():

    global enemy_number

    enemy_number += 1

    if enemy_number >= len(enemies):

        win_game()

        return

    start_enemy()


# ==========================================
# GAME OVER
# ==========================================

def game_over():

    display(f"""
========================
       GAME OVER
========================

{name} has fallen.


FINAL STATS

Max HP:      {max_health}
Max Mana:    {max_mana}
Max Damage:  {max_damage}
Heal Rate:   {heal_rate}
""")

    controls("""
        <button py-click="restart_game">
            PLAY AGAIN
        </button>
    """)


# ==========================================
# WIN
# ==========================================

def win_game():

    display(f"""
========================
        YOU WIN!
========================

{name} defeated every enemy!


FINAL BUILD

Max HP:      {max_health}
Max Mana:    {max_mana}
Max Damage:  {max_damage}
Heal Rate:   {heal_rate}
""")

    controls("""
        <button py-click="restart_game">
            PLAY AGAIN
        </button>
    """)


# ==========================================
# RESTART
# ==========================================

def restart_game(event=None):

    global max_health
    global health

    global max_mana
    global mana

    global max_damage
    global heal_rate

    global enemy_number

    max_health = 100
    health = max_health

    max_mana = 50
    mana = max_mana

    max_damage = 15
    heal_rate = 20

    enemy_number = 0

    show_start()


# ==========================================
# BOOT
# ==========================================

show_start()
