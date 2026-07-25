from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

@app.get("/")
def read_root():
    return{ "Message":"Hello Samuel" }

@app.get("/greet")
def greet():
    return{"Message":"Hello Teshale"}

@app.get("/greet{name}")
def greet_name(name:str, age: Optional[int]=None):
    return {"Message":f"Hello {name} are good? you are {age} years old."}


class student(BaseModel):
    name: str
    age: int
    roll: int

@app.post("/create_student")
def create_student(student: student):
    return{
        "name": student.name,
        "age": student.age,
        "roll": student.roll
    }
    