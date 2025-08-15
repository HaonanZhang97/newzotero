"""
第6步：用户数据模型层(User Model)
===============================

学习目标：
- 什么是Model层/Entity层
- 数据模型的定义和验证
- 数据传输对象(DTO)的使用
- 与SpringBoot Entity的对比
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any
from datetime import datetime
import re
import json

# ============================================
# 第6步：用户数据模型
# ============================================

@dataclass
class User:
    """
    用户实体模型 (Entity)
    
    对比SpringBoot:
    Flask @dataclass User ↔ SpringBoot @Entity User
    手动验证方法 ↔ @Valid 注解验证
    手动字段定义 ↔ JPA 注解映射
    
    职责：
    1. 定义用户数据结构
    2. 数据序列化/反序列化
    3. 基础数据验证
    4. 数据格式转换
    """
    
    # ============================================
    # 实体字段定义
    # ============================================
    id: Optional[int] = None
    username: str = ""
    email: str = ""
    password_hash: Optional[str] = None
    full_name: Optional[str] = None
    status: str = "active"  # active, inactive, suspended
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    last_login: Optional[str] = None
    
    # 计算字段 (不存储在数据库)
    _validation_errors: List[str] = field(default_factory=list, init=False)
    
    def __post_init__(self):
        """初始化后处理 - 设置默认值"""
        if not self.created_at:
            self.created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if not self.updated_at:
            self.updated_at = self.created_at
    
    # ============================================
    # 数据验证方法
    # ============================================
    
    def is_valid(self) -> bool:
        """验证实体数据是否有效"""
        self._validation_errors.clear()
        
        # ID验证
        if self.id is not None and self.id <= 0:
            self._validation_errors.append("ID必须是正整数")
        
        # 用户名验证
        if not self.username:
            self._validation_errors.append("用户名不能为空")
        elif len(self.username) < 3:
            self._validation_errors.append("用户名至少3个字符")
        elif not re.match(r'^[a-zA-Z0-9_]+$', self.username):
            self._validation_errors.append("用户名只能包含字母、数字和下划线")
        
        # 邮箱验证
        if not self.email:
            self._validation_errors.append("邮箱不能为空")
        elif not re.match(r'^[^@]+@[^@]+\.[^@]+$', self.email):
            self._validation_errors.append("邮箱格式不正确")
        
        # 状态验证
        valid_statuses = ["active", "inactive", "suspended"]
        if self.status not in valid_statuses:
            self._validation_errors.append(f"状态必须是: {', '.join(valid_statuses)}")
        
        return len(self._validation_errors) == 0
    
    def get_validation_errors(self) -> List[str]:
        """获取验证错误列表"""
        return self._validation_errors.copy()
    
    # ============================================
    # 数据转换方法
    # ============================================
    
    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """
        转换为字典 - 用于API响应
        
        Args:
            include_sensitive: 是否包含敏感信息(如password_hash)
        """
        result = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'status': self.status,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'last_login': self.last_login
        }
        
        if include_sensitive:
            result['password_hash'] = self.password_hash
        
        # 移除None值
        return {k: v for k, v in result.items() if v is not None}
    
    def to_json(self, include_sensitive: bool = False) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(include_sensitive), ensure_ascii=False, indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """从字典创建User实例"""
        return cls(
            id=data.get('id'),
            username=data.get('username', ''),
            email=data.get('email', ''),
            password_hash=data.get('password_hash'),
            full_name=data.get('full_name'),
            status=data.get('status', 'active'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            last_login=data.get('last_login')
        )
    
    # ============================================
    # 业务方法
    # ============================================
    
    @property
    def display_name(self) -> str:
        """显示名称 - 优先使用full_name，否则使用username"""
        return self.full_name if self.full_name else self.username
    
    @property
    def is_active(self) -> bool:
        """是否活跃用户"""
        return self.status == "active"
    
    def update_login_time(self):
        """更新最后登录时间"""
        self.last_login = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.updated_at = self.last_login

# ============================================
# 第6步：数据传输对象 (DTO)
# ============================================

@dataclass
class UserCreateRequest:
    """
    用户创建请求DTO
    
    对比SpringBoot:
    Flask UserCreateRequest ↔ SpringBoot UserCreateDto
    手动验证 ↔ @Valid + @NotNull等注解
    
    职责：
    1. 定义创建用户需要的数据结构
    2. 请求数据验证
    3. 数据清理和格式化
    """
    
    username: str = ""
    email: str = ""
    password: Optional[str] = None
    full_name: Optional[str] = None
    
    def __init__(self, data: Dict[str, Any]):
        """从请求数据初始化"""
        self.username = str(data.get('username', '')).strip()
        self.email = str(data.get('email', '')).strip().lower()
        self.password = data.get('password')
        self.full_name = data.get('full_name', '').strip() if data.get('full_name') else None
        
        # 清理空字符串
        if self.full_name == '':
            self.full_name = None
    
    def validate(self) -> None:
        """验证请求数据 - 抛出异常如果无效"""
        errors = []
        
        # 用户名验证
        if not self.username:
            errors.append("用户名不能为空")
        elif len(self.username) < 3:
            errors.append("用户名至少3个字符")
        elif len(self.username) > 50:
            errors.append("用户名最多50个字符")
        elif not re.match(r'^[a-zA-Z0-9_]+$', self.username):
            errors.append("用户名只能包含字母、数字和下划线")
        
        # 邮箱验证
        if not self.email:
            errors.append("邮箱不能为空")
        elif len(self.email) > 100:
            errors.append("邮箱最多100个字符")
        elif not re.match(r'^[^@]+@[^@]+\.[^@]+$', self.email):
            errors.append("邮箱格式不正确")
        
        # 密码验证（如果提供）
        if self.password is not None:
            if not self.password:
                errors.append("密码不能为空")
            elif len(self.password) < 6:
                errors.append("密码至少6个字符")
            elif len(self.password) > 128:
                errors.append("密码最多128个字符")
            elif not re.search(r'[A-Za-z]', self.password):
                errors.append("密码必须包含字母")
            elif not re.search(r'[0-9]', self.password):
                errors.append("密码必须包含数字")
        
        # 全名验证（如果提供）
        if self.full_name is not None:
            if len(self.full_name) > 100:
                errors.append("全名最多100个字符")
        
        if errors:
            raise ValueError(f"数据验证失败: {'; '.join(errors)}")
    
    def to_user_dict(self) -> Dict[str, Any]:
        """转换为创建User实体所需的数据"""
        result = {
            'username': self.username,
            'email': self.email,
            'status': 'active'
        }
        
        if self.full_name:
            result['full_name'] = self.full_name
        
        return result

@dataclass
class UserUpdateRequest:
    """
    用户更新请求DTO
    
    职责：
    1. 定义更新用户需要的数据结构
    2. 部分更新字段验证
    3. 只更新提供的字段
    """
    
    email: Optional[str] = None
    full_name: Optional[str] = None
    status: Optional[str] = None
    
    def __init__(self, data: Dict[str, Any]):
        """从请求数据初始化 - 只处理提供的字段"""
        if 'email' in data:
            self.email = str(data['email']).strip().lower()
        
        if 'full_name' in data:
            full_name = str(data['full_name']).strip()
            self.full_name = full_name if full_name else None
        
        if 'status' in data:
            self.status = str(data['status']).strip()
    
    def validate(self) -> None:
        """验证更新数据"""
        errors = []
        
        # 邮箱验证（如果提供）
        if self.email is not None:
            if not self.email:
                errors.append("邮箱不能为空")
            elif len(self.email) > 100:
                errors.append("邮箱最多100个字符")
            elif not re.match(r'^[^@]+@[^@]+\.[^@]+$', self.email):
                errors.append("邮箱格式不正确")
        
        # 状态验证（如果提供）
        if self.status is not None:
            valid_statuses = ["active", "inactive", "suspended"]
            if self.status not in valid_statuses:
                errors.append(f"状态必须是: {', '.join(valid_statuses)}")
        
        # 全名验证（如果提供）
        if self.full_name is not None:
            if len(self.full_name) > 100:
                errors.append("全名最多100个字符")
        
        if errors:
            raise ValueError(f"数据验证失败: {'; '.join(errors)}")
    
    def to_update_dict(self) -> Dict[str, Any]:
        """转换为更新数据字典 - 只包含非None字段"""
        result = {}
        
        if self.email is not None:
            result['email'] = self.email
        if self.full_name is not None:
            result['full_name'] = self.full_name
        if self.status is not None:
            result['status'] = self.status
        
        # 添加更新时间
        result['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        return result

# ============================================
# 第7步将要添加的功能（暂时注释掉）
# ============================================
# TODO: 第7步解锁 - 添加数据库映射
# from sqlalchemy import Column, Integer, String, DateTime
# from sqlalchemy.ext.declarative import declarative_base
# 
# Base = declarative_base()
# 
# class UserEntity(Base):
#     """SQLAlchemy用户表映射"""
#     __tablename__ = 'users'
#     
#     id = Column(Integer, primary_key=True)
#     username = Column(String(50), unique=True, nullable=False)
#     email = Column(String(100), unique=True, nullable=False)

# TODO: 第7步解锁 - 添加模型关系
# @dataclass 
# class UserProfile:
#     """用户资料扩展模型"""
#     user_id: int
#     avatar_url: Optional[str] = None
#     bio: Optional[str] = None

print(f"📊 User models loaded - Entity and DTO classes ready!")
