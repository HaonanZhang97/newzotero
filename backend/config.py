"""
第3步：Flask配置管理
==================

学习目标：
- 什么是Flask配置
- 为什么需要多环境配置
- Development vs Production的区别
- 如何在应用工厂中使用配置
"""

import os

# ============================================
# 第3步：最基础的配置类
# ============================================

class Config:
    """
    基础配置类 - 所有环境共享的配置
    
    为什么用类而不是字典？
    1. 更好的代码组织
    2. 可以继承和扩展
    3. IDE支持更好
    4. 可以添加方法处理复杂逻辑
    """
    
    # 基本设置
    SECRET_KEY = 'dev-secret-key-for-learning'  # 开发用密钥
    DEBUG = False  # 默认不开启调试
    
    # API设置
    API_VERSION = 'v1'
    API_PREFIX = '/api/v1'
    
    print("📋 Base Config class loaded")


class DevelopmentConfig(Config):
    """
    开发环境配置 - 继承基础配置
    
    开发环境特点：
    - 开启DEBUG模式
    - 详细的错误信息
    - 自动重载代码
    """
    DEBUG = True  # 开启调试模式
    ENV = 'development'
    
    print("🔧 Development Config class loaded")


class ProductionConfig(Config):
    """
    生产环境配置 - 继承基础配置
    
    生产环境特点：
    - 关闭DEBUG模式
    - 从环境变量获取敏感信息
    - 更严格的安全设置
    """
    DEBUG = False  # 关闭调试模式
    ENV = 'production'
    
    # 生产环境从环境变量获取密钥
    SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback-secret-key')
    
    print("🚀 Production Config class loaded")


# ============================================
# 第3步：配置选择器
# ============================================

# 配置映射字典
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig  # 默认使用开发环境
}

def get_config(env_name=None):
    """
    根据环境名称获取配置类
    
    Args:
        env_name: 环境名称 ('development', 'production')
        
    Returns:
        对应的配置类
    """
    if env_name is None:
        env_name = 'default'
    
    config_class = config_map.get(env_name, DevelopmentConfig)
    print(f"📊 Selected config: {config_class.__name__}")
    return config_class

# ============================================
# 第4步将要添加的功能（暂时注释掉）
# ============================================
# TODO: 第4步解锁 - 添加更多环境
# class TestingConfig(Config):
#     TESTING = True
#     WTF_CSRF_ENABLED = False

# TODO: 第5步解锁 - 添加数据库配置
# class Config:
#     SQLALCHEMY_DATABASE_URI = '...'
#     SQLALCHEMY_TRACK_MODIFICATIONS = False

# TODO: 第6步解锁 - 添加文件上传配置
# class Config:
#     UPLOAD_FOLDER = 'uploads'
#     MAX_CONTENT_LENGTH = 16 * 1024 * 1024

print("⚙️ config.py loaded - Step 3 ready!")
