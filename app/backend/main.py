from fastapi import FastAPI

app = FastAPI()


@app.get("/hello/{message}")
async def index(message: str):
    return {"message": message}
