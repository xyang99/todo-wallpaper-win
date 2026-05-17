import json
import sys
import subprocess
import time
from pathlib import Path
from urllib.parse import unquote

from paths import TODO_FILE, WALLPAPER_FILE, ensure_migration
# Ensure migration from repository to XDG locations
PROJECT_DIR = Path(__file__).parent.resolve()
ensure_migration(PROJECT_DIR)


def _migrate_data(raw_data) -> dict:
    """Migrate old array format to new dict format with metadata."""
    if isinstance(raw_data, list):
        # Old format: just an array of tasks
        return {"tasks": raw_data, "wallpaper_path": None}
    elif isinstance(raw_data, dict):
        # Already in new format
        if "tasks" not in raw_data:
            return {"tasks": [], "wallpaper_path": None}
        return raw_data
    return {"tasks": [], "wallpaper_path": None}


def _load_raw_data() -> dict:
    """Load raw data from JSON file (internal)."""
    if not TODO_FILE.exists():
        return {"tasks": [], "wallpaper_path": None}

    try:
        with open(TODO_FILE, "r", encoding="utf-8") as file:
            content = file.read().strip()
            if not content:
                return {"tasks": [], "wallpaper_path": None}
            raw_data = json.loads(content)
            return _migrate_data(raw_data)
    except json.JSONDecodeError:
        return {"tasks": [], "wallpaper_path": None}


