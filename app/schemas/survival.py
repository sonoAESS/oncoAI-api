from pydantic import BaseModel
from typing import List

class SurvivalInput(BaseModel):
    """
    Schema for survival prediction input.

    Attributes:
    - features (List[float]): A list of 32 numerical features for the prediction.
    """
    features: List[float]

    class Config:
        from_attributes = True

class SurvivalOutput(BaseModel):
    """
    Schema for survival prediction output.

    Attributes:
    - survival_probability (float): The predicted survival probability.
    """
    survival_probability: float

    class Config:
        from_attributes = True
