from pymongo import MongoClient

MONGO_URL = "mongodb://mongo:27017"

client = MongoClient(MONGO_URL)
db = client["auth_db"]
users_collection = db["users"]