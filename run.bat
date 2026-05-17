@echo off
chcp 65001 >nul
title 水质监测智能分析系统 - 一键启动

echo ================================================
echo    水质监测智能分析系统  一键启动工具
echo ================================================
echo.

:: 切换到项目根目录
cd /d "C:\Users\93478\Desktop\水质监测"

echo [1/3] 正在检查项目路径...
echo 当前目录: %CD%
echo.

echo [2/3] 正在启动 Ollama 服务（如果未启动）...
tasklist | find "ollama" >nul
if %errorlevel% neq 0 (
    echo 正在启动 Ollama 服务...
    start "" ollama serve
    timeout /t 5 >nul
) else (
    echo ✓ Ollama 服务已在运行。
)

echo.
echo [3/3] 正在启动 Streamlit 前端界面...
echo 路径: streamlit_app\water_quality_streamlit.py
echo 请稍等，浏览器将自动打开...
echo.

:: 启动 Streamlit（已修改为你的实际路径）
streamlit run streamlit_app\water_quality_streamlit.py --server.port 8501 --server.address 127.0.0.1

pause