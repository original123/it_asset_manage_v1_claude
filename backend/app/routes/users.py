"""用户管理路由"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app.models import User, AuditLog
from app.extensions import db
from app.utils import (
    api_response, error_response, get_current_user,
    admin_required, paginate_query, get_request_json
)

users_bp = Blueprint('users', __name__)


@users_bp.route('', methods=['GET'])
@jwt_required()
@admin_required
def list_users():
    """获取用户列表"""
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)
    role = request.args.get('role')
    is_active = request.args.get('is_active')
    keyword = request.args.get('keyword', '').strip()

    query = User.query

    if role:
        query = query.filter(User.role == role)
    if is_active is not None:
        query = query.filter(User.is_active == (is_active.lower() == 'true'))
    if keyword:
        query = query.filter(
            db.or_(
                User.username.ilike(f'%{keyword}%'),
                User.display_name.ilike(f'%{keyword}%'),
                User.email.ilike(f'%{keyword}%'),
            )
        )

    query = query.order_by(User.created_at.desc())
    result = paginate_query(query, page, page_size)

    return api_response(
        [u.to_dict(include_email=True) for u in result['items']],
        pagination=result['pagination']
    )


@users_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
@admin_required
def get_user(id):
    """获取用户详情"""
    user = User.query.get_or_404(id)
    return api_response(user.to_dict(include_email=True))


@users_bp.route('', methods=['POST'])
@jwt_required()
@admin_required
def create_user():
    """创建用户"""
    current_user = get_current_user()
    data = get_request_json()

    required_fields = ['username', 'password', 'display_name']
    for field in required_fields:
        if not data.get(field):
            return error_response(f'{field} 不能为空', 422, 422)

    if User.query.filter_by(username=data['username']).first():
        return error_response('用户名已存在', 422, 422)

    if data.get('email') and User.query.filter_by(email=data['email']).first():
        return error_response('邮箱已存在', 422, 422)

    user = User(
        username=data['username'],
        display_name=data['display_name'],
        email=data.get('email'),
        role=data.get('role', 'user'),
        is_active=data.get('is_active', True),
    )
    user.set_password(data['password'])

    db.session.add(user)
    db.session.commit()

    AuditLog.log_action(
        user=current_user, action='create', resource_type='user',
        resource_id=user.id, resource_name=user.username,
        ip_address=request.remote_addr
    )
    db.session.commit()

    return api_response(user.to_dict(include_email=True), '用户创建成功'), 201


@users_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_user(id):
    """更新用户"""
    current_user = get_current_user()
    user = User.query.get_or_404(id)
    data = get_request_json()

    changes = {}

    if 'display_name' in data and data['display_name'] != user.display_name:
        changes['display_name'] = {'old': user.display_name, 'new': data['display_name']}
        user.display_name = data['display_name']

    if 'email' in data and data['email'] != user.email:
        if data['email'] and User.query.filter(User.email == data['email'], User.id != id).first():
            return error_response('邮箱已存在', 422, 422)
        changes['email'] = {'old': user.email, 'new': data['email']}
        user.email = data['email']

    if 'role' in data and data['role'] != user.role:
        changes['role'] = {'old': user.role, 'new': data['role']}
        user.role = data['role']

    if 'is_active' in data and data['is_active'] != user.is_active:
        changes['is_active'] = {'old': user.is_active, 'new': data['is_active']}
        user.is_active = data['is_active']

    if 'password' in data and data['password']:
        user.set_password(data['password'])
        changes['password'] = {'old': '***', 'new': '***'}

    db.session.commit()

    if changes:
        AuditLog.log_action(
            user=current_user, action='update', resource_type='user',
            resource_id=user.id, resource_name=user.username,
            changes=changes, ip_address=request.remote_addr
        )
        db.session.commit()

    return api_response(user.to_dict(include_email=True), '用户更新成功')


@users_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_user(id):
    """删除用户"""
    current_user = get_current_user()
    user = User.query.get_or_404(id)

    if user.id == current_user.id:
        return error_response('不能删除自己的账号', 400, 400)

    snapshot = user.to_dict(include_email=True)

    AuditLog.log_action(
        user=current_user, action='delete', resource_type='user',
        resource_id=user.id, resource_name=user.username,
        snapshot=snapshot, ip_address=request.remote_addr
    )

    db.session.delete(user)
    db.session.commit()

    return api_response(None, '用户删除成功')


@users_bp.route('/options', methods=['GET'])
@jwt_required()
def get_user_options():
    """获取用户选项（用于下拉选择）"""
    users = User.query.filter_by(is_active=True).order_by(User.display_name).all()
    return api_response([
        {'id': u.id, 'username': u.username, 'display_name': u.display_name}
        for u in users
    ])
