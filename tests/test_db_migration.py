"""データベースマイグレーションのテスト"""

import pytest
from unittest.mock import AsyncMock, patch
import asyncpg

from db_migration import DatabaseMigration, run_migration


@pytest.mark.asyncio
async def test_check_and_migrate_no_user_id():
    """current_user_idがない場合はマイグレーションをスキップ"""
    migration = DatabaseMigration(
        db_host="localhost",
        db_port=5432,
        current_user_id=None,
    )
    
    result = await migration.check_and_migrate()
    assert result is False


@pytest.mark.asyncio
async def test_check_and_migrate_reminder_table_exists():
    """リマインダーテーブルが存在する場合はマイグレーションをスキップ"""
    migration = DatabaseMigration(
        db_host="localhost",
        db_port=5432,
        current_user_id="test_user",
    )
    
    # モックの接続を作成
    mock_conn = AsyncMock(spec=asyncpg.Connection)
    
    # _has_reminder_tableがTrueを返すようにモック
    with patch.object(migration, "_has_reminder_table", return_value=True):
        with patch("asyncpg.connect", return_value=mock_conn):
            result = await migration.check_and_migrate()
    
    assert result is False
    mock_conn.close.assert_called_once()


@pytest.mark.asyncio
async def test_check_and_migrate_reminder_table_not_exists():
    """リマインダーテーブルが存在しない場合はマイグレーションを実行"""
    migration = DatabaseMigration(
        db_host="localhost",
        db_port=5432,
        current_user_id="new_user_id",
    )
    
    # モックの接続を作成
    mock_conn = AsyncMock(spec=asyncpg.Connection)
    
    # _has_reminder_tableがFalseを返すようにモック
    with patch.object(migration, "_has_reminder_table", return_value=False):
        # _migrate_user_idsをモック
        with patch.object(migration, "_migrate_user_ids", return_value=None) as mock_migrate:
            with patch("asyncpg.connect", return_value=mock_conn):
                result = await migration.check_and_migrate()
    
    assert result is True
    mock_migrate.assert_called_once_with(mock_conn)
    mock_conn.close.assert_called_once()


@pytest.mark.asyncio
async def test_has_reminder_table():
    """リマインダーテーブル存在チェックのテスト"""
    migration = DatabaseMigration(
        db_host="localhost",
        db_port=5432,
        current_user_id="test_user",
    )
    
    # モックの接続を作成
    mock_conn = AsyncMock(spec=asyncpg.Connection)
    
    # テーブルが存在する場合
    mock_conn.fetchval.return_value = True
    result = await migration._has_reminder_table(mock_conn)
    assert result is True
    
    # テーブルが存在しない場合
    mock_conn.fetchval.return_value = False
    result = await migration._has_reminder_table(mock_conn)
    assert result is False


@pytest.mark.asyncio
async def test_migrate_user_ids():
    """user_idマイグレーションのテスト"""
    migration = DatabaseMigration(
        db_host="localhost",
        db_port=5432,
        current_user_id="new_user_id",
    )
    
    # モックの接続とトランザクションを作成
    mock_conn = AsyncMock(spec=asyncpg.Connection)
    mock_transaction = AsyncMock()
    mock_conn.transaction.return_value = mock_transaction
    
    # テーブルとカラムの存在確認のモック
    mock_conn.fetchval.side_effect = [
        True,   # conversation_historyテーブルが存在
        True,   # user_idカラムが存在
        100,    # 更新前の件数
        5,      # 更新前のユニークユーザー数
        100,    # 更新後の件数
        True,   # conversation_summariesテーブルが存在
        True,   # user_idカラムが存在
        50,     # 更新前の件数
        3,      # 更新前のユニークユーザー数
        50,     # 更新後の件数
        True,   # user_knowledgeテーブルが存在
        True,   # user_idカラムが存在
        25,     # 更新前の件数
        2,      # 更新前のユニークユーザー数
        25,     # 更新後の件数
    ]
    
    # executeの戻り値をモック（"UPDATE 100" 形式）
    mock_conn.execute.side_effect = ["UPDATE 100", "UPDATE 50", "UPDATE 25"]
    
    await migration._migrate_user_ids(mock_conn)
    
    # UPDATEクエリが実行されたことを確認
    assert mock_conn.execute.call_count == 3
    mock_conn.execute.assert_any_call(
        "UPDATE conversation_history SET user_id = $1;",
        "new_user_id",
    )
    mock_conn.execute.assert_any_call(
        "UPDATE conversation_summaries SET user_id = $1;",
        "new_user_id",
    )
    mock_conn.execute.assert_any_call(
        "UPDATE user_knowledge SET user_id = $1;",
        "new_user_id",
    )


@pytest.mark.asyncio
async def test_migrate_user_ids_table_not_exists():
    """存在しないテーブルはスキップされることのテスト"""
    migration = DatabaseMigration(
        db_host="localhost",
        db_port=5432,
        current_user_id="new_user_id",
    )
    
    # モックの接続とトランザクションを作成
    mock_conn = AsyncMock(spec=asyncpg.Connection)
    mock_transaction = AsyncMock()
    mock_conn.transaction.return_value = mock_transaction
    
    # テーブルが存在しない
    mock_conn.fetchval.side_effect = [
        False,  # conversation_historyテーブルが存在しない
        False,  # conversation_summariesテーブルが存在しない
        False,  # user_knowledgeテーブルが存在しない
    ]
    
    await migration._migrate_user_ids(mock_conn)
    
    # UPDATEクエリが実行されていないことを確認
    mock_conn.execute.assert_not_called()


@pytest.mark.asyncio
async def test_run_migration_helper():
    """run_migrationヘルパー関数のテスト"""
    with patch("db_migration.DatabaseMigration") as MockMigration:
        mock_instance = MockMigration.return_value
        mock_instance.check_and_migrate = AsyncMock(return_value=True)
        
        result = await run_migration(
            db_host="localhost",
            db_port=5432,
            current_user_id="test_user",
        )
        
        assert result is True
        MockMigration.assert_called_once_with(
            db_host="localhost",
            db_port=5432,
            db_name="postgres",
            db_user="postgres",
            db_password="postgres",
            current_user_id="test_user",
        )
        mock_instance.check_and_migrate.assert_called_once()