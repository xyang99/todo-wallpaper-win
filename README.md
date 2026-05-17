# Todo-Wallpaper

A simple interactive todo list that appears as your Linux desktop wallpaper.

## Features

- 📝 **Manage todos** via simple CLI commands
- 🖼️ **Live wallpaper rendering** with minimalist design
- 🚀 **Automatic startup** on login (via systemd)
- 🎨 **Clean, readable formatting** with blue accent

## Installation

```bash
pip install todo-wallpaper
```

After installation, enable autostart:

```bash
todo init
```

### Data Locations

- `~/.local/share/todo-wallpaper/todos.json` — todo list storage
- `~/.cache/todo-wallpaper/wallpaper.png` — generated wallpaper
- `~/.config/systemd/user/todo-wallpaper-init.service` — autostart service

## Usage

### Adding Todos

```bash
todo add "Buy groceries"
todo add "Complete project"
```

The wallpaper will automatically render and update your desktop.

### Listing Todos

```bash
todo list
```

Output:

```
1: Buy groceries
2: Complete project
```

### Removing Todos

```bash
todo remove 1  # Remove first todo
todo remove 2  # Remove second todo
```

### Get Help

```bash
todo
```

### Set Up Autostart

```bash
todo init
```

## Workflow Examples

### Daily Routine

```bash
# Start your day
todo add "Review emails"
todo add "Team standup"
todo add "Code review"

# Check what's on your plate
todo list

# Mark items as done
todo remove 1  # ✓ emails done
todo remove 1  # ✓ standup done
```

### Want to stop autostart?

```bash
systemctl --user disable todo-wallpaper-init.service
```

### Re-enable autostart?

```bash
systemctl --user enable todo-wallpaper-init.service
```

### Manual wallpaper render

```bash
python3 render.py
```

## Optional: File Watcher

Use `watch.py` to auto-update wallpaper whenever todos.json changes:

```bash
python3 watch.py
```

This runs a daemon in the foreground. Press Ctrl+C to stop.

Requirements: `watchdog` package (`pip install watchdog`)

## Tips

1. **Keybinding**: Create a shell alias for faster access:

   ```bash
   alias todo='python3 ~/projects/random/todo-wallpaper/todo.py'
   # Now use: todo add "task name"
   ```

2. **Full-screen todo view**: List all todos in a terminal:

   ```bash
   watch -n 1 'python3 ~/projects/random/todo-wallpaper/todo.py list'
   ```

3. **Regular refresh** (if not using watch.py):
   ```bash
   # Add to crontab to refresh every hour
   0 * * * * python3 ~/projects/random/todo-wallpaper/render.py
   ```

## Development

### Testing

```bash
# Add a test todo
python3 todo.py add "Test task"

# Verify it appears in wallpaper
python3 render.py

# List todos
todo list

# Remove it
todo remove 1
```

### Project Structure

- **State**: todos.json (persistent JSON file)
- **Rendering**: render.py (Pillow image generation)
- **Interface**: todo.py (CLI commands)
- **Automation**: init.py + systemd service (startup)

## License

MIT

## Support

Issues or suggestions? Check:

- Are all dependencies installed? Run `python3 setup.py`
- Is feh correctly setting the wallpaper? Try manually: `feh --bg-fill wallpaper.png`
- Are todo files in the right location? Should be in `~/projects/random/todo-wallpaper/`
