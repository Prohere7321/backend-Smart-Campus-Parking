from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from pymongo import MongoClient
import os

load_dotenv()

app = FastAPI()

MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB = os.getenv("MONGODB_DB")

client = MongoClient(MONGODB_URI)
db = client[MONGODB_DB]


@app.get("/")
def root():
    return {"message": "Smart Campus Parking Backend is running"}


@app.get("/parking/status")
def parking_status():
    try:
        records = list(
            db["parking_status"].find(
                {},
                {"_id": 0}
            )
        )

        return records

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve parking status: {str(e)}"
        )
