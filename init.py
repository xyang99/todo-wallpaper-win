#!/usr/bin/env python3
"""Initialize todo-wallpaper and enable systemd autostart."""

import subprocess
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).parent
SYSTEMD_DIR = Path.home() / ".config/systemd/user"
SERVICE_FILE = SYSTEMD_DIR / "todo-wallpaper-init.service"

SERVICE_CONTENT = """[Unit]
Description=Todo-Wallpaper Initial Render
After=graphical-session-reach.target
PartOf=graphical-session.target

[Service]
Type=oneshot
ExecStart={python_path} -m todo sync
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
    setup_script = PROJECT_DIR / "setup.py"
    if setup_script.exists():
        setup_result = subprocess.run(
            [sys.executable, str(setup_script)],
            cwd=PROJECT_DIR,
        )

        if setup_result.returncode != 0:
            print("\n✗ Setup failed. Fix dependencies and try again.")
            return 1
    else:
        print("✓ Skipping source setup checks (package install already handled dependencies)")

    # Step 2: Confirm packaged command availability
    print("\nStep 2: Checking the installed todo command...")
    command_check = subprocess.run(
        [sys.executable, "-m", "todo", "list"],
        capture_output=True,
        text=True,
    )
    if command_check.returncode != 0:
        print("⚠ The installed package could not be executed with 'python -m todo'.")
        print("  Install it with: pip install todo-wallpaper")
    else:
        print("✓ Installed package entrypoint is available")

    # Step 3: Create systemd user service
    print("\nStep 3: Setting up autostart...")
    SYSTEMD_DIR.mkdir(parents=True, exist_ok=True)

    service_content = SERVICE_CONTENT.format(
        python_path=sys.executable,
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
            print("  todo sync")
            return 0

    print("\n⚠ Failed to enable autostart (systemd user services may not be available)")
    print("You can still use: todo [add|remove|list|sync]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
