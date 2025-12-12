"""用户模型"""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db


class User(db.Model):
    """用户表"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    display_name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    role = db.Column(db.String(20), nullable=False, default='user')  # admin, user
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联
    containers = db.relationship('Container', backref='owner', lazy='dynamic', foreign_keys='Container.owner_id')
    services = db.relationship('Service', backref='owner', lazy='dynamic', foreign_keys='Service.owner_id')
    gpus = db.relationship('GPU', backref='assigned_user', lazy='dynamic', foreign_keys='GPU.assigned_to')

    def set_password(self, password):
        """设置密码哈希"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        """是否管理员"""
        return self.role == 'admin'

    def to_dict(self, include_email=False):
        """转换为字典"""
        data = {
            'id': self.id,
            'username': self.username,
            'display_name': self.display_name,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        if include_email:
            data['email'] = self.email
        return data

    def __repr__(self):
        return f'<User {self.username}>'
