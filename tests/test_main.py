"""main.py のテスト"""

import json
import os
import tempfile
import threading
from unittest.mock import Mock, patch

import pytest
from fastapi import APIRouter
from fastapi.testclient import TestClient

from main import create_app


class TestCreateApp:
    """create_app 関数のテスト"""

    def setup_method(self):
        """各テストメソッドの前に実行されるセットアップ"""
        self.temp_dir = tempfile.mkdtemp()

    @patch("main.PostgresManager")
    @patch("main.LiteLLMChatMemory")
    def test_create_app_with_config_file(
        self, mock_chatmemory, mock_postgres_manager
    ):
        """設定ファイルが存在する場合のアプリ作成をテスト"""
        # モックの設定
        mock_pg_instance = Mock()
        mock_postgres_manager.return_value = mock_pg_instance

        mock_cm_instance = Mock()
        mock_cm_instance.get_router.return_value = APIRouter()
        mock_chatmemory.return_value = mock_cm_instance


        # 設定ファイルを作成
        config = {
            "characterList": [
                {
                    "apiKey": "test-api-key",
                    "llmModel": "openai/gpt-4o-mini",
                    "embeddedApiKey": "test-embed-key",
                    "embeddedModel": "openai/text-embedding-3-small",
                }
            ],
            "currentCharacterIndex": 0,
            "cocoroMemoryPort": 55602,
            "cocoroMemoryDBPort": 5432,
            "cocoroNotificationApiPort": 55604,
        }

        config_file = os.path.join(self.temp_dir, "setting.json")
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False)

        # アプリを作成
        app, port, pg_manager, shutdown_event = create_app(self.temp_dir)

        # 検証
        assert port == 55602
        assert isinstance(shutdown_event, threading.Event)
        mock_postgres_manager.assert_called_once_with(port=5432)
        mock_pg_instance.initialize_db.assert_called_once()
        mock_pg_instance.start_server.assert_called_once()

    @patch("main.PostgresManager")
    @patch("main.LiteLLMChatMemory")
    @patch.dict(os.environ, {"OPENAI_API_KEY": "env-api-key"})
    def test_create_app_without_config_file(
        self, mock_chatmemory, mock_postgres_manager
    ):
        """設定ファイルが存在しない場合のアプリ作成をテスト"""
        # モックの設定
        mock_pg_instance = Mock()
        mock_postgres_manager.return_value = mock_pg_instance

        mock_cm_instance = Mock()
        mock_cm_instance.get_router.return_value = APIRouter()
        mock_chatmemory.return_value = mock_cm_instance


        # 存在しないディレクトリを指定
        app, port, pg_manager, shutdown_event = create_app("/nonexistent/path")

        # 検証
        assert port == 55602  # デフォルト値
        mock_chatmemory.assert_called_once()
        # 環境変数からAPIキーが読み込まれることを確認
        args, kwargs = mock_chatmemory.call_args
        assert kwargs["api_key"] == "env-api-key"

    @patch("main.PostgresManager")
    @patch("main.LiteLLMChatMemory")
    def test_create_app_missing_api_key(
        self, mock_chatmemory, mock_postgres_manager
    ):
        """APIキーが設定されていない場合のエラーをテスト"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="OPENAI_API_KEY環境変数も設定されていません"):
                create_app("/nonexistent/path")

    @patch("main.PostgresManager")
    @patch("main.LiteLLMChatMemory")
    def test_create_app_invalid_character_index(
        self, mock_chatmemory, mock_postgres_manager
    ):
        """無効なキャラクターインデックスの場合のテスト"""
        # モックの設定
        mock_pg_instance = Mock()
        mock_postgres_manager.return_value = mock_pg_instance

        mock_cm_instance = Mock()
        mock_cm_instance.get_router.return_value = APIRouter()
        mock_chatmemory.return_value = mock_cm_instance


        # 無効なインデックスを持つ設定ファイルを作成
        config = {
            "characterList": [{"apiKey": "test-api-key", "llmModel": "openai/gpt-4o-mini"}],
            "currentCharacterIndex": 5,  # 無効なインデックス
        }

        config_file = os.path.join(self.temp_dir, "setting.json")
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False)

        # 環境変数を設定
        with patch.dict(os.environ, {"OPENAI_API_KEY": "env-api-key"}):
            app, port, pg_manager, shutdown_event = create_app(self.temp_dir)

            # デフォルト値が使用されることを確認
            assert port == 55602

    @patch("main.PostgresManager")
    @patch("main.LiteLLMChatMemory")
    def test_create_app_missing_api_key_in_config(
        self, mock_chatmemory, mock_postgres_manager
    ):
        """設定ファイルにAPIキーがない場合のエラーをテスト"""
        # APIキーが設定されていない設定ファイルを作成
        config = {
            "characterList": [
                {
                    "llmModel": "openai/gpt-4o-mini"
                    # apiKeyが設定されていない
                }
            ],
            "currentCharacterIndex": 0,
        }

        config_file = os.path.join(self.temp_dir, "setting.json")
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False)

        with pytest.raises(
            ValueError, match="APIキーが設定ファイルにもOPENAI_API_KEY環境変数にも見つかりません"
        ):
            create_app(self.temp_dir)


class TestAppEndpoints:
    """FastAPIエンドポイントのテスト"""

    def setup_method(self):
        """各テストメソッドの前に実行されるセットアップ"""
        self.temp_dir = tempfile.mkdtemp()

    @patch("main.PostgresManager")
    @patch("main.LiteLLMChatMemory")
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key"})
    def test_health_check_endpoint(
        self, mock_chatmemory, mock_postgres_manager
    ):
        """ヘルスチェックエンドポイントのテスト"""
        # モックの設定
        mock_pg_instance = Mock()
        mock_postgres_manager.return_value = mock_pg_instance

        mock_cm_instance = Mock()
        mock_cm_instance.get_router.return_value = APIRouter()
        mock_chatmemory.return_value = mock_cm_instance


        app, _, _, _ = create_app()
        client = TestClient(app)

        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert data["services"]["chatmemory"] == "running"
        assert data["services"]["database"] == "running"

    @patch("main.PostgresManager")
    @patch("main.LiteLLMChatMemory")
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key"})
    def test_control_endpoint_shutdown(
        self, mock_chatmemory, mock_postgres_manager
    ):
        """制御エンドポイントのシャットダウンコマンドテスト"""
        # モックの設定
        mock_pg_instance = Mock()
        mock_postgres_manager.return_value = mock_pg_instance

        mock_cm_instance = Mock()
        mock_cm_instance.get_router.return_value = APIRouter()
        mock_chatmemory.return_value = mock_cm_instance


        app, _, _, shutdown_event = create_app()
        client = TestClient(app)

        response = client.post("/api/control", json={"command": "shutdown"})

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["message"] == "Shutdown initiated"

        # シャットダウンイベントがセットされるまで少し待つ
        import time

        time.sleep(0.1)
        assert shutdown_event.is_set()

    @patch("main.PostgresManager")
    @patch("main.LiteLLMChatMemory")
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key"})
    def test_control_endpoint_unknown_command(
        self, mock_chatmemory, mock_postgres_manager
    ):
        """制御エンドポイントの不明なコマンドテスト"""
        # モックの設定
        mock_pg_instance = Mock()
        mock_postgres_manager.return_value = mock_pg_instance

        mock_cm_instance = Mock()
        mock_cm_instance.get_router.return_value = APIRouter()
        mock_chatmemory.return_value = mock_cm_instance


        app, _, _, _ = create_app()
        client = TestClient(app)

        response = client.post("/api/control", json={"command": "unknown"})

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error"
        assert "Unknown command" in data["message"]

    @patch("main.PostgresManager")
    @patch("main.LiteLLMChatMemory") 
    @patch("main.run_migration")
    def test_create_app_migration_success(
        self, mock_run_migration, mock_chatmemory, mock_postgres_manager
    ):
        """マイグレーション成功のテスト"""
        # モックの設定
        mock_pg_instance = Mock()
        mock_postgres_manager.return_value = mock_pg_instance

        mock_cm_instance = Mock()
        mock_cm_instance.get_router.return_value = APIRouter()
        mock_chatmemory.return_value = mock_cm_instance


        # マイグレーションが成功する設定
        mock_run_migration.return_value = True

        config_data = {
            "characterList": [{"userId": "test_user", "apiKey": "test-key"}],
            "currentCharacterIndex": 0
        }
        
        with patch("main.load_config", return_value=config_data):
            with patch("asyncio.get_event_loop") as mock_get_loop:
                mock_loop = Mock()
                mock_get_loop.return_value = mock_loop
                mock_loop.is_closed.return_value = False
                
                app, _, _, _ = create_app()
                
                # マイグレーションが実行されたことを確認
                mock_run_migration.assert_called_once()

    @patch("main.PostgresManager")
    @patch("main.LiteLLMChatMemory")
    @patch("main.run_migration")
    def test_create_app_migration_error(
        self, mock_run_migration, mock_chatmemory, mock_postgres_manager
    ):
        """マイグレーションエラーのテスト"""
        # モックの設定
        mock_pg_instance = Mock()
        mock_postgres_manager.return_value = mock_pg_instance

        mock_cm_instance = Mock()
        mock_cm_instance.get_router.return_value = APIRouter()
        mock_chatmemory.return_value = mock_cm_instance


        # マイグレーションでエラーが発生する設定
        mock_run_migration.side_effect = Exception("Migration error")

        config_data = {
            "characterList": [{"userId": "test_user", "apiKey": "test-key"}],
            "currentCharacterIndex": 0
        }
        
        with patch("main.load_config", return_value=config_data):
            with patch("asyncio.get_event_loop") as mock_get_loop:
                mock_loop = Mock()
                mock_get_loop.return_value = mock_loop
                mock_loop.is_closed.return_value = False
                
                # エラーが発生してもアプリが作成されることを確認
                app, _, _, _ = create_app()
                assert app is not None

    @patch("main.PostgresManager")
    @patch("main.LiteLLMChatMemory")
    def test_create_app_no_user_id(
        self, mock_chatmemory, mock_postgres_manager
    ):
        """userIdなしでのアプリ作成テスト"""
        # モックの設定
        mock_pg_instance = Mock()
        mock_postgres_manager.return_value = mock_pg_instance

        mock_cm_instance = Mock()
        mock_cm_instance.get_router.return_value = APIRouter()
        mock_chatmemory.return_value = mock_cm_instance


        config_data = {
            "characterList": [{"apiKey": "test-key"}],  # userIdなし
            "currentCharacterIndex": 0
        }
        
        with patch("main.load_config", return_value=config_data):
            app, _, _, _ = create_app()
            assert app is not None

    @patch("main.PostgresManager")
    @patch("main.LiteLLMChatMemory")
    def test_create_app_invalid_character_index(
        self, mock_chatmemory, mock_postgres_manager
    ):
        """無効なキャラクターインデックスのテスト"""
        # モックの設定
        mock_pg_instance = Mock()
        mock_postgres_manager.return_value = mock_pg_instance

        mock_cm_instance = Mock()
        mock_cm_instance.get_router.return_value = APIRouter()
        mock_chatmemory.return_value = mock_cm_instance


        config_data = {
            "characterList": [{"userId": "test_user", "apiKey": "test-key"}],
            "currentCharacterIndex": 5  # 範囲外
        }
        
        with patch("main.load_config", return_value=config_data):
            with patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key"}):
                app, _, _, _ = create_app()
                assert app is not None

    @patch("main.PostgresManager")
    @patch("main.LiteLLMChatMemory")
    def test_health_endpoint_scheduler_stopped(
        self, mock_chatmemory, mock_postgres_manager
    ):
        """リマインダースケジューラー停止時のヘルスチェックテスト"""
        # モックの設定
        mock_pg_instance = Mock()
        mock_postgres_manager.return_value = mock_pg_instance

        mock_cm_instance = Mock()
        mock_cm_instance.get_router.return_value = APIRouter()
        mock_chatmemory.return_value = mock_cm_instance


        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key"}):
            app, _, _, _ = create_app()
            client = TestClient(app)

            response = client.get("/health")

            assert response.status_code == 200
            data = response.json()

    @patch("main.PostgresManager")
    @patch("main.LiteLLMChatMemory")
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key"})
    def test_control_endpoint_unknown_command(
        self, mock_chatmemory, mock_postgres_manager
    ):
        """制御エンドポイントの不明なコマンドテスト"""
        # モックの設定
        mock_pg_instance = Mock()
        mock_postgres_manager.return_value = mock_pg_instance

        mock_cm_instance = Mock()
        mock_cm_instance.get_router.return_value = APIRouter()
        mock_chatmemory.return_value = mock_cm_instance


        app, _, _, _ = create_app()
        client = TestClient(app)

        response = client.post("/api/control", json={"command": "unknown"})

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error"
        assert "Unknown command: unknown" in data["message"]


@patch("uvicorn.Config")
@patch("uvicorn.Server")
@patch("main.create_app")
def test_main_function(mock_create_app, mock_server, mock_uvicorn_config):
    """main関数のテスト"""
    from main import main

    # モックの設定
    mock_app = Mock()
    mock_pg_manager = Mock()
    mock_shutdown_event = Mock()
    mock_create_app.return_value = (
        mock_app,
        55602,
        mock_pg_manager,
        mock_shutdown_event,
    )

    # Uvicornサーバーのモック設定
    mock_server_instance = Mock()
    mock_server.return_value = mock_server_instance

    # コマンドライン引数をモック
    with patch("sys.argv", ["main.py"]):
        with patch("main.signal.signal"):  # シグナル設定をモック
            with patch("main.atexit.register"):  # atexit.registerをモック
                # サーバー実行時に例外を発生させて終了
                mock_server_instance.run.side_effect = KeyboardInterrupt()

                try:
                    main()
                except KeyboardInterrupt:
                    pass

    # アプリが作成されることを確認
    mock_create_app.assert_called_once()
    # uvicornサーバーが実行されることを確認
    mock_server_instance.run.assert_called_once()
