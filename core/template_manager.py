import json
import os
import sys


def _templates_dir() -> str:
    """
    Find the templates folder intelligently:
    1. If a 'templates/' folder exists next to the EXE/script — use that (user can add files here)
    2. If running as a Nuitka onefile EXE — use the bundled templates inside it
    3. Fallback — create a templates/ folder next to the executable
    """
    # When running as Nuitka onefile, sys.argv[0] is the EXE path
    exe_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    external = os.path.join(exe_dir, "templates")

    # Priority 1: external folder next to EXE (user-editable, always wins)
    if os.path.isdir(external):
        return external

    # Priority 2: bundled inside Nuitka onefile (sys._MEIPASS equivalent for Nuitka)
    # Nuitka sets __compiled__ and uses a temp extraction dir
    if getattr(sys, "frozen", False) or "__compiled__" in dir(sys):
        # Nuitka onefile extracts to a temp dir accessible via __file__ of the main module
        try:
            import __main__
            bundle_dir = os.path.dirname(os.path.abspath(__main__.__file__))
            bundled = os.path.join(bundle_dir, "templates")
            if os.path.isdir(bundled):
                return bundled
        except Exception:
            pass

    # Priority 3: running as plain .py script (development)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dev_path = os.path.join(script_dir, "..", "templates")
    dev_path = os.path.normpath(dev_path)
    if os.path.isdir(dev_path):
        return dev_path

    # Fallback: create external folder so it works anyway
    os.makedirs(external, exist_ok=True)
    return external


def save_template(name: str, data: dict):
    folder = _templates_dir()
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, name + ".json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def load_template(name: str) -> dict:
    folder = _templates_dir()
    path = os.path.join(folder, name + ".json")
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def list_templates() -> list:
    folder = _templates_dir()
    if not os.path.isdir(folder):
        return []
    return sorted(
        f[:-5] for f in os.listdir(folder) if f.endswith(".json")
    )
