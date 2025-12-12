"""Flask应用入口"""
import os
import random
from app import create_app
from app.extensions import db
from app.models import User, Environment, Datacenter, Server, Container, Service, GPU

app = create_app()


@app.cli.command('init-db')
def init_db():
    """初始化数据库"""
    db.create_all()

    # 初始化环境数据
    Environment.init_default_environments()

    # 创建默认管理员账号
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            display_name='管理员',
            role='admin',
            is_active=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print('默认管理员账号已创建: admin / admin123')

    print('数据库初始化完成!')


@app.cli.command('create-admin')
def create_admin():
    """创建管理员账号"""
    import getpass

    username = input('用户名: ')
    display_name = input('显示名称: ')
    password = getpass.getpass('密码: ')

    if User.query.filter_by(username=username).first():
        print(f'用户名 {username} 已存在!')
        return

    admin = User(
        username=username,
        display_name=display_name,
        role='admin',
        is_active=True
    )
    admin.set_password(password)
    db.session.add(admin)
    db.session.commit()
    print(f'管理员 {username} 创建成功!')


@app.cli.command('generate-data')
def generate_data():
    """生成示例数据"""
    print('开始生成示例数据...')

    # 创建机房
    datacenters_data = [
        {'name': '北京机房', 'location': '北京市朝阳区', 'description': '主要生产环境机房'},
        {'name': '上海机房', 'location': '上海市浦东新区', 'description': '灾备和测试环境机房'},
        {'name': '深圳机房', 'location': '深圳市南山区', 'description': '华南区域业务机房'},
    ]

    datacenters = []
    for dc_data in datacenters_data:
        dc = Datacenter.query.filter_by(name=dc_data['name']).first()
        if not dc:
            dc = Datacenter(**dc_data)
            db.session.add(dc)
        datacenters.append(dc)
    db.session.commit()
    print(f'创建了 {len(datacenters)} 个机房')

    # 获取环境
    environments = Environment.query.all()
    env_map = {e.name: e for e in environments}

    # 服务器配置模板
    server_templates = [
        {'cpu_cores': 4, 'memory_gb': 8, 'disk_gb': 100, 'os_type': 'CentOS 7.9'},
        {'cpu_cores': 8, 'memory_gb': 16, 'disk_gb': 200, 'os_type': 'Ubuntu 20.04'},
        {'cpu_cores': 16, 'memory_gb': 32, 'disk_gb': 500, 'os_type': 'CentOS 8'},
        {'cpu_cores': 32, 'memory_gb': 64, 'disk_gb': 1000, 'os_type': 'Ubuntu 22.04'},
        {'cpu_cores': 64, 'memory_gb': 128, 'disk_gb': 2000, 'os_type': 'Rocky Linux 9'},
    ]

    # 服务名称池
    service_names = [
        'nginx', 'mysql', 'redis', 'elasticsearch', 'kafka',
        'zookeeper', 'mongodb', 'postgresql', 'rabbitmq', 'consul',
        'prometheus', 'grafana', 'jenkins', 'gitlab', 'harbor',
        'nacos', 'sentinel', 'xxl-job', 'seata', 'skywalking'
    ]

    # 负责人列表
    responsible_persons = ['张三', '李四', '王五', '赵六', '孙七', '周八', '吴九', '郑十']

    servers_created = 0
    containers_created = 0
    services_created = 0
    gpus_created = 0

    # 为每个机房创建服务器
    for dc_idx, dc in enumerate(datacenters):
        # 每个机房创建5-10台服务器
        num_servers = random.randint(5, 10)

        for i in range(num_servers):
            # 随机选择环境和配置
            env_name = random.choice(['生产环境', '预发环境', '测试环境', '开发环境'])
            env = env_map.get(env_name)
            if not env:
                continue

            template = random.choice(server_templates)

            # 生成IP地址
            ip_prefix = f'10.{dc_idx + 1}.{random.randint(1, 10)}'
            internal_ip = f'{ip_prefix}.{random.randint(2, 254)}'

            # 部分服务器有外网IP
            external_ip = None
            if random.random() > 0.7:
                external_ip = f'203.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(2, 254)}'

            # 服务器名称
            env_short = {'生产环境': 'prod', '预发环境': 'pre', '测试环境': 'test', '开发环境': 'dev'}
            server_name = f'{env_short.get(env_name, "srv")}-{dc.name[:2]}-{i+1:02d}'

            # 检查服务器是否已存在
            existing = Server.query.filter_by(internal_ip=internal_ip).first()
            if existing:
                continue

            server = Server(
                name=server_name,
                datacenter_id=dc.id,
                environment_id=env.id,
                internal_ip=internal_ip,
                external_ip=external_ip,
                cpu_cores=template['cpu_cores'],
                memory_gb=template['memory_gb'],
                disk_gb=template['disk_gb'],
                os_type=template['os_type'],
                status=random.choice(['online', 'online', 'online', 'maintenance']),
                responsible_person=random.choice(responsible_persons),
                cpu_usage=random.randint(10, 85),
                memory_usage=random.randint(20, 90),
                disk_usage=random.randint(15, 75),
                ssh_port=22,
                description=f'{dc.name} {env_name} 服务器'
            )
            db.session.add(server)
            db.session.flush()  # 获取server.id
            servers_created += 1

            # 为每台服务器创建1-5个容器
            num_containers = random.randint(1, 5)
            available_services = random.sample(service_names, min(num_containers * 2, len(service_names)))

            for j in range(num_containers):
                container_name = f'{server_name}-{available_services[j]}'

                container = Container(
                    name=container_name,
                    server_id=server.id,
                    container_id=f'{random.randint(1000, 9999)}{random.randint(100000, 999999):06x}',
                    image=f'{available_services[j]}:latest',
                    status=random.choice(['running', 'running', 'running', 'stopped']),
                    cpu_limit=random.choice([1, 2, 4]),
                    memory_limit=random.choice([1, 2, 4, 8]),
                    restart_policy='always'
                )
                db.session.add(container)
                db.session.flush()
                containers_created += 1

                # 为容器创建1-2个服务
                num_services = random.randint(1, 2)
                for k in range(num_services):
                    port = random.choice([80, 443, 3000, 3306, 5432, 6379, 8080, 8443, 9000, 9200])
                    service = Service(
                        container_id=container.id,
                        name=f'{available_services[j]}-{port}',
                        port=port,
                        protocol='TCP',
                        health_check_url=f'http://localhost:{port}/health' if port in [80, 8080, 3000] else None,
                        is_exposed=random.choice([True, False])
                    )
                    db.session.add(service)
                    services_created += 1

            # 部分服务器有GPU
            if random.random() > 0.8:
                num_gpus = random.choice([1, 2, 4, 8])
                gpu_models = ['NVIDIA A100 80GB', 'NVIDIA A100 40GB', 'NVIDIA V100 32GB', 'NVIDIA RTX 4090']
                gpu_model = random.choice(gpu_models)

                for g in range(num_gpus):
                    gpu = GPU(
                        server_id=server.id,
                        gpu_index=g,
                        model=gpu_model,
                        memory_gb=int(gpu_model.split()[-1].replace('GB', '')),
                        driver_version='535.104.05',
                        cuda_version='12.2',
                        usage_percent=random.randint(0, 95),
                        memory_used_gb=random.randint(0, int(gpu_model.split()[-1].replace('GB', ''))),
                        temperature=random.randint(35, 75),
                        power_usage=random.randint(50, 300)
                    )
                    db.session.add(gpu)
                    gpus_created += 1

    db.session.commit()

    print(f'数据生成完成!')
    print(f'  - 机房: {len(datacenters)} 个')
    print(f'  - 服务器: {servers_created} 台')
    print(f'  - 容器: {containers_created} 个')
    print(f'  - 服务: {services_created} 个')
    print(f'  - GPU: {gpus_created} 块')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
