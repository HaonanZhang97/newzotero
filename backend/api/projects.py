"""
Projects API Module
项目管理的 API 端点

这个模块演示了如何使用统一的响应格式化工具
"""

from flask import Blueprint, jsonify, request

# 导入Service层
from ..services.project_service import ProjectService

# 导入统一的响应格式化工具
from ..utils.api_response import (
    format_response, 
    format_success_response, 
    format_error_response,
    handle_service_exception,
    HTTPStatus
)

# ============================================
# 创建项目管理蓝图
# ============================================

projects_bp = Blueprint(
    'projects',                    # 蓝图名称
    __name__,                      # 模块名
    url_prefix='/api/v1/projects'  # URL前缀
)

# ============================================
# RESTful API 端点
# ============================================

@projects_bp.route('', methods=['GET'])
def get_projects():
    """
    GET /api/v1/projects
    获取项目列表（根据用户ID）
    """
    try:
        # 需要用户ID参数来获取项目
        user_id = request.args.get('user_id', type=int)
        if not user_id:
            return format_error_response("缺少必需的用户ID参数", HTTPStatus.BAD_REQUEST)
        
        # 可选的分页参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        result = ProjectService.get_user_projects(user_id, page, per_page)
        return format_response(result)
    except Exception as e:
        return handle_service_exception(e, "获取项目列表失败")

@projects_bp.route('/<int:project_id>', methods=['GET'])
def get_project(project_id):
    """
    GET /api/v1/projects/{id}
    获取特定项目信息
    """
    try:
        result = ProjectService.get_project_by_id(project_id)
        return format_response(result)
    except Exception as e:
        return handle_service_exception(e)

@projects_bp.route('', methods=['POST'])
def create_project():
    """
    POST /api/v1/projects
    创建新项目
    """
    try:
        data = request.get_json()
        
        if not data:
            return format_error_response("请求数据不能为空", HTTPStatus.BAD_REQUEST)
        
        result = ProjectService.create_project(data)
        return format_response(result, success_status=HTTPStatus.CREATED)
    except Exception as e:
        return handle_service_exception(e)

@projects_bp.route('/<int:project_id>', methods=['PUT'])
def update_project(project_id):
    """
    PUT /api/v1/projects/{id}
    更新项目信息
    """
    try:
        data = request.get_json()
        
        if not data:
            return format_error_response("请求数据不能为空", HTTPStatus.BAD_REQUEST)
        
        # 假设从认证中获取当前用户ID，这里暂时使用默认值
        current_user_id = data.get('current_user_id', 1)
        result = ProjectService.update_project(project_id, data, current_user_id)
        return format_response(result)
    except Exception as e:
        return handle_service_exception(e)

