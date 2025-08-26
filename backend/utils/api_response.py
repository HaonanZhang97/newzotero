"""
API Response Utilities
提供统一的 API 响应格式化工具

这个模块包含了所有 API 层需要的响应格式化功能，
确保整个应用的 HTTP 响应格式保持一致。
"""

from flask import jsonify
from typing import Tuple, Any, Dict, Optional, Union
import logging

# 配置日志
logger = logging.getLogger(__name__)

def format_response(
    service_result: Dict[str, Any], 
    success_status: int = 200, 
    error_status: int = 400
) -> Tuple[Any, int]:
    """
    统一格式化 Service 层返回结果为 HTTP 响应
    
    Args:
        service_result: Service层返回的结果字典
        success_status: 成功时的HTTP状态码，默认200
        error_status: 失败时的HTTP状态码，默认400
    
    Returns:
        Tuple[Flask.Response, int]: (响应对象, 状态码)
    
    Service层结果格式：
    {
        "success": True/False,
        "message": "操作说明",
        "data": {...} 或 "user": {...} 或 "users": [...]
    }
    
    成功响应格式：
    {
        "message": "操作成功",
        "data": {...}
    }
    
    错误响应格式：
    {
        "error": {
            "message": "错误信息"
        }
    }
    """
    if service_result.get("success"):
        response_data = {
            "message": service_result.get("message", "操作成功")
        }
        
        # 灵活处理不同的数据字段名
        data_fields = ["data", "user", "users", "project", "projects"]
        for field in data_fields:
            if field in service_result:
                response_data["data"] = service_result[field]
                break
                
        logger.debug(f"✅ API成功响应: {response_data.get('message')}")
        return jsonify(response_data), success_status
    else:
        error_response = {
            "error": {
                "message": service_result.get("message", "操作失败")
            }
        }
        
        logger.warning(f"⚠️ API错误响应: {error_response['error']['message']}")
        return jsonify(error_response), error_status

def format_success_response(
    message: str = "操作成功",
    data: Optional[Union[Dict[str, Any], list]] = None,
    status_code: int = 200
) -> Tuple[Any, int]:
    """
    快速创建成功响应
    
    Args:
        message: 成功消息
        data: 响应数据
        status_code: HTTP状态码
    
    Returns:
        Tuple[Flask.Response, int]: (响应对象, 状态码)
    """
    response_data: Dict[str, Any] = {"message": message}
    if data is not None:
        response_data["data"] = data
        
    logger.debug(f"✅ API快速成功响应: {message}")
    return jsonify(response_data), status_code

def format_error_response(
    message: str = "操作失败",
    status_code: int = 400,
    error_code: Optional[str] = None
) -> Tuple[Any, int]:
    """
    快速创建错误响应
    
    Args:
        message: 错误消息
        status_code: HTTP状态码
        error_code: 错误代码（可选）
    
    Returns:
        Tuple[Flask.Response, int]: (响应对象, 状态码)
    """
    error_response = {
        "error": {
            "message": message
        }
    }
    
    if error_code:
        error_response["error"]["code"] = error_code
        
    logger.warning(f"⚠️ API快速错误响应: {message} (状态码: {status_code})")
    return jsonify(error_response), status_code

def handle_service_exception(
    exception: Exception,
    default_message: str = "系统错误，请稍后重试",
    default_status: int = 500
) -> Tuple[Any, int]:
    """
    统一处理 Service 层抛出的异常
    
    Args:
        exception: 捕获的异常
        default_message: 默认错误消息
        default_status: 默认HTTP状态码
    
    Returns:
        Tuple[Flask.Response, int]: (响应对象, 状态码)
    """
    if isinstance(exception, ValueError):
        # 业务逻辑错误，通常是 400 Bad Request
        logger.warning(f"⚠️ 业务逻辑错误: {str(exception)}")
        return format_error_response(str(exception), 400)
    elif isinstance(exception, PermissionError):
        # 权限错误，403 Forbidden
        logger.warning(f"🚫 权限错误: {str(exception)}")
        return format_error_response(str(exception), 403)
    elif isinstance(exception, FileNotFoundError):
        # 资源不存在，404 Not Found
        logger.warning(f"🔍 资源不存在: {str(exception)}")
        return format_error_response("请求的资源不存在", 404)
    else:
        # 系统错误，500 Internal Server Error
        logger.error(f"❌ 系统错误: {str(exception)}")
        return format_error_response(default_message, default_status)

# ============================================
# 常用的 HTTP 状态码常量
# ============================================

class HTTPStatus:
    """HTTP状态码常量"""
    # 成功响应
    OK = 200
    CREATED = 201
    ACCEPTED = 202
    NO_CONTENT = 204
    
    # 客户端错误
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    CONFLICT = 409
    UNPROCESSABLE_ENTITY = 422
    
    # 服务器错误
    INTERNAL_SERVER_ERROR = 500
    NOT_IMPLEMENTED = 501
    SERVICE_UNAVAILABLE = 503

# ============================================
# 使用示例和文档
# ============================================

"""
使用示例：

1. 基本用法 - 格式化 Service 层结果：
```python
from ..utils.api_response import format_response

@users_bp.route('', methods=['GET'])
def get_users():
    try:
        result = UserService.get_all_users()
        return format_response(result)
    except Exception as e:
        return handle_service_exception(e)
```

2. 快速成功响应：
```python
from ..utils.api_response import format_success_response

@users_bp.route('/health', methods=['GET'])
def health_check():
    return format_success_response("服务正常运行", {"status": "healthy"})
```

3. 快速错误响应：
```python
from ..utils.api_response import format_error_response, HTTPStatus

@users_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    if user_id <= 0:
        return format_error_response("无效的用户ID", HTTPStatus.BAD_REQUEST)
```

4. 异常处理：
```python
from ..utils.api_response import handle_service_exception

@users_bp.route('', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        result = UserService.create_user(data)
        return format_response(result, success_status=201)
    except Exception as e:
        return handle_service_exception(e)
```
"""
