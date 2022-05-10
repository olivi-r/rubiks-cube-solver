@echo off
pyinstaller screen.py -n "Rubiks Cube Solver" --clean -w -F -i logo.ico --add-data logo.png;. --add-data logo.ico;.
move "dist\Rubiks Cube Solver.exe" "Rubiks Cube Solver.exe"
del "Rubiks Cube Solver.spec"
rmdir /S /Q build
rmdir dist
