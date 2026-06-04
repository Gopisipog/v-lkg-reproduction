"""
V-LKG Windows Executable Builder
=================================
Creates a standalone V-LKG Launcher.exe using Windows IExpress
(built-in on Windows) or PyInstaller if available.

Usage:
    python launcher\build_exe.py

The resulting .exe will be placed in the project root.
"""

import os
import sys
import subprocess
import shutil
import tempfile


def build_with_iexpress():
    """Use Windows IExpress to create a self-extracting executable.
    IExpress is built into Windows XP through Windows 11.
    """
    print("Building V-LKG Launcher.exe using Windows IExpress...")

    # We'll create a SED file for IExpress
    sed_content = f"""[Version]
Class=IEXPRESS
SEDVersion=3
[Options]
PackagePurpose=InstallApp
ShowInstallProgramWindow=1
HideExtractAnimation=1
UseLongFileName=1
InsideCompressed=0
CAB_FixedSize=0
CAB_MaxSize=0
[SourceFiles]
SourceFilesRoot=.\\
SourceFile{1}=setup_and_run.bat
[TargetDir]
Directory=.
[TargetInstall]
TargetFileName=V-LKG_Launcher.exe
[AppStrings]
InstallPrompt=
DisplayLicense=
FinishMessage=Setup complete! Run setup_and_run.bat (or click above to install).
Wizard=0
ProgramsFolder=V-LKG
ProgramName=V-LKG Launcher
Shortcuts=
[Strings]
InstallTitle=V-LKG Launcher
"""

    sed_path = os.path.join(tempfile.gettempdir(), "vlkg_launcher.sed")
    with open(sed_path, "w", encoding="utf-8") as f:
        f.write(sed_content)

    # Run IExpress
    try:
        result = subprocess.run(
            ["iexpress.exe", "/N", sed_path],
            capture_output=True,
            text=True,
            timeout=30,
        )
        print("IExpress output:", result.stdout)
        if result.returncode == 0:
            print("✅ Launcher created: V-LKG_Launcher.exe")
        else:
            print("IExpress failed. You can create the .exe manually:")
            print(f"  1. Run: iexpress /N {sed_path}")
    except FileNotFoundError:
        print("IExpress not found on this system.")
        return None
    except subprocess.TimeoutExpired:
        print("IExpress timed out - this is normal, check for V-LKG_Launcher.exe")

    return os.path.abspath("V-LKG_Launcher.exe")


def build_with_pyinstaller():
    """Alternative: build with PyInstaller (requires pip install pyinstaller)."""
    print("Attempting PyInstaller build...")

    if not shutil.which("pyinstaller"):
        print("PyInstaller not found. Install with: pip install pyinstaller")
        return None

    result = subprocess.run(
        [
            "pyinstaller",
            "--onefile",
            "--name", "V-LKG_Launcher",
            "--console",
            "--add-data", "setup_and_run.bat;.",
            "launcher/launcher_script.py",
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        exe_path = os.path.join("dist", "V-LKG_Launcher.exe")
        if os.path.exists(exe_path):
            shutil.copy(exe_path, "V-LKG_Launcher.exe")
            print(f"✅ PyInstaller created: V-LKG_Launcher.exe ({os.path.getsize(exe_path)} bytes)")
            return exe_path
    else:
        print("PyInstaller build failed:", result.stderr)
        return None


if __name__ == "__main__":
    print("=" * 50)
    print("  V-LKG Launcher Builder")
    print("=" * 50)
    print()

    # Try IExpress first (built-in Windows)
    exe_path = build_with_iexpress()

    if not exe_path:
        print()
        print("Creating standalone batch file launcher instead...")

    print()
    print("Done! You can find V-LKG_Launcher.exe or setup_and_run.bat")
    print("in the project root directory.")
    print()
    print("📋 To create a .exe manually using Windows IExpress:")
    print("  1. Press Win+R, type: iexpress")
    print("  2. Choose 'Create a new Self Extraction Directive file'")
    print("  3. Package purpose: 'Extract files and run an installation command'")
    print("  4. Package title: 'V-LKG Launcher'")
    print("  5. Add: setup_and_run.bat")
    print("  6. Install program: setup_and_run.bat")
    print("  7. Finish - it will create V-LKG_Launcher.exe")
