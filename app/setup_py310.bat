@echo off
echo This script will download and install Python 3.10 for your project

echo Step 1: Downloading Python 3.10...
curl -o python310.exe https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe

echo Step 2: Installing Python 3.10 (will take a few minutes)...
python310.exe /quiet InstallAllUsers=0 PrependPath=0 Include_test=0 TargetDir=%CD%\python310

echo Step 3: Creating a virtual environment...
%CD%\python310\python.exe -m venv venv_py310

echo Step 4: Activating the virtual environment and installing packages...
call venv_py310\Scripts\activate.bat && pip install -r requirements.txt

echo Setup complete! 
echo To run your application, use:
echo call venv_py310\Scripts\activate.bat
echo python run.py
