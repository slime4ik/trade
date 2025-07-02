# 📦 Обменник — Django-приложение для обмена вещами

Это веб-приложение на Django, где пользователи могут публиковать объявления, предлагать обмен и принимать/отклонять предложения.

## 🚀 Установка

### 1. Клонируй репозиторий

```bash
git clone https://github.com/yourusername/obmennik.git
cd obmennik
```
### 2. Создай и активируй виртуальное окружение
```python
python3 -m venv env
source env/bin/activate  # Для Windows: env\Scripts\activate
```
3. Установи зависимости
```python
pip install -r requirements.txt
````
⚙️ Миграции
```python
python manage.py makemigrations
python manage.py migrate
```
👤 Создание суперпользователя (админка)
```python
python manage.py createsuperuser
```
🌐 Запуск сервера
```python
python manage.py runserver
```
Открой http://127.0.0.1:8000 в браузере.
Аутентификация только в http://127.0.0.1:8000/admin
🧪 Запуск тестов
```python
python manage.py test
```
🗃️ Стек технологий

    Django

    PostgreSQL / SQLite

    HTML, CSS (Bootstrap)
