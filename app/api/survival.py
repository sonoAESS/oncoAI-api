from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from fastapi.responses import JSONResponse
from typing import List
import pandas as pd

from app.schemas.survival import SurvivalInput, SurvivalOutput
from app.core.security import get_current_active_user
from app.core.model import model_predict

router = APIRouter(prefix="/predict", tags=["predict"])

@router.post("/", response_model=SurvivalOutput)
async def predict_survival(data: SurvivalInput, current_user=Depends(get_current_active_user)):
    if len(data.features) != 32:
        raise HTTPException(status_code=400, detail="Se requieren 32 características para el modelo")
    prob = model_predict(data.features)
    return SurvivalOutput(survival_probability=prob)

@router.post("/batch_predict", response_class=JSONResponse)
async def batch_predict(file: UploadFile = File(...), current_user=Depends(get_current_active_user)):
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
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": f"Error leyendo archivo: {str(e)}"})

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
        except Exception:
            preds.append(None)

    results = [{"row": i, "survival_probability": p} for i, p in enumerate(preds)]
    return {"predictions": results}
