import os
import re
from pathlib import Path

def contains_chinese(text):
    """检查文本是否包含中文字符"""
    # Unicode范围：中文字符的Unicode范围
    chinese_pattern = re.compile(r'[\u4e00-\u9fff]')
    return bool(chinese_pattern.search(str(text)))

def check_file_content(file_path):
    """检查文件内容是否包含中文"""
    # 检查文件扩展名
    if file_path.suffix.lower() in {'.pyc', '.pyo', '.pyd', '.so', '.dll', '.exe', 
                                  '.jpg', '.jpeg', '.png', '.gif', '.ico', '.svg',
                                  '.woff', '.woff2', '.ttf', '.eot', '.db', 
                                  '.sqlite', '.sqlite3', '.pdf', '.zip', '.tar', 
                                  '.gz', '.rar'}:
        return False

    try:
        # 尝试以不同编码读取文件
        encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030']
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                    if contains_chinese(content):
                        return True
            except UnicodeDecodeError:
                continue
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return False

def find_chinese_files(start_path):
    """查找包含中文的文件"""
    # 要排除的目录
    exclude_dirs = {'.venv', '.git', '__pycache__', 'node_modules', 'dist', 
                   'build', 'cache', 'uploads', 'temp', 'logs'}
    
    chinese_files = []

    for root, dirs, files in os.walk(start_path):
        # 从遍历列表中移除要排除的目录
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            file_path = Path(root) / file
            
            # 检查文件名是否包含中文
            if contains_chinese(file):
                chinese_files.append((str(file_path), "Chinese in filename"))
                continue
            
            # 检查文件内容是否包含中文
            if check_file_content(file_path):
                chinese_files.append((str(file_path), "Chinese in content"))

    return chinese_files

def main():
    # 获取当前目录
    current_dir = Path.cwd()
    print("Searching for files containing Chinese characters...")
    
    # 查找包含中文的文件
    chinese_files = find_chinese_files(current_dir)
    
    # 打印结果
    if chinese_files:
        print("\nFound files containing Chinese characters:")
        print("-" * 80)
        for file_path, reason in chinese_files:
            print(f"{file_path}\n    {reason}")
        print("-" * 80)
        print(f"Total files found: {len(chinese_files)}")
    else:
        print("No files containing Chinese characters were found.")

if __name__ == '__main__':
    main() 