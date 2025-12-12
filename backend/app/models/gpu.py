"""GPU模型"""
from datetime import datetime
from app.extensions import db


class GPU(db.Model):
    """GPU资源表"""
    __tablename__ = 'gpus'

    id = db.Column(db.Integer, primary_key=True)
    server_id = db.Column(db.Integer, db.ForeignKey('servers.id'), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # 分配给的用户

    # GPU配置
    model = db.Column(db.String(64), nullable=False)  # GPU型号 (如: NVIDIA A100)
    memory_gb = db.Column(db.Integer, nullable=False)  # 显存大小
    index = db.Column(db.Integer, default=0)  # GPU索引 (多卡时)

    # 资源使用率 (手动更新)
    gpu_usage = db.Column(db.Float, default=0)
    memory_usage = db.Column(db.Float, default=0)

    # 状态
    status = db.Column(db.String(20), default='free')  # free, in_use, error
    description = db.Column(db.Text, nullable=True)

    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def is_available(self):
        """是否可用"""
        return self.status == 'free' and self.assigned_to is None

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'server_id': self.server_id,
            'server_name': self.server.name if self.server else None,
            'assigned_to': self.assigned_to,
            'assigned_user_name': self.assigned_user.display_name if self.assigned_user else None,
            'model': self.model,
            'memory_gb': self.memory_gb,
            'index': self.index,
            'gpu_usage': self.gpu_usage,
            'memory_usage': self.memory_usage,
            'status': self.status,
            'is_available': self.is_available,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f'<GPU {self.model} on {self.server.name if self.server else "Unknown"}>'
