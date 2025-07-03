"""
PyInstaller用の隠れたインポート

このファイルはPyInstallerがパッケージ化時に必要なモジュールを
適切に検出するためのものです。
通常の実行時には使用されませんが、PyInstallerの依存関係解析で
必要となるインポートを明示的に記述しています。

lintツールはこれらのインポートを「未使用」として警告しますが、
PyInstallerには必要なため削除しないでください。
"""

# ruff: noqa: F401
# pylint: disable=unused-import

try:
    # PostgreSQL関連の動的インポート
    import psycopg2
    import psycopg2.extensions
    import psycopg2.extras
    import psycopg2._psycopg
    import asyncpg  # マイグレーション用
except ImportError:
    pass

try:
    # Windows特有のモジュール（条件付きインポート対策）
    import ctypes.wintypes
    import psutil._pswindows
except ImportError:
    pass

try:
    # HTTP/非同期関連
    import httpx._client
    import httpx._config
    import httpx._exceptions
    import asyncio.selector_events
except ImportError:
    pass

try:
    # LiteLLM関連（動的インポートが多い）
    import litellm.llms
    import litellm.llms.openai
    import litellm.utils
    import litellm.exceptions
except ImportError:
    pass

try:
    # tiktoken関連
    import tiktoken_ext
    import tiktoken_ext.openai_public
except ImportError:
    pass

try:
    # ChatMemory関連
    import chatmemory.llms
    import chatmemory.memory
    import chatmemory.embeddings
except ImportError:
    pass

try:
    # FastAPI/Pydantic関連
    import pydantic.main
    import pydantic.fields
    import pydantic.validators
    import fastapi.routing
    import fastapi.applications
except ImportError:
    pass

try:
    # uvicorn関連（詳細なサブモジュール）
    import uvicorn.protocols.http.h11_impl
    import uvicorn.protocols.websockets.wsproto_impl
    import uvicorn.loops.uvloop
    import uvicorn.loops.asyncio
except ImportError:
    pass

try:
    # dotenv関連
    import dotenv.main
    import dotenv.parser
except ImportError:
    pass

try:
    # ログ関連
    import logging.handlers
    import logging.config
except ImportError:
    pass
