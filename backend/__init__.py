"""
NewZotero Backend - RESTful Knowledge Management System
======================================================

学习Flask项目结构 - 一步一步来！

第1步：理解包的基本结构
- 什么是 __init__.py
- 版本信息管理
- 基本导入概念
"""

# ============================================
# 第1步：包的基本信息（必须的）
# ============================================
__version__ = "0.1.0"
__author__ = "Haonan Zhang"
__title__ = "NewZotero Backend"
__description__ = "Learning Flask step by step"

# 版本信息字典（方便其他地方使用）
VERSION_INFO = {
    "version": __version__,
    "title": __title__, 
    "description": __description__,
    "author": __author__
}

# ============================================
# 第3步：导入核心组件（继续解锁！）
# ============================================
# 第2步解锁 - 导入应用工厂
from .app import create_app

# 第3步解锁 - 导入配置类
from .config import Config, DevelopmentConfig, ProductionConfig, get_config

# ============================================
# 第4步：定义公共接口（暂时注释掉）
# ============================================
# TODO: 第4步解锁 - 定义包的公共接口
__all__ = [
    # 基本信息（现在就可以用）
    "__version__",
    "__author__", 
    "__title__",
    "__description__",
    "VERSION_INFO",
    
    # 核心组件（随着学习进展逐步解锁）
    "create_app",        # 第2步解锁 ✅
    "Config",            # 第3步解锁 ✅
    "DevelopmentConfig", # 第3步解锁 ✅
    "ProductionConfig",  # 第3步解锁 ✅
    "get_config",        # 第3步解锁 ✅
]

# ============================================
# 第5步：包初始化（暂时注释掉）
# ============================================
# TODO: 第5步解锁 - 包初始化和日志
# import logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)
# logger.info(f"Initializing {__title__} v{__version__}")

print(f"📦 Package '{__title__}' v{__version__} loaded!")
print(f"👤 Author: {__author__}")
print(f"📝 Description: {__description__}")
print(f"✅ Step 7 complete: Repository layer integrated!")
print(f"🗄️ Full architecture: Controller → Service → Repository → Storage")
