"""
データベースバージョン管理モジュール

アプリケーションの起動時にバージョン情報をデータベースに記録し、
バージョン履歴を管理する機能を提供します。
"""

import asyncio
import logging

import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)

# 現在のアプリケーションバージョン
CURRENT_VERSION = "3.0.1"


class VersionManager:
    """データベースバージョン管理クラス"""

    def __init__(self, db_host: str = "127.0.0.1", db_port: int = 5432):
        """
        バージョンマネージャーを初期化

        Args:
            db_host: データベースホスト
            db_port: データベースポート
        """
        self.db_host = db_host
        self.db_port = db_port
        self.db_name = "postgres"
        self.db_user = "postgres"
        self.db_password = "postgres"  # noqa: S105

    def _get_connection(self):
        """データベース接続を取得"""
        return psycopg2.connect(
            host=self.db_host,
            port=self.db_port,
            database=self.db_name,
            user=self.db_user,
            password=self.db_password,
        )

    def create_version_table(self):
        """バージョン管理テーブルを作成"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    # バージョン管理テーブルを作成
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS app_versions (
                            id SERIAL PRIMARY KEY,
                            version VARCHAR(50) NOT NULL,
                            applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                            description TEXT,
                            UNIQUE(version)
                        )
                    """)
                    
                    # インデックスを作成
                    cursor.execute("""
                        CREATE INDEX IF NOT EXISTS idx_app_versions_version 
                        ON app_versions(version)
                    """)
                    
                    cursor.execute("""
                        CREATE INDEX IF NOT EXISTS idx_app_versions_applied_at 
                        ON app_versions(applied_at)
                    """)
                    
                    conn.commit()
                    logger.info("バージョン管理テーブルが作成されました")

        except psycopg2.Error as e:
            logger.error(f"バージョン管理テーブルの作成に失敗しました: {e}")
            raise

    def get_current_db_version(self) -> str | None:
        """データベースに記録されている最新バージョンを取得"""
        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT version FROM app_versions 
                        ORDER BY applied_at DESC, id DESC 
                        LIMIT 1
                    """)
                    result = cursor.fetchone()
                    return result["version"] if result else None

        except psycopg2.Error as e:
            logger.error(f"現在のDBバージョン取得に失敗しました: {e}")
            return None

    def is_version_recorded(self, version: str) -> bool:
        """指定されたバージョンが既に記録されているかチェック"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "SELECT COUNT(*) FROM app_versions WHERE version = %s",
                        (version,)
                    )
                    count = cursor.fetchone()[0]
                    return count > 0

        except psycopg2.Error as e:
            logger.error(f"バージョン存在チェックに失敗しました: {e}")
            return False

    def record_version(self, version: str, description: str = None):
        """新しいバージョンをデータベースに記録"""
        try:
            # 既に記録されているかチェック
            if self.is_version_recorded(version):
                logger.info(f"バージョン {version} は既に記録されています")
                return False

            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO app_versions (version, description)
                        VALUES (%s, %s)
                    """, (version, description))
                    
                    conn.commit()
                    logger.info(f"バージョン {version} が記録されました")
                    return True

        except psycopg2.Error as e:
            logger.error(f"バージョン記録に失敗しました: {e}")
            raise

    def get_version_history(self, limit: int = 10) -> list[dict]:
        """バージョン履歴を取得"""
        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT version, applied_at, description
                        FROM app_versions 
                        ORDER BY applied_at DESC, id DESC
                        LIMIT %s
                    """, (limit,))
                    
                    return [dict(row) for row in cursor.fetchall()]

        except psycopg2.Error as e:
            logger.error(f"バージョン履歴取得に失敗しました: {e}")
            return []

    def initialize_version_management(self, version: str = None, description: str = None):
        """
        バージョン管理の初期化処理
        
        Args:
            version: 記録するバージョン（デフォルトはCURRENT_VERSION）
            description: バージョンの説明
        """
        if version is None:
            version = CURRENT_VERSION

        if description is None:
            description = f"CocoroMemory バージョン {version} の起動"

        try:
            # バージョン管理テーブルを作成
            self.create_version_table()
            
            # 現在のバージョンを記録
            self.record_version(version, description)
            
            # 現在のDBバージョンをログ出力
            current_db_version = self.get_current_db_version()
            logger.info(f"データベースの現在のバージョン: {current_db_version}")
            
            return True

        except Exception as e:
            logger.error(f"バージョン管理の初期化に失敗しました: {e}")
            return False


async def initialize_version_management_async(
    db_host: str = "127.0.0.1", 
    db_port: int = 5432,
    version: str = None,
    description: str = None
) -> bool:
    """
    非同期バージョン管理初期化処理
    
    Args:
        db_host: データベースホスト
        db_port: データベースポート
        version: 記録するバージョン
        description: バージョンの説明
        
    Returns:
        bool: 初期化成功フラグ
    """
    
    def sync_initialize():
        vm = VersionManager(db_host=db_host, db_port=db_port)
        return vm.initialize_version_management(version=version, description=description)
    
    # 別スレッドで同期処理を実行
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, sync_initialize)