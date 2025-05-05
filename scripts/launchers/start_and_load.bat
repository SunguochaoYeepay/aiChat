@echo off
echo ==========================================
echo    启动服务并加载模型
echo ==========================================
echo.

REM 设置工作目录
cd /d %~dp0

REM 激活虚拟环境
call chat_env\Scripts\activate.bat

echo 启动服务...
echo.

REM 在后台启动Django服务
start cmd /c "cd admin_system && python manage.py runserver 0.0.0.0:8000 --settings=admin_system.minimal_settings"

echo 服务启动中，等待几秒...
timeout /t 5 /nobreak > nul

echo 发送测试请求触发模型加载...
python -c "import requests; import json; print('正在发送请求...'); response = requests.post('http://127.0.0.1:8000/api/v1/chat/completions', json={'messages': [{'role': 'user', 'content': '你好'}]}); print('请求已发送，模型正在加载中...'); print(f'状态码: {response.status_code}'); print('等待10秒...'); import time; time.sleep(10); status = requests.get('http://127.0.0.1:8000/api/status').json(); print(f'服务状态: {json.dumps(status, ensure_ascii=False)}');"

echo.
echo 服务已启动，模型已触发加载。
echo API服务地址: http://localhost:8000/api/v1/chat/completions
echo 状态API地址: http://localhost:8000/api/status
echo.
echo 按任意键结束此窗口，服务将在后台继续运行...
pause 