# authentication using jwt  , OAuth2

# from fastapi import FastAPI,HTTPException,Depends
# from jose import jwt,JWTError
# from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# from datetime import datetime,timedelta,timezone
# from passlib.context import CryptContext
# from typing_extensions import deprecated
#
# app=FastAPI()
#
# # JWT Config
# SECRET_KEY="mysecret"
# ALGORITHM="HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES=30
#
# # Password hashing setup
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
#
# # OauthSetup
# oauth2_schema=OAuth2PasswordBearer(tokenUrl="login")
#
# # Dummy User Data
#
# fake_user_db={
#     "admin":{
#         "username":"admin",
#         "hashed_password":pwd_context.hash("1234")
#     }
# }
#
# # Hashed Password
# def hashed_password(password:str):
#     return pwd_context.hash(password)
#
# # verify password
# def verify_password(plain_password,hashed_password):
#     return pwd_context.verify(plain_password,hashed_password)
#
# def create_token(data:dict):
#     to_encode=data.copy()
#     expire=datetime.now(timezone.utc) +timedelta(minutes=30)
#     to_encode.update({
#         "exp":expire
#     })
#     token=jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
#
#     return token
#
#
# @app.post("/login")
# def login(form_data:OAuth2PasswordRequestForm=Depends()):
#     user=fake_user_db.get(form_data.username)
#
#     if not user or not verify_password(form_data.password,user["hashed_password"]):
#         raise HTTPException(
#             status_code=401,
#             detail="Incorrect username or password"
#         )
#
#     access_token=create_token({"sub":user["username"]})
#
#     return {
#         "access_token":access_token,
#         "token_type":"bearer"
#     }
#
#
# # verify token
#
# def verify_token(token:str=Depends(oauth2_schema)):
#     try:
#         payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
#         username:str=payload.get("sub")
#         if username is None:
#             raise HTTPException(
#                 status_code=401,
#                 detail="Invalid token"
#             )
#         return username
#
#     except jwt.JWTError:
#         raise HTTPException(
#             status_code=401,
#             detail="Invalid token"
#         )
#
# # Protected route
#
# @app.get("/greet")
# def greeting(username:str=Depends(verify_token)):
#     return {
#         "message"f"Hello {username}!"
#     }





# Authentication using JWT and OAuth2

from fastapi import FastAPI, HTTPException, Depends
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta, timezone
from pwdlib import PasswordHash

app = FastAPI()

# JWT Configuration
SECRET_KEY = "replace-this-with-a-long-random-secret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing setup
password_hash = PasswordHash.recommended()

# OAuth2 Setup
oauth2_schema = OAuth2PasswordBearer(tokenUrl="login")

# Dummy User Database
fake_user_db = {
    "admin": {
        "username": "admin",
        "hashed_password": password_hash.hash("1234")
    }
}


# Hash password
def hashed_password(password: str):
    return password_hash.hash(password)


# Verify password
def verify_password(plain_password: str, hashed_password: str):
    return password_hash.verify(plain_password, hashed_password)


# Create JWT access token
def create_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({"exp": expire})

    token = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token


# Login endpoint
@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):

    user = fake_user_db.get(form_data.username)

    if not user or not verify_password(
        form_data.password,
        user["hashed_password"]
    ):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    access_token = create_token({
        "sub": user["username"]
    })

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# Verify JWT token
def verify_token(token: str = Depends(oauth2_schema)):

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        username = payload.get("sub")

        if username is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"}
            )

        return username

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )


# Protected route
@app.get("/greet")
def greeting(username: str = Depends(verify_token)):
    return {
        "message": f"Hello {username}!"
    }