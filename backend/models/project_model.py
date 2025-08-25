"""
第9步：项目数据模型层(Project Model) - SQLAlchemy集成
=================================================

学习目标：
- 学习一对多关系设计 (User -> Projects)
- 掌握外键约束和关系映射
- 理解项目管理的数据结构
- 练习SQLAlchemy关系定义
"""

from dataclasses import dataclass
from typing import Optional, Dict, List, Any
from datetime import datetime, date
import re
import json

# SQLAlchemy imports
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Date, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

# 导入已有的db实例
from .user_model import db

# ============================================
# 第9步：SQLAlchemy项目模型
# ============================================

class Project(db.Model):
    """
    SQLAlchemy项目模型 (ORM Entity)
    
    对比SpringBoot:
    Flask SQLAlchemy Project ↔ SpringBoot @Entity Project
    db.Model继承 ↔ JpaRepository<Project, Long>
    ForeignKey ↔ @ManyToOne + @JoinColumn
    
    职责：
    1. 定义项目表结构
    2. 建立与User的关联关系
    3. 项目数据验证和转换
    4. 项目业务逻辑方法
    """
    
    __tablename__ = 'projects'
    
    # ============================================
    # 基础字段定义
    # ============================================
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    
    # ============================================
    # 关联字段 - 外键关系
    # ============================================
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # ============================================
    # 项目状态和管理
    # ============================================
    status = db.Column(db.String(20), nullable=False, default='active')  # active, completed, archived, paused
    priority = db.Column(db.Integer, nullable=False, default=1)  # 1-5 优先级
    
    # ============================================
    # 时间管理字段
    # ============================================
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    deadline = db.Column(db.Date, nullable=True)
    
    # ============================================
    # 项目设置
    # ============================================
    #is_public = db.Column(db.Boolean, nullable=False, default=False)
    color = db.Column(db.String(7), nullable=False, default='#4CAF50')  # 项目颜色标识
    
    # ============================================
    # 统计字段 (后续添加Note和Document时会用到)
    # ============================================
    note_count = db.Column(db.Integer, nullable=False, default=0)
    document_count = db.Column(db.Integer, nullable=False, default=0)
    
    # ============================================
    # 时间戳字段
    # ============================================
    created_at = db.Column(db.DateTime, nullable=False, default=func.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=func.now(), onupdate=func.now())
    
    # ============================================
    # 关系定义 - 与User的关系
    # ============================================
    # 这里定义了反向关系，可以通过 project.user 访问所属用户
    user = db.relationship('User', backref='projects')
    
    def __init__(self, name: str, user_id: int, **kwargs):
        """初始化项目实例"""
        self.name = name
        self.user_id = user_id
        self.description = kwargs.get('description')
        self.status = kwargs.get('status', 'active')
        self.priority = kwargs.get('priority', 1)
        self.start_date = kwargs.get('start_date')
        self.end_date = kwargs.get('end_date')
        self.deadline = kwargs.get('deadline')
    #    self.is_public = kwargs.get('is_public', False)
        self.color = kwargs.get('color', '#4CAF50')
    
    def __repr__(self):
        """字符串表示"""
        return f'<Project {self.name}>'
    
    # ============================================
    # 数据验证方法
    # ============================================
    
    def validate(self) -> List[str]:
        """验证项目数据，返回错误列表"""
        errors = []
        
        # 项目名验证
        if not self.name:
            errors.append("项目名不能为空")
        elif len(self.name) < 2:
            errors.append("项目名至少2个字符")
        elif len(self.name) > 200:
            errors.append("项目名最多200个字符")
        
        # 用户ID验证
        if not self.user_id:
            errors.append("必须指定项目所属用户")
        elif not isinstance(self.user_id, int) or self.user_id <= 0:
            errors.append("用户ID必须是正整数")
        
        # 状态验证
        valid_statuses = ["active", "completed", "archived", "paused"]
        if self.status not in valid_statuses:
            errors.append(f"项目状态必须是: {', '.join(valid_statuses)}")
        
        # 优先级验证
        if not isinstance(self.priority, int) or self.priority < 1 or self.priority > 5:
            errors.append("优先级必须是1-5之间的整数")
        
        # 描述长度验证
        if self.description and len(self.description) > 2000:
            errors.append("项目描述最多2000个字符")
        
        # 颜色验证
        if self.color and not re.match(r'^#[0-9A-Fa-f]{6}$', self.color):
            errors.append("颜色必须是有效的十六进制格式，如#4CAF50")
        
        # 日期逻辑验证
        if self.start_date and self.end_date and self.start_date > self.end_date:
            errors.append("开始日期不能晚于结束日期")
        
        if self.deadline and self.start_date and self.deadline < self.start_date:
            errors.append("截止日期不能早于开始日期")
        
        return errors
    
    def is_valid(self) -> bool:
        """检查项目数据是否有效"""
        return len(self.validate()) == 0
    
    # ============================================
    # 数据转换方法
    # ============================================
    
    def to_dict(self, include_user_info: bool = False) -> Dict[str, Any]:
        """
        转换为字典 - 用于API响应
        
        Args:
            include_user_info: 是否包含用户信息
        """
        result = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'user_id': self.user_id,
            'status': self.status,
            'priority': self.priority,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'deadline': self.deadline.isoformat() if self.deadline else None,
          #  'is_public': self.is_public,
            'color': self.color,
            'note_count': self.note_count,
            'document_count': self.document_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        # 包含用户信息
        if include_user_info and self.user:
            result['user'] = {
                'id': self.user.id,
                'username': self.user.username,
                'full_name': self.user.full_name
            }
        
        # 移除None值
        return {k: v for k, v in result.items() if v is not None}
    
    def to_json(self, include_user_info: bool = False) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(include_user_info), ensure_ascii=False, indent=2)
    
    # ============================================
    # 业务方法
    # ============================================
    
    @property
    def is_active(self) -> bool:
        """是否活跃项目"""
        return self.status == "active"
    
    @property
    def is_completed(self) -> bool:
        """是否已完成"""
        return self.status == "completed"
    
    @property
    def is_overdue(self) -> bool:
        """是否逾期"""
        if not self.deadline:
            return False
        return self.deadline < date.today() and not self.is_completed
    
    @property
    def progress_status(self) -> str:
        """项目进度状态"""
        if self.is_completed:
            return "已完成"
        elif self.is_overdue:
            return "已逾期"
        elif self.deadline:
            days_left = (self.deadline - date.today()).days
            if days_left <= 3:
                return f"即将到期({days_left}天)"
            else:
                return f"进行中({days_left}天后到期)"
        else:
            return "进行中"
    
    def update_from_dict(self, data: Dict[str, Any]):
        """从字典更新项目数据"""
        updatable_fields = [
            'name', 'description', 'status', 'priority', 
            'start_date', 'end_date', 'deadline', 
            # 'is_public',  # 暂时不支持公开功能
            'color'
        ]
        
        for key, value in data.items():
            if key in updatable_fields and hasattr(self, key):
                # 日期字段特殊处理
                if key in ['start_date', 'end_date', 'deadline'] and value:
                    if isinstance(value, str):
                        value = datetime.strptime(value, '%Y-%m-%d').date()
                
                setattr(self, key, value)
        
        self.updated_at = datetime.utcnow()
    
    def complete_project(self):
        """完成项目"""
        self.status = 'completed'
        self.end_date = date.today()
        self.updated_at = datetime.utcnow()
    
    def archive_project(self):
        """归档项目"""
        self.status = 'archived'
        self.updated_at = datetime.utcnow()
    
    # ============================================
    # 类方法 (查询方法)
    # ============================================
    
    @classmethod
    def create_from_dict(cls, data: Dict[str, Any]) -> 'Project':
        """从字典创建项目实例"""
        return cls(
            name=data['name'],
            user_id=data['user_id'],
            description=data.get('description'),
            status=data.get('status', 'active'),
            priority=data.get('priority', 1),
            start_date=data.get('start_date'),
            end_date=data.get('end_date'),
            deadline=data.get('deadline'),
            # is_public=data.get('is_public', False),  # 暂时不支持公开功能
            color=data.get('color', '#4CAF50')
        )

