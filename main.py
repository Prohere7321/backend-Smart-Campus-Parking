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

@app.get("/admin/all-vehicles")
def get_all_vehicles():
    try:
        users = list(
            db["users"].find(
                {},
                {
                    "_id": 0,
                    "name": 1,
                    "email": 1,
                    "role": 1,
                    "student_id": 1,
                    "staff_id": 1,
                    "driving_score": 1,
                    "vehicles": 1
                }
            )
        )

        all_vehicles = []

        for user in users:
            for vehicle in user.get("vehicles", []):
                full_plate = vehicle.get("plate", "")
                plate = full_plate
                province = ""

                # Mobile app currently stores Thai province as part of plate.
                # Split the final space-separated part for the admin table.
                if " " in full_plate:
                    plate, province = full_plate.rsplit(" ", 1)

                owner_id = (
                    user.get("student_id")
                    or user.get("staff_id")
                    or ""
                )

                all_vehicles.append({
                    "owner": user.get("name", ""),
                    "ownerEmail": user.get("email", ""),
                    "role": user.get("role", ""),
                    "id": owner_id,
                    "plate": plate,
                    "province": province,
                    "vehicle": vehicle.get("model", ""),
                    "score": user.get("driving_score", 100)
                })

        return all_vehicles

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve all vehicles: {str(e)}"
        )

class ScoreAdjustment(BaseModel):
    user_email: str
    points_changed: int
    reason: str = ""
    gate_name: str = ""
    image_url: str = ""


@app.post("/admin/adjust-score")
def adjust_score(adjustment: ScoreAdjustment):
    try:
        user = db["users"].find_one(
            {"email": adjustment.user_email},
            {"_id": 0, "driving_score": 1}
        )

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        current_score = user.get("driving_score", 100)

        new_score = max(
            0,
            min(100, current_score + adjustment.points_changed)
        )

        result = db["users"].update_one(
            {"email": adjustment.user_email},
            {"$set": {"driving_score": new_score}}
        )

        if result.matched_count != 1:
            raise HTTPException(
                status_code=500,
                detail="Failed to update driving score"
            )

        return {
            "message": "Driving score updated successfully",
            "user_email": adjustment.user_email,
            "previous_score": current_score,
            "points_changed": adjustment.points_changed,
            "new_score": new_score
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to adjust driving score: {str(e)}"
        )

@app.get("/detections")
def get_detections():
    try:
        records = list(
            db["detection_logs"].find(
                {},
                {"_id": 0}
            ).sort("timestamp", -1)
        )

        detections = []

        for record in records:
            event = str(record.get("event", ""))
            event_lower = event.lower()

            # Support both newer detection records and older detection_logs.
            violation = record.get("violation")

            if violation is None:
                violation = (
                    "no helmet" in event_lower
                    or "violation" in event_lower
                )

            vehicle_type = record.get("vehicle_type")

            if not vehicle_type:
                vehicle_type = (
                    "motorcycle"
                    if "helmet" in event_lower
                    else "car"
                )

            helmet_detected = record.get("helmet_detected")

            if helmet_detected is None and vehicle_type == "motorcycle":
                helmet_detected = not violation

            detections.append({
                "timestamp": record.get("timestamp"),
                "license_plate": record.get("license_plate", ""),
                "vehicle_type": vehicle_type,
                "helmet_detected": helmet_detected,
                "violation": bool(violation),
                "matched_user": record.get("matched_user"),
                "gate_type": (
                    record.get("gate_type")
                    or record.get("camera_location")
                )
            })

        return detections

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve detections: {str(e)}"
        )
