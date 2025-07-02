# 📦 Обменник — Django-приложение для обмена вещами

Это веб-приложение на Django, где пользователи могут публиковать объявления, предлагать обмен и принимать/отклонять предложения.

## 🚀 Установка

### 1. Клонируй репозиторий

```bash
git clone https://github.com/yourusername/obmennik.git
cd obmennik

2. Создай и активируй виртуальное окружение

python3 -m venv env
source env/bin/activate  # Для Windows: env\Scripts\activate

3. Установи зависимости

pip install -r requirements.txt

⚙️ Миграции

python manage.py makemigrations
python manage.py migrate

👤 Создание суперпользователя (админка)

python manage.py createsuperuser

🌐 Запуск сервера

python manage.py runserver

Открой http://127.0.0.1:8000 в браузере.
🧪 Запуск тестов

python manage.py test

🗃️ Стек технологий

    Django

    PostgreSQL / SQLite

    HTML, CSS (Bootstrap)
