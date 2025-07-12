@echo off
echo Creating a new virtual environment...
python -m venv venv_compatible
call venv_compatible\Scripts\activate.bat

echo Installing compatible packages...
pip install -r compatible_requirements.txt

echo Setup complete! Now you can run the application.
echo Run: venv_compatible\Scripts\activate.bat
echo Then: python run.py
