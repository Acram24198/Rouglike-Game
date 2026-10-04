from random import randint
from pyscript import document
from pyscript.ffi import to_js
from js import fetch, localStorage, JSON, confirm
import asyncio


# ==========================================
# API
# ==========================================

API_URL = "https://roguelike-api.andrewresor7.workers.dev"

auth_token = None
logged_in = False

supporter = False
show_supporter_tag = False
supporter_bonus = False
is_admin = False


# ==========================================
# DEV MODE
# ==========================================

DEV_PASSWORD = "7355608"

dev_mode = False
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

min_damage = 5
max_damage = 15

min_heal = 5
heal_rate = 20


# ==========================================
# ENEMIES
# ==========================================

enemies = [
    ["Goblin", 75, 5],
    ["Skeleton", 100, 12],
    ["Orc", 120, 15],
    ["Dark Knight", 175, 20],
    ["Dragon", 250, 25],
    ["Robotic Orc", 350, 35],
    ["Jordan Yoder", 450, 50],
    ["Riley Gould", 150, 100],
    ["Evil Jordan", 300, 125],
    ["Alex Resor", 450, 100]
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


def login_message(text="", error=False):

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
        "Content-Type": "application/json"
    }

    if use_auth and auth_token:

        headers["Authorization"] = (
            f"Bearer {auth_token}"
        )

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

        return response.status, data

    except Exception as error:

        print(
            "API ERROR:",
            error
        )

        return 0, None


# ==========================================
# ACCOUNT DATA
# ==========================================

def load_account_data(user):

    global name
    global supporter
    global show_supporter_tag
    global supporter_bonus
    global is_admin

    name = user.username

    supporter = bool(
        getattr(
            user,
            "supporter",
            False
        )
    )

    show_supporter_tag = bool(
        getattr(
            user,
            "show_supporter_tag",
            False
        )
    )

    supporter_bonus = bool(
        getattr(
            user,
            "supporter_bonus",
            False
        )
    )

    is_admin = bool(
        getattr(
            user,
            "is_admin",
            False
        )
    )


# ==========================================
# REGISTER
# ==========================================

async def register(event=None):

    global auth_token
    global logged_in

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

    if status not in (200, 201):

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

    load_account_data(
        data.user
    )

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

    load_account_data(
        data.user
    )

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

    global supporter
    global show_supporter_tag
    global supporter_bonus
    global is_admin

    if auth_token:

        await api_request(
            "/logout",
            "POST",
            use_auth=True
        )

    auth_token = None
    logged_in = False
    name = ""

    supporter = False
    show_supporter_tag = False
    supporter_bonus = False
    is_admin = False

    localStorage.removeItem(
        "roguelike_token"
    )

    document.querySelector(
        "#account-bar"
    ).style.display = "none"

    document.querySelector(
        "#supporter-settings"
    ).style.display = "none"

    document.querySelector(
        "#supporter-button"
    ).style.display = "none"

    admin_button = document.querySelector("#admin-button")
    if admin_button:
        admin_button.style.display = "none"

    admin_panel = document.querySelector("#admin-panel")
    if admin_panel:
        admin_panel.style.display = "none"

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

    account_name = name

    if (
        supporter
        and show_supporter_tag
    ):
        account_name += " ★ SUPPORTER"

    document.querySelector(
        "#account-status"
    ).innerText = (
        f"Logged in as: {account_name}"
    )

    supporter_button = (
        document.querySelector(
            "#supporter-button"
        )
    )

    if supporter:
        supporter_button.style.display = (
            "inline-block"
        )
    else:
        supporter_button.style.display = (
            "none"
        )

        document.querySelector(
            "#supporter-settings"
        ).style.display = "none"

    admin_button = document.querySelector("#admin-button")
    if admin_button:
        admin_button.style.display = (
            "inline-block" if is_admin else "none"
        )

    if not is_admin:
        admin_panel = document.querySelector("#admin-panel")
        if admin_panel:
            admin_panel.style.display = "none"


