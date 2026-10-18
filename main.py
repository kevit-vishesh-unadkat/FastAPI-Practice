from pydantic.json_schema import JsonSchemaValue
from pydantic import HttpUrl
from fastapi import status
from inspect import AGEN_CLOSED
from fastapi import FastAPI,Path,HTTPException,Query
import json
from typing import Annotated,Literal,Optional
from pydantic import BaseModel , Field, computed_field
from fastapi.responses import JSONResponse


app=FastAPI()

class Patient(BaseModel):
    id:str
    name:str
    age:int
    city:str
    height:float
    weight:float

def load_data():
    with open("patients.json","r") as f:
        return json.load(f)

def save_data(data):
    with open("patients..json","w") as f:
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

@app.post("/create")
def create_patient(patient:Patient):
    """this function is used to create a new patient"""

    data=load_data()

    # first check user is already exists in database

    if patient.id in data:
        raise HTTPException (status_code=400,detail="user is already exist")

    data[patient.id]=patient.model_dump(exclude=['id'])

    save_data(data)

    return JSONResponse(status_code=201,content={"message":"patient is created successfully"})


@app.delete("/delete/{patient_id}")
def delete_patient(patient_id:str):
    """this function is used to delete a use from a database"""

    data=load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404,detail="patient is not found")

    del data[patient_id]

    save_data(data)

    return JSONResponse(status_code=200,content={"message":"patient is deleted"})