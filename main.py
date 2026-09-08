from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from pymongo import MongoClient
import os

load_dotenv()

app = FastAPI()

MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB = os.getenv("MONGODB_DB")

client = MongoClient(MONGODB_URI)
db = client[MONGODB_DB]

class VehicleRegistration(BaseModel):
    plate: str
    model: str
    user_email: str
    role: str

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

@app.get("/officer/detections")
def officer_detections(violation_only: bool = False):
    try:
        query = {}

        if violation_only:
            query = {
                "event": {
                    "$regex": "helmet|violation",
                    "$options": "i"
                }
            }

        records = list(
            db["detection_logs"].find(
                query,
                {"_id": 0}
            ).sort("timestamp", -1)
        )

        return records

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve detection logs: {str(e)}"
        )

@app.get("/parking/user-vehicles")
def get_user_vehicles(user_email: str):
    try:
        user = db["users"].find_one(
            {"email": user_email},
            {"_id": 0, "vehicles": 1}
        )

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        return user.get("vehicles", [])

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve user vehicles: {str(e)}"
        )

@app.post("/parking/register-vehicle")
def register_vehicle(vehicle: VehicleRegistration):
    try:
        user = db["users"].find_one(
            {"email": vehicle.user_email},
            {"_id": 0, "vehicles": 1}
        )

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        existing_vehicles = user.get("vehicles", [])

        for existing_vehicle in existing_vehicles:
            if existing_vehicle.get("plate") == vehicle.plate:
                raise HTTPException(
                    status_code=409,
                    detail="Vehicle already registered"
                )

        vehicle_data = {
            "plate": vehicle.plate,
            "model": vehicle.model
        }

        result = db["users"].update_one(
            {"email": vehicle.user_email},
            {"$push": {"vehicles": vehicle_data}}
        )

        if result.modified_count != 1:
            raise HTTPException(
                status_code=500,
                detail="Failed to register vehicle"
            )

        return {
            "message": "Vehicle registered successfully",
            "vehicle": vehicle_data
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to register vehicle: {str(e)}"
        )

@app.delete("/parking/delete-vehicle")
def delete_vehicle(user_email: str, plate: str):
    try:
        user = db["users"].find_one(
            {"email": user_email},
            {"_id": 0, "vehicles": 1}
        )

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        existing_vehicles = user.get("vehicles", [])

        if not any(vehicle.get("plate") == plate for vehicle in existing_vehicles):
            raise HTTPException(
                status_code=404,
                detail="Vehicle not found"
            )

        result = db["users"].update_one(
            {"email": user_email},
            {"$pull": {"vehicles": {"plate": plate}}}
        )

        if result.modified_count != 1:
            raise HTTPException(
                status_code=500,
                detail="Failed to delete vehicle"
            )

        return {
            "message": "Vehicle deleted successfully",
            "plate": plate
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete vehicle: {str(e)}"
        )
