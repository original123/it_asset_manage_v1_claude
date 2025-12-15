"""Flask应用配置"""
import os
from datetime import timedelta
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class Config:
    """基础配置"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # MySQL数据库配置 - 必须通过环境变量设置
    # 后备值使用SQLite用于本地开发（不含生产凭据）
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///instance/it_assets_dev.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }

    # JWT配置
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_TOKEN_LOCATION = ['headers']  # 只使用 header 传递 token
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    JWT_COOKIE_CSRF_PROTECT = False  # 禁用 CSRF 保护，因为只用 headers

    # CORS配置
    CORS_ORIGINS = ['http://localhost:5173', 'http://127.0.0.1:5173']

    # 分页配置
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    JWT_COOKIE_SECURE = False


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    JWT_COOKIE_SECURE = True


class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
