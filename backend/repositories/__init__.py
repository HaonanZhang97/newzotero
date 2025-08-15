"""
第7步：Repository包初始化
========================

Repository层：负责数据持久化和存储
"""

# ============================================
# 第7步：Repository层功能解锁
# ============================================

from .user_repository import UserRepository

__all__ = [
    'UserRepository'
]

print("🗄️ Repository层已加载 - 数据持久化功能已启用")
