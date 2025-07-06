"""データベースマイグレーション機能

初回バージョンアップ時にuser_idを統一するためのマイグレーション処理を提供
"""

import logging
import asyncpg
from typing import Optional

logger = logging.getLogger(__name__)


class DatabaseMigration:
    """データベースマイグレーションを管理するクラス"""

    def __init__(
        self,
        db_host: str,
        db_port: int,
        db_name: str = "postgres",
        db_user: str = "postgres",
        db_password: str = "postgres",
        current_user_id: Optional[str] = None,
    ):
        """初期化

        Args:
            db_host: データベースホスト
            db_port: データベースポート
            db_name: データベース名
            db_user: データベースユーザー
            db_password: データベースパスワード
            current_user_id: 現在選択中のキャラクターのuserId
        """
        self.db_host = db_host
        self.db_port = db_port
        self.db_name = db_name
        self.db_user = db_user
        self.db_password = db_password
        self.current_user_id = current_user_id

    async def check_and_migrate(self) -> bool:
        """リマインダーテーブルの存在確認とマイグレーション実行

        Returns:
            bool: マイグレーションを実行した場合はTrue、スキップした場合はFalse
        """
        if not self.current_user_id:
            logger.warning(
                "current_user_idが設定されていません。マイグレーションをスキップします。"
            )
            return False

        conn = None
        try:
            # データベースに接続
            conn = await asyncpg.connect(
                host=self.db_host,
                port=self.db_port,
                database=self.db_name,
                user=self.db_user,
                password=self.db_password,
            )

            # リマインダーテーブルの存在確認
            has_reminder_table = await self._has_reminder_table(conn)

            if not has_reminder_table:
                logger.info(
                    "リマインダーテーブルが存在しません。user_idマイグレーションを実行します。"
                )
                await self._migrate_user_ids(conn)
                return True
            else:
                logger.info(
                    "リマインダーテーブルが既に存在します。マイグレーションをスキップします。"
                )
                return False

        except Exception as e:
            logger.error(f"マイグレーション処理中にエラーが発生しました: {e}")
            raise
        finally:
            if conn:
                await conn.close()

    async def _has_reminder_table(self, conn: asyncpg.Connection) -> bool:
        """リマインダーテーブルが存在するかチェック

        Args:
            conn: データベース接続

        Returns:
            bool: テーブルが存在する場合はTrue
        """
        query = """
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name = 'reminders'
        );
        """
        result = await conn.fetchval(query)
        return bool(result)

    async def _migrate_user_ids(self, conn: asyncpg.Connection) -> None:
        """全テーブルのuser_idを更新

        Args:
            conn: データベース接続
        """
        # トランザクション開始
        async with conn.transaction():
            # ChatMemoryが使用するテーブルのリスト
            tables_to_update = [
                "conversation_history",
                "conversation_summaries",
                "user_knowledge",
                # 他にuser_idカラムを持つテーブルがあれば追加
            ]

            for table_name in tables_to_update:
                try:
                    # テーブル名の安全性チェック（想定されるテーブル名のみ許可）
                    allowed_tables = [
                        "conversation_history",
                        "conversation_summaries",
                        "user_knowledge",
                    ]
                    if table_name not in allowed_tables:
                        logger.warning(f"予期しないテーブル名: {table_name}。スキップします。")
                        continue

                    # テーブルが存在するか確認
                    table_exists = await conn.fetchval(
                        """
                        SELECT EXISTS (
                            SELECT 1
                            FROM information_schema.tables
                            WHERE table_schema = 'public'
                            AND table_name = $1
                        );
                        """,
                        table_name,
                    )

                    if not table_exists:
                        logger.info(f"テーブル {table_name} が存在しません。スキップします。")
                        continue

                    # user_idカラムが存在するか確認
                    column_exists = await conn.fetchval(
                        """
                        SELECT EXISTS (
                            SELECT 1
                            FROM information_schema.columns
                            WHERE table_schema = 'public'
                            AND table_name = $1
                            AND column_name = 'user_id'
                        );
                        """,
                        table_name,
                    )

                    if not column_exists:
                        logger.info(
                            f"テーブル {table_name} にuser_idカラムがありません。スキップします。"
                        )
                        continue

                    # 更新前の件数を取得（NULLも含む）
                    count_before = await conn.fetchval("SELECT COUNT(*) FROM " + table_name + ";")

                    # 更新前のユニークなuser_id数を取得（NULLは除く）
                    unique_users_before = await conn.fetchval(
                        "SELECT COUNT(DISTINCT user_id) FROM "
                        + table_name
                        + " WHERE user_id IS NOT NULL;"
                    )

                    # NULLも含めてuser_idを更新
                    rows_updated = await conn.execute(
                        "UPDATE " + table_name + " SET user_id = $1;",
                        self.current_user_id,
                    )

                    # 更新後の確認
                    count_after = await conn.fetchval(
                        "SELECT COUNT(*) FROM " + table_name + " WHERE user_id = $1;",
                        self.current_user_id,
                    )

                    # UPDATEの結果から更新行数を取得
                    updated_count = int(rows_updated.split()[-1]) if rows_updated else 0

                    logger.info(
                        f"テーブル {table_name} のuser_idを更新しました: "
                        f"総レコード数={count_before}, "
                        f"更新前ユニークユーザー数={unique_users_before}, "
                        f"更新行数={updated_count}, "
                        f"更新後レコード数={count_after}"
                    )

                except Exception as e:
                    logger.error(f"テーブル {table_name} の更新中にエラーが発生しました: {e}")
                    # 個別テーブルのエラーは続行する

            logger.info(f"すべてのuser_idを {self.current_user_id} に統一しました。")


async def run_migration(
    db_host: str,
    db_port: int,
    current_user_id: Optional[str],
    db_name: str = "postgres",
    db_user: str = "postgres",
    db_password: str = "postgres",
) -> bool:
    """マイグレーションを実行するヘルパー関数

    Args:
        db_host: データベースホスト
        db_port: データベースポート
        current_user_id: 現在選択中のキャラクターのuserId
        db_name: データベース名
        db_user: データベースユーザー
        db_password: データベースパスワード

    Returns:
        bool: マイグレーションを実行した場合はTrue
    """
    migration = DatabaseMigration(
        db_host=db_host,
        db_port=db_port,
        db_name=db_name,
        db_user=db_user,
        db_password=db_password,
        current_user_id=current_user_id,
    )
    return await migration.check_and_migrate()
