"""
第8步：Flask配置管理 - 添加数据库支持
==================================

学习目标：
- 添加SQLAlchemy数据库配置
- 环境变量管理
- 数据库URI配置
- Flask-Migrate集成
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# ============================================
# 第8步：增强的配置类 - 添加数据库支持
# ============================================

class Config:
    """
    基础配置类 - 所有环境共享的配置
    
    第8步新增：
    - SQLAlchemy数据库配置
    - 环境变量支持
    - 数据库连接池配置
    """
    
    # 基本设置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-for-learning'
    DEBUG = False
    
    # API设置
    API_VERSION = 'v1'
    API_PREFIX = '/api/v1'
    
    # 第8步：数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///newzotero.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 关闭事件系统以节省资源
    SQLALCHEMY_ECHO = False  # 不显示SQL语句
    
    # 数据库连接池配置
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,  # 连接前验证
        'pool_recycle': 300,    # 连接回收时间（秒）
    }
    
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    JWT_ALGORITHM = os.environ.get('JWT_ALGORITHM', 'HS256')
    JWT_ACCESS_TOKEN_EXPIRE = os.environ.get('JWT_ACCESS_TOKEN_EXPIRE', 12)
    JWT_REFRESH_TOKEN_EXPIRE = os.environ.get('JWT_REFRESH_TOKEN_EXPIRE', 30)


class DevelopmentConfig(Config):
    """
    开发环境配置 - 第8步增强
    
    开发环境数据库特点：
    - 显示SQL语句便于调试
    - 使用开发数据库
    """
    DEBUG = True
    ENV = 'development'
    
    # 开发环境显示SQL语句
    SQLALCHEMY_ECHO = True
    
    # 开发环境可以使用SQLite或PostgreSQL
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///newzotero_dev.db'
    
    print("🔧 Development Config class loaded")


class ProductionConfig(Config):
    """
    生产环境配置 - 第8步增强
    
    生产环境数据库特点：
    - 不显示SQL语句
    - 必须使用环境变量
    - 更严格的连接池设置
    """
    DEBUG = False
    ENV = 'production'
    
    # 生产环境从环境变量获取密钥
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'fallback-secret-key'
    
    # 生产环境必须使用环境变量中的数据库
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://user:password@localhost/newzotero_prod'
    
    # 生产环境连接池配置
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_size': 10,        # 连接池大小
        'max_overflow': 20      # 最大溢出连接
    }
    
    print("🚀 Production Config class loaded")


class TestingConfig(Config):
    """
    第8步：测试环境配置
    
    测试环境数据库特点：
    - 使用内存数据库或测试专用数据库
    - 每次测试后清理数据
    """
    TESTING = True
    DEBUG = True
    
    # 测试环境使用内存SQLite数据库
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # 测试时不需要CSRF保护
    WTF_CSRF_ENABLED = False
    
    print("🧪 Testing Config class loaded")


# ============================================
# 第8步：配置选择器 - 增强版
# ============================================

config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config(env_name=None):
    """
    根据环境名称获取配置类
    
    第8步增强：
    - 支持测试环境
    - 更好的环境变量处理
    """
    if env_name is None:
        env_name = os.environ.get('FLASK_ENV', 'default')
    
    config_class = config_map.get(env_name, DevelopmentConfig)
    print(f"📊 Selected config: {config_class.__name__}")
    return config_class

print("⚙️ config.py loaded - Step 8 ready! (Database support added)")
