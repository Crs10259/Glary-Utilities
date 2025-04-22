import os
import re
import glob
from utils.resource_manager import ResourceManager

def check_resources():
    """检查项目中的资源引用，确保都使用了正确的路径"""
    
    # 确保资源目录存在
    ResourceManager.initialize()
    
    # 旧的资源路径
    old_patterns = [
        r'[\"\']assets/images/([^\"\']+)[\"\']',
        r'[\"\']src/assets/images/([^\"\']+)[\"\']',
        r'[\"\']assets/icons/([^\"\']+)[\"\']',
        r'url\(assets/images/([^)]+)\)',
        r'url\(src/assets/images/([^)]+)\)'
    ]
    
    # 扫描的文件类型
    file_types = ['*.py', '*.ui', '*.qss', '*.css', '*.json']
    
    # 需要检查的目录
    directories = ['src']
    
    issues_found = False
    
    for directory in directories:
        for file_type in file_types:
            pattern = os.path.join(directory, '**', file_type)
            files = glob.glob(pattern, recursive=True)
            
            for file_path in files:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    try:
                        content = f.read()
                    except Exception as e:
                        print(f"无法读取文件 {file_path}: {e}")
                        continue
                
                # 检查所有模式
                for pattern in old_patterns:
                    matches = re.findall(pattern, content)
                    if matches:
                        issues_found = True
                        print(f"在文件 {file_path} 中发现旧的资源引用:")
                        for match in matches:
                            print(f"    - {match}")
    
    if not issues_found:
        print("未发现资源路径问题，所有资源路径都已正确使用。")
    else:
        print("\n请确保所有资源路径使用以下方式引用:")
        print("1. 使用 ResourceManager 类方法获取资源路径")
        print("2. 直接使用 'resources/images/' 或 'resources/icons/' 路径")
    
    return not issues_found

if __name__ == "__main__":
    check_resources() 