"""容器模型"""
from datetime import datetime
from app.extensions import db


class Container(db.Model):
    """容器表"""
    __tablename__ = 'containers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, index=True)
    server_id = db.Column(db.Integer, db.ForeignKey('servers.id'), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # 使用人和用途
    assigned_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # 使用人
    purpose = db.Column(db.String(200), nullable=True)  # 用途简介

    # 容器配置
    image = db.Column(db.String(256), nullable=True)  # Docker镜像
    container_id = db.Column(db.String(64), nullable=True)  # Docker容器ID

    # 资源配置
    cpu_limit = db.Column(db.Float, nullable=True)  # CPU限制
    memory_limit_mb = db.Column(db.Integer, nullable=True)  # 内存限制(MB)

    # 资源使用率 (手动更新)
    cpu_usage = db.Column(db.Float, default=0)
    memory_usage = db.Column(db.Float, default=0)

    # 状态
    status = db.Column(db.String(20), default='running')  # running, stopped, error
    description = db.Column(db.Text, nullable=True)

    # 排序
    sort_order = db.Column(db.Integer, default=0)  # 排序顺序

    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联
    port_mappings = db.relationship('PortMapping', backref='container', lazy='dynamic', cascade='all, delete-orphan')
    services = db.relationship('Service', backref='container', lazy='dynamic', cascade='all, delete-orphan')
    assigned_user = db.relationship('User', foreign_keys=[assigned_user_id], backref='assigned_containers')

    @property
    def service_count(self):
        """服务数量"""
        return self.services.count()

    def to_dict(self, include_children=False):
        """转换为字典"""
        data = {
            'id': self.id,
            'name': self.name,
            'server_id': self.server_id,
            'server_name': self.server.name if self.server else None,
            'owner_id': self.owner_id,
            'owner_name': self.owner.display_name if self.owner else None,
            'assigned_user_id': self.assigned_user_id,
            'assigned_user_name': self.assigned_user.display_name if self.assigned_user else None,
            'purpose': self.purpose,
            'image': self.image,
            'container_id': self.container_id,
            'cpu_limit': self.cpu_limit,
            'memory_limit_mb': self.memory_limit_mb,
            'cpu_usage': self.cpu_usage,
            'memory_usage': self.memory_usage,
            'status': self.status,
            'description': self.description,
            'sort_order': self.sort_order,
            'service_count': self.service_count,
            'port_mappings': [pm.to_dict() for pm in self.port_mappings],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_children:
            data['services'] = [s.to_dict() for s in self.services]
        return data

    def __repr__(self):
        return f'<Container {self.name}>'
