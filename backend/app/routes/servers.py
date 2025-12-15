"""服务器路由"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app.models import Server, AuditLog
from app.extensions import db
from app.utils import (
    api_response, error_response, get_current_user,
    admin_required, paginate_query, get_request_json, validate_or_error
)
from app.schemas import server_create_schema, server_update_schema

servers_bp = Blueprint('servers', __name__)


@servers_bp.route('', methods=['GET'])
@jwt_required()
def list_servers():
    """获取服务器列表"""
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)
    datacenter_id = request.args.get('datacenter_id', type=int)
    environment_id = request.args.get('environment_id', type=int)
    status = request.args.get('status')
    keyword = request.args.get('keyword', '').strip()

    query = Server.query

    if datacenter_id:
        query = query.filter(Server.datacenter_id == datacenter_id)
    if environment_id:
        query = query.filter(Server.environment_id == environment_id)
    if status:
        query = query.filter(Server.status == status)
    if keyword:
        query = query.filter(
            db.or_(
                Server.name.ilike(f'%{keyword}%'),
                Server.internal_ip.ilike(f'%{keyword}%'),
                Server.external_ip.ilike(f'%{keyword}%'),
                Server.responsible_person.ilike(f'%{keyword}%'),
            )
        )

    query = query.order_by(Server.created_at.desc())
    result = paginate_query(query, page, page_size)

    return api_response(
        [s.to_dict() for s in result['items']],
        pagination=result['pagination']
    )


@servers_bp.route('/tree', methods=['GET'])
@jwt_required()
def get_servers_tree():
    """获取服务器树形结构（含容器和GPU）"""
    datacenter_id = request.args.get('datacenter_id', type=int)
    environment_id = request.args.get('environment_id', type=int)
    expand_level = request.args.get('expand_level', 1, type=int)  # 1=服务器, 2=容器, 3=服务

    query = Server.query

    if datacenter_id:
        query = query.filter(Server.datacenter_id == datacenter_id)
    if environment_id:
        query = query.filter(Server.environment_id == environment_id)

    servers = query.order_by(Server.name).all()

    tree_data = []
    for server in servers:
        server_data = server.to_dict()

        if expand_level >= 2:
            # 为树形展示准备 children 数组
            children = []

            # 添加容器到 children
            for container in server.containers:
                container_data = container.to_dict()
                container_data['_type'] = 'container'  # 标记类型

                if expand_level >= 3:
                    # 将服务作为容器的子节点
                    container_data['children'] = []
                    for service in container.services:
                        service_data = service.to_dict()
                        service_data['_type'] = 'service'  # 标记类型
                        container_data['children'].append(service_data)

                children.append(container_data)

            # 添加 GPU 到 children（与容器平级）
            for gpu in server.gpus:
                gpu_data = gpu.to_dict()
                gpu_data['_type'] = 'gpu'  # 标记类型
                children.append(gpu_data)

            server_data['children'] = children
            server_data['hasChildren'] = len(children) > 0

        tree_data.append(server_data)

    return api_response(tree_data)


@servers_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_server(id):
    """获取服务器详情"""
    server = Server.query.get_or_404(id)
    return api_response(server.to_dict(include_children=True))


@servers_bp.route('', methods=['POST'])
@jwt_required()
@admin_required
def create_server():
    """创建服务器"""
    user = get_current_user()

    # 验证输入数据
    data, error = validate_or_error(server_create_schema)
    if error:
        return error

    server = Server(
        name=data['name'],
        datacenter_id=data['datacenter_id'],
        environment_id=data['environment_id'],
        internal_ip=data['internal_ip'],
        external_ip=data.get('external_ip'),
        cpu_cores=data.get('cpu_cores'),
        memory_gb=data.get('memory_gb'),
        disk_gb=data.get('disk_gb'),
        os_type=data.get('os_type'),
        status=data.get('status', 'online'),
        responsible_person=data.get('responsible_person'),
        description=data.get('description'),
        ssh_port=data.get('ssh_port', 22),
        ssh_user=data.get('ssh_user', 'root'),
    )

    db.session.add(server)
    db.session.commit()

    AuditLog.log_action(
        user=user, action='create', resource_type='server',
        resource_id=server.id, resource_name=server.name,
        ip_address=request.remote_addr
    )
    db.session.commit()

    return api_response(server.to_dict(), '服务器创建成功'), 201


@servers_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_server(id):
    """更新服务器"""
    user = get_current_user()
    server = Server.query.get_or_404(id)

    # 验证输入数据
    data, error = validate_or_error(server_update_schema)
    if error:
        return error

    old_data = server.to_dict()
    changes = {}

    updatable_fields = [
        'name', 'datacenter_id', 'environment_id', 'internal_ip', 'external_ip',
        'cpu_cores', 'memory_gb', 'disk_gb', 'os_type', 'cpu_usage', 'memory_usage',
        'disk_usage', 'status', 'responsible_person', 'description', 'ssh_port', 'ssh_user'
    ]

    for field in updatable_fields:
        if field in data:
            old_val = getattr(server, field)
            new_val = data[field]
            if old_val != new_val:
                changes[field] = {'old': old_val, 'new': new_val}
                setattr(server, field, new_val)

    db.session.commit()

    if changes:
        AuditLog.log_action(
            user=user, action='update', resource_type='server',
            resource_id=server.id, resource_name=server.name,
            changes=changes, ip_address=request.remote_addr
        )
        db.session.commit()

    return api_response(server.to_dict(), '服务器更新成功')


@servers_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_server(id):
    """删除服务器"""
    user = get_current_user()
    server = Server.query.get_or_404(id)
    snapshot = server.to_dict(include_children=True)

    AuditLog.log_action(
        user=user, action='delete', resource_type='server',
        resource_id=server.id, resource_name=server.name,
        snapshot=snapshot, ip_address=request.remote_addr
    )

    db.session.delete(server)
    db.session.commit()

    return api_response(None, '服务器删除成功')
