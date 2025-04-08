#!/bin/bash
# Script cai dat Git hooks cho Linux/Mac

echo "Dang cai dat Git hooks..."

# Tao thu muc hooks neu chua ton tai
mkdir -p .git/hooks

# Sao chep pre-commit hook
cp -f .git/hooks/pre-commit.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
echo "Cai dat pre-commit hook thanh cong!"

echo "Hoan tat cai dat Git hooks!"
echo "Luu y: Neu ban dang su dung Windows, hay chay scripts/install_hooks.bat thay vi script nay."
