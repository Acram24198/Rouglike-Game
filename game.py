from random import randint
from pyscript import document
from pyscript.ffi import to_js
from js import fetch, localStorage, JSON
import asyncio


# ==========================================
# API
# ==========================================

API_URL = "https://roguelike-api.andrewresor7.workers.dev"

auth_token = None
logged_in = False


# ==========================================
# DEV MODE
# ==========================================

DEV_PASSWORD = "7355608"

dev_mode = False

# Once DEV mode is activated during a run,
# that run cannot submit leaderboard stats.
run_disqualified = False


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
    ["Orc", 125, 15],
    ["Dark Knight", 175, 20],
    ["Dragon", 250, 25],
    ["Robotic Orc", 350, 35],
    ["Jordan Yoder", 450, 50],
    ["Riley Gould", 150, 100]
]

enemy_number = 0

enemy_name = ""
enemy_hp = 0
enemy_max_dmg = 0


# ==========================================
# HTML HELPERS
# ==========================================

def display(text):

    document.querySelector(
        "#game"
    ).innerText = text


def controls(html):

    document.querySelector(
        "#controls"
    ).innerHTML = html


def login_message(
    text="",
    error=False
):

    element = document.querySelector(
        "#login-message"
    )

    element.innerText = text

    if error:
        element.className = "error"
    else:
        element.className = "success"


# ==========================================
# API REQUEST
# ==========================================

async def api_request(
    path,
    method="GET",
    body=None,
    use_auth=False
):

    headers = {
        "Content-Type":
            "application/json"
    }

    if use_auth and auth_token:

        headers[
            "Authorization"
        ] = f"Bearer {auth_token}"

    options = {
        "method": method,
        "headers": headers
    }

    if body is not None:

        options["body"] = JSON.stringify(
            to_js(body)
        )

    try:

        response = await fetch(
            API_URL + path,
            to_js(options)
        )

        data = await response.json()

        return (
            response.status,
            data
        )

    except Exception as error:

        print(
            "API ERROR:",
            error
        )

        return 0, None


# ==========================================
# REGISTER
# ==========================================

async def register(event=None):

    global auth_token
    global logged_in
    global name

    username = document.querySelector(
        "#account-username"
    ).value.strip()

    password = document.querySelector(
        "#account-password"
    ).value

    login_message(
        "Creating account..."
    )

    status, data = await api_request(
        "/register",
        "POST",
        {
            "username": username,
            "password": password
        }
    )

    if data is None:

        login_message(
            "Could not connect to account server.",
            True
        )

        return

    if status not in (
        200,
        201
    ):

        error_message = getattr(
            data,
            "error",
            "Registration failed."
        )

        login_message(
            error_message,
            True
        )

        return

    auth_token = data.token

    logged_in = True

    name = data.user.username

    localStorage.setItem(
        "roguelike_token",
        auth_token
    )

    document.querySelector(
        "#account-password"
    ).value = ""

    login_message("")

    show_logged_in()

    await load_leaderboards()

    reset_run()

    show_start()


# ==========================================
# LOGIN
# ==========================================

async def login(event=None):

    global auth_token
    global logged_in
    global name

    username = document.querySelector(
        "#account-username"
    ).value.strip()

    password = document.querySelector(
        "#account-password"
    ).value

    login_message(
        "Logging in..."
    )

    status, data = await api_request(
        "/login",
        "POST",
        {
            "username": username,
            "password": password
        }
    )

    if data is None:

        login_message(
            "Could not connect to account server.",
            True
        )

        return

    if status != 200:

        error_message = getattr(
            data,
            "error",
            "Login failed."
        )

        login_message(
            error_message,
            True
        )

        return

    auth_token = data.token

    logged_in = True

    name = data.user.username

    localStorage.setItem(
        "roguelike_token",
        auth_token
    )

    document.querySelector(
        "#account-password"
    ).value = ""

    login_message("")

    show_logged_in()

    await load_leaderboards()

    reset_run()

    show_start()


# ==========================================
# LOGOUT
# ==========================================

async def logout(event=None):

    global auth_token
    global logged_in
    global name

    if auth_token:

        await api_request(
            "/logout",
            "POST",
            use_auth=True
        )

    auth_token = None

    logged_in = False

    name = ""

    localStorage.removeItem(
        "roguelike_token"
    )

    document.querySelector(
        "#account-bar"
    ).style.display = "none"

    document.querySelector(
        "#login-area"
    ).style.display = "block"

    document.querySelector(
        "#account-password"
    ).value = ""

    display("""
========================
       ROGUELIKE
========================

Log in or create an account to play.
""")

    controls("")


# ==========================================
# ACCOUNT DISPLAY
# ==========================================

def show_logged_in():

    document.querySelector(
        "#login-area"
    ).style.display = "none"

    document.querySelector(
        "#account-bar"
    ).style.display = "block"

    document.querySelector(
        "#account-status"
    ).innerText = (
        f"Logged in as: {name}"
    )


def show_logged_out():

    document.querySelector(
        "#account-bar"
    ).style.display = "none"

    document.querySelector(
        "#login-area"
    ).style.display = "block"

    display("""
========================
       ROGUELIKE
========================

Log in or create an account to play.
""")

    controls("")


