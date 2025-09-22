from nicegui import ui
import requests


API_URL = "http://localhost:8000"
session = requests.Session()


def show_login():
    ui.label("🔑 Вход в MyGarden").classes("text-2xl font-bold mb-4")

    email_input = ui.input("Email").props("outlined").classes("w-64")
    password_input = ui.input("Пароль").props("outlined password reveal-password").classes("w-64")
    # password_confirm_input = ui.input("Подтвердите пароль").props("outlined password reveal-password").classes("w-64")

    def login_user():
        email = email_input.value.strip()
        password = password_input.value.strip()
        payload = {
            "email": email,
            "password": password
        }

        try:
            response = requests.post(f"{API_URL}/users/login_json", json=payload)
            if response.status_code == 200:
                token = response.json().get("access_token")
                if token:
                    # Сохраняем токен в сессии
                    session.headers.update({"Authorization": f"Bearer {token}"})
                    # print('session.headers', session.headers)
                    ui.notify("Вход успешен ✅", color="positive")
                    ui.timer(2.0, lambda: ui.navigate.to('/plants'))
                else:
                    ui.notify("Ошибка: токен не получен", color="negative")
            else:
                ui.notify(f"Ошибка: {response.json().get('detail')}", color="negative")

        except Exception as e:
            ui.notify(f"Ошибка: {e}", color="negative")

    ui.button("Войти", on_click=login_user).classes("mt-4")