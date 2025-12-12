"""环境模型"""
from datetime import datetime
from app.extensions import db


class Environment(db.Model):
    """环境表"""
    __tablename__ = 'environments'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True, nullable=False)
    code = db.Column(db.String(16), unique=True, nullable=False)  # prod, staging, test, dev
    color = db.Column(db.String(16), nullable=False, default='#909399')
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 关联
    servers = db.relationship('Server', backref='environment', lazy='dynamic')

    @property
    def server_count(self):
        """服务器数量"""
        return self.servers.count()

    def to_dict(self, include_stats=False):
        """转换为字典"""
        data = {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'color': self.color,
            'sort_order': self.sort_order,
        }
        if include_stats:
            data['server_count'] = self.server_count
        return data

    @staticmethod
    def init_default_environments():
        """初始化默认环境数据"""
        defaults = [
            {'name': '生产环境', 'code': 'prod', 'color': '#F56C6C', 'sort_order': 1},
            {'name': '预发环境', 'code': 'staging', 'color': '#E6A23C', 'sort_order': 2},
            {'name': '测试环境', 'code': 'test', 'color': '#67C23A', 'sort_order': 3},
            {'name': '开发环境', 'code': 'dev', 'color': '#909399', 'sort_order': 4},
        ]
        for env_data in defaults:
            env = Environment.query.filter_by(code=env_data['code']).first()
            if env is None:
                env = Environment(**env_data)
                db.session.add(env)
        db.session.commit()

    def __repr__(self):
        return f'<Environment {self.name}>'
