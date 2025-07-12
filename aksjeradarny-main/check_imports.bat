@echo off
echo Running import check...
python check_imports.py > import_check_results.txt
echo Results saved to import_check_results.txt
type import_check_results.txt
