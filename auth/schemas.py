from pydantic import BaseModel, EmailStr

# schema for new user create

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str

# schema for user login

class UserLogin(BaseModel):
    username: str
    password: str
