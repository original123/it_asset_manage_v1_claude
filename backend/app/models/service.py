"""服务模型"""
from datetime import datetime
from app.extensions import db


class Service(db.Model):
    """服务表"""
    __tablename__ = 'services'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, index=True)
    container_id = db.Column(db.Integer, db.ForeignKey('containers.id'), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # 服务配置
    service_type = db.Column(db.String(32), nullable=True)  # web, api, database, cache, etc.
    port = db.Column(db.Integer, nullable=True)  # 服务端口
    version = db.Column(db.String(32), nullable=True)  # 版本号

    # 状态
    status = db.Column(db.String(20), default='healthy')  # healthy, unhealthy, stopped
    health_check_url = db.Column(db.String(256), nullable=True)  # 健康检查URL
    description = db.Column(db.Text, nullable=True)

    # 排序
    sort_order = db.Column(db.Integer, default=0)  # 排序顺序

    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'container_id': self.container_id,
            'container_name': self.container.name if self.container else None,
            'owner_id': self.owner_id,
            'owner_name': self.owner.display_name if self.owner else None,
            'service_type': self.service_type,
            'port': self.port,
            'version': self.version,
            'status': self.status,
            'health_check_url': self.health_check_url,
            'description': self.description,
            'sort_order': self.sort_order,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f'<Service {self.name}>'
