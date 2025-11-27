import logging
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from fastapi.responses import JSONResponse
from typing import List
import pandas as pd

from app.schemas.survival import SurvivalInput, SurvivalOutput
from app.core.security import get_current_active_user
from app.core.model import model_predict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/lgg_survival")

@router.post(
    "/",
    response_model=SurvivalOutput,
    summary="Predict LGG survival probability",
    description=(
        "Predicts the survival probability for Lower Grade Glioma (LGG) cancer patients "
        "based on 32 molecular and clinical features. The model uses machine learning "
        "to analyze gene expression levels and somatic copy number alterations (SCNA) "
        "to provide a survival probability score between 0 and 1."
    ),
    responses={
        200: {
            "description": "Prediction successful",
            "content": {
                "application/json": {
                    "example": {
                        "survival_probability": 0.85
                    }
                }
            }
        },
        400: {
            "description": "Invalid input data",
            "content": {
                "application/json": {
                    "examples": {
                        "wrong_feature_count": {
                            "summary": "Incorrect number of features",
                            "value": {"detail": "Se requieren 32 características para el modelo"}
                        },
                        "non_numeric_features": {
                            "summary": "Non-numeric features",
                            "value": {"detail": "Las características deben ser numéricas"}
                        }
                    }
                }
            }
        },
        401: {
            "description": "Authentication required",
            "content": {
                "application/json": {
                    "example": {"detail": "Not authenticated"}
                }
            }
        },
        422: {
            "description": "Validation Error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "features"],
                                "msg": "ensure this value has at least 32 items",
                                "type": "value_error.const"
                            }
                        ]
                    }
                }
            }
        }
    }
)
async def predict_survival(data: SurvivalInput, current_user=Depends(get_current_active_user)):
    """
    Predict LGG survival probability from molecular features.

    This endpoint analyzes 32 specific molecular features including gene expression levels
    and somatic copy number alterations (SCNA) to predict patient survival probability.

    **Required Features (32 total):**
    - **Gene Expression Features (16):** B2M, C1QB, C1QC, CASP1, CD2, CD3E, CD4, CD74, FCER1G, FCGR3A, IL10, LCK, LCP2, LYN, PTPRC, SERPING1
    - **SCNA Features (16):** Corresponding _scna variants for each gene above

    **Parameters:**
    - **data** (SurvivalInput): Input data containing feature array
        - **features** (List[float]): Array of 32 numerical values representing molecular features

    **Returns:**
    - **SurvivalOutput**: Prediction result
        - **survival_probability** (float): Predicted survival probability (0.0 to 1.0)

    **Raises:**
    - **400 Bad Request**: Invalid feature count or non-numeric values
    - **401 Unauthorized**: Missing or invalid authentication token
    - **422 Unprocessable Entity**: Invalid input format
    """
    if len(data.features) != 32:
        raise HTTPException(status_code=400, detail="Se requieren 32 características para el modelo")

    # Validate that the features are numeric
    if not all(isinstance(feature, (int, float)) for feature in data.features):
        raise HTTPException(status_code=400, detail="Las características deben ser numéricas")

    prob = model_predict(data.features)
    return SurvivalOutput(survival_probability=prob)

@router.post("/batch_predict", response_class=JSONResponse)
async def batch_predict(file: UploadFile = File(...), current_user=Depends(get_current_active_user)):
    """
    Predict survival probabilities for a batch of input data from a CSV or Excel file.

    Parameters:
    - file (UploadFile): The uploaded file containing the input data.

    Returns:
    - JSONResponse: A JSON response containing the survival probabilities for each row in the input data.

    Raises:
    - HTTPException: If the file format is not supported or if there is an error reading the file.
    """
    if file.content_type not in [
        "text/csv",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    ]:
        return JSONResponse(status_code=400, content={"error": "Formato no soportado, usa CSV o Excel"})

    try:
        if file.content_type == "text/csv":
            df = pd.read_csv(file.file)
        else:
            df = pd.read_excel(file.file)
    except FileNotFoundError:
        logger.exception("Archivo no encontrado")
        return JSONResponse(status_code=400, content={"error": "Archivo no encontrado"})
    except pd.errors.ParserError:
        logger.exception("Error al leer el archivo")
        return JSONResponse(status_code=400, content={"error": "Error al leer el archivo, verifique el formato"})
    except Exception as e:
        logger.exception(f"Error inesperado al leer el archivo: {str(e)}")
        return JSONResponse(status_code=500, content={"error": f"Error inesperado al leer el archivo: {str(e)}"})

    required_cols = [
        'B2M_expression', 'B2M_scna', 'C1QB_expression', 'C1QB_scna',
        'C1QC_expression', 'C1QC_scna', 'CASP1_expression', 'CASP1_scna',
        'CD2_expression', 'CD2_scna', 'CD3E_expression', 'CD3E_scna',
        'CD4_expression', 'CD4_scna', 'CD74_expression', 'CD74_scna',
        'FCER1G_expression', 'FCER1G_scna', 'FCGR3A_expression', 'FCGR3A_scna',
        'IL10_expression', 'IL10_scna', 'LCK_expression', 'LCK_scna',
        'LCP2_expression', 'LCP2_scna', 'LYN_expression', 'LYN_scna',
        'PTPRC_expression', 'PTPRC_scna', 'SERPING1_expression', 'SERPING1_scna'
    ]

    missing_cols = [c for c in required_cols if c not in df.columns]
    if missing_cols:
        return JSONResponse(status_code=400, content={"error": f"Faltan columnas: {missing_cols}"})

    data = df[required_cols].values.tolist()
    preds = []
    for features in data:
        try:
            prob = model_predict(features)
            preds.append(prob)
        except Exception as e:
            logger.exception(f"Error al predecir la probabilidad de supervivencia: {str(e)}")
            preds.append(None)

    results = [{"row": i, "survival_probability": p} for i, p in enumerate(preds)]
    return {"predictions": results}

@router.get("/health")
def health_check():
    return {"status": "healthy prediction"}