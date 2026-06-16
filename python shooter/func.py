# func.py
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import sys
import os
import random
import json

state = {
    'log_file_path': "game_log.txt",
    'highscore_file': "highscores.json",
    'max_highscores': 10,
    'enemy_count': 5,
    'logger': None,
    'enemies': [],
    'game_over': False,
    'score': 0,
    'elapsed_time': 0,
    'ground': None,
    'player': None,
    'weapon': None,
    'menu_visible': False,
    'pause_menu': None,
    'menu_bg': None,
    'game_over_entity': None,
    'overlay_bg': None,
    'lose_text': None,
    'name_input': None,
    'submit_button': None,
    'highscore_text': None,
    'restart_button': None,
    'game_over_quit_button': None,
    'score_text': None,
    'shoot_sound': None,
    'hit_sound': None,
    'die_sound': None,
    'step_sound': None,
}

# ── Highscores ────────────────────────────────────────────────────────────────

def load_highscores():
    """Lädt die Highscores aus der JSON-Datei.

    Returns:
        list: Liste von Highscore-Einträgen (je ein Dict mit 'name' und 'score').
              Bei Fehler oder fehlender Datei wird eine leere Liste zurückgegeben.
    """
    if os.path.isfile(state['highscore_file']):
        try:
            with open(state['highscore_file'], "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Fehler beim Laden der Highscores: {e}")
    return []


