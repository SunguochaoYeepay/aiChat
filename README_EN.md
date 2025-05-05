# Qwen-VL-Chat Service Quick Start Guide

## Quick Start (Recommended)

If you encounter Chinese character encoding issues (garbled text), please use the English version of the startup script:

1. Double-click `start_simple.bat`
2. Select a startup mode when prompted:
   - Option 1: **Quick Start** - Starts API service only, model loads on first request (slower initial response)
   - Option 2: **Full Start** - Preloads model and starts API service (recommended for best experience)
   - Option 3: Exit program

## Encoding Issues

If you see garbled text when running the Chinese scripts, this is due to character encoding issues between the batch file and Windows Command Prompt. Use the English version `start_simple.bat` to avoid this problem.

## Available Scripts

- `start_simple.bat` (New): English version of the startup script, avoids encoding issues
- `start_all_services.bat` (New): Chinese version, may display correctly after setting UTF-8 encoding
- `start_service.bat` (Original): Original startup script with potential model loading issues
- `start_api_service.bat`: Original API service script with multiple startup options
- `admin_system/start_with_chat_env.bat`: Direct Django service launcher, no model preloading

## Common Issues

1. **Model not loaded error**
   - Accessing `/api/status` returns `{"status": "stopped", "message": "模型未加载"...}`
   - Solution: Use `start_simple.bat` and select option 2 (Full Start)

2. **Service starts but API is inaccessible**
   - Ensure you're using the correct URL path: `http://localhost:8000/api/v1/chat/completions`
   - The API root path is `/api/`, not the root directory `/`

3. **Slow model loading**
   - This is normal behavior - large models take time to load, especially on first load
   - Check `model_startup.log` to monitor model loading progress

## Log Files

- `model_startup.log`: Records the model loading process, useful for troubleshooting
- Django service logs are displayed directly in the command line window

## API Endpoints

Main API endpoints:

- `/api/v1/chat/completions`: Chat completion API
- `/api/analyze`: Image analysis API
- `/api/search`: Knowledge base search API
- `/api/status`: Service status API
 