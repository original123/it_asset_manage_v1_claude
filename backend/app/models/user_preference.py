"""用户偏好模型"""
from datetime import datetime
from app.extensions import db


class UserPreference(db.Model):
    """用户偏好表"""
    __tablename__ = 'user_preferences'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)

    # 导航偏好
    grouping_mode = db.Column(db.String(30), default='environment-first')  # environment-first, datacenter-first, flat
    view_mode = db.Column(db.String(20), default='grid')  # grid, list
    panel_width = db.Column(db.Integer, default=260)  # 左侧面板宽度
    show_detail_bar = db.Column(db.Boolean, default=True)  # 是否显示详情栏

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联用户
    user = db.relationship('User', backref=db.backref('preference', uselist=False, cascade='all, delete-orphan'))

    def to_dict(self):
        """转换为字典"""
        return {
            'grouping_mode': self.grouping_mode,
            'view_mode': self.view_mode,
            'panel_width': self.panel_width,
            'show_detail_bar': self.show_detail_bar,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f'<UserPreference user_id={self.user_id}>'
