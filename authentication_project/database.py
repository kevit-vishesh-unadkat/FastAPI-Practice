import os

from dotenv import  load_dotenv
from pymongo import MongoClient
from pymongo.server_api import ServerApi


load_dotenv()

MONGODB_URL=os.getenv(
    "MONGODB_URL",
    "mongodb://localhost:27017/"
)

DATABASE_NAME = os.getenv(
    "DATABASE_NAME",
    "fastapi_auth_db"
)

client = MongoClient(
    MONGODB_URL,
    server_api=ServerApi("1"),
    serverSelectionTimeoutMS=5000,
)

db=client[DATABASE_NAME]

users_collection=db['users']
tasks_collection=db['tasks']

def check_database_connection():
    client.admin.command("ping")

def close_database_connection():
    client.close()

def initialize_database():
    users_collection.create_index("username", unique=True)
    users_collection.create_index("email", unique=True)
    tasks_collection.create_index("owner_id")