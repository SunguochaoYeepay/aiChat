@echo off
echo ================================================================================
echo            安装项目依赖
echo ================================================================================

REM 激活虚拟环境
call ..\..\chat_env\Scripts\activate.bat

echo 正在安装基本依赖...
pip install -r ..\..\requirements.txt

echo 正在安装向量搜索依赖...
pip install sentence-transformers faiss-cpu

echo 正在更新pip...
python -m pip install --upgrade pip

echo ================================================================================
echo 依赖安装完成！现在可以启动API服务了。
echo ================================================================================
pause 