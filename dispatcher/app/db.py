from pymongo import MongoClient

MONGO_URL = "mongodb://mongo:27017"

client = MongoClient(MONGO_URL)
db = client["dispatcher_db"]
logs_collection = db["logs"]