import argparse
import atexit
import logging
import os
import signal
import sys
import threading
from logging.handlers import RotatingFileHandler
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI

# PyInstaller用の隠れたインポート（実行時は影響なし）
try:
    import pyinstaller_imports  # noqa: F401
except ImportError:
    pass

try:
    # パッケージとして実行される場合（pytest等）
    from .config_loader import load_config
    from .db_migration import run_migration
    from .litellm_chatmemory import LiteLLMChatMemory
    from .postgres_manager import PostgresManager, get_short_path_name
    from .version_manager import (
        VersionManager,
        compare_versions,
        initialize_version_management_async,
    )
except ImportError:
    # 直接実行される場合

    from config_loader import load_config
    from db_migration import run_migration
    from litellm_chatmemory import LiteLLMChatMemory
    from postgres_manager import PostgresManager, get_short_path_name
    from version_manager import (
        VersionManager,
        compare_versions,
        initialize_version_management_async,
    )

# .envファイルから環境変数を読み込む
load_dotenv()

# ログディレクトリの設定
if getattr(sys, "frozen", False):
    # PyInstallerでパッケージ化されている場合
    log_dir = Path(getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))).parent / "Logs"
else:
    # 開発環境の場合
    log_dir = Path(__file__).parent.parent / "Logs"

log_dir.mkdir(exist_ok=True)

# ロギングの設定
log_file = log_dir / "cocoro_memory.log"

# 日本語パス対策: RotatingFileHandlerは短いパス名を使用
try:
    short_log_file = get_short_path_name(str(log_file))
    handlers = [
        RotatingFileHandler(
            short_log_file, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
        ),
        logging.StreamHandler(sys.stdout)
        if not getattr(sys, "frozen", False) or sys.stdout
        else logging.NullHandler(),
    ]
except Exception as e:
    # ログファイルが作成できない場合は標準出力のみ
    print(f"警告: ログファイルの作成に失敗しました: {e}")
    handlers = [logging.StreamHandler(sys.stdout)]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=handlers,
)
logger = logging.getLogger(__name__)


def create_app(config_dir=None):
    """CocoroMemory アプリケーションを作成する関数

    Args:
    ----
        config_dir (str, optional): 設定ディレクトリのパス. デフォルトはNone.

    Returns:
    -------
        tuple: (FastAPI アプリケーション, ポート番号, PostgresManager インスタンス,
                シャットダウンイベント)

    """
    # 設定ファイルを読み込む
    config = load_config(config_dir)

    # setting.jsonから値を取得
    character_list = config.get("characterList", [])
    current_char_index = config.get("currentCharacterIndex", 0)

    # 有効なキャラクターが存在するかチェック
    current_user_id = None  # マイグレーション用のuser_id
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
        postgres_port = 5432  # デフォルトのPostgreSQLポート
    else:
        current_char = character_list[current_char_index]
        current_user_id = current_char.get("userId")  # 現在のキャラクターのuserIdを取得
        llm_api_key = current_char.get("apiKey")
        llm_model = current_char.get("llmModel", "openai/gpt-4o-mini")
        embedded_api_key = current_char.get(
            "embeddedApiKey", llm_api_key
        )  # デフォルトはLLMのAPIキー
        embedded_model = current_char.get("embeddedModel", "openai/text-embedding-3-small")
        memory_port = config.get("cocoroMemoryPort", 55602)
        postgres_port = config.get("cocoroMemoryDBPort", 5432)  # PostgreSQLポート設定を追加
        # APIキーが設定ファイルにない場合はエラー
        if not llm_api_key:
            raise ValueError("APIキーが設定ファイルにもOPENAI_API_KEY環境変数にも見つかりません")

    # PostgreSQLサーバーを起動
    pg_manager = PostgresManager(port=postgres_port)
    pg_manager.initialize_db()
    pg_manager.start_server()

    # データベースマイグレーションを実行（バージョン管理テーブルの有無で判定）
    if current_user_id:
        try:
            # バージョン管理テーブルの存在を確認（テーブル作成前にチェック）
            vm = VersionManager(db_host="127.0.0.1", db_port=postgres_port)

            if not vm.table_exists():
                logger.info("バージョン管理テーブルが存在しないため、マイグレーションを実行します")
                should_migrate = True
            else:
                logger.info(
                    "バージョン管理テーブルが既に存在するため、マイグレーションをスキップします"
                )
                should_migrate = False

            if should_migrate:
                import asyncio

                # 既存のイベントループを取得、なければ新規作成
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_closed():
                        raise RuntimeError("Event loop is closed")
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)

                migration_executed = loop.run_until_complete(
                    run_migration(
                        db_host="127.0.0.1",
                        db_port=postgres_port,
                        current_user_id=current_user_id,
                    )
                )
                if migration_executed:
                    logger.info("データベースマイグレーションが完了しました。")
                else:
                    logger.info("マイグレーション処理は成功しましたが、既に適用済みでした。")
        except Exception as e:
            logger.error(f"マイグレーション処理中にエラーが発生しました: {e}")
            # マイグレーションエラーは致命的でないため続行
    else:
        logger.info("current_user_idが設定されていないため、マイグレーションをスキップします。")

    # バージョン管理の初期化（マイグレーション後に実行）
    try:
        import asyncio

        # 既存のイベントループを取得、なければ新規作成
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                raise RuntimeError("Event loop is closed")
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        version_initialized = loop.run_until_complete(
            initialize_version_management_async(
                db_host="127.0.0.1",
                db_port=postgres_port,
            )
        )
        if version_initialized:
            logger.info("バージョン管理が初期化されました")
        else:
            logger.warning("バージョン管理の初期化に失敗しました")
    except Exception as e:
        logger.error(f"バージョン管理の初期化中にエラーが発生しました: {e}")
        # バージョン管理エラーは致命的でないため続行

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

    # シャットダウンイベントを作成
    shutdown_event = threading.Event()

    # シャットダウンエンドポイントを追加
    @app.post("/api/control")
    async def control_endpoint(request: dict):
        """制御用エンドポイント

        Args:
            request (dict): リクエストボディ
                - command: "shutdown" でシャットダウン

        Returns:
            dict: レスポンス
        """
        command = request.get("command")
        if command == "shutdown":
            logger.info("REST API経由でシャットダウンリクエストを受信しました")
            # 非同期でシャットダウンイベントをセット
            threading.Thread(target=lambda: shutdown_event.set()).start()
            return {"status": "success", "message": "Shutdown initiated"}
        else:
            return {"status": "error", "message": f"Unknown command: {command}"}

    # ヘルスチェックエンドポイントを追加
    @app.get("/health")
    async def health_check():
        """ヘルスチェックエンドポイント

        Returns:
            dict: サービスの状態
        """
        from datetime import datetime

        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {"database": "running", "chatmemory": "running"},
        }

    return app, memory_port, pg_manager, shutdown_event


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
    app, port, pg_manager, shutdown_event = create_app(args.config_dir)

    # アプリケーション終了時にPostgreSQLサーバーを停止するよう登録
    atexit.register(pg_manager.stop_server)

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
        from uvicorn import Config, Server

        # Uvicornサーバーのカスタム設定
        def run_server():
            config = Config(app=app, host="127.0.0.1", port=port)

            # コンソールなしモードでの特別な設定
            if getattr(sys, "frozen", False) and not sys.stdout:
                # Windows GUIモードの場合、uvicornのロギングを無効化
                from uvicorn.config import LOGGING_CONFIG

                uvicorn_log_config = LOGGING_CONFIG.copy()
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
