from fastapi import FastAPI,HTTPException,Depends,Header
from jose import jwt
from datetime import datetime,timedelta,timezone

app=FastAPI()

SECRET_KEY="mysecretkey"

ALGORITHM="HS256"

def create_token(data:dict):
    to_encode=data.copy()
    expire=datetime.now(timezone.utc) +timedelta(minutes=30)
    to_encode.update({
        "exp":expire
    })
    token=jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)

    return token

# Login API (Token Generate)

@app.post("/login")
def login(username:str,password:str):
    if username!="admin" and password!="1234":
        raise HTTPException(status_code=401,detail="Incorrect username or password")

    token=create_token({
        "sub":username
    })

    return {
        "access_token":token
    }

#Token Varification

def varify_token(token:str=Header(None)):

    try:
        payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        return payload
    except:
        raise HTTPException(status_code=404,detail="Invalid and expired token")


# Protected Route
@app.get("/greet")
def greeting(user=Depends(varify_token)):
    return {
        "message":"Secure Data Accessed",
        "user":user
    }