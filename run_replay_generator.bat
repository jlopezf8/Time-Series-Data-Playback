@echo off
setlocal enabledelayedexpansion

:: Set the title of the command prompt window
title Time-Series Replay Generator

:: --- Step 1: Check for Python and required libraries ---
echo Checking for required software...
echo.

:: Check for Python
python --version >nul 2>nul
if %errorlevel% neq 0 (
    echo ---------------------------------------------------------------
    echo ERROR: Python is not installed or not found in your PATH.
    echo Please install Python from python.org and try again.
    echo ---------------------------------------------------------------
    echo.
    pause
    exit /b
)

:: Check for pandas library
python -c "import pandas" >nul 2>nul
if %errorlevel% neq 0 (
    echo ---------------------------------------------------------------
    echo Required library 'pandas' not found. Attempting to install...
    pip install pandas
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install pandas. Please check your internet
        echo connection or try installing it manually by running:
        echo pip install pandas
        echo ---------------------------------------------------------------
        echo.
        pause
        exit /b
    )
    echo 'pandas' installed successfully.
    echo ---------------------------------------------------------------
) else (
    echo Python and required libraries are ready.
)
echo.

:: --- Step 2: Find all .csv files in the current folder ---
echo Searching for .csv files...
echo ===================================
set "count=0"
for %%F in (*.csv) do (
    set /a count+=1
    set "file[!count!]=%%F"
    echo !count!. %%F
)

:: --- Step 3: Check if any files were found ---
if %count%==0 (
    echo No .csv files found in this folder.
    echo Please place your data files here and try again.
    echo.
    pause
    exit /b
)
echo ===================================
echo.

:: --- Step 4: Ask the user to choose a file ---
:choice
set "choice="
set /p choice="Enter the number of the file you want to process: "

:: Validate the input
if not defined choice (goto choice)
if %choice% GTR %count% (echo Invalid number. Try again.& echo.& goto choice)
if %choice% LSS 1 (echo Invalid number. Try again.& echo.& goto choice)

:: --- Step 5: Run the Python script with the chosen file ---
set "chosenFile=!file[%choice%]!"
echo.
echo Processing "!chosenFile!"...
echo.

:: Call the python script and pass the filename in quotes
python create_replay.py "%chosenFile%"

:: --- Step 6: Finish ---
echo.
echo ===================================
echo Script finished. Press any key to exit.
pause >nul
