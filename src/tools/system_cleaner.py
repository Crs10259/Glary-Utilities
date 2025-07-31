import os
import shutil
import subprocess
import tempfile
from .base_tools import BaseThread
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer

class CleanerWorker(BaseThread):
    """Worker thread for scanning and cleaning files"""
    progress_updated = pyqtSignal(int, str)
    scan_completed = pyqtSignal(dict)
    clean_completed = pyqtSignal(dict)
    
    def __init__(self, options, exclusions, extensions, operation="scan"):
        super().__init__()
        self.options = options  # Dictionary of options to scan
        self.exclusions = exclusions  # List of directories/files to exclude
        self.extensions = extensions  # List of file extensions to clean
        self.operation = operation  # "scan" or "clean"
        self.stop_requested = False
    
    def run(self):
        """Run worker thread"""
        if self.operation == "scan":
            self.scan_files()
        elif self.operation == "clean":
            self.clean_files()
    
    def stop(self):
        """Request worker thread to stop"""
        self.stop_requested = True
    
    def scan_files(self):
        """Scan unnecessary files"""
        results = {
            "files": [],
            "total_size": 0,
            "count": 0
        }
        
        # Get temporary directory
        temp_dir = tempfile.gettempdir()
        
        # Get user home directory
        home_dir = os.path.expanduser("~")
        
        progress = 0
        self.progress_updated.emit(progress, "开始扫描...")
        
        # Scan temporary files
        if self.options.get("temp_files", False):
            self.progress_updated.emit(progress, "Scanning temporary files...")
            temp_files = self.scan_directory(temp_dir)
            results["files"].extend(temp_files)
            progress += 20
            self.progress_updated.emit(progress, f"Found {len(temp_files)} temporary files")
        
        # Scan recycle bin
        if self.options.get("recycle_bin", False):
            self.progress_updated.emit(progress, "Scanning recycle bin...")
            recycle_files = self.scan_recycle_bin()
            results["files"].extend(recycle_files)
            progress += 20
            self.progress_updated.emit(progress, f"Found {len(recycle_files)} recycle bin files")
        
        # Scan cache files (browser)
        if self.options.get("cache_files", False):
            self.progress_updated.emit(progress, "Scanning cache files...")
            cache_files = self.scan_browser_caches(home_dir)
            results["files"].extend(cache_files)
            progress += 20
            self.progress_updated.emit(progress, f"Found {len(cache_files)} cache files")
        
        # Scan log files
        if self.options.get("log_files", False):
            self.progress_updated.emit(progress, "Scanning log files...")
            log_files = self.scan_log_files()
            results["files"].extend(log_files)
            progress += 20
            self.progress_updated.emit(progress, f"Found {len(log_files)} log files")
        
        # Calculate total
        results["count"] = len(results["files"])
        results["total_size"] = sum(file["size"] for file in results["files"])
        
        self.progress_updated.emit(100, f"Scan completed. Found {results['count']} files ({self.format_size(results['total_size'])})")
        self.scan_completed.emit(results)
    
    def clean_files(self):
        """Clean selected files"""
        results = {
            "cleaned_count": 0,
            "cleaned_size": 0,
            "failed_count": 0
        }
        
        total_files = len(self.options.get("files", []))
        if total_files == 0:
            self.progress_updated.emit(100, "No files to clean")
            self.clean_completed.emit(results)
            return
        
        self.progress_updated.emit(0, f"Cleaning {total_files} files...")
        
        for i, file_info in enumerate(self.options.get("files", [])):
            if self.stop_requested:
                break
                
            file_path = file_info["path"]
            try:
                if os.path.exists(file_path):
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                    
                    results["cleaned_count"] += 1
                    results["cleaned_size"] += file_info["size"]
                    
                    progress = int((i + 1) / total_files * 100)
                    self.progress_updated.emit(progress, f"Cleaned {results['cleaned_count']} files ({self.format_size(results['cleaned_size'])})")
                else:
                    results["failed_count"] += 1
            except Exception as e:
                self.logger.error(f"Error cleaning {file_path}: {e}")
                results["failed_count"] += 1
        
        self.progress_updated.emit(100, f"Clean completed. Cleaned {results['cleaned_count']} files ({self.format_size(results['cleaned_size'])})")
        self.clean_completed.emit(results)
    
    def scan_directory(self, directory):
        """Scan directory to find files to clean"""
        files = []
        
        try:
            for root, dirs, filenames in os.walk(directory):
                if self.stop_requested:
                    break
                    
                # Skip excluded directories
                dirs[:] = [d for d in dirs if os.path.join(root, d) not in self.exclusions]
                
                for filename in filenames:
                    file_path = os.path.join(root, filename)
                    
                    # Skip excluded files
                    if file_path in self.exclusions:
                        continue
                    
                    # Only include files with specified extensions (if provided)
                    if self.extensions and not any(filename.endswith(ext) for ext in self.extensions):
                        continue
                    
                    try:
                        file_size = os.path.getsize(file_path)
                        files.append({
                            "path": file_path,
                            "name": filename,
                            "size": file_size
                        })
                    except Exception as e:
                        self.logger.error(f"Error getting file info {file_path}: {e}")
        except Exception as e:
            self.logger.error(f"Error scanning directory {directory}: {e}")
        
        return files
    
    def scan_recycle_bin(self):
        """Scan recycle bin for files"""
        files = []
        
        try:
            if self.platform_manager.is_windows():
                # Windows recycle bin located at C:\\$Recycle.Bin
                recycle_bin = "C:\\$Recycle.Bin"
                if os.path.exists(recycle_bin):
                    files = self.scan_directory(recycle_bin)
            elif self.platform_manager.is_mac():  # macOS
                # macOS trash located at ~/.Trash
                trash_path = os.path.expanduser("~/.Trash")
                if os.path.exists(trash_path):
                    files = self.scan_directory(trash_path)
            elif self.platform_manager.is_linux():
                # Linux trash located at ~/.local/share/Trash
                trash_path = os.path.expanduser("~/.local/share/Trash")
                if os.path.exists(trash_path):
                    files = self.scan_directory(trash_path)
        except Exception as e:
            self.logger.error(f"Error scanning recycle bin: {e}")
        
        return files
    
    def scan_browser_caches(self, home_dir):
        """Scan browser cache directory"""
        files = []
        
        try:
            system = self.platform_manager.current_system
            
            # Chrome cache
            chrome_cache = None
            if system == "Windows":
                chrome_cache = os.path.join(home_dir, "AppData", "Local", "Google", "Chrome", "User Data", "Default", "Cache")
            elif system == "Darwin":
                chrome_cache = os.path.join(home_dir, "Library", "Caches", "Google", "Chrome")
            elif system == "Linux":
                chrome_cache = os.path.join(home_dir, ".cache", "google-chrome")
            
            if chrome_cache and os.path.exists(chrome_cache):
                files.extend(self.scan_directory(chrome_cache))
            
            # Firefox cache
            firefox_cache = None
            if system == "Windows":
                firefox_cache = os.path.join(home_dir, "AppData", "Local", "Mozilla", "Firefox", "Profiles")
            elif system == "Darwin":
                firefox_cache = os.path.join(home_dir, "Library", "Caches", "Firefox")
            elif system == "Linux":
                firefox_cache = os.path.join(home_dir, ".cache", "mozilla", "firefox")
            
            if firefox_cache and os.path.exists(firefox_cache):
                # For Firefox, we need to scan each profile
                if system == "Windows":
                    # Scan each profile directory
                    for profile in os.listdir(firefox_cache):
                        profile_cache = os.path.join(firefox_cache, profile, "cache2")
                        if os.path.exists(profile_cache):
                            files.extend(self.scan_directory(profile_cache))
                else:
                    files.extend(self.scan_directory(firefox_cache))
            
            # Edge cache (only Windows)
            if system == "Windows":
                edge_cache = os.path.join(home_dir, "AppData", "Local", "Microsoft", "Edge", "User Data", "Default", "Cache")
                if os.path.exists(edge_cache):
                    files.extend(self.scan_directory(edge_cache))
            
        except Exception as e:
            self.logger.error(f"Error scanning browser cache: {e}")
        
        return files
    
    def scan_log_files(self):
        """Scan log files"""
        files = []
        
        try:
            system = self.platform_manager.current_system
            
            if system == "Windows":
                # Windows logs
                log_paths = [
                    os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "Logs"),
                    os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "Temp")
                ]
                
                for log_path in log_paths:
                    if os.path.exists(log_path):
                        for root, dirs, filenames in os.walk(log_path):
                            if self.stop_requested:
                                break
                                
                            for filename in filenames:
                                if filename.endswith(".log"):
                                    file_path = os.path.join(root, filename)
                                    try:
                                        file_size = os.path.getsize(file_path)
                                        files.append({
                                            "path": file_path,
                                            "name": filename,
                                            "size": file_size
                                        })
                                    except Exception as e:
                                        self.logger.error(f"Error getting log file info: {e}")
            elif system == "Darwin" or system == "Linux":
                # macOS/Linux logs
                log_paths = [
                    "/var/log",
                    os.path.expanduser("~/Library/Logs") if system == "Darwin" else None,
                ]
                
                for log_path in log_paths:
                    if log_path and os.path.exists(log_path):
                        log_files = self.scan_directory(log_path)
                        # Only include .log files
                        log_files = [f for f in log_files if f["name"].endswith(".log")]
                        files.extend(log_files)
        except Exception as e:
            self.logger.error(f"Error scanning log files: {e}")
        
        return files
    
    def format_size(self, size_bytes):
        """Format bytes to human readable size"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
            if size_bytes < 1024:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024