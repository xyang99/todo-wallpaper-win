#!/usr/bin/env python3
"""Initialize todo-wallpaper: run setup, install the CLI wrapper, and enable systemd autostart."""

import os
import subprocess
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).parent
HOME = Path.home()
SYSTEMD_DIR = HOME / ".config/systemd/user"
SERVICE_FILE = SYSTEMD_DIR / "todo-wallpaper-init.service"
LOCAL_BIN_DIR = HOME / ".local/bin"
WRAPPER_FILE = PROJECT_DIR / "todo"
WRAPPER_LINK = LOCAL_BIN_DIR / "todo"

SERVICE_CONTENT = """[Unit]
Description=Todo-Wallpaper Initial Render
After=graphical-session-reach.target
PartOf=graphical-session.target

[Service]
Type=oneshot
ExecStart={python_path} {render_script}
RemainAfterExit=yes

[Install]
WantedBy=graphical-session.target
"""


def run_command(cmd: list[str], description: str) -> bool:
    """Run a shell command and return success status."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✓ {description}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description}")
        if e.stderr:
            print(f"  {e.stderr.strip()}")
        return False
    except FileNotFoundError:
        print(f"✗ {description} (command not found)")
        return False


def main() -> int:
    print("=== Todo-Wallpaper Initialization ===\n")

    # Step 1: Run setup
    print("Step 1: Running setup...")
    setup_result = subprocess.run(
        [sys.executable, "setup.py"],
        cwd=PROJECT_DIR,
    )

    if setup_result.returncode != 0:
        print("\n✗ Setup failed. Fix dependencies and try again.")
        return 1

    # Step 2: Install the command wrapper
    print("\nStep 2: Installing the todo command wrapper...")
    WRAPPER_FILE.chmod(0o755)
    LOCAL_BIN_DIR.mkdir(parents=True, exist_ok=True)

    if WRAPPER_LINK.exists() or WRAPPER_LINK.is_symlink():
        WRAPPER_LINK.unlink()

    WRAPPER_LINK.symlink_to(WRAPPER_FILE)
    print(f"✓ Installed command: {WRAPPER_LINK}")

    current_path = os.environ.get("PATH", "")
    if str(LOCAL_BIN_DIR) not in current_path.split(":"):
        print(f"⚠ {LOCAL_BIN_DIR} is not on your PATH yet")
        print(f"  Add this to your shell config: export PATH=\"{LOCAL_BIN_DIR}:$PATH\"")

    # Step 3: Create systemd user service
    print("\nStep 3: Setting up autostart...")
    SYSTEMD_DIR.mkdir(parents=True, exist_ok=True)

    service_content = SERVICE_CONTENT.format(
        python_path=sys.executable,
        render_script=PROJECT_DIR / "render.py",
    )

    SERVICE_FILE.write_text(service_content)
    print(f"✓ Created systemd service: {SERVICE_FILE}")

    # Step 4: Enable service
    if run_command(
        ["systemctl", "--user", "daemon-reload"],
        "Reloaded systemd user daemon",
    ):
        if run_command(
            ["systemctl", "--user", "enable", "todo-wallpaper-init.service"],
            "Enabled todo-wallpaper-init.service",
        ):
            print("\n=== Initialization Complete ===")
            print("✓ Wallpaper will render automatically on next login")
            print("\nYou can now use:")
            print("  todo add 'Your task'")
            print("  todo list")
            print("  todo remove 1")
            print("\nTo manually trigger wallpaper render:")
            print("  python3 render.py")
            return 0

    print("\n⚠ Failed to enable autostart (systemd user services may not be available)")
    print("You can still use: python3 todo.py [add|remove|list]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
