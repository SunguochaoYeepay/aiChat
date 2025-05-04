"""
部署脚本 - 用于系统部署和环境配置

此脚本用于自动化部署过程，包括环境检查、依赖安装、数据库迁移和静态文件收集等。
"""
import os
import sys
import subprocess
import argparse
import shutil
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent

# 依赖列表
REQUIRED_PACKAGES = [
    'django>=4.2',
    'channels>=4.0.0',
    'daphne>=4.0.0',
    'numpy>=1.20.0',
    'sentence-transformers>=2.2.0',
    'torch>=1.11.0',
    'transformers>=4.20.0',
    'pillow>=9.0.0',
]

def run_command(command, description=None, exit_on_error=True):
    """运行命令并处理结果"""
    if description:
        print(f"[INFO] {description}")
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        if result.stdout:
            print(result.stdout)
        return True
    else:
        print(f"[ERROR] 命令执行失败: {command}")
        print(f"错误信息: {result.stderr}")
        
        if exit_on_error:
            sys.exit(1)
        return False

def check_environment():
    """检查运行环境"""
    print("[INFO] 正在检查运行环境...")
    
    # 检查Python版本
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("[ERROR] Python版本过低，需要Python 3.8+")
        sys.exit(1)
    
    print(f"[INFO] Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # 检查CUDA是否可用（如果系统有GPU）
    try:
        import torch
        cuda_available = torch.cuda.is_available()
        if cuda_available:
            device_count = torch.cuda.device_count()
            device_name = torch.cuda.get_device_name(0) if device_count > 0 else "未知"
            print(f"[INFO] CUDA可用，设备数量: {device_count}，设备名称: {device_name}")
        else:
            print("[WARN] CUDA不可用，将使用CPU模式")
    except ImportError:
        print("[WARN] 未安装PyTorch，无法检查CUDA状态")
    
    print("[INFO] 环境检查完成")
    return True

def install_dependencies():
    """安装项目依赖"""
    print("[INFO] 正在安装项目依赖...")
    
    # 检查pip版本
    run_command("pip --version", "检查pip版本")
    
    # 升级pip
    run_command("pip install --upgrade pip", "升级pip")
    
    # 安装依赖
    for package in REQUIRED_PACKAGES:
        run_command(f"pip install {package}", f"安装{package}")
    
    # 安装项目所有依赖
    if os.path.exists(os.path.join(BASE_DIR, "requirements.txt")):
        run_command("pip install -r requirements.txt", "安装requirements.txt中的依赖")
    
    print("[INFO] 依赖安装完成")
    return True

def setup_database():
    """设置数据库"""
    print("[INFO] 正在设置数据库...")
    
    # 执行数据库迁移
    run_command("python manage.py makemigrations", "创建数据库迁移")
    run_command("python manage.py migrate", "应用数据库迁移")
    
    # 处理知识库
    run_command("python manage.py migrate_kb", "迁移知识库")
    run_command("python manage.py process_kb --all", "处理知识库向量索引")
    
    print("[INFO] 数据库设置完成")
    return True

def collect_static_files():
    """收集静态文件"""
    print("[INFO] 正在收集静态文件...")
    
    # 创建静态文件目录
    static_dir = os.path.join(BASE_DIR, "static")
    os.makedirs(static_dir, exist_ok=True)
    
    # 创建边界框图像目录
    box_image_dir = os.path.join(static_dir, "box_images")
    os.makedirs(box_image_dir, exist_ok=True)
    
    # 收集静态文件
    run_command("python manage.py collectstatic --noinput", "收集静态文件")
    
    print("[INFO] 静态文件收集完成")
    return True

def create_superuser():
    """创建超级用户"""
    print("[INFO] 开始创建超级用户...")
    
    # 检查是否已存在超级用户
    check_superuser_cmd = (
        'python manage.py shell -c "'
        'from django.contrib.auth.models import User; '
        'print(User.objects.filter(is_superuser=True).exists())'
        '"'
    )
    
    result = subprocess.run(check_superuser_cmd, shell=True, capture_output=True, text=True)
    if "True" in result.stdout:
        print("[INFO] 超级用户已存在，跳过创建")
        return True
    
    # 创建超级用户
    username = input("请输入管理员用户名 [admin]: ") or "admin"
    email = input("请输入管理员邮箱 [admin@example.com]: ") or "admin@example.com"
    
    create_superuser_cmd = (
        f'python manage.py shell -c "'
        f'from django.contrib.auth.models import User; '
        f'User.objects.create_superuser(\'{username}\', \'{email}\', \'admin123\')'
        f'"'
    )
    
    run_command(create_superuser_cmd, "创建超级用户")
    print(f"[INFO] 超级用户已创建: {username} (密码: admin123)")
    
    return True

def setup_production_server():
    """配置生产服务器"""
    print("[INFO] 正在配置生产服务器...")
    
    # 创建systemd服务文件
    service_file = """[Unit]
Description=AI图像分析服务
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory={base_dir}
ExecStart=/usr/bin/daphne -b 0.0.0.0 -p 8000 admin_system.asgi:application
Restart=always
RestartSec=5
SyslogIdentifier=ai-design-helper

[Install]
WantedBy=multi-user.target
""".format(base_dir=BASE_DIR)
    
    service_path = os.path.join(BASE_DIR, "ai-design-helper.service")
    with open(service_path, "w") as f:
        f.write(service_file)
    
    print(f"[INFO] 服务文件已创建: {service_path}")
    print("[INFO] 要安装服务，请执行以下命令:")
    print(f"  sudo cp {service_path} /etc/systemd/system/")
    print("  sudo systemctl daemon-reload")
    print("  sudo systemctl enable ai-design-helper")
    print("  sudo systemctl start ai-design-helper")
    
    # 创建Nginx配置文件
    nginx_conf = """server {
    listen 80;
    server_name _;  # 替换为你的域名

    location /static/ {
        alias {base_dir}/staticfiles/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 300s;
        proxy_read_timeout 300s;
    }

    location /ws/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
""".format(base_dir=BASE_DIR)
    
    nginx_path = os.path.join(BASE_DIR, "ai-design-helper.nginx.conf")
    with open(nginx_path, "w") as f:
        f.write(nginx_conf)
    
    print(f"[INFO] Nginx配置文件已创建: {nginx_path}")
    print("[INFO] 要配置Nginx，请执行以下命令:")
    print(f"  sudo cp {nginx_path} /etc/nginx/sites-available/ai-design-helper")
    print("  sudo ln -s /etc/nginx/sites-available/ai-design-helper /etc/nginx/sites-enabled/")
    print("  sudo nginx -t")
    print("  sudo systemctl restart nginx")
    
    print("[INFO] 生产服务器配置完成")
    return True

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="AI图像分析服务部署脚本")
    parser.add_argument("--check", action="store_true", help="仅检查环境")
    parser.add_argument("--deps", action="store_true", help="仅安装依赖")
    parser.add_argument("--db", action="store_true", help="仅设置数据库")
    parser.add_argument("--static", action="store_true", help="仅收集静态文件")
    parser.add_argument("--superuser", action="store_true", help="仅创建超级用户")
    parser.add_argument("--production", action="store_true", help="配置生产服务器")
    
    args = parser.parse_args()
    
    # 检查是否指定了特定任务
    specific_task = any([
        args.check, args.deps, args.db, 
        args.static, args.superuser, args.production
    ])
    
    # 执行任务
    if args.check or not specific_task:
        check_environment()
    
    if args.deps or not specific_task:
        install_dependencies()
    
    if args.db or not specific_task:
        setup_database()
    
    if args.static or not specific_task:
        collect_static_files()
    
    if args.superuser or not specific_task:
        create_superuser()
    
    if args.production:
        setup_production_server()
    
    if not specific_task:
        print("\n[INFO] 部署完成")
        print("[INFO] 要启动开发服务器，请运行:")
        print("  python manage.py runserver")
        print("[INFO] 要配置生产环境，请运行:")
        print("  python deploy.py --production")

if __name__ == "__main__":
    main() 