@projects_bp.route('/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    """
    DELETE /api/v1/projects/{id}
    删除项目
    """
    try:
        # 假设从认证中获取当前用户ID，这里暂时使用默认值
        current_user_id = request.args.get('current_user_id', 1, type=int)
        result = ProjectService.delete_project(project_id, current_user_id)
        return format_response(result)
    except Exception as e:
        return handle_service_exception(e)

# ============================================
# 项目特殊操作端点
# ============================================

@projects_bp.route('/<int:project_id>/status', methods=['PATCH'])
def change_project_status(project_id):
    """
    PATCH /api/v1/projects/{id}/status
    更改项目状态
    """
    try:
        data = request.get_json()
        new_status = data.get('status') if data else None
        
        if not new_status:
            return format_error_response("缺少必需的状态参数", HTTPStatus.BAD_REQUEST)
        
        # 假设从认证中获取当前用户ID，这里暂时使用默认值
        current_user_id = data.get('current_user_id', 1)
        result = ProjectService.change_project_status(project_id, new_status, current_user_id)
        return format_response(result)
    except Exception as e:
        return handle_service_exception(e)

@projects_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user_projects(user_id):
    """
    GET /api/v1/projects/user/{user_id}
    获取用户的所有项目
    """
    try:
        result = ProjectService.get_user_projects(user_id)
        return format_response(result)
    except Exception as e:
        return handle_service_exception(e)

@projects_bp.route('/overdue', methods=['GET'])
def get_overdue_projects():
    """
    GET /api/v1/projects/overdue
    获取过期项目
    """
    try:
        user_id = request.args.get('user_id', type=int)  # 可选参数
        result = ProjectService.get_overdue_projects(user_id)
        return format_response(result)
    except Exception as e:
        return handle_service_exception(e)

@projects_bp.route('/statistics', methods=['GET'])
def get_project_statistics():
    """
    GET /api/v1/projects/statistics
    获取项目统计信息
    """
    try:
        user_id = request.args.get('user_id', type=int)
        if not user_id:
            return format_error_response("缺少必需的用户ID参数", HTTPStatus.BAD_REQUEST)
        
        result = ProjectService.get_user_project_statistics(user_id)
        return format_response(result)
    except Exception as e:
        return handle_service_exception(e)

# ============================================
# 项目查询和分析端点
# ============================================

@projects_bp.route('/search', methods=['POST'])
def search_projects():
    """
    POST /api/v1/projects/search
    根据条件搜索项目
    """
    try:
        data = request.get_json()
        if not data:
            return format_error_response("搜索条件不能为空", HTTPStatus.BAD_REQUEST)
        
        # 假设从认证中获取当前用户ID
        current_user_id = data.get('current_user_id', 1)
        criteria = data.get('criteria', {})
        
        result = ProjectService.search_projects(criteria, current_user_id)
        return format_response(result)
    except Exception as e:
        return handle_service_exception(e)

@projects_bp.route('/analytics', methods=['GET'])
def get_project_analytics():
    """
    GET /api/v1/projects/analytics?user_id={user_id}&days={days}
    获取项目分析数据
    """
    try:
        user_id = request.args.get('user_id', type=int)
        days = request.args.get('days', 30, type=int)
        
        if not user_id:
            return format_error_response("缺少必需的用户ID参数", HTTPStatus.BAD_REQUEST)
        
        result = ProjectService.get_project_analytics(user_id, days)
        return format_response(result)
    except Exception as e:
        return handle_service_exception(e)

@projects_bp.route('/<int:project_id>/with-user', methods=['GET'])
def get_project_with_user_info(project_id):
    """
    GET /api/v1/projects/{id}/with-user
    获取包含用户信息的项目详情
    """
    try:
        result = ProjectService.get_project_with_user_info(project_id)
        return format_response(result)
    except Exception as e:
        return handle_service_exception(e)

@projects_bp.route('/<int:project_id>/complete', methods=['PATCH'])
def mark_project_completed(project_id):
    """
    PATCH /api/v1/projects/{id}/complete
    标记项目完成
    """
    try:
        data = request.get_json() or {}
        current_user_id = data.get('current_user_id', 1)
        
        result = ProjectService.mark_project_completed(project_id, current_user_id)
        return format_response(result)
    except Exception as e:
        return handle_service_exception(e)

# ============================================
# 批量操作端点
# ============================================

@projects_bp.route('/bulk', methods=['PUT'])
def bulk_update_projects():
    """
    PUT /api/v1/projects/bulk
    批量更新项目
    """
    try:
        data = request.get_json()
        
        if not data or 'project_ids' not in data or 'update_data' not in data:
            return format_error_response(
                "请求数据格式错误，需要 project_ids 和 update_data", 
                HTTPStatus.BAD_REQUEST
            )
        
        # 假设从认证中获取当前用户ID，这里暂时使用默认值
        current_user_id = data.get('current_user_id', 1)
        result = ProjectService.bulk_update_projects(
            data['project_ids'], 
            data['update_data'], 
            current_user_id
        )
        return format_response(result)
    except Exception as e:
        return handle_service_exception(e)

@projects_bp.route('/bulk', methods=['DELETE'])
def bulk_delete_projects():
    """
    DELETE /api/v1/projects/bulk
    批量删除项目
    """
    try:
        data = request.get_json()
        
        if not data or 'project_ids' not in data:
            return format_error_response(
                "请求数据格式错误，需要 project_ids 数组", 
                HTTPStatus.BAD_REQUEST
            )
        
        # 假设从认证中获取当前用户ID，这里暂时使用默认值
        current_user_id = data.get('current_user_id', 1)
        result = ProjectService.bulk_delete_projects(data['project_ids'], current_user_id)
        return format_response(result)
    except Exception as e:
        return handle_service_exception(e)

# ============================================
# 模块信息端点
# ============================================

@projects_bp.route('/info', methods=['GET'])
def projects_info():
    """
    GET /api/v1/projects/info
    获取项目管理模块信息
    """
    try:
        service_info = ProjectService.get_service_info()
        
        api_info = {
            'module': 'Projects Management API',
            'blueprint_name': projects_bp.name,
            'url_prefix': projects_bp.url_prefix,
            'api_endpoints': [
                'GET /api/v1/projects - 获取项目列表',
                'GET /api/v1/projects/{id} - 获取特定项目',
                'POST /api/v1/projects - 创建新项目',
                'PUT /api/v1/projects/{id} - 更新项目',
                'DELETE /api/v1/projects/{id} - 删除项目',
                'PATCH /api/v1/projects/{id}/status - 更改项目状态',
                'PATCH /api/v1/projects/{id}/complete - 标记项目完成',
                'GET /api/v1/projects/{id}/with-user - 获取项目及用户信息',
                'GET /api/v1/projects/user/{user_id} - 获取用户项目',
                'GET /api/v1/projects/overdue - 获取过期项目',
                'GET /api/v1/projects/statistics - 获取统计信息',
                'GET /api/v1/projects/analytics - 获取分析数据',
                'POST /api/v1/projects/search - 搜索项目',
                'PUT /api/v1/projects/bulk - 批量更新项目',
                'DELETE /api/v1/projects/bulk - 批量删除项目',
                'GET /api/v1/projects/info - 模块信息'
            ],
            'service_layer': service_info
        }
        
        return format_success_response("模块信息获取成功", api_info)
    except Exception as e:
        return handle_service_exception(e, "获取模块信息失败")
