# backend/main.py
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

app = FastAPI()

# CORS フロントエンドとバックエンド間の通信を許可
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    input = req.message

    prompt = PromptTemplate.from_template("""ユーザからの入力に対してドラえもんとして答えて。
    ユーザからの入力：{input}
    """)

    model = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)

    chain = (
        {
            "input": RunnablePassthrough(),
        }
        | prompt
        | model
        | StrOutputParser()
    )

    return ChatResponse(reply=chain.invoke(input))
