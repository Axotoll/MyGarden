from pymongo import MongoClient
from app.config import MONGO_DB_URI


client = MongoClient(MONGO_DB_URI)
db = client.get_database("plants")
plants_collection = db.plants
species_collection = db.species
users_collection = db.users

try:
    client.admin.command("ping")
    print("✅ Successfully connected to MongoDB!")
    # print("Databases:", client.list_database_names())
    # print("Collections in 'plants' database:", db.list_collection_names())
    # print("Sample document from 'plants' collection:", plants_collection.find_one())
except Exception as e:
    print("❌ Connection error:", e)