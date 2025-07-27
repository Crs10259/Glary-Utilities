# Linux 优化说明

## 概述

本文档说明了在Linux系统上对Glary Utilities应用程序进行的性能优化和窗口移动功能改进。

## 主要优化内容

### 1. 窗口移动功能优化

#### 问题描述
在Linux系统上，使用无边框窗口（`Qt.FramelessWindowHint`）可能导致窗口无法正常移动。

#### 解决方案
- **统一窗口风格**: 在所有平台上都使用自定义无边框窗口
- **窗口标志优化**: 使用 `Qt.FramelessWindowHint` 实现完全自定义的窗口装饰
- **鼠标事件改进**: 增强鼠标事件处理，支持通过标题栏和窗口边缘拖动
- **边界检查**: 确保窗口不会移出屏幕边界

#### 代码实现
```python
# 在所有平台上都使用自定义无边框窗口
self.setWindowFlags(Qt.FramelessWindowHint)
self.setAttribute(Qt.WA_TranslucentBackground)

# Linux特定的窗口属性优化
if self.platform_manager.is_linux():
    # 确保窗口可以正确显示和交互
    self.setAttribute(Qt.WA_X11NetWmWindowTypeDesktop, False)
    self.setAttribute(Qt.WA_ShowWithoutActivating, False)
    # 设置窗口类型为正常窗口
    self.setAttribute(Qt.WA_X11NetWmWindowTypeNormal, True)
```

### 2. 性能优化

#### 动画优化
- **减少动画持续时间**: 在Linux上将动画时间从400ms减少到200ms
- **简化缓动曲线**: 使用更简单的 `QEasingCurve.OutCubic` 替代复杂的 `OutQuint`
- **禁用复杂动画**: 在Linux上默认禁用页面切换动画和图标悬停动画

#### 视觉效果优化
- **禁用阴影效果**: 在Linux上禁用窗口阴影以提高性能
- **优化透明度**: 减少透明度动画的复杂度

#### 设置选项
新增了"优化Linux性能"设置选项，允许用户控制是否启用性能优化：
- 默认启用
- 可通过设置界面关闭
- 影响动画效果和窗口行为

### 3. 平台特定处理

#### 平台管理器
使用 `PlatformManager` 类来检测当前操作系统：
```python
from tools.base_tools import PlatformManager
platform_manager = PlatformManager()

if platform_manager.is_linux():
    # Linux特定代码
elif platform_manager.is_windows():
    # Windows特定代码
elif platform_manager.is_mac():
    # macOS特定代码
```

#### 统一体验
在所有平台上提供一致的用户体验：
- 统一的自定义无边框窗口
- 一致的窗口移动和交互行为
- 跨平台的视觉效果

## 测试

### 测试脚本
提供了 `test_linux_window.py` 测试脚本来验证窗口移动功能：

```bash
python test_linux_window.py
```

### 测试内容
1. 窗口拖动功能
2. 平台检测
3. 鼠标事件处理
4. 边界检查

## 使用方法

### 启用Linux优化
1. 打开应用程序设置
2. 在"常规"选项卡中找到"优化Linux性能"选项
3. 确保该选项已启用（默认启用）

### 自定义设置
- **启用动画**: 关闭Linux优化以启用完整动画效果
- **禁用动画**: 在设置中关闭"启用动画效果"

## 兼容性

### 支持的Linux发行版
- Ubuntu 18.04+
- Debian 10+
- Fedora 30+
- CentOS 8+
- Arch Linux
- 其他基于X11的Linux发行版

### 桌面环境
- GNOME
- KDE Plasma
- XFCE
- Cinnamon
- MATE
- 其他支持X11的桌面环境

## 故障排除

### 窗口仍然无法移动
1. 确保"优化Linux性能"选项已启用
2. 尝试重启应用程序
3. 检查桌面环境是否支持窗口管理
4. 运行测试脚本验证功能

### 性能问题
1. 关闭所有动画效果
2. 检查系统资源使用情况
3. 更新图形驱动程序
4. 考虑使用更轻量级的桌面环境

### 视觉效果问题
1. 检查是否启用了合成器
2. 更新图形驱动程序
3. 调整桌面环境设置

## 技术细节

### 窗口标志说明
- `Qt.FramelessWindowHint`: 无边框窗口，实现完全自定义的窗口装饰
- `Qt.WA_TranslucentBackground`: 支持透明背景
- `Qt.WA_X11NetWmWindowTypeNormal`: 设置窗口类型为正常窗口（Linux）
- `Qt.WA_X11NetWmWindowTypeDesktop`: 禁用桌面窗口类型（Linux）

### 性能优化策略
1. **减少动画复杂度**: 简化缓动曲线和持续时间
2. **条件渲染**: 根据平台选择性启用视觉效果
3. **事件优化**: 优化鼠标事件处理逻辑
4. **内存管理**: 减少不必要的对象创建

## 更新日志

### v1.1.0
- 统一窗口风格，在所有平台使用自定义无边框窗口
- 改进窗口移动功能，支持标题栏和边缘拖动
- 优化Linux兼容性，确保窗口正确显示和交互
- 保持性能优化设置

### v1.0.0
- 初始Linux优化实现
- 添加平台检测功能
- 实现窗口移动优化
- 添加性能优化设置

### 未来计划
- 支持Wayland显示服务器
- 进一步优化动画性能
- 添加更多平台特定优化
- 改进用户界面响应性 