#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
生产环境部署脚本

此脚本用于准备生产环境，包括收集静态文件、创建数据库迁移、应用迁移等操作。
"""
import os
import sys
import subprocess
import argparse
from pathlib import Path

# 基础路径设置
BASE_DIR = Path(__file__).resolve().parent

def run_command(command, cwd=None):
    """运行命令并打印输出"""
    print(f"执行: {command}")
    process = subprocess.Popen(
        command,
        shell=True,
        cwd=cwd or BASE_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True
    )
    
    # 实时打印输出
    for line in process.stdout:
        print(line, end='')
    
    # 等待进程完成
    process.wait()
    
    if process.returncode != 0:
        print(f"命令执行失败，退出码: {process.returncode}")
        return False
    
    return True

def collect_static_files():
    """收集静态文件"""
    print("\n===== 收集静态文件 =====")
    return run_command("python manage.py collectstatic --noinput")

def create_migrations():
    """创建数据库迁移"""
    print("\n===== 创建数据库迁移 =====")
    return run_command("python manage.py makemigrations")

def apply_migrations():
    """应用数据库迁移"""
    print("\n===== 应用数据库迁移 =====")
    return run_command("python manage.py migrate")

def check_system():
    """检查系统设置"""
    print("\n===== 检查系统设置 =====")
    return run_command("python manage.py check --deploy")

def create_superuser():
    """创建超级用户（如果不存在）"""
    print("\n===== 创建超级用户 =====")
    print("注意：如果已存在超级用户，此步骤将被跳过")
    
    try:
        # 尝试使用脚本方式创建超级用户
        from django.contrib.auth.models import User
        if not User.objects.filter(is_superuser=True).exists():
            username = input("请输入管理员用户名: ")
            email = input("请输入管理员邮箱: ")
            
            # 使用命令行方式创建密码，这样密码不会显示在屏幕上
            command = f'python manage.py createsuperuser --username="{username}" --email="{email}" --noinput'
            if run_command(command):
                print("创建超级用户成功，请使用manage.py changepassword命令设置密码")
            else:
                print("创建超级用户失败")
        else:
            print("超级用户已存在，跳过创建步骤")
        return True
    except Exception as e:
        print(f"创建超级用户时出错: {str(e)}")
        return False

def prepare_production():
    """准备生产环境"""
    print("\n===== 准备生产环境 =====")
    
    # 1. 收集静态文件
    if not collect_static_files():
        return False
    
    # 2. 创建数据库迁移
    if not create_migrations():
        return False
    
    # 3. 应用数据库迁移
    if not apply_migrations():
        return False
    
    # 4. 检查系统设置
    if not check_system():
        print("系统检查存在问题，但将继续部署过程")
    
    # 5. 创建超级用户（如果需要）
    create_superuser_option = input("\n是否需要创建超级用户？(y/n): ")
    if create_superuser_option.lower() == 'y':
        if not create_superuser():
            print("创建超级用户失败，但将继续部署过程")
    
    print("\n===== 部署过程完成 =====")
    print("您现在可以使用WSGI/ASGI服务器（如Gunicorn、Daphne等）启动应用")
    print("示例命令: gunicorn admin_system.wsgi:application")
    print("          daphne admin_system.asgi:application")
    
    return True

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='生产环境部署工具')
    parser.add_argument('--collect-static', action='store_true', help='仅收集静态文件')
    parser.add_argument('--migrate', action='store_true', help='仅应用数据库迁移')
    parser.add_argument('--check', action='store_true', help='仅检查系统设置')
    parser.add_argument('--createsuperuser', action='store_true', help='仅创建超级用户')
    parser.add_argument('--all', action='store_true', help='执行所有部署步骤')
    
    args = parser.parse_args()
    
    # 如果没有指定任何选项，则视为--all
    if not any(vars(args).values()):
        args.all = True
    
    if args.all:
        prepare_production()
    else:
        if args.collect_static:
            collect_static_files()
        if args.migrate:
            create_migrations()
            apply_migrations()
        if args.check:
            check_system()
        if args.createsuperuser:
            create_superuser()

if __name__ == "__main__":
    # 确保在正确的目录中执行
    os.chdir(BASE_DIR)
    sys.path.insert(0, str(BASE_DIR))
    
    # 设置Django环境
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admin_system.settings')
    
    # 执行主函数
    main() 