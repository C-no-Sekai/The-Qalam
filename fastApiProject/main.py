from fastapi import FastAPI
from test import data_function

app = FastAPI()


@app.get("/dataRequest")
async def data_req():
    return data_function()
