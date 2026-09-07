from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Smart Campus Parking Backend is running"}


@app.get("/parking/status")
def parking_status():
    return {
        "status": "ok",
        "message": "Parking status endpoint is working"
    }
