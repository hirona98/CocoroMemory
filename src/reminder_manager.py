"""
リマインダー管理機能

このモジュールはCocoroMemoryシステムにリマインダー機能を提供します。
データベースの管理、API エンドポイント、スケジューラー機能を含みます。
"""

import asyncio
import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import httpx
import psycopg2
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

# ログ設定
logger = logging.getLogger(__name__)


class ReminderCreate(BaseModel):
    """リマインダー作成用データモデル"""

    user_id: str = Field(..., description="ユーザーID")
    trigger_time: datetime = Field(..., description="トリガー時刻")
    message: str = Field(..., description="リマインダーメッセージ")
    reminder_type: str = Field(
        "absolute", description="リマインダータイプ（absolute/relative/recurring）"
    )
    preparation_minutes: int = Field(0, description="事前準備時間（分）")


class ReminderUpdate(BaseModel):
    """リマインダー更新用データモデル"""

    trigger_time: Optional[datetime] = Field(None, description="トリガー時刻")
    message: Optional[str] = Field(None, description="リマインダーメッセージ")
    status: Optional[str] = Field(None, description="ステータス（pending/completed/cancelled）")
    preparation_minutes: Optional[int] = Field(None, description="事前準備時間（分）")


class ReminderResponse(BaseModel):
    """リマインダーレスポンス用データモデル"""

    id: int
    user_id: str
    trigger_time: datetime
    message: str
    status: str
    reminder_type: str
    preparation_minutes: int
    created_at: datetime
    notified_at: Optional[datetime]


