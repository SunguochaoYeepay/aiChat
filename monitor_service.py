#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
服务监控脚本 - 用于监控GPU服务性能并生成报告

此脚本负责监控系统性能，包括CPU、内存、GPU使用情况，并以日志文件或实时显示的方式提供监控数据。
"""
import os
import sys
import time
import datetime
import argparse
import psutil
import json
import requests
import matplotlib.pyplot as plt
from pathlib import Path

# 尝试导入GPU监控库
try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

try:
    import pynvml
    pynvml.nvmlInit()
    HAS_PYNVML = True
except (ImportError, Exception):
    HAS_PYNVML = False

# 基础路径设置
BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# 服务端点
DJANGO_ENDPOINT = "http://localhost:8000/api/status"
GPU_ENDPOINT = "http://localhost:8001/status"

class ServiceMonitor:
    """服务监控类"""
    
    def __init__(self, interval=5, log_file=None):
        """初始化监控器"""
        self.interval = interval  # 监控间隔（秒）
        self.log_file = log_file
        self.running = False
        self.data = {
            "timestamps": [],
            "cpu": [],
            "memory": [],
            "gpu_memory": [],
            "gpu_util": [],
            "django_status": [],
            "gpu_status": []
        }
    
    def get_system_metrics(self):
        """获取系统指标"""
        metrics = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "gpu_util": 0,
            "gpu_memory": 0
        }
        
        # 获取GPU指标
        if HAS_PYNVML:
            try:
                device_count = pynvml.nvmlDeviceGetCount()
                if device_count > 0:
                    handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                    info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                    metrics["gpu_memory"] = info.used / info.total * 100
                    metrics["gpu_util"] = pynvml.nvmlDeviceGetUtilizationRates(handle).gpu
            except Exception as e:
                print(f"获取GPU信息出错: {e}")
        elif HAS_TORCH and torch.cuda.is_available():
            # 使用PyTorch获取有限的GPU信息
            try:
                metrics["gpu_memory"] = torch.cuda.memory_allocated() / torch.cuda.max_memory_allocated() * 100 if torch.cuda.max_memory_allocated() > 0 else 0
            except Exception as e:
                print(f"获取GPU信息出错: {e}")
        
        return metrics
    
    def check_service_status(self):
        """检查服务状态"""
        status = {
            "django": False,
            "gpu": False
        }
        
        # 检查Django服务
        try:
            response = requests.get(DJANGO_ENDPOINT, timeout=2)
            if response.status_code == 200:
                status["django"] = True
        except Exception:
            pass
        
        # 检查GPU服务
        try:
            response = requests.get(GPU_ENDPOINT, timeout=2)
            if response.status_code == 200:
                status["gpu"] = True
        except Exception:
            pass
        
        return status
    
    def log_metrics(self, metrics, status):
        """记录指标"""
        # 添加到数据集
        self.data["timestamps"].append(metrics["timestamp"])
        self.data["cpu"].append(metrics["cpu_percent"])
        self.data["memory"].append(metrics["memory_percent"])
        self.data["gpu_memory"].append(metrics["gpu_memory"])
        self.data["gpu_util"].append(metrics["gpu_util"])
        self.data["django_status"].append(1 if status["django"] else 0)
        self.data["gpu_status"].append(1 if status["gpu"] else 0)
        
        # 格式化输出
        output = (
            f"时间: {metrics['timestamp']} | "
            f"CPU: {metrics['cpu_percent']:.1f}% | "
            f"内存: {metrics['memory_percent']:.1f}% | "
            f"GPU利用率: {metrics['gpu_util']:.1f}% | "
            f"GPU内存: {metrics['gpu_memory']:.1f}% | "
            f"Django: {'在线' if status['django'] else '离线'} | "
            f"GPU服务: {'在线' if status['gpu'] else '离线'}"
        )
        
        print(output)
        
        # 写入日志文件
        if self.log_file:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(output + "\n")
    
    def save_report(self, filename):
        """保存监控报告"""
        # 图表目录
        charts_dir = os.path.join(LOG_DIR, "charts")
        os.makedirs(charts_dir, exist_ok=True)
        
        # 绘制CPU和内存使用率
        plt.figure(figsize=(12, 6))
        plt.plot(self.data["timestamps"], self.data["cpu"], label="CPU使用率(%)")
        plt.plot(self.data["timestamps"], self.data["memory"], label="内存使用率(%)")
        if any(x > 0 for x in self.data["gpu_util"]):
            plt.plot(self.data["timestamps"], self.data["gpu_util"], label="GPU利用率(%)")
        if any(x > 0 for x in self.data["gpu_memory"]):
            plt.plot(self.data["timestamps"], self.data["gpu_memory"], label="GPU内存使用率(%)")
        plt.title("系统资源使用情况")
        plt.xlabel("时间")
        plt.ylabel("百分比(%)")
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(charts_dir, f"{filename}_resources.png"))
        
        # 绘制服务状态
        plt.figure(figsize=(12, 4))
        plt.plot(self.data["timestamps"], self.data["django_status"], label="Django服务", marker="o")
        plt.plot(self.data["timestamps"], self.data["gpu_status"], label="GPU服务", marker="o")
        plt.title("服务可用性")
        plt.xlabel("时间")
        plt.ylabel("状态 (1=在线, 0=离线)")
        plt.yticks([0, 1], ["离线", "在线"])
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(charts_dir, f"{filename}_status.png"))
        
        # 保存原始数据
        with open(os.path.join(LOG_DIR, f"{filename}_data.json"), "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        
        print(f"报告已保存到 {os.path.join(charts_dir, filename)}_*.png")
    
    def start(self, duration=None):
        """开始监控"""
        self.running = True
        start_time = time.time()
        
        print("开始监控服务...")
        try:
            while self.running:
                # 检查是否达到监控时长
                if duration and (time.time() - start_time) > duration:
                    break
                
                # 获取指标
                metrics = self.get_system_metrics()
                status = self.check_service_status()
                
                # 记录指标
                self.log_metrics(metrics, status)
                
                # 等待下一个监控间隔
                time.sleep(self.interval)
                
        except KeyboardInterrupt:
            print("\n监控已停止（用户中断）")
        
        self.running = False
        
        # 如果有足够的数据，生成报告
        if len(self.data["timestamps"]) > 1:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            self.save_report(f"report_{timestamp}")

def main():
    """主函数"""
    # 命令行参数解析
    parser = argparse.ArgumentParser(description='AI图像分析服务监控工具')
    parser.add_argument('--interval', type=int, default=5, help='监控间隔（秒）')
    parser.add_argument('--duration', type=int, help='监控持续时间（秒），不指定则持续运行')
    parser.add_argument('--log', action='store_true', help='记录到日志文件')
    
    args = parser.parse_args()
    
    # 设置日志文件
    log_file = None
    if args.log:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(LOG_DIR, f"monitor_{timestamp}.log")
    
    # 创建并启动监控器
    monitor = ServiceMonitor(interval=args.interval, log_file=log_file)
    monitor.start(duration=args.duration)

if __name__ == "__main__":
    main() 