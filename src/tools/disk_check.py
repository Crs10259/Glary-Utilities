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
        """检查磁盘错误而不修复它们"""
        # 验证驱动器
        if not os.path.exists(self.drive):
            self.progress_updated.emit(f"驱动器 {self.drive} 不存在或不可访问")
            self.operation_completed.emit(False)
            return
        
        self.progress_updated.emit(f"正在检查驱动器 {self.drive}...")
        
        # 构建命令参数
        cmd = ["chkdsk", self.drive]
        
        # 添加必要的选项
        if self.check_file_system:
            # 文件系统检查不需要额外参数
            pass
        
        if self.check_bad_sectors:
            cmd.append("/B")  # 检查坏扇区
        
        self.progress_updated.emit(f"运行命令: {' '.join(cmd)}")
        
        try:
            # 使用self.platform_manager运行chkdsk
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                universal_newlines=True,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            
            # 处理输出
            while True:
                line = proc.stdout.readline()
                if not line:
                    break
                
                line = line.strip()
                if line:
                    self.progress_updated.emit(line)
            
            proc.wait()
            
            if proc.returncode == 0:
                self.progress_updated.emit("磁盘检查成功完成")
                self.operation_completed.emit(True)
            else:
                self.progress_updated.emit(f"磁盘检查失败，返回代码 {proc.returncode}")
                self.operation_completed.emit(False)
        except FileNotFoundError:
            self.progress_updated.emit("错误: 找不到chkdsk命令。请确保您在Windows系统上运行此程序。")
            self.operation_completed.emit(False)
        except PermissionError:
            self.progress_updated.emit("错误: 权限被拒绝。请尝试以管理员身份运行程序。")
            self.operation_completed.emit(False)
        except Exception as e:
            self.progress_updated.emit(f"运行磁盘检查时出错: {str(e)}")
            self.operation_completed.emit(False)
    
    def repair_disk(self):
        """Check and repair disk errors"""
        self.progress_updated.emit(f"正在检查并修复驱动器 {self.drive}...")
        
        # Build command arguments
        cmd = ["chkdsk", self.drive, "/F"]  # /F to fix errors
        
        if self.check_bad_sectors:
            cmd.append("/R")  # Repair bad sectors
        
        self.progress_updated.emit(f"运行命令: {' '.join(cmd)}")
        self.progress_updated.emit("注意: 此操作可能需要系统重新启动")
        
        try:
            # 使用self.platform_manager运行chkdsk修复命令
            result = self.platform_manager.run_command(cmd)
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if line.strip():
                        self.progress_updated.emit(line.strip())
                
                self.progress_updated.emit("磁盘修复已成功安排")
                self.operation_completed.emit(True)
            else:
                for line in result.stdout.split('\n'):
                    if line.strip():
                        self.progress_updated.emit(line.strip())
                
                if result.stderr:
                    self.progress_updated.emit(f"错误: {result.stderr}")
                
                self.progress_updated.emit(f"磁盘修复失败，返回代码 {result.returncode}")
                self.operation_completed.emit(False)
        except Exception as e:
            self.progress_updated.emit(f"运行磁盘修复时出错: {str(e)}")
            self.operation_completed.emit(False)