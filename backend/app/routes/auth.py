"""认证路由"""
from flask import Blueprint, request
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required,
    get_jwt_identity, get_jwt
)
from app.models import User
from app.extensions import db
from app.utils import api_response, error_response, get_current_user, validate_or_error
from app.schemas import login_schema

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    # 验证输入数据
    data, error = validate_or_error(login_schema)
    if error:
        return error

    username = data['username'].strip()
    password = data['password']

    user = User.query.filter_by(username=username).first()
    if user is None or not user.check_password(password):
        return error_response('用户名或密码错误', 401, 401)

    if not user.is_active:
        return error_response('账号已被禁用', 403, 403)

    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return api_response({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user.to_dict(include_email=True)
    }, '登录成功')


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """用户登出"""
    # JWT是无状态的，客户端删除token即可
    return api_response(None, '登出成功')


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_me():
    """获取当前用户信息"""
    user = get_current_user()
    if not user:
        return error_response('用户不存在', 404, 404)
    return api_response(user.to_dict(include_email=True))


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """刷新访问Token"""
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user or not user.is_active:
        return error_response('用户不存在或已被禁用', 401, 401)

    access_token = create_access_token(identity=str(user_id))
    return api_response({'access_token': access_token}, 'Token刷新成功')


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """修改密码"""
    user = get_current_user()
    data = request.get_json() or {}
    old_password = data.get('old_password', '')
    new_password = data.get('new_password', '')

    if not old_password or not new_password:
        return error_response('旧密码和新密码不能为空', 422, 422)

    if len(new_password) < 6:
        return error_response('新密码长度不能少于6位', 422, 422)

    if not user.check_password(old_password):
        return error_response('旧密码错误', 400, 400)

    user.set_password(new_password)
    db.session.commit()

    return api_response(None, '密码修改成功')
