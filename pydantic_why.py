from pydantic import BaseModel, EmailStr, AnyUrl, Field, computed_field
from typing import List, Dict, Any, Optional, Annotated,Literal


class Patient(BaseModel):
    name:Annotated[str,Field(...,max_length=50,title="Name of Patient",description="give the name of the patient in less than 50 chars")]
    email:EmailStr
    linkedin_url:AnyUrl
    age:int=Field(gt=0,lt=100,description ="Age of the Patient")
    gender: Annotated[Literal['male', 'female', 'others'], Field(..., description='Gender of the patient')]
    height: Annotated[float, Field(..., gt=0, description='Height of the patient in mtrs')]
    weight: Annotated[float, Field(..., gt=0, description='Weight of the patient in kgs')]

    @computed_field
    @property
    def bmi(self)->float:
        bmi=round(self.height/(self.weight**2),2)
        return bmi

    @computed_field
    @property
    def verdict(self) -> str:

        if self.bmi < 18.5:
            return 'Underweight'
        elif self.bmi < 25:
            return 'Normal'
        elif self.bmi < 30:
            return 'Normal'
        else:
            return 'Obese'