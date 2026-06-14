# Todo-Wallpaper

A simple interactive todo list that appears as your Linux or Windows desktop wallpaper.

## Features

- 📝 **Manage todos** via simple CLI commands
- 🖼️ **Live wallpaper rendering** with minimalist design
- 🚀 **Automatic startup** on login
- 🎨 **Clean, readable formatting** with green accent

## Installation

From this folder:

```powershell
python -m pip install -e .
```

The installed command is:

```powershell
todo-wallpaper
```

You can also run without installing:

```powershell
python .\todo.py list
```

### Data Locations

Windows:
- Todos: `%LOCALAPPDATA%\todo-wallpaper\todos.json` or `%APPDATA%\todo-wallpaper\todos.json`
- Wallpaper image: `%LOCALAPPDATA%\todo-wallpaper\Cache\wallpaper.png`
- Startup launcher: `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\todo-wallpaper-sync.cmd`

Linux:
- Todos: `~/.local/share/todo-wallpaper/todos.json`
- Wallpaper image: `~/.cache/todo-wallpaper/wallpaper.png`
- Autostart: `~/.config/systemd/user/todo-wallpaper-init.service`

## Usage

```powershell
todo-wallpaper add "Buy groceries"
todo-wallpaper list
todo-wallpaper remove 1
todo-wallpaper sync
```

On Windows, the app sets wallpaper with the native `SystemParametersInfoW` API.
On Linux, it tries GNOME `gsettings` first, then `feh`.

### Autostart

```powershell
todo-wallpaper init
```

On Windows, this creates a `.cmd` launcher in your Startup folder so the wallpaper syncs when you sign in.
On Linux, this creates and enables a user `systemd` service.

### Get Help

```powershell
todo-wallpaper
```

## Development

Do not commit virtual environments such as `.venv/`. The project already lists runtime dependencies in `pyproject.toml`.

### Project Structure

- **State**: todos.json (persistent JSON file)
- **Rendering**: render.py (Pillow image generation)
- **Interface**: todo.py (CLI commands)
- **Automation**: init.py (startup)

## License

MIT
