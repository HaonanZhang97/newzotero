"""
第5步：使用Service层的用户管理 Blueprint  
=========================================

学习目标：
- API层如何调用Service层
- 业务逻辑与HTTP处理的分离
- 错误处理的层次化
- 代码结构的清晰化
"""

from flask import Blueprint, jsonify, request

# 第5步：导入Service层
from ..services import UserService

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
    
    第5步改进：API层只负责HTTP处理，业务逻辑交给Service层
    """
    print("📋 API层: GET /api/v1/users - 接收请求")
    
    try:
        # 🏢 调用Service层处理业务逻辑
        result = UserService.get_all_users()
        
        print("✅ API层: 业务处理成功，返回响应")
        return jsonify(result), 200
        
    except Exception as e:
        print(f"❌ API层: 处理失败 - {e}")
        return jsonify({
            'status': 'error',
            'message': f'获取用户列表失败: {str(e)}'
        }), 500

@users_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """
    GET /api/v1/users/{id}
    获取特定用户信息
    
    第5步改进：参数提取 + Service层调用 + 错误处理
    """
    print(f"📋 API层: GET /api/v1/users/{user_id} - 接收请求")
    
    try:
        # 🏢 调用Service层处理业务逻辑
        result = UserService.get_user_by_id(user_id)
        
        print("✅ API层: 业务处理成功，返回响应")
        return jsonify(result), 200
        
    except ValueError as e:
        # 业务逻辑错误（如用户不存在）
        print(f"⚠️ API层: 业务逻辑错误 - {e}")
        return jsonify({
            'status': 'error', 
            'message': str(e)
        }), 404
        
    except Exception as e:
        # 系统错误
        print(f"❌ API层: 系统错误 - {e}")
        return jsonify({
            'status': 'error',
            'message': '系统错误，请稍后重试'
        }), 500

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
            return jsonify({
                'status': 'error',
                'message': '请求数据不能为空'
            }), 400
        
        print(f"📥 API层: 接收到数据 - username: {data.get('username')}")
        
        # 步骤2：🏢 调用Service层处理所有业务逻辑
        result = UserService.create_user(data)
        
        print("✅ API层: 业务处理成功，返回响应")
        return jsonify(result), 201
        
    except ValueError as e:
        # 业务逻辑错误（数据验证失败等）
        print(f"⚠️ API层: 业务逻辑错误 - {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
        
    except Exception as e:
        # 系统错误
        print(f"❌ API层: 系统错误 - {e}")
        return jsonify({
            'status': 'error', 
            'message': '系统错误，请稍后重试'
        }), 500

@users_bp.route('/info', methods=['GET'])
def users_info():
    """
    GET /api/v1/users/info
    获取用户管理模块信息
    
    第5步改进：显示Service层信息
    """
    print("📋 API层: GET /api/v1/users/info - 获取模块信息")
    
    try:
        # 🏢 调用Service层获取服务信息
        service_info = UserService.get_service_info()
        
        # API层添加自己的信息
        result = {
            'module': 'Users Management API',
            'blueprint_name': users_bp.name,
            'url_prefix': users_bp.url_prefix,
            'api_endpoints': [
                'GET /api/v1/users - 获取用户列表',
                'GET /api/v1/users/{id} - 获取特定用户',
                'POST /api/v1/users - 创建新用户',
                'GET /api/v1/users/info - 模块信息'
            ],
            'service_layer': service_info  # Service层信息
        }
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f"❌ API层: 获取模块信息失败 - {e}")
        return jsonify({
            'status': 'error',
            'message': '获取模块信息失败'
        }), 500

# ============================================
# 第6步将要添加的功能（暂时注释掉）
# ============================================
# TODO: 第6步解锁 - 添加Model层数据验证
# from ..models.user_model import User, UserCreateRequest
# 
# @users_bp.route('', methods=['POST'])
# def create_user():
#     data = request.get_json()
#     user_request = UserCreateRequest(data)  # 使用Model层
#     user_request.validate()  # Model层验证
#     result = UserService.create_user(user_request.to_dict())

# TODO: 第6步解锁 - 添加更完整的CRUD操作
# @users_bp.route('/<int:user_id>', methods=['PUT'])
# def update_user(user_id):
#     """更新用户信息"""
#     pass
# 
# @users_bp.route('/<int:user_id>', methods=['DELETE'])  
# def delete_user(user_id):
#     """删除用户"""
#     pass

print(f"👥 Users Blueprint '{users_bp.name}' loaded with Service layer integration!")
