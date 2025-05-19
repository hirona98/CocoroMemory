import atexit
import os
import sys

from chatmemory import ChatMemory
from dotenv import load_dotenv
from fastapi import FastAPI

from postgres_manager import PostgresManager

# .envファイルから環境変数を読み込む
load_dotenv()

# 環境変数からAPIキーを取得
api_key = os.getenv("OPENAI_API_KEY")
if api_key is None:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

# PostgreSQLサーバーを起動
pg_manager = PostgresManager()
pg_manager.initialize_db()
pg_manager.start_server()

# アプリケーション終了時にPostgreSQLサーバーを停止するよう登録
atexit.register(pg_manager.stop_server)

cm = ChatMemory(
    openai_api_key=api_key,
    llm_model="gpt-4o-mini",
    # Your PostgreSQL configurations
    db_name="postgres",
    db_user="postgres",
    db_password="postgres",
    db_host="127.0.0.1",
    db_port=5433,
)

app = FastAPI()
app.include_router(cm.get_router())

# スクリプトが直接実行された場合、uvicornを起動
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
