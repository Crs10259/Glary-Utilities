import os
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QSize

def get_resource_path(relative_path):
    """获取资源文件的绝对路径"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if relative_path.startswith("/"):
        relative_path = relative_path[1:]
    return os.path.join(base_dir, relative_path)

def load_icon(icon_path, fallback=None):
    """安全加载图标
    
    Args:
        icon_path: 图标路径（相对于src目录）
        fallback: 若加载失败，使用的备用图标路径
        
    Returns:
        QIcon对象或None
    """
    if not icon_path:
        return None
        
    # 获取完整路径
    full_path = get_resource_path(icon_path)
    
    if not os.path.exists(full_path):
        print(f"警告: 找不到图标 {full_path}")
        if fallback:
            return load_icon(fallback)
        return None
    
    try:
        icon = QIcon(full_path)
        if icon.isNull():
            print(f"警告: 加载的图标为空 {full_path}")
            if fallback:
                return load_icon(fallback)
            return None
        return icon
    except Exception as e:
        print(f"加载图标时出错 {full_path}: {str(e)}")
        if fallback:
            return load_icon(fallback)
        return None

def load_pixmap(icon_path, size=QSize(32, 32), fallback=None):
    """安全加载像素图
    
    Args:
        icon_path: 图标路径（相对于src目录）
        size: 图标大小
        fallback: 若加载失败，使用的备用图标路径
        
    Returns:
        QPixmap对象或None
    """
    icon = load_icon(icon_path, fallback)
    if not icon:
        return None
        
    try:
        pixmap = icon.pixmap(size)
        if pixmap.isNull():
            print(f"警告: 加载的像素图为空 {icon_path}")
            return None
        return pixmap
    except Exception as e:
        print(f"将图标转换为像素图时出错 {icon_path}: {str(e)}")
        return None 