from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def test():
    return {"message": "Hello World"}


@app.get("/login")
async def login():
    return {"message": f"Hello {name}"}


@app.get("/formfill")
async def form():
    return {"message": f"Hello {name}"}


@app.get("/predictor")
async def grade_predict():
    return {"message": f"Hello {name}"}
