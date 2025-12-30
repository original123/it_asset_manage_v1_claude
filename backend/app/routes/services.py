"""服务路由"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app.models import Service, AuditLog
from app.extensions import db
from app.utils import (
    api_response, error_response, get_current_user,
    paginate_query, get_request_json, validate_or_error
)
from app.schemas import service_create_schema, service_update_schema

services_bp = Blueprint('services', __name__)


@services_bp.route('', methods=['GET'])
@jwt_required()
def list_services():
    """获取服务列表"""
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)
    container_id = request.args.get('container_id', type=int)
    owner_id = request.args.get('owner_id', type=int)
    status = request.args.get('status')

    query = Service.query

    if container_id:
        query = query.filter(Service.container_id == container_id)
    if owner_id:
        query = query.filter(Service.owner_id == owner_id)
    if status:
        query = query.filter(Service.status == status)

    query = query.order_by(Service.created_at.desc())
    result = paginate_query(query, page, page_size)

    return api_response(
        [s.to_dict() for s in result['items']],
        pagination=result['pagination']
    )


@services_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_service(id):
    """获取服务详情"""
    service = Service.query.get_or_404(id)
    return api_response(service.to_dict())


@services_bp.route('', methods=['POST'])
@jwt_required()
def create_service():
    """创建服务"""
    user = get_current_user()

    # 验证输入数据
    data, error = validate_or_error(service_create_schema)
    if error:
        return error

    service = Service(
        name=data['name'],
        container_id=data['container_id'],
        owner_id=user.id,
        service_type=data.get('service_type'),
        port=data.get('port'),
        version=data.get('version'),
        status=data.get('status', 'healthy'),
        health_check_url=data.get('health_check_url'),
        description=data.get('description'),
    )

    db.session.add(service)
    db.session.commit()

    AuditLog.log_action(
        user=user, action='create', resource_type='service',
        resource_id=service.id, resource_name=service.name,
        ip_address=request.remote_addr
    )
    db.session.commit()

    return api_response(service.to_dict(), '服务创建成功'), 201


@services_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_service(id):
    """更新服务"""
    user = get_current_user()
    service = Service.query.get_or_404(id)

    if not user.is_admin and service.owner_id != user.id:
        return error_response('无权限修改此服务', 403, 403)

    data = get_request_json()
    changes = {}

    updatable_fields = [
        'name', 'service_type', 'port', 'version', 'status',
        'health_check_url', 'description'
    ]

    for field in updatable_fields:
        if field in data:
            old_val = getattr(service, field)
            new_val = data[field]
            if old_val != new_val:
                changes[field] = {'old': old_val, 'new': new_val}
                setattr(service, field, new_val)

    db.session.commit()

    if changes:
        AuditLog.log_action(
            user=user, action='update', resource_type='service',
            resource_id=service.id, resource_name=service.name,
            changes=changes, ip_address=request.remote_addr
        )
        db.session.commit()

    return api_response(service.to_dict(), '服务更新成功')


@services_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_service(id):
    """删除服务"""
    user = get_current_user()
    service = Service.query.get_or_404(id)

    if not user.is_admin and service.owner_id != user.id:
        return error_response('无权限删除此服务', 403, 403)

    snapshot = service.to_dict()

    AuditLog.log_action(
        user=user, action='delete', resource_type='service',
        resource_id=service.id, resource_name=service.name,
        snapshot=snapshot, ip_address=request.remote_addr
    )

    db.session.delete(service)
    db.session.commit()

    return api_response(None, '服务删除成功')


@services_bp.route('/update-sort-order', methods=['POST'])
@jwt_required()
def update_service_sort_order():
    """批量更新服务排序"""
    user = get_current_user()

    # 只有管理员可以更新排序
    if not user.is_admin:
        return error_response('无权限更新排序', 403, 403)

    data = get_request_json()
    if not data or 'items' not in data:
        return error_response('缺少items参数', 400, 400)

    items = data['items']  # [{id: 1, sort_order: 0}, {id: 2, sort_order: 1}, ...]

    for item in items:
        service_id = item.get('id')
        sort_order = item.get('sort_order')
        if service_id is not None and sort_order is not None:
            service = Service.query.get(service_id)
            if service:
                service.sort_order = sort_order

    db.session.commit()
    return api_response(None, '排序更新成功')
