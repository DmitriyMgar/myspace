"""
Точка входа для WSGI-серверов
"""
from app import create_app

application = create_app()

if __name__ == '__main__':
    application.run() 