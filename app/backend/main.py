from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from endpoints.chat_stream import router as chat_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
