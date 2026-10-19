from pydantic.json_schema import JsonSchemaValue
from pydantic import HttpUrl
from fastapi import status
# from inspect import AGEN_CLOSED
from fastapi import FastAPI,Path,HTTPException,Query
import json
from typing import Annotated,Literal,Optional
from pydantic import BaseModel , Field, computed_field,EmailStr,AnyUrl
from fastapi.responses import JSONResponse


app=FastAPI()

class Patient(BaseModel):
    id: Annotated[str, Field(..., description='ID of the patient', examples=['P001'])]
    name: Annotated[str, Field(..., description='Name of the patient')]
    city: Annotated[str, Field(..., description='City where the patient is living')]
    age: Annotated[int, Field(..., gt=0, lt=120, description='Age of the patient')]
    gender: Annotated[Literal['male', 'female', 'others'], Field(..., description='Gender of the patient')]
    height: Annotated[float, Field(..., gt=0, description='Height of the patient in mtrs')]
    weight: Annotated[float, Field(..., gt=0, description='Weight of the patient in kgs')]

    @computed_field
    @property
    def bmi(self) -> float:
        bmi = round(self.height / (self.weight ** 2), 2)
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

class PatientUpdate(BaseModel):
    name:Annotated[Optional[str],Field(default=None)]
    city:Annotated[Optional[str],Field(default=None)]
    age:Annotated[Optional[int],Field(default=None,gt=0)]
    gender: Annotated[Optional[Literal['male', 'female']], Field(default=None)]
    height: Annotated[Optional[float], Field(default=None, gt=0)]
    weight: Annotated[Optional[float], Field(default=None, gt=0)]


def load_data():
    with open("patients.json","r") as f:
        return json.load(f)

def save_data(data):
    with open("patients.json", "w") as f:
        json.dump(data,f)
@app.get("/hello")
def greet():
    return {"message":"Hello From Vishesh UndKkat"}

@app.get("/about")
def about():
    return {"message":"this website is all about patient management system."}

@app.get("/view")
def view():
    data=load_data()

    return data


@app.get("/view/{patient_id}")
def view_patient(patient_id:str):
    """this function is used to view particular patient by it's id"""
    data=load_data()

    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404,detail="patient is not found")

@app.get("/view/name/{patient_name}")
def get_by_patient_name(patient_name:str):
    """this function is used to fetch the data of a particular patient by patient name"""

    data=load_data()

    if patient_name in data:
        return data[patient_name]
    raise HTTPException(status_code=404,detail="patient is not found")

@app.post('/create')
def create_patient(patient: Patient):

    # load existing data
    data = load_data()

    # check if the patient already exists
    if patient.id in data:
        raise HTTPException(status_code=400, detail='Patient already exists')

    # new patient add to the database
    data[patient.id] = patient.model_dump(exclude=["id"])

    # save into the json file
    save_data(data)

    return JSONResponse(status_code=201, content={'message':'patient created successfully'})

@app.put("/edit/{patient_id}")


@app.delete("/delete/{patient_id}")
def delete_patient(patient_id:str):
    """this function is used to delete a use from a database"""

    data=load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404,detail="patient is not found")

    del data[patient_id]

    save_data(data)

    return JSONResponse(status_code=200,content={"message":"patient is deleted"})