def save_highscores(scores):
    """Speichert die Highscores in die JSON-Datei.

    Args:
        scores (list): Liste von Highscore-Einträgen zum Speichern.
    """
    try:
        with open(state['highscore_file'], "w", encoding="utf-8") as f:
            json.dump(scores, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Fehler beim Speichern der Highscores: {e}")


def add_highscore(name, points):
    """Fügt einen neuen Highscore-Eintrag hinzu und aktualisiert die Liste.

    Args:
        name (str): Name des Spielers.
        points (int): Erzielte Punktzahl.

    Returns:
        list: Aktualisierte Top-10-Highscores.
    """
    scores = load_highscores()
    scores.append({"name": name, "score": points})
    scores.sort(key=lambda x: x["score"], reverse=True)
    scores = scores[:state['max_highscores']]
    save_highscores(scores)
    return scores


def format_top10(scores):
    """Formatiert die Highscore-Liste zu einem lesbaren String.

    Args:
        scores (list): Liste von Highscore-Einträgen.

    Returns:
        str: Formatierter String mit Platzierungen und Punkten.
    """
    lines = ["Top 10:"]
    for i, entry in enumerate(scores, start=1):
        lines.append(f"{i}. {entry['name']} – {entry['score']}")
    return "\n".join(lines)

# ── Enemies ───────────────────────────────────────────────────────────────────

def spawn_enemy():
    """Erstellt einen neuen Feind zufällig in der Spielwelt und fügt ihn der Feindeliste hinzu."""
    enemy = Entity(
        model="cube",
        color=color.red,
        scale=1,
        position=Vec3(random.uniform(-20, 20), 0.5, random.uniform(-20, 20)),
        collider="box",
    )
    state['enemies'].append(enemy)


def respawn_enemies():
    """Stellt sicher, dass die gewünschte Anzahl an Feinden vorhanden ist, indem neue erzeugt werden."""
    while len(state['enemies']) < state['enemy_count']:
        spawn_enemy()

# ── Menu ──────────────────────────────────────────────────────────────────────

def toggle_menu():
    """Schaltet das Pause-Menü ein oder aus und passt den Mauszeiger und Spielerstatus an."""
    state['menu_visible'] = not state['menu_visible']
    state['pause_menu'].enabled = state['menu_visible']
    mouse.visible = state['menu_visible']
    if state['menu_visible']:
        state['player'].disable()
    else:
        state['player'].enable()
    print("Menü " + ("geöffnet" if state['menu_visible'] else "geschlossen"))

# ── Score ─────────────────────────────────────────────────────────────────────

def update_score_text():
    """Aktualisiert die Score-Anzeige im UI mit dem aktuellen Punktestand."""
    state['score_text'].text = f"Score: {state['score']}"

# ── Game flow ─────────────────────────────────────────────────────────────────

def submit_score():
    """Speichert den aktuellen Spielstand als Highscore, wenn ein Name eingegeben wurde."""
    player_name = state['name_input'].text.strip() or "Anonymous"
    top_scores = add_highscore(player_name, state['score'])
    state['highscore_text'].text = format_top10(top_scores)
    state['name_input'].enabled = False
    state['submit_button'].enabled = False
    state['restart_button'].enabled = True
    state['game_over_quit_button'].enabled = True


def restart_game():
    """Setzt den Spielzustand zurück für ein neues Spiel."""
    for e in state['enemies']:
        destroy(e)
    state['enemies'].clear()
    respawn_enemies()

    state['game_over'] = False
    state['score'] = 0
    state['elapsed_time'] = 0
    update_score_text()

    state['game_over_entity'].enabled = False
    state['name_input'].text = ""
    state['name_input'].enabled = True
    state['submit_button'].enabled = True
    state['highscore_text'].text = ""
    state['restart_button'].enabled = False
    state['game_over_quit_button'].enabled = False

    state['player'].position = Vec3(0, 1, 0)
    state['player'].enable()
    print("Neues Spiel gestartet.")

# ── Sound ─────────────────────────────────────────────────────────────────────

def load_sound(path):
    """Lädt eine Sounddatei, falls sie existiert.

    Args:
        path (str): Pfad zur Sounddatei.

    Returns:
        Audio oder None: Audio-Objekt bei Erfolg, None bei Fehler oder fehlender Datei.
    """
    if os.path.isfile(path):
        try:
            return Audio(path, autoplay=False)
        except Exception as e:
            print(f"Sound '{path}' konnte nicht geladen werden: {e}")
    return None

# ── Shooting ──────────────────────────────────────────────────────────────────

def shoot():
    """Verarbeitet einen Schuss: Waffe animieren, Sound abspielen, Trefferprüfung und Projektilerzeugung."""
    from classes import Projectile

    if state['game_over']:
        return

    # Rückstoß-Animation
    state['weapon'].animate_position(Vec2(0.5, -0.35), duration=0.05, curve=curve.out_quad)
    invoke(
        lambda: state['weapon'].animate_position(Vec2(0.5, -0.4), duration=0.1, curve=curve.in_quad),
        delay=0.06,
    )

    if state['shoot_sound']:
        state['shoot_sound'].play()

    # Sofort-Raycast
    hit_info = raycast(
        camera.world_position, camera.forward,
        distance=100, ignore=[state['player'], state['weapon']],
    )
    if hit_info.hit and hit_info.entity in state['enemies']:
        if state['hit_sound']:
            state['hit_sound'].play()
        print(f"Direkter Treffer: {hit_info.entity}")
        destroy(hit_info.entity)
        state['enemies'].remove(hit_info.entity)
        state['score'] += 1
        update_score_text()
        spawn_enemy()
        return

    # Projektil erzeugen, falls kein Sofortreffer
    Projectile(
        position=camera.world_position + camera.forward * 0.5,
        direction=camera.forward,
    )

# ── Ursina hooks ─────────────────────────────────────────────────────────────

def input(key):
    """Ursina-Eingabehook: Verarbeitet Mausklicks und Escape-Taste.

    Args:
        key (str): Name der gedrückten Taste oder Mausereignis.
    """
    if key == "left mouse down" and not state['menu_visible']:
        shoot()
    if key == "escape":
        toggle_menu()


def update():
    """Ursina-Update-Schleife: Spiellogik pro Frame."""
    if state['menu_visible'] or state['game_over']:
        return

    state['elapsed_time'] += time.dt

    # Schrittgeräusch
    if state['step_sound'] and any(held_keys[k] for k in ("w", "a", "s", "d")):
        if not state['step_sound'].playing:
            state['step_sound'].play()

    base_speed = 2 + state['elapsed_time'] * 0.5

    for enemy in state['enemies']:
        direction_to_player = (state['player'].position - enemy.position).normalized()
        enemy.position += direction_to_player * time.dt * base_speed

        # Weltgrenzen
        if enemy.x >  25: enemy.x = -25
        if enemy.x < -25: enemy.x =  25
        if enemy.z >  25: enemy.z = -25
        if enemy.z < -25: enemy.z =  25

        # Kollision Spieler ↔ Gegner
        if distance(state['player'].position, enemy.position) < 1.5:
            state['game_over'] = True
            state['player'].disable()
            state['game_over_entity'].enabled = True
            if state['die_sound']:
                state['die_sound'].play()
            print("Spieler getroffen – Game Over")
            break

# ── Setup ─────────────────────────────────────────────────────────────────────

def setup(app):
    """Initialisiert das Spiel: Logger, Ground, Player, Weapon, Sounds, Menüs und Score-Anzeige."""
    from classes import Logger

    # Logging
    state['logger'] = Logger(state['log_file_path'])
    sys.stdout = state['logger']
    sys.stderr = sys.stdout
    print("Logging initialisiert.")

    # Ground
    state['ground'] = Entity(
        model="plane",
        scale=(50, 1, 50),
        texture=load_texture("white_cube"),
        texture_scale=(50, 50),
        collider="box",
        position=(0, -0.5, 0),
    )

    # Player
    state['player'] = FirstPersonController()
    state['player'].cursor.visible = False

    # Weapon
    state['weapon'] = Entity(
        parent=camera.ui,
        model="cube",
        color=color.gray,
        scale=(0.2, 0.05, 1),
        position=Vec2(0.5, -0.4),
        origin=(-0.5, -0.5),
    )

    # Sounds
    state['shoot_sound'] = load_sound("shoot1.wav")
    state['hit_sound']   = load_sound("explode5.wav")
    state['die_sound']   = load_sound("die-sound.wav")
    state['step_sound']  = load_sound("step5.wav")

    # Pause-Menü
    state['pause_menu'] = Entity(parent=camera.ui, enabled=False)
    state['menu_bg'] = Entity(
        parent=state['pause_menu'],
        model="quad",
        color=color.rgba(0, 0, 0, 180),
        scale=(0.6, 0.4),
        position=Vec2(0, 0),
    )
    Button(text="Weiter",  parent=state['pause_menu'], color=color.azure,
           scale=(0.3, 0.1), position=Vec2(0,  0.07), on_click=toggle_menu)
    Button(text="Beenden", parent=state['pause_menu'], color=color.red,
           scale=(0.3, 0.1), position=Vec2(0, -0.07), on_click=application.quit)

    # Game-Over Overlay
    state['game_over_entity'] = Entity(parent=camera.ui, enabled=False)
    state['overlay_bg'] = Entity(
        parent=state['game_over_entity'],
        model="quad",
        color=color.rgba(0, 0, 0, 200),
        scale=(1.2, 0.8),
        position=Vec2(0, 0),
    )
    state['lose_text'] = Text(
        parent=state['game_over_entity'],
        text="YOU LOST\nGib deinen Namen ein:",
        origin=(0, 0),
        color=color.white,
        scale=2,
        position=Vec2(0, 0.25),
    )
    state['name_input'] = InputField(
        parent=state['game_over_entity'],
        default_value="",
        character_limit=12,
        position=Vec2(0, 0),
        scale=(0.5, 0.07),
        color=color.gray,
    )
    state['submit_button'] = Button(
        text="Eintragen",
        parent=state['game_over_entity'],
        color=color.azure,
        scale=(0.3, 0.1),
        position=Vec2(0, -0.15),
        on_click=submit_score,
    )
    state['highscore_text'] = Text(
        parent=state['game_over_entity'],
        text="",
        origin=(0, 0),
        color=color.yellow,
        scale=1.5,
        position=Vec2(0, -0.35),
    )
    state['restart_button'] = Button(
        parent=state['game_over_entity'],
        text="Neues Spiel",
        color=color.green,
        scale=(0.3, 0.08),
        position=Vec2(-0.2, -0.45),
        enabled=False,
        on_click=restart_game,
    )
    state['game_over_quit_button'] = Button(
        parent=state['game_over_entity'],
        text="Beenden",
        color=color.red,
        scale=(0.3, 0.08),
        position=Vec2(0.2, -0.45),
        enabled=False,
        on_click=application.quit,
    )

    # Score-Anzeige
    state['score_text'] = Text(
        text="Score: 0",
        parent=camera.ui,
        origin=(0.5, -0.5),
        position=window.top_right + Vec2(-0.02, -0.02),
        color=color.white,
        scale=1.5,
    )

    respawn_enemies()
