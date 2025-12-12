"""智能搜索路由"""
import re
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app.models import Server, Container, Service, PortMapping
from app.extensions import db
from app.utils import api_response

search_bp = Blueprint('search', __name__)


def is_ip_pattern(keyword):
    """判断是否为IP地址模式"""
    ip_pattern = r'^(\d{1,3}\.){0,3}\d{0,3}$'
    return bool(re.match(ip_pattern, keyword))


def is_port_pattern(keyword):
    """判断是否为端口号模式"""
    try:
        port = int(keyword)
        return 1 <= port <= 65535
    except ValueError:
        return False


@search_bp.route('', methods=['GET'])
@jwt_required()
def smart_search():
    """智能搜索"""
    keyword = request.args.get('keyword', '').strip()
    limit = request.args.get('limit', 50, type=int)

    if not keyword:
        return api_response({'servers': [], 'containers': [], 'services': [], 'port_mappings': []})

    results = {
        'servers': [],
        'containers': [],
        'services': [],
        'port_mappings': [],
        'search_type': 'keyword'  # 搜索类型：keyword, ip, port
    }

    # 判断搜索类型
    if is_ip_pattern(keyword):
        results['search_type'] = 'ip'
        # 搜索服务器IP
        servers = Server.query.filter(
            db.or_(
                Server.internal_ip.ilike(f'%{keyword}%'),
                Server.external_ip.ilike(f'%{keyword}%'),
            )
        ).limit(limit).all()
        results['servers'] = [s.to_dict() for s in servers]

        # 搜索端口映射中的IP
        port_mappings = PortMapping.query.filter(
            db.or_(
                PortMapping.internal_ip.ilike(f'%{keyword}%'),
                PortMapping.external_ip.ilike(f'%{keyword}%'),
            )
        ).limit(limit).all()
        results['port_mappings'] = [pm.to_dict() for pm in port_mappings]

    elif is_port_pattern(keyword):
        results['search_type'] = 'port'
        port = int(keyword)
        # 搜索端口映射
        port_mappings = PortMapping.query.filter(
            db.or_(
                PortMapping.container_port == port,
                PortMapping.internal_port == port,
                PortMapping.external_port == port,
            )
        ).limit(limit).all()
        results['port_mappings'] = [pm.to_dict() for pm in port_mappings]

        # 搜索服务端口
        services = Service.query.filter(Service.port == port).limit(limit).all()
        results['services'] = [s.to_dict() for s in services]

        # 搜索SSH端口
        servers = Server.query.filter(Server.ssh_port == port).limit(limit).all()
        results['servers'] = [s.to_dict() for s in servers]

    else:
        results['search_type'] = 'keyword'
        # 关键词搜索
        # 搜索服务器
        servers = Server.query.filter(
            db.or_(
                Server.name.ilike(f'%{keyword}%'),
                Server.responsible_person.ilike(f'%{keyword}%'),
                Server.description.ilike(f'%{keyword}%'),
            )
        ).limit(limit).all()
        results['servers'] = [s.to_dict() for s in servers]

        # 搜索容器
        containers = Container.query.filter(
            db.or_(
                Container.name.ilike(f'%{keyword}%'),
                Container.image.ilike(f'%{keyword}%'),
                Container.description.ilike(f'%{keyword}%'),
            )
        ).limit(limit).all()
        results['containers'] = [c.to_dict() for c in containers]

        # 搜索服务
        services = Service.query.filter(
            db.or_(
                Service.name.ilike(f'%{keyword}%'),
                Service.service_type.ilike(f'%{keyword}%'),
                Service.description.ilike(f'%{keyword}%'),
            )
        ).limit(limit).all()
        results['services'] = [s.to_dict() for s in services]

    # 统计结果数量
    results['total'] = (
        len(results['servers']) +
        len(results['containers']) +
        len(results['services']) +
        len(results['port_mappings'])
    )

    return api_response(results)


@search_bp.route('/quick', methods=['GET'])
@jwt_required()
def quick_search():
    """快速搜索（用于自动补全）"""
    keyword = request.args.get('keyword', '').strip()
    limit = request.args.get('limit', 10, type=int)

    if not keyword or len(keyword) < 2:
        return api_response([])

    suggestions = []

    # 搜索服务器名称
    servers = Server.query.filter(Server.name.ilike(f'%{keyword}%')).limit(limit).all()
    for s in servers:
        suggestions.append({
            'type': 'server',
            'id': s.id,
            'name': s.name,
            'description': f'{s.internal_ip} - {s.datacenter.name if s.datacenter else ""}'
        })

    # 搜索容器名称
    containers = Container.query.filter(Container.name.ilike(f'%{keyword}%')).limit(limit).all()
    for c in containers:
        suggestions.append({
            'type': 'container',
            'id': c.id,
            'name': c.name,
            'description': f'on {c.server.name if c.server else ""}'
        })

    return api_response(suggestions[:limit])
