from pydantic import BaseModel
from typing import List

class SurvivalInput(BaseModel):
    features: List[float]

class SurvivalOutput(BaseModel):
    survival_probability: float
