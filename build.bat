@echo off
pyinstaller screen.py -n "Rubiks Cube Solver" --clean -w -F -i exe_logo.ico --add-data logo.png;.
