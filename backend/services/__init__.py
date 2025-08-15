"""
Services 模块初始化 - 第7步
=========================

第7步：业务逻辑层集成Repository层
"""

from .user_service import UserService

# 第7步：可用的 Service 类
__all__ = [
    'UserService',
]

print("🏢 Services package loading...")
print(f"📋 Available services: {__all__}")
print("🔧 第7步：Service层与Repository层集成完成")
