
from flask import Blueprint, jsonify, request
from typing import Tuple, Any

# 第5步：导入Service层
from ..services.user_service import UserService

# 导入统一的响应格式化工具
from ..utils.api_response import (
    format_response, 
    format_success_response, 
    format_error_response,
    handle_service_exception,
    HTTPStatus
)

# ============================================
# 第5步：使用Service层的 Blueprint
# ============================================

# 创建用户管理蓝图
users_bp = Blueprint(
    'users',                    # 蓝图名称
    __name__,                   # 模块名
    url_prefix='/api/v1/users'  # URL前缀
)

# ============================================
# 第5步：使用Service层的RESTful路由
# ============================================

@users_bp.route('', methods=['GET'])
def get_users():
    """
    GET /api/v1/users
    获取所有用户列表
    
    """
    
    try:
        # 🏢 调用Service层处理业务逻辑
        result = UserService.get_all_users()
        return format_response(result)

    except Exception as e:
        return handle_service_exception(e, "获取用户列表失败")

@users_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """
    GET /api/v1/users/{id}
    获取特定用户信息
    
    第5步改进：参数提取 + Service层调用 + 错误处理
    """
    
    try:
        # 🏢 调用Service层处理业务逻辑
        result = UserService.get_user_by_id(user_id)
        return format_response(result)

    except Exception as e:
        return handle_service_exception(e)
          

@users_bp.route('', methods=['POST'])
def create_user():
    """
    POST /api/v1/users
    创建新用户
    
    第5步改进：复杂的业务逻辑全部交给Service层
    """
    print("📋 API层: POST /api/v1/users - 接收请求")
    
    try:
        # 步骤1：获取请求数据（API层职责）
        data = request.get_json()
        
        if not data:
            return format_error_response("请求数据不能为空", HTTPStatus.BAD_REQUEST)
        
        # 步骤2：🏢 调用Service层处理所有业务逻辑
        result = UserService.create_user(data)
        return format_response(result, success_status=HTTPStatus.CREATED)

    except Exception as e:
        return handle_service_exception(e)
    

@users_bp.route('/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """
    PUT /api/v1/users/{id}
    更新用户信息
    """
    try:
        data = request.get_json()
        if not data:
            return format_error_response("请求数据不能为空", HTTPStatus.BAD_REQUEST)

        result = UserService.update_user(user_id, data)
        return format_response(result)

    except Exception as e:
        return handle_service_exception(e)
    
@users_bp.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """
    DELETE /api/v1/users/{id}
    删除用户
    """
    try:
        result = UserService.delete_user(user_id)
        return format_response(result)

    except Exception as e:
        return handle_service_exception(e)

# ============================================
# 用户查询和统计端点
# ============================================

@users_bp.route('/status/<status>', methods=['GET'])
def get_users_by_status(status):
    """
    GET /api/v1/users/status/{status}
    根据状态查找用户
    """
    try:
        result = UserService.find_users_by_status(status)
        return format_response(result)
    except Exception as e:
        return handle_service_exception(e)

@users_bp.route('/statistics', methods=['GET'])
def get_user_statistics():
    """
    GET /api/v1/users/statistics
    获取用户统计信息
    """
    try:
        result = UserService.get_user_statistics()
        return format_response(result)
    except Exception as e:
        return handle_service_exception(e)

@users_bp.route('/info', methods=['GET'])
def users_info():
    """
    GET /api/v1/users/info
    获取用户管理模块信息
    
    第5步改进：显示Service层信息
    """
    
    try:
        # 🏢 调用Service层获取服务信息
        service_info = UserService.get_service_info()
        
        # API层添加自己的信息
        api_info = {
            'module': 'Users Management API',
            'blueprint_name': users_bp.name,
            'url_prefix': users_bp.url_prefix,
            'api_endpoints': [
                'GET /api/v1/users - 获取用户列表',
                'GET /api/v1/users/{id} - 获取特定用户',
                'POST /api/v1/users - 创建新用户（包含唯一性验证）',
                'PUT /api/v1/users/{id} - 更新用户信息（包含唯一性验证）',
                'DELETE /api/v1/users/{id} - 删除用户',
                'GET /api/v1/users/status/{status} - 根据状态查找用户',
                'GET /api/v1/users/statistics - 获取用户统计信息',
                'GET /api/v1/users/info - 模块信息'
            ],
            'service_layer': service_info  # Service层信息
        }
        
        return format_success_response("模块信息获取成功", api_info)

    except Exception as e:
        return handle_service_exception(e, "获取模块信息失败")

