from pathlib import Path
import os
import platform
import shutil
import sys

try:
    import platformdirs
except Exception:
    platformdirs = None

APP_NAME = "todo-wallpaper"
HOME = Path.home()


def _fallback_dirs() -> tuple[Path, Path, Path, Path]:
    system = platform.system()
    if system == "Windows":
        appdata = Path(os.environ.get("APPDATA", HOME / "AppData" / "Roaming"))
        localappdata = Path(os.environ.get("LOCALAPPDATA", HOME / "AppData" / "Local"))
        data_dir = appdata / APP_NAME
        config_dir = appdata / APP_NAME
        cache_dir = localappdata / APP_NAME / "Cache"
        state_dir = localappdata / APP_NAME / "State"
        return data_dir, config_dir, cache_dir, state_dir

    data_dir = HOME / ".local" / "share" / APP_NAME
    config_dir = HOME / ".config" / APP_NAME
    cache_dir = HOME / ".cache" / APP_NAME
    state_dir = HOME / ".local" / "state" / APP_NAME
    return data_dir, config_dir, cache_dir, state_dir


if platformdirs:
    data_dir = Path(platformdirs.user_data_dir(APP_NAME))
    config_dir = Path(platformdirs.user_config_dir(APP_NAME))
    cache_dir = Path(platformdirs.user_cache_dir(APP_NAME))
    state_dir = Path(platformdirs.user_state_dir(APP_NAME))
else:
    data_dir, config_dir, cache_dir, state_dir = _fallback_dirs()

for d in (data_dir, config_dir, cache_dir, state_dir):
    try:
        d.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass

TODO_FILE = data_dir / "todos.json"
WALLPAPER_FILE = cache_dir / "wallpaper.png"
OUTPUT = WALLPAPER_FILE
CONFIG_FILE = config_dir / "config.toml"


def ensure_migration(repo_dir: Path) -> None:
    """Migrate legacy files from the repository root into user data folders."""
    repo_todos = repo_dir / "todos.json"
    repo_wallpaper = repo_dir / "wallpaper.png"

    try:
        if repo_todos.exists() and not TODO_FILE.exists():
            TODO_FILE.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(repo_todos), str(TODO_FILE))
            print(f"Migrated todos.json -> {TODO_FILE}")
    except Exception as e:
        print(f"Warning: failed to migrate todos.json: {e}")

    try:
        if repo_wallpaper.exists() and not WALLPAPER_FILE.exists():
            WALLPAPER_FILE.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(repo_wallpaper), str(WALLPAPER_FILE))
            print(f"Migrated wallpaper.png -> {WALLPAPER_FILE}")
    except Exception as e:
        print(f"Warning: failed to migrate wallpaper.png: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        ensure_migration(Path(sys.argv[1]))
    else:
        print("Usage: python paths.py /path/to/repo")
