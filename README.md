# Glary Utilities

A comprehensive system utility tool for Windows that helps optimize, clean, and maintain your computer, but author is fool.
The project is not perfect, such as translation (mostly usable), light colored themes (mostly unusable) and incomplete functional testing (MacOS).

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
- Python 3.13 or later (if running from source)
- uv (recommended) or pip for dependency management

## Installation

### Running from Source

1. Clone this repository:
   ```bash
   git clone https://github.com/Crs10259/Glary-Utilities.git
   cd Glary-Utilities
   ```

2. Install the required dependencies using one of the following methods:

   **Option A: Using uv (Recommended)**
   ```bash
   # Install uv if you haven't already
   pip install uv
   
   # Install dependencies
   uv sync
   ```

   **Option B: Using pip**
   ```bash
   pip install -e .
   ```

3. Run the application using one of the following methods:

   **Option A: Using the installed command (after installation)**
   ```bash
   glary-utilities
   ```

   **Option B: Direct Python execution**
   ```bash
   python src/main.py
   ```

   **Option C: Using the launcher script**
   ```bash
   python run.py
   ```

## Building from Source

To build the application and create an installer:

1. Install the required dependencies:

   **Using uv:**
   ```bash
   uv sync
   ```

   **Using pip:**
   ```bash
   pip install -e .
   ```

2. For creating standalone executables, you can use various packaging tools:
   - **Windows**: Use tools like PyInstaller, cx_Freeze, or auto-py-to-exe
   - **macOS**: Use PyInstaller, py2app, or create-dmg
   - **Linux**: Use PyInstaller, AppImage, or snapcraft

3. For creating installers, you can use:
   - **Windows**: NSIS (Nullsoft Scriptable Install System), Inno Setup, or WiX Toolset
   - **macOS**: pkgbuild, create-dmg, or DMG Canvas
   - **Linux**: AppImage, snapcraft, or Flatpak

### Example: Building with PyInstaller

```bash
# Install PyInstaller
uv add pyinstaller

# Build executable
pyinstaller --onefile --windowed --name "Glary-Utilities" src/main.py
```

## Running the Application

After installation, you can run the application in several ways:

### 1. Using the installed command (recommended)
```bash
glary-utilities
```

### 2. Direct Python execution
```bash
python src/main.py
```

### 3. Using the launcher script
```bash
python run.py
```

### Command Line Options

The application supports several command line options:

- `--debug`: Enable debug mode
- `--no-splash`: Skip splash screen
- `--check-translations`: Check for missing translations
- `--reset-settings`: Reset all settings to default
- `--exit-after-check`: Exit after translation check

## Dependency Management

This project uses `pyproject.toml` for dependency management instead of `requirements.txt`. The project supports both `uv` and `pip` for installing dependencies.

### Why uv?

- **Faster**: uv is significantly faster than pip for dependency resolution and installation
- **Reliable**: Better dependency resolution and lock file support
- **Modern**: Built with modern Python packaging standards in mind
- **Compatible**: Works seamlessly with existing pip-based workflows

### Key Dependencies

- **PyQt5**: GUI framework
- **psutil**: System and process utilities
- **GPUtil**: GPU information
- **Pillow**: Image processing
- **pywin32**: Windows-specific functionality (Windows only)
- **WMI**: Windows Management Instrumentation (Windows only)

### Development Dependencies

To install development dependencies:

```bash
# Using uv
uv sync --dev

# Using pip
pip install -e ".[dev]"
```

### Build Dependencies

To install build dependencies for creating executables:

```bash
# Using uv
uv sync --build

# Using pip
pip install -e ".[build]"
```

## Translations

The application supports multiple languages. Translations are stored in JSON files in the `resources/translations` directory. The application will automatically use the system language if a translation is available.

To add a new translation:
1. Copy the `en.json` file to a new file named with the language code (e.g., `fr.json` for French)
2. Translate the text in the new file
3. The application will automatically detect and use the new translation

## License

[MIT License](LICENSE)