def show_logged_out():

    document.querySelector(
        "#account-bar"
    ).style.display = "none"

    document.querySelector(
        "#supporter-button"
    ).style.display = "none"

    document.querySelector(
        "#supporter-settings"
    ).style.display = "none"

    admin_button = document.querySelector("#admin-button")
    if admin_button:
        admin_button.style.display = "none"

    admin_panel = document.querySelector("#admin-panel")
    if admin_panel:
        admin_panel.style.display = "none"

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
# IN-GAME ADMIN
# ==========================================

def admin_message(text="", error=False):
    element = document.querySelector("#admin-message")
    if not element:
        return
    element.innerText = text
    element.className = "error" if error else "success"


async def open_admin_panel(event=None):
    if not is_admin:
        return

    panel = document.querySelector("#admin-panel")
    if not panel:
        return

    document.querySelector("#supporter-settings").style.display = "none"
    panel.style.display = "block"
    admin_message("Loading accounts...")
    await load_admin_users()


def close_admin_panel(event=None):
    panel = document.querySelector("#admin-panel")
    if panel:
        panel.style.display = "none"


async def load_admin_users(event=None):
    if not is_admin:
        return

    status, data = await api_request(
        "/admin/users",
        use_auth=True
    )

    if status != 200 or data is None:
        message = "Unable to load users."
        if data is not None:
            message = getattr(data, "error", message)
        admin_message(message, True)
        return

    table = document.querySelector("#admin-users")
    if not table:
        return

    rows = ""

    for user in data.users:
        user_id = int(user.id)
        username = str(user.username)
        safe_username = (
            username
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#39;")
        )

        supporter_text = "YES" if bool(user.supporter) else "NO"
        tag_text = "ON" if bool(user.show_supporter_tag) else "OFF"
        bonus_text = "ON" if bool(user.supporter_bonus) else "OFF"

        if bool(user.supporter):
            supporter_action = (
                f'<button py-click="remove_supporter" '
                f'data-user-id="{user_id}">REMOVE SUPPORTER</button>'
            )
        else:
            supporter_action = (
                f'<button py-click="grant_supporter" '
                f'data-user-id="{user_id}">GRANT SUPPORTER</button>'
            )

        if bool(getattr(user, "is_admin", False)):
            action = (
                supporter_action +
                '<span class="admin-protected"> ADMIN ACCOUNT</span>'
            )
        else:
            action = (
                supporter_action +
                f'<button class="admin-delete" '
                f'py-click="delete_account" '
                f'data-user-id="{user_id}" '
                f'data-username="{safe_username}">DELETE</button>'
            )

        rows += (
            "<tr>"
            f"<td>{safe_username}</td>"
            f"<td>{user.wins}</td>"
            f"<td>{user.furthest_enemy}</td>"
            f"<td>{supporter_text}</td>"
            f"<td>{tag_text}</td>"
            f"<td>{bonus_text}</td>"
            f"<td>{action}</td>"
            "</tr>"
        )

    if not rows:
        rows = '<tr><td colspan="7">No accounts found.</td></tr>'

    table.innerHTML = rows
    admin_message(f"Loaded {len(data.users)} accounts.")


def admin_event_element(event):
    if event is None:
        return None

    try:
        target = event.target
        if target:
            return target
    except:
        pass

    try:
        target = event.currentTarget
        if target:
            return target
    except:
        pass

    return None


def admin_event_user_id(event):
    button = admin_event_element(event)

    if button is None:
        return None

    try:
        value = button.getAttribute("data-user-id")

        if value is None:
            return None

        return int(str(value))
    except:
        return None


def admin_event_username(event):
    button = admin_event_element(event)

    if button is None:
        return ""

    try:
        value = button.getAttribute("data-username")

        if value is None:
            return ""

        return str(value)
    except:
        return ""


async def set_supporter_status(user_id, enabled):
    if not is_admin:
        return False

    if user_id is None:
        admin_message("Invalid user ID.", True)
        return False

    admin_message("Updating supporter status...")

    status, data = await api_request(
        "/admin/supporter",
        "POST",
        {
            "user_id": user_id,
            "supporter": enabled
        },
        use_auth=True
    )

    if status != 200 or data is None:
        message = "Could not update supporter."
        if data is not None:
            message = getattr(data, "error", message)
        admin_message(message, True)
        return False

    admin_message("Supporter status updated.")
    await load_admin_users()
    await load_leaderboards()
    return True