# ==========================================
# RESTORE LOGIN
# ==========================================

async def restore_session():

    global auth_token
    global logged_in
    global name

    saved_token = localStorage.getItem(
        "roguelike_token"
    )

    if not saved_token:

        show_logged_out()

        await load_leaderboards()

        return

    auth_token = saved_token

    status, data = await api_request(
        "/me",
        use_auth=True
    )

    if (
        status == 200
        and data is not None
        and data.logged_in
    ):

        logged_in = True

        name = data.user.username

        show_logged_in()

        reset_run()

        show_start()

    else:

        auth_token = None

        logged_in = False

        name = ""

        localStorage.removeItem(
            "roguelike_token"
        )

        show_logged_out()

    await load_leaderboards()


# ==========================================
# LEADERBOARDS
# ==========================================

async def load_leaderboards():

    status, data = await api_request(
        "/leaderboards"
    )

    if (
        status != 200
        or data is None
    ):

        document.querySelector(
            "#wins-leaderboard"
        ).innerText = (
            "Unable to load."
        )

        document.querySelector(
            "#furthest-leaderboard"
        ).innerText = (
            "Unable to load."
        )

        return

    # ------------------------------
    # WINS
    # ------------------------------

    wins_html = ""

    for index, player in enumerate(
        data.wins
    ):

        wins_html += (
            '<div class="leaderboard-row">'
            f'<span>{index + 1}. '
            f'{player.username}</span>'
            f'<span>{player.wins}</span>'
            '</div>'
        )

    if not wins_html:

        wins_html = (
            '<div class="leaderboard-empty">'
            'No wins yet.'
            '</div>'
        )

    document.querySelector(
        "#wins-leaderboard"
    ).innerHTML = wins_html

    # ------------------------------
    # FURTHEST RUN
    # ------------------------------

    furthest_html = ""

    for index, player in enumerate(
        data.furthest
    ):

        furthest_html += (
            '<div class="leaderboard-row">'
            f'<span>{index + 1}. '
            f'{player.username}</span>'
            f'<span>Round '
            f'{player.furthest_enemy}</span>'
            '</div>'
        )

    if not furthest_html:

        furthest_html = (
            '<div class="leaderboard-empty">'
            'No runs yet.'
            '</div>'
        )

    document.querySelector(
        "#furthest-leaderboard"
    ).innerHTML = furthest_html


# ==========================================
# SUBMIT PROGRESS
# ==========================================

async def submit_progress():

    if not logged_in:
        return

    if run_disqualified:
        return

    round_number = (
        enemy_number + 1
    )

    status, data = await api_request(
        "/progress",
        "POST",
        {
            "furthest_enemy":
                round_number
        },
        use_auth=True
    )

    if status == 200:

        await load_leaderboards()


# ==========================================
# SUBMIT WIN
# ==========================================

async def submit_win():

    if not logged_in:
        return

    if run_disqualified:
        return

    status, data = await api_request(
        "/win",
        "POST",
        use_auth=True
    )

    if status == 200:

        await load_leaderboards()


# ==========================================
# DEV MODE
# ==========================================

def open_dev_login(event=None):

    if dev_mode:

        open_dev_panel()

        return

    document.querySelector(
        "#dev-login"
    ).style.display = "block"

    document.querySelector(
        "#dev-status"
    ).innerText = ""


def close_dev_login(event=None):

    document.querySelector(
        "#dev-login"
    ).style.display = "none"

    document.querySelector(
        "#dev-password"
    ).value = ""

    document.querySelector(
        "#dev-status"
    ).innerText = ""


def check_dev_password(event=None):

    global dev_mode
    global run_disqualified

    entered_password = (
        document.querySelector(
            "#dev-password"
        ).value
    )

    if entered_password == DEV_PASSWORD:

        dev_mode = True

        run_disqualified = True

        document.querySelector(
            "#dev-login"
        ).style.display = "none"

        document.querySelector(
            "#dev-password"
        ).value = ""

        document.querySelector(
            "#dev-button"
        ).innerText = (
            "DEV ACTIVE"
        )

        open_dev_panel()

    else:

        document.querySelector(
            "#dev-status"
        ).innerText = (
            "Incorrect password."
        )


def open_dev_panel(event=None):

    if not dev_mode:
        return

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

    enemy_select = (
        document.querySelector(
            "#dev-enemy"
        )
    )

    options = ""

    for i, enemy in enumerate(
        enemies
    ):

        selected = ""

        if i == enemy_number:
            selected = "selected"

        options += (
            f'<option value="{i}" '
            f'{selected}>'
            f'{enemy[0]}'
            f'</option>'
        )

    enemy_select.innerHTML = (
        options
    )

    document.querySelector(
        "#dev-panel"
    ).style.display = "block"


def close_dev_panel(event=None):

    document.querySelector(
        "#dev-panel"
    ).style.display = "none"


