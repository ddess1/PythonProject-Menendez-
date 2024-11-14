from jinja2 import Template
from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///luxury_cars.db'  # Название базы данных
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Модели базы данных

class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Car {self.name}>'


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.username}>'


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    car = db.relationship('Car', backref=db.backref('orders', lazy=True))
    user = db.relationship('User', backref=db.backref('orders', lazy=True))

    def __repr__(self):
        return f'<Order {self.id} for {self.car.name}>'


# Маршруты для страниц

@app.route('/')
def home():
     # Получаем все автомобили для отображения на главной
    return render_template('home.html')


@app.route('/car/<int:id>')
def car_detail(id):
    car = Car.query.get_or_404(id)  # Получаем детали автомобиля по id
    return render_template('car_detail.html', car=car)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        user = User(username=username, email=email, password=password)

        try:
            db.session.add(user)
            db.session.commit()
            return redirect('/login')  # После регистрации перенаправляем на страницу входа
        except:
            return "Error during registration"
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email, password=password).first()

        if user:
            return redirect('/')  # Перенаправляем на главную страницу после входа
        else:
            return "Invalid credentials, please try again"
    return render_template('login.html')


@app.route('/add_car', methods=['GET', 'POST'])
def add_car():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        image_url = request.form['image_url']

        car = Car(name=name, description=description, price=price, image_url=image_url)

        try:
            db.session.add(car)
            db.session.commit()
            return redirect('/')  # После добавления автомобиля перенаправляем на главную
        except:
            return "Error adding car"
    return render_template('add_car.html')


@app.route('/admin')
def admin_panel():
    cars = Car.query.all()
    users = User.query.all()
    return render_template('admin.html', cars=cars, users=users)


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/cars_info')
def cars_info():
    return render_template('cars_info.html')

@app.route('/cart')
def cart():
    # Для упрощения предположим, что мы отображаем только заказанные автомобили
    # Реализовать корзину можно будет позже с использованием сессий или дополнительной модели
    return render_template('cart.html')


# Запуск приложения
if __name__ == '__main__':
    app.run(debug=True)
