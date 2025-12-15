"""Marshmallow Schemas for Input Validation"""
from flask_marshmallow import Marshmallow
from marshmallow import fields, validate, validates, ValidationError, post_load, EXCLUDE
import re

ma = Marshmallow()


def init_marshmallow(app):
    """Initialize Flask-Marshmallow with app"""
    ma.init_app(app)


# ============== Validation Helpers ==============

def validate_ip_address(value):
    """Validate IPv4 address format"""
    if value is None:
        return
    pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if not re.match(pattern, value):
        raise ValidationError('Invalid IP address format')
    parts = value.split('.')
    for part in parts:
        if int(part) > 255:
            raise ValidationError('Invalid IP address: octets must be 0-255')


# ============== Server Schemas ==============

class ServerCreateSchema(ma.Schema):
    """Schema for creating a server"""
    class Meta:
        unknown = EXCLUDE

    name = fields.String(
        required=True,
        validate=[
            validate.Length(min=1, max=64, error='Server name must be 1-64 characters'),
            validate.Regexp(r'^[a-zA-Z0-9\-_\.]+$', error='Server name can only contain letters, numbers, hyphens, underscores, and dots')
        ]
    )
    datacenter_id = fields.Integer(required=True, validate=validate.Range(min=1))
    environment_id = fields.Integer(required=True, validate=validate.Range(min=1))
    internal_ip = fields.String(required=True, validate=validate_ip_address)
    external_ip = fields.String(allow_none=True, validate=validate_ip_address)
    cpu_cores = fields.Integer(allow_none=True, validate=validate.Range(min=1, max=1024))
    memory_gb = fields.Integer(allow_none=True, validate=validate.Range(min=1, max=65536))
    disk_gb = fields.Integer(allow_none=True, validate=validate.Range(min=1, max=1000000))
    os_type = fields.String(allow_none=True, validate=validate.Length(max=64))
    status = fields.String(
        load_default='online',
        validate=validate.OneOf(['online', 'offline', 'maintenance'])
    )
    responsible_person = fields.String(allow_none=True, validate=validate.Length(max=64))
    description = fields.String(allow_none=True)
    ssh_port = fields.Integer(load_default=22, validate=validate.Range(min=1, max=65535))
    ssh_user = fields.String(load_default='root', validate=validate.Length(max=32))


class ServerUpdateSchema(ma.Schema):
    """Schema for updating a server"""
    class Meta:
        unknown = EXCLUDE

    name = fields.String(
        validate=[
            validate.Length(min=1, max=64),
            validate.Regexp(r'^[a-zA-Z0-9\-_\.]+$')
        ]
    )
    datacenter_id = fields.Integer(validate=validate.Range(min=1))
    environment_id = fields.Integer(validate=validate.Range(min=1))
    internal_ip = fields.String(validate=validate_ip_address)
    external_ip = fields.String(allow_none=True, validate=validate_ip_address)
    cpu_cores = fields.Integer(allow_none=True, validate=validate.Range(min=1, max=1024))
    memory_gb = fields.Integer(allow_none=True, validate=validate.Range(min=1, max=65536))
    disk_gb = fields.Integer(allow_none=True, validate=validate.Range(min=1, max=1000000))
    os_type = fields.String(allow_none=True, validate=validate.Length(max=64))
    cpu_usage = fields.Float(validate=validate.Range(min=0, max=100))
    memory_usage = fields.Float(validate=validate.Range(min=0, max=100))
    disk_usage = fields.Float(validate=validate.Range(min=0, max=100))
    status = fields.String(validate=validate.OneOf(['online', 'offline', 'maintenance']))
    responsible_person = fields.String(allow_none=True, validate=validate.Length(max=64))
    description = fields.String(allow_none=True)
    ssh_port = fields.Integer(validate=validate.Range(min=1, max=65535))
    ssh_user = fields.String(validate=validate.Length(max=32))


# ============== Container Schemas ==============

