import os
import random
import subprocess
import time
from .base_tools import BaseThread
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer

class VirusScanThread(BaseThread):
    """Thread for running virus scan operations in the background"""
    update_progress = pyqtSignal(int)
    update_log = pyqtSignal(str)
    found_threat = pyqtSignal(str, str)
    finished_scan = pyqtSignal(bool, str, int)
    
    def __init__(self, scan_options, parent=None):
        super().__init__(parent)
        self.scan_options = scan_options
        self.is_running = False
        self.should_stop = False
        self.threats_found = 0
        
    def run(self):
        self.is_running = True
        self.should_stop = False
        self.threats_found = 0
        
        try:
            scan_type = self.scan_options.get('scan_type', 'quick')
            scan_targets = self.scan_options.get('scan_targets', [])
            scan_options = self.scan_options.get('options', {})
            
            self.update_log.emit(f"Starting {scan_type} scan...")
            self.update_progress.emit(0)
            
            if scan_type == "quick":
                self.quick_scan()
            elif scan_type == "full":
                self.full_scan()
            elif scan_type == "custom":
                self.custom_scan(scan_targets)
            
            if self.should_stop:
                self.update_log.emit("Scan was stopped by user.")
                self.finished_scan.emit(False, "Scan cancelled", self.threats_found)
            else:
                self.update_log.emit("Scan completed successfully.")
                self.finished_scan.emit(True, "Scan completed", self.threats_found)
                
        except Exception as e:
            self.update_log.emit(f"Error during scan: {str(e)}")
            self.finished_scan.emit(False, f"Scan failed: {str(e)}", self.threats_found)
        
        self.is_running = False
    
    def stop(self):
        """Signal the scan to stop"""
        self.should_stop = True
    
    def quick_scan(self):
        """Perform a quick scan of common locations"""
        self.update_log.emit("Performing quick scan of common locations...")
        
        # Common locations to scan
        locations = [
            os.path.join(os.environ.get('TEMP', 'C:\\Windows\\Temp')),
            os.path.join(os.environ.get('USERPROFILE', ''), 'Downloads'),
            os.path.join(os.environ.get('USERPROFILE', ''), 'Desktop'),
            os.path.join(os.environ.get('ProgramData', 'C:\\ProgramData'), 'Microsoft\\Windows\\Start Menu\\Programs\\Startup')
        ]
        
        total_items = len(locations)
        scanned_items = 0
        
        for location in locations:
            if self.should_stop:
                return
                
            # Update progress
            progress = int((scanned_items / total_items) * 100)
            self.update_progress.emit(progress)
            
            self.update_log.emit(f"Scanning: {location}")
            
            try:
                # Simulate scanning files in this location
                self.simulate_directory_scan(location)
            except Exception as e:
                self.update_log.emit(f"Error scanning {location}: {str(e)}")
            
            scanned_items += 1
        
        self.update_progress.emit(100)
        self.update_log.emit(f"Quick scan complete. Found {self.threats_found} potential threats.")
    
    def full_scan(self):
        """Perform a full system scan"""
        self.update_log.emit("Performing full system scan. This may take a while...")
        
        # Get drives to scan
        drives = []
        for drive_letter in range(ord('C'), ord('Z') + 1):
            drive = chr(drive_letter) + ":\\"
            if os.path.exists(drive):
                drives.append(drive)
        
        total_drives = len(drives)
        scanned_drives = 0
        
        for drive in drives:
            if self.should_stop:
                return
                
            # Update progress - we'll allocate 95% of the progress to the scanning
            progress = int((scanned_drives / total_drives) * 95)
            self.update_progress.emit(progress)
            
            self.update_log.emit(f"Scanning drive: {drive}")
            
            try:
                # Simulate scanning this drive (just first level for simulation)
                self.simulate_directory_scan(drive, depth=0)
            except Exception as e:
                self.update_log.emit(f"Error scanning {drive}: {str(e)}")
            
            scanned_drives += 1
            
            # Simulate deeper scan by sleeping
            time.sleep(2)
        
        self.update_progress.emit(100)
        self.update_log.emit(f"Full scan complete. Found {self.threats_found} potential threats.")
    
    def custom_scan(self, targets):
        """Scan specific targets selected by user"""
        if not targets:
            self.update_log.emit("No targets specified for custom scan.")
            self.update_progress.emit(100)
            return
            
        self.update_log.emit(f"Starting custom scan of {len(targets)} locations...")
        
        total_targets = len(targets)
        scanned_targets = 0
        
        for target in targets:
            if self.should_stop:
                return
                
            # Update progress
            progress = int((scanned_targets / total_targets) * 100)
            self.update_progress.emit(progress)
            
            self.update_log.emit(f"Scanning: {target}")
            
            try:
                # Check if target exists
                if os.path.exists(target):
                    # Simulate scanning
                    if os.path.isdir(target):
                        self.simulate_directory_scan(target)
                    else:
                        self.simulate_file_scan(target)
                else:
                    self.update_log.emit(f"Warning: Target does not exist: {target}")
            except Exception as e:
                self.update_log.emit(f"Error scanning {target}: {str(e)}")
            
            scanned_targets += 1
        
        self.update_progress.emit(100)
        self.update_log.emit(f"Custom scan complete. Found {self.threats_found} potential threats.")
    
    def simulate_directory_scan(self, directory, depth=1):
        """Simulate scanning a directory for threats"""
        try:
            # Check if we have permission to access the directory
            items = os.listdir(directory)
            
            # Simulate finding some files with issues (for demo purposes)
            for item in items[:10]:  # Limit to first 10 items for simulation
                if self.should_stop:
                    return
                    
                item_path = os.path.join(directory, item)
                
                # Simulate scanning the file
                if os.path.isfile(item_path):
                    self.simulate_file_scan(item_path)
                
                # If this is a directory and we're recursing, scan it too
                if os.path.isdir(item_path) and depth > 0:
                    # Only recurse for a few folders (for simulation)
                    if random.random() < 0.1:  # 10% chance to recurse for demo
                        self.simulate_directory_scan(item_path, depth - 1)
                
                # Pause briefly to simulate work
                time.sleep(0.05)
                
        except PermissionError:
            self.update_log.emit(f"Permission denied for: {directory}")
        except Exception as e:
            self.update_log.emit(f"Error scanning directory {directory}: {str(e)}")
    
    def simulate_file_scan(self, file_path):
        """Simulate scanning a single file for threats"""
        try:
            # Log that we're scanning this file
            self.update_log.emit(f"Scanning file: {os.path.basename(file_path)}")
            
            # Simulate the scan by sleeping a bit
            time.sleep(0.1)
            
            # Randomly decide if this file has a threat (for demo)
            if random.random() < 0.02:  # 2% chance to find a "threat"
                threat_type = random.choice([
                    "Potential malware", 
                    "Suspicious script", 
                    "Unwanted adware",
                    "PUP (Potentially Unwanted Program)",
                    "Suspicious behavior detected"
                ])
                
                self.threats_found += 1
                self.update_log.emit(f"⚠️ Found potential threat: {os.path.basename(file_path)}")
                self.found_threat.emit(file_path, threat_type)
        
        except PermissionError:
            self.update_log.emit(f"Permission denied for: {file_path}")
        except Exception as e:
            self.update_log.emit(f"Error scanning file {file_path}: {str(e)}")
