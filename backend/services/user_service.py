"""
第7步：集成Repository层的用户业务逻辑层
====================================

学习目标：
- Service层与Repository层的集成
- 完整的数据持久化流程
- 分层架构的最终形态
"""

from typing import Dict, List, Optional
import hashlib

# 第7步：导入Model层和Repository层
from ..models import User, UserCreateRequest, UserUpdateRequest
from ..repositories.user_repository import get_user_repository

class UserService:
    """
    用户业务逻辑服务 - 第7步：集成Repository层
    
    完整架构：
    Controller → Service → Repository → 数据存储
    
    职责：
    1. 使用DTO验证请求数据
    2. 使用Entity处理业务逻辑
    3. 通过Repository持久化数据
    4. 业务流程编排和事务管理
    
    与SpringBoot Service层对比：
    - Flask UserService + Repository ↔ SpringBoot @Service + @Repository
    - 手动Repository注入 ↔ @Autowired Repository
    - 手动事务管理 ↔ @Transactional 注解
    """
    
    def __init__(self):
        """初始化Service，注入Repository依赖"""
        self.user_repository = get_user_repository()
    
    @classmethod
    def create_user(cls, request_data: Dict) -> Dict:
        """
        创建新用户 - 完整业务流程
        
        业务流程：
        1. 请求数据 → DTO验证
        2. DTO → Entity转换
        3. 业务规则检查（唯一性等）
        4. Entity验证
        5. Repository持久化
        6. 返回结果
        
        Args:
            request_data: 用户创建请求数据
            
        Returns:
            创建成功的用户信息字典
        """
        try:
            service = cls()
            
            # 第1步：DTO验证
            create_request = UserCreateRequest(request_data)
            create_request.validate()
            
            # 第2步：业务规则检查
            # 检查用户名唯一性
            if service.user_repository.exists_by_username(create_request.username):
                raise ValueError(f"用户名 '{create_request.username}' 已存在")
            
            # 检查邮箱唯一性
            if service.user_repository.exists_by_email(create_request.email):
                raise ValueError(f"邮箱 '{create_request.email}' 已存在")
            
            # 第3步：DTO → Entity转换
            user_data = create_request.to_user_dict()
            user = User.from_dict(user_data)
            
            # 第4步：Entity验证
            if not user.is_valid():
                errors = user.get_validation_errors()
                raise ValueError(f"用户数据验证失败: {'; '.join(errors)}")
            
            # 第5步：Repository持久化
            saved_user = service.user_repository.save(user)
            
            return {
                "success": True,
                "message": "用户创建成功",
                "data": saved_user.to_dict()
            }
            
        except ValueError as e:
            return {"success": False, "message": str(e), "data": None}
        except Exception as e:
            return {"success": False, "message": f"系统错误: {str(e)}", "data": None}
    
    @classmethod
    def get_all_users(cls) -> Dict:
        """获取所有用户列表"""
        try:
            service = cls()
            users = service.user_repository.find_all()
            
            return {
                "success": True,
                "message": f"获取到 {len(users)} 个用户",
                "data": [user.to_dict() for user in users]
            }
        except Exception as e:
            return {"success": False, "message": f"获取失败: {str(e)}", "data": None}
    
    @classmethod
    def get_user_by_id(cls, user_id: int) -> Dict:
        """根据ID获取用户"""
        try:
            service = cls()
            user = service.user_repository.find_by_id(user_id)
            
            if user:
                return {"success": True, "message": "查找成功", "data": user.to_dict()}
            else:
                return {"success": False, "message": f"用户ID {user_id} 不存在", "data": None}
        except Exception as e:
            return {"success": False, "message": f"查询失败: {str(e)}", "data": None}
    
    @classmethod
    def update_user(cls, user_id: int, request_data: Dict) -> Dict:
        """更新用户信息"""
        try:
            service = cls()
            
            # 检查用户是否存在
            existing_user = service.user_repository.find_by_id(user_id)
            if not existing_user:
                return {"success": False, "message": f"用户ID {user_id} 不存在", "data": None}
            
            # DTO验证
            update_request = UserUpdateRequest(request_data)
            update_request.validate()
            
            # 业务规则检查
            if update_request.email and update_request.email != existing_user.email:
                if service.user_repository.exists_by_email(update_request.email):
                    raise ValueError(f"邮箱 '{update_request.email}' 已存在")
            
            # 更新Entity
            update_data = update_request.to_update_dict()
            for key, value in update_data.items():
                if hasattr(existing_user, key):
                    setattr(existing_user, key, value)
            
            # Entity验证
            if not existing_user.is_valid():
                errors = existing_user.get_validation_errors()
                raise ValueError(f"更新数据验证失败: {'; '.join(errors)}")
            
            # Repository持久化
            updated_user = service.user_repository.save(existing_user)
            
            return {"success": True, "message": "用户更新成功", "data": updated_user.to_dict()}
            
        except ValueError as e:
            return {"success": False, "message": str(e), "data": None}
        except Exception as e:
            return {"success": False, "message": f"更新失败: {str(e)}", "data": None}
    
    @classmethod
    def delete_user(cls, user_id: int) -> Dict:
        """删除用户"""
        try:
            service = cls()
            
            # 检查用户是否存在
            user = service.user_repository.find_by_id(user_id)
            if not user:
                return {"success": False, "message": f"用户ID {user_id} 不存在", "data": None}
            
            # 执行删除
            deleted = service.user_repository.delete_by_id(user_id)
            
            if deleted:
                return {"success": True, "message": f"用户 '{user.username}' 删除成功", "data": {"deleted_user_id": user_id}}
            else:
                return {"success": False, "message": "删除操作失败", "data": None}
                
        except Exception as e:
            return {"success": False, "message": f"删除失败: {str(e)}", "data": None}
    
    @classmethod
    def find_users_by_status(cls, status: str) -> Dict:
        """根据状态查找用户"""
        try:
            service = cls()
            users = service.user_repository.find_by_status(status)
            
            return {
                "success": True,
                "message": f"找到 {len(users)} 个状态为 '{status}' 的用户",
                "data": [user.to_dict() for user in users]
            }
        except Exception as e:
            return {"success": False, "message": f"查询失败: {str(e)}", "data": None}
    
    @classmethod
    def get_user_statistics(cls) -> Dict:
        """获取用户统计信息"""
        try:
            service = cls()
            stats = service.user_repository.get_statistics()
            
            return {"success": True, "message": "统计信息获取成功", "data": stats}
        except Exception as e:
            return {"success": False, "message": f"获取统计失败: {str(e)}", "data": None}
    
    @classmethod
    def username_exists(cls, username: str) -> bool:
        """检查用户名是否存在"""
        try:
            service = cls()
            return service.user_repository.exists_by_username(username)
        except:
            return False
    
    @classmethod
    def email_exists(cls, email: str) -> bool:
        """检查邮箱是否存在"""
        try:
            service = cls()
            return service.user_repository.exists_by_email(email)
        except:
            return False
    
    @classmethod
    def get_service_info(cls) -> Dict:
        """获取服务信息"""
        return {
            'service_name': 'UserService',
            'version': '3.0.0',  # 第7步：Repository层集成
            'description': '用户管理业务逻辑服务 - 完整分层架构',
            'layer_integration': {
                'controller_layer': '✅ Flask API routes',
                'service_layer': '✅ Business logic & validation',
                'repository_layer': '✅ Data access & persistence',
                'model_layer': '✅ Entity + DTO models',
                'storage_layer': '✅ JSON file storage'
            },
            'complete_architecture': 'HTTP → Controller → Service → Repository → Storage',
            'features': [
                '完整CRUD操作',
                '数据持久化',
                '业务规则验证',
                '唯一性约束',
                '统计信息',
                '状态查询'
            ]
        }
    
    @staticmethod
    def hash_password(password: str) -> str:
        """密码哈希处理"""
        return hashlib.sha256(password.encode()).hexdigest()

print("🔧 UserService v3.0 loaded - Service层与Repository层集成完成！")