def _save_raw_data(data: dict) -> None:
    """Save raw data to JSON file (internal)."""
    with open(TODO_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


def load_todos() -> list[str]:
    """Load list of tasks."""
    data = _load_raw_data()
    return data.get("tasks", [])


def save_todos(todos: list[str]) -> None:
    """Save list of tasks while preserving metadata."""
    data = _load_raw_data()
    data["tasks"] = todos
    _save_raw_data(data)


def load_wallpaper_path() -> str | None:
    """Load stored original wallpaper path."""
    data = _load_raw_data()
    return data.get("wallpaper_path")


def save_wallpaper_path(path: str | None) -> None:
    """Save original wallpaper path."""
    data = _load_raw_data()
    data["wallpaper_path"] = path
    _save_raw_data(data)


def set_gnome_wallpaper(image_path: Path) -> bool:
    """Set wallpaper using GNOME gsettings."""
    try:
        file_uri = f"file://{image_path.resolve()}"
        subprocess.run(
            [
                "gsettings",
                "set",
                "org.gnome.desktop.background",
                "picture-uri",
                file_uri,
            ],
            check=True,
            capture_output=True,
        )
        # Also set picture-uri-dark for GNOME 42+
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
    """Set wallpaper using feh (fallback for other desktop environments)."""
    try:
        subprocess.run(
            [
                "feh",
                "--bg-fill",
                str(image_path),
            ],
            check=True,
            capture_output=True,
        )
        return True
    except FileNotFoundError:
        return False
    except subprocess.CalledProcessError:
        return False


def get_current_wallpaper() -> str | None:
    """Get current wallpaper path from GNOME gsettings or feh cache."""
    # Try GNOME gsettings first
    try:
        result = subprocess.run(
            [
                "gsettings",
                "get",
                "org.gnome.desktop.background",
                "picture-uri",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        # gsettings returns quoted string like "'file:///path/to/image'"
        wallpaper_uri = result.stdout.strip().strip("'\"")
        if wallpaper_uri:
            # If it's a file URI, convert to a path string; don't require the file to exist
            if wallpaper_uri.startswith("file://"):
                return wallpaper_uri[7:]
            return wallpaper_uri
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    # Try feh cache as fallback
    try:
        feh_cache = Path.home() / ".fehbg"
        if feh_cache.exists():
            with open(feh_cache, "r") as f:
                content = f.read()
                # feh cache has format: feh --bg-fill '/path/to/image'
                # Extract path between quotes
                start = content.find("'")
                end = content.rfind("'")
                if start >= 0 and end > start:
                    path = content[start + 1 : end]
                    return path
    except (OSError, IOError):
        pass

    return None


def render() -> None:
    try:
        result = subprocess.run(
            [sys.executable, str(PROJECT_DIR / "render.py")],
            capture_output=True,
            text=True,
            check=True,
            cwd=str(PROJECT_DIR),
        )
        print(result.stdout.strip())
    except subprocess.CalledProcessError as e:
        print(f"✗ Render failed: {e.stderr}")
        exit(1)

    # Small delay to ensure file is written before setting wallpaper
    time.sleep(0.5)

    # Try GNOME first, then fall back to feh
    if set_gnome_wallpaper(WALLPAPER_FILE):
        print("✓ Wallpaper set (GNOME)")
    elif set_feh_wallpaper(WALLPAPER_FILE):
        print("✓ Wallpaper set (feh)")
    else:
        print("✗ Failed to set wallpaper")
        print("  Install gsettings (GNOME) or feh: sudo apt install gnome-shell feh")
        exit(1)


def render_done_wallpaper() -> bool:
    """Render and apply the fallback 'All Tasks Done!' wallpaper."""
    result = subprocess.run(
        [sys.executable, str(PROJECT_DIR / "render.py"), "--done"],
        capture_output=True,
        text=True,
        check=False,
        cwd=str(PROJECT_DIR),
    )
    if result.returncode != 0:
        print("✗ Failed to generate 'all tasks done' image")
        return False

    time.sleep(0.5)
    if set_gnome_wallpaper(WALLPAPER_FILE):
        print("✓ Wallpaper set to 'All Tasks Done!' (GNOME)")
        return True
    if set_feh_wallpaper(WALLPAPER_FILE):
        print("✓ Wallpaper set to 'All Tasks Done!' (feh)")
        return True

    print("✗ Failed to set wallpaper")
    return False


def restore_wallpaper(wallpaper_path: str) -> bool:
    """Restore wallpaper from stored path."""
    path = Path(wallpaper_path)
    if not path.exists():
        return False

    if set_gnome_wallpaper(path):
        return True
    elif set_feh_wallpaper(path):
        return True
    return False


def sync_wallpaper() -> None:
    """Apply the current todo state to the desktop wallpaper."""
    todos = load_todos()
    if todos:
        render()
        return

    stored_wallpaper = load_wallpaper_path()
    if stored_wallpaper:
        restored_path = Path(unquote(stored_wallpaper))
        if restored_path.exists() and restore_wallpaper(stored_wallpaper):
            save_wallpaper_path(None)
            print("✓ Wallpaper restored to original")
            return

        save_wallpaper_path(None)

    render_done_wallpaper()


def add_todo(text: str) -> None:
    # Step 1: Check if list is empty
    todos = load_todos()
    is_first_task = len(todos) == 0

    # Step 2: If empty, record current wallpaper path
    if is_first_task:
        current_wallpaper = get_current_wallpaper()
        if current_wallpaper:
            save_wallpaper_path(current_wallpaper)
            print(f"✓ Stored original wallpaper: {current_wallpaper}")

    # Step 3-4: Add task and generate/update wallpaper
    todos.append(text)
    save_todos(todos)
    print(f"✓ Added: {text}")
    render()


def remove_todo(index: int) -> None:
    todos = load_todos()
    todo_index = index - 1

    if todo_index < 0 or todo_index >= len(todos):
        print(f"✗ Invalid index: {index} (you have {len(todos)} todos)")
        exit(1)

    removed = todos.pop(todo_index)
    save_todos(todos)
    print(f"✓ Removed: {removed}")

    # Check if list is now empty
    if len(todos) == 0:
        sync_wallpaper()
    else:
        # List not empty, normal render
        render()


def list_todos() -> None:
    todos = load_todos()

    for index, todo in enumerate(todos, start=1):
        print(f"{index}: {todo}")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 todo.py [add|remove|list] [args]")
        print("  add TEXT     - Add a new todo")
        print("  remove IDX   - Remove todo by 1-based index")
        print("  list         - Show all todos")
        print("  sync         - Re-apply the current wallpaper state")
        print("  init         - Set up wallpaper autostart")
        exit(1)

    command = sys.argv[1]

    if command == "add":
        if len(sys.argv) < 3:
            print("✗ add requires text: python3 todo.py add 'Your task'")
            exit(1)
        add_todo(" ".join(sys.argv[2:]))

    elif command == "remove":
        if len(sys.argv) < 3:
            print("✗ remove requires index: python3 todo.py remove 1")
            exit(1)
        try:
            remove_todo(int(sys.argv[2]))
        except ValueError:
            print(f"✗ Invalid index: not a number")
            exit(1)

    elif command == "list":
        list_todos()

    elif command == "init":
        from init import main as init_main

        exit(init_main())

    elif command == "sync":
        sync_wallpaper()

    else:
        print(f"✗ Unknown command: {command}")
        exit(1)


if __name__ == "__main__":
    main()