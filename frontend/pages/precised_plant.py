from nicegui import ui
import requests
from pages.login import session

API_URL = "http://localhost:8000"

def show_precised_plant(plant_id):
    if not session.headers.get("Authorization"):
        ui.notify("Пожалуйста, войдите в систему", color="negative")
        ui.timer(2.0, lambda: ui.navigate.to('/login'))
        return
    
    response = session.get(f"{API_URL}/user_plants/{plant_id}")

    if response.status_code == 200:
        data = response.json()
        plant = data.get("plant", [])

        species_info = plant.get("species_info", [])
        species = species_info[0] if species_info else {}
        name = species.get("name", "Unknown")
        scientific_name = species.get("scientific_name", "")
        family = species.get("family", "")
        
        date_planted = plant["date_planted"][:10]
        last_watered = plant["last_watered"][:10]
        last_fertilized = plant["last_fertilized"][:10]
        care_tips = plant.get("care_tips", "")
        growth_log = plant.get("growth_log", [])

        ui.label("🌿 Ваше растение").classes("text-2xl font-bold mb-6")

        with ui.card().classes('p-4 bg-green-50 shadow-md'):
                ui.label(name).classes("text-lg font-bold")
                ui.label(scientific_name).classes("italic text-sm text-gray-600")
                ui.label(f"Family: {family}").classes("text-sm text-gray-500 mt-1")
                
                with ui.card_section().classes("mt-4"):
                    ui.label(f"Planted: {date_planted}")
                    ui.label(f"Last watered: {last_watered}")
                    ui.label(f"Last fertilized: {last_fertilized}")
                
                if care_tips:
                    ui.label(f"Tips: {care_tips}").classes("mt-2 text-sm text-gray-700")
                
                if growth_log:
                    ui.label("Growth Log:").classes("mt-2 font-semibold")
                    for g in growth_log:
                        ui.label(f"{g['date'][:10]} — {g['height']}cm").classes("text-sm text-gray-600")

    else:
        ui.notify("Ошибка при загрузке растения", color="negative")