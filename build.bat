@echo off
chcp 65001 >nul 2>&1
title 奶龙打包工具
echo ========================================
echo   奶龙 Desktop Pet Builder
echo ========================================
echo.

echo [1/2] Building exe with PyInstaller...
C:\Users\kong\AppData\Local\Programs\Python\Python312\python -m PyInstaller --onefile --noconsole --name "NailongPet" --add-data "spritesheet.webp;." --add-data "music.mp3;." --hidden-import=PIL --hidden-import=pygame nailong_desktop_pet.py
if errorlevel 1 (
    echo Build failed!
    pause
    exit /b 1
)

echo.
echo [2/2] Build complete!
echo EXE location: dist\NailongPet.exe
echo.
pause
