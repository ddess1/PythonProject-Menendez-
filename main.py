from flask import Flask, render_template, request, redirect, url_for, redirect, make_response, render_template
import requests
from datetime import datetime

from auth import get_current_user
from models import User

# URL FastAPI
FASTAPI_URL = "http://127.0.0.1:8000/api/"

# Инициализация Flask-приложения
flask_app = Flask(__name__)

@flask_app.route("/", methods=["GET", "POST"])
def index():
    user_data = None
    cars_data = []
    message = ""

    if request.method == "POST":
        user_id = request.form.get("user_id")

        if user_id:
            try:
                # Отправляем запрос к FastAPI для получения данных пользователя
                response = requests.get(f"http://127.0.0.1:8000/api/users/{user_id}")
                if response.status_code == 200:
                    user_data = response.json()
                    if "message" in user_data:
                        message = user_data["message"]
                else:
                    message = "Ошибка при запросе данных."
            except Exception as e:
                message = f"Ошибка соединения: {e}"

    # Запрос к FastAPI для получения списка машин
    try:
        cars_response = requests.get("http://127.0.0.1:8000/cars/")
        if cars_response.status_code == 200:
            cars_data = cars_response.json()
        else:
            message = "Ошибка при запросе списка машин."
    except Exception as e:
        message = f"Ошибка соединения с сервером машин: {e}"

    return render_template("index.html", user_data=user_data, message=message, cars_data=cars_data)


@flask_app.route("/download/<int:car_id>")
def redirect_to_fastapi_download(car_id):
    return redirect(f"http://127.0.0.1:8000/download/{car_id}")

@flask_app.route("/register", methods=["GET", "POST"])
def register():
    message = "Register"
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        # Собираем данные в формате JSON
        data = {"name": name, "email": email, "password": password}

        # Отправляем запрос с JSON-данными
        response = requests.post("http://127.0.0.1:8000/api/register/", json=data)
        if response.status_code == 200:
            return redirect(url_for("login"))
        else:
            message = response.json().get("detail", "An error occurred")

    return render_template("register.html", message=message)


from flask import redirect, make_response


@flask_app.route("/login", methods=["GET", "POST"])
def login():
    message = "login br"
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        data = {"email": email, "password": password}

        response = requests.post(f"http://127.0.0.1:8000/api/login/", json=data)
        if response.status_code == 200:
            response_data = response.json()
            access_token = response_data.get("access_token")  # Получаем токен
            if access_token:
                # Проверяем статус пользователя
                user_info_response = requests.get(
                    "http://127.0.0.1:8000/profile",
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                if user_info_response.status_code == 200:
                    user_info = user_info_response.json()
                    if user_info.get("role") == "admin":  # Проверяем, является ли пользователь админом
                        resp = make_response(redirect("/admin_page"))
                    else:
                        resp = make_response(redirect("/profile_page"))

                    resp.set_cookie("access_token", access_token, httponly=True)  # Сохраняем токен в cookie
                    return resp
                else:
                    message = "Failed to fetch user information."
            else:
                message = "Access token not found in response."
        else:
            message = response.json().get("detail", "An error occurred")

    return render_template("login.html", message=message)


#eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJleHAiOjE3MzE4NzU5MzZ9.MTPur-R54qzPWN_u4E_n3Y4CoSgdLD0Ex7FfpRV3xhY
#eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoyLCJleHAiOjE3MzE4NzYwMjd9.EC5yJVcVVGKLsD-CASiEC4BPmmuwnguqTzlst29cg5A




from fastapi.templating import Jinja2Templates
from fastapi import Request, Depends

templates = Jinja2Templates(directory="templates")

@flask_app.get("/profile_page")
def profile_page():
    # Получаем токен из cookie
    access_token = request.cookies.get("access_token")
    if not access_token:
        return redirect("/login")  # Если токена нет, перенаправляем на страницу логина

    # Получаем информацию о пользователе с FastAPI
    response = requests.get(
        "http://127.0.0.1:8000/profile",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    if response.status_code == 200:
        user_data = response.json()  # Данные о пользователе из FastAPI
        return render_template("profile.html", user=user_data)  # Передаем данные о пользователе в шаблон
    else:
        return redirect("/login")  # Если не удалось получить данные о пользователе, редиректим на страницу логина
from flask import request, redirect, render_template

@flask_app.route("/delete_profile", methods=["POST"])
def delete_profile_page():
    access_token = request.cookies.get("access_token")
    response = requests.delete(
        "http://127.0.0.1:8000/profile",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    if response.status_code == 200:
        return render_template("register.html", message="Profile deleted successfully!")
    else:
        return render_template("profile.html", message=response.json().get("detail", "Error occurred"))

@flask_app.route("/edit_profile", methods=["GET", "POST"])
def edit_profile_page():
    message = ""
    if request.method == "POST":
        data = {
            "name": request.form.get("name"),
            "email": request.form.get("email"),
            "password": request.form.get("password")
        }
        response = requests.put(
            "http://127.0.0.1:8000/profile",
            json=data,
            headers={"Authorization": f"Bearer {request.cookies.get('access_token')}"}
        )
        if response.status_code == 200:
            return redirect("/profile_page")
        else:
            message = response.json().get("detail", "Error occurred")
    return render_template("edit_profile.html", message=message)





#eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJleHAiOjE3MzE4NzU5MzZ9.MTPur-R54qzPWN_u4E_n3Y4CoSgdLD0Ex7FfpRV3xhY
#eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoyLCJleHAiOjE3MzE4NzYwMjd9.EC5yJVcVVGKLsD-CASiEC4BPmmuwnguqTzlst29cg5A
@flask_app.route("/car/<int:car_id>", methods=["GET"])
def about_car(car_id):
    car_data = {}
    message = ""

    try:
        response = requests.get(f"http://127.0.0.1:8000/cars/{car_id}")
        if response.status_code == 200:
            car_data = response.json()
            # Преобразование времени в нужный формат
            created_at = datetime.strptime(car_data['created_at'], "%Y-%m-%dT%H:%M:%S")
            car_data['created_at'] = created_at.strftime("%B %d, %Y at %H:%M")
        else:
            message = "Ошибка при запросе данных о машине."
    except Exception as e:
        message = f"Ошибка соединения с сервером: {e}"

    return render_template("about_car.html", car_data=car_data, message=message)


if __name__ == "__main__":
    flask_app.run(debug=True, port=5000)
