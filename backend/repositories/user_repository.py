"""
第7步：用户数据仓储层(User Repository)
====================================

学习目标：
- Repository模式的实现
- 文件存储的数据持久化
- 与SpringBoot JpaRepository的对比
- CRUD操作的标准实现
"""

import json
import os
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from ..models.user_model import User

class UserRepository:
    """
    用户数据仓储类
    
    对比SpringBoot:
    Flask UserRepository ↔ SpringBoot JpaRepository<User, Long>
    手动文件操作 ↔ 自动SQL生成
    JSON文件存储 ↔ 数据库表存储
    
    职责：
    1. 用户数据的CRUD操作
    2. 数据持久化到文件
    3. 数据查询和过滤
    4. 数据完整性保证
    """
    
    def __init__(self, data_file_path: Optional[str] = None):
        """
        初始化Repository
        
        Args:
            data_file_path: 数据文件路径，默认为backend/data/users.json
        """
        if data_file_path is None:
            # 确保data目录存在
            current_dir = os.path.dirname(os.path.abspath(__file__))
            backend_dir = os.path.dirname(current_dir)
            data_dir = os.path.join(backend_dir, 'data')
            os.makedirs(data_dir, exist_ok=True)
            data_file_path = os.path.join(data_dir, 'users.json')
        
        self.data_file_path = data_file_path
        self._ensure_data_file_exists()
    
    def _ensure_data_file_exists(self) -> None:
        """确保数据文件存在"""
        if not os.path.exists(self.data_file_path):
            self._save_data([])
    
    def _load_data(self) -> List[Dict[str, Any]]:
        """
        从文件加载数据
        
        Returns:
            用户数据列表
        """
        try:
            with open(self.data_file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                return data if isinstance(data, list) else []
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"⚠️ 数据文件读取错误: {e}")
            return []
    
    def _save_data(self, data: List[Dict[str, Any]]) -> None:
        """
        保存数据到文件
        
        Args:
            data: 要保存的用户数据列表
        """
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.data_file_path), exist_ok=True)
            
            with open(self.data_file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=2)
        except Exception as e:
            raise RuntimeError(f"数据保存失败: {e}")
    
    def _get_next_id(self, users: List[Dict[str, Any]]) -> int:
        """
        获取下一个可用的ID
        
        Args:
            users: 现有用户列表
            
        Returns:
            下一个ID
        """
        if not users:
            return 1
        
        max_id = max(user.get('id', 0) for user in users)
        return max_id + 1
    
    # ============================================
    # CRUD操作 - Create, Read, Update, Delete
    # ============================================
    
    def save(self, user: User) -> User:
        """
        保存用户（创建或更新）
        
        对比SpringBoot: save() ↔ JpaRepository.save()
        
        Args:
            user: 要保存的用户对象
            
        Returns:
            保存后的用户对象（包含生成的ID）
            
        Raises:
            ValueError: 数据验证失败
            RuntimeError: 保存操作失败
        """
        # 验证用户数据
        if not user.is_valid():
            errors = user.get_validation_errors()
            raise ValueError(f"用户数据无效: {'; '.join(errors)}")
        
        users = self._load_data()
        
        # 更新时间
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if user.id is None:
            # 新增用户
            user.id = self._get_next_id(users)
            # 直接设置时间字段，因为User模型中的时间是字符串类型
            user_dict = user.to_dict(include_sensitive=True)
            user_dict['created_at'] = now
            user_dict['updated_at'] = now
            users.append(user_dict)
            # 更新User对象的内部状态
            user = User.from_dict(user_dict)
        else:
            # 更新现有用户
            user_dict = user.to_dict(include_sensitive=True)
            user_dict['updated_at'] = now
            
            # 查找并更新
            updated = False
            for i, existing_user in enumerate(users):
                if existing_user.get('id') == user.id:
                    # 保留原始创建时间
                    user_dict['created_at'] = existing_user.get('created_at')
                    users[i] = user_dict
                    updated = True
                    break
            
            if not updated:
                raise ValueError(f"用户ID {user.id} 不存在")
        
        self._save_data(users)
        return user
    
    def find_by_id(self, user_id: int) -> Optional[User]:
        """
        根据ID查找用户
        
        对比SpringBoot: findById() ↔ JpaRepository.findById()
        
        Args:
            user_id: 用户ID
            
        Returns:
            找到的用户对象，未找到返回None
        """
        users = self._load_data()
        
        for user_data in users:
            if user_data.get('id') == user_id:
                return User.from_dict(user_data)
        
        return None
    
    def find_by_username(self, username: str) -> Optional[User]:
        """
        根据用户名查找用户
        
        对比SpringBoot: findByUsername() ↔ 自定义查询方法
        
        Args:
            username: 用户名
            
        Returns:
            找到的用户对象，未找到返回None
        """
        users = self._load_data()
        
        for user_data in users:
            if user_data.get('username') == username:
                return User.from_dict(user_data)
        
        return None
    
    def find_by_email(self, email: str) -> Optional[User]:
        """
        根据邮箱查找用户
        
        Args:
            email: 邮箱地址
            
        Returns:
            找到的用户对象，未找到返回None
        """
        users = self._load_data()
        
        for user_data in users:
            if user_data.get('email') == email:
                return User.from_dict(user_data)
        
        return None
    
    def find_all(self) -> List[User]:
        """
        查找所有用户
        
        对比SpringBoot: findAll() ↔ JpaRepository.findAll()
        
        Returns:
            所有用户对象列表
        """
        users = self._load_data()
        return [User.from_dict(user_data) for user_data in users]
    
    def find_by_status(self, status: str) -> List[User]:
        """
        根据状态查找用户
        
        Args:
            status: 用户状态
            
        Returns:
            指定状态的用户列表
        """
        users = self._load_data()
        result = []
        
        for user_data in users:
            if user_data.get('status') == status:
                result.append(User.from_dict(user_data))
        
        return result
    
    def exists_by_username(self, username: str) -> bool:
        """
        检查用户名是否已存在
        
        对比SpringBoot: existsByUsername() ↔ 自定义存在性检查
        
        Args:
            username: 用户名
            
        Returns:
            True如果用户名已存在，否则False
        """
        return self.find_by_username(username) is not None
    
    def exists_by_email(self, email: str) -> bool:
        """
        检查邮箱是否已存在
        
        Args:
            email: 邮箱地址
            
        Returns:
            True如果邮箱已存在，否则False
        """
        return self.find_by_email(email) is not None
    
    def delete_by_id(self, user_id: int) -> bool:
        """
        根据ID删除用户
        
        对比SpringBoot: deleteById() ↔ JpaRepository.deleteById()
        
        Args:
            user_id: 要删除的用户ID
            
        Returns:
            True如果删除成功，False如果用户不存在
        """
        users = self._load_data()
        
        for i, user_data in enumerate(users):
            if user_data.get('id') == user_id:
                del users[i]
                self._save_data(users)
                return True
        
        return False
    
    def count(self) -> int:
        """
        获取用户总数
        
        对比SpringBoot: count() ↔ JpaRepository.count()
        
        Returns:
            用户总数
        """
        users = self._load_data()
        return len(users)
    
    def count_by_status(self, status: str) -> int:
        """
        根据状态统计用户数量
        
        Args:
            status: 用户状态
            
        Returns:
            指定状态的用户数量
        """
        users = self._load_data()
        return sum(1 for user in users if user.get('status') == status)
    
    # ============================================
    # 高级查询方法
    # ============================================
    
    def find_by_criteria(self, **criteria) -> List[User]:
        """
        根据多个条件查询用户
        
        Args:
            **criteria: 查询条件，如status='active', username='john'
            
        Returns:
            符合条件的用户列表
        """
        users = self._load_data()
        result = []
        
        for user_data in users:
            match = True
            for key, value in criteria.items():
                if user_data.get(key) != value:
                    match = False
                    break
            
            if match:
                result.append(User.from_dict(user_data))
        
        return result
    
    def find_recent_users(self, days: int = 7) -> List[User]:
        """
        查找最近注册的用户
        
        Args:
            days: 最近天数，默认7天
            
        Returns:
            最近注册的用户列表
        """
        users = self._load_data()
        recent_users = []
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for user_data in users:
            created_at = user_data.get('created_at')
            if created_at:
                try:
                    created_date = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                    if created_date >= cutoff_date:
                        recent_users.append(User.from_dict(user_data))
                except ValueError:
                    continue
        
        return recent_users
    
    # ============================================
    # 数据库管理方法
    # ============================================
    
    def clear_all(self) -> None:
        """
        清空所有用户数据（慎用！）
        """
        self._save_data([])
    
    def backup_data(self, backup_path: Optional[str] = None) -> str:
        """
        备份用户数据
        
        Args:
            backup_path: 备份文件路径
            
        Returns:
            实际的备份文件路径
        """
        if backup_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_dir = os.path.dirname(self.data_file_path)
            backup_path = os.path.join(backup_dir, f'users_backup_{timestamp}.json')
        
        users = self._load_data()
        
        try:
            with open(backup_path, 'w', encoding='utf-8') as file:
                json.dump(users, file, ensure_ascii=False, indent=2)
            return backup_path
        except Exception as e:
            raise RuntimeError(f"数据备份失败: {e}")
    
    def restore_data(self, backup_path: str) -> None:
        """
        从备份恢复数据
        
        Args:
            backup_path: 备份文件路径
        """
        try:
            with open(backup_path, 'r', encoding='utf-8') as file:
                backup_data = json.load(file)
            
            if not isinstance(backup_data, list):
                raise ValueError("备份文件格式无效")
            
            self._save_data(backup_data)
        except Exception as e:
            raise RuntimeError(f"数据恢复失败: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取用户数据统计信息
        
        Returns:
            统计信息字典
        """
        users = self._load_data()
        
        stats = {
            'total_users': len(users),
            'active_users': sum(1 for u in users if u.get('status') == 'active'),
            'inactive_users': sum(1 for u in users if u.get('status') == 'inactive'),
            'suspended_users': sum(1 for u in users if u.get('status') == 'suspended')
        }
        
        return stats

# ============================================
# Repository实例（单例模式）
# ============================================

# 默认的Repository实例，供Service层使用
_default_user_repository = None

def get_user_repository() -> UserRepository:
    """
    获取默认的UserRepository实例（单例）
    
    Returns:
        UserRepository实例
    """
    global _default_user_repository
    if _default_user_repository is None:
        _default_user_repository = UserRepository()
    return _default_user_repository

print(f"🗄️ UserRepository loaded - 用户数据持久化功能已就绪！")
