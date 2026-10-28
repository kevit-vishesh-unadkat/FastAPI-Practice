from bson.json_util import default
from sqlalchemy.util.typing import Annotated
from typing import Literal
from pydantic import Field,EmailStr
from pydantic import BaseModel

UserRole=Literal['admin','organizer','staff','attendee']

class CreateUser(BaseModel):
    email:EmailStr
    name:Annotated[str,Field(...,min_length=2,max_length=100)]

class UserUpdate(BaseModel):
    email:EmailStr|None=None
    name:Annotated[str,Field(default=None,min_length=2,max_length=100)]|None=None
    is_active:bool|None=None

class UserRead(BaseModel):
    id:str
    email:EmailStr
    name:str
    role:UserRole
    is_active:bool
