from nicegui import ui
import requests
from pages.login import session

API_URL = "http://localhost:8000"

def show_plants():
    if not session.headers.get("Authorization"):
        ui.notify("Пожалуйста, войдите в систему", color="negative")
        ui.timer(2.0, lambda: ui.navigate.to('/login'))
        return
    
    response = session.get(f"{API_URL}/user_plants")

    if response.status_code == 200:
        data = response.json()
        plants = data.get("plants", [])

        ui.label("🌿 Ваши растения").classes("text-2xl font-bold mb-6")

        with ui.element('div').classes('grid grid-cols-3 gap-4'):
            for plant in plants:
                plant_id = plant["_id"]
                species = plant["species_info"][0] if plant["species_info"] else {}
                name = species.get("name", "Unknown")
                scientific_name = species.get("scientific_name", "")
                family = species.get("family", "")
                
                date_planted = plant["date_planted"][:10]
                last_watered = plant["last_watered"][:10]
                last_fertilized = plant["last_fertilized"][:10]

                # care_tips = plant.get("care_tips", "")
                # growth_log = plant.get("growth_log", [])

                with ui.card().classes('p-4 bg-green-50 shadow-md rounded-lg w-80 hover:shadow-lg cursor-pointer') \
                        .on('click', lambda e, pid=plant_id: ui.navigate.to(f'/plants/{pid}')):
                    
                    # Name
                    with ui.row().classes("items-baseline"):
                        ui.label("Name:").classes("font-semibold text-gray-700 mr-2")
                        ui.label(name).classes("text-lg font-bold text-green-900")
                    
                    # Scientific name
                    with ui.row().classes("items-baseline mt-1"):
                        ui.label("Scientific name:").classes("font-semibold text-gray-700 mr-2")
                        ui.label(scientific_name).classes("italic text-sm text-gray-600")
                    
                    # Family
                    with ui.row().classes("items-baseline mt-1"):
                        ui.label("Family:").classes("font-semibold text-gray-700 mr-2")
                        ui.label(family).classes("text-sm text-gray-500")
                    
                    with ui.card_section().classes("mt-4 border-t pt-2"):
                        with ui.row().classes("items-baseline"):
                            ui.label("Planted:").classes("font-semibold text-gray-700 mr-2")
                            ui.label(date_planted).classes("text-sm text-gray-600")
                        
                        with ui.row().classes("items-baseline"):
                            ui.label("Last watered:").classes("font-semibold text-gray-700 mr-2")
                            ui.label(last_watered).classes("text-sm text-gray-600")
                        
                        with ui.row().classes("items-baseline"):
                            ui.label("Last fertilized:").classes("font-semibold text-gray-700 mr-2")
                            ui.label(last_fertilized).classes("text-sm text-gray-600")

    else:
        ui.notify("Ошибка при загрузке растений", color="negative")