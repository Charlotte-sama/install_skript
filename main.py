import json
import requests
import os
import subprocess
import ctypes
import sys

def run_as_admin():
    # Prüfen, ob bereits Admin
    try:
        is_admin = (os.getuid() == 0)
    except AttributeError:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0

    # Falls bereits Admin: weiterlaufen
    if is_admin:
        return True

    # Falls NICHT Admin → neu starten als Admin
    print("🔐 Starte Script mit Administratorrechten neu...")

    params = " ".join([f'"{arg}"' for arg in sys.argv])
    try:
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, params, None, 1
        )
    except Exception as e:
        print(f"❌ Admin-Anforderung fehlgeschlagen: {e}")
        return False

    sys.exit()  # Wichtig: altes (nicht-admin) Script beenden

run_as_admin()

# Config laden
with open("config\\settings.json") as f:
    config = json.load(f)

install_path = config["variables"]["installPath"]
os.makedirs(install_path, exist_ok=True)

def download_app(app, path):
    print(f"\nLade {app['name']} herunter...")
    r = requests.get(app["url"], stream=True)

    file_path = os.path.join(path, app["setup_name"])

    with open(file_path, "wb") as f_out:
        for chunk in r.iter_content(1024):
            f_out.write(chunk)

    print(f"{app['name']} erfolgreich heruntergeladen! -> {file_path}")
    return file_path


def run_installer(file_path):
    print(f"Starte Installer: {file_path}")

    try:
        if file_path.endswith(".exe"):
            subprocess.run([file_path], check=True)
        elif file_path.endswith(".msi"):
            subprocess.run(["msiexec", "/i", file_path], check=True)
        else:
            print("⚠ Unbekanntes Format – kann nicht automatisch installiert werden.")
            return

        print("Installation abgeschlossen!")
    except Exception as e:
        print(f"❌ Fehler beim Ausführen: {e}")


print("Starte Verarbeitung...\n")

for app in config["variables"]["apps"]:

    # Programme überspringen
    if not app.get("install", False):
        print(f"⏭ Überspringe {app['name']} (install=false)")
        continue

    # Download
    file_path = download_app(app, install_path)

    # Installer ausführen
    run_installer(file_path)

print("\nAlle Aufgaben abgeschlossen!")
