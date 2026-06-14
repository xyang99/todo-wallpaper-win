"""Initialize todo-wallpaper autostart on Windows or Linux."""

import platform
import subprocess
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.resolve()

SYSTEMD_DIR = Path.home() / ".config" / "systemd" / "user"
SERVICE_FILE = SYSTEMD_DIR / "todo-wallpaper-init.service"

SERVICE_CONTENT = """[Unit]
Description=Todo-Wallpaper Initial Render
After=graphical-session-reach.target
PartOf=graphical-session.target

[Service]
Type=oneshot
ExecStart={python_path} {todo_path} sync
RemainAfterExit=yes

[Install]
WantedBy=graphical-session.target
"""


def run_command(cmd: list[str], description: str) -> bool:
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(description)
        return True
    except subprocess.CalledProcessError as e:
        print(f"{description} failed")
        if e.stderr:
            print(f"  {e.stderr.strip()}")
        return False
    except FileNotFoundError:
        print(f"{description} failed (command not found)")
        return False


def init_windows() -> int:
    startup = (
        Path.home()
        / "AppData"
        / "Roaming"
        / "Microsoft"
        / "Windows"
        / "Start Menu"
        / "Programs"
        / "Startup"
    )
    startup.mkdir(parents=True, exist_ok=True)

    launcher = startup / "todo-wallpaper-sync.cmd"
    todo_py = PROJECT_DIR / "todo.py"
    launcher.write_text(
        "@echo off\n"
        f'cd /d "{PROJECT_DIR}"\n'
        f'"{sys.executable}" "{todo_py}" sync\n',
        encoding="utf-8",
    )

    print(f"Created Windows Startup launcher: {launcher}")
    print("Wallpaper will sync automatically the next time you sign in.")
    return 0


def init_linux() -> int:
    SYSTEMD_DIR.mkdir(parents=True, exist_ok=True)
    service_content = SERVICE_CONTENT.format(
        python_path=sys.executable,
        todo_path=PROJECT_DIR / "todo.py",
    )
    SERVICE_FILE.write_text(service_content, encoding="utf-8")
    print(f"Created systemd service: {SERVICE_FILE}")

    if run_command(["systemctl", "--user", "daemon-reload"], "Reloaded systemd user daemon"):
        if run_command(
            ["systemctl", "--user", "enable", "todo-wallpaper-init.service"],
            "Enabled todo-wallpaper-init.service",
        ):
            print("Wallpaper will render automatically on next login.")
            return 0

    print("Failed to enable autostart; you can still use: python todo.py sync")
    return 0


def main() -> int:
    print("=== Todo-Wallpaper Initialization ===")
    if platform.system() == "Windows":
        return init_windows()
    return init_linux()


if __name__ == "__main__":
    sys.exit(main())
