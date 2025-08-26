"""
API 模块初始化
=============

第4步：Blueprint 组织层
"""

from .users import users_bp
from .projects import projects_bp

# 第4步：可用的 Blueprint 列表
__all__ = [
    'users_bp',
    'projects_bp',
]

# 第5步将解锁的 Blueprint（暂时注释）
# from .files import files_bp
# from .notes import notes_bp

print("� API package loading...")
print(f"🔧 Available blueprints: {__all__}")
