import os
import subprocess
from .base_tools import BaseThread
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer

class DismThread(BaseThread):
    """DISM操作的工作线程"""
    progress_updated = pyqtSignal(str)
    operation_completed = pyqtSignal(bool, str)
    
    def __init__(self, operation):
        super().__init__()
        self.operation = operation  # 其中之一: check_health, scan_health, restore_health, cleanup_image
    
    def run(self):
        """运行工作线程"""
        if not self.platform_manager.is_windows():
            self.progress_updated.emit("DISM仅在Windows上可用")
            self.operation_completed.emit(False, "此平台不支持该操作")
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
                self.progress_updated.emit(f"未知操作: {self.operation}")
                self.operation_completed.emit(False, "未知操作")
        except Exception as e:
            self.progress_updated.emit(f"执行操作时出错: {str(e)}")
            self.operation_completed.emit(False, str(e))
    
    def check_health(self):
        """检查Windows映像的健康状况"""
        self.progress_updated.emit("正在检查Windows映像健康状况...")
        proc = subprocess.Popen(
            ["dism", "/Online", "/Cleanup-Image", "/CheckHealth"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            universal_newlines=True
        )
        
        self._process_output(proc)
    
    def scan_health(self):
        """扫描Windows映像的健康状况"""
        self.progress_updated.emit("正在扫描Windows映像健康状况...")
        proc = subprocess.Popen(
            ["dism", "/Online", "/Cleanup-Image", "/ScanHealth"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            universal_newlines=True
        )
        
        self._process_output(proc)
    
    def restore_health(self):
        """恢复Windows映像的健康状况"""
        self.progress_updated.emit("正在恢复Windows映像健康状况...")
        proc = subprocess.Popen(
            ["dism", "/Online", "/Cleanup-Image", "/RestoreHealth"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            universal_newlines=True
        )
        
        self._process_output(proc)
    
    def cleanup_image(self):
        """清理Windows映像"""
        self.progress_updated.emit("正在清理Windows映像...")
        proc = subprocess.Popen(
            ["dism", "/Online", "/Cleanup-Image", "/StartComponentCleanup"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            universal_newlines=True
        )
        
        self._process_output(proc)
    
    def _process_output(self, proc):
        """处理DISM命令的输出"""
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
            last_line = f"操作失败，返回代码 {proc.returncode}"
        
        self.operation_completed.emit(success, last_line)