class ContainerCreateSchema(ma.Schema):
    """Schema for creating a container"""
    class Meta:
        unknown = EXCLUDE

    name = fields.String(
        required=True,
        validate=[
            validate.Length(min=1, max=64),
            validate.Regexp(r'^[a-zA-Z0-9\-_\.]+$', error='Container name can only contain letters, numbers, hyphens, underscores, and dots')
        ]
    )
    server_id = fields.Integer(required=True, validate=validate.Range(min=1))
    image = fields.String(allow_none=True, validate=validate.Length(max=256))
    container_id = fields.String(allow_none=True, validate=validate.Length(max=64))
    cpu_limit = fields.Float(allow_none=True, validate=validate.Range(min=0.1, max=1024))
    memory_limit_mb = fields.Integer(allow_none=True, validate=validate.Range(min=64, max=1048576))
    status = fields.String(
        load_default='running',
        validate=validate.OneOf(['running', 'stopped', 'error'])
    )
    description = fields.String(allow_none=True)


class ContainerUpdateSchema(ma.Schema):
    """Schema for updating a container"""
    class Meta:
        unknown = EXCLUDE

    name = fields.String(
        validate=[
            validate.Length(min=1, max=64),
            validate.Regexp(r'^[a-zA-Z0-9\-_\.]+$')
        ]
    )
    server_id = fields.Integer(validate=validate.Range(min=1))
    image = fields.String(allow_none=True, validate=validate.Length(max=256))
    container_id = fields.String(allow_none=True, validate=validate.Length(max=64))
    cpu_limit = fields.Float(allow_none=True, validate=validate.Range(min=0.1, max=1024))
    memory_limit_mb = fields.Integer(allow_none=True, validate=validate.Range(min=64, max=1048576))
    cpu_usage = fields.Float(validate=validate.Range(min=0, max=100))
    memory_usage = fields.Float(validate=validate.Range(min=0, max=100))
    status = fields.String(validate=validate.OneOf(['running', 'stopped', 'error']))
    description = fields.String(allow_none=True)


# ============== Service Schemas ==============

class ServiceCreateSchema(ma.Schema):
    """Schema for creating a service"""
    class Meta:
        unknown = EXCLUDE

    name = fields.String(
        required=True,
        validate=[
            validate.Length(min=1, max=64),
            validate.Regexp(r'^[a-zA-Z0-9\-_\.]+$', error='Service name can only contain letters, numbers, hyphens, underscores, and dots')
        ]
    )
    container_id = fields.Integer(required=True, validate=validate.Range(min=1))
    service_type = fields.String(
        allow_none=True,
        validate=validate.OneOf(['web', 'api', 'database', 'cache', 'queue', 'proxy', 'monitor', 'other'])
    )
    port = fields.Integer(allow_none=True, validate=validate.Range(min=1, max=65535))
    version = fields.String(allow_none=True, validate=validate.Length(max=32))
    status = fields.String(
        load_default='healthy',
        validate=validate.OneOf(['healthy', 'unhealthy', 'stopped'])
    )
    health_check_url = fields.String(allow_none=True, validate=validate.Length(max=256))
    description = fields.String(allow_none=True)


class ServiceUpdateSchema(ma.Schema):
    """Schema for updating a service"""
    class Meta:
        unknown = EXCLUDE

    name = fields.String(
        validate=[
            validate.Length(min=1, max=64),
            validate.Regexp(r'^[a-zA-Z0-9\-_\.]+$')
        ]
    )
    container_id = fields.Integer(validate=validate.Range(min=1))
    service_type = fields.String(
        allow_none=True,
        validate=validate.OneOf(['web', 'api', 'database', 'cache', 'queue', 'proxy', 'monitor', 'other'])
    )
    port = fields.Integer(allow_none=True, validate=validate.Range(min=1, max=65535))
    version = fields.String(allow_none=True, validate=validate.Length(max=32))
    status = fields.String(validate=validate.OneOf(['healthy', 'unhealthy', 'stopped']))
    health_check_url = fields.String(allow_none=True, validate=validate.Length(max=256))
    description = fields.String(allow_none=True)


# ============== GPU Schemas ==============

class GPUCreateSchema(ma.Schema):
    """Schema for creating a GPU"""
    class Meta:
        unknown = EXCLUDE

    server_id = fields.Integer(required=True, validate=validate.Range(min=1))
    model = fields.String(required=True, validate=validate.Length(min=1, max=64))
    memory_gb = fields.Integer(required=True, validate=validate.Range(min=1, max=1024))
    index = fields.Integer(load_default=0, validate=validate.Range(min=0, max=15))
    status = fields.String(
        load_default='free',
        validate=validate.OneOf(['free', 'in_use', 'error'])
    )
    description = fields.String(allow_none=True)


