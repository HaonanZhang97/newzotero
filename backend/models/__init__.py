"""
Models 模块初始化
================

第6步：数据模型层(Model Layer / Entity Layer)
第9步：项目模型层(Project Model Layer)
"""

from .user_model import User, UserCreateRequest, UserUpdateRequest
from .project_model import Project, ProjectCreateRequest, ProjectUpdateRequest

# 第6步+第9步+第11步：可用的 Model 类
__all__ = [
    'User',
    'UserCreateRequest', 
    'UserUpdateRequest',
    'Project',
    'ProjectCreateRequest',
    'ProjectUpdateRequest',
]

# 第7步将解锁的 Model（暂时注释）
# from .file_model import File, FileUploadRequest
# from .note_model import Note, NoteCreateRequest

print("📊 Models package loading...")
print(f"🔧 Available models: {__all__}")
