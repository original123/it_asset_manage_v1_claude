"""GPU路由"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app.models import GPU, User, AuditLog
from app.extensions import db
from app.utils import (
    api_response, error_response, get_current_user,
    admin_required, paginate_query, get_request_json
)

gpus_bp = Blueprint('gpus', __name__)


@gpus_bp.route('', methods=['GET'])
@jwt_required()
def list_gpus():
    """获取GPU列表"""
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)
    server_id = request.args.get('server_id', type=int)
    status = request.args.get('status')
    assigned_to = request.args.get('assigned_to', type=int)

    query = GPU.query

    if server_id:
        query = query.filter(GPU.server_id == server_id)
    if status:
        query = query.filter(GPU.status == status)
    if assigned_to:
        query = query.filter(GPU.assigned_to == assigned_to)

    query = query.order_by(GPU.server_id, GPU.index)
    result = paginate_query(query, page, page_size)

    return api_response(
        [g.to_dict() for g in result['items']],
        pagination=result['pagination']
    )


@gpus_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_gpu(id):
    """获取GPU详情"""
    gpu = GPU.query.get_or_404(id)
    return api_response(gpu.to_dict())


@gpus_bp.route('', methods=['POST'])
@jwt_required()
@admin_required
def create_gpu():
    """创建GPU"""
    user = get_current_user()
    data = get_request_json()

    required_fields = ['server_id', 'model', 'memory_gb']
    for field in required_fields:
        if not data.get(field):
            return error_response(f'{field} 不能为空', 422, 422)

    gpu = GPU(
        server_id=data['server_id'],
        model=data['model'],
        memory_gb=data['memory_gb'],
        index=data.get('index', 0),
        status=data.get('status', 'free'),
        description=data.get('description'),
    )

    db.session.add(gpu)
    db.session.commit()

    AuditLog.log_action(
        user=user, action='create', resource_type='gpu',
        resource_id=gpu.id, resource_name=f"{gpu.model} on {gpu.server.name}",
        ip_address=request.remote_addr
    )
    db.session.commit()

    return api_response(gpu.to_dict(), 'GPU创建成功'), 201


@gpus_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_gpu(id):
    """更新GPU"""
    user = get_current_user()
    gpu = GPU.query.get_or_404(id)
    data = get_request_json()

    changes = {}
    updatable_fields = [
        'model', 'memory_gb', 'index', 'gpu_usage', 'memory_usage',
        'status', 'description'
    ]

    for field in updatable_fields:
        if field in data:
            old_val = getattr(gpu, field)
            new_val = data[field]
            if old_val != new_val:
                changes[field] = {'old': old_val, 'new': new_val}
                setattr(gpu, field, new_val)

    db.session.commit()

    if changes:
        AuditLog.log_action(
            user=user, action='update', resource_type='gpu',
            resource_id=gpu.id, resource_name=f"{gpu.model}",
            changes=changes, ip_address=request.remote_addr
        )
        db.session.commit()

    return api_response(gpu.to_dict(), 'GPU更新成功')


@gpus_bp.route('/<int:id>/assign', methods=['POST'])
@jwt_required()
@admin_required
def assign_gpu(id):
    """分配GPU给用户"""
    user = get_current_user()
    gpu = GPU.query.get_or_404(id)
    data = get_request_json()

    user_id = data.get('user_id')
    if not user_id:
        return error_response('user_id 不能为空', 422, 422)

    target_user = User.query.get(user_id)
    if not target_user:
        return error_response('用户不存在', 404, 404)

    old_assigned = gpu.assigned_to
    gpu.assigned_to = user_id
    gpu.status = 'in_use'

    db.session.commit()

    AuditLog.log_action(
        user=user, action='update', resource_type='gpu',
        resource_id=gpu.id, resource_name=f"{gpu.model}",
        changes={'assigned_to': {'old': old_assigned, 'new': user_id}},
        ip_address=request.remote_addr
    )
    db.session.commit()

    return api_response(gpu.to_dict(), f'GPU已分配给 {target_user.display_name}')


@gpus_bp.route('/<int:id>/release', methods=['POST'])
@jwt_required()
@admin_required
def release_gpu(id):
    """释放GPU"""
    user = get_current_user()
    gpu = GPU.query.get_or_404(id)

    old_assigned = gpu.assigned_to
    gpu.assigned_to = None
    gpu.status = 'free'

    db.session.commit()

    AuditLog.log_action(
        user=user, action='update', resource_type='gpu',
        resource_id=gpu.id, resource_name=f"{gpu.model}",
        changes={'assigned_to': {'old': old_assigned, 'new': None}, 'status': {'old': 'in_use', 'new': 'free'}},
        ip_address=request.remote_addr
    )
    db.session.commit()

    return api_response(gpu.to_dict(), 'GPU已释放')


@gpus_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_gpu(id):
    """删除GPU"""
    user = get_current_user()
    gpu = GPU.query.get_or_404(id)
    snapshot = gpu.to_dict()

    AuditLog.log_action(
        user=user, action='delete', resource_type='gpu',
        resource_id=gpu.id, resource_name=f"{gpu.model}",
        snapshot=snapshot, ip_address=request.remote_addr
    )

    db.session.delete(gpu)
    db.session.commit()

    return api_response(None, 'GPU删除成功')
