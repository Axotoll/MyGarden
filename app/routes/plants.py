from fastapi import APIRouter, HTTPException, Query
from pymongo.errors import PyMongoError
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime

from app.db.mongo import plants_collection
from app.models.plant import Plant, GrowthEntry

router = APIRouter()


################################### GET ###################################

# GET /plants → список всех растений
@router.get("/")
async def get_plants_list(user_id: str = Query(...)):
    try:
        pipeline = [
            { 
                "$match": { "user_id": user_id }  
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

        return {"plants": plants}

    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


# GET /plants/{id} → одно растение
@router.get("/{id}")
async def get_single_user_plant(id: str):
    try:
        object_id = ObjectId(id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    plant = plants_collection.find_one({"_id": object_id})
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")

    plant["_id"] = str(plant["_id"])
    return {"plant": plant}


# фильты и поиск по имени и виду
@router.get("/search")
async def filter_plants(type: str = Query(..., regex="^(name|species)$"), value: str = Query(..., min_length=1)):
    try:
        if type == "name":
            plants = list(plants_collection.find({"name": {"$regex": value}}))
            for plant in plants:
                plant["_id"] = str(plant["_id"])
            return {
                "message": f"{len(plants)} plants with this name was found.",
                "plants": plants}
        
        elif type == "species":
            plants = list(plants_collection.find({"species": {"$regex": value}}))
            for plant in plants:
                plant["_id"] = str(plant["_id"])
            return {
                "message": f"{len(plants)} plants with this species was found.",
                "plants": plants}

        else:
            raise HTTPException(status_code=400, detail="Invalid filter type.")
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


# GET /plants/{id}/growth → история роста
@router.get("/{id}/growth")
async def get_growth_entry(id: str):
    try:
        object_id = ObjectId(id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    plant = plants_collection.find_one({"_id": object_id}, {"growth_log": 1})
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")

    return {"growth_log": plant.get("growth_log", [])}


################################### POST ##################################

# POST /plants/{id}/growth → добавить запись роста
@router.post("/{id}/growth")
async def add_growth_entry(id: str, growth_entry: GrowthEntry):
    try:
        object_id = ObjectId(id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    entry_data = growth_entry.dict()
    entry_data["date"] = entry_data.get("date") or datetime.utcnow().isoformat()

    result = plants_collection.update_one(
        {"_id": object_id},
        {"$push": {"growth_log": entry_data}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Plant not found")

    return {"message": "Growth entry added successfully", "entry": entry_data}


# POST /plants/{id}/water - обновление water -> now
@router.post("/{id}/water")
async def update_watering_date(id):
    try:
        now = datetime.utcnow()
        object_id = ObjectId(id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    update_data = {"last_watered": now}

    if not update_data:
        raise HTTPException(status_code=400, detail="No data provided for update")

    result = plants_collection.update_one({"_id": object_id}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Plant not found")

    return {"message": "Watering date updated successfully"}


# POST /plants/{id}/fertilize - обновление fertilize -> now
@router.post("/{id}/fertilize")
async def update_fertilizing_date(id):
    try:
        now = datetime.utcnow()
        object_id = ObjectId(id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    update_data = {"last_fertilized": now}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No data provided for update")

    result = plants_collection.update_one({"_id": object_id}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Plant not found")

    return {"message": "Fertilizing date updated successfully"}


# POST /plants → добавить растение
@router.post("/")
async def add_user_plant(plant: Plant):
    try:
        doc = plant.dict()
        plants_collection.insert_one(doc)
        doc["_id"] = str(doc.get("_id", ""))
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid data: {str(e)}")

    return {"message": "Plant added successfully", "plant": doc}



################################### PUT ###################################

# PUT /plants/{id} → обновить растение
@router.put("/{id}")
async def update_plant(id: str, plant: Plant):
    try:
        object_id = ObjectId(id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    update_data = {k: v for k, v in plant.dict().items() if v not in (None, "")}
    if not update_data:
        raise HTTPException(status_code=400, detail="No data provided for update")

    result = plants_collection.update_one({"_id": object_id}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Plant not found")

    return {"message": "Plant updated successfully"}


################################# DELETE ##################################

# DELETE /plants/{id} → удалить растение
@router.delete("/{id}")
async def delete_user_plant(id: str):
    try:
        object_id = ObjectId(id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    result = plants_collection.delete_one({"_id": object_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Plant not found")

    return {"message": "Plant deleted successfully"}