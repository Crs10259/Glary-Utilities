#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Settings Manager - 提供从utils/settings_manager.py到src/settings_manager.py的兼容层
这解决了模块导入问题
"""

from utils.settings_manager import Settings

# 导出Settings类，确保与utils/settings_manager.py中相同
__all__ = ['Settings'] 