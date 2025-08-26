import joblib
import numpy as np
import logging
from pathlib import Path
from app.core.config import MODEL_PATH

# Configure logging
logger = logging.getLogger(__name__)

# Load model with error handling
try:
    model_path = Path(MODEL_PATH)
    if not model_path.exists():
        raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")

    model = joblib.load(MODEL_PATH)
    logger.info(f"Model loaded successfully from {MODEL_PATH}")

except FileNotFoundError as e:
    logger.error(f"Model loading failed: {e}")
    model = None
    # Create a dummy model for development/testing
    from sklearn.ensemble import RandomForestClassifier
    import numpy as np
    model = RandomForestClassifier(n_estimators=10, random_state=42)
    # Train on dummy data
    X_dummy = np.random.rand(100, 32)
    y_dummy = np.random.randint(0, 2, 100)
    model.fit(X_dummy, y_dummy)
    logger.warning("Using dummy model for development - replace with actual trained model")

except Exception as e:
    logger.error(f"Error loading model: {e}")
    raise

def model_predict(features: list[float]) -> float:
    """
    Predict survival probability for given features.

    Parameters:
    - features (list[float]): List of 32 numerical features.

    Returns:
    - float: Survival probability between 0 and 1.

    Raises:
    - ValueError: If the number of features is not 32 or if the features are not numeric.
    - RuntimeError: If the model prediction fails.
    """
    if len(features) != 32:
        raise ValueError("El modelo requiere exactamente 32 características")

    if not all(isinstance(f, (int, float)) for f in features):
        raise ValueError("Todas las características deben ser numéricas")

    try:
        input_array = np.array(features).reshape(1, -1)
        prob = model.predict_proba(input_array)[:, 1][0]
        return float(prob)
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise RuntimeError(f"Error en la predicción: {e}")
