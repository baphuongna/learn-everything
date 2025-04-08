@echo off
REM Script cai dat Git hooks cho Windows

echo Dang cai dat Git hooks...

REM Tao thu muc hooks neu chua ton tai
if not exist .git\hooks mkdir .git\hooks

REM Sao chep pre-commit hook
copy /Y .git\hooks\pre-commit.bat .git\hooks\pre-commit
echo Cai dat pre-commit hook thanh cong!

echo Hoan tat cai dat Git hooks!
echo Luu y: Neu ban dang su dung Git Bash, hay chay scripts/install_hooks.sh thay vi script nay.
