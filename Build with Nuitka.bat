@echo off
title Request Builder PRO — Builder
cd /d "%~dp0"

echo.
echo  ============================================
echo       Request Builder PRO — NUITKA BUILD
echo       Coded by Yashvir Gaming
echo  ============================================
echo.

echo [1/3] Installing requirements...
pip install -r requirements.txt --quiet
pip install nuitka --quiet
pip install ordered-set zstandard --quiet

echo.
echo [2/3] Building EXE...
echo.

python -m nuitka main_gui.py ^
--onefile ^
--standalone ^
--windows-console-mode=disable ^
--enable-plugin=tk-inter ^
--include-package=core ^
--include-package=parsers ^
--include-package=utils ^
--include-package=ui ^
--include-data-dir=templates=templates ^
--windows-product-name="Request Builder PRO" ^
--windows-file-description="HTTP Request Builder and Checker Generator" ^
--windows-product-version=1.0.0.0 ^
--windows-file-version=1.0.0.0 ^
--jobs=4 ^
--lto=yes ^
--assume-yes-for-downloads ^
--remove-output ^
--output-filename=RequestBuilderPRO.exe

echo.
echo [3/3] Cleaning temp folders...
if exist main_gui.build    rmdir /s /q main_gui.build
if exist main_gui.dist     rmdir /s /q main_gui.dist
if exist main_gui.onefile-build rmdir /s /q main_gui.onefile-build

echo.
echo  ============================================
echo              BUILD COMPLETE
echo  ============================================
echo.
echo  Output: RequestBuilderPRO.exe
echo  Share this single file — no other files needed.
echo  Templates are bundled inside the EXE.
echo.
pause
