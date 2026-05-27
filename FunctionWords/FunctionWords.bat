@echo off
echo Dang khoi dong Web Server...
start /min cmd /c "python -m http.server 8000"

:: Đợi 3 giây để server ổn định
timeout /t 3 /nobreak >nul

echo Dang mo Chrome...
:: Thêm cờ --disable-web-security chỉ dùng cho môi trường dev để test (Lưu ý: Không dùng khi duyệt web thông thường)
start chrome --incognito --use-fake-ui-for-media-stream --disable-web-security --user-data-dir="C:/temp-chrome-dev" --unsafely-treat-insecure-origin-as-secure="http://localhost:8000" "http://localhost:8000/FunctionWords.html"