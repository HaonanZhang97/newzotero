"""
第10步：项目数据仓储层(Project Repository) - 练习实现
====================================================

学习目标：
- 练习Repository模式实现
- 掌握项目相关的数据库操作
- 学习外键关系查询
- 实现复杂查询条件
"""

# type: ignore  # 忽略 SQLAlchemy 类型检查问题

from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, date, timedelta
from sqlalchemy import and_, or_, desc, asc, func
from sqlalchemy.orm import joinedload
from ..models.project_model import db, Project
from ..models.user_model import User

class ProjectRepository:
    """
    项目数据仓储类 - 你来实现！
    
    对比SpringBoot:
    Flask ProjectRepository ↔ SpringBoot JpaRepository<Project, Long>
    外键查询 ↔ @Query with JOIN
    动态查询 ↔ Criteria API
    
    职责：
    1. 项目数据的CRUD操作
    2. 用户-项目关系查询
    3. 复杂条件查询
    4. 统计和聚合查询
    """
    
    def __init__(self):
        """初始化Repository"""
        # TODO: 实现初始化逻辑（如果需要的话）
        pass
    
    # ============================================
    # CRUD操作 - Create, Read, Update, Delete
    # ============================================
    
    def save(self, project: Project) -> Project:
        """
        保存项目（创建或更新）
        
        Args:
            project: 要保存的项目对象
            
        Returns:
            保存后的项目对象（包含生成的ID）
            
        Raises:
            Exception: 保存失败时抛出异常
        """

        errors = project.validate()
        if errors:
            raise ValueError(f"项目数据验证失败: {errors}")
        
        try:
            if project.id is None:
                db.session.add(project)
            else:
                pass

            db.session.commit()
            return project
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"保存项目失败: {e}")
        

    def find_by_id(self, project_id: int) -> Optional[Project]:
        """
        根据ID查找项目
        
        Args:
            project_id: 项目ID
            
        Returns:
            找到的项目或None
        """

        return Project.query.get(project_id)
    
    def find_all(self) -> List[Project]:
        """
        获取所有项目
        
        Returns:
            所有项目列表
        """

        return Project.query.all()
    
    def update(self, project_id: int, update_data: Dict[str, Any]) -> Optional[Project]:
        """
        更新项目
        
        Args:
            project: 要更新的项目对象
            
        Returns:
            更新后的项目对象
        """
        try:
            project = self.find_by_id(project_id)
            if project:
                project.update_from_dict(update_data)

                errors = project.validate()
                if errors:
                    raise ValueError(f"更新数据无效: {'; '.join(errors)}")

                db.session.commit()
                return project
            return None
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"更新项目失败: {e}")

    def delete_by_id(self, project_id: int) -> bool:
        """
        根据ID删除项目
        
        Args:
            project_id: 要删除的项目ID
            
        Returns:
            是否删除成功
        """
        try:
            project = self.find_by_id(project_id)
            if project:
                db.session.delete(project)
                db.session.commit()
                return True
            return False
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"删除项目失败: {e}")

    def delete(self, project: Project) -> bool:
        """
        删除项目对象
        
        Args:
            project: 要删除的项目对象
            
        Returns:
            是否删除成功
        """
        try:
            db.session.delete(project)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"删除项目失败: {e}")

    # ============================================
    # 用户相关查询
    # ============================================
    
    def find_by_user_id(self, user_id: int) -> List[Project]:
        """
        查找某个用户的所有项目
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户的项目列表
        """
        return Project.query.filter_by(user_id=user_id).all()
    
    def find_by_user_and_status(self, user_id: int, status: str) -> List[Project]:
        """
        根据用户和状态查找项目
        
        Args:
            user_id: 用户ID
            status: 项目状态
            
        Returns:
            符合条件的项目列表
        """
        return Project.query.filter_by(user_id=user_id, status=status).all()

    def get_user_project_count(self, user_id: int) -> int:
        """
        获取用户的项目总数
        
        Args:
            user_id: 用户ID
            
        Returns:
            项目总数
        """
        try:
            return Project.query.filter_by(user_id=user_id).count()
        except Exception as e:
            raise RuntimeError(f"获取用户项目总数失败: {e}")

    def find_user_active_projects(self, user_id: int) -> List[Project]:
        """
        查找用户的活跃项目
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户的活跃项目列表
        """
        return Project.query.filter_by(user_id=user_id, status='active').all()
    
    # ============================================
    # 复杂查询和条件筛选
    # ============================================
    
    def find_by_criteria(self, **criteria) -> List[Project]:
        """
        根据复合条件查找项目
        
        Args:
            criteria: 查询条件字典，可能包含：
                - user_id: 用户ID
                - status: 项目状态
                - priority: 优先级
                - name_like: 项目名模糊查询
                - is_public: 是否公开
                - created_after: 创建时间之后
                - created_before: 创建时间之前
                - deadline_before: 截止时间之前
                
        Returns:
            符合条件的项目列表
        """
        query = Project.query
        for key, value in criteria.items():
            if key == 'name_like':
                # 使用 ilike 进行不区分大小写的模糊匹配
                query = query.filter(Project.name.ilike(f"%{value}%"))  # type: ignore
            elif key == 'created_after':
                query = query.filter(Project.created_at >= value)
            elif key == 'created_before':
                query = query.filter(Project.created_at <= value)
            elif key == 'deadline_after':
                query = query.filter(Project.deadline >= value)  
            elif key == 'deadline_before':
                query = query.filter(Project.deadline <= value)
            elif hasattr(Project, key):
                query = query.filter(getattr(Project, key) == value)

        return query.all()

    def find_overdue_projects(self, user_id: Optional[int] = None) -> List[Project]:
        """
        查找逾期项目
        
        Args:
            user_id: 可选的用户ID，如果提供则只查找该用户的逾期项目
            
        Returns:
            逾期项目列表
        """
        try:
            today = date.today()
            query = Project.query.filter(
                Project.deadline < today,  # type: ignore
                Project.status != 'completed'  # type: ignore
            )
            if user_id is not None:
                query = query.filter(Project.user_id == user_id)  # type: ignore
            return query.all()

        except Exception as e:
            raise RuntimeError(f"查找逾期项目失败: {e}")

    def find_by_priority_range(self, user_id: int, min_priority: int, max_priority: int) -> List[Project]:
        """
        根据优先级范围查找项目
        
        Args:
            user_id: 用户ID
            min_priority: 最小优先级
            max_priority: 最大优先级
            
        Returns:
            符合优先级范围的项目列表
        """
        try:
            return Project.query.filter_by(user_id=user_id).filter(
                Project.priority.between(min_priority, max_priority)  # type: ignore
            ).all()  # type: ignore
        except Exception as e:
            raise RuntimeError(f"根据优先级范围查找项目失败: {e}")
    
    # ============================================
    # 排序和分页
    # ============================================
    
    def find_user_projects_sorted(self, user_id: int, sort_by: str = 'created_at', 
                                  sort_order: str = 'desc') -> List[Project]:
        """
        获取用户项目并排序
        
        Args:
            user_id: 用户ID
            sort_by: 排序字段 ('created_at', 'updated_at', 'name', 'priority', 'deadline')
            sort_order: 排序方向 ('asc' 或 'desc')
            
        Returns:
            排序后的项目列表
        """
        try:
            # 先筛选用户的项目
            query = Project.query.filter_by(user_id=user_id)
            
            # 根据字段名获取对应的列对象
            if sort_by == 'updated_at':
                sort_column = Project.updated_at
            elif sort_by == 'name':
                sort_column = Project.name
            elif sort_by == 'priority':
                sort_column = Project.priority
            elif sort_by == 'deadline':
                sort_column = Project.deadline
            else:
                # 默认按创建时间排序
                sort_column = Project.created_at
            
            # 根据排序方向应用排序
            if sort_order == 'asc':
                query = query.order_by(asc(sort_column))  # type: ignore
            else:
                query = query.order_by(desc(sort_column))  # type: ignore
            
            return query.all()
            
        except Exception as e:
            raise RuntimeError(f"获取用户项目失败: {e}")

    def find_with_pagination(self, user_id: int, page: int = 1, 
                           per_page: int = 10) -> Tuple[List[Project], int, int]:
        """
        分页查询用户项目
        
        Args:
            user_id: 用户ID
            page: 页码（从1开始）
            per_page: 每页数量
            
        Returns:
            (项目列表, 总数量, 总页数)
        """
        try:
            # SQLAlchemy 的分页查询
            pagination = Project.query.filter_by(user_id=user_id).paginate(
                page=page,
                per_page=per_page,
                error_out=False  # 页码超出范围时不抛错，返回空列表
            )
            
            return (
                pagination.items,              # 当前页的项目列表
                pagination.total or 0,         # 总记录数（处理None情况）
                pagination.pages               # 总页数
            )
            
        except Exception as e:
            raise RuntimeError(f"分页查询失败: {e}")
    
    # ============================================
    # 统计和聚合查询
    # ============================================
    
    def get_user_project_statistics(self, user_id: int) -> Dict[str, Any]:
        """
        获取用户项目统计信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            统计信息字典，包含：
            - total_count: 总项目数
            - active_count: 活跃项目数
            - completed_count: 已完成项目数
            - overdue_count: 逾期项目数
            - avg_priority: 平均优先级
        """
        try:
            from sqlalchemy import func
            
            total_count = Project.query.filter_by(user_id=user_id).count()  # type: ignore
            
            # 活跃项目（进行中 + 待开始）
            active_count = Project.query.filter_by(user_id=user_id).filter(
                Project.status.in_(['pending', 'in_progress'])  # type: ignore
            ).count()  # type: ignore
            
            completed_count = Project.query.filter_by(user_id=user_id, status='completed').count()  # type: ignore
            
            # 逾期项目数量
            overdue_count = len(self.find_overdue_projects(user_id))
            
            # 平均优先级
            avg_priority_result = Project.query.filter_by(user_id=user_id).with_entities(
                func.avg(Project.priority)  # type: ignore
            ).scalar()
            avg_priority = round(avg_priority_result, 2) if avg_priority_result else 0.0
            
            return {
                'total_count': total_count,
                'active_count': active_count,
                'completed_count': completed_count,
                'overdue_count': overdue_count,
                'avg_priority': avg_priority
            }
            
        except Exception as e:
            raise RuntimeError(f"获取统计信息失败: {e}")
    
    def get_priority_distribution(self, user_id: int) -> Dict[int, int]:
        """
        获取用户项目优先级分布
        
        Args:
            user_id: 用户ID
            
        Returns:
            优先级分布字典 {优先级: 数量}
        """
        try:
            from sqlalchemy import func
            
            # 查询优先级分布
            results = Project.query.filter_by(user_id=user_id).with_entities(
                Project.priority,  # type: ignore
                func.count(Project.id).label('count')  # type: ignore
            ).group_by(Project.priority).all()  # type: ignore
            
            # 转换为字典格式
            distribution = {}
            for priority, count in results:
                distribution[priority] = count
                
            return distribution
            
        except Exception as e:
            raise RuntimeError(f"获取优先级分布失败: {e}")
    
    # ============================================
    # 关联查询
    # ============================================
    
    def find_with_user_info(self, project_id: int) -> Optional[Project]:
        """
        查找项目并包含用户信息
        
        Args:
            project_id: 项目ID
            
        Returns:
            包含用户信息的项目对象
        """
        try:
            # 使用 joinedload 在一次查询中获取项目和用户信息
            project = Project.query.options(
                joinedload(Project.user)  # type: ignore
            ).filter(Project.id == project_id).first()  # type: ignore
            
            return project
            
        except Exception as e:
            raise RuntimeError(f"查询项目用户信息失败: {e}")
    
    def find_public_projects(self, limit: int = 10) -> List[Project]:
        """
        查找公开项目
        
        Args:
            limit: 返回数量限制
            
        Returns:
            公开项目列表
        """
        try:
            projects = Project.query.filter_by(is_public=True).order_by(
                Project.created_at.desc()  # type: ignore
            ).limit(limit).all()  # type: ignore
            
            return projects
            
        except Exception as e:
            raise RuntimeError(f"查询公开项目失败: {e}")
    
    # ============================================
    # 批量操作
    # ============================================
    
    def bulk_update_status(self, project_ids: List[int], new_status: str) -> int:
        """
        批量更新项目状态
        
        Args:
            project_ids: 项目ID列表
            new_status: 新状态
            
        Returns:
            更新的项目数量
        """
        try:
            if not project_ids:
                return 0
                
            updated_count = Project.query.filter(
                Project.id.in_(project_ids)  # type: ignore
            ).update(
                {'status': new_status},
                synchronize_session='fetch'
            )
            
            db.session.commit()
            return updated_count
            
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"批量更新状态失败: {e}")
    
    def bulk_delete_by_ids(self, project_ids: List[int]) -> int:
        """
        批量删除项目
        
        Args:
            project_ids: 要删除的项目ID列表
            
        Returns:
            删除的项目数量
        """
        try:
            if not project_ids:
                return 0
                
            deleted_count = Project.query.filter(
                Project.id.in_(project_ids)  # type: ignore
            ).delete(synchronize_session='fetch')
            
            db.session.commit()
            return deleted_count
            
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"批量删除失败: {e}")
    
    # ============================================
    # 事务管理
    # ============================================
    
    def save_multiple(self, projects: List[Project]) -> List[Project]:
        """
        批量保存项目（事务性）
        
        Args:
            projects: 项目列表
            
        Returns:
            保存后的项目列表
        """
        try:
            if not projects:
                return []
            
            # 验证所有项目
            for project in projects:
                if not project.name or not project.name.strip():
                    raise ValueError(f"项目名称不能为空")
                if not project.user_id:
                    raise ValueError(f"项目必须关联用户")
            
            # 批量添加到会话
            for project in projects:
                db.session.add(project)
            
            # 提交事务
            db.session.commit()
            
            return projects
            
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"批量保存失败: {e}")

