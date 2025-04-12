#!/bin/bash

echo "=== Glary Utilities Build Script (Linux/Mac) ==="
echo

# 检查 Python 安装
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Please install Python 3.8 or later"
    exit 1
fi

# 检查 Python 版本
python_version=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
if (( $(echo "$python_version < 3.8" | bc -l) )); then
    echo "Error: Python 3.8 or later is required (found $python_version)"
    exit 1
fi

# 检查 pip 安装
if ! python3 -m pip --version &> /dev/null; then
    echo "Error: pip is not installed"
    echo "Installing pip..."
    python3 -m ensurepip --default-pip
    if [ $? -ne 0 ]; then
        echo "Failed to install pip"
        exit 1
    fi
fi

# 创建虚拟环境
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        echo "Failed to create virtual environment"
        exit 1
    fi
fi

# 激活虚拟环境
echo "Activating virtual environment..."
source .venv/bin/activate
if [ $? -ne 0 ]; then
    echo "Failed to activate virtual environment"
    exit 1
fi

# 升级 pip
echo "Upgrading pip..."
pip install --upgrade pip
if [ $? -ne 0 ]; then
    echo "Warning: Failed to upgrade pip"
fi

# 安装依赖
echo "Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Failed to install dependencies"
    exit 1
fi

# 设置执行权限
echo "Setting executable permissions..."
chmod +x src/main.py

echo
echo "Build completed successfully!"
echo "To start the application, run: python src/main.py"
fi