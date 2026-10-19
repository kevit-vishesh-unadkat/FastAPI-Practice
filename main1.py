from typing import Annotated, Optional
from unittest import result

from fastapi import FastAPI , HTTPException
from pydantic import BaseModel,Field
from pymongo import MongoClient
from bson import ObjectId
from starlette.responses import JSONResponse

app=FastAPI()

client=MongoClient("mongodb://127.0.0.1:27017")
db=client['student_db']
students=db['students']

class Student(BaseModel):
    name:Annotated[str,Field(min_length=2,max_length=50)]
    age:Annotated[int,Field(gt=0,lt=100)]
    city:Annotated[str,Field(min_length=2,max_length=100)]

# pydantic model for update query

class StudentUpdate(BaseModel):
    name:Annotated[Optional[str],Field(default=None)]
    age: Annotated[Optional[int], Field(default=None)]
    city: Annotated[Optional[str], Field(default=None)]

@app.get("/students")
def get_student():
    """this function is used to get a student from the database"""
    result= [
        {**student,"_id":str(student["_id"])}
        for student in students.find()
    ]

    return result


@app.post("/students")
def create_student(student:Student):
    students.insert_one(student.model_dump())

    return {
        JSONResponse(status_code=201,content={"message":"student is created successfully"})
    }


# READ ONE
@app.get("/students/{student_id}")
def get_student(student_id: str):
    if not ObjectId.is_valid(student_id):
        raise HTTPException(status_code=400, detail="Invalid student ID")

    student = students.find_one({"_id": ObjectId(student_id)})

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    student["_id"] = str(student["_id"])
    return student

@app.put("/edit/{student_id}")
def update_student(student_id:str,student:StudentUpdate):
    if not ObjectId.is_valid(student_id):
        raise HTTPException(status_code=400,detail="student not found")

    student=students.update_one(
        {"_id":ObjectId(student_id)},
        {"$set":student.model_dump()}
    )

    if student.matched_count==0:
        raise HTTPException(status_code=404,detail="student not found")

    return {
        JSONResponse(status_code=200,content={"message":"student updated successfully"})
    }

# delete api
@app.delete("/delete/{student_id}")
def delete_student(student_id:str):
    if not ObjectId.is_valid(student_id):
        raise HTTPException(status_code=400,detail="student not found")

    student=students.delete_one({"_id":ObjectId(student_id)})

    if student.deleted_count==0:
        raise HTTPException(status_code=404,detail="student not found")

    return{
        JSONResponse(status_code=200,content={"message":"student deleted successfully"})
    }

# PATCH: Update specific student fields
@app.patch("/students/{student_id}")
def patch_student(student_id: str, student: dict):
    if not ObjectId.is_valid(student_id):
        raise HTTPException(status_code=400, detail="Invalid student ID")

    result = students.update_one(
        {"_id": ObjectId(student_id)},
        {"$set": student}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")

    return {"message": "Student updated successfully"}