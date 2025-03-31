#!/usr/bin/env python
import os
import sys
import shutil
import platform
import subprocess
from pathlib import Path

def build_application():
    """使用PyInstaller构建应用程序"""
    print("正在构建 Glary Utilities...")
    
    # 获取脚本目录的绝对路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 设置源目录
    src_dir = os.path.join(script_dir, "src")
    
    # 如果构建目录不存在，则创建
    build_dir = os.path.join(script_dir, "build")
    if not os.path.exists(build_dir):
        os.mkdir(build_dir)
    
    # 如果dist目录不存在，则创建
    dist_dir = os.path.join(script_dir, "dist")
    if not os.path.exists(dist_dir):
        os.mkdir(dist_dir)
    
    # 定义PyInstaller命令
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
    
    # 在Windows上使用--noconsole
    if platform.system() == "Windows":
        pyinstaller_args.insert(4, "--noconsole")
    
    print("正在使用以下参数运行PyInstaller:", ' '.join(pyinstaller_args))
    
    # 运行PyInstaller
    subprocess.run(pyinstaller_args, check=True)
    
    print("构建成功完成！")
    
    # 创建安装程序（特定于平台）
    if platform.system() == "Windows":
        create_windows_installer()
    else:
        print("不支持在此平台上创建安装程序")

def create_windows_installer():
    """使用NSIS创建Windows安装程序"""
    print("正在创建Windows安装程序...")
    
    # 检查是否安装了NSIS
    try:
        subprocess.run(["makensis", "-VERSION"], capture_output=True, check=True)
    except (subprocess.SubprocessError, FileNotFoundError):
        print("NSIS未安装或不在PATH中。请从https://nsis.sourceforge.io/安装NSIS。")
        return
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 创建NSIS脚本
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
    
    # 运行NSIS以创建安装程序
    subprocess.run(["makensis", nsis_script], check=True)
    
    print("Windows安装程序创建成功！")

if __name__ == "__main__":
    build_application() 