import atexit
import os
import subprocess
import sys
import time


class PostgresManager:
    def __init__(self, base_dir=None):
        """PostgreSQLサーバーを管理するクラス"""
        if base_dir is None:
            # 実行ファイルのディレクトリを取得
            if getattr(sys, 'frozen', False):
                # PyInstallerでパッケージングされている場合
                self.base_dir = os.path.dirname(sys.executable)
            else:
                # 通常の実行の場合
                self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        else:
            self.base_dir = base_dir
            
        # PostgreSQLの各種ディレクトリとコマンドのパスを設定
        self.pgsql_dir = os.path.join(self.base_dir, "pgsql")
        self.data_dir = os.path.join(self.base_dir, "Data")
        self.log_dir = os.path.join(self.base_dir, "Logs")
        
        # bin_dir の探索: _internal/pgsql/bin 優先
        bin_dir_candidate = os.path.join(self.base_dir, "_internal", "pgsql", "bin")
        if os.path.exists(bin_dir_candidate):
            self.bin_dir = bin_dir_candidate
        else:
            self.bin_dir = os.path.join(self.pgsql_dir, "bin")
        
        # 各種コマンドへのパス
        self.postgres_exe = os.path.join(self.bin_dir, "postgres.exe")
        self.pg_ctl_exe = os.path.join(self.bin_dir, "pg_ctl.exe")
        self.initdb_exe = os.path.join(self.bin_dir, "initdb.exe")
        self.createdb_exe = os.path.join(self.bin_dir, "createdb.exe")
        self.psql_exe = os.path.join(self.bin_dir, "psql.exe")
        
        # ログファイルのパス
        self.log_file = os.path.join(self.log_dir, "postgresql.log")
        
        self.process = None
        
    def is_initialized(self):
        """PostgreSQLデータディレクトリが初期化されているかチェック"""
        return os.path.exists(os.path.join(self.data_dir, "PG_VERSION"))
        
    def initialize_db(self):
        """データベースを初期化"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
            
        if not self.is_initialized():
            print("PostgreSQLデータディレクトリを初期化しています...")
            subprocess.run([
                self.initdb_exe, 
                "-D", self.data_dir,
                "-U", "postgres",
                "--encoding=UTF8",
                "--locale=C"
            ], check=True)
            
            # パスワード設定用のSQLファイルを作成
            with open(os.path.join(self.base_dir, "set_password.sql"), "w") as f:
                f.write("ALTER USER postgres WITH PASSWORD 'postgres';")
                
            print("PostgreSQL データディレクトリが初期化されました")
        else:
            print("PostgreSQL データディレクトリは既に初期化されています")
            
    def start_server(self):
        """PostgreSQLサーバーを起動"""
        if not self.is_initialized():
            self.initialize_db()
            
        # サーバーが既に起動しているか確認
        try:
            status = subprocess.run(
                [self.pg_ctl_exe, "status", "-D", self.data_dir],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            if status.returncode == 0:
                print("PostgreSQLサーバーは既に起動しています")
                return True
        except Exception as e:
            print(f"ステータス確認中にエラーが発生しました: {e}")
            
        print("PostgreSQLサーバーを起動中...")
        try:
            subprocess.run([
                self.pg_ctl_exe,
                "start",
                "-D", self.data_dir,
                "-l", self.log_file,
                "-o", f'"-p 5433"',
                "-w"  # 起動完了まで待機
            ], check=True)
            
            # 数秒待機してサーバーが起動するのを待つ
            time.sleep(3)
            
            # パスワードを設定
            if os.path.exists(os.path.join(self.base_dir, "set_password.sql")):
                subprocess.run([
                    self.psql_exe,
                    "-p", "5433",
                    "-U", "postgres",
                    "-f", os.path.join(self.base_dir, "set_password.sql")
                ])
                # SQLファイルを削除
                os.remove(os.path.join(self.base_dir, "set_password.sql"))
                
            print("PostgreSQLサーバーが起動しました")
            return True
        except Exception as e:
            print(f"サーバー起動中にエラーが発生しました: {e}")
            return False
            
    def stop_server(self):
        """PostgreSQLサーバーを停止"""
        # 先にサーバーが実行中かどうかを確認
        try:
            status = subprocess.run(
                [self.pg_ctl_exe, "status", "-D", self.data_dir],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            # 戻り値が0以外の場合、サーバーは実行されていない
            if status.returncode != 0:
                print("PostgreSQLサーバーは既に停止しているか実行されていません")
                return True
                
            # サーバーが動作している場合は停止を試みる
            subprocess.run([
                self.pg_ctl_exe,
                "stop",
                "-D", self.data_dir,
                "-m", "fast"
            ], check=True)
            print("PostgreSQLサーバーを停止しました")
            return True
        
        except Exception as e:
            # PIDファイルがない場合も含めてエラーメッセージを出力
            print(f"サーバー停止中にエラーが発生しました: {e}")
            # エラーが発生しても、サーバーは実行されていないとみなす
            return True
