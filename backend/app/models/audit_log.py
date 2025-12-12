"""审计日志模型"""
from datetime import datetime
import json
from app.extensions import db


class AuditLog(db.Model):
    """审计日志表"""
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    username = db.Column(db.String(64), nullable=False)  # 记录用户名，即使用户删除也保留

    # 操作信息
    action = db.Column(db.String(20), nullable=False)  # create, update, delete
    resource_type = db.Column(db.String(32), nullable=False)  # server, container, service, gpu, etc.
    resource_id = db.Column(db.Integer, nullable=False)
    resource_name = db.Column(db.String(128), nullable=True)  # 资源名称

    # 变更内容 (JSON格式)
    changes = db.Column(db.Text, nullable=True)  # {"field": {"old": "...", "new": "..."}}
    snapshot = db.Column(db.Text, nullable=True)  # 操作前的完整快照 (用于删除操作)

    # 客户端信息
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(256), nullable=True)

    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # 用户关联
    user = db.relationship('User', backref='audit_logs', lazy='select')

    def set_changes(self, changes_dict):
        """设置变更内容"""
        self.changes = json.dumps(changes_dict, ensure_ascii=False)

    def get_changes(self):
        """获取变更内容"""
        if self.changes:
            return json.loads(self.changes)
        return {}

    def set_snapshot(self, snapshot_dict):
        """设置快照"""
        self.snapshot = json.dumps(snapshot_dict, ensure_ascii=False)

    def get_snapshot(self):
        """获取快照"""
        if self.snapshot:
            return json.loads(self.snapshot)
        return {}

    def to_dict(self, include_details=False):
        """转换为字典"""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.username,
            'action': self.action,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'resource_name': self.resource_name,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        if include_details:
            data['changes'] = self.get_changes()
            data['snapshot'] = self.get_snapshot()
            data['user_agent'] = self.user_agent
        return data

    @staticmethod
    def log_action(user, action, resource_type, resource_id, resource_name=None,
                   changes=None, snapshot=None, ip_address=None, user_agent=None):
        """记录操作日志"""
        log = AuditLog(
            user_id=user.id if user else None,
            username=user.username if user else 'system',
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_name=resource_name,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        if changes:
            log.set_changes(changes)
        if snapshot:
            log.set_snapshot(snapshot)
        db.session.add(log)
        return log

    def __repr__(self):
        return f'<AuditLog {self.action} {self.resource_type}:{self.resource_id}>'
