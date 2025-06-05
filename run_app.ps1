$env:MONGO_URI = "mongodb://localhost:27017/cyberblog"
$env:FLASK_ENV = "development"
$env:SECRET_KEY = "cyberblog_secret_key"
$env:DEBUG = "True"
$env:MONGO_CLIENT = "mongodb://localhost:27017/cyberblog"

Write-Host "Запуск приложения КиберБлог..."
.\.venv\Scripts\python app.py 