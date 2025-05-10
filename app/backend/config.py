from langchain_openai import ChatOpenAI
from langsmith import Client
import logging

model = ChatOpenAI(model="gpt-4o-mini")
client = Client()

MAX_SPEAK_COUNT = 6

# Logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
