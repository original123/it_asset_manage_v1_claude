"""用户偏好路由"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app.models import UserPreference
from app.extensions import db
from app.utils import api_response, error_response, get_current_user

preferences_bp = Blueprint('preferences', __name__)


@preferences_bp.route('', methods=['GET'])
@jwt_required()
def get_preferences():
    """获取当前用户偏好"""
    user = get_current_user()
    if not user:
        return error_response('用户不存在', 404, 404)

    # 获取或创建用户偏好
    pref = UserPreference.query.filter_by(user_id=user.id).first()
    if not pref:
        # 返回默认值
        return api_response({
            'grouping_mode': 'environment-first',
            'view_mode': 'grid',
            'panel_width': 260,
            'show_detail_bar': True,
            'updated_at': None,
        })

    return api_response(pref.to_dict())


@preferences_bp.route('', methods=['PUT'])
@jwt_required()
def update_preferences():
    """更新用户偏好"""
    user = get_current_user()
    if not user:
        return error_response('用户不存在', 404, 404)

    data = request.get_json() or {}

    # 获取或创建用户偏好
    pref = UserPreference.query.filter_by(user_id=user.id).first()
    if not pref:
        pref = UserPreference(user_id=user.id)
        db.session.add(pref)

    # 更新字段
    if 'grouping_mode' in data:
        allowed_modes = ['environment-first', 'datacenter-first', 'flat']
        if data['grouping_mode'] in allowed_modes:
            pref.grouping_mode = data['grouping_mode']

    if 'view_mode' in data:
        allowed_views = ['grid', 'list']
        if data['view_mode'] in allowed_views:
            pref.view_mode = data['view_mode']

    if 'panel_width' in data:
        width = int(data['panel_width'])
        if 200 <= width <= 400:
            pref.panel_width = width

    if 'show_detail_bar' in data:
        pref.show_detail_bar = bool(data['show_detail_bar'])

    db.session.commit()

    return api_response(pref.to_dict(), '偏好已保存')
