"""端口映射模型 - 三层端口结构"""
from datetime import datetime
from app.extensions import db


class PortMapping(db.Model):
    """端口映射表 - 三层端口映射"""
    __tablename__ = 'port_mappings'

    id = db.Column(db.Integer, primary_key=True)
    container_id = db.Column(db.Integer, db.ForeignKey('containers.id'), nullable=False)

    # 三层端口结构
    container_port = db.Column(db.Integer, nullable=False)  # Docker容器内部端口 (如: 22)
    internal_ip = db.Column(db.String(45), nullable=True)   # 内网IP (默认使用服务器IP)
    internal_port = db.Column(db.Integer, nullable=False)   # 内网映射端口 (如: 20020)
    external_ip = db.Column(db.String(45), nullable=True)   # 外网IP (防火墙IP)
    external_port = db.Column(db.Integer, nullable=True)    # 外网映射端口 (如: 8000, 可为空)

    # 协议和描述
    protocol = db.Column(db.String(10), default='tcp')  # tcp, udp
    description = db.Column(db.String(128), nullable=True)  # 用途说明

    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def internal_address(self):
        """内网访问地址"""
        ip = self.internal_ip or (self.container.server.internal_ip if self.container and self.container.server else '')
        return f"{ip}:{self.internal_port}" if ip else f":{self.internal_port}"

    @property
    def external_address(self):
        """外网访问地址"""
        if self.external_ip and self.external_port:
            return f"{self.external_ip}:{self.external_port}"
        return None

    @property
    def mapping_chain(self):
        """端口映射链路描述"""
        chain = f"{self.container_port} → {self.internal_address}"
        if self.external_address:
            chain += f" → {self.external_address}"
        return chain

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'container_id': self.container_id,
            'container_port': self.container_port,
            'internal_ip': self.internal_ip,
            'internal_port': self.internal_port,
            'external_ip': self.external_ip,
            'external_port': self.external_port,
            'protocol': self.protocol,
            'description': self.description,
            'internal_address': self.internal_address,
            'external_address': self.external_address,
            'mapping_chain': self.mapping_chain,
        }

    def __repr__(self):
        return f'<PortMapping {self.mapping_chain}>'
