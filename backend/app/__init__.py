"""Flask应用工厂"""
import os
from flask import Flask, jsonify
from config import config
from app.extensions import db, migrate, jwt, cors, ma
from marshmallow import ValidationError


def create_app(config_name=None):
    """创建Flask应用实例"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # 初始化扩展
    register_extensions(app)

    # 注册蓝图
    register_blueprints(app)

    # 注册错误处理
    register_error_handlers(app)

    # 注册JWT回调
    register_jwt_callbacks(app)

    return app


def register_extensions(app):
    """注册Flask扩展"""
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app, origins=app.config['CORS_ORIGINS'], supports_credentials=True)
    ma.init_app(app)


def register_blueprints(app):
    """注册蓝图路由"""
    from app.routes.auth import auth_bp
    from app.routes.servers import servers_bp
    from app.routes.containers import containers_bp
    from app.routes.services import services_bp
    from app.routes.gpus import gpus_bp
    from app.routes.datacenters import datacenters_bp
    from app.routes.environments import environments_bp
    from app.routes.audit_logs import audit_logs_bp
    from app.routes.search import search_bp
    from app.routes.users import users_bp
    from app.routes.import_export import import_export_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(servers_bp, url_prefix='/api/servers')
    app.register_blueprint(containers_bp, url_prefix='/api/containers')
    app.register_blueprint(services_bp, url_prefix='/api/services')
    app.register_blueprint(gpus_bp, url_prefix='/api/gpus')
    app.register_blueprint(datacenters_bp, url_prefix='/api/datacenters')
    app.register_blueprint(environments_bp, url_prefix='/api/environments')
    app.register_blueprint(audit_logs_bp, url_prefix='/api/audit-logs')
    app.register_blueprint(search_bp, url_prefix='/api/search')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(import_export_bp, url_prefix='/api/import-export')


def register_error_handlers(app):
    """注册全局错误处理"""
    @app.errorhandler(ValidationError)
    def handle_validation_error(e):
        """处理Marshmallow验证错误"""
        return jsonify(code=400, message='参数验证失败', data={'errors': e.messages}), 400

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify(code=400, message='请求参数错误', data=None), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify(code=401, message='未授权访问', data=None), 401

    @app.errorhandler(403)
    def forbidden(e):
        return jsonify(code=403, message='无权限执行此操作', data=None), 403

    @app.errorhandler(404)
    def not_found(e):
        return jsonify(code=404, message='资源不存在', data=None), 404

    @app.errorhandler(422)
    def unprocessable_entity(e):
        return jsonify(code=422, message='参数验证失败', data=None), 422

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify(code=500, message='服务器内部错误', data=None), 500


def register_jwt_callbacks(app):
    """注册JWT回调函数"""
    import sys

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        print(f"[JWT DEBUG] Token expired - header: {jwt_header}, payload: {jwt_payload}", file=sys.stderr, flush=True)
        return jsonify(code=401, message='Token已过期', data=None), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        print(f"[JWT DEBUG] Invalid token error: {error}", file=sys.stderr, flush=True)
        return jsonify(code=401, message='无效的Token', data=None), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        print(f"[JWT DEBUG] Missing token error: {error}", file=sys.stderr, flush=True)
        return jsonify(code=401, message='缺少认证Token', data=None), 401

    @jwt.token_verification_failed_loader
    def token_verification_failed_callback(jwt_header, jwt_payload):
        print(f"[JWT DEBUG] Token verification failed - header: {jwt_header}, payload: {jwt_payload}", file=sys.stderr, flush=True)
        return jsonify(code=401, message='Token验证失败', data=None), 401
