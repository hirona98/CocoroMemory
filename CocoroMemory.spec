# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# プロジェクトのルートディレクトリ
root_dir = os.path.dirname(os.path.abspath(SPEC))

# 埋め込みPostgreSQLディレクトリ
pgsql_dir = os.path.join(root_dir, 'pgsql')
data_dir = os.path.join(root_dir, 'Data')
scripts_dir = os.path.join(root_dir, 'Scripts')
logs_dir = os.path.join(root_dir, 'Logs')

# PostgreSQLのバイナリとデータをデータファイルとして追加
pgsql_datas = []
for root, dirs, files in os.walk(pgsql_dir):
    for file in files:
        file_path = os.path.join(root, file)
        rel_path = os.path.relpath(file_path, root_dir)
        target_path = os.path.dirname(rel_path)
        pgsql_datas.append((file_path, target_path))

# データディレクトリの必要なファイルを追加（PG_VERSION などの初期化ファイル）
data_datas = []
for root, dirs, files in os.walk(data_dir):
    for file in files:
        if file in ['PG_VERSION', 'postgresql.conf', 'pg_hba.conf', 'pg_ident.conf']:
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, root_dir)
            target_path = os.path.dirname(rel_path)
            data_datas.append((file_path, target_path))

# スクリプトディレクトリのバッチファイルを追加
scripts_datas = []
for root, dirs, files in os.walk(scripts_dir):
    for file in files:
        if file.endswith('.bat'):
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, root_dir)
            target_path = os.path.dirname(rel_path)
            scripts_datas.append((file_path, target_path))

# tiktokenのデータファイルを収集
tiktoken_datas = []
try:
    tiktoken_datas = collect_data_files('tiktoken_ext')
except:
    pass

# litellmのデータファイルを収集
litellm_datas = []
try:
    litellm_datas = collect_data_files('litellm')
except:
    pass

# chatmemoryのデータファイルを収集
chatmemory_datas = []
try:
    chatmemory_datas = collect_data_files('chatmemory')
except:
    pass

# すべてのデータファイルを結合
all_datas = pgsql_datas + data_datas + scripts_datas + tiktoken_datas + litellm_datas + chatmemory_datas

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=all_datas,
    hiddenimports=['uvicorn.logging', 'uvicorn.loops', 'uvicorn.loops.auto', 'uvicorn.protocols', 'uvicorn.protocols.http', 'uvicorn.protocols.http.auto', 'uvicorn.protocols.websockets', 'uvicorn.protocols.websockets.auto', 'uvicorn.lifespan', 'uvicorn.lifespan.on', 'uvicorn.lifespan.off', 'tiktoken_ext.openai_public', 'tiktoken_ext'] + collect_submodules('tiktoken_ext'),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='CocoroMemory',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # アイコンファイルがあれば指定
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='CocoroMemory',
)