# ============================================
# 第11步：项目数据传输对象 (DTO)
# ============================================

@dataclass
class ProjectCreateRequest:
    """
    项目创建请求DTO
    
    对比SpringBoot:
    Flask ProjectCreateRequest ↔ SpringBoot ProjectCreateDto
    手动验证 ↔ @Valid + @NotNull等注解
    
    职责：
    1. 定义创建项目需要的数据结构
    2. 请求数据验证
    3. 数据清理和格式化
    4. 业务规则验证
    """
    
    name: str = ""
    description: Optional[str] = None
    user_id: int = 0
    priority: int = 1
    status: str = "active"
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    deadline: Optional[date] = None
    color: str = "#4CAF50"
    
    def __init__(self, data: Dict[str, Any]):
        """从请求数据初始化"""
        self.name = str(data.get('name', '')).strip()
        self.description = data.get('description', '').strip() if data.get('description') else None
        self.user_id = int(data.get('user_id', 0))
        self.priority = int(data.get('priority', 1))
        self.status = str(data.get('status', 'active')).strip()
        self.color = str(data.get('color', '#4CAF50')).strip()
        
        # 日期字段处理
        self.start_date = self._parse_date(data.get('start_date'))
        self.end_date = self._parse_date(data.get('end_date'))
        self.deadline = self._parse_date(data.get('deadline'))
        
        # 清理空字符串
        if self.description == '':
            self.description = None
    
    def _parse_date(self, date_str: Any) -> Optional[date]:
        """解析日期字符串"""
        if not date_str:
            return None
        
        if isinstance(date_str, date):
            return date_str
        
        if isinstance(date_str, str):
            try:
                return datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                try:
                    return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S').date()
                except ValueError:
                    return None
        
        return None
    
    def validate(self) -> None:
        """验证请求数据 - 抛出异常如果无效"""
        errors = []
        
        # 项目名验证
        if not self.name:
            errors.append("项目名不能为空")
        elif len(self.name) < 2:
            errors.append("项目名至少2个字符")
        elif len(self.name) > 200:
            errors.append("项目名最多200个字符")
        
        # 用户ID验证
        if not self.user_id:
            errors.append("必须指定项目所属用户")
        elif self.user_id <= 0:
            errors.append("用户ID必须是正整数")
        
        # 状态验证
        valid_statuses = ["active", "completed", "archived", "paused"]
        if self.status not in valid_statuses:
            errors.append(f"项目状态必须是: {', '.join(valid_statuses)}")
        
        # 优先级验证
        if not isinstance(self.priority, int) or self.priority < 1 or self.priority > 5:
            errors.append("优先级必须是1-5之间的整数")
        
        # 描述长度验证
        if self.description and len(self.description) > 2000:
            errors.append("项目描述最多2000个字符")
        
        # 颜色验证
        if self.color and not re.match(r'^#[0-9A-Fa-f]{6}$', self.color):
            errors.append("颜色必须是有效的十六进制格式，如#4CAF50")
        
        # 日期逻辑验证
        if self.start_date and self.end_date and self.start_date > self.end_date:
            errors.append("开始日期不能晚于结束日期")
        
        if self.deadline and self.start_date and self.deadline < self.start_date:
            errors.append("截止日期不能早于开始日期")
        
        if errors:
            raise ValueError(f"数据验证失败: {'; '.join(errors)}")
    
    def to_project_dict(self) -> Dict[str, Any]:
        """转换为创建Project实体所需的数据"""
        result = {
            'name': self.name,
            'user_id': self.user_id,
            'status': self.status,
            'priority': self.priority,
            'color': self.color
        }
        
        if self.description:
            result['description'] = self.description
        if self.start_date:
            result['start_date'] = self.start_date
        if self.end_date:
            result['end_date'] = self.end_date
        if self.deadline:
            result['deadline'] = self.deadline
        
        return result


