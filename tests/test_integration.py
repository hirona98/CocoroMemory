"""統合テスト"""

import json
import os
import tempfile
import time
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from main import create_app


class TestIntegration:
    """統合テストクラス"""

    def setup_method(self):
        """各テストメソッドの前に実行されるセットアップ"""
        self.temp_dir = tempfile.mkdtemp()

        # テスト用の設定ファイルを作成
        self.test_config = {
            "characterList": [
                {
                    "apiKey": "test-api-key-for-integration",
                    "llmModel": "openai/gpt-4o-mini",
                    "embeddedApiKey": "test-embed-key-for-integration",
                    "embeddedModel": "openai/text-embedding-3-small",
                }
            ],
            "currentCharacterIndex": 0,
            "cocoroMemoryPort": 55602,
            "cocoroMemoryDBPort": 5432,
            "cocoroNotificationApiPort": 55604,
        }

        self.config_file = os.path.join(self.temp_dir, "setting.json")
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(self.test_config, f, ensure_ascii=False)

    @patch("main.PostgresManager")
    @patch("main.LiteLLMChatMemory")
    def test_full_application_creation(
        self, mock_chatmemory, mock_postgres_manager
    ):
        """アプリケーション全体の作成をテスト"""
        # モックの設定
        mock_pg_instance = self._setup_postgres_mock(mock_postgres_manager)
        self._setup_chatmemory_mock(mock_chatmemory)

        # アプリケーションを作成
        app, port, pg_manager, shutdown_event = create_app(self.temp_dir)

        # 基本的な検証
        assert port == 55602
        assert pg_manager == mock_pg_instance

        # PostgreSQLの初期化と起動が呼ばれることを確認
        mock_pg_instance.initialize_db.assert_called_once()
        mock_pg_instance.start_server.assert_called_once()

        # ChatMemoryの設定確認
        mock_chatmemory.assert_called_once()
        args, kwargs = mock_chatmemory.call_args
        assert kwargs["llm_model"] == "openai/gpt-4o-mini"
        assert kwargs["api_key"] == "test-api-key-for-integration"
        assert kwargs["embedded_api_key"] == "test-embed-key-for-integration"
        assert kwargs["db_port"] == 5432

    @patch("main.PostgresManager")
    @patch("main.LiteLLMChatMemory")
    def test_health_check_integration(
        self, mock_chatmemory, mock_postgres_manager
    ):
        """ヘルスチェックエンドポイントの統合テスト"""
        # モックの設定
        self._setup_postgres_mock(mock_postgres_manager)
        self._setup_chatmemory_mock(mock_chatmemory)

        # アプリケーションを作成
        app, _, _, _ = create_app(self.temp_dir)
        client = TestClient(app)

        # ヘルスチェックを実行
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()

        # レスポンス内容の詳細検証
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert isinstance(data["services"], dict)
        assert data["services"]["chatmemory"] == "running"
        assert data["services"]["database"] == "running"

    @patch("main.PostgresManager")
    @patch("main.LiteLLMChatMemory")
    def test_control_endpoints_integration(
        self, mock_chatmemory, mock_postgres_manager
    ):
        """制御エンドポイントの統合テスト"""
        # モックの設定
        self._setup_postgres_mock(mock_postgres_manager)
        self._setup_chatmemory_mock(mock_chatmemory)

        # アプリケーションを作成
        app, _, _, shutdown_event = create_app(self.temp_dir)
        client = TestClient(app)

        # 正常なシャットダウンコマンド
        response = client.post("/api/control", json={"command": "shutdown"})
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "Shutdown initiated" in data["message"]

        # シャットダウンイベントがセットされるまで待機
        time.sleep(0.1)
        assert shutdown_event.is_set()

        # 不正なコマンド
        response = client.post("/api/control", json={"command": "invalid"})
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error"
        assert "Unknown command" in data["message"]

    @patch("main.PostgresManager")
    @patch("main.LiteLLMChatMemory")
    def test_router_integration(
        self, mock_chatmemory, mock_postgres_manager
    ):
        """ルーターの統合をテスト"""
        # モックの設定
        self._setup_postgres_mock(mock_postgres_manager)
        mock_cm_instance = self._setup_chatmemory_mock(mock_chatmemory)

        # アプリケーションを作成
        app, _, _, _ = create_app(self.temp_dir)

        # ルーターが正しく追加されていることを確認
        mock_cm_instance.get_router.assert_called_once()

    @patch("main.PostgresManager")
    @patch("main.LiteLLMChatMemory")
    @patch.dict(os.environ, {"OPENAI_API_KEY": "env-test-key"})
    def test_environment_variable_fallback_integration(
        self, mock_chatmemory, mock_postgres_manager
    ):
        """環境変数フォールバックの統合テスト"""
        # モックの設定
        self._setup_postgres_mock(mock_postgres_manager)
        self._setup_chatmemory_mock(mock_chatmemory)

        # 設定ファイルが存在しない場合
        app, port, _, _ = create_app("/nonexistent/path")

        # デフォルト値が使用されることを確認
        assert port == 55602

        # 環境変数からAPIキーが読み込まれることを確認
        mock_chatmemory.assert_called_once()
        args, kwargs = mock_chatmemory.call_args
        assert kwargs["api_key"] == "env-test-key"
        assert kwargs["llm_model"] == "openai/gpt-4o-mini"

    @patch("main.PostgresManager")
    @patch("main.LiteLLMChatMemory")
    def test_error_handling_integration(
        self, mock_chatmemory, mock_postgres_manager
    ):
        """エラーハンドリングの統合テスト"""
        # PostgreSQLマネージャーが例外を発生させる場合
        mock_postgres_manager.side_effect = Exception("PostgreSQL initialization failed")

        with pytest.raises(Exception, match="PostgreSQL initialization failed"):
            create_app(self.temp_dir)

    def _setup_postgres_mock(self, mock_postgres_manager):
        """PostgreSQLマネージャーのモックを設定"""
        mock_pg_instance = mock_postgres_manager.return_value
        mock_pg_instance.initialize_db.return_value = None
        mock_pg_instance.start_server.return_value = True
        mock_pg_instance.stop_server.return_value = True
        return mock_pg_instance

    def _setup_chatmemory_mock(self, mock_chatmemory):
        """ChatMemoryのモックを設定"""
        from fastapi import APIRouter

        mock_cm_instance = mock_chatmemory.return_value
        mock_router = APIRouter()
        mock_cm_instance.get_router.return_value = mock_router
        return mock_cm_instance



