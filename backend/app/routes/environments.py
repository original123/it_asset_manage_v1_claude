"""环境路由"""
from flask import Blueprint
from flask_jwt_extended import jwt_required
from app.models import Environment
from app.utils import api_response

environments_bp = Blueprint('environments', __name__)


@environments_bp.route('', methods=['GET'])
@jwt_required()
def list_environments():
    """获取环境列表"""
    environments = Environment.query.order_by(Environment.sort_order).all()
    return api_response([env.to_dict(include_stats=True) for env in environments])


@environments_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_environment(id):
    """获取环境详情"""
    environment = Environment.query.get_or_404(id)
    return api_response(environment.to_dict(include_stats=True))
