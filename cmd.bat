@echo off

REM Create the main directory
mkdir DataTalk
cd DataTalk

REM Create the core directory and files
mkdir core
cd core
echo. > __init__.py
echo. > connection.py
echo. > execution.py
echo. > llm.py
echo. > utils.py
echo. > visualization.py
cd ..

REM Create the ui directory and files
mkdir ui
cd ui
echo. > __init__.py
echo. > connection_page.py
echo. > query_interface.py
cd ..

REM Create the main app.py file
echo. > app.py

REM Create requirements.txt (add dependencies later)
echo. > requirements.txt

echo Directory structure created successfully:
tree /f  
REM (The /f option displays the files in each directory)

cd ..