from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required
from models import db, Client

auth_blueprint = Blueprint('auth', __name__, template_folder='../templates/auth')

@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = Client.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            flash('Вы успешно вошли!', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Неверный email или пароль.', 'danger')
    return render_template('login.html')


@auth_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']

        if Client.query.filter_by(email=email).first():
            flash('Этот email уже зарегистрирован.', 'danger')
        else:
            user = Client(first_name=first_name, last_name=last_name, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash('Вы успешно зарегистрированы!', 'success')
            return redirect(url_for('auth.login'))
    return render_template('register.html')


@auth_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы.', 'info')
    return redirect(url_for('auth.login'))
