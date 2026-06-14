import ctypes
import json
import platform
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import unquote

from paths import TODO_FILE, WALLPAPER_FILE, ensure_migration

PROJECT_DIR = Path(__file__).parent.resolve()
ensure_migration(PROJECT_DIR)


def _migrate_data(raw_data) -> dict:
    if isinstance(raw_data, list):
        return {"tasks": raw_data, "wallpaper_path": None}
    if isinstance(raw_data, dict):
        if "tasks" not in raw_data:
            return {"tasks": [], "wallpaper_path": None}
        return raw_data
    return {"tasks": [], "wallpaper_path": None}


def _load_raw_data() -> dict:
    if not TODO_FILE.exists():
        return {"tasks": [], "wallpaper_path": None}

    try:
        with open(TODO_FILE, "r", encoding="utf-8") as file:
            content = file.read().strip()
            if not content:
                return {"tasks": [], "wallpaper_path": None}
            return _migrate_data(json.loads(content))
    except json.JSONDecodeError:
        return {"tasks": [], "wallpaper_path": None}


def _save_raw_data(data: dict) -> None:
    TODO_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(TODO_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


def load_todos() -> list[str]:
    return _load_raw_data().get("tasks", [])


def save_todos(todos: list[str]) -> None:
    data = _load_raw_data()
    data["tasks"] = todos
    _save_raw_data(data)


def load_wallpaper_path() -> str | None:
    return _load_raw_data().get("wallpaper_path")


def save_wallpaper_path(path: str | None) -> None:
    data = _load_raw_data()
    data["wallpaper_path"] = path
    _save_raw_data(data)


def set_windows_wallpaper(image_path: Path) -> bool:
    SPI_SETDESKWALLPAPER = 20
    SPIF_UPDATEINIFILE = 0x01
    SPIF_SENDCHANGE = 0x02
    flags = SPIF_UPDATEINIFILE | SPIF_SENDCHANGE
    return bool(
        ctypes.windll.user32.SystemParametersInfoW(
            SPI_SETDESKWALLPAPER,
            0,
            str(image_path.resolve()),
            flags,
        )
    )


def get_windows_wallpaper() -> str | None:
    try:
        import winreg

        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Desktop") as key:
            value, _ = winreg.QueryValueEx(key, "WallPaper")
            return value or None
    except OSError:
        return None


def set_gnome_wallpaper(image_path: Path) -> bool:
    try:
        file_uri = f"file://{image_path.resolve()}"
        subprocess.run(
            ["gsettings", "set", "org.gnome.desktop.background", "picture-uri", file_uri],
            check=True,
            capture_output=True,
        )
        subprocess.run(
            [
                "gsettings",
                "set",
                "org.gnome.desktop.background",
                "picture-uri-dark",
                file_uri,
            ],
            check=False,
            capture_output=True,
        )
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def set_feh_wallpaper(image_path: Path) -> bool:
    try:
        subprocess.run(["feh", "--bg-fill", str(image_path)], check=True, capture_output=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def set_wallpaper(image_path: Path) -> str | None:
    system = platform.system()
    if system == "Windows":
        return "Windows" if set_windows_wallpaper(image_path) else None
    if set_gnome_wallpaper(image_path):
        return "GNOME"
    if set_feh_wallpaper(image_path):
        return "feh"
    return None


def get_linux_wallpaper() -> str | None:
    try:
        result = subprocess.run(
            ["gsettings", "get", "org.gnome.desktop.background", "picture-uri"],
            capture_output=True,
            text=True,
            check=True,
        )
        wallpaper_uri = result.stdout.strip().strip("'\"")
        if wallpaper_uri:
            if wallpaper_uri.startswith("file://"):
                return wallpaper_uri[7:]
            return wallpaper_uri
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    try:
        feh_cache = Path.home() / ".fehbg"
        if feh_cache.exists():
            with open(feh_cache, "r", encoding="utf-8") as f:
                content = f.read()
            start = content.find("'")
            end = content.rfind("'")
            if start >= 0 and end > start:
                return content[start + 1 : end]
    except OSError:
        pass

    return None


def get_current_wallpaper() -> str | None:
    if platform.system() == "Windows":
        return get_windows_wallpaper()
    return get_linux_wallpaper()


def render_image(done: bool = False) -> bool:
    args = [sys.executable, str(PROJECT_DIR / "render.py")]
    if done:
        args.append("--done")

    result = subprocess.run(
        args,
        capture_output=True,
        text=True,
        check=False,
        cwd=str(PROJECT_DIR),
    )
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.returncode != 0:
        if result.stderr.strip():
            print(result.stderr.strip())
        return False
    return True


def render() -> None:
    if not render_image():
        print("Render failed")
        exit(1)

    time.sleep(0.5)
    setter = set_wallpaper(WALLPAPER_FILE)
    if setter:
        print(f"Wallpaper set ({setter})")
        return

    print("Failed to set wallpaper")
    if platform.system() == "Windows":
        print("Try running this from a normal desktop session, not an elevated service.")
    else:
        print("Install gsettings (GNOME) or feh: sudo apt install gnome-shell feh")
    exit(1)


def render_done_wallpaper() -> bool:
    if not render_image(done=True):
        print("Failed to generate 'all tasks done' image")
        return False

    time.sleep(0.5)
    setter = set_wallpaper(WALLPAPER_FILE)
    if setter:
        print(f"Wallpaper set to 'All Tasks Done!' ({setter})")
        return True

    print("Failed to set wallpaper")
    return False


def restore_wallpaper(wallpaper_path: str) -> bool:
    path = Path(wallpaper_path)
    if not path.exists():
        return False
    return bool(set_wallpaper(path))


def sync_wallpaper() -> None:
    todos = load_todos()
    if todos:
        render()
        return

    stored_wallpaper = load_wallpaper_path()
    if stored_wallpaper:
        restored_path = Path(unquote(stored_wallpaper))
        if restored_path.exists() and restore_wallpaper(str(restored_path)):
            save_wallpaper_path(None)
            print("Wallpaper restored to original")
            return

        save_wallpaper_path(None)

    render_done_wallpaper()


def add_todo(text: str) -> None:
    todos = load_todos()
    is_first_task = len(todos) == 0

    if is_first_task:
        current_wallpaper = get_current_wallpaper()
        if current_wallpaper:
            save_wallpaper_path(current_wallpaper)
            print(f"Stored original wallpaper: {current_wallpaper}")

    todos.append(text)
    save_todos(todos)
    print(f"Added: {text}")
    render()


def remove_todo(index: int) -> None:
    todos = load_todos()
    todo_index = index - 1

    if todo_index < 0 or todo_index >= len(todos):
        print(f"Invalid index: {index} (you have {len(todos)} todos)")
        exit(1)

    removed = todos.pop(todo_index)
    save_todos(todos)
    print(f"Removed: {removed}")

    if len(todos) == 0:
        sync_wallpaper()
    else:
        render()


def list_todos() -> None:
    todos = load_todos()
    for index, todo in enumerate(todos, start=1):
        print(f"{index}: {todo}")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python todo.py [add|remove|list|sync|init] [args]")
        print("  add TEXT     - Add a new todo")
        print("  remove IDX   - Remove todo by 1-based index")
        print("  list         - Show all todos")
        print("  sync         - Re-apply the current wallpaper state")
        print("  init         - Set up wallpaper autostart")
        exit(1)

    command = sys.argv[1]

    if command == "add":
        if len(sys.argv) < 3:
            print("add requires text: python todo.py add \"Your task\"")
            exit(1)
        add_todo(" ".join(sys.argv[2:]))
    elif command == "remove":
        if len(sys.argv) < 3:
            print("remove requires index: python todo.py remove 1")
            exit(1)
        try:
            remove_todo(int(sys.argv[2]))
        except ValueError:
            print("Invalid index: not a number")
            exit(1)
    elif command == "list":
        list_todos()
    elif command == "init":
        from init import main as init_main

        exit(init_main())
    elif command == "sync":
        sync_wallpaper()
    else:
        print(f"Unknown command: {command}")
        exit(1)


if __name__ == "__main__":
    main()