class ReminderManager:
    """リマインダー管理クラス"""

    def __init__(
        self,
        db_host: str = "127.0.0.1",
        db_port: int = 5433,
        db_name: str = "postgres",
        db_user: str = "postgres",
        db_password: str = "postgres",
        notification_port: int = 55604,
    ):
        """
        リマインダーマネージャーを初期化

        Args:
            db_host: データベースホスト
            db_port: データベースポート
            db_name: データベース名
            db_user: データベースユーザー
            db_password: データベースパスワード
            notification_port: 通知APIのポート番号
        """
        self.db_config = {
            "host": db_host,
            "port": db_port,
            "database": db_name,
            "user": db_user,
            "password": db_password,
        }
        self.notification_port = notification_port
        self.scheduler_running = False
        self.scheduler_thread = None
        self.shutdown_event = threading.Event()

        # データベーステーブルを初期化
        self._initialize_database()

    def _initialize_database(self):
        """データベーステーブルを初期化"""
        try:
            with psycopg2.connect(**self.db_config) as conn:
                with conn.cursor() as cursor:
                    # リマインダーテーブルを作成
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS reminders (
                            id SERIAL PRIMARY KEY,
                            user_id TEXT NOT NULL,
                            trigger_time TIMESTAMP NOT NULL,
                            message TEXT NOT NULL,
                            status TEXT DEFAULT 'pending',
                            reminder_type TEXT NOT NULL,
                            preparation_minutes INTEGER DEFAULT 0,
                            created_at TIMESTAMP DEFAULT NOW(),
                            notified_at TIMESTAMP NULL
                        );
                    """)

                    # インデックスを作成（検索性能向上のため）
                    cursor.execute("""
                        CREATE INDEX IF NOT EXISTS idx_reminders_user_status 
                        ON reminders(user_id, status);
                    """)
                    cursor.execute("""
                        CREATE INDEX IF NOT EXISTS idx_reminders_trigger_time 
                        ON reminders(trigger_time) WHERE status = 'pending';
                    """)

                    conn.commit()
                    logger.info("リマインダーテーブルを初期化しました")
        except Exception as e:
            logger.error(f"データベース初期化エラー: {e}")
            raise

    def get_connection(self):
        """データベース接続を取得"""
        return psycopg2.connect(**self.db_config)

    async def create_reminder(self, reminder: ReminderCreate) -> ReminderResponse:
        """新しいリマインダーを作成"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO reminders (user_id, trigger_time, message, reminder_type, preparation_minutes)
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING id, created_at;
                    """,
                        (
                            reminder.user_id,
                            reminder.trigger_time,
                            reminder.message,
                            reminder.reminder_type,
                            reminder.preparation_minutes,
                        ),
                    )

                    result = cursor.fetchone()
                    reminder_id, created_at = result
                    conn.commit()

                    logger.info(
                        f"リマインダーを作成しました: ID={reminder_id}, ユーザー={reminder.user_id}"
                    )

                    return ReminderResponse(
                        id=reminder_id,
                        user_id=reminder.user_id,
                        trigger_time=reminder.trigger_time,
                        message=reminder.message,
                        status="pending",
                        reminder_type=reminder.reminder_type,
                        preparation_minutes=reminder.preparation_minutes,
                        created_at=created_at,
                        notified_at=None,
                    )
        except Exception as e:
            logger.error(f"リマインダー作成エラー: {e}")
            raise HTTPException(status_code=500, detail=f"リマインダー作成に失敗しました: {str(e)}")

    async def get_reminders(
        self, user_id: Optional[str] = None, status: Optional[str] = None
    ) -> List[ReminderResponse]:
        """リマインダーを取得"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    query = "SELECT id, user_id, trigger_time, message, status, reminder_type, preparation_minutes, created_at, notified_at FROM reminders"
                    params = []
                    conditions = []

                    if user_id:
                        conditions.append("user_id = %s")
                        params.append(user_id)

                    if status:
                        conditions.append("status = %s")
                        params.append(status)

                    if conditions:
                        query += " WHERE " + " AND ".join(conditions)

                    query += " ORDER BY trigger_time ASC"

                    cursor.execute(query, params)
                    results = cursor.fetchall()

                    reminders = []
                    for row in results:
                        reminders.append(
                            ReminderResponse(
                                id=row[0],
                                user_id=row[1],
                                trigger_time=row[2],
                                message=row[3],
                                status=row[4],
                                reminder_type=row[5],
                                preparation_minutes=row[6],
                                created_at=row[7],
                                notified_at=row[8],
                            )
                        )

                    return reminders
        except Exception as e:
            logger.error(f"リマインダー取得エラー: {e}")
            raise HTTPException(status_code=500, detail=f"リマインダー取得に失敗しました: {str(e)}")

    async def update_reminder(
        self, reminder_id: int, update_data: ReminderUpdate
    ) -> ReminderResponse:
        """リマインダーを更新"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # 更新対象のフィールドを構築
                    update_fields = []
                    params = []

                    if update_data.trigger_time is not None:
                        update_fields.append("trigger_time = %s")
                        params.append(update_data.trigger_time)

                    if update_data.message is not None:
                        update_fields.append("message = %s")
                        params.append(update_data.message)

                    if update_data.status is not None:
                        update_fields.append("status = %s")
                        params.append(update_data.status)

                    if update_data.preparation_minutes is not None:
                        update_fields.append("preparation_minutes = %s")
                        params.append(update_data.preparation_minutes)

                    if not update_fields:
                        raise HTTPException(
                            status_code=400, detail="更新するフィールドが指定されていません"
                        )

                    params.append(reminder_id)

                    cursor.execute(
                        f"""
                        UPDATE reminders 
                        SET {", ".join(update_fields)}
                        WHERE id = %s
                        RETURNING id, user_id, trigger_time, message, status, reminder_type, preparation_minutes, created_at, notified_at;
                    """,
                        params,
                    )

                    result = cursor.fetchone()
                    if not result:
                        raise HTTPException(status_code=404, detail="リマインダーが見つかりません")

                    conn.commit()

                    logger.info(f"リマインダーを更新しました: ID={reminder_id}")

                    return ReminderResponse(
                        id=result[0],
                        user_id=result[1],
                        trigger_time=result[2],
                        message=result[3],
                        status=result[4],
                        reminder_type=result[5],
                        preparation_minutes=result[6],
                        created_at=result[7],
                        notified_at=result[8],
                    )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"リマインダー更新エラー: {e}")
            raise HTTPException(status_code=500, detail=f"リマインダー更新に失敗しました: {str(e)}")

    async def delete_reminder(self, reminder_id: int) -> dict:
        """リマインダーを削除"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "DELETE FROM reminders WHERE id = %s RETURNING id;", (reminder_id,)
                    )
                    result = cursor.fetchone()

                    if not result:
                        raise HTTPException(status_code=404, detail="リマインダーが見つかりません")

                    conn.commit()

                    logger.info(f"リマインダーを削除しました: ID={reminder_id}")

                    return {
                        "status": "success",
                        "message": f"リマインダー {reminder_id} を削除しました",
                    }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"リマインダー削除エラー: {e}")
            raise HTTPException(status_code=500, detail=f"リマインダー削除に失敗しました: {str(e)}")

    async def send_notification(self, message: str, notification_type: str = "reminder"):
        """通知APIを使用して通知を送信"""
        try:
            notification_data = {
                "type": notification_type,
                "title": "リマインダー",
                "message": message,
                "timestamp": datetime.now().isoformat(),
                "source": "CocoroMemory",
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"http://127.0.0.1:{self.notification_port}/api/v1/notification",
                    json=notification_data,
                    timeout=10.0,
                )

                if response.status_code == 200:
                    logger.info(f"通知を送信しました: {message}")
                else:
                    logger.warning(f"通知送信に失敗しました: HTTP {response.status_code}")

        except Exception as e:
            logger.error(f"通知送信エラー: {e}")

    def _check_pending_reminders(self):
        """期限が来たリマインダーをチェックして通知"""
        try:
            current_time = datetime.now()

            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # 期限が来たリマインダーを取得
                    cursor.execute(
                        """
                        SELECT id, user_id, trigger_time, message, preparation_minutes
                        FROM reminders 
                        WHERE status = 'pending' AND trigger_time <= %s
                        ORDER BY trigger_time ASC;
                    """,
                        (current_time,),
                    )

                    due_reminders = cursor.fetchall()

                    # 事前通知が必要なリマインダーを取得
                    preparation_time = current_time + timedelta(
                        minutes=5
                    )  # 5分後までの事前通知をチェック
                    cursor.execute(
                        """
                        SELECT id, user_id, trigger_time, message, preparation_minutes
                        FROM reminders 
                        WHERE status = 'pending' 
                        AND preparation_minutes > 0 
                        AND trigger_time <= %s 
                        AND trigger_time > %s
                        AND notified_at IS NULL
                        ORDER BY trigger_time ASC;
                    """,
                        (preparation_time, current_time),
                    )

                    preparation_reminders = cursor.fetchall()

                    # 期限が来たリマインダーを処理
                    for reminder in due_reminders:
                        reminder_id, user_id, trigger_time, message, prep_minutes = reminder

                        # 通知を送信
                        asyncio.create_task(
                            self.send_notification(f"【リマインダー】{message}", "reminder")
                        )

                        # ステータスを完了に更新
                        cursor.execute(
                            """
                            UPDATE reminders 
                            SET status = 'completed', notified_at = %s 
                            WHERE id = %s;
                        """,
                            (current_time, reminder_id),
                        )

                        logger.info(
                            f"リマインダーを通知しました: ID={reminder_id}, メッセージ='{message}'"
                        )

                    # 事前通知を処理
                    for reminder in preparation_reminders:
                        reminder_id, user_id, trigger_time, message, prep_minutes = reminder

                        # 事前通知時間を計算
                        prep_time = trigger_time - timedelta(minutes=prep_minutes)

                        if current_time >= prep_time:
                            # 事前通知を送信
                            prep_message = (
                                f"【事前通知】{prep_minutes}分後に「{message}」の予定があります"
                            )
                            asyncio.create_task(self.send_notification(prep_message, "preparation"))

                            # 事前通知済みとしてマーク
                            cursor.execute(
                                """
                                UPDATE reminders 
                                SET notified_at = %s 
                                WHERE id = %s;
                            """,
                                (current_time, reminder_id),
                            )

                            logger.info(
                                f"事前通知を送信しました: ID={reminder_id}, メッセージ='{prep_message}'"
                            )

                    conn.commit()

        except Exception as e:
            logger.error(f"リマインダーチェックエラー: {e}")

    def start_scheduler(self):
        """スケジューラーを開始"""
        if self.scheduler_running:
            logger.warning("スケジューラーは既に実行中です")
            return

        self.scheduler_running = True
        self.shutdown_event.clear()

        def scheduler_loop():
            """スケジューラーのメインループ"""
            logger.info("リマインダースケジューラーを開始しました")

            while self.scheduler_running and not self.shutdown_event.is_set():
                try:
                    self._check_pending_reminders()
                except Exception as e:
                    logger.error(f"スケジューラーエラー: {e}")

                # 1分間隔でチェック（shutdown_eventを考慮した待機）
                for _ in range(60):  # 60秒を1秒ずつ分割して待機
                    if self.shutdown_event.is_set():
                        break
                    time.sleep(1)

            logger.info("リマインダースケジューラーを停止しました")

        self.scheduler_thread = threading.Thread(target=scheduler_loop, daemon=True)
        self.scheduler_thread.start()

        logger.info("スケジューラースレッドを開始しました")

    def stop_scheduler(self):
        """スケジューラーを停止"""
        if not self.scheduler_running:
            return

        logger.info("スケジューラーの停止を開始しています...")
        self.scheduler_running = False
        self.shutdown_event.set()

        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=5.0)
            if self.scheduler_thread.is_alive():
                logger.warning("スケジューラースレッドの停止がタイムアウトしました")
            else:
                logger.info("スケジューラースレッドを正常に停止しました")

    def get_router(self) -> APIRouter:
        """FastAPI ルーターを取得"""
        router = APIRouter(prefix="/reminders", tags=["reminders"])

        @router.post("/", response_model=ReminderResponse)
        async def create_reminder_endpoint(reminder: ReminderCreate):
            """リマインダーを作成"""
            return await self.create_reminder(reminder)

        @router.get("/", response_model=List[ReminderResponse])
        async def get_reminders_endpoint(
            user_id: Optional[str] = None, status: Optional[str] = None
        ):
            """リマインダー一覧を取得"""
            return await self.get_reminders(user_id=user_id, status=status)

        @router.put("/{reminder_id}", response_model=ReminderResponse)
        async def update_reminder_endpoint(reminder_id: int, update_data: ReminderUpdate):
            """リマインダーを更新"""
            return await self.update_reminder(reminder_id, update_data)

        @router.delete("/{reminder_id}")
        async def delete_reminder_endpoint(reminder_id: int):
            """リマインダーを削除"""
            return await self.delete_reminder(reminder_id)

        return router
