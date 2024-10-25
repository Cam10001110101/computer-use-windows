@echo off
:: Initialize conda for batch
IF EXIST "%ProgramData%\anaconda3\Scripts\activate.bat" (
    CALL "%ProgramData%\anaconda3\Scripts\activate.bat"
) ELSE (
    CALL "%USERPROFILE%\anaconda3\Scripts\activate.bat"
)

:: Activate the environment
CALL conda activate computer_use

:: Set PYTHONPATH
SET PYTHONPATH=.

:: Run the app
python -m streamlit run computer_use_demo/streamlit.py
pause
