#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Простой тест Flask приложения
"""

from flask import Flask

app = Flask(__name__)
app.secret_key = 'test-secret-key-123'

@app.route('/')
def hello():
    return '<h1>Flask работает!</h1><p>Секретный ключ установлен правильно</p>'

if __name__ == '__main__':
    print("Тестирование Flask...")
    print(f"Secret key: {app.secret_key}")
    app.run(debug=True, port=5001)