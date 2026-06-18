# main.py
import sys
import os

if getattr(sys, 'frozen', False):
    os.chdir(sys._MEIPASS)

from ursina import Ursina
import ursina

if getattr(sys, 'frozen', False):
    from pathlib import Path
    ursina.application.asset_folder = Path(sys._MEIPASS)
    from panda3d.core import getModelPath
    getModelPath().append_path(sys._MEIPASS)

import func

app = Ursina()
func.setup(app)

def input(key):
    """Weiterleitung der Eingabe an func.input."""
    func.input(key)

def update():
    """Weiterleitung des Updates an func.update."""
    func.update()

app.run()
