#!/usr/bin/env python
import os
import sys
import shutil
import platform
import subprocess
import argparse
from pathlib import Path

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="构建Glary Utilities应用程序")
    parser.add_argument("--no-installer", action="store_true", help="不创建安装程序，只构建应用程序")
    parser.add_argument("--clean", action="store_true", help="构建前清理build和dist目录")
    parser.add_argument("--debug", action="store_true", help="构建调试版本")
    return parser.parse_args()

def build_application(args):
    """使用PyInstaller构建应用程序"""
    print("正在构建 Glary Utilities...")
    
    # 获取脚本目录的绝对路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 设置源目录
    src_dir = os.path.join(script_dir, "src")
    
    # 如果指定了清理选项，清理build和dist目录
    if args.clean:
        print("清理构建目录...")
        build_dir = os.path.join(script_dir, "build")
        dist_dir = os.path.join(script_dir, "dist")
        
        if os.path.exists(build_dir):
            shutil.rmtree(build_dir)
        if os.path.exists(dist_dir):
            shutil.rmtree(dist_dir)
    
    # 如果构建目录不存在，则创建
    build_dir = os.path.join(script_dir, "build")
    if not os.path.exists(build_dir):
        os.mkdir(build_dir)
    
    # 如果dist目录不存在，则创建
    dist_dir = os.path.join(script_dir, "dist")
    if not os.path.exists(dist_dir):
        os.mkdir(dist_dir)
    
    # 确保图标路径存在
    icon_path = os.path.join(src_dir, 'resources/icons/icon.png')
    if not os.path.exists(icon_path):
        print(f"警告: 图标文件不存在 {icon_path}，将使用PyInstaller默认图标")
        icon_path = ""
    
    # 定义PyInstaller命令
    pyinstaller_args = [
        "pyinstaller",
        "--name=GlaryUtilities",
        "--onedir",
        "--windowed",
    ]
    
    # 在Windows上使用--noconsole
    if platform.system() == "Windows":
        pyinstaller_args.append("--noconsole")
    
    # 调试模式下不使用--noconsole
    if args.debug:
        if "--noconsole" in pyinstaller_args:
            pyinstaller_args.remove("--noconsole")
    
    # 如果图标存在，添加图标参数
    if icon_path:
        pyinstaller_args.append(f"--icon={icon_path}")
    
    # 添加数据文件
    pyinstaller_args.extend([
        f"--add-data={os.path.join(src_dir, 'resources')}{os.pathsep}resources",
        f"--add-data={os.path.join(src_dir, 'translations')}{os.pathsep}translations",
        "--clean"
    ])
    
    # 添加主脚本路径
    pyinstaller_args.append(os.path.join(src_dir, "main.py"))
    
    print("正在使用以下参数运行PyInstaller:", ' '.join(pyinstaller_args))
    
    # 运行PyInstaller
    try:
        subprocess.run(pyinstaller_args, check=True)
        print("构建成功完成！")
        
        # 创建安装程序（特定于平台）
        if platform.system() == "Windows" and not args.no_installer:
            create_windows_installer()
        elif not args.no_installer:
            print("不支持在此平台上创建安装程序")
    except subprocess.CalledProcessError as e:
        print(f"构建失败: {e}")
        return False
    
    return True

def create_windows_installer():
    """使用NSIS创建Windows安装程序"""
    print("正在创建Windows安装程序...")
    
    # 检查是否安装了NSIS
    try:
        subprocess.run(["makensis", "-VERSION"], capture_output=True, check=True)
    except (subprocess.SubprocessError, FileNotFoundError):
        print("NSIS未安装或不在PATH中。请从 https://nsis.sourceforge.io/ 安装NSIS。")
        print("跳过安装程序创建，应用程序已成功构建在 dist/GlaryUtilities 目录中。")
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
!define MUI_ICON "${NSISDIR}\\Contrib\\Graphics\\Icons\\modern-install.ico"
!define MUI_UNICON "${NSISDIR}\\Contrib\\Graphics\\Icons\\modern-uninstall.ico"

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; Languages
!insertmacro MUI_LANGUAGE "English"
!insertmacro MUI_LANGUAGE "SimpChinese"

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
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\GlaryUtilities" "Publisher" "Glarysoft"
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
    try:
        print("运行NSIS创建安装程序...")
        result = subprocess.run(["makensis", nsis_script], check=True, capture_output=True, text=True)
        print(result.stdout)
        print("Windows安装程序创建成功！")
    except subprocess.CalledProcessError as e:
        print(f"创建安装程序时出错: {e}")
        print(f"NSIS输出: {e.stdout}")
        print(f"NSIS错误: {e.stderr}")
        print("应用程序已成功构建在 dist/GlaryUtilities 目录中。")

if __name__ == "__main__":
    args = parse_arguments()
    build_application(args) 