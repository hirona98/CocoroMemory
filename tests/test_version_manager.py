"""
バージョン管理機能のテスト
"""

import asyncio
import pytest
from unittest.mock import patch, MagicMock

from src.version_manager import VersionManager, initialize_version_management_async, CURRENT_VERSION, compare_versions


class TestVersionComparison:
    """バージョン比較関数のテスト"""

    def test_compare_versions_equal(self):
        """同じバージョンの比較"""
        assert compare_versions("3.0.1", "3.0.1") == 0
        assert compare_versions("1.0.0", "1.0.0") == 0

    def test_compare_versions_greater(self):
        """大きいバージョンの比較"""
        assert compare_versions("3.1.0", "3.0.1") == 1
        assert compare_versions("3.0.2", "3.0.1") == 1
        assert compare_versions("4.0.0", "3.9.9") == 1

    def test_compare_versions_lesser(self):
        """小さいバージョンの比較"""
        assert compare_versions("3.0.1", "3.1.0") == -1
        assert compare_versions("3.0.1", "3.0.2") == -1
        assert compare_versions("2.9.9", "3.0.0") == -1

    def test_compare_versions_different_length(self):
        """異なる長さのバージョン比較"""
        assert compare_versions("3.0", "3.0.0") == -1
        assert compare_versions("3.0.0", "3.0") == 1


