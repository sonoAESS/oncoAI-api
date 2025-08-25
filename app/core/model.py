import joblib
import numpy as np
from app.core.config import MODEL_PATH

model = joblib.load(MODEL_PATH)

def model_predict(features: list[float]) -> float:
    if len(features) != 32:
        raise ValueError("El modelo requiere 32 características")
    input_array = np.array(features).reshape(1, -1)
    prob = model.predict_proba(input_array)[:, 1][0]
    return prob
