#!/usr/bin/env python3
"""Setup todo-wallpaper dependencies and generate initial wallpaper."""

import subprocess
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).parent


def run_command(cmd: list[str], description: str) -> bool:
    """Run a shell command and return success status."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✓ {description}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description}")
        if e.stderr:
            print(f"  Error: {e.stderr.strip()}")
        return False
    except FileNotFoundError:
        print(f"✗ {description} (command not found)")
        return False


def check_python_package(package: str, import_name: str = None) -> bool:
    """Check if a Python package is installed."""
    if import_name is None:
        import_name = package

    try:
        __import__(import_name)
        print(f"✓ Python package '{package}' is installed")
        return True
    except ImportError:
        print(f"✗ Python package '{package}' is missing")
        return False


def main() -> int:
    print("=== Todo-Wallpaper Setup ===\n")

    # Check Python packages
    print("Checking Python dependencies...")
    pillow_ok = check_python_package("Pillow", "PIL")
    watchdog_ok = check_python_package("watchdog")

    if not pillow_ok:
        print("\n  Install with: pip install Pillow")

    # Check system tools
    print("\nChecking system tools...")
    feh_ok = run_command(["which", "feh"], "feh is installed")

    if not feh_ok:
        print("  Install with: sudo apt install feh")

    # Check fonts
    print("\nChecking fonts...")
    font_path = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    if font_path.exists():
        print("✓ DejaVuSans font is installed")
    else:
        print("✗ DejaVuSans font is missing")
        print("  Install with: sudo apt install fonts-dejavu")

    # Generate initial wallpaper if todos.json exists
    print("\nGenerating initial wallpaper...")
    if pillow_ok and feh_ok and font_path.exists():
        result = subprocess.run(
            [sys.executable, "render.py"],
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print(f"✓ {result.stdout.strip()}")
        else:
            print(f"✗ Failed to render wallpaper: {result.stderr}")
            return 1
    else:
        print("⚠ Skipping wallpaper render (missing dependencies)")

    # Summary
    print("\n=== Setup Summary ===")
    if pillow_ok and feh_ok and font_path.exists():
        print("✓ All dependencies are satisfied!")
        print("\nNext steps:")
        print("  1. Run: python3 init.py  (to enable autostart)")
        print("  2. Or use: python3 todo.py add 'Your task'")
        return 0
    else:
        print("⚠ Some dependencies are missing. Please install them first.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