async def grant_supporter(event=None):
    if event is None:
        return
    await set_supporter_status(
        admin_event_user_id(event),
        True
    )


async def remove_supporter(event=None):
    if event is None:
        return
    await set_supporter_status(
        admin_event_user_id(event),
        False
    )


async def delete_account(event=None):
    if not is_admin or event is None:
        return

    user_id = admin_event_user_id(event)

    if user_id is None:
        admin_message("Invalid user ID.", True)
        return

    username = admin_event_username(event)

    if not username:
        username = f"User #{user_id}"

    approved = confirm(
        f'Delete account "{username}" permanently?\\n\\n'
        "This removes the account, leaderboard stats, supporter status, "
        "and active login sessions. This cannot be undone."
    )

    if not approved:
        return

    admin_message(
        f'Deleting "{username}"...'
    )

    status, data = await api_request(
        "/admin/delete-user",
        "POST",
        {
            "user_id": user_id
        },
        use_auth=True
    )

    if status != 200 or data is None:
        message = "Could not delete account."

        if data is not None:
            message = getattr(
                data,
                "error",
                message
            )

        admin_message(message, True)
        return

    admin_message(
        f'Account "{username}" deleted.'
    )

    await load_admin_users()
    await load_leaderboards()


# ==========================================
# SUPPORTER SETTINGS
# ==========================================

def open_supporter_settings(event=None):

    if not supporter:
        return

    document.querySelector(
        "#supporter-settings"
    ).style.display = "block"

    update_supporter_panel()


def close_supporter_settings(event=None):

    document.querySelector(
        "#supporter-settings"
    ).style.display = "none"


def update_supporter_panel():

    if not supporter:
        return

    if show_supporter_tag:
        tag_text = "ON"
    else:
        tag_text = "OFF"

    if supporter_bonus:
        bonus_text = "ON"
        percent_text = "40%"
    else:
        bonus_text = "OFF"
        percent_text = "NORMAL"

    document.querySelector(
        "#supporter-tag-status"
    ).innerText = (
        f"Supporter Tag: {tag_text}"
    )

    document.querySelector(
        "#supporter-bonus-status"
    ).innerText = (
        f"Supporter Bonus: {bonus_text}"
    )

    document.querySelector(
        "#supporter-upgrade-status"
    ).innerText = (
        f"Upgrade Power: {percent_text}"
    )


async def save_supporter_settings():

    status, data = await api_request(
        "/supporter/settings",
        "POST",
        {
            "show_supporter_tag":
                show_supporter_tag,

            "supporter_bonus":
                supporter_bonus
        },
        use_auth=True
    )

    if (
        status == 200
        and data is not None
    ):

        load_account_data(
            data.user
        )

        show_logged_in()
        update_supporter_panel()

        await load_leaderboards()

        return True

    return False


async def toggle_supporter_tag(
    event=None
):

    global show_supporter_tag

    if not supporter:
        return

    old_value = show_supporter_tag

    show_supporter_tag = (
        not show_supporter_tag
    )

    success = await save_supporter_settings()

    if not success:

        show_supporter_tag = old_value

        update_supporter_panel()


async def toggle_supporter_bonus(
    event=None
):

    global supporter_bonus

    if not supporter:
        return

    old_value = supporter_bonus

    supporter_bonus = (
        not supporter_bonus
    )

    success = await save_supporter_settings()

    if not success:

        supporter_bonus = old_value

        update_supporter_panel()


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

        load_account_data(
            data.user
        )

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

def leaderboard_name(player):

    player_name = player.username

    if bool(
        getattr(
            player,
            "supporter_tag",
            False
        )
    ):
        player_name += " ★"

    return player_name


