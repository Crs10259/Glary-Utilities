import os
import subprocess
from .base_tools import BaseThread
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer

class NetworkResetThread(BaseThread):
    """Worker thread for network reset operations"""
    progress_updated = pyqtSignal(str)
    operation_completed = pyqtSignal(bool)
    
    def __init__(self, operations):
        super().__init__()
        self.operations = operations  # Dictionary of operations to perform
    
    def run(self):
        """Run the worker thread"""
        success = True
        
        if not self.platform_manager.is_windows():
            self.progress_updated.emit("Network reset is only supported on Windows")
            self.operation_completed.emit(False)
            return
        
        try:
            # Flush DNS
            if self.operations.get("flush_dns", False):
                self.progress_updated.emit("Flushing DNS cache...")
                success = success and self.flush_dns()
            
            # Reset Winsock
            if self.operations.get("reset_winsock", False):
                self.progress_updated.emit("Resetting Winsock...")
                success = success and self.reset_winsock()
            
            # Reset TCP/IP
            if self.operations.get("reset_tcp_ip", False):
                self.progress_updated.emit("Resetting TCP/IP stack...")
                success = success and self.reset_tcp_ip()
            
            # Reset Firewall
            if self.operations.get("reset_firewall", False):
                self.progress_updated.emit("Resetting firewall settings...")
                success = success and self.reset_firewall()
            
            self.progress_updated.emit("Network reset operations completed")
            self.operation_completed.emit(success)
        except Exception as e:
            self.progress_updated.emit(f"Error performing network reset: {str(e)}")
            self.operation_completed.emit(False)
    
    def flush_dns(self):
        """Flush DNS cache"""
        try:
            # Run ipconfig /flushdns
            proc = subprocess.run(["ipconfig", "/flushdns"], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE,
                                 text=True,
                                 check=True)
            
            self.progress_updated.emit(proc.stdout)
            return True
        except subprocess.CalledProcessError as e:
            self.progress_updated.emit(f"Error flushing DNS: {e.stderr}")
            return False
    
    def reset_winsock(self):
        """Reset Winsock catalog"""
        try:
            # Run netsh winsock reset
            proc = subprocess.run(["netsh", "winsock", "reset"], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE,
                                 text=True,
                                 check=True)
            
            self.progress_updated.emit(proc.stdout)
            return True
        except subprocess.CalledProcessError as e:
            self.progress_updated.emit(f"Error resetting Winsock: {e.stderr}")
            return False
    
    def reset_tcp_ip(self):
        """Reset TCP/IP stack"""
        try:
            # Run netsh int ip reset
            proc = subprocess.run(["netsh", "int", "ip", "reset"], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE,
                                 text=True,
                                 check=True)
            
            self.progress_updated.emit(proc.stdout)
            return True
        except subprocess.CalledProcessError as e:
            self.progress_updated.emit(f"Error resetting TCP/IP: {e.stderr}")
            return False
    
    def reset_firewall(self):
        """Reset Windows Firewall settings"""
        try:
            # Run netsh advfirewall reset
            proc = subprocess.run(["netsh", "advfirewall", "reset"], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE,
                                 text=True,
                                 check=True)
            
            self.progress_updated.emit(proc.stdout)
            return True
        except subprocess.CalledProcessError as e:
            self.progress_updated.emit(f"Error resetting firewall: {e.stderr}")
            return False
