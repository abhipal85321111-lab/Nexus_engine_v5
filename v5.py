import numpy as np

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

        # 1. REAL RAW VELOCITY - pehle check karo
        raw_vel = (coords - self.last_pos) / dt
        raw_speed = np.linalg.norm(raw_vel)

        # 2. REAL STOP DETECTION - Raw speed se, smoothed se nahi!
        if raw_speed < 0.1:  # Ek dum ruka
            self.velocity *= 0.0  # Velocity turant zero
            predicted = coords
            state = "STOPPED [BRAKE]"
        else:
            # Tabhi smooth kar
            self.velocity = raw_vel * self.alpha + self.velocity * (1 - self.alpha)
            speed = np.linalg.norm(self.velocity)
            predicted = coords + self.velocity * dt * predict_frames
            state = f"MOVING {speed:.1f}u/s"
        
        self.last_pos = coords.copy()
        print(f"[V5.2] Pos: {coords} | {state} | Raw: {raw_speed:.1f} | Vel: {self.velocity.round(1)} | Pred: {predicted.round(1)}")
        return predicted

# ========== TEST ==========
if __name__ == "__main__":
    v5 = NexusV5_RealPredictor()
    
    print("--- Player Running ---")
    v5.predict_next_frame([100.5, 200.0, 50.2])
    v5.predict_next_frame([101.0, 200.5, 50.2])
    v5.predict_next_frame([101.6, 201.1, 50.2])
    v5.predict_next_frame([102.3, 201.8, 50.2])

    print("\n--- Player Stopped ---")
    v5.predict_next_frame([102.3, 201.8, 50.2])
    v5.predict_next_frame([102.3, 201.8, 50.2])

    print("\n--- Player Reversed ---")
    v5.predict_next_frame([101.8, 201.2, 50.2])
