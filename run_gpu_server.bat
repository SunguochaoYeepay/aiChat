@echo off
chcp 65001
echo ==========================================
echo 正在启动AI图像分析服务器(GPU版本)...
echo ==========================================
echo 时间: %date% %time%
echo 系统: %OS%
echo 目录: %CD%

echo.
echo 检查GPU可用性...
python -c "import torch; print(f'CUDA可用: {torch.cuda.is_available()}'); print(f'GPU设备: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"无\"}')"

echo.
echo 开始启动服务器...
echo 日志将保存到 gpu_server_log.txt
echo.
echo 请稍候几分钟，模型加载可能需要一些时间...

python gpu_model_server.py > gpu_server_log.txt 2>&1

echo.
echo 如果服务器无法启动，请查看gpu_server_log.txt了解详情
pause 