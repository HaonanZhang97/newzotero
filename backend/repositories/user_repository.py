"""
第8步：用户数据仓储层(User Repository) - 数据库版本
================================================

学习目标：
- Repository模式与SQLAlchemy集成
- 数据库的数据持久化
- 与SpringBoot JpaRepository的对比
- CRUD操作的SQLAlchemy实现
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from ..models.user_model import db, User

class UserRepository:
    """
    用户数据仓储类 - 数据库版本
    
    对比SpringBoot:
    Flask UserRepository ↔ SpringBoot JpaRepository<User, Long>
    SQLAlchemy ORM ↔ Hibernate ORM
    手动查询构建 ↔ 自动SQL生成
    
    职责：
    1. 用户数据的CRUD操作
    2. 数据持久化到数据库
    3. 数据查询和过滤
    4. 事务管理
    """
    
    def __init__(self):
        """初始化Repository"""
        pass
    
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
        errors = user.validate()
        if errors:
            raise ValueError(f"用户数据无效: {'; '.join(errors)}")
        
        try:
            if user.id is None:
                # 新增用户
                db.session.add(user)
            else:
                # 更新现有用户 - SQLAlchemy会自动检测变更
                pass
            
            db.session.commit()
            return user
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"用户保存失败: {e}")
    
    def update_user(self, user_id: int, update_data: Dict[str, Any]) -> Optional[User]:
            """
            更新用户数据
            
            Args:
                user_id: 用户ID
                update_data: 要更新的数据
                
            Returns:
                更新后的用户对象，未找到返回None
            """
            try:
                user = self.find_by_id(user_id)
                if user:
                    user.update_from_dict(update_data)
                    
                    # 验证更新后的数据
                    errors = user.validate()
                    if errors:
                        raise ValueError(f"更新数据无效: {'; '.join(errors)}")
                    
                    db.session.commit()
                    return user
                return None
            except Exception as e:
                db.session.rollback()
                raise RuntimeError(f"用户更新失败: {e}")

    def find_by_id(self, user_id: int) -> Optional[User]:
        """
        根据ID查找用户
        
        对比SpringBoot: findById() ↔ JpaRepository.findById()
        
        Args:
            user_id: 用户ID
            
        Returns:
            找到的用户对象，未找到返回None
        """
        return User.find_by_id(user_id)
    
    def find_by_username(self, username: str) -> Optional[User]:
        """
        根据用户名查找用户
        
        对比SpringBoot: findByUsername() ↔ 自定义查询方法
        
        Args:
            username: 用户名
            
        Returns:
            找到的用户对象，未找到返回None
        """
        return User.find_by_username(username)
    
    def find_by_email(self, email: str) -> Optional[User]:
        """
        根据邮箱查找用户
        
        Args:
            email: 邮箱地址
            
        Returns:
            找到的用户对象，未找到返回None
        """
        return User.find_by_email(email)
    
    def find_all(self) -> List[User]:
        """
        查找所有用户
        
        对比SpringBoot: findAll() ↔ JpaRepository.findAll()
        
        Returns:
            所有用户对象列表
        """
        return User.get_all_users()
    
    def find_by_status(self, status: str) -> List[User]:
        """
        根据状态查找用户
        
        Args:
            status: 用户状态
            
        Returns:
            指定状态的用户列表
        """
        return User.query.filter_by(status=status).all()
    
    def exists_by_username(self, username: str) -> bool:
        """
        检查用户名是否已存在
        
        对比SpringBoot: existsByUsername() ↔ 自定义存在性检查
        
        Args:
            username: 用户名
            
        Returns:
            True如果用户名已存在，否则False
        """
        return User.query.filter_by(username=username).first() is not None
    
    def exists_by_email(self, email: str) -> bool:
        """
        检查邮箱是否已存在
        
        Args:
            email: 邮箱地址
            
        Returns:
            True如果邮箱已存在，否则False
        """
        return User.query.filter_by(email=email).first() is not None
    
    def delete_by_id(self, user_id: int) -> bool:
        """
        根据ID删除用户
        
        对比SpringBoot: deleteById() ↔ JpaRepository.deleteById()
        
        Args:
            user_id: 要删除的用户ID
            
        Returns:
            True如果删除成功，False如果用户不存在
        """
        try:
            user = self.find_by_id(user_id)
            if user:
                db.session.delete(user)
                db.session.commit()
                return True
            return False
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"用户删除失败: {e}")
    
    def count(self) -> int:
        """
        获取用户总数
        
        对比SpringBoot: count() ↔ JpaRepository.count()
        
        Returns:
            用户总数
        """
        return User.count_users()
    
    def count_by_status(self, status: str) -> int:
        """
        根据状态统计用户数量
        
        Args:
            status: 用户状态
            
        Returns:
            指定状态的用户数量
        """
        return User.query.filter_by(status=status).count()
    
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
        query = User.query
        for key, value in criteria.items():
            if hasattr(User, key):
                query = query.filter(getattr(User, key) == value)
        return query.all()
    
    def find_recent_users(self, days: int = 7) -> List[User]:
        """
        查找最近注册的用户
        
        Args:
            days: 最近天数，默认7天
            
        Returns:
            最近注册的用户列表
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return User.query.filter(User.created_at >= cutoff_date).all()
    
    def find_users_with_pagination(self, page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        """
        分页查询用户
        
        Args:
            page: 页码（从1开始）
            per_page: 每页数量
            
        Returns:
            包含用户列表和分页信息的字典
        """
        pagination = User.query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return {
            'users': pagination.items,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page,
            'per_page': pagination.per_page,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    
    # ============================================
    # 事务管理方法
    # ============================================
    
    def save_batch(self, users: List[User]) -> List[User]:
        """
        批量保存用户
        
        Args:
            users: 要保存的用户列表
            
        Returns:
            保存后的用户列表
        """
        try:
            for user in users:
                # 验证每个用户
                errors = user.validate()
                if errors:
                    raise ValueError(f"用户 {user.username} 数据无效: {'; '.join(errors)}")
                
                if user.id is None:
                    db.session.add(user)
            
            db.session.commit()
            return users
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"批量保存失败: {e}")
    
    
    # ============================================
    # 数据库管理方法
    # ============================================
    
    def clear_all(self) -> None:
        """
        清空所有用户数据（慎用！）
        """
        try:
            User.query.delete()
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"清空数据失败: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取用户数据统计信息
        
        Returns:
            统计信息字典
        """
        total_users = self.count()
        active_users = self.count_by_status('active')
        inactive_users = self.count_by_status('inactive')
        suspended_users = self.count_by_status('suspended')
        
        stats = {
            'total_users': total_users,
            'active_users': active_users,
            'inactive_users': inactive_users,
            'suspended_users': suspended_users,
            'status_distribution': {
                'active': active_users,
                'inactive': inactive_users,
                'suspended': suspended_users
            }
        }
        
        # 计算最近注册统计
        recent_7_days = len(self.find_recent_users(7))
        recent_30_days = len(self.find_recent_users(30))
        
        stats['recent_registrations'] = {
            '7_days': recent_7_days,
            '30_days': recent_30_days
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

print(f"🗄️ UserRepository loaded - 数据库持久化功能已就绪！")