class TestEndToEndFlow:
    """エンドツーエンドフローのテスト"""

    def setup_method(self):
        """各テストメソッドの前に実行されるセットアップ"""
        self.temp_dir = tempfile.mkdtemp()

    @patch("main.PostgresManager")
    @patch("main.LiteLLMChatMemory")
    def test_application_lifecycle(
        self, mock_chatmemory, mock_postgres_manager
    ):
        """アプリケーションのライフサイクルをテスト"""
        # モックの設定
        mock_pg_instance = mock_postgres_manager.return_value
        mock_pg_instance.initialize_db.return_value = None
        mock_pg_instance.start_server.return_value = True
        mock_pg_instance.stop_server.return_value = True

        mock_cm_instance = mock_chatmemory.return_value
        from fastapi import APIRouter

        mock_cm_instance.get_router.return_value = APIRouter()

        # 環境変数を設定
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            # 1. アプリケーション作成
            app, port, pg_manager, shutdown_event = create_app()

            # 2. アプリケーションが正常に作成されたことを確認
            assert app is not None
            assert port == 55602
            assert pg_manager == mock_pg_instance

            # 3. 必要なサービスが開始されたことを確認
            mock_pg_instance.initialize_db.assert_called_once()
            mock_pg_instance.start_server.assert_called_once()

            # 4. ヘルスチェックが正常に動作することを確認
            client = TestClient(app)
            response = client.get("/health")
            assert response.status_code == 200

            # 5. シャットダウンが正常に動作することを確認
            response = client.post("/api/control", json={"command": "shutdown"})
            assert response.status_code == 200

            # 6. シャットダウンイベントがセットされることを確認
            time.sleep(0.1)
            assert shutdown_event.is_set()

    @patch("main.PostgresManager")
    @patch("main.LiteLLMChatMemory")
    def test_configuration_flow(
        self, mock_chatmemory, mock_postgres_manager
    ):
        """設定の読み込みから適用までのフローをテスト"""
        # カスタム設定を作成
        custom_config = {
            "characterList": [
                {
                    "apiKey": "custom-api-key",
                    "llmModel": "openai/gpt-4",
                    "embeddedApiKey": "custom-embed-key",
                    "embeddedModel": "openai/text-embedding-ada-002",
                }
            ],
            "currentCharacterIndex": 0,
            "cocoroMemoryPort": 55603,
            "cocoroMemoryDBPort": 5434,
            "cocoroNotificationApiPort": 55605,
        }

        config_file = os.path.join(self.temp_dir, "setting.json")
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(custom_config, f, ensure_ascii=False)

        # モックの設定
        mock_pg_instance = mock_postgres_manager.return_value
        mock_pg_instance.initialize_db.return_value = None
        mock_pg_instance.start_server.return_value = True

        mock_cm_instance = mock_chatmemory.return_value
        from fastapi import APIRouter

        mock_cm_instance.get_router.return_value = APIRouter()

        # アプリケーションを作成
        app, port, pg_manager, _ = create_app(self.temp_dir)

        # カスタム設定が正しく適用されたことを確認
        assert port == 55603

        # PostgreSQLマネージャーが正しいポートで作成されたことを確認
        mock_postgres_manager.assert_called_once_with(port=5434)

        # ChatMemoryが正しい設定で作成されたことを確認
        mock_chatmemory.assert_called_once()
        args, kwargs = mock_chatmemory.call_args
        assert kwargs["llm_model"] == "openai/gpt-4"
        assert kwargs["api_key"] == "custom-api-key"
        assert kwargs["embedded_api_key"] == "custom-embed-key"
        assert kwargs["embedded_model"] == "openai/text-embedding-ada-002"
        assert kwargs["db_port"] == 5434
