#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
统一启动脚本 - 用于同时启动Django管理系统和GPU模型服务

此脚本提供简单的命令行接口，用于启动整个系统或其中的某个组件。
"""
import os
import sys
import argparse
import subprocess
import time
import signal
import psutil
from pathlib import Path

# 基础路径设置
BASE_DIR = Path(__file__).resolve().parent
DJANGO_DIR = os.path.join(BASE_DIR, "admin_system")

# 进程管理
processes = []

def run_command(command, cwd=None, shell=True):
    """运行命令并返回进程对象"""
    try:
        process = subprocess.Popen(
            command,
            shell=shell,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        return process
    except Exception as e:
        print(f"执行命令失败: {command}")
        print(f"错误信息: {str(e)}")
        return None

def start_django():
    """启动Django管理系统"""
    print("正在启动Django管理系统...")
    
    # 检查是否存在manage.py
    manage_py = os.path.join(DJANGO_DIR, "manage.py")
    if not os.path.exists(manage_py):
        print(f"错误: 找不到Django管理文件 ({manage_py})")
        return None
    
    # 启动Django
    process = run_command(
        "python manage.py runserver 0.0.0.0:8000",
        cwd=DJANGO_DIR
    )
    
    if process:
        print(f"Django管理系统已启动，PID: {process.pid}")
        return process
    else:
        print("Django管理系统启动失败")
        return None

def start_gpu_server():
    """启动GPU模型服务"""
    print("正在启动GPU模型服务...")
    
    # 检查服务文件是否存在
    gpu_server = os.path.join(BASE_DIR, "gpu_model_server.py")
    if not os.path.exists(gpu_server):
        print(f"错误: 找不到GPU服务文件 ({gpu_server})")
        return None
    
    # 启动GPU服务
    process = run_command(
        "python gpu_model_server.py",
        cwd=BASE_DIR
    )
    
    if process:
        print(f"GPU模型服务已启动，PID: {process.pid}")
        return process
    else:
        print("GPU模型服务启动失败")
        return None

def monitor_processes():
    """监控所有启动的进程"""
    global processes
    
    while processes:
        for i, proc in enumerate(processes[:]):
            if proc.poll() is not None:
                # 进程已结束
                print(f"进程 {proc.pid} 已结束，退出码: {proc.returncode}")
                processes.remove(proc)
        
        # 输出进程状态
        if processes:
            try:
                for proc in processes:
                    p = psutil.Process(proc.pid)
                    print(f"进程 {proc.pid} 运行中 (CPU: {p.cpu_percent()}%, 内存: {p.memory_info().rss / 1024 / 1024:.1f} MB)")
            except:
                pass
        
        # 等待一段时间
        time.sleep(10)
    
    print("所有进程已结束")

def stop_all():
    """停止所有启动的进程"""
    global processes
    
    print("正在停止所有服务...")
    
    for proc in processes:
        try:
            # 尝试终止进程
            if os.name == 'nt':  # Windows
                subprocess.call(['taskkill', '/F', '/T', '/PID', str(proc.pid)])
            else:  # Linux/Mac
                os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
                proc.terminate()
            print(f"已终止进程 {proc.pid}")
        except:
            print(f"终止进程 {proc.pid} 失败")
    
    # 清空进程列表
    processes = []

def handle_signal(sig, frame):
    """处理信号（如Ctrl+C）"""
    print("\n接收到终止信号，正在关闭所有服务...")
    stop_all()
    sys.exit(0)

def main():
    """主函数"""
    global processes
    
    # 设置信号处理
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)
    
    # 命令行参数解析
    parser = argparse.ArgumentParser(description='AI图像分析服务启动工具')
    parser.add_argument('--django', action='store_true', help='仅启动Django管理系统')
    parser.add_argument('--gpu', action='store_true', help='仅启动GPU模型服务')
    parser.add_argument('--all', action='store_true', help='启动所有服务')
    
    args = parser.parse_args()
    
    # 默认启动所有服务
    if not (args.django or args.gpu):
        args.all = True
    
    # 启动服务
    if args.all or args.django:
        django_process = start_django()
        if django_process:
            processes.append(django_process)
    
    if args.all or args.gpu:
        gpu_process = start_gpu_server()
        if gpu_process:
            processes.append(gpu_process)
    
    # 如果没有成功启动任何进程，退出
    if not processes:
        print("没有成功启动任何服务，退出")
        return
    
    print("\n所有服务已启动，按Ctrl+C终止")
    
    # 监控进程
    try:
        monitor_processes()
    except KeyboardInterrupt:
        print("\n接收到终止信号，正在关闭所有服务...")
        stop_all()

if __name__ == "__main__":
    main() 