"""机房路由"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app.models import Datacenter, Server, Container, Service, AuditLog
from app.extensions import db
from app.utils import (
    api_response, error_response, get_current_user,
    admin_required, get_request_json, validate_or_error
)
from app.schemas import datacenter_create_schema, datacenter_update_schema

datacenters_bp = Blueprint('datacenters', __name__)


@datacenters_bp.route('', methods=['GET'])
@jwt_required()
def list_datacenters():
    """获取机房列表"""
    include_stats = request.args.get('include_stats', 'false').lower() == 'true'
    datacenters = Datacenter.query.filter_by(is_active=True).order_by(Datacenter.name).all()
    return api_response([dc.to_dict(include_stats=include_stats) for dc in datacenters])


@datacenters_bp.route('/overview', methods=['GET'])
@jwt_required()
def get_datacenters_overview():
    """获取机房总览统计"""
    datacenters = Datacenter.query.filter_by(is_active=True).all()

    overview = []
    for dc in datacenters:
        servers = Server.query.filter_by(datacenter_id=dc.id).all()
        server_ids = [s.id for s in servers]

        container_count = Container.query.filter(Container.server_id.in_(server_ids)).count() if server_ids else 0
        service_count = db.session.query(Service).join(Container).filter(
            Container.server_id.in_(server_ids)
        ).count() if server_ids else 0

        # 按环境统计
        env_stats = db.session.query(
            Server.environment_id, db.func.count(Server.id)
        ).filter(Server.datacenter_id == dc.id).group_by(Server.environment_id).all()

        # 按状态统计
        status_stats = db.session.query(
            Server.status, db.func.count(Server.id)
        ).filter(Server.datacenter_id == dc.id).group_by(Server.status).all()

        # GPU服务器数量
        gpu_server_count = db.session.query(db.func.count(db.distinct(Server.id))).join(
            GPU, GPU.server_id == Server.id
        ).filter(Server.datacenter_id == dc.id).scalar() or 0

        overview.append({
            'id': dc.id,
            'name': dc.name,
            'location': dc.location,
            'server_count': len(servers),
            'container_count': container_count,
            'service_count': service_count,
            'gpu_server_count': gpu_server_count,
            'env_stats': {str(env_id): count for env_id, count in env_stats},
            'status_stats': {status: count for status, count in status_stats},
        })

    return api_response(overview)


@datacenters_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_datacenter(id):
    """获取机房详情"""
    datacenter = Datacenter.query.get_or_404(id)
    return api_response(datacenter.to_dict(include_stats=True))


@datacenters_bp.route('', methods=['POST'])
@jwt_required()
@admin_required
def create_datacenter():
    """创建机房"""
    user = get_current_user()

    # 验证输入数据
    data, error = validate_or_error(datacenter_create_schema)
    if error:
        return error

    if Datacenter.query.filter_by(name=data['name']).first():
        return error_response('机房名称已存在', 422, 422)

    datacenter = Datacenter(
        name=data['name'],
        location=data.get('location'),
        description=data.get('description'),
    )

    db.session.add(datacenter)
    db.session.commit()

    AuditLog.log_action(
        user=user, action='create', resource_type='datacenter',
        resource_id=datacenter.id, resource_name=datacenter.name,
        ip_address=request.remote_addr
    )
    db.session.commit()

    return api_response(datacenter.to_dict(), '机房创建成功'), 201


@datacenters_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_datacenter(id):
    """更新机房"""
    user = get_current_user()
    datacenter = Datacenter.query.get_or_404(id)
    data = get_request_json()

    changes = {}
    if 'name' in data and data['name'] != datacenter.name:
        if Datacenter.query.filter(Datacenter.name == data['name'], Datacenter.id != id).first():
            return error_response('机房名称已存在', 422, 422)
        changes['name'] = {'old': datacenter.name, 'new': data['name']}
        datacenter.name = data['name']

    if 'location' in data and data['location'] != datacenter.location:
        changes['location'] = {'old': datacenter.location, 'new': data['location']}
        datacenter.location = data['location']

    if 'description' in data and data['description'] != datacenter.description:
        changes['description'] = {'old': datacenter.description, 'new': data['description']}
        datacenter.description = data['description']

    db.session.commit()

    if changes:
        AuditLog.log_action(
            user=user, action='update', resource_type='datacenter',
            resource_id=datacenter.id, resource_name=datacenter.name,
            changes=changes, ip_address=request.remote_addr
        )
        db.session.commit()

    return api_response(datacenter.to_dict(), '机房更新成功')


@datacenters_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_datacenter(id):
    """删除机房"""
    user = get_current_user()
    datacenter = Datacenter.query.get_or_404(id)

    if datacenter.servers.count() > 0:
        return error_response('机房下存在服务器，无法删除', 400, 400)

    snapshot = datacenter.to_dict()

    AuditLog.log_action(
        user=user, action='delete', resource_type='datacenter',
        resource_id=datacenter.id, resource_name=datacenter.name,
        snapshot=snapshot, ip_address=request.remote_addr
    )

    db.session.delete(datacenter)
    db.session.commit()

    return api_response(None, '机房删除成功')


# 需要导入GPU模型
from app.models import GPU