class TestVersionManager:
    """VersionManagerクラスのテスト"""

    @pytest.fixture
    def version_manager(self):
        """VersionManagerインスタンスを作成"""
        return VersionManager(db_host="localhost", db_port=5433)

    @patch('src.version_manager.psycopg2.connect')
    def test_table_exists_true(self, mock_connect, version_manager):
        """バージョン管理テーブルが存在する場合のテスト"""
        # モックの設定
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = [True]

        # テスト実行
        result = version_manager.table_exists()

        # 検証
        assert result is True
        mock_cursor.execute.assert_called_once()

    @patch('src.version_manager.psycopg2.connect')
    def test_table_exists_false(self, mock_connect, version_manager):
        """バージョン管理テーブルが存在しない場合のテスト"""
        # モックの設定
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = [False]

        # テスト実行
        result = version_manager.table_exists()

        # 検証
        assert result is False

    @patch('src.version_manager.psycopg2.connect')
    def test_create_version_table(self, mock_connect, version_manager):
        """バージョン管理テーブル作成のテスト"""
        # モックの設定
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        # テスト実行
        version_manager.create_version_table()

        # 検証
        mock_connect.assert_called_once()
        assert mock_cursor.execute.call_count >= 3  # テーブル作成 + インデックス作成
        mock_conn.commit.assert_called_once()

    @patch('src.version_manager.psycopg2.connect')
    def test_is_version_recorded_true(self, mock_connect, version_manager):
        """バージョンが記録済みの場合のテスト"""
        # モックの設定
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = [1]  # 1件存在

        # テスト実行
        result = version_manager.is_version_recorded("3.0.1")

        # 検証
        assert result is True
        mock_cursor.execute.assert_called_once()

    @patch('src.version_manager.psycopg2.connect')
    def test_is_version_recorded_false(self, mock_connect, version_manager):
        """バージョンが未記録の場合のテスト"""
        # モックの設定
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = [0]  # 0件

        # テスト実行
        result = version_manager.is_version_recorded("3.0.1")

        # 検証
        assert result is False

    @patch('src.version_manager.psycopg2.connect')
    def test_record_version_new(self, mock_connect, version_manager):
        """新しいバージョンの記録テスト"""
        # モックの設定
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        
        # is_version_recordedのモック（未記録を返す）
        with patch.object(version_manager, 'is_version_recorded', return_value=False):
            # テスト実行
            result = version_manager.record_version("3.0.1", "テストバージョン")

            # 検証
            assert result is True
            mock_cursor.execute.assert_called_once()
            mock_conn.commit.assert_called_once()

    @patch('src.version_manager.psycopg2.connect')
    def test_record_version_already_exists(self, mock_connect, version_manager):
        """既存バージョンの記録テスト"""
        # is_version_recordedのモック（記録済みを返す）
        with patch.object(version_manager, 'is_version_recorded', return_value=True):
            # テスト実行
            result = version_manager.record_version("3.0.1", "テストバージョン")

            # 検証
            assert result is False

    @patch('src.version_manager.psycopg2.connect')
    def test_get_current_db_version(self, mock_connect, version_manager):
        """現在のDBバージョン取得のテスト"""
        # モックの設定
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = {"version": "3.0.1"}

        # テスト実行
        result = version_manager.get_current_db_version()

        # 検証
        assert result == "3.0.1"
        mock_cursor.execute.assert_called_once()

    @patch('src.version_manager.psycopg2.connect')
    def test_get_current_db_version_none(self, mock_connect, version_manager):
        """DBバージョンが存在しない場合のテスト"""
        # モックの設定
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None

        # テスト実行
        result = version_manager.get_current_db_version()

        # 検証
        assert result is None

    @patch('src.version_manager.psycopg2.connect')
    def test_get_version_history(self, mock_connect, version_manager):
        """バージョン履歴取得のテスト"""
        # モックの設定
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        
        # サンプルデータ
        sample_history = [
            {"version": "3.0.1", "applied_at": "2025-07-03", "description": "最新版"},
            {"version": "3.0.0", "applied_at": "2025-07-01", "description": "初回版"},
        ]
        mock_cursor.fetchall.return_value = sample_history

        # テスト実行
        result = version_manager.get_version_history()

        # 検証
        assert len(result) == 2
        assert result[0]["version"] == "3.0.1"
        assert result[1]["version"] == "3.0.0"

    def test_initialize_version_management_success(self, version_manager):
        """バージョン管理初期化の成功テスト"""
        with patch.object(version_manager, 'create_version_table') as mock_create, \
             patch.object(version_manager, 'record_version', return_value=True) as mock_record, \
             patch.object(version_manager, 'get_current_db_version', return_value="3.0.1") as mock_get:
            
            # テスト実行
            result = version_manager.initialize_version_management("3.0.1", "テスト")

            # 検証
            assert result is True
            mock_create.assert_called_once()
            mock_record.assert_called_once_with("3.0.1", "テスト")
            mock_get.assert_called_once()

    def test_initialize_version_management_with_defaults(self, version_manager):
        """デフォルトパラメータでの初期化テスト"""
        with patch.object(version_manager, 'create_version_table') as mock_create, \
             patch.object(version_manager, 'record_version', return_value=True) as mock_record, \
             patch.object(version_manager, 'get_current_db_version', return_value=CURRENT_VERSION) as mock_get:
            
            # テスト実行
            result = version_manager.initialize_version_management()

            # 検証
            assert result is True
            mock_create.assert_called_once()
            mock_record.assert_called_once()
            # デフォルトバージョンとデフォルト説明文が使われているか確認
            args, _ = mock_record.call_args
            assert args[0] == CURRENT_VERSION
            assert "CocoroMemory バージョン" in args[1]


class TestInitializeVersionManagementAsync:
    """非同期バージョン管理初期化のテスト"""

    @pytest.mark.asyncio
    async def test_initialize_version_management_async_success(self):
        """非同期初期化の成功テスト"""
        with patch('src.version_manager.VersionManager') as mock_vm_class:
            mock_vm = MagicMock()
            mock_vm.initialize_version_management.return_value = True
            mock_vm_class.return_value = mock_vm

            # テスト実行
            result = await initialize_version_management_async(
                db_host="localhost",
                db_port=5433,
                version="3.0.1",
                description="非同期テスト"
            )

            # 検証
            assert result is True
            mock_vm_class.assert_called_once_with(db_host="localhost", db_port=5433)
            mock_vm.initialize_version_management.assert_called_once_with(
                version="3.0.1", 
                description="非同期テスト"
            )

    @pytest.mark.asyncio
    async def test_initialize_version_management_async_failure(self):
        """非同期初期化の失敗テスト"""
        with patch('src.version_manager.VersionManager') as mock_vm_class:
            mock_vm = MagicMock()
            mock_vm.initialize_version_management.return_value = False
            mock_vm_class.return_value = mock_vm

            # テスト実行
            result = await initialize_version_management_async()

            # 検証
            assert result is False