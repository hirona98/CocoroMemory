import argparse
import atexit
import os
import sys
import logging
import signal
import threading
from logging.handlers import RotatingFileHandler
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI

from config_loader import load_config
from litellm_chatmemory import LiteLLMChatMemory
from postgres_manager import PostgresManager

# .envファイルから環境変数を読み込む
load_dotenv()

# ログディレクトリの設定
if getattr(sys, 'frozen', False):
    # PyInstallerでパッケージ化されている場合
    log_dir = Path(sys._MEIPASS).parent / "Logs"
else:
    # 開発環境の場合
    log_dir = Path(__file__).parent.parent / "Logs"

log_dir.mkdir(exist_ok=True)

# ロギングの設定
log_file = log_dir / "cocoro_memory.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5),
        logging.StreamHandler(sys.stdout) if not getattr(sys, 'frozen', False) or sys.stdout else logging.NullHandler()
    ]
)
logger = logging.getLogger(__name__)


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
        embedded_api_key = api_key  # デフォルトは同じAPIキー
        embedded_model = "openai/text-embedding-3-small"
        memory_port = 55602
        postgres_port = 5433  # デフォルトのPostgreSQLポート
    else:
        current_char = character_list[current_char_index]
        llm_api_key = current_char.get("apiKey")
        llm_model = current_char.get("llmModel", "openai/gpt-4o-mini")
        embedded_api_key = current_char.get(
            "embeddedApiKey", llm_api_key
        )  # デフォルトはLLMのAPIキー
        embedded_model = current_char.get("embeddedModel", "openai/text-embedding-3-small")
        memory_port = config.get("cocoroMemoryPort", 55602)
        postgres_port = config.get("cocoroMemoryDBPort", 5433)  # PostgreSQLポート設定を追加
        # APIキーが設定ファイルにない場合はエラー
        if not llm_api_key:
            raise ValueError("APIキーが設定ファイルにもOPENAI_API_KEY環境変数にも見つかりません")

    # PostgreSQLサーバーを起動
    pg_manager = PostgresManager(port=postgres_port)
    pg_manager.initialize_db()
    pg_manager.start_server()

    # LiteLLMChatMemory インスタンスを作成
    cm = LiteLLMChatMemory(
        llm_model=llm_model,
        api_key=llm_api_key,
        embedded_api_key=embedded_api_key,
        embedded_model=embedded_model,
        # PostgreSQL設定
        db_name="postgres",
        db_user="postgres",
        db_password="postgres",  # noqa: S106
        db_host="127.0.0.1",
        db_port=postgres_port,  # PostgreSQLのポート（ChatMemoryのポートとは別）
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
    
    # シャットダウンイベント
    shutdown_event = threading.Event()
    
    def signal_handler(sig, frame):
        """シグナルハンドラー：Ctrl+CやKillシグナルを受けた時の処理"""
        logger.info(f"シグナル {sig} を受信しました。シャットダウンを開始します...")
        shutdown_event.set()
    
    # Windowsでのシグナル設定
    if sys.platform == "win32":
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGBREAK, signal_handler)  # Windows固有のCTRL+BREAKシグナル
    else:
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    # 設定情報のログ出力
    logger.info("CocoroMemory を起動します")
    config_dir = "(デフォルト)" if not args.config_dir else args.config_dir
    logger.info(f"設定ディレクトリ: {config_dir}")
    logger.info(f"使用ポート: {port}")

    # サーバー起動
    try:
        import uvicorn
        from uvicorn import Server, Config
        
        # Uvicornサーバーのカスタム設定
        def run_server():
            config = Config(app=app, host="127.0.0.1", port=port)
            
            # コンソールなしモードでの特別な設定
            if getattr(sys, "frozen", False) and not sys.stdout:
                # Windows GUIモードの場合、uvicornのロギングを無効化
                uvicorn_log_config = uvicorn.config.LOGGING_CONFIG
                uvicorn_log_config["handlers"]["default"]["class"] = "logging.NullHandler"
                uvicorn_log_config["handlers"]["access"]["class"] = "logging.NullHandler"
                config.log_config = uvicorn_log_config
            
            server = Server(config)
            
            # シャットダウンイベントを監視するスレッド
            def monitor_shutdown():
                shutdown_event.wait()
                logger.info("シャットダウンイベントを検出しました")
                server.should_exit = True
            
            monitor_thread = threading.Thread(target=monitor_shutdown, daemon=True)
            monitor_thread.start()
            
            # サーバーを実行
            server.run()
        
        run_server()
        
    except Exception as e:
        logger.error(f"サーバー起動エラー: {e}", exc_info=True)
        # EXE実行時などのエラー処理
        if getattr(sys, "frozen", False) and sys.stdout:
            import time

            print("5秒後に自動終了します...")
            time.sleep(5)
        elif not getattr(sys, "frozen", False):
            input("Enterキーを押すと終了します...")
    finally:
        # 明示的にPostgreSQLを停止
        logger.info("PostgreSQLサーバーを停止しています...")
        pg_manager.stop_server()


# スクリプトが直接実行された場合
if __name__ == "__main__":
    main()
