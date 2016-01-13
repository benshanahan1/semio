@echo off

:: Build Python executable first.
python setup.py py2exe

:: Copy license and readme into dist/.
xcopy license.md dist
xcopy readme.md dist

:: Copy Max's files over (the max/ and mesh/ directories).
:: The "echo d" comes first so that xcopy knows we are copying a directory.
echo d | xcopy /e max "dist/max"
echo d | xcopy /e mesh "dist/mesh"