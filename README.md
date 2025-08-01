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
- [uv](https://docs.astral.sh/uv/) (recommended) or pip for dependency management

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
   
   > **Note**: [uv](https://docs.astral.sh/uv/) is a fast Python package installer and resolver, written in Rust. It's designed to be a drop-in replacement for pip and virtualenv.

   **Option B: Using pip (Development mode)**
   ```bash
   pip install -e .
   ```

   **Option C: Using pipx (For system-wide installation)**
   ```bash
   # Install pipx if you haven't already
   pip install pipx
   
   # Install the application
   pipx install .
   
   # Run the application
   glary-utilities
   ```

3. Run the application using one of the following methods:

   **Option A: Using uv (Development)**
   ```bash
   uv run python src/main.py
   ```

   **Option B: Direct Python execution**
   ```bash
   python src/main.py
   ```

   **Option C: Using the launcher script**
   ```bash
   python run.py
   ```

   **Option D: Using the installed command (after pipx installation)**
   ```bash
   glary-utilities
   
   # Available command line options:
   glary-utilities --help          # Show help
   glary-utilities --debug         # Enable debug mode
   glary-utilities --no-splash     # Skip splash screen
   glary-utilities --reset-settings # Reset all settings
   ```

## Building from Source

To build the application and create an installer:

1. Install the required dependencies:

   **Using uv:**
   ```bash
   uv sync
   ```

   **Using pip (Development mode):**
   ```bash
   pip install -e .
   ```

   **Using pipx (For system installation):**
   ```bash
   pipx install .
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

You can run the application in several ways:

### 1. Development mode (recommended for development)
```bash
# Using uv
uv run python src/main.py

# Using pip
python src/main.py
```

### 2. Using the launcher script
```bash
python run.py
```

### 3. System installation (after pipx install)
```bash
glary-utilities
```

### Command Line Options

The application supports several command line options:

- `--debug`: Enable debug mode
- `--no-splash`: Skip splash screen
- `--check-translations`: Check for missing translations
- `--reset-settings`: Reset all settings to default
- `--exit-after-check`: Exit after translation check

## Application Installation

This is a desktop application, not a library. Here are the recommended installation methods:

### For Development
```bash
# Using uv (recommended)
uv sync
uv run python src/main.py

# Using pip
pip install -e .
python src/main.py
```

### For System Installation
```bash
# Using pipx (recommended for applications)
pip install pipx
pipx install .

# Then run from anywhere
glary-utilities
```

## Dependency Management

This project uses `pyproject.toml` for dependency management instead of `requirements.txt`. The project supports both `uv` and `pip` for installing dependencies.

### Why uv?

- **Faster**: uv is significantly faster than pip for dependency resolution and installation
- **Reliable**: Better dependency resolution and lock file support
- **Modern**: Built with modern Python packaging standards in mind
- **Compatible**: Works seamlessly with existing pip-based workflows

> **Learn more**: Visit the [uv documentation](https://docs.astral.sh/uv/) for detailed guides, tutorials, and advanced usage examples.

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

