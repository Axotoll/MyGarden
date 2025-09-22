from nicegui import ui
import requests

API_URL = "http://localhost:8000"

def show_register():
    ui.label("📝 Регистрация в MyGarden").classes("text-2xl font-bold mb-4")

    username_input = ui.input("Имя пользователя").props("outlined").classes("w-64")
    email_input = ui.input("Email").props("outlined").classes("w-64")
    password_input = ui.input("Пароль").props("outlined password reveal-password").classes("w-64")
    password_confirm_input = ui.input("Подтвердите пароль").props("outlined password reveal-password").classes("w-64")

    def register_user():
        username = username_input.value.strip()
        email = email_input.value.strip()
        password = password_input.value.strip()
        password_confirm = password_confirm_input.value.strip()

        if password != password_confirm:
            ui.notify("Пароли не совпадают ❌", color="negative")
            return

        payload = {
            "username": username,
            "email": email,
            "password": password
        }

        try:
            response = requests.post(f"{API_URL}/users/register", json=payload)
            if response.status_code == 201:
                ui.notify("Регистрация успешна ✅", color="positive")

                ui.timer(2.0, lambda: ui.navigate.to('/login'))

            else:
                # выводим сообщение ошибки от FastAPI
                ui.notify(f"Ошибка: {response.json().get('detail')}", color="negative")
        except Exception as e:
            ui.notify(f"Ошибка: {e}", color="negative")

    ui.button("Зарегистрироваться", on_click=register_user).classes("mt-4")