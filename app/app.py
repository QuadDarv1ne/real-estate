import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

# Импорт конфигурации
from config import Config

# Инициализация приложения Flask
app = Flask(__name__)
app.config.from_object(Config)

# Инициализация базы данных
db = SQLAlchemy(app)

# Инициализация Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Импорт моделей
from models import Client, Property

# Flask-Login: загрузка пользователя
@login_manager.user_loader
def load_user(user_id):
    return Client.query.get(int(user_id))

# Главная страница
@app.route('/')
def index():
    return render_template('index.html')

# Страница каталога
@app.route('/catalog')
def catalog():
    properties = Property.query.all()
    return render_template('catalog.html', properties=properties)

# Страница контактов
@app.route('/contact')
def contact():
    return render_template('contact.html')

# Страница "О нас"
@app.route('/about')
def about():
    return render_template('about.html')

# Регистрация пользователя
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            flash('Укажите имя пользователя и пароль.', 'error')
            return redirect(url_for('register'))

        # Проверка на уникальность пользователя
        if Client.query.filter_by(username=username).first():
            flash('Пользователь с таким именем уже существует.', 'error')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        new_user = Client(username=username, password=hashed_password)
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Вы успешно зарегистрированы!', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash('Ошибка при регистрации. Попробуйте снова.', 'error')
            return render_template('register.html')
    return render_template('register.html')

# Авторизация пользователя
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = Client.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Вы вошли в систему!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Неверное имя пользователя или пароль.', 'error')
            return render_template('login.html')
    return render_template('login.html')

# Выход из системы
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы.', 'success')
    return redirect(url_for('index'))

# Запуск приложения
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Создание таблиц в базе данных
    app.run(debug=True)
