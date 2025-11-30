@echo off
echo ================================
echo Email Productivity Agent Setup
echo ================================
echo.

echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Checking .env file...
if exist .env (
    echo .env file found!
) else (
    echo WARNING: .env file not found!
    echo Please create a .env file with your GEMINI_API_KEY
)

echo.
echo Loading mock email data...
python load_mock_data.py

echo.
echo ================================
echo Setup complete!
echo ================================
echo.
echo To run the application:
echo   streamlit run app.py
echo.
pause

