from fastapi import APIRouter, HTTPException, Query
from pymongo.errors import PyMongoError

from datetime import datetime, timedelta

from app.db.mongo import plants_collection

router = APIRouter()

# Получить список растений у которых полив больше 7 дней назад
@router.get("/")
async def get_reminders(type: str = Query(..., regex="^(water|fertilize)$")):
    try:
        now = datetime.utcnow()
        
        if type == "water":
            seven_days_ago = now - timedelta(days=7)
            plants = list(plants_collection.find(
                {"last_watered": {"$exists": True, "$lt": seven_days_ago}},
                {"_id": 1, "name": 1, "species": 1, "last_watered": 1}
            ))
            for plant in plants:
                plant["_id"] = str(plant["_id"])
            return {
                "message": f"{len(plants)} plants need watering.",
                "plants": plants}
        
        elif type == "fertilize":
            month_ago = now - timedelta(days=30)
            plants = list(plants_collection.find(
                {"last_fertilized": {"$exists": True, "$lt": month_ago}},
                {"_id": 1, "name": 1, "species": 1, "last_fertilized": 1}
            ))
            for plant in plants:
                plant["_id"] = str(plant["_id"])
            return {
                "message": f"{len(plants)} plants need fertilizing.",
                "plants": plants}
        else:
            raise HTTPException(status_code=400, detail="Invalid reminder type.")
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    