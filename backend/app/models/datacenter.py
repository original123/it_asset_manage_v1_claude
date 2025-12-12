"""机房模型"""
from datetime import datetime
from app.extensions import db


class Datacenter(db.Model):
    """机房表"""
    __tablename__ = 'datacenters'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    location = db.Column(db.String(128), nullable=True)
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联
    servers = db.relationship('Server', backref='datacenter', lazy='dynamic')

    @property
    def server_count(self):
        """服务器数量"""
        return self.servers.count()

    def to_dict(self, include_stats=False):
        """转换为字典"""
        data = {
            'id': self.id,
            'name': self.name,
            'location': self.location,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        if include_stats:
            data['server_count'] = self.server_count
        return data

    def __repr__(self):
        return f'<Datacenter {self.name}>'
