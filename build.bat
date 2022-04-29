@echo off
pyinstaller screen.py -n "Rubiks Cube Solver" --clean -w -F -i exe_logo.ico --add-data logo.png;.
move "dist\Rubiks Cube Solver.exe" "Rubiks Cube Solver.exe"
del "Rubiks Cube Solver.spec"
rmdir /S /Q build
rmdir dist
