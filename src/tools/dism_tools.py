import os
import subprocess
from .base_tools import BaseThread
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer

class DismThread(BaseThread):
    """Worker thread for DISM operations"""
    progress_updated = pyqtSignal(str)
    operation_completed = pyqtSignal(bool, str)
    
    def __init__(self, operation):
        super().__init__()
        self.operation = operation  # One of: check_health, scan_health, restore_health, cleanup_image
    
    def run(self):
        """Run worker thread"""
        if not self.platform_manager.is_windows():
            self.progress_updated.emit("DISM is only available on Windows")
            self.operation_completed.emit(False, "This operation is not supported on this platform")
            return
        
        try:
            if self.operation == "check_health":
                self.check_health()
            elif self.operation == "scan_health":
                self.scan_health()
            elif self.operation == "restore_health":
                self.restore_health()
            elif self.operation == "cleanup_image":
                self.cleanup_image()
            else:
                self.progress_updated.emit(f"Unknown operation: {self.operation}")
                self.operation_completed.emit(False, "Unknown operation")
        except Exception as e:
            self.progress_updated.emit(f"Error executing operation: {str(e)}")
            self.operation_completed.emit(False, str(e))
    
    def check_health(self):
        """Check Windows image health status"""
        self.progress_updated.emit("Checking Windows image health status...")
        proc = subprocess.Popen(
            ["dism", "/Online", "/Cleanup-Image", "/CheckHealth"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            universal_newlines=True
        )
        
        self._process_output(proc)
    
    def scan_health(self):
        """Scan Windows image health status"""
        self.progress_updated.emit("Scanning Windows image health status...")
        proc = subprocess.Popen(
            ["dism", "/Online", "/Cleanup-Image", "/ScanHealth"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            universal_newlines=True
        )
        
        self._process_output(proc)
    
    def restore_health(self):
        """Restore Windows image health status"""
        self.progress_updated.emit("Restoring Windows image health status...")
        proc = subprocess.Popen(
            ["dism", "/Online", "/Cleanup-Image", "/RestoreHealth"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            universal_newlines=True
        )
        
        self._process_output(proc)
    
    def cleanup_image(self):
        """Clean up Windows image"""
        self.progress_updated.emit("Cleaning up Windows image...")
        proc = subprocess.Popen(
            ["dism", "/Online", "/Cleanup-Image", "/StartComponentCleanup"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            universal_newlines=True
        )
        
        self._process_output(proc)
    
    def _process_output(self, proc):
        """Process DISM command output"""
        success = True
        last_line = ""
        
        while True:
            line = proc.stdout.readline()
            if not line:
                break
            
            line = line.strip()
            if line:
                self.progress_updated.emit(line)
                last_line = line
        
        proc.wait()
        
        if proc.returncode != 0:
            success = False
            last_line = f"Operation failed, return code {proc.returncode}"
        
        self.operation_completed.emit(success, last_line)
