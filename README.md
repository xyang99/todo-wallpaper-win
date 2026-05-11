# Todo-Wallpaper

A simple interactive todo list that appears as your Linux desktop wallpaper.

## Features

- 📝 **Manage todos** via simple CLI commands
- 🖼️ **Live wallpaper rendering** with minimalist design
- 🚀 **Automatic startup** on login (via systemd)
- 🎨 **Clean, readable formatting** with blue accent

## Architecture

```
todo-wallpaper/
├── todos.json              # Todo storage (JSON)
├── render.py               # Wallpaper renderer (Pillow)
├── todo.py                 # CLI interface
├── todo                    # Shell wrapper for the global command
├── watch.py                # File watcher (optional daemon)
├── init.py                 # One-command setup
├── setup.py                # Dependency checker
└── wallpaper.png           # Generated wallpaper
```

## Installation

### Prerequisites

Ensure you have Python 3 installed:

```bash
python3 --version  # Should be 3.7+
```

### Quick Setup (One Command)

```bash
cd ~/projects/random/todo-wallpaper
python3 init.py
```

This will:

1. ✓ Check and install Python dependencies (Pillow, watchdog)
2. ✓ Verify system tools (feh, fonts)
3. ✓ Generate your first wallpaper
4. ✓ Install the `todo` command into `~/.local/bin`
5. ✓ Enable automatic startup on login via systemd

### Manual Setup

If you prefer to set up manually:

```bash
# Install dependencies
pip install Pillow watchdog

# Install system tools
sudo apt install feh fonts-dejavu

# Run setup checks
python3 setup.py

# Generate initial wallpaper
python3 render.py

# Install the command wrapper
mkdir -p ~/.local/bin
ln -sf ~/projects/random/todo-wallpaper/todo ~/.local/bin/todo

# Make sure ~/.local/bin is on PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# Enable autostart (optional)
mkdir -p ~/.config/systemd/user
cp todo-wallpaper-init.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable todo-wallpaper-init.service
```

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

### Batch Operations

Add multiple tasks:

```bash
for task in "Fix bug" "Write docs" "Deploy"; do
   todo add "$task"
done
```

## Files Explained

| File            | Purpose                                      |
| --------------- | -------------------------------------------- |
| `todos.json`    | JSON file storing your todo list             |
| `render.py`     | Generates wallpaper PNG from todos.json      |
| `todo.py`       | CLI tool to add/remove/list todos            |
| `todo`          | Shell wrapper for the `todo` command         |
| `watch.py`      | Optional: auto-renders on todos.json changes |
| `setup.py`      | Checks and installs dependencies             |
| `init.py`       | One-command installation + autostart setup   |
| `wallpaper.png` | Generated wallpaper image                    |

## Customization

### Colors

Edit `render.py`:

```python
BACKGROUND = (20, 20, 30)      # Dark blue-gray
TEXT = (240, 240, 240)         # Light white
ACCENT = (120, 200, 255)       # Light blue
```

### Font Size

Edit `render.py`:

```python
title_font = ImageFont.truetype(..., 54)    # Title (TODO)
font = ImageFont.truetype(..., 36)          # Items
```

### Wallpaper Dimensions

Edit `render.py`:

```python
WIDTH = 1920
HEIGHT = 1080
```

### Font Path

If you have a different font installed, update `render.py`:

```python
font = ImageFont.truetype("/path/to/font.ttf", 36)
```

Find available fonts on Linux:

```bash
fc-list | grep -i "font-name"
```

## Troubleshooting

### "feh not found"

```bash
sudo apt install feh
```

### "Font not found"

```bash
sudo apt install fonts-dejavu
# Or check available fonts:
fc-list | head -20
```

### "Pillow not found"

```bash
pip install Pillow
```

### Wallpaper not updating on startup

Check systemd service status:

```bash
systemctl --user status todo-wallpaper-init.service
journalctl --user -u todo-wallpaper-init.service -n 20
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
