from random import randint
from pyscript import document


# ==========================================
# DEV MODE
# ==========================================

DEV_PASSWORD = "7355608"

dev_mode = False


# ==========================================
# PLAYER
# ==========================================

name = ""

max_health = 100
health = max_health

max_mana = 50
mana = max_mana
mana_regen = 3

max_damage = 15
heal_rate = 20


# ==========================================
# ENEMIES
# ==========================================

enemies = [
    ["Goblin", 75, 5],
    ["Skeleton", 100, 12],
    ["Orc", 125, 18],
    ["Dark Knight", 175, 25],
    ["Dragon", 250, 30],
    ["Robotic Orc", 350, 45],
    ["Jordan Yoder", 450, 60]
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
# DEV MODE FUNCTIONS
# ==========================================

def open_dev_login(event=None):

    if dev_mode:
        open_dev_panel()
        return

    document.querySelector("#dev-login").style.display = "block"
    document.querySelector("#dev-status").innerText = ""


def close_dev_login(event=None):

    document.querySelector("#dev-login").style.display = "none"
    document.querySelector("#dev-password").value = ""
    document.querySelector("#dev-status").innerText = ""


def check_dev_password(event=None):

    global dev_mode

    entered_password = document.querySelector(
        "#dev-password"
    ).value

    if entered_password == DEV_PASSWORD:

        dev_mode = True

        document.querySelector(
            "#dev-login"
        ).style.display = "none"

        document.querySelector(
            "#dev-password"
        ).value = ""

        document.querySelector(
            "#dev-button"
        ).innerText = "DEV ACTIVE"

        open_dev_panel()

    else:

        document.querySelector(
            "#dev-status"
        ).innerText = "Incorrect password."


def open_dev_panel(event=None):

    if not dev_mode:
        return

    # Fill current player stats
    document.querySelector(
        "#dev-health"
    ).value = str(health)

    document.querySelector(
        "#dev-max-health"
    ).value = str(max_health)

    document.querySelector(
        "#dev-mana"
    ).value = str(mana)

    document.querySelector(
        "#dev-max-mana"
    ).value = str(max_mana)

    document.querySelector(
        "#dev-damage"
    ).value = str(max_damage)

    document.querySelector(
        "#dev-regen"
    ).value = str(mana_regen)

    document.querySelector(
        "#dev-heal"
    ).value = str(heal_rate)

    # Automatically generate enemy list
    enemy_select = document.querySelector("#dev-enemy")

    options = ""

    for i, enemy in enumerate(enemies):

        selected = ""

        if i == enemy_number:
            selected = "selected"

        options += (
            f'<option value="{i}" {selected}>'
            f'{enemy[0]}'
            f'</option>'
        )

    enemy_select.innerHTML = options

    document.querySelector(
        "#dev-panel"
    ).style.display = "block"


def close_dev_panel(event=None):

    document.querySelector(
        "#dev-panel"
    ).style.display = "none"


def get_dev_number(element_id, fallback):

    try:

        value = int(
            document.querySelector(
                element_id
            ).value
        )

        return value

    except:
        return fallback


def apply_dev_changes(event=None):

    global health
    global max_health

    global mana
    global max_mana
    global mana_regen

    global max_damage
    global heal_rate

    if not dev_mode:
        return

    health = get_dev_number(
        "#dev-health",
        health
    )

    max_health = get_dev_number(
        "#dev-max-health",
        max_health
    )

    mana = get_dev_number(
        "#dev-mana",
        mana
    )

    max_mana = get_dev_number(
        "#dev-max-mana",
        max_mana
    )

    max_damage = get_dev_number(
        "#dev-damage",
        max_damage
    )

    mana_regen = get_dev_number(
        "#dev-regen",
        mana_regen
    )

    heal_rate = get_dev_number(
        "#dev-heal",
        heal_rate
    )

    # Prevent invalid values
    max_health = max(1, max_health)
    max_mana = max(0, max_mana)
    max_damage = max(1, max_damage)
    mana_regen = max(0, mana_regen)
    heal_rate = max(1, heal_rate)

    health = max(0, health)
    mana = max(0, mana)

    # Keep current values within maximums
    if health > max_health:
        health = max_health

    if mana > max_mana:
        mana = max_mana

    # Refresh combat display if an enemy exists
    if enemy_name:

        show_combat(
            "Developer stats applied."
        )


def dev_load_enemy(event=None):

    global enemy_number

    if not dev_mode:
        return

    try:

        enemy_number = int(
            document.querySelector(
                "#dev-enemy"
            ).value
        )

    except:
        return

    # Apply stat changes too
    apply_dev_changes()

    # Start selected enemy at full HP
    start_enemy()

    close_dev_panel()


# ==========================================
# MANA REGEN
# ==========================================

def regenerate_mana():

    global mana

    mana += mana_regen

    if mana > max_mana:
        mana = max_mana


# ==========================================
# START SCREEN
# ==========================================

def show_start():

    display("""
========================
       Roguelike
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

    name = document.querySelector(
        "#nameInput"
    ).value.strip()

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

HP:         {max(health, 0)}/{max_health}
Mana:       {mana}/{max_mana}
Mana Regen: {mana_regen}/turn
Damage:     1-{max_damage}
Heal Rate:  1-{heal_rate}


========================
       {enemy_name}
========================

HP:         {max(enemy_hp, 0)}
Damage:     1-{enemy_max_dmg}


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

    if enemy_hp <= 0:

        show_upgrade(
            f"You defeated the {enemy_name}!"
        )

        return

    enemy_damage = randint(
        1,
        enemy_max_dmg
    )

    health -= enemy_damage

    message += (
        f"\n\nThe {enemy_name} attacks you "
        f"for {enemy_damage} damage!"
    )

    if health <= 0:

        game_over()
        return

    regenerate_mana()

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

    healing = randint(
        1,
        heal_rate
    )

    health += healing

    if health > max_health:
        health = max_health

    message = (
        f"You heal {healing} HP!"
    )

    enemy_damage = randint(
        1,
        enemy_max_dmg
    )

    health -= enemy_damage

    message += (
        f"\n\nThe {enemy_name} attacks you "
        f"for {enemy_damage} damage!"
    )

    if health <= 0:

        game_over()
        return

    regenerate_mana()

    show_combat(message)


# ==========================================
# UPGRADE SCREEN
# ==========================================

def show_upgrade(message=""):

    new_mana = round(
        max_mana * 1.25
    )

    new_damage = round(
        max_damage * 1.15
    )

    new_heal = round(
        heal_rate * 1.25
    )

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

    max_mana = round(
        max_mana * 1.25
    )

    mana = max_mana

    next_enemy()


# ==========================================
# DAMAGE UPGRADE
# ==========================================

def upgrade_damage(event=None):

    global max_damage
    global mana

    max_damage = round(
        max_damage * 1.15
    )

    mana = max_mana

    next_enemy()


# ==========================================
# HEAL UPGRADE
# ==========================================

def upgrade_heal(event=None):

    global heal_rate
    global mana

    heal_rate = round(
        heal_rate * 1.25
    )

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
Mana Regen:  {mana_regen}/turn
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
Mana Regen:  {mana_regen}/turn
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
    global mana_regen

    global max_damage
    global heal_rate

    global enemy_number
    global enemy_name
    global enemy_hp
    global enemy_max_dmg

    global dev_mode

    # Disable dev mode for the new run
    dev_mode = False

    document.querySelector(
        "#dev-button"
    ).innerText = "DEV"

    document.querySelector(
        "#dev-panel"
    ).style.display = "none"

    document.querySelector(
        "#dev-login"
    ).style.display = "none"

    # Reset player
    max_health = 100
    health = max_health

    max_mana = 50
    mana = max_mana
    mana_regen = 3

    max_damage = 15
    heal_rate = 20

    # Reset enemies
    enemy_number = 0

    enemy_name = ""
    enemy_hp = 0
    enemy_max_dmg = 0

    show_start()


# ==========================================
# BOOT
# ==========================================

show_start()
