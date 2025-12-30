"""容器路由"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app.models import Container, PortMapping, AuditLog
from app.extensions import db
from app.utils import (
    api_response, error_response, get_current_user,
    paginate_query, get_request_json, validate_or_error
)
from app.schemas import container_create_schema, container_update_schema

containers_bp = Blueprint('containers', __name__)


@containers_bp.route('', methods=['GET'])
@jwt_required()
def list_containers():
    """获取容器列表"""
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)
    server_id = request.args.get('server_id', type=int)
    owner_id = request.args.get('owner_id', type=int)
    status = request.args.get('status')
    keyword = request.args.get('keyword', '').strip()

    query = Container.query

    if server_id:
        query = query.filter(Container.server_id == server_id)
    if owner_id:
        query = query.filter(Container.owner_id == owner_id)
    if status:
        query = query.filter(Container.status == status)
    if keyword:
        query = query.filter(Container.name.ilike(f'%{keyword}%'))

    query = query.order_by(Container.created_at.desc())
    result = paginate_query(query, page, page_size)

    return api_response(
        [c.to_dict() for c in result['items']],
        pagination=result['pagination']
    )


@containers_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_container(id):
    """获取容器详情"""
    container = Container.query.get_or_404(id)
    return api_response(container.to_dict(include_children=True))


@containers_bp.route('', methods=['POST'])
@jwt_required()
def create_container():
    """创建容器"""
    user = get_current_user()

    # 验证输入数据
    data, error = validate_or_error(container_create_schema)
    if error:
        return error

    container = Container(
        name=data['name'],
        server_id=data['server_id'],
        owner_id=user.id,
        image=data.get('image'),
        container_id=data.get('container_id'),
        cpu_limit=data.get('cpu_limit'),
        memory_limit_mb=data.get('memory_limit_mb'),
        status=data.get('status', 'running'),
        description=data.get('description'),
    )

    db.session.add(container)
    db.session.flush()  # 获取container.id

    # 处理端口映射
    port_mappings = data.get('port_mappings', [])
    for pm_data in port_mappings:
        if pm_data.get('container_port') and pm_data.get('internal_port'):
            pm = PortMapping(
                container_id=container.id,
                container_port=pm_data['container_port'],
                internal_ip=pm_data.get('internal_ip'),
                internal_port=pm_data['internal_port'],
                external_ip=pm_data.get('external_ip'),
                external_port=pm_data.get('external_port'),
                protocol=pm_data.get('protocol', 'tcp'),
                description=pm_data.get('description'),
            )
            db.session.add(pm)

    db.session.commit()

    AuditLog.log_action(
        user=user, action='create', resource_type='container',
        resource_id=container.id, resource_name=container.name,
        ip_address=request.remote_addr
    )
    db.session.commit()

    return api_response(container.to_dict(), '容器创建成功'), 201


@containers_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_container(id):
    """更新容器"""
    user = get_current_user()
    container = Container.query.get_or_404(id)

    # 权限检查：管理员或所有者
    if not user.is_admin and container.owner_id != user.id:
        return error_response('无权限修改此容器', 403, 403)

    data = get_request_json()
    old_data = container.to_dict()
    changes = {}

    updatable_fields = [
        'name', 'image', 'container_id', 'cpu_limit', 'memory_limit_mb',
        'cpu_usage', 'memory_usage', 'status', 'description'
    ]

    for field in updatable_fields:
        if field in data:
            old_val = getattr(container, field)
            new_val = data[field]
            if old_val != new_val:
                changes[field] = {'old': old_val, 'new': new_val}
                setattr(container, field, new_val)

    # 更新端口映射
    if 'port_mappings' in data:
        # 删除旧的端口映射
        PortMapping.query.filter_by(container_id=container.id).delete()

        # 添加新的端口映射
        for pm_data in data['port_mappings']:
            if pm_data.get('container_port') and pm_data.get('internal_port'):
                pm = PortMapping(
                    container_id=container.id,
                    container_port=pm_data['container_port'],
                    internal_ip=pm_data.get('internal_ip'),
                    internal_port=pm_data['internal_port'],
                    external_ip=pm_data.get('external_ip'),
                    external_port=pm_data.get('external_port'),
                    protocol=pm_data.get('protocol', 'tcp'),
                    description=pm_data.get('description'),
                )
                db.session.add(pm)

        changes['port_mappings'] = {'old': 'updated', 'new': 'updated'}

    db.session.commit()

    if changes:
        AuditLog.log_action(
            user=user, action='update', resource_type='container',
            resource_id=container.id, resource_name=container.name,
            changes=changes, ip_address=request.remote_addr
        )
        db.session.commit()

    return api_response(container.to_dict(), '容器更新成功')


@containers_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_container(id):
    """删除容器"""
    user = get_current_user()
    container = Container.query.get_or_404(id)

    # 权限检查：管理员或所有者
    if not user.is_admin and container.owner_id != user.id:
        return error_response('无权限删除此容器', 403, 403)

    snapshot = container.to_dict(include_children=True)

    AuditLog.log_action(
        user=user, action='delete', resource_type='container',
        resource_id=container.id, resource_name=container.name,
        snapshot=snapshot, ip_address=request.remote_addr
    )

    db.session.delete(container)
    db.session.commit()

    return api_response(None, '容器删除成功')


@containers_bp.route('/update-sort-order', methods=['POST'])
@jwt_required()
def update_sort_order():
    """批量更新容器排序"""
    user = get_current_user()

    # 只有管理员可以更新排序
    if not user.is_admin:
        return error_response('无权限更新排序', 403, 403)

    data = get_request_json()
    if not data or 'items' not in data:
        return error_response('缺少items参数', 400, 400)

    items = data['items']  # [{id: 1, sort_order: 0}, {id: 2, sort_order: 1}, ...]

    for item in items:
        container_id = item.get('id')
        sort_order = item.get('sort_order')
        if container_id is not None and sort_order is not None:
            container = Container.query.get(container_id)
            if container:
                container.sort_order = sort_order

    db.session.commit()
    return api_response(None, '排序更新成功')
