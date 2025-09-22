from nicegui import ui
from pages import register, login, plants, precised_plant
from pages.login import session
def show_header():
    with ui.header().classes('bg-green-600 text-white h-14 flex items-center px-4 shadow-md'):
        ui.label("🌿 MyGarden").classes("font-bold text-lg mr-8")
        
        # Навигация
        ui.button("My Plants", on_click=lambda: ui.navigate.to('/plants')).classes("mx-2")

        # Справа: логин / логаут
        with ui.row().classes("ml-auto"):
            if session.headers.get("Authorization"):
                ui.button("Logout", on_click=logout).classes("mx-2")
            else:
                ui.button("Register", on_click=lambda: ui.navigate.to('/register')).classes("mx-2")
                ui.button("Login", on_click=lambda: ui.navigate.to('/login')).classes("mx-2")

def logout():
    session.headers.pop("Authorization", None)
    ui.notify("Вы вышли из системы", color="positive")
    ui.timer(2.0, lambda: ui.navigate.to('/login'))
    


# ----- Страницы -----
@ui.page('/')
def home():
    show_header()
    ui.label("Добро пожаловать в MyGarden!").classes("mt-20 text-2xl")  # mt-20 чтобы не перекрывалось меню


@ui.page('/register')
def register_page():
    show_header()
    register.show_register()

@ui.page('/login')
def login_page():
    show_header()
    login.show_login()

@ui.page('/plants')
def plants_page():
    show_header()
    plants.show_plants()

@ui.page('/plants/{plant_id}')
def plant_detail_page(plant_id: str):
    show_header()
    precised_plant.show_precised_plant(plant_id)


# ---------- Запуск ----------
ui.run(port=8081, title="MyGarden 🌿")