from fastapi import APIRouter, HTTPException, Query, Depends
from pymongo.errors import PyMongoError
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime


from app.db.mongo import plants_collection, users_collection
from app.models.plant import Plant, GrowthEntry, PlantCreate
from app.auth.oauth2 import get_current_user

router = APIRouter()


################################### GET ###################################

#DONE
# GET /plants → список всех растений
@router.get("/")
async def get_plants_list(current_user=Depends(get_current_user)):
    try:
        pipeline = [
            { 
                "$match": { "user_id": current_user.id }  
            },
            {
                "$lookup": {
                    "from": "species",
                    "let": { "speciesIdStr": "$species_id" },
                    "pipeline": [
                        {
                            "$match": {
                                "$expr": {
                                    "$eq": [
                                        "$_id",
                                        { "$convert": { "input": "$$speciesIdStr", "to": "objectId", "onError": None, "onNull": None } }
                                    ]
                                }
                            }
                        }
                    ],
                    "as": "species_info"
                }
            }
        ]

        plants = list(plants_collection.aggregate(pipeline))

        # конвертируем _id в строку
        for plant in plants:
            plant["_id"] = str(plant["_id"])
            #need to convert "_id" from species_info as well
            if "species_info" in plant and plant["species_info"]:
                for species in plant["species_info"]:
                    species["_id"] = str(species["_id"])
            if "growth_log" in plant and plant["growth_log"]:
                for entry in plant["growth_log"]:
                    entry["_id_growth"] = str(entry["_id_growth"])

        return {"plants": plants}

    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