def leaderboard_bonus(player):

    if bool(
        getattr(
            player,
            "supporter_bonus",
            False
        )
    ):
        return " [BONUS]"

    return ""


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

    wins_html = ""

    for index, player in enumerate(
        data.wins
    ):

        player_name = (
            leaderboard_name(player)
        )

        bonus = (
            leaderboard_bonus(player)
        )

        wins_html += (
            '<div class="leaderboard-row">'
            f'<span>{index + 1}. '
            f'{player_name}'
            f'{bonus}</span>'
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

    furthest_html = ""

    for index, player in enumerate(
        data.furthest
    ):

        player_name = (
            leaderboard_name(player)
        )

        bonus = (
            leaderboard_bonus(player)
        )

        furthest_html += (
            '<div class="leaderboard-row">'
            f'<span>{index + 1}. '
            f'{player_name}'
            f'{bonus}</span>'
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

    enemy_select.innerHTML = options

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

    global min_damage
    global max_damage

    global min_heal
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
        5,
        max_damage
    )

    # Damage window always stays 10 wide.
    min_damage = max_damage - 10

    mana_regen = max(
        0,
        mana_regen
    )

    heal_rate = max(
        5,
        heal_rate
    )

    # Healing window always stays 15 wide.
    min_heal = heal_rate - 15

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

    supporter_text = ""

    if supporter:

        supporter_text = (
            "\nSupporter Access: ACTIVE"
        )

        if supporter_bonus:
            supporter_text += (
                "\nSupporter Bonus: ON (+40% upgrades)"
            )
        else:
            supporter_text += (
                "\nSupporter Bonus: OFF"
            )

    display(f"""
========================
       ROGUELIKE
========================

Welcome, {name}.

Fight through every enemy.
Choose an upgrade after each victory.

Your leaderboard progress will be
saved automatically.
{supporter_text}
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

    global min_damage
    global max_damage

    global min_heal
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

    min_damage = 5
    max_damage = 15

    min_heal = 5
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

    supporter_text = ""

    if (
        supporter
        and supporter_bonus
    ):

        supporter_text = (
            "\nSupporter Bonus: +40% upgrades"
        )

    display(f"""
========================
       {name}
========================

Round:      {enemy_number + 1}
HP:         {max(health, 0)}/{max_health}
Mana:       {mana}/{max_mana}
Mana Regen: {mana_regen}/turn
Damage:     {min_damage}-{max_damage}
Heal Rate:  {min_heal}-{heal_rate}
{supporter_text}


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
        min_damage,
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
        min_heal,
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
# UPGRADE HELPERS
# ==========================================

def mana_upgrade_multiplier():

    if (
        supporter
        and supporter_bonus
    ):
        return 1.40

    return 1.25


def damage_upgrade_multiplier():

    if (
        supporter
        and supporter_bonus
    ):
        return 1.40

    return 1.15


def heal_upgrade_multiplier():

    if (
        supporter
        and supporter_bonus
    ):
        return 1.40

    return 1.25


def regen_upgrade_multiplier():

    if (
        supporter
        and supporter_bonus
    ):
        return 1.40

    return 1.25


def upgrade_percent(multiplier):

    return round(
        (multiplier - 1) * 100
    )


# ==========================================
# UPGRADE SCREEN
# ==========================================

def show_upgrade(message=""):

    mana_multiplier = (
        mana_upgrade_multiplier()
    )

    damage_multiplier = (
        damage_upgrade_multiplier()
    )

    heal_multiplier = (
        heal_upgrade_multiplier()
    )

    regen_multiplier = (
        regen_upgrade_multiplier()
    )

    mana_percent = upgrade_percent(
        mana_multiplier
    )

    damage_percent = upgrade_percent(
        damage_multiplier
    )

    heal_percent = upgrade_percent(
        heal_multiplier
    )

    regen_percent = upgrade_percent(
        regen_multiplier
    )

    new_mana = max(
        max_mana + 1,
        round(
            max_mana *
            mana_multiplier
        )
    )

    new_max_damage = max(
        max_damage + 1,
        round(
            max_damage *
            damage_multiplier
        )
    )

    # Minimum follows maximum so the
    # damage roll window always stays 10.
    new_min_damage = new_max_damage - 10

    new_max_heal = max(
        heal_rate + 1,
        round(
            heal_rate *
            heal_multiplier
        )
    )

    # Minimum follows maximum so the
    # healing roll window always stays 15.
    new_min_heal = new_max_heal - 15

    new_regen = max(
        mana_regen + 1,
        round(
            mana_regen *
            regen_multiplier
        )
    )

    bonus_text = ""

    if (
        supporter
        and supporter_bonus
    ):

        bonus_text = (
            "\n★ SUPPORTER BONUS ACTIVE ★\n"
        )

    display(f"""
{message}

========================
    CHOOSE AN UPGRADE
========================
{bonus_text}
MAX MANA +{mana_percent}%
{max_mana} -> {new_mana}

DAMAGE +{damage_percent}%
{min_damage}-{max_damage}
->
{new_min_damage}-{new_max_damage}

HEALING +{heal_percent}%
{min_heal}-{heal_rate}
->
{new_min_heal}-{new_max_heal}

MANA REGEN +{regen_percent}%
{mana_regen}/turn -> {new_regen}/turn
""")

    controls(f"""
        <button py-click="upgrade_mana">
            MANA +{mana_percent}%
        </button>

        <button py-click="upgrade_damage">
            DAMAGE +{damage_percent}%
        </button>

        <button py-click="upgrade_heal">
            HEALING +{heal_percent}%
        </button>

        <button py-click="upgrade_regen">
            MANA REGEN +{regen_percent}%
        </button>
    """)


# ==========================================
# MANA UPGRADE
# ==========================================

def upgrade_mana(event=None):

    global max_mana
    global mana

    multiplier = (
        mana_upgrade_multiplier()
    )

    max_mana = max(
        max_mana + 1,
        round(
            max_mana *
            multiplier
        )
    )

    mana = max_mana

    next_enemy()


# ==========================================
# DAMAGE UPGRADE
# ==========================================

def upgrade_damage(event=None):

    global min_damage
    global max_damage
    global mana

    multiplier = (
        damage_upgrade_multiplier()
    )

    max_damage = max(
        max_damage + 1,
        round(
            max_damage *
            multiplier
        )
    )

    # Keep the damage range exactly 10 wide.
    min_damage = max_damage - 10

    mana = max_mana

    next_enemy()


# ==========================================
# HEAL UPGRADE
# ==========================================

def upgrade_heal(event=None):

    global min_heal
    global heal_rate
    global mana

    multiplier = (
        heal_upgrade_multiplier()
    )

    heal_rate = max(
        heal_rate + 1,
        round(
            heal_rate *
            multiplier
        )
    )

    # Keep the healing range exactly 15 wide.
    min_heal = heal_rate - 15

    mana = max_mana

    next_enemy()


# ==========================================
# MANA REGEN UPGRADE
# ==========================================

def upgrade_regen(event=None):

    global mana_regen
    global mana

    multiplier = (
        regen_upgrade_multiplier()
    )

    mana_regen = max(
        mana_regen + 1,
        round(
            mana_regen *
            multiplier
        )
    )

    mana = max_mana

    next_enemy()


# ==========================================
# NEXT ENEMY
# ==========================================

def next_enemy():

    global enemy_number

    global max_health
    global health

    global mana

    # Every completed round gives
    # a permanent +25 maximum HP.
    max_health += 25

    # Recover 25%-75% of the new max HP.
    min_recovery = max(
        1,
        round(max_health * 0.25)
    )

    max_recovery = max(
        min_recovery,
        round(max_health * 0.75)
    )

    recovered_health = randint(
        min_recovery,
        max_recovery
    )

    health += recovered_health

    if health > max_health:
        health = max_health

    mana = max_mana

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

    bonus_text = ""

    if (
        supporter
        and supporter_bonus
    ):

        bonus_text = (
            "\nSupporter Bonus: ACTIVE"
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
Damage:      {min_damage}-{max_damage}
Heal Rate:   {min_heal}-{heal_rate}
{bonus_text}

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

    bonus_text = ""

    if (
        supporter
        and supporter_bonus
    ):

        bonus_text = (
            "\nSupporter Bonus: ACTIVE"
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
Damage:      {min_damage}-{max_damage}
Heal Rate:   {min_heal}-{heal_rate}
{bonus_text}

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

