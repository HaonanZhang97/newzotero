"""
Services 模块初始化 - 第7步+第11步
===============================

第7步：业务逻辑层集成Repository层
第11步：项目业务逻辑层
"""

from .user_service import UserService
from .project_service import ProjectService

# 第7步+第11步：可用的 Service 类
__all__ = [
    'UserService',
    'ProjectService',
]

print("🏢 Services package loading...")
print(f"📋 Available services: {__all__}")
print("🔧 第7步+第11步：Service层与Repository层集成完成")
