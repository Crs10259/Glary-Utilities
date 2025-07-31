import os
import subprocess
from .base_tools import BaseThread
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer

class DiskCheckThread(BaseThread):
    """Worker thread for disk check operations"""
    progress_updated = pyqtSignal(str)
    operation_completed = pyqtSignal(bool)
    
    def __init__(self, drive, check_file_system, check_bad_sectors, read_only=True, operation="check"):
        super().__init__()
        self.drive = drive  # Drive letter to check
        self.check_file_system = check_file_system  # Whether to check file system
        self.check_bad_sectors = check_bad_sectors  # Whether to check for bad sectors
        self.read_only = read_only  # Whether to run in read-only mode
        self.operation = operation  # "check" or "repair"
    
    def run(self):
        """Run the worker thread"""
        if not self.platform_manager.is_windows():
            self.progress_updated.emit("磁盘检查当前仅在Windows系统上支持")
            self.operation_completed.emit(False)
            return
        
        try:
            if self.operation == "check":
                self.check_disk()
            elif self.operation == "repair":
                if self.read_only:
                    self.progress_updated.emit("只读模式已启用。仅在检查模式下运行...")
                    self.check_disk()
                else:
                    self.repair_disk()
            else:
                self.progress_updated.emit(f"未知操作: {self.operation}")
                self.operation_completed.emit(False)
        except Exception as e:
            self.progress_updated.emit(f"执行操作时出错: {str(e)}")
            self.operation_completed.emit(False)
    
    def check_disk(self):
        """Check disk errors without fixing them"""
        # Validate drive
        if not os.path.exists(self.drive):
            self.progress_updated.emit(f"Drive {self.drive} does not exist or is not accessible")
            self.operation_completed.emit(False)
            return
        
        self.progress_updated.emit(f"Checking drive {self.drive}...")
        
        # Build command arguments
        cmd = ["chkdsk", self.drive]
        
        # Add necessary options
        if self.check_file_system:
            # File system check doesn't need additional parameters
            pass
        
        if self.check_bad_sectors:
            cmd.append("/B")  # Check bad sectors
        
        self.progress_updated.emit(f"Running command: {' '.join(cmd)}")
        
        try:
            # Use self.platform_manager to run chkdsk
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                universal_newlines=True,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            
            # Process output
            while True:
                line = proc.stdout.readline()
                if not line:
                    break
                
                line = line.strip()
                if line:
                    self.progress_updated.emit(line)
            
            proc.wait()
            
            if proc.returncode == 0:
                self.progress_updated.emit("Disk check completed successfully")
                self.operation_completed.emit(True)
            else:
                self.progress_updated.emit(f"Disk check failed with return code {proc.returncode}")
                self.operation_completed.emit(False)
        except FileNotFoundError:
            self.progress_updated.emit("Error: chkdsk command not found. Please ensure you are running this program on a Windows system.")
            self.operation_completed.emit(False)
        except PermissionError:
            self.progress_updated.emit("Error: Permission denied. Please try running the program as administrator.")
            self.operation_completed.emit(False)
        except Exception as e:
            self.progress_updated.emit(f"Error running disk check: {str(e)}")
            self.operation_completed.emit(False)
    
    def repair_disk(self):
        """Check and repair disk errors"""
        self.progress_updated.emit(f"Checking and repairing drive {self.drive}...")
        
        # Build command arguments
        cmd = ["chkdsk", self.drive, "/F"]  # /F to fix errors
        
        if self.check_bad_sectors:
            cmd.append("/R")  # Repair bad sectors
        
        self.progress_updated.emit(f"Running command: {' '.join(cmd)}")
        self.progress_updated.emit("Note: This operation may require system restart")
        
        try:
            # Use self.platform_manager to run chkdsk repair command
            result = self.platform_manager.run_command(cmd)
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if line.strip():
                        self.progress_updated.emit(line.strip())
                
                self.progress_updated.emit("Disk repair has been successfully scheduled")
                self.operation_completed.emit(True)
            else:
                for line in result.stdout.split('\n'):
                    if line.strip():
                        self.progress_updated.emit(line.strip())
                
                if result.stderr:
                    self.progress_updated.emit(f"Error: {result.stderr}")
                
                self.progress_updated.emit(f"Disk repair failed with return code {result.returncode}")
                self.operation_completed.emit(False)
        except Exception as e:
            self.progress_updated.emit(f"Error running disk repair: {str(e)}")
            self.operation_completed.emit(False)