class GPUUpdateSchema(ma.Schema):
    """Schema for updating a GPU"""
    class Meta:
        unknown = EXCLUDE

    server_id = fields.Integer(validate=validate.Range(min=1))
    assigned_to = fields.Integer(allow_none=True, validate=validate.Range(min=1))
    model = fields.String(validate=validate.Length(min=1, max=64))
    memory_gb = fields.Integer(validate=validate.Range(min=1, max=1024))
    index = fields.Integer(validate=validate.Range(min=0, max=15))
    gpu_usage = fields.Float(validate=validate.Range(min=0, max=100))
    memory_usage = fields.Float(validate=validate.Range(min=0, max=100))
    status = fields.String(validate=validate.OneOf(['free', 'in_use', 'error']))
    description = fields.String(allow_none=True)


# ============== Datacenter Schemas ==============

class DatacenterCreateSchema(ma.Schema):
    """Schema for creating a datacenter"""
    class Meta:
        unknown = EXCLUDE

    name = fields.String(
        required=True,
        validate=[
            validate.Length(min=1, max=64),
            validate.Regexp(r'^[\u4e00-\u9fa5a-zA-Z0-9\-_\.]+$', error='Datacenter name can only contain Chinese characters, letters, numbers, hyphens, underscores, and dots')
        ]
    )
    location = fields.String(allow_none=True, validate=validate.Length(max=128))
    description = fields.String(allow_none=True)
    is_active = fields.Boolean(load_default=True)


class DatacenterUpdateSchema(ma.Schema):
    """Schema for updating a datacenter"""
    class Meta:
        unknown = EXCLUDE

    name = fields.String(
        validate=[
            validate.Length(min=1, max=64),
            validate.Regexp(r'^[\u4e00-\u9fa5a-zA-Z0-9\-_\.]+$')
        ]
    )
    location = fields.String(allow_none=True, validate=validate.Length(max=128))
    description = fields.String(allow_none=True)
    is_active = fields.Boolean()


# ============== User Schemas ==============

class UserCreateSchema(ma.Schema):
    """Schema for creating a user"""
    class Meta:
        unknown = EXCLUDE

    username = fields.String(
        required=True,
        validate=[
            validate.Length(min=3, max=64, error='Username must be 3-64 characters'),
            validate.Regexp(r'^[a-zA-Z][a-zA-Z0-9_]*$', error='Username must start with a letter and contain only letters, numbers, and underscores')
        ]
    )
    password = fields.String(
        required=True,
        validate=validate.Length(min=6, max=128, error='Password must be 6-128 characters')
    )
    display_name = fields.String(
        required=True,
        validate=validate.Length(min=1, max=64, error='Display name must be 1-64 characters')
    )
    email = fields.Email(allow_none=True)
    role = fields.String(
        load_default='user',
        validate=validate.OneOf(['admin', 'user'])
    )
    is_active = fields.Boolean(load_default=True)


class UserUpdateSchema(ma.Schema):
    """Schema for updating a user"""
    class Meta:
        unknown = EXCLUDE

    username = fields.String(
        validate=[
            validate.Length(min=3, max=64),
            validate.Regexp(r'^[a-zA-Z][a-zA-Z0-9_]*$')
        ]
    )
    password = fields.String(validate=validate.Length(min=6, max=128))
    display_name = fields.String(validate=validate.Length(min=1, max=64))
    email = fields.Email(allow_none=True)
    role = fields.String(validate=validate.OneOf(['admin', 'user']))
    is_active = fields.Boolean()


class LoginSchema(ma.Schema):
    """Schema for user login"""
    class Meta:
        unknown = EXCLUDE

    username = fields.String(required=True, validate=validate.Length(min=1, max=64))
    password = fields.String(required=True, validate=validate.Length(min=1, max=128))


# ============== Schema Instances ==============

# Server schemas
server_create_schema = ServerCreateSchema()
server_update_schema = ServerUpdateSchema()

# Container schemas
container_create_schema = ContainerCreateSchema()
container_update_schema = ContainerUpdateSchema()

# Service schemas
service_create_schema = ServiceCreateSchema()
service_update_schema = ServiceUpdateSchema()

# GPU schemas
gpu_create_schema = GPUCreateSchema()
gpu_update_schema = GPUUpdateSchema()

# Datacenter schemas
datacenter_create_schema = DatacenterCreateSchema()
datacenter_update_schema = DatacenterUpdateSchema()

# User schemas
user_create_schema = UserCreateSchema()
user_update_schema = UserUpdateSchema()
login_schema = LoginSchema()
