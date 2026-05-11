# todo.py

from pathlib import Path
import json
import subprocess
import sys
import time

# Use absolute paths to work correctly when called from subprocess
PROJECT_DIR = Path(__file__).parent.resolve()
TODO_FILE = PROJECT_DIR / "todos.json"
WALLPAPER_FILE = PROJECT_DIR / "wallpaper.png"


def load_todos() -> list[str]:
    if not TODO_FILE.exists():
        return []

    try:
        with open(TODO_FILE, "r", encoding="utf-8") as file:
            content = file.read().strip()
            if not content:
                return []
            return json.loads(content)
    except json.JSONDecodeError:
        return []


def save_todos(todos: list[str]) -> None:
    with open(TODO_FILE, "w", encoding="utf-8") as file:
        json.dump(todos, file, indent=2)


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


def add_todo(text: str) -> None:
    todos = load_todos()
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

    else:
        print(f"✗ Unknown command: {command}")
        exit(1)


if __name__ == "__main__":
    main()