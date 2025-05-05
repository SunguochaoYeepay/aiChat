@echo off
echo 正在使用chat_env环境启动Django服务...

cd %~dp0
cd ..

call chat_env\Scripts\activate.bat

echo 正在检查CUDA可用性...
python -c "import torch; print('CUDA可用:', torch.cuda.is_available())"

echo 启动Django服务器...
cd admin_system
python manage.py runserver 0.0.0.0:8000

pause 