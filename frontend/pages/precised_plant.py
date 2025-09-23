from nicegui import ui
from pages.login import session
import requests

API_URL = "http://localhost:8000"
def delete_growth_entry(plant_id, entry_id):
    if not session.headers.get("Authorization"):
        ui.notify("Пожалуйста, войдите в систему", color="negative")
        ui.timer(2.0, lambda: ui.navigate.to('/login'))
        return
    
    try:
        response = session.delete(f"{API_URL}/user_plants/{plant_id}/growth/{entry_id}")
        if response.status_code == 200 or response.status_code == 201:
            ui.notify("Запись удалена ✅", color="positive")
            ui.timer(2.0, lambda: ui.navigate.to(f'/plants/{plant_id}'))
        else:
            ui.notify(f"Ошибка: {response.json().get('detail')}", color="negative")
    except Exception as e:
        ui.notify(f"Ошибка: {e}", color="negative")

def delete_plant(plant_id):
    if not session.headers.get("Authorization"):
        ui.notify("Пожалуйста, войдите в систему", color="negative")
        ui.timer(2.0, lambda: ui.navigate.to('/login'))
        return
    
    try:
        response = session.delete(f"{API_URL}/user_plants/{plant_id}")
        if response.status_code == 200 or response.status_code == 201:
            ui.notify("Растение удалено ✅", color="positive")
            ui.timer(2.0, lambda: ui.navigate.to('/plants'))
        else:
            ui.notify(f"Ошибка: {response.json().get('detail')}", color="negative")
    except Exception as e:
        ui.notify(f"Ошибка: {e}", color="negative")

def update_plant(plant_id):
    '''
    {
        "date": "2025-09-23T12:22:32.904Z",
        "height": 0,
        "photo_url": "string",
        "notes": "string"
    }'''
    if not session.headers.get("Authorization"):
        ui.notify("Пожалуйста, войдите в систему", color="negative")
        ui.timer(2.0, lambda: ui.navigate.to('/login'))
        return
    
    with ui.dialog() as dialog, ui.card():
        ui.label("Обновить растение").classes("text-lg font-bold mb-2")

        date = ui.date("Дата").props("outlined").classes("w-64")
        height = ui.number("Высота").props("outlined").classes("w-64")
        photo_url = ui.input("URL фото").props("outlined").classes("w-64")
        notes = ui.textarea("Примечания").props("outlined").classes("w-64")

        def submit():
            payload = {
                "date": date.value,
                "height": height.value,
                "photo_url": photo_url.value,
                "notes": notes.value
            }
            try:
                response = session.post(f"{API_URL}/user_plants/{plant_id}/growth", json=payload)
                if response.status_code in [200, 201]:
                    ui.notify("Растение обновлено ✅", color="positive")
                    dialog.close()
                    ui.timer(2.0, lambda: ui.navigate.to(f'/plants/{plant_id}'))
                else:
                    ui.notify(f"Ошибка: {response.json().get('detail')}", color="negative")
            except Exception as e:
                ui.notify(f"Ошибка: {e}", color="negative")

        ui.button("Сохранить", on_click=submit).classes("mt-2 bg-blue-500 text-white hover:bg-blue-600")
        ui.button("Отмена", on_click=dialog.close).classes("mt-2 ml-2 bg-gray-300 hover:bg-gray-400")

    dialog.open()

def show_precised_plant(plant_id: str):
    if not session.headers.get("Authorization"):
        ui.notify("Пожалуйста, войдите в систему", color="negative")
        ui.timer(2.0, lambda: ui.navigate.to('/login'))
        return

    response = session.get(f"{API_URL}/user_plants/{plant_id}")

    if response.status_code != 200:
        ui.notify("Ошибка при загрузке растения", color="negative")
        return

    data = response.json()
    plant = data.get("plant", {})

    species_info = plant.get("species_info", [])
    species = species_info[0] if species_info else {}
    name = species.get("name", "Unknown")
    scientific_name = species.get("scientific_name", "")
    family = species.get("family", "")
    
    date_planted = plant.get("date_planted", "")[:10]
    last_watered = plant.get("last_watered", "")[:10]
    last_fertilized = plant.get("last_fertilized", "")[:10]
    care_tips = plant.get("care_tips", "")
    growth_log = plant.get("growth_log", [])


    # Page title
    ui.label(f"🌿 {name}").classes("text-3xl font-extrabold mb-6")

    # Main card
    with ui.card().classes("p-6 bg-white shadow-lg rounded-lg w-full max-w-4xl mx-auto"):
        # Basic Info
        with ui.row().classes("mb-4 items-center"):
            ui.label("Scientific Name:").classes("font-semibold text-gray-700 w-40")
            ui.label(scientific_name).classes("text-gray-600")
        with ui.row().classes("mb-4 items-center"):
            ui.label("Family:").classes("font-semibold text-gray-700 w-40")
            ui.label(family).classes("text-gray-600")
        with ui.row().classes("mb-4 items-center"):
            ui.label("Planted:").classes("font-semibold text-gray-700 w-40")
            ui.label(date_planted).classes("text-gray-600")
        with ui.row().classes("mb-4 items-center"):
            ui.label("Last Watered:").classes("font-semibold text-gray-700 w-40")
            ui.label(last_watered).classes("text-gray-600")
        with ui.row().classes("mb-4 items-center"):
            ui.label("Last Fertilized:").classes("font-semibold text-gray-700 w-40")
            ui.label(last_fertilized).classes("text-gray-600")
        
        if care_tips:
            ui.label("Care Tips:").classes("mt-4 font-semibold text-gray-700")
            ui.label(care_tips).classes("text-gray-600 mb-4")
        else:
            ui.label("No care tips available").classes("text-gray-600 mb-4")

        # Growth log table
        # Growth log table
    if growth_log:
        ui.label("Growth Log:").classes("mt-4 mb-2 font-semibold text-gray-700")

        # add empty 'actions' field for the button
        rows = [
            {
                "_id_growth": g.get("_id_growth", ""),
                "date": g.get("date", "")[:10],
                "height": g.get("height", ""),
                "photo_url": g.get("photo_url", ""),
                "notes": g.get("notes", ""),
                "actions": ""  # placeholder for button
            }
            for g in growth_log
        ]

        columns = [
            {"name": "date", "label": "Date", "field": "date"},
            {"name": "height", "label": "Height (cm)", "field": "height"},
            {"name": "photo_url", "label": "Photo URL", "field": "photo_url"},
            {"name": "notes", "label": "Notes", "field": "notes"},
            {"name": "actions", "label": "Actions", "field": "actions"},
        ]
        
        ui.table(rows=rows, columns=columns, row_key="date").classes("mb-4")
        

    else:
        ui.label("No growth log available").classes("text-gray-600 mb-4")



    # Optional: Add some modern spacing
    ui.label("").classes("mb-6")