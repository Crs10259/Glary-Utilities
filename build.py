#!/usr/bin/env python
import os
import sys
import shutil
import platform
import subprocess
from pathlib import Path

def build_application():
    """Build the application using PyInstaller"""
    print("Building Glary Utilities...")
    
    # Get the absolute path to the script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Set the source directory
    src_dir = os.path.join(script_dir, "src")
    
    # Create build directory if it doesn't exist
    build_dir = os.path.join(script_dir, "build")
    if not os.path.exists(build_dir):
        os.mkdir(build_dir)
    
    # Create dist directory if it doesn't exist
    dist_dir = os.path.join(script_dir, "dist")
    if not os.path.exists(dist_dir):
        os.mkdir(dist_dir)
    
    # Define PyInstaller command
    pyinstaller_args = [
        "pyinstaller",
        "--name=GlaryUtilities",
        "--onedir",
        "--windowed",
        f"--icon={os.path.join(src_dir, 'assets/images/icon.png')}",
        f"--add-data={os.path.join(src_dir, 'assets')}{os.pathsep}assets",
        f"--add-data={os.path.join(src_dir, 'translations')}{os.pathsep}translations",
        "--clean",
        os.path.join(src_dir, "main.py")
    ]
    
    # On Windows, use --noconsole
    if platform.system() == "Windows":
        pyinstaller_args.insert(4, "--noconsole")
    
    print("Running PyInstaller with arguments:", ' '.join(pyinstaller_args))
    
    # Run PyInstaller
    subprocess.run(pyinstaller_args, check=True)
    
    print("Build completed successfully!")
    
    # Create installer (platform-specific)
    if platform.system() == "Windows":
        create_windows_installer()
    else:
        print("Installer creation not supported on this platform")

def create_windows_installer():
    """Create a Windows installer using NSIS"""
    print("Creating Windows installer...")
    
    # Check if NSIS is installed
    try:
        subprocess.run(["makensis", "-VERSION"], capture_output=True, check=True)
    except (subprocess.SubprocessError, FileNotFoundError):
        print("NSIS is not installed or not in PATH. Please install NSIS from https://nsis.sourceforge.io/")
        return
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create NSIS script
    nsis_script = os.path.join(script_dir, "installer.nsi")
    with open(nsis_script, "w") as f:
        f.write("""
!include "MUI2.nsh"

; Application information
Name "Glary Utilities"
OutFile "dist\\GlaryUtilities_Setup.exe"
InstallDir "$PROGRAMFILES\\Glary Utilities"
InstallDirRegKey HKCU "Software\\Glary Utilities" ""

; Request application privileges
RequestExecutionLevel admin

; Interface settings
!define MUI_ABORTWARNING
!define MUI_ICON "src\\assets\\images\\icon.png"
!define MUI_UNICON "src\\assets\\images\\icon.png"

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; Languages
!insertmacro MUI_LANGUAGE "English"

; Installation section
Section "Install"
    SetOutPath "$INSTDIR"
    
    ; Copy files
    File /r "dist\\GlaryUtilities\\*.*"
    
    ; Create uninstaller
    WriteUninstaller "$INSTDIR\\Uninstall.exe"
    
    ; Create shortcut
    CreateDirectory "$SMPROGRAMS\\Glary Utilities"
    CreateShortcut "$SMPROGRAMS\\Glary Utilities\\Glary Utilities.lnk" "$INSTDIR\\GlaryUtilities.exe"
    CreateShortcut "$SMPROGRAMS\\Glary Utilities\\Uninstall.lnk" "$INSTDIR\\Uninstall.exe"
    CreateShortcut "$DESKTOP\\Glary Utilities.lnk" "$INSTDIR\\GlaryUtilities.exe"
    
    ; Registry entries
    WriteRegStr HKCU "Software\\Glary Utilities" "" $INSTDIR
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\GlaryUtilities" "DisplayName" "Glary Utilities"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\GlaryUtilities" "UninstallString" "$INSTDIR\\Uninstall.exe"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\GlaryUtilities" "DisplayIcon" "$INSTDIR\\GlaryUtilities.exe"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\GlaryUtilities" "Publisher" "Your Company"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\GlaryUtilities" "DisplayVersion" "1.0.0"
SectionEnd

; Uninstallation section
Section "Uninstall"
    ; Remove files
    Delete "$INSTDIR\\Uninstall.exe"
    RMDir /r "$INSTDIR"
    
    ; Remove shortcuts
    Delete "$SMPROGRAMS\\Glary Utilities\\Glary Utilities.lnk"
    Delete "$SMPROGRAMS\\Glary Utilities\\Uninstall.lnk"
    RMDir "$SMPROGRAMS\\Glary Utilities"
    Delete "$DESKTOP\\Glary Utilities.lnk"
    
    ; Remove registry entries
    DeleteRegKey HKCU "Software\\Glary Utilities"
    DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\GlaryUtilities"
SectionEnd
""")
    
    # Run NSIS to create installer
    subprocess.run(["makensis", nsis_script], check=True)
    
    print("Windows installer created successfully!")

if __name__ == "__main__":
    build_application() 