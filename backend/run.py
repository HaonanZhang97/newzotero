"""
应用启动脚本
==========

用于启动Flask应用的入口点
"""

import os
import sys
from backend import create_app

def main():
    """主函数：创建并运行Flask应用"""
    
    # 从环境变量获取配置，默认为开发环境
    env = os.environ.get('FLASK_ENV', 'development')
    
    print(f"🚀 Starting NewZotero Backend...")
    print(f"📊 Environment: {env}")
    
    # 创建应用
    app = create_app(env)
    
    # 从环境变量获取主机和端口
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5000))
    
    print(f"🌐 Server will run on: http://{host}:{port}")
    print(f"💡 Health check: http://{host}:{port}/health")
    
    # 运行应用
    try:
        app.run(
            host=host,
            port=port,
            debug=app.config.get('DEBUG', False)
        )
    except KeyboardInterrupt:
        print("\n👋 Shutting down gracefully...")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
