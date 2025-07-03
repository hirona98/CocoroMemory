#!/usr/bin/env python3
"""データベーステーブル確認スクリプト"""

import subprocess
import os
import time
import sys

def main():
    # PostgreSQLを起動
    print("PostgreSQLを起動しています...")
    subprocess.run(['Scripts/start_postgres.bat'], shell=True, check=False)
    time.sleep(5)

    try:
        # 環境変数でパスワードを設定
        env = os.environ.copy()
        env['PGPASSWORD'] = 'postgres'

        # テーブル一覧を取得
        print("テーブル一覧を取得しています...")
        result = subprocess.run([
            'pgsql/bin/psql.exe',
            '-h', '127.0.0.1',
            '-p', '5433',
            '-U', 'postgres',
            '-d', 'postgres',
            '-c', r'\dt'
        ], capture_output=True, text=True, env=env)

        print('=== テーブル一覧 ===')
        print(result.stdout)
        if result.stderr:
            print('=== エラー出力 ===')
            print(result.stderr)

        # chatmemoryが使用するテーブルが存在するかチェック
        expected_tables = ['conversation_history', 'conversation_summaries', 'user_knowledge']
        for table in expected_tables:
            result = subprocess.run([
                'pgsql/bin/psql.exe',
                '-h', '127.0.0.1',
                '-p', '5433',
                '-U', 'postgres',
                '-d', 'postgres',
                '-c', f"SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = '{table}');"
            ], capture_output=True, text=True, env=env)
            
            exists = 't' in result.stdout
            print(f"テーブル {table}: {'存在' if exists else '存在しない'}")

    finally:
        # PostgreSQLを停止
        print("PostgreSQLを停止しています...")
        subprocess.run(['Scripts/stop_postgres.bat'], shell=True, check=False)

if __name__ == "__main__":
    main()