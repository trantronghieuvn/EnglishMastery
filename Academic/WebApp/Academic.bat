@echo off
echo Dang khoi dong Hoc Tieng Anh...
start cmd /k "python -m http.server 8001"
timeout /t 2 /nobreak >nul
start chrome --incognito --use-fake-ui-for-media-stream --unsafely-treat-insecure-origin-as-secure="http://localhost:8001" "http://localhost:8001/HocTiengAnh.html"