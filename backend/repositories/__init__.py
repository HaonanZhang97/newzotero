"""
第7步：Repository包初始化
第10步：项目Repository包初始化
========================

Repository层：负责数据持久化和存储
"""

# ============================================
# 第7步+第10步：Repository层功能解锁
# ============================================

from .user_repository import UserRepository
from .project_repository import ProjectRepository

__all__ = [
    'UserRepository',
    'ProjectRepository'
]

print("🗄️ Repository层已加载 - 数据持久化功能已启用")
