@echo off

:: Check if Python is installed
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Python not found. Please download and install Python from https://www.python.org/downloads/
    echo Ensure you check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

:: Verify Python version
python --version

:: Delete existing virtual environment if it exists
if exist "venv" (
    echo Deleting existing virtual environment...
    rmdir /s /q venv
)

:: Create virtual environment
echo Creating virtual environment...
python -m venv venv
if %ERRORLEVEL% neq 0 (
    echo Failed to create virtual environment. Ensure the 'venv' module is available.
    pause
    exit /b 1
)

:: Activate virtual environment
call venv\Scripts\activate
if %ERRORLEVEL% neq 0 (
    echo Failed to activate virtual environment. Check if venv\Scripts\activate exists.
    pause
    exit /b 1
)

:: Upgrade pip
pip install --upgrade pip

:: Install dependencies
echo Installing dependencies...
pip install flask flask-cors python-docx==1.1.2 PyPDF2 nltk scikit-learn requests beautifulsoup4 gunicorn
if %ERRORLEVEL% neq 0 (
    echo Failed to install dependencies. Check your internet connection or pip configuration.
    pause
    exit /b 1
)

:: Download NLTK data
echo Downloading NLTK data...
python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True)"

:: Run the Flask app
echo Starting Flask server...
python app.py
if %ERRORLEVEL% neq 0 (
    echo Failed to start Flask server. Check for errors in app.py or dependencies.
    pause
    exit /b 1
)
echo Flask server started. Press Ctrl+C to stop, then type 'Y' to terminate the batch job.
pause