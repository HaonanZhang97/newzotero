"""
第8步：支持数据库的应用工厂
============================

学习目标：
- 如何集成SQLAlchemy到Flask应用
- 数据库初始化和配置
- 应用上下文中的数据库操作
"""

from flask import Flask

# 第3步解锁 - 导入配置
from .config import get_config

# 第8步新增 - 导入数据库
from .models.user_model import db

# ============================================
# 第8步：支持数据库的应用工厂
# ============================================
def create_app(config_name=None):
    """
    应用工厂函数 - 现在支持数据库集成！
    
    Args:
        config_name: 环境名称 ('development', 'production')
                    如果为None，使用默认配置
    
    第8步新功能：数据库集成
    1. 初始化SQLAlchemy
    2. 数据库配置加载
    3. 数据库错误处理
    """
    print(f"🏭 Creating Flask app with database support for config: {config_name}")
    
    # 创建Flask应用实例
    app = Flask(__name__)
    
    # 第3步功能：加载配置
    config_class = get_config(config_name)
    app.config.from_object(config_class)
    
    # ============================================
    # 第8步：数据库初始化
    # ============================================
    
    # 初始化数据库
    db.init_app(app)
    print(f"🗄️ 数据库已初始化")
    print(f"📍 数据库URL: {app.config.get('SQLALCHEMY_DATABASE_URI', '未配置')[:50]}...")
    
    # ============================================
    # 第4步：Blueprint 注册  
    # ============================================
    
    # 导入和注册用户管理 Blueprint
    from .api import users_bp
    app.register_blueprint(users_bp)
    
    print(f"📋 已注册 Blueprint: {users_bp.name}")
    print(f"🔗 Blueprint URL 前缀: {users_bp.url_prefix}")
    
    # ============================================
    # 第8步：数据库相关路由
    # ============================================
    
    @app.route('/db/info')
    def db_info():
        """数据库信息路由"""
        try:
            from .models.user_model import User
            with app.app_context():
                user_count = User.count_users()
                return {
                    'database': {
                        'status': 'connected',
                        'url': app.config.get('SQLALCHEMY_DATABASE_URI', '未配置')[:50] + '...',
                        'user_count': user_count,
                        'tables': ['users']  # 后续可以动态获取
                    },
                    'step': 8,
                    'message': 'Database integration active!'
                }
        except Exception as e:
            return {
                'database': {
                    'status': 'error',
                    'error': str(e)
                },
                'step': 8,
                'message': 'Database connection failed'
            }, 500
    
    # ============================================
    # 基础路由 - 更新支持数据库信息
    # ============================================
    
    @app.route('/')
    def hello():
        try:
            from .models.user_model import User
            with app.app_context():
                user_count = User.count_users()
                db_status = 'connected'
        except:
            user_count = 'unknown'
            db_status = 'disconnected'
            
        return {
            'message': 'Hello from NewZotero with Database!',
            'status': 'running',
            'step': 8,
            'environment': app.config.get('ENV', 'unknown'),
            'debug_mode': app.config.get('DEBUG', False),
            'api_version': app.config.get('API_VERSION', '1.0'),
            'database': {
                'status': db_status,
                'users': user_count
            },
            'available_apis': [
                '/api/v1/users - 用户管理API (现在使用数据库)',
                '/api/v1/users/info - 用户模块信息',
                '/db/info - 数据库信息'
            ],
            'registered_blueprints': list(app.blueprints.keys())
        }
    
    # 健康检查路由 - 现在包含数据库状态
    @app.route('/health')
    def health():
        try:
            # 测试数据库连接
            with app.app_context():
                from sqlalchemy import text
                db.session.execute(text('SELECT 1'))
                db_status = 'healthy'
        except:
            db_status = 'error'
            
        return {
            'status': 'healthy' if db_status == 'healthy' else 'degraded',
            'step': 8,
            'message': 'Flask app with Database working!',
            'config': {
                'environment': app.config.get('ENV'),
                'debug': app.config.get('DEBUG'),
                'secret_key_set': bool(app.config.get('SECRET_KEY'))
            },
            'database': {
                'status': db_status
            },
            'blueprints': {
                'count': len(app.blueprints),
                'names': list(app.blueprints.keys())
            }
        }
    
    # 配置信息路由
    @app.route('/config')
    def show_config():
        safe_config = {
            'ENV': app.config.get('ENV'),
            'DEBUG': app.config.get('DEBUG'), 
            'API_VERSION': app.config.get('API_VERSION'),
            'API_PREFIX': app.config.get('API_PREFIX'),
            'SECRET_KEY_CONFIGURED': bool(app.config.get('SECRET_KEY')),
            'DATABASE_CONFIGURED': bool(app.config.get('SQLALCHEMY_DATABASE_URI'))
        }
        return {
            'message': 'Current configuration with database',
            'config': safe_config,
            'blueprints_registered': len(app.blueprints)
        }
    
    print(f"✅ Flask app created with {config_class.__name__} and database support!")
    print(f"🔧 DEBUG mode: {app.config.get('DEBUG')}")
    print(f"🌍 Environment: {app.config.get('ENV', 'default')}")
    print(f"📋 Registered blueprints: {list(app.blueprints.keys())}")
    
    return app

# ============================================
# 第3步将要添加的功能（暂时注释掉）
# ============================================
# TODO: 第3步解锁 - 添加配置支持
# def create_app(config_name=None):
#     app = Flask(__name__)
#     
#     # 加载配置
#     if config_name:
#         app.config.from_object(get_config(config_name))
#     
#     return app

# ============================================  
# 第4步将要添加的功能（暂时注释掉）
# ============================================
# TODO: 第4步解锁 - 添加错误处理
# def register_error_handlers(app):
#     @app.errorhandler(404)
#     def not_found(error):
#         return {'error': 'Not Found'}, 404

# ============================================
# 第5步将要添加的功能（暂时注释掉）  
# ============================================
# TODO: 第5步解锁 - 添加蓝图注册
# def register_blueprints(app):
#     from .api.v1.users import users_bp
#     app.register_blueprint(users_bp)

print("📄 app.py loaded - Step 2 ready!")
