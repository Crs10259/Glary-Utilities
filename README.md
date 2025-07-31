# Glary Utilities

A comprehensive system utility tool for Windows that helps optimize, clean, and maintain your computer.

## Features

- **Dashboard**: Quick overview of system status and access to main utilities
- **System Cleaner**: Remove unnecessary files to free up disk space
  - Clean temporary files, browser caches, and log files
  - Empty recycle bin
  - Customizable file exclusions and extensions
- **GPU Information**: View detailed information about your graphics card
- **System Repair**: Check and fix various system issues
- **DISM Tool**: Interface for Windows Deployment Image Servicing and Management tool
- **Network Reset**: Reset and fix network configurations
- **Disk Check**: Verify disk integrity and fix errors
- **Boot Repair**: Fix boot-related issues 
- **Virus Scan**: Basic malware scanning functionality

## Requirements

- Windows 10 or later (some features may work on earlier versions)
- Python 3.8 or later (if running from source)

## Installation

### Using the Installer

1. Download the latest installer from the [Releases](https://github.com/Crs10259/Glary-Utilities.git/releases) page
2. Run the installer and follow the on-screen instructions
3. Launch Glary Utilities from the Start menu or desktop shortcut

### Running from Source

1. Clone this repository:
   ```
   git clone https://github.com/Crs10259/Glary-Utilities.git
   cd Glary-Utilities
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python src/main.py
   ```

## Building from Source

To build the application and create an installer:

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. For creating standalone executables, you can use various packaging tools:
   - **Windows**: Use tools like cx_Freeze, py2exe, or auto-py-to-exe
   - **macOS**: Use py2app or create-dmg
   - **Linux**: Use AppImage or snapcraft

3. For creating installers, you can use:
   - **Windows**: NSIS (Nullsoft Scriptable Install System) or Inno Setup
   - **macOS**: pkgbuild or create-dmg
   - **Linux**: AppImage or snapcraft

## Translations

The application supports multiple languages. Translations are stored in JSON files in the `resources/translations` directory. The application will automatically use the system language if a translation is available.

To add a new translation:
1. Copy the `en.json` file to a new file named with the language code (e.g., `fr.json` for French)
2. Translate the text in the new file
3. The application will automatically detect and use the new translation

## License

[MIT License](LICENSE)

