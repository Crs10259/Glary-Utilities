import os
import shutil
import subprocess
import tempfile
from .base_tools import BaseThread
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer

class CleanerWorker(BaseThread):
    """扫描和清理文件的工作线程"""
    progress_updated = pyqtSignal(int, str)
    scan_completed = pyqtSignal(dict)
    clean_completed = pyqtSignal(dict)
    
    def __init__(self, options, exclusions, extensions, operation="scan"):
        super().__init__()
        self.options = options  # 要扫描的选项字典
        self.exclusions = exclusions  # 排除的目录/文件列表
        self.extensions = extensions  # 要清理的文件扩展名列表
        self.operation = operation  # "scan" 或 "clean"
        self.stop_requested = False
    
    def run(self):
        """运行工作线程"""
        if self.operation == "scan":
            self.scan_files()
        elif self.operation == "clean":
            self.clean_files()
    
    def stop(self):
        """请求工作线程停止"""
        self.stop_requested = True
    
    def scan_files(self):
        """扫描不必要的文件"""
        results = {
            "files": [],
            "total_size": 0,
            "count": 0
        }
        
        # 获取临时目录
        temp_dir = tempfile.gettempdir()
        
        # 获取用户主目录
        home_dir = os.path.expanduser("~")
        
        progress = 0
        self.progress_updated.emit(progress, "开始扫描...")
        
        # 扫描临时文件
        if self.options.get("temp_files", False):
            self.progress_updated.emit(progress, "扫描临时文件...")
            temp_files = self.scan_directory(temp_dir)
            results["files"].extend(temp_files)
            progress += 20
            self.progress_updated.emit(progress, f"找到 {len(temp_files)} 个临时文件")
        
        # 扫描回收站
        if self.options.get("recycle_bin", False):
            self.progress_updated.emit(progress, "扫描回收站...")
            recycle_files = self.scan_recycle_bin()
            results["files"].extend(recycle_files)
            progress += 20
            self.progress_updated.emit(progress, f"找到 {len(recycle_files)} 个回收站文件")
        
        # 扫描缓存文件（浏览器）
        if self.options.get("cache_files", False):
            self.progress_updated.emit(progress, "扫描缓存文件...")
            cache_files = self.scan_browser_caches(home_dir)
            results["files"].extend(cache_files)
            progress += 20
            self.progress_updated.emit(progress, f"找到 {len(cache_files)} 个缓存文件")
        
        # 扫描日志文件
        if self.options.get("log_files", False):
            self.progress_updated.emit(progress, "扫描日志文件...")
            log_files = self.scan_log_files()
            results["files"].extend(log_files)
            progress += 20
            self.progress_updated.emit(progress, f"找到 {len(log_files)} 个日志文件")
        
        # 计算总数
        results["count"] = len(results["files"])
        results["total_size"] = sum(file["size"] for file in results["files"])
        
        self.progress_updated.emit(100, f"扫描完成。找到 {results['count']} 个文件 ({self.format_size(results['total_size'])})")
        self.scan_completed.emit(results)
    
    def clean_files(self):
        """清理选定的文件"""
        results = {
            "cleaned_count": 0,
            "cleaned_size": 0,
            "failed_count": 0
        }
        
        total_files = len(self.options.get("files", []))
        if total_files == 0:
            self.progress_updated.emit(100, "没有文件可清理")
            self.clean_completed.emit(results)
            return
        
        self.progress_updated.emit(0, f"清理 {total_files} 个文件...")
        
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
                    self.progress_updated.emit(progress, f"清理了 {results['cleaned_count']} 个文件 ({self.format_size(results['cleaned_size'])})")
                else:
                    results["failed_count"] += 1
            except Exception as e:
                self.logger.error(f"清理 {file_path} 时出错: {e}")
                results["failed_count"] += 1
        
        self.progress_updated.emit(100, f"清理完成。清理了 {results['cleaned_count']} 个文件 ({self.format_size(results['cleaned_size'])})")
        self.clean_completed.emit(results)
    
    def scan_directory(self, directory):
        """扫描目录以查找要清理的文件"""
        files = []
        
        try:
            for root, dirs, filenames in os.walk(directory):
                if self.stop_requested:
                    break
                    
                # 跳过排除的目录
                dirs[:] = [d for d in dirs if os.path.join(root, d) not in self.exclusions]
                
                for filename in filenames:
                    file_path = os.path.join(root, filename)
                    
                    # 跳过排除的文件
                    if file_path in self.exclusions:
                        continue
                    
                    # 仅包括具有指定扩展名的文件（如果提供了扩展名）
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
                        self.logger.error(f"获取文件信息时出错 {file_path}: {e}")
        except Exception as e:
            self.logger.error(f"扫描目录 {directory} 时出错: {e}")
        
        return files
    
    def scan_recycle_bin(self):
        """扫描回收站中的文件"""
        files = []
        
        try:
            if self.platform_manager.is_windows():
                # Windows回收站位于C:\\$Recycle.Bin
                recycle_bin = "C:\\$Recycle.Bin"
                if os.path.exists(recycle_bin):
                    files = self.scan_directory(recycle_bin)
            elif self.platform_manager.is_mac():  # macOS
                # macOS垃圾箱位于~/.Trash
                trash_path = os.path.expanduser("~/.Trash")
                if os.path.exists(trash_path):
                    files = self.scan_directory(trash_path)
            elif self.platform_manager.is_linux():
                # Linux垃圾箱位于~/.local/share/Trash
                trash_path = os.path.expanduser("~/.local/share/Trash")
                if os.path.exists(trash_path):
                    files = self.scan_directory(trash_path)
        except Exception as e:
            self.logger.error(f"扫描回收站时出错: {e}")
        
        return files
    
    def scan_browser_caches(self, home_dir):
        """扫描浏览器缓存目录"""
        files = []
        
        try:
            system = self.platform_manager.current_system
            
            # Chrome缓存
            chrome_cache = None
            if system == "Windows":
                chrome_cache = os.path.join(home_dir, "AppData", "Local", "Google", "Chrome", "User Data", "Default", "Cache")
            elif system == "Darwin":
                chrome_cache = os.path.join(home_dir, "Library", "Caches", "Google", "Chrome")
            elif system == "Linux":
                chrome_cache = os.path.join(home_dir, ".cache", "google-chrome")
            
            if chrome_cache and os.path.exists(chrome_cache):
                files.extend(self.scan_directory(chrome_cache))
            
            # Firefox缓存
            firefox_cache = None
            if system == "Windows":
                firefox_cache = os.path.join(home_dir, "AppData", "Local", "Mozilla", "Firefox", "Profiles")
            elif system == "Darwin":
                firefox_cache = os.path.join(home_dir, "Library", "Caches", "Firefox")
            elif system == "Linux":
                firefox_cache = os.path.join(home_dir, ".cache", "mozilla", "firefox")
            
            if firefox_cache and os.path.exists(firefox_cache):
                # 对于Firefox，我们需要扫描每个配置文件
                if system == "Windows":
                    # 扫描每个配置文件目录
                    for profile in os.listdir(firefox_cache):
                        profile_cache = os.path.join(firefox_cache, profile, "cache2")
                        if os.path.exists(profile_cache):
                            files.extend(self.scan_directory(profile_cache))
                else:
                    files.extend(self.scan_directory(firefox_cache))
            
            # Edge缓存（仅限Windows）
            if system == "Windows":
                edge_cache = os.path.join(home_dir, "AppData", "Local", "Microsoft", "Edge", "User Data", "Default", "Cache")
                if os.path.exists(edge_cache):
                    files.extend(self.scan_directory(edge_cache))
            
        except Exception as e:
            self.logger.error(f"扫描浏览器缓存时出错: {e}")
        
        return files
    
    def scan_log_files(self):
        """扫描日志文件"""
        files = []
        
        try:
            system = self.platform_manager.current_system
            
            if system == "Windows":
                # Windows日志
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
                                        self.logger.error(f"获取日志文件信息时出错: {e}")
            elif system == "Darwin" or system == "Linux":
                # macOS/Linux日志
                log_paths = [
                    "/var/log",
                    os.path.expanduser("~/Library/Logs") if system == "Darwin" else None,
                ]
                
                for log_path in log_paths:
                    if log_path and os.path.exists(log_path):
                        log_files = self.scan_directory(log_path)
                        # 仅包括.log文件
                        log_files = [f for f in log_files if f["name"].endswith(".log")]
                        files.extend(log_files)
        except Exception as e:
            self.logger.error(f"扫描日志文件时出错: {e}")
        
        return files
    
    def format_size(self, size_bytes):
        """将字节格式化为人类可读的大小"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
            if size_bytes < 1024:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024