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
pg_manager.start_server()

# アプリケーション終了時にPostgreSQLサーバーを停止するよう登録
atexit.register(pg_manager.stop_server)

def initialize_db():
    # 実行ファイルのディレクトリを取得
    if getattr(sys, 'frozen', False):
        # PyInstallerでパッケージ化された場合
        base_dir = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    else:
        # 通常のPython実行の場合srcの親ディレクトリを基準にする
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # PostgreSQLバイナリディレクトリのパスを構築
    pg_bin_dir = os.path.join(base_dir, "pgsql", "bin")
    # PyInstaller実行時は _internal/pgsql/bin も見る
    if not os.path.exists(pg_bin_dir) and getattr(sys, 'frozen', False):
        pg_bin_dir = os.path.join(base_dir, "_internal", "pgsql", "bin")
    # コマンドパスを設定
    initdb_cmd = os.path.join(pg_bin_dir, "initdb.exe")
    # 存在確認
    if not os.path.exists(initdb_cmd):
        print(f"Error: initdb.exe not found at {initdb_cmd}")
        print(f"Current directory: {os.getcwd()}")
        print(f"Directory listing: {os.listdir(os.path.dirname(os.path.abspath(__file__)))}")
        if os.path.exists(os.path.join(base_dir, "pgsql")):
            print(f"pgsql directory listing: {os.listdir(os.path.join(base_dir, 'pgsql'))}")
        sys.exit(1)

initialize_db()

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
