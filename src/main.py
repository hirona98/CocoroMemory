import os
from dotenv import load_dotenv
from fastapi import FastAPI
from chatmemory import ChatMemory

# .envファイルから環境変数を読み込む
load_dotenv()

# 環境変数からAPIキーを取得
api_key = os.getenv("OPENAI_API_KEY")
if api_key is None:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

cm = ChatMemory(
    openai_api_key=api_key,
    llm_model="gpt-4o",
    # Your PostgreSQL configurations
    db_name="postgres",
    db_user="postgres",
    db_password="postgres",
    db_host="127.0.0.1",
    db_port=5432,
)

app = FastAPI()
app.include_router(cm.get_router())
