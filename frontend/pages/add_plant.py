from nicegui import ui
import requests
from pages.login import session

API_URL = "http://localhost:8000"

def show_add_plant():
    if not session.headers.get("Authorization"):
        ui.notify("Пожалуйста, войдите в систему", color="negative")
        ui.timer(2.0, lambda: ui.navigate.to('/login'))
        return
    
    ui.label("Добавление растения").classes("text-2xl font-bold mb-6")
    '''
    {
        "species_id": "string",
        "date_planted": "2025-09-23T09:16:44.605Z",
        "last_watered": "2025-09-23T09:16:44.605Z",
        "last_fertilized": "2025-09-23T09:16:44.605Z",
        "growth_log": [],
        "care_tips": "string"
    }
    '''
    species_id_input = ui.input("ID вида").props("outlined").classes("w-64")

    with ui.input('Дата посадки') as date_planted_input:
        with ui.menu().props('no-parent-event') as menu:
            with ui.date().bind_value(date_planted_input):
                with ui.row().classes('justify-end'):
                    ui.button('Close', on_click=menu.close).props('flat')
        with date_planted_input.add_slot('append'):
            ui.icon('edit_calendar').on('click', menu.open).classes('cursor-pointer')
    
    with ui.input('Последнее полив') as last_watered_input:
        with ui.menu().props('no-parent-event') as menu:
            with ui.date().bind_value(last_watered_input):
                with ui.row().classes('justify-end'):
                    ui.button('Close', on_click=menu.close).props('flat')
        with last_watered_input.add_slot('append'):
            ui.icon('edit_calendar').on('click', menu.open).classes('cursor-pointer')

    with ui.input('Последнее удобрение') as last_fertilized_input:
        with ui.menu().props('no-parent-event') as menu:
            with ui.date().bind_value(last_fertilized_input):
                with ui.row().classes('justify-end'):
                    ui.button('Close', on_click=menu.close).props('flat')
        with last_fertilized_input.add_slot('append'):
            ui.icon('edit_calendar').on('click', menu.open).classes('cursor-pointer')
    # date_planted_input = ui.date("Дата посадки").props("outlined").classes("w-64")
    # last_watered_input = ui.date("Последнее полив").props("outlined").classes("w-64")
    # last_fertilized_input = ui.date("Последнее удобрение").props("outlined").classes("w-64")


    def add_plant():
        species_id = species_id_input.value.strip()
        date_planted = date_planted_input.value.strip()
        last_watered = last_watered_input.value.strip()
        last_fertilized = last_fertilized_input.value.strip()
        payload = {
            "species_id": species_id,
            "date_planted": date_planted,
            "last_watered": last_watered,
            "last_fertilized": last_fertilized,
            "growth_log": [],
            "care_tips": ""
        }
        try:
            response = session.post(f"{API_URL}/user_plants", json=payload)
            if response.status_code == 200 or response.status_code == 201:
                ui.notify("Растение добавлено ✅", color="positive")
                ui.timer(2.0, lambda: ui.navigate.to('/plants'))
            else:
                ui.notify(f"Ошибка: {response.json().get('detail')}", color="negative")
        except Exception as e:
            ui.notify(f"Ошибка: {e}", color="negative")
    
    ui.button("Добавить растение", on_click=add_plant).classes("mt-4")

