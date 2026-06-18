# build_exe.py
import os
import sys
import subprocess

def build():
    print("Starte Kompilierung für Python Shooter...")

    # 1. Sicherstellen, dass PyInstaller installiert ist
    try:
        import PyInstaller
        print("PyInstaller ist bereits installiert.")
    except ImportError:
        print("PyInstaller wird installiert...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)

    # 2. Ursina & Panda3D Pfade ermitteln
    try:
        import ursina
        import panda3d
        ursina_dir = os.path.dirname(ursina.__file__)
        panda3d_dir = os.path.dirname(panda3d.__file__)
        print(f"Ursina-Pfad gefunden: {ursina_dir}")
        print(f"Panda3D-Pfad gefunden: {panda3d_dir}")
    except ImportError:
        print("Fehler: Ursina-Engine oder Panda3D ist nicht in dieser Python-Umgebung installiert.")
        sys.exit(1)

    # 3. PyInstaller Befehl konfigurieren
    # Wir binden die Sound-Dateien, die gesamte Ursina-Engine und Panda3D ein
    cmd = [
        "pyinstaller",
        "--onefile",
        "--noconsole",
        "--name=python_shooter",
        "--add-data=die-sound.wav;.",
        "--add-data=explode5.ogg;.",
        "--add-data=shoot1.wav;.",
        "--add-data=step5.wav;.",
        f"--add-data={ursina_dir};ursina",
        f"--add-data={panda3d_dir};panda3d",
        "main.py"
    ]

    print("Führe PyInstaller aus...")
    print("Befehl:", " ".join(cmd))
    
    try:
        subprocess.run(cmd, check=True)
        print("\nErfolgreich kompiliert! Die ausführbare Datei befindet sich unter 'dist/python_shooter.exe'.")
    except subprocess.CalledProcessError as e:
        print(f"\nFehler bei der Kompilierung: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build()
