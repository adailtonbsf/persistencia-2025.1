import os
from motor.motor_asyncio import AsyncIOMotorClient
from odmantic import AIOEngine
from dotenv import load_dotenv

load_dotenv()
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/eventos_db")
client = AsyncIOMotorClient(MONGO_URL)
engine = AIOEngine(client=client, database="eventos_db")