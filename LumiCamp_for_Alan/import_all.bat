@echo off
echo Importing vocabulary data...
call conda activate ./env
python import_data.py
python import_senior_high_data.py
echo Data import completed.
pause