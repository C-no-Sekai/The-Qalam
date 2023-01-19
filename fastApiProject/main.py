from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from db_setup import DBSetup
from support_functions import *
import threading


class Validation(BaseModel):
    login: str = None
    password: str = None
    section: str = None

    class Config:
        orm_mode = True


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
)

dbHandler = DBSetup('my_db.db')


# This is the function that will be called when the user clicks on the "Register" button
def add_user(input_data: Validation):
    if not all(input_data.dict().values()):
        return
    # Verify that the user doesn't already exist
    if dbHandler.exists(input_data.login, input_data.password):
        return
    # Verify credentials from Qalam
    valid, name = verify_credentials(input_data.login, input_data.password)
    if not valid:
        return
    # Add user to database
    dbHandler.add_user(input_data.login, input_data.password, name, input_data.section)


@app.post("/validate")
async def starter(input_data: Validation):
    if dbHandler.exists(input_data.login, input_data.password):
        return {'result': True}
    return {'result': False}


@app.post("/addUser")
async def starter(input_data: Validation):
    threading.Thread(target=lambda: add_user(input_data)).start()
    return {'result': 'pending'}


@app.get("/")
async def root():
    return {"message": "Hello World", "value": False}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
