import os
import sys
import subprocess
from pathlib import Path

def run_with_venv():
    """在虚拟环境中运行Django服务器"""
    try:
        # 获取当前路径
        current_dir = Path.cwd()
        
        # 虚拟环境路径
        venv_dir = current_dir / "chat_env"
        
        # Django项目路径
        django_project_dir = current_dir / "admin_system"
        
        # 检查虚拟环境是否存在
        if not venv_dir.exists():
            print(f"错误: 虚拟环境不存在: {venv_dir}")
            return False
        
        # 检查Django项目是否存在
        if not django_project_dir.exists():
            print(f"错误: Django项目不存在: {django_project_dir}")
            return False
        
        # 确定python解释器路径
        if os.name == 'nt':  # Windows
            python_executable = venv_dir / "Scripts" / "python.exe"
        else:  # Linux/Mac
            python_executable = venv_dir / "bin" / "python"
        
        if not python_executable.exists():
            print(f"错误: Python解释器不存在: {python_executable}")
            return False
        
        # 启动Django服务器
        print(f"使用虚拟环境启动Django服务器: {python_executable}")
        print(f"Django项目路径: {django_project_dir}")
        
        # 构建命令
        cmd = [
            str(python_executable),
            "manage.py",
            "runserver"
        ]
        
        # 运行命令
        print(f"运行命令: {' '.join(cmd)}")
        process = subprocess.Popen(
            cmd,
            cwd=str(django_project_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # 实时输出日志
        print("\n== Django服务器日志 ==\n")
        try:
            for line in process.stdout:
                print(line, end='')
        except KeyboardInterrupt:
            print("\n收到中断信号，正在停止服务器...")
        finally:
            process.terminate()
            print("Django服务器已停止")
        
        return True
    
    except Exception as e:
        print(f"启动Django服务器时出错: {str(e)}")
        return False

if __name__ == "__main__":
    run_with_venv() 