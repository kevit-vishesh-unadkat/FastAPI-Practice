from fastapi import HTTPException
from sqlalchemy.util.typing import Annotated
from fastapi import FastAPI 
from pydantic import BaseModel

app=FastAPI()

class Book(BaseModel):
    title:str
    author:str
    pages:int

books = [
    {"id": 1, "title": "Python Basics", "author": "Real P.", "pages": 635},
    {"id": 2, "title": "Breaking the Rules", "author": "Stephen G.", "pages": 99},
]

@app.get("/")
def greet():
    return "Hello From Vishesh Unadkat"

@app.get("/books")
def get_books():
    """this function is use to get al book from database"""
    return {
        "books":books,
        "count":len(books)
    }

@app.get("/books/{book_id}")
def get_book_by_id(book_id:int):
    """this function is use to fetch a book by id"""

    for book in books:
        if book["id"]==book_id:
            return book
    raise HTTPException(status_code=404,detail="book is not found")