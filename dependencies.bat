@echo off
echo Установка зависимостей для VK мигратора...
pip install --upgrade setuptools^<81
pip install natasha^>=1.6.0
pip install pymorphy2^>=0.9.1
echo Установка завершена!
pause