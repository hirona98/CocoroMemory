import argparse
import atexit
import os
import sys

from dotenv import load_dotenv
from fastapi import FastAPI

from config_loader import load_config
from litellm_chatmemory import LiteLLMChatMemory
from postgres_manager import PostgresManager

# .envファイルから環境変数を読み込む
load_dotenv()


def create_app(config_dir=None):
    """CocoroMemory アプリケーションを作成する関数

    Args:
    ----
        config_dir (str, optional): 設定ディレクトリのパス. デフォルトはNone.

    Returns:
    -------
        tuple: (FastAPI アプリケーション, ポート番号, PostgresManager インスタンス)

    """
    # 設定ファイルを読み込む
    config = load_config(config_dir)

    # setting.jsonから値を取得
    character_list = config.get("characterList", [])
    current_char_index = config.get("currentCharacterIndex", 0)

    # 有効なキャラクターが存在するかチェック
    if not character_list or current_char_index >= len(character_list):
        # 設定ファイルが不完全な場合は環境変数から読み込む
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key is None:
            raise ValueError(
                "設定ファイルが見つからないか不完全で、OPENAI_API_KEY環境変数も設定されていません"
            )
        llm_api_key = api_key
        llm_model = "openai/gpt-4o-mini"
        memory_port = 55602
    else:
        current_char = character_list[current_char_index]
        llm_api_key = current_char.get("apiKey")
        llm_model = current_char.get("llmModel", "openai/gpt-4o-mini")
        memory_port = config.get("cocoroMemoryPort", 55602)
        # APIキーが設定ファイルにない場合はエラー
        if not llm_api_key:
            raise ValueError("APIキーが設定ファイルにもOPENAI_API_KEY環境変数にも見つかりません")

    # PostgreSQLサーバーを起動
    pg_manager = PostgresManager()
    pg_manager.initialize_db()
    pg_manager.start_server()

    # LiteLLMChatMemory インスタンスを作成
    cm = LiteLLMChatMemory(
        llm_model=llm_model,
        api_key=llm_api_key,
        # PostgreSQL設定
        db_name="postgres",
        db_user="postgres",
        db_password="postgres",  # noqa: S106
        db_host="127.0.0.1",
        db_port=5433,  # PostgreSQLのポート（ChatMemoryのポートとは別）
    )

    app = FastAPI()
    app.include_router(cm.get_router())

    return app, memory_port, pg_manager


def main():
    """CocoroMemory サーバーのメインエントリポイント"""
    # コマンドライン引数を解析
    parser = argparse.ArgumentParser(description="CocoroMemory Server")
    parser.add_argument("folder_path", nargs="?", help="設定ファイルのフォルダパス（省略可）")
    parser.add_argument("--config-dir", "-c", help="設定ファイルのディレクトリパス")
    args = parser.parse_args()

    # フォルダパスが位置引数で渡された場合は--config-dirより優先
    if args.folder_path:
        args.config_dir = args.folder_path

    # アプリケーションを作成
    app, port, pg_manager = create_app(args.config_dir)

    # アプリケーション終了時にPostgreSQLサーバーを停止するよう登録
    atexit.register(pg_manager.stop_server)

    # 設定情報のログ出力
    print("CocoroMemory を起動します")
    config_dir = "(デフォルト)" if not args.config_dir else args.config_dir
    print(f"設定ディレクトリ: {config_dir}")
    print(f"使用ポート: {port}")

    # サーバー起動
    try:
        import uvicorn

        uvicorn.run(app, host="127.0.0.1", port=port)
    except Exception as e:
        print(f"サーバー起動エラー: {e}")
        import traceback

        traceback.print_exc()
        # EXE実行時などのエラー処理
        if getattr(sys, "frozen", False):
            import time

            print("5秒後に自動終了します...")
            time.sleep(5)
        else:
            input("Enterキーを押すと終了します...")


# スクリプトが直接実行された場合
if __name__ == "__main__":
    main()
