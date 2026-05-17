# render.py

from pathlib import Path
import json

from PIL import Image, ImageDraw, ImageFont

WIDTH = 1920
HEIGHT = 1080

BACKGROUND = (20, 20, 30)
TEXT = (240, 240, 240)
ACCENT = (120, 200, 255)

from paths import TODO_FILE, OUTPUT, ensure_migration
# Ensure migration from repository to XDG locations
ensure_migration(Path(__file__).parent.resolve())


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


def render_wallpaper(todos: list[str]) -> None:
    image = Image.new("RGB", (WIDTH, HEIGHT), BACKGROUND)

    draw = ImageDraw.Draw(image)

    font = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        36,
    )

    title_font = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        54,
    )

    draw.text(
        (80, 60),
        "TODO",
        fill=ACCENT,
        font=title_font,
    )

    y = 180

    for index, todo in enumerate(todos, start=1):
        draw.text(
            (100, y),
            f"{index}. {todo}",
            fill=TEXT,
            font=font,
        )

        y += 60

    image.save(OUTPUT)


def render_all_tasks_done() -> None:
    """Render a celebratory 'All Tasks Done!' image."""
    image = Image.new("RGB", (WIDTH, HEIGHT), BACKGROUND)
    draw = ImageDraw.Draw(image)

    title_font = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        72,
    )

    subtitle_font = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        48,
    )

    # Main message
    draw.text(
        (960, 300),
        "All Tasks Done!",
        fill=ACCENT,
        font=title_font,
        anchor="mm",
    )

    # Subtitle
    draw.text(
        (960, 500),
        "Take a break, you've earned it! ✨",
        fill=TEXT,
        font=subtitle_font,
        anchor="mm",
    )

    image.save(OUTPUT)


def main() -> None:
    try:
        # Check if --done flag is passed to render "all tasks done" image
        import sys
        if len(sys.argv) > 1 and sys.argv[1] == "--done":
            render_all_tasks_done()
            print("✓ 'All Tasks Done!' image rendered")
        else:
            todos = load_todos()
            render_wallpaper(todos)
            print(f"✓ Wallpaper rendered ({len(todos)} todos)")
    except FileNotFoundError as e:
        print(f"✗ Font not found: {e}")
        print("  Install DejaVuSans font: sudo apt install fonts-dejavu")
        exit(1)
    except Exception as e:
        print(f"✗ Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()