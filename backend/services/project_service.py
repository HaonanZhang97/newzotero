"""
第11步：项目业务逻辑服务层(Project Service) - 练习实现
=======================================================

学习目标：
- 练习Service层业务逻辑编排
- 掌握项目相关的业务规则
- 学习跨层数据传递
- 实现复杂业务流程
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, date, timedelta
from ..models.project_model import Project, ProjectCreateRequest, ProjectUpdateRequest
from ..models.user_model import User
from ..repositories.project_repository import ProjectRepository
from ..repositories.user_repository import UserRepository

class ProjectService:
    """
    项目业务逻辑服务类 - 你来实现！
    
    对比SpringBoot:
    Flask ProjectService ↔ SpringBoot @Service ProjectService
    Repository注入 ↔ @Autowired Repository
    业务逻辑编排 ↔ Business Logic Orchestration
    
    职责：
    1. 项目CRUD业务逻辑
    2. 项目状态管理
    3. 用户权限验证
    4. 业务规则验证
    5. 跨Repository数据协调
    """
    
    def __init__(self):
        """初始化Service，注入Repository依赖"""
        self.project_repository = ProjectRepository()
        self.user_repository = UserRepository()

    # ============================================
    # 项目CRUD业务逻辑
    # ============================================
    
    @classmethod
    def create_project(cls, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建新项目
        
        Args:
            project_data: 项目数据字典，包含：
                - name: 项目名称
                - description: 项目描述
                - user_id: 所属用户ID
                - priority: 优先级(1-5)
                - deadline: 截止时间
                - status: 项目状态
                # - is_public: 是否公开  # 暂时不支持公开功能
                
        Returns:
            创建结果字典
        """
        try:
            service = cls()
            
            # 第1步：DTO验证
            create_request = ProjectCreateRequest(project_data)
            create_request.validate()
            
            # 第2步：业务规则检查
            # 检查用户是否存在
            user = service.user_repository.find_by_id(create_request.user_id)
            if not user:
                return {"success": False, "message": f"用户ID {create_request.user_id} 不存在"}
            
            # 检查项目名称重复性（同一用户下）
            existing_projects = service.project_repository.find_by_user_and_status(
                create_request.user_id, create_request.status
            )
            for existing_project in existing_projects:
                if existing_project.name == create_request.name:
                    return {"success": False, "message": f"项目名称 '{create_request.name}' 已存在"}
            
            # 第3步：DTO → Entity转换
            project_data_dict = create_request.to_project_dict()
            project = Project(**project_data_dict)
            
            # 第4步：Entity验证
            errors = project.validate()
            if errors:
                return {"success": False, "errors": errors}
            
            # 第5步：Repository持久化
            saved_project = service.project_repository.save(project)
            
            return {
                "success": True,
                "message": "项目创建成功",
                "data": saved_project.to_dict()
            }
            
        except ValueError as e:
            return {"success": False, "message": str(e)}
        except Exception as e:
            return {"success": False, "message": f"创建失败: {str(e)}"}

    
    @classmethod
    def get_project_by_id(cls, project_id: int, current_user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        根据ID获取项目详情
        
        Args:
            project_id: 项目ID
            current_user_id: 当前用户ID（用于权限检查）
            
        Returns:
            项目详情字典
        """
        try:
            service = cls()
            project = service.project_repository.find_by_id(project_id)
            if not project:
                return {"success": False, "message": f"项目ID {project_id} 不存在"}
            if project.user_id != current_user_id:
                return {"success": False, "message": "无权访问该项目"}
            return {"success": True, "data": project.to_dict()}
        except Exception as e:
            return {"success": False, "message": f"获取项目失败: {str(e)}"}

    @classmethod
    def update_project(cls, project_id: int, update_data: Dict[str, Any], 
                      current_user_id: int) -> Dict[str, Any]:
        """
        更新项目信息
        
        Args:
            project_id: 项目ID
            update_data: 更新数据
            current_user_id: 当前用户ID
            
        Returns:
            更新结果字典
        """
        try:
            service = cls()
            project = service.project_repository.find_by_id(project_id)
            if not project:
                return {"success": False, "message": f"项目ID {project_id} 不存在"}
            if project.user_id != current_user_id:
                return {"success": False, "message": "无权访问该项目"}
            
            update_request = ProjectUpdateRequest(update_data)
            update_request.validate()
            
            request_data = update_request.to_update_dict()
            for key, value in request_data.items():
                if hasattr(project, key):
                    setattr(project, key, value)

            errors = project.validate()
            if errors:
                raise ValueError(f"项目数据验证失败: {'; '.join(errors)}")

            updated_project = service.project_repository.save(project)

            return {"success": True, "message": "项目更新成功", "data": updated_project.to_dict()}

        except ValueError as e:
            return {"success": False, "message": str(e), "data": None}
        except Exception as e:
            return {"success": False, "message": f"更新项目失败: {str(e)}"}

    @classmethod
    def delete_project(cls, project_id: int, current_user_id: int) -> Dict[str, Any]:
        """
        删除项目
        
        Args:
            project_id: 项目ID
            current_user_id: 当前用户ID
            
        Returns:
            删除结果字典
        """
        try:
            service = cls()
            project = service.project_repository.find_by_id(project_id)

            if not project:
                return {"success": False, "message": f"项目ID {project_id} 不存在"}
            if project.user_id != current_user_id:
                return {"success": False, "message": "无权访问该项目"}
            
            deleted = service.project_repository.delete(project)
            if deleted:
                return {"success": True, "message": "项目删除成功"}
            else:
                return {"success": False, "message": "项目删除失败"}
            
        except Exception as e:
            return {"success": False, "message": f"删除项目失败: {str(e)}"}

    # ============================================
    # 项目查询业务逻辑
    # ============================================
    
    @classmethod
    def get_user_projects(cls, user_id: int, page: int = 1, per_page: int = 10,
                         sort_by: str = 'created_at', sort_order: str = 'desc') -> Dict[str, Any]:
        """
        获取用户的项目列表（分页）
        
        Args:
            user_id: 用户ID
            page: 页码
            per_page: 每页数量
            sort_by: 排序字段
            sort_order: 排序方向
            
        Returns:
            项目列表和分页信息
        """
        try:
            service = cls()

            # 第1步：验证用户是否存在
            user = service.user_repository.find_by_id(user_id)
            if not user:
                return {"success": False, "message": f"用户ID {user_id} 不存在"}

            # 第2步：验证分页参数
            if page < 1:
                page = 1
            if per_page < 1:
                per_page = 10
            if per_page > 100:  # 限制每页最大数量
                per_page = 100

            # 第3步：验证排序参数
            valid_sort_fields = ['created_at', 'updated_at', 'name', 'priority', 'deadline']
            if sort_by not in valid_sort_fields:
                sort_by = 'created_at'
            
            if sort_order not in ['asc', 'desc']:
                sort_order = 'desc'

            # 第4步：使用Repository的分页排序方法
            projects, total_count, total_pages = service.project_repository.find_with_pagination(
                user_id=user_id,
                page=page,
                per_page=per_page,
                sort_by=sort_by,
                sort_order=sort_order
            )

            # 第5步：转换为字典格式
            projects_data = [project.to_dict() for project in projects]

            # 第6步：构建分页信息
            pagination_info = {
                'current_page': page,
                'per_page': per_page,
                'total_count': total_count,
                'total_pages': total_pages,
                'has_prev': page > 1,
                'has_next': page < total_pages,
                'prev_page': page - 1 if page > 1 else None,
                'next_page': page + 1 if page < total_pages else None
            }

            return {
                "success": True,
                "message": f"成功获取用户 {user_id} 的项目列表",
                "data": projects_data,
                "pagination": pagination_info,
                "sort": {
                    "sort_by": sort_by,
                    "sort_order": sort_order
                }
            }

        except Exception as e:
            return {"success": False, "message": f"获取用户项目列表失败: {str(e)}"}

    @classmethod
    def search_projects(cls, criteria: Dict[str, Any], 
                       current_user_id: int) -> Dict[str, Any]:
        """
        根据条件搜索项目
        
        Args:
            criteria: 搜索条件
            current_user_id: 当前用户ID（影响搜索范围）
            
        Returns:
            搜索结果
        """
        try:
            service = cls()
            
            # 第1步：验证当前用户是否存在
            user = service.user_repository.find_by_id(current_user_id)
            if not user:
                return {"success": False, "message": f"用户ID {current_user_id} 不存在"}
            
            # 第2步：处理搜索条件，融合user_id
            # 权限控制：用户只能搜索自己的项目
            search_criteria = criteria.copy()  # 复制原始条件，避免修改原始数据
            search_criteria['user_id'] = current_user_id  # 强制添加user_id限制
            
            # 第3步：验证搜索条件的合法性
            valid_criteria_keys = [
                'user_id', 'status', 'priority', 'name_like', 
                'created_after', 'created_before', 'deadline_before', 'deadline_after'
            ]
            
            # 过滤掉不合法的搜索条件
            filtered_criteria = {
                key: value for key, value in search_criteria.items() 
                if key in valid_criteria_keys and value is not None
            }
            
            # 第4步：执行搜索
            projects = service.project_repository.find_by_criteria(**filtered_criteria)
            
            # 第5步：转换为字典格式
            projects_data = [project.to_dict() for project in projects]
            
            # 第6步：返回搜索结果
            return {
                "success": True,
                "message": f"搜索完成，找到 {len(projects)} 个项目",
                "data": projects_data,
                "search_criteria": filtered_criteria,
                "result_count": len(projects)
            }
            
        except Exception as e:
            return {"success": False, "message": f"搜索项目失败: {str(e)}"}

    # 注释：暂时不支持公开项目功能，因为模型中没有is_public字段
    # @classmethod
    # def get_public_projects(cls, limit: int = 10) -> Dict[str, Any]:
    #     """
    #     获取公开项目列表
    #     
    #     Args:
    #         limit: 返回数量限制
    #         
    #     Returns:
    #         公开项目列表
    #     """
    #     # TODO: 实现获取公开项目的业务逻辑
    #     # 注意：需要先在Project模型中添加is_public字段
    #     pass
    
    # ============================================
    # 项目状态管理
    # ============================================
    
    @classmethod
    def change_project_status(cls, project_id: int, new_status: str, 
                             current_user_id: int) -> Dict[str, Any]:
        """
        修改项目状态
        
        Args:
            project_id: 项目ID
            new_status: 新状态
            current_user_id: 当前用户ID
            
        Returns:
            状态修改结果
        """
        try:
            service = cls()
            
            # 第1步：获取项目信息（用于状态转换验证）
            project = service.project_repository.find_by_id(project_id)
            if not project:
                return {"success": False, "message": f"项目ID {project_id} 不存在"}
            if project.user_id != current_user_id:
                return {"success": False, "message": "无权访问该项目"}
            
            # 第2步：验证状态转换是否合法
            old_status = project.status
            if not cls._is_valid_status_transition(old_status, new_status):
                return {
                    "success": False, 
                    "message": f"不允许从状态 '{old_status}' 转换为 '{new_status}'"
                }
            
            # 第3步：使用 update_project 进行状态更新
            result = cls.update_project(
                project_id=project_id,
                update_data={"status": new_status},
                current_user_id=current_user_id
            )
            
            # 第4步：如果更新成功，添加状态变更的特殊处理
            if result.get("success"):
                # 这里可以添加状态变更后的业务逻辑
                # 比如：发送通知、记录日志、触发其他流程等
                result["message"] = f"项目状态已从 '{old_status}' 更改为 '{new_status}'"
                result["status_change"] = {
                    "from": old_status,
                    "to": new_status,
                    "changed_by": current_user_id,
                    "changed_at": datetime.now().isoformat()
                }
            
            return result
            
        except Exception as e:
            return {"success": False, "message": f"状态变更失败: {str(e)}"}
    
    @staticmethod
    def _is_valid_status_transition(from_status: str, to_status: str) -> bool:
        """
        验证状态转换是否合法
        
        Args:
            from_status: 原状态
            to_status: 目标状态
            
        Returns:
            是否允许转换
        """
        # 定义允许的状态转换规则
        valid_transitions = {
            'pending': ['active', 'cancelled'],
            'active': ['completed', 'paused', 'cancelled'],
            'paused': ['active', 'cancelled'],
            'completed': [],  # 完成状态不允许转换到其他状态
            'cancelled': []   # 取消状态不允许转换到其他状态
        }
        
        return to_status in valid_transitions.get(from_status, [])

    
    @classmethod
    def get_overdue_projects(cls, user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        获取逾期项目
        
        Args:
            user_id: 用户ID（可选，管理员可以查看所有用户的）
            
        Returns:
            逾期项目列表
        """
        try:
            service = cls()
            
            # 第1步：如果指定了用户ID，验证用户是否存在
            if user_id is not None:
                user = service.user_repository.find_by_id(user_id)
                if not user:
                    return {"success": False, "message": f"用户ID {user_id} 不存在"}
            
            # 第2步：调用Repository的find_overdue_projects方法
            overdue_projects = service.project_repository.find_overdue_projects(user_id)
            
            # 第3步：转换为字典格式
            projects_data = [project.to_dict() for project in overdue_projects]
            
            # 第4步：构建返回结果
            return {
                "success": True,
                "message": f"找到 {len(overdue_projects)} 个逾期项目",
                "data": projects_data,
                "overdue_count": len(overdue_projects),
                "filter": {
                    "user_id": user_id,
                    "checked_date": date.today().isoformat()
                }
            }
            
        except Exception as e:
            return {"success": False, "message": f"获取逾期项目失败: {str(e)}"}
    
    @classmethod
    def mark_project_completed(cls, project_id: int, current_user_id: int) -> Dict[str, Any]:
        """
        标记项目完成
        
        Args:
            project_id: 项目ID
            current_user_id: 当前用户ID
            
        Returns: 
            完成标记结果
        """
        return cls.change_project_status(project_id, 'completed', current_user_id)
    
    # ============================================
    # 批量操作业务逻辑
    # ============================================
    
    @classmethod
    def bulk_update_projects(cls, project_ids: List[int], update_data: Dict[str, Any],
                            current_user_id: int) -> Dict[str, Any]:
        """
        批量更新项目
        
        Args:
            project_ids: 项目ID列表
            update_data: 更新数据
            current_user_id: 当前用户ID
            
        Returns:
            批量更新结果
        """
        try:
            service = cls()
            
            # 第1步：验证输入
            if not project_ids:
                return {"success": False, "message": "项目ID列表不能为空"}
            
            # 第2步：验证所有项目的权限
            projects = []
            for project_id in project_ids:
                project = service.project_repository.find_by_id(project_id)
                if not project:
                    return {"success": False, "message": f"项目ID {project_id} 不存在"}
                if project.user_id != current_user_id:
                    return {"success": False, "message": f"无权访问项目ID {project_id}"}
                projects.append(project)
            
            # 第3步：检查是否只是状态更新（可以使用批量更新）
            if len(update_data) == 1 and 'status' in update_data:
                # 批量状态更新
                new_status = update_data['status']
                
                # 验证状态转换
                for project in projects:
                    if not cls._is_valid_status_transition(project.status, new_status):
                        return {
                            "success": False,
                            "message": f"项目 '{project.name}' 不允许从状态 '{project.status}' 转换为 '{new_status}'"
                        }
                
                # 执行批量状态更新
                updated_count = service.project_repository.bulk_update_status(project_ids, new_status)
                
                return {
                    "success": True,
                    "message": f"成功批量更新 {updated_count} 个项目的状态",
                    "updated_count": updated_count,
                    "update_type": "bulk_status_update",
                    "data": {"status": new_status}
                }
            
            else:
                # 复杂更新，逐个处理
                success_count = 0
                failed_projects = []
                
                for project_id in project_ids:
                    result = cls.update_project(project_id, update_data, current_user_id)
                    if result.get("success"):
                        success_count += 1
                    else:
                        failed_projects.append({"project_id": project_id, "error": result.get("message")})
                
                return {
                    "success": True,
                    "message": f"批量更新完成：成功 {success_count} 个，失败 {len(failed_projects)} 个",
                    "success_count": success_count,
                    "failed_count": len(failed_projects),
                    "failed_projects": failed_projects,
                    "update_type": "individual_update"
                }
                
        except Exception as e:
            return {"success": False, "message": f"批量更新项目失败: {str(e)}"}

    
    @classmethod
    def bulk_delete_projects(cls, project_ids: List[int], 
                            current_user_id: int) -> Dict[str, Any]:
        """
        批量删除项目
        
        Args:
            project_ids: 项目ID列表
            current_user_id: 当前用户ID
            
        Returns:
            批量删除结果
        """
        try:
            service = cls()
            
            # 第1步：验证输入
            if not project_ids:
                return {"success": False, "message": "项目ID列表不能为空"}
            
            # 第2步：验证所有项目的权限
            valid_project_ids = []
            for project_id in project_ids:
                project = service.project_repository.find_by_id(project_id)
                if not project:
                    return {"success": False, "message": f"项目ID {project_id} 不存在"}
                if project.user_id != current_user_id:
                    return {"success": False, "message": f"无权访问项目ID {project_id}"}
                valid_project_ids.append(project_id)
            
            # 第3步：执行批量删除
            deleted_count = service.project_repository.bulk_delete_by_ids(valid_project_ids)
            
            return {
                "success": True,
                "message": f"成功删除 {deleted_count} 个项目",
                "deleted_count": deleted_count,
                "deleted_project_ids": valid_project_ids
            }
            
        except Exception as e:
            return {"success": False, "message": f"批量删除项目失败: {str(e)}"}
    
    # ============================================
    # 统计和分析业务逻辑
    # ============================================
    
    @classmethod
    def get_user_project_statistics(cls, user_id: int) -> Dict[str, Any]:
        """
        获取用户项目统计信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            统计信息字典
        """
        try:
            service = cls()
            
            # 第1步：验证用户是否存在
            user = service.user_repository.find_by_id(user_id)
            if not user:
                return {"success": False, "message": f"用户ID {user_id} 不存在"}
            
            # 第2步：调用Repository的统计方法
            stats = service.project_repository.get_user_project_statistics(user_id)
            
            # 第3步：计算完成率
            total_count = stats.get('total_count', 0)
            completed_count = stats.get('completed_count', 0)
            completion_rate = round((completed_count / total_count * 100), 2) if total_count > 0 else 0.0
            
            # 第4步：构建增强的统计信息
            enhanced_stats = {
                **stats,
                'completion_rate': completion_rate,
                'pending_count': stats.get('active_count', 0),  # 活跃项目包含待开始的
                'completion_rate_text': f"{completion_rate}%"
            }
            
            return {
                "success": True,
                "message": f"成功获取用户 {user_id} 的项目统计信息",
                "data": enhanced_stats,
                "summary": {
                    "user_id": user_id,
                    "total_projects": total_count,
                    "completion_status": "优秀" if completion_rate >= 80 else "良好" if completion_rate >= 60 else "需要改进"
                }
            }
            
        except Exception as e:
            return {"success": False, "message": f"获取项目统计失败: {str(e)}"}
    
    @classmethod
    def get_project_analytics(cls, user_id: int, days: int = 30) -> Dict[str, Any]:
        """
        获取项目分析数据
        
        Args:
            user_id: 用户ID
            days: 分析天数
            
        Returns:
            分析数据
        """
        try:
            service = cls()
            
            # 第1步：验证用户是否存在
            user = service.user_repository.find_by_id(user_id)
            if not user:
                return {"success": False, "message": f"用户ID {user_id} 不存在"}
            
            # 第2步：获取基础统计信息
            basic_stats = service.project_repository.get_user_project_statistics(user_id)
            
            # 第3步：获取优先级分布
            priority_distribution = service.project_repository.get_priority_distribution(user_id)
            
            # 第4步：获取逾期项目
            overdue_projects = service.project_repository.find_overdue_projects(user_id)
            
            # 第5步：计算时间范围内的项目（最近N天创建的）
            end_date = date.today()
            start_date = end_date - timedelta(days=days)
            
            recent_projects = service.project_repository.find_by_criteria(
                user_id=user_id,
                created_after=start_date
            )
            
            # 第6步：构建分析数据
            analytics_data = {
                "basic_statistics": basic_stats,
                "priority_distribution": priority_distribution,
                "time_analysis": {
                    "period_days": days,
                    "recent_projects_count": len(recent_projects),
                    "recent_projects_rate": round(len(recent_projects) / max(basic_stats.get('total_count', 1), 1) * 100, 2)
                },
                "overdue_analysis": {
                    "overdue_count": len(overdue_projects),
                    "overdue_projects": [proj.to_dict() for proj in overdue_projects[:5]]  # 只返回前5个
                },
                "insights": []
            }
            
            # 第7步：生成洞察建议
            insights = []
            completion_rate = (basic_stats.get('completed_count', 0) / max(basic_stats.get('total_count', 1), 1)) * 100
            
            if completion_rate < 50:
                insights.append("完成率较低，建议优化项目管理流程")
            elif completion_rate > 80:
                insights.append("项目完成率很高，保持良好的工作习惯")
            
            if len(overdue_projects) > 0:
                insights.append(f"有 {len(overdue_projects)} 个项目逾期，建议及时处理")
                
            if len(recent_projects) == 0 and days <= 7:
                insights.append("最近没有新项目，可以考虑制定新的目标")
            
            analytics_data["insights"] = insights
            
            return {
                "success": True,
                "message": f"成功获取用户 {user_id} 的项目分析数据",
                "data": analytics_data,
                "analysis_period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "days": days
                }
            }
            
        except Exception as e:
            return {"success": False, "message": f"获取项目分析失败: {str(e)}"}
    
    # ============================================
    # 项目权限和验证
    # ============================================
    
    @classmethod
    def check_project_access_permission(cls, project_id: int, 
                                       user_id: int, action: str = 'read') -> bool:
        """
        检查项目访问权限
        
        Args:
            project_id: 项目ID
            user_id: 用户ID
            action: 操作类型 ('read', 'write', 'delete')
            
        Returns:
            是否有权限
        """
        try:
            service = cls()
            project = service.project_repository.find_by_id(project_id)
            
            if not project:
                return False
                
            # 基础权限规则：项目所有者拥有全部权限
            if project.user_id == user_id:
                return True
            
            # 其他权限规则（未来扩展）
            # 1. 如果有is_public字段，公开项目任何人可读
            # 2. 如果有协作功能，协作者可能有部分权限
            
            return False
            
        except Exception:
            return False
    
    @classmethod
    def validate_project_data(cls, project_data: Dict[str, Any], 
                             is_update: bool = False) -> List[str]:
        """
        验证项目数据
        
        Args:
            project_data: 项目数据
            is_update: 是否为更新操作
            
        Returns:
            错误信息列表（空列表表示验证通过）
        """
        errors = []
        
        try:
            if is_update:
                # 更新操作使用 ProjectUpdateRequest
                update_request = ProjectUpdateRequest(project_data)
                update_request.validate()
            else:
                # 创建操作使用 ProjectCreateRequest
                create_request = ProjectCreateRequest(project_data)
                create_request.validate()
                
        except ValueError as e:
            errors.append(str(e))
        except Exception as e:
            errors.append(f"数据验证失败: {str(e)}")
            
        return errors
    
    # ============================================
    # 项目关联操作
    # ============================================
    
    @classmethod
    def get_project_with_user_info(cls, project_id: int) -> Dict[str, Any]:
        """
        获取包含用户信息的项目详情
        
        Args:
            project_id: 项目ID
            
        Returns:
            项目和用户信息
        """
        try:
            service = cls()
            
            # 第1步：获取项目信息
            project = service.project_repository.find_by_id(project_id)
            if not project:
                return {"success": False, "message": f"项目ID {project_id} 不存在"}
            
            # 第2步：获取用户信息
            user = service.user_repository.find_by_id(project.user_id)
            if not user:
                return {"success": False, "message": f"项目所属用户不存在"}
            
            # 第3步：构建包含用户信息的项目数据
            project_data = project.to_dict()
            project_data['user_info'] = {
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'created_at': user.created_at.isoformat() if user.created_at else None
            }
            
            return {
                "success": True,
                "message": "成功获取项目和用户信息",
                "data": project_data
            }
            
        except Exception as e:
            return {"success": False, "message": f"获取项目用户信息失败: {str(e)}"}
    
    @classmethod
    def check_project_name_duplicate(cls, user_id: int, project_name: str, 
                                    exclude_project_id: Optional[int] = None) -> bool:
        """
        检查项目名称是否重复
        
        Args:
            user_id: 用户ID
            project_name: 项目名称
            exclude_project_id: 排除的项目ID（用于更新时检查）
            
        Returns:
            是否重复
        """
        try:
            service = cls()
            
            # 获取用户的所有项目
            user_projects = service.project_repository.find_by_user_id(user_id)
            
            for project in user_projects:
                # 排除指定的项目ID（更新时使用）
                if exclude_project_id and project.id == exclude_project_id:
                    continue
                    
                # 检查名称是否重复（不区分大小写）
                if project.name.lower() == project_name.lower():
                    return True
            
            return False
            
        except Exception:
            # 出现异常时，为了安全起见，返回True（表示可能重复）
            return True
    
    # ============================================
    # 服务信息和工具方法
    # ============================================
    
    @classmethod
    def get_service_info(cls) -> Dict[str, Any]:
        """获取服务信息"""
        return {
            'service_name': 'ProjectService',
            'version': '1.0.0',
            'description': '项目管理业务逻辑服务 - 完整分层架构',
            'layer_integration': {
                'controller_layer': '✅ Flask API routes',
                'service_layer': '✅ Business logic & validation',
                'repository_layer': '✅ Data access & persistence',
                'model_layer': '✅ Entity models',
                'storage_layer': '✅ Database storage'
            },
            'complete_architecture': 'HTTP → Controller → Service → Repository → Database',
            'features': [
                '项目CRUD操作',
                '权限控制',
                '状态管理',
                '批量操作',
                '统计分析',
                '数据验证',
                '业务规则执行'
            ]
        }


