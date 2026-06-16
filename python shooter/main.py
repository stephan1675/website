# main.py
from ursina import Ursina
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
