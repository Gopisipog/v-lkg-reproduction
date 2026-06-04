"""
V-LKG Launcher Script
=====================
Used by PyInstaller to create a standalone .exe.
When run, it extracts and executes setup_and_run.bat in a temp folder.
"""

import os
import sys
import subprocess
import tempfile
import shutil


def main():
    # Get the directory where the .exe is running from
    if getattr(sys, 'frozen', False):
        # Running in a PyInstaller bundle
        base_dir = sys._MEIPASS
    else:
        # Running as a script
        base_dir = os.path.dirname(os.path.abspath(__file__))

    # Path to the batch file (bundled with the exe)
    bat_file = os.path.join(base_dir, "setup_and_run.bat")

    if not os.path.exists(bat_file):
        print(f"Error: setup_and_run.bat not found at {bat_file}")
        print("The launcher may be corrupted. Please re-download.")
        input("Press Enter to exit...")
        return

    print("=" * 50)
    print("  V-LKG - Leadership Knowledge Graph")
    print("  Local Setup & Launcher")
    print("=" * 50)
    print()

    # Run the batch file
    subprocess.run([bat_file], shell=True)


if __name__ == "__main__":
    main()
