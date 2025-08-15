"""
Models 模块初始化
================

第6步：数据模型层(Model Layer / Entity Layer)
"""

from .user_model import User, UserCreateRequest, UserUpdateRequest

# 第6步：可用的 Model 类
__all__ = [
    'User',
    'UserCreateRequest', 
    'UserUpdateRequest',
]

# 第7步将解锁的 Model（暂时注释）
# from .file_model import File, FileUploadRequest
# from .note_model import Note, NoteCreateRequest

print("📊 Models package loading...")
print(f"🔧 Available models: {__all__}")
