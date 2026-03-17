import asyncio
import json
import os
import requests
from dotenv import load_dotenv

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory

from aiogram import Bot, Dispatcher
from aiogram.types import Update, Message
from openai import OpenAI

# Установите ключи
os.environ["OPENAI_API_KEY"] = "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"
client = OpenAI(api_key="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")
load_dotenv()
OPENAI_API_KEY = "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"
TOKEN = "8742326422:AAGa8Dr9mGg-VCUhF1bq2HmNMUtPXr8jY58"

bot = Bot(TOKEN)
dp = Dispatcher()

# Хранилище истории
store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

# Настройка цепочки LangChain
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an intelligent assistant"),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])

llm = ChatOpenAI(model="gpt-4.1-mini")
chain = prompt | llm

conversational_agent = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history",
)

@dp.message(lambda message: message.text)
async def filter_messages(message: Message):
    config = {"configurable": {"session_id": str(message.from_user.id)}}
    response = conversational_agent.invoke(
        {"input": message.text},
        config=config
    )
    await message.answer(response.content)

# Асинхронный обработчик
async def async_handler(event: dict, context) -> dict:
    body: str = event.get("body", "")
    try:
        update_data = json.loads(body) if body else {}
        update = Update.model_validate(update_data)
        await dp.feed_update(bot, update)
        return {"statusCode": 200, "body": ""}
    except Exception as e:
        return {"statusCode": 500, "body": f"Error: {str(e)}"}

# Синхронная обёртка — это и будет ваша точка входа
def handler(event: dict, context) -> dict:
    """
    Синхронная точка входа для Yandex Cloud.
    Запускает асинхронный обработчик через asyncio.
    """
    return asyncio.run(async_handler(event, context))