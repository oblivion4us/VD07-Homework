# app.py
import webbrowser
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from forms import EditProfileForm
from flask_wtf.csrf import CSRFProtect
import threading

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
csrf = CSRFProtect(app)
db = SQLAlchemy(app)


# Определение модели пользователя
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# Создание базы данных и тестового пользователя
with app.app_context():
    db.create_all()
    # Проверка и создание тестового пользователя
    if not User.query.filter_by(email="test@example.com").first():
        user = User(name="Test User", email="test@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()


# Маршрут для редактирования профиля
@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    user = User.query.filter_by(email="test@example.com").first()  # Замените на актуального пользователя
    form = EditProfileForm(obj=user)

    if form.validate_on_submit():
        user.name = form.name.data
        user.email = form.email.data

        if form.password.data:
            user.set_password(form.password.data)

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('edit_profile'))

    # Установить текущие данные пользователя в форму
    form.name.data = user.name
    form.email.data = user.email
    return render_template('edit_profile.html', form=form)


def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000/edit_profile")


if __name__ == '__main__':
    # Открываем браузер в отдельном потоке после запуска приложения
    threading.Timer(1, open_browser).start()
    # Отключаем перезагрузчик, чтобы избежать двойного запуска
    app.run(debug=True, use_reloader=False)


