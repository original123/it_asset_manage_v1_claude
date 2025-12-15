"""通用工具函数"""
from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from app.models import User, AuditLog
from app.extensions import db


def api_response(data=None, message='success', code=0, pagination=None):
    """统一API响应格式"""
    response = {
        'code': code,
        'message': message,
        'data': data,
    }
    if pagination:
        response['pagination'] = pagination
    return jsonify(response)


def error_response(message, code=400, http_code=None):
    """错误响应"""
    if http_code is None:
        http_code = code if code in [400, 401, 403, 404, 422, 500] else 400
    return jsonify({'code': code, 'message': message, 'data': None}), http_code


def get_current_user():
    """获取当前登录用户"""
    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        return User.query.get(int(user_id))
    except Exception:
        return None


def admin_required(fn):
    """管理员权限装饰器"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = get_current_user()
        if not user or not user.is_admin:
            return error_response('需要管理员权限', 403, 403)
        return fn(*args, **kwargs)
    return wrapper


def owner_or_admin_required(resource_getter):
    """资源所有者或管理员权限装饰器"""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user = get_current_user()
            if not user:
                return error_response('未授权访问', 401, 401)

            if user.is_admin:
                return fn(*args, **kwargs)

            resource = resource_getter(*args, **kwargs)
            if resource and hasattr(resource, 'owner_id') and resource.owner_id == user.id:
                return fn(*args, **kwargs)

            return error_response('无权限执行此操作', 403, 403)
        return wrapper
    return decorator


def log_action(action, resource_type):
    """审计日志装饰器"""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user = get_current_user()
            result = fn(*args, **kwargs)

            # 只记录成功的操作
            if isinstance(result, tuple):
                response, status_code = result
            else:
                response = result
                status_code = 200

            if status_code in [200, 201]:
                try:
                    data = response.get_json() if hasattr(response, 'get_json') else {}
                    resource_data = data.get('data', {})
                    resource_id = resource_data.get('id') if isinstance(resource_data, dict) else kwargs.get('id', 0)
                    resource_name = resource_data.get('name') if isinstance(resource_data, dict) else None

                    AuditLog.log_action(
                        user=user,
                        action=action,
                        resource_type=resource_type,
                        resource_id=resource_id,
                        resource_name=resource_name,
                        ip_address=request.remote_addr,
                        user_agent=request.user_agent.string[:256] if request.user_agent else None,
                    )
                    db.session.commit()
                except Exception as e:
                    print(f"Audit log error: {e}")

            return result
        return wrapper
    return decorator


def paginate_query(query, page=1, page_size=20, max_page_size=100):
    """分页查询"""
    page = max(1, page)
    page_size = min(max(1, page_size), max_page_size)

    pagination = query.paginate(page=page, per_page=page_size, error_out=False)

    return {
        'items': pagination.items,
        'pagination': {
            'page': pagination.page,
            'page_size': pagination.per_page,
            'total': pagination.total,
            'pages': pagination.pages,
        }
    }


def get_request_json():
    """获取请求JSON数据"""
    return request.get_json() or {}


def validate_json(schema, data=None):
    """
    使用Marshmallow Schema验证JSON数据

    Args:
        schema: Marshmallow Schema实例
        data: 要验证的数据，如果为None则从request.get_json()获取

    Returns:
        tuple: (validated_data, errors)
            - 如果验证成功: (validated_data, None)
            - 如果验证失败: (None, errors_dict)
    """
    from marshmallow import ValidationError

    if data is None:
        data = request.get_json() or {}

    try:
        validated_data = schema.load(data)
        return validated_data, None
    except ValidationError as e:
        return None, e.messages


def validate_or_error(schema, data=None):
    """
    验证JSON数据，失败时返回错误响应

    Args:
        schema: Marshmallow Schema实例
        data: 要验证的数据

    Returns:
        tuple: (validated_data, error_response_or_none)
            - 如果验证成功: (validated_data, None)
            - 如果验证失败: (None, error_response) - 可直接返回给客户端
    """
    validated_data, errors = validate_json(schema, data)
    if errors:
        return None, error_response(f'参数验证失败: {errors}', 400, 400)
    return validated_data, None

