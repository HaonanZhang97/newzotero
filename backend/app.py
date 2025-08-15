"""
第4步：带有 Blueprint 的应用工厂
===============================

学习目标：
- 如何注册 Blueprint 到应用
- Blueprint 的 URL 前缀如何工作
- 模块化 API 的组织方式
"""

from flask import Flask

# 第3步解锁 - 导入配置
from .config import get_config

# ============================================
# 第4步：支持 Blueprint 的应用工厂
# ============================================
def create_app(config_name=None):
    """
    应用工厂函数 - 现在支持 Blueprint 注册！
    
    Args:
        config_name: 环境名称 ('development', 'production')
                    如果为None，使用默认配置
    
    第4步新功能：Blueprint 注册
    1. 导入 Blueprint
    2. 注册到应用
    3. 统一管理 API 路由
    """
    print(f"🏭 Creating Flask app with config: {config_name}")
    
    # 创建Flask应用实例
    app = Flask(__name__)
    
    # 第3步功能：加载配置
    config_class = get_config(config_name)
    app.config.from_object(config_class)
    
    # ============================================
    # 第4步：Blueprint 注册
    # ============================================
    
    # 导入和注册用户管理 Blueprint
    from .api import users_bp
    app.register_blueprint(users_bp)
    
    print(f"📋 已注册 Blueprint: {users_bp.name}")
    print(f"🔗 Blueprint URL 前缀: {users_bp.url_prefix}")
    
    # 第5步将解锁更多 Blueprint（暂时注释）
    # from .api import files_bp, notes_bp
    # app.register_blueprint(files_bp)
    # app.register_blueprint(notes_bp)
    
    # ============================================
    # 基础路由
    # ============================================
    
    @app.route('/')
    def hello():
        return {
            'message': 'Hello from NewZotero!',
            'status': 'running',
            'step': 4,
            'environment': app.config.get('ENV', 'unknown'),
            'debug_mode': app.config.get('DEBUG', False),
            'api_version': app.config.get('API_VERSION', '1.0'),
            'available_apis': [
                '/api/v1/users - 用户管理API',
                '/api/v1/users/info - 用户模块信息'
            ],
            'registered_blueprints': list(app.blueprints.keys())
        }
    
    # 健康检查路由 - 现在显示 Blueprint 信息
    @app.route('/health')
    def health():
        return {
            'status': 'healthy',
            'step': 4,
            'message': 'Flask app with Blueprints working!',
            'config': {
                'environment': app.config.get('ENV'),
                'debug': app.config.get('DEBUG'),
                'secret_key_set': bool(app.config.get('SECRET_KEY'))
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
            'SECRET_KEY_CONFIGURED': bool(app.config.get('SECRET_KEY'))
        }
        return {
            'message': 'Current configuration',
            'config': safe_config,
            'blueprints_registered': len(app.blueprints)
        }
    
    print(f"✅ Flask app created with {config_class.__name__}!")
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
