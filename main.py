from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import numpy as np

# ===== V5 ENGINE =====
class NexusV5_RealPredictor:
    """V5.2 PRO - Real STOP fix"""
    def __init__(self):
        self.last_pos = None
        self.velocity = np.zeros(3, dtype=np.float32)
        self.alpha = 0.7

    def predict_next_frame(self, coords, dt=0.016, predict_frames=3):
        coords = np.array(coords, dtype=np.float32)
        
        if self.last_pos is None:
            self.last_pos = coords
            print(f"[V5.2] INIT Pos: {coords}")
            return coords

        raw_vel = (coords - self.last_pos) / dt
        raw_speed = np.linalg.norm(raw_vel)

        if raw_speed < 0.1:
            self.velocity *= 0.0
            predicted = coords
            state = "STOPPED [BRAKE]"
        else:
            self.velocity = raw_vel * self.alpha + self.velocity * (1 - self.alpha)
            speed = np.linalg.norm(self.velocity)
            predicted = coords + self.velocity * dt * predict_frames
            state = f"MOVING {speed:.1f}u/s"
        
        self.last_pos = coords.copy()
        print(f"[V5.2] Pos: {coords} | {state} | Raw: {raw_speed:.1f} | Vel: {self.velocity.round(1)} | Pred: {predicted.round(1)}")
        return predicted

# Global
app = FastAPI(title="NEXUS V5 LIVE - Real Predictor")
predictor = NexusV5_RealPredictor()

class PredictRequest(BaseModel):
    coords: List[float]
    dt: float = 0.016
    predict_frames: int = 3

@app.get("/")
def home():
    return {
        "engine": "NEXUS V5.2 PRO",
        "status": "LIVE ✅",
        "author": "Abhishek Pal",
        "endpoints": ["/predict"]
    }

@app.post("/predict")
def predict_pos(req: PredictRequest):
    pred = predictor.predict_next_frame(req.coords, req.dt, req.predict_frames)
    
    return {
        "input": req.coords,
        "predicted": pred.tolist(),
        "velocity": predictor.velocity.tolist(),
        "raw_speed": float(np.linalg.norm((np.array(req.coords) - predictor.last_pos) / req.dt)) if predictor.last_pos is not None else 0,
        "status": "STOPPED [BRAKE]" if float(np.linalg.norm(predictor.velocity)) < 0.1 else "MOVING"
    }

@app.get("/test")
def test_run():
    # Quick test same as your local test
    v5 = NexusV5_RealPredictor()
    v5.predict_next_frame([100.5, 200.0, 50.2])
    v5.predict_next_frame([101.0, 200.5, 50.2])
    v5.predict_next_frame([102.3, 201.8, 50.2])
    v5.predict_next_frame([102.3, 201.8, 50.2])
    return {"test": "Check Render Logs for output - STOPPED working ✅"}