@dataclass
class ProjectUpdateRequest:
    """
    项目更新请求DTO
    
    职责：
    1. 定义更新项目需要的数据结构
    2. 部分更新字段验证
    3. 只更新提供的字段
    """
    
    name: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[int] = None
    status: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    deadline: Optional[date] = None
    color: Optional[str] = None
    
    def __init__(self, data: Dict[str, Any]):
        """从请求数据初始化 - 只处理提供的字段"""
        if 'name' in data:
            self.name = str(data['name']).strip()
        
        if 'description' in data:
            desc = str(data['description']).strip() if data['description'] else None
            self.description = desc if desc else None
        
        if 'priority' in data:
            self.priority = int(data['priority'])
        
        if 'status' in data:
            self.status = str(data['status']).strip()
        
        if 'color' in data:
            self.color = str(data['color']).strip()
        
        # 日期字段处理
        if 'start_date' in data:
            self.start_date = self._parse_date(data['start_date'])
        
        if 'end_date' in data:
            self.end_date = self._parse_date(data['end_date'])
        
        if 'deadline' in data:
            self.deadline = self._parse_date(data['deadline'])
    
    def _parse_date(self, date_str: Any) -> Optional[date]:
        """解析日期字符串"""
        if not date_str:
            return None
        
        if isinstance(date_str, date):
            return date_str
        
        if isinstance(date_str, str):
            try:
                return datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                try:
                    return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S').date()
                except ValueError:
                    return None
        
        return None
    
    def validate(self) -> None:
        """验证更新数据"""
        errors = []
        
        # 项目名验证（如果提供）
        if self.name is not None:
            if not self.name:
                errors.append("项目名不能为空")
            elif len(self.name) < 2:
                errors.append("项目名至少2个字符")
            elif len(self.name) > 200:
                errors.append("项目名最多200个字符")
        
        # 状态验证（如果提供）
        if self.status is not None:
            valid_statuses = ["active", "completed", "archived", "paused"]
            if self.status not in valid_statuses:
                errors.append(f"项目状态必须是: {', '.join(valid_statuses)}")
        
        # 优先级验证（如果提供）
        if self.priority is not None:
            if not isinstance(self.priority, int) or self.priority < 1 or self.priority > 5:
                errors.append("优先级必须是1-5之间的整数")
        
        # 描述长度验证（如果提供）
        if self.description is not None and len(self.description) > 2000:
            errors.append("项目描述最多2000个字符")
        
        # 颜色验证（如果提供）
        if self.color is not None and not re.match(r'^#[0-9A-Fa-f]{6}$', self.color):
            errors.append("颜色必须是有效的十六进制格式，如#4CAF50")
        
        # 日期逻辑验证
        # 注意：这里只能验证当前提供的字段，完整的日期逻辑需要在Service层结合现有数据验证
        if (self.start_date is not None and self.end_date is not None and 
            self.start_date > self.end_date):
            errors.append("开始日期不能晚于结束日期")
        
        if (self.deadline is not None and self.start_date is not None and 
            self.deadline < self.start_date):
            errors.append("截止日期不能早于开始日期")
        
        if errors:
            raise ValueError(f"数据验证失败: {'; '.join(errors)}")
    
    def to_update_dict(self) -> Dict[str, Any]:
        """转换为更新数据字典 - 只包含非None字段"""
        result = {}
        
        if self.name is not None:
            result['name'] = self.name
        if self.description is not None:
            result['description'] = self.description
        if self.priority is not None:
            result['priority'] = self.priority
        if self.status is not None:
            result['status'] = self.status
        if self.start_date is not None:
            result['start_date'] = self.start_date
        if self.end_date is not None:
            result['end_date'] = self.end_date
        if self.deadline is not None:
            result['deadline'] = self.deadline
        if self.color is not None:
            result['color'] = self.color
        
        return result

# ============================================
# 第9步将要添加的功能（预留）
# ============================================
# TODO: 第10步解锁 - 添加与Note的关系
# notes = db.relationship('Note', backref='project', lazy=True)

# TODO: 第11步解锁 - 添加与Document的关系  
# documents = db.relationship('Document', backref='project', lazy=True)

print(f"📁 Project model loaded - 项目管理功能已就绪！")
