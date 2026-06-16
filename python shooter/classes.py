# classes.py
import sys
import datetime
from ursina import *


class Logger:
    """Logger-Klasse zur gleichzeitigen Ausgabe auf Terminal und in Logdatei."""
    def __init__(self, filename):
        """Initialisiert den Logger mit einer Logdatei.

        Args:
            filename (str): Pfad zur Logdatei.
        """
        self.terminal = sys.__stdout__
        self.log = open(filename, "a", encoding="utf-8")
        self.write(f"\n--- Spielstart: {datetime.datetime.now()} ---\n")

    def write(self, message):
        """Schreibt eine Nachricht sowohl ins Terminal als auch ins Logfile.

        Args:
            message (str): Zu schreibende Nachricht.
        """
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        """Leert die Puffer von Terminal und Logfile."""
        self.terminal.flush()
        self.log.flush()


class Projectile(Entity):
    """Projektil-Klasse für Schüsse des Spielers."""
    def __init__(self, **kwargs):
        """Initialisiert ein Projektil mit Richtung und Standardwerten.

        Args:
            **kwargs: Schlüsselwortargumente für Entity, einschließlich 'direction'.
        """
        direction = kwargs.pop("direction", Vec3(0, 0, 1))
        super().__init__(
            model="sphere",
            color=color.yellow,
            scale=0.1,
            origin_y=-0.5,
            collider="box",
            **kwargs,
        )
        self.direction = direction.normalized()
        self.speed = 50
        self.lifetime = 2

    def update(self):
        """Aktualisiert die Projektilposition, Lebensdauer und Kollisionserkennung."""
        from func import state, update_score_text, spawn_enemy

        self.position += self.direction * time.dt * self.speed
        self.lifetime -= time.dt

        if self.lifetime <= 0:
            destroy(self)
            return

        hit_info = self.intersects()
        if hit_info.hit and hit_info.entity in state["enemies"]:
            if state["hit_sound"]:
                state["hit_sound"].play()
            print(f"Treffer: {hit_info.entity}")
            destroy(hit_info.entity)
            state["enemies"].remove(hit_info.entity)
            state["score"] += 1
            update_score_text()
            spawn_enemy()
            destroy(self)