def get_dev_number(
    element_id,
    fallback
):

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

    max_health = max(
        1,
        max_health
    )

    max_mana = max(
        0,
        max_mana
    )

    max_damage = max(
        1,
        max_damage
    )

    mana_regen = max(
        0,
        mana_regen
    )

    heal_rate = max(
        1,
        heal_rate
    )

    health = max(
        0,
        health
    )

    mana = max(
        0,
        mana
    )

    if health > max_health:
        health = max_health

    if mana > max_mana:
        mana = max_mana

    if enemy_name:

        show_combat(
            "Developer stats applied.\n"
            "Leaderboard disabled "
            "for this run."
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

    apply_dev_changes()

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

    if not logged_in:

        show_logged_out()

        return

    display(f"""
========================
       ROGUELIKE
========================

Welcome, {name}.

Fight through every enemy.
Choose an upgrade after each victory.

Your leaderboard progress will be
saved automatically.
""")

    controls("""
        <button py-click="start_game">
            START RUN
        </button>
    """)


# ==========================================
# START GAME
# ==========================================

def start_game(event=None):

    if not logged_in:
        return

    reset_run()

    start_enemy()


# ==========================================
# RESET RUN
# ==========================================

def reset_run():

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
    global run_disqualified

    max_health = 100
    health = max_health

    max_mana = 50
    mana = max_mana
    mana_regen = 3

    max_damage = 15
    heal_rate = 20

    enemy_number = 0

    enemy_name = ""
    enemy_hp = 0
    enemy_max_dmg = 0

    dev_mode = False

    run_disqualified = False

    document.querySelector(
        "#dev-button"
    ).innerText = "DEV"

    document.querySelector(
        "#dev-panel"
    ).style.display = "none"

    document.querySelector(
        "#dev-login"
    ).style.display = "none"


# ==========================================
# LOAD ENEMY
# ==========================================

def start_enemy():

    global enemy_name
    global enemy_hp
    global enemy_max_dmg

    enemy = enemies[
        enemy_number
    ]

    enemy_name = enemy[0]

    enemy_hp = enemy[1]

    enemy_max_dmg = enemy[2]

    # Save the round automatically.
    # DEV runs are rejected by
    # submit_progress().

    asyncio.create_task(
        submit_progress()
    )

    show_combat(
        f"You encounter a "
        f"{enemy_name}!"
    )


# ==========================================
# COMBAT SCREEN
# ==========================================

def show_combat(message=""):

    dev_text = ""

    if run_disqualified:

        dev_text = (
            "\n\n"
            "[DEV RUN - "
            "LEADERBOARD DISABLED]"
        )

    display(f"""
========================
       {name}
========================

Round:      {enemy_number + 1}
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


{message}{dev_text}
""")

    controls("""
        <button py-click="attack">
            ATTACK
        </button>

        <button py-click="heal">
            HEAL (10 MANA)
        </button>
    """)


# ==========================================
# ATTACK
# ==========================================

def attack(event=None):

    global enemy_hp
    global health

    damage = randint(
        1,
        max_damage
    )

    enemy_hp -= damage

    message = (
        f"You attack the "
        f"{enemy_name}!\n"
        f"You deal {damage} damage!"
    )

    if enemy_hp <= 0:

        show_upgrade(
            f"You defeated the "
            f"{enemy_name}!"
        )

        return

    enemy_damage = randint(
        1,
        enemy_max_dmg
    )

    health -= enemy_damage

    message += (
        f"\n\nThe {enemy_name} "
        f"attacks you for "
        f"{enemy_damage} damage!"
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
            "You don't have "
            "enough mana!"
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
        f"\n\nThe {enemy_name} "
        f"attacks you for "
        f"{enemy_damage} damage!"
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

    if enemy_number >= len(
        enemies
    ):

        win_game()

        return

    start_enemy()


# ==========================================
# GAME OVER
# ==========================================

def game_over():

    if run_disqualified:

        leaderboard_text = (
            "\nDEV MODE was used.\n"
            "This run was not submitted."
        )

    else:

        leaderboard_text = (
            "\nYour furthest round "
            "has been saved."
        )

    display(f"""
========================
       GAME OVER
========================

{name} has fallen.

You reached Round {enemy_number + 1}.


FINAL STATS

Max HP:      {max_health}
Max Mana:    {max_mana}
Mana Regen:  {mana_regen}/turn
Max Damage:  {max_damage}
Heal Rate:   {heal_rate}

{leaderboard_text}
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

    if not run_disqualified:

        asyncio.create_task(
            submit_win()
        )

        leaderboard_text = (
            "\nWin recorded!"
        )

    else:

        leaderboard_text = (
            "\nDEV MODE was used.\n"
            "Win was not submitted."
        )

    display(f"""
========================
         YOU WIN!
========================

{name} defeated every enemy!

Rounds cleared: {len(enemies)}


FINAL BUILD

Max HP:      {max_health}
Max Mana:    {max_mana}
Mana Regen:  {mana_regen}/turn
Max Damage:  {max_damage}
Heal Rate:   {heal_rate}

{leaderboard_text}
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

    reset_run()

    show_start()


# ==========================================
# BOOT
# ==========================================

asyncio.create_task(
    restore_session()
)
