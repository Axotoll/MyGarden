from fastapi import APIRouter, HTTPException, Query, Depends
from app.db.mongo import plants_collection, users_collection, species_collection


router = APIRouter()

@router.get("/")
async def get_species(q: str = Query("", min_length=0)):
    cursor = species_collection.find(
        {"$or": [
            {"name": {"$regex": q, "$options": "i"}},
            {"scientific_name": {"$regex": q, "$options": "i"}},
        ]},
        {"name": 1, "scientific_name": 1}
    ).limit(20)
    results = cursor.to_list(length=20)
    return [
        {
            "label": f'{s["name"]} ({s["scientific_name"]})',
            "value": str(s["_id"]),
        }
        for s in results
    ]
    