#DONE
# GET /plants/{id} → одно растение пользователя
@router.get("/{id}")
async def get_single_user_plant(id: str, current_user=Depends(get_current_user)):
    try:
        object_id = ObjectId(id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    if not plants_collection.find_one({"_id": id, "user_id": current_user.id}):
        raise HTTPException(status_code=403, detail="Forbidden")
    pipeline = [
            { 
                "$match": { "_id": id }  
            },
            {
                "$lookup": {
                    "from": "species",
                    "let": { "speciesIdStr": "$species_id" },
                    "pipeline": [
                        {
                            "$match": {
                                "$expr": {
                                    "$eq": [
                                        "$_id",
                                        { "$convert": { "input": "$$speciesIdStr", "to": "objectId", "onError": None, "onNull": None } }
                                    ]
                                }
                            }
                        }
                    ],
                    "as": "species_info"
                }
            }
        ]
    plants = list(plants_collection.aggregate(pipeline))
    # plant = plants_collection.find_one({"_id": object_id})
    for plant in plants:
            plant["_id"] = str(plant["_id"])
            #need to convert "_id" from species_info as well
            if "species_info" in plant and plant["species_info"]:
                for species in plant["species_info"]:
                    species["_id"] = str(species["_id"])
            if "growth_log" in plant and plant["growth_log"]:
                for entry in plant["growth_log"]:
                    entry["_id_growth"] = str(entry["_id_growth"])

    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")

    # plant["_id"] = str(plant["_id"])
    return {"plant": plant}


#DONE
# GET /plants/{id}/growth → история роста пользователя
@router.get("/{id}/growth")
async def get_growth_entry(id: str, current_user=Depends(get_current_user)):
    try:
        object_id = ObjectId(id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    if not plants_collection.find_one({"_id": id, "user_id": current_user.id}):
        raise HTTPException(status_code=403, detail="Forbidden")
    
    plant = plants_collection.find_one({"_id": id}, {"growth_log": 1})
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")

    return {"growth_log": plant.get("growth_log", [])}


################################### POST ##################################

#DONE
# POST /plants/{id}/growth → добавить запись роста пользователя
@router.post("/{id}/growth")
async def add_growth_entry(id: str, growth_entry: GrowthEntry, current_user=Depends(get_current_user)):
    try:
        object_id = ObjectId(id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    entry_data = growth_entry.dict()
    entry_data["date"] = entry_data.get("date") or datetime.utcnow().isoformat()
    entry_data["_id_growth"] = str(ObjectId())

    if not plants_collection.find_one({"_id": id, "user_id": current_user.id}):
        raise HTTPException(status_code=403, detail="Forbidden")
    
    result = plants_collection.update_one(
        {"_id": id},
        {"$push": {"growth_log": entry_data}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Plant not found")

    return {"message": "Growth entry added successfully", "entry": entry_data}

#DONE
# POST /plants/{id}/water - обновление water -> now
@router.post("/{id}/water")
async def update_watering_date(id, current_user=Depends(get_current_user)):
    try:
        now = datetime.utcnow()

    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    update_data = {"last_watered": now}

    if not update_data:
        raise HTTPException(status_code=400, detail="No data provided for update")

    if not plants_collection.find_one({"_id": id, "user_id": current_user.id}):
        raise HTTPException(status_code=403, detail="Forbidden")
    
    result = plants_collection.update_one({"_id": id}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Plant not found")

    return {"message": "Watering date updated successfully"}


#DONE
# POST /plants/{id}/fertilize - обновление fertilize -> now
@router.post("/{id}/fertilize")
async def update_fertilizing_date(id, current_user=Depends(get_current_user)):
    try:
        now = datetime.utcnow()

    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    update_data = {"last_fertilized": now}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No data provided for update")

    if not plants_collection.find_one({"_id": id, "user_id": current_user.id}):
        raise HTTPException(status_code=403, detail="Forbidden")
    
    result = plants_collection.update_one({"_id": id}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Plant not found")

    return {"message": "Fertilizing date updated successfully"}


#DONE
# POST /plants → добавить растение для пользователя 
@router.post("/")
async def add_user_plant(plant_in: PlantCreate, current_user=Depends(get_current_user)):
    try:
        doc = plant_in.dict()

        doc["_id"] = str(ObjectId())
        doc["user_id"] = current_user.id

        plants_collection.insert_one(doc)
        
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid data: {str(e)}")

    return {"message": f"Plant for user {current_user.id} added successfully", "plant": doc}


################################### PUT ###################################

#DONE
# PUT /plants/{id} → обновить растение принадлежащее пользователю
@router.put("/{id}")
async def update_plant(id: str, plant: PlantCreate, current_user=Depends(get_current_user)):
    try:
        object_id = ObjectId(id)

    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    update_data = {k: v for k, v in plant.dict().items() if v not in (None, "")}
    if not update_data:
        raise HTTPException(status_code=400, detail="No data provided for update")

    if not plants_collection.find_one({"_id": id, "user_id": current_user.id}):
        raise HTTPException(status_code=403, detail="Forbidden")
        
    result = plants_collection.update_one({"_id": id}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Plant not found")

    return {"message": "Plant updated successfully"}


################################# DELETE ##################################

@router.delete("/{id}/growth/{id_growth}")
async def delete_growth_entry(id: str, id_growth: str, current_user=Depends(get_current_user)):
    try:
        object_id = ObjectId(id)
        object_id_growth = ObjectId(id_growth)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    if not plants_collection.find_one({"_id": id, "user_id": current_user.id}):
        raise HTTPException(status_code=403, detail="Forbidden")
    
    result = plants_collection.update_one(
        {"_id": id},
        {"$pull": {"growth_log": {"_id_growth": id_growth}}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Plant not found")

    return {"message": "Growth entry deleted successfully"}

#DONE
# DELETE /plants/{id} → удалить растение принадлежащее пользователю
@router.delete("/{id}")
async def delete_user_plant(id: str, current_user=Depends(get_current_user)):
    try:
        object_id = ObjectId(id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    if not plants_collection.find_one({"_id": id, "user_id": current_user.id}):
        raise HTTPException(status_code=403, detail="Forbidden")
    
    result = plants_collection.delete_one({"_id": id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Plant not found")

    return {"message": "Plant deleted successfully"}