"""服务器模型"""
from datetime import datetime
from app.extensions import db


class Server(db.Model):
    """服务器表"""
    __tablename__ = 'servers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, index=True)
    datacenter_id = db.Column(db.Integer, db.ForeignKey('datacenters.id'), nullable=False)
    environment_id = db.Column(db.Integer, db.ForeignKey('environments.id'), nullable=False)

    # 网络配置
    internal_ip = db.Column(db.String(45), nullable=False, index=True)  # 内网IP
    external_ip = db.Column(db.String(45), nullable=True)  # 外网IP (可选)

    # 硬件配置
    cpu_cores = db.Column(db.Integer, nullable=True)
    memory_gb = db.Column(db.Integer, nullable=True)
    disk_gb = db.Column(db.Integer, nullable=True)
    os_type = db.Column(db.String(64), nullable=True)  # 操作系统

    # 资源使用率 (手动更新)
    cpu_usage = db.Column(db.Float, default=0)
    memory_usage = db.Column(db.Float, default=0)
    disk_usage = db.Column(db.Float, default=0)

    # 状态
    status = db.Column(db.String(20), default='online')  # online, offline, maintenance
    responsible_person = db.Column(db.String(64), nullable=True)  # 负责人
    description = db.Column(db.Text, nullable=True)

    # SSH配置
    ssh_port = db.Column(db.Integer, default=22)
    ssh_user = db.Column(db.String(32), default='root')

    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联
    containers = db.relationship('Container', backref='server', lazy='dynamic', cascade='all, delete-orphan')
    gpus = db.relationship('GPU', backref='server', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def container_count(self):
        """容器数量"""
        return self.containers.count()

    @property
    def gpu_count(self):
        """GPU数量"""
        return self.gpus.count()

    @property
    def ssh_command(self):
        """生成SSH命令"""
        return f"ssh -p {self.ssh_port} {self.ssh_user}@{self.internal_ip}"

    def to_dict(self, include_children=False):
        """转换为字典"""
        data = {
            'id': self.id,
            'name': self.name,
            'datacenter_id': self.datacenter_id,
            'datacenter_name': self.datacenter.name if self.datacenter else None,
            'environment_id': self.environment_id,
            'environment_name': self.environment.name if self.environment else None,
            'environment_color': self.environment.color if self.environment else None,
            'internal_ip': self.internal_ip,
            'external_ip': self.external_ip,
            'cpu_cores': self.cpu_cores,
            'memory_gb': self.memory_gb,
            'disk_gb': self.disk_gb,
            'os_type': self.os_type,
            'cpu_usage': self.cpu_usage,
            'memory_usage': self.memory_usage,
            'disk_usage': self.disk_usage,
            'status': self.status,
            'responsible_person': self.responsible_person,
            'description': self.description,
            'ssh_port': self.ssh_port,
            'ssh_user': self.ssh_user,
            'ssh_command': self.ssh_command,
            'container_count': self.container_count,
            'gpu_count': self.gpu_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_children:
            data['containers'] = [c.to_dict() for c in self.containers]
            data['gpus'] = [g.to_dict() for g in self.gpus]
        return data

    def __repr__(self):
        return f'<Server {self.name}>'
