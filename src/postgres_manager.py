import os
import subprocess
import sys
import time


class Config:
    POSTGRES_PORT = "5433"  # デフォルト値、後で設定から更新される
    POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")


class PostgresInitializer:
    def __init__(self, base_dir, initdb_exe, data_dir, log_dir):
        self.base_dir = base_dir
        self.initdb_exe = initdb_exe
        self.data_dir = data_dir
        self.log_dir = log_dir

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
            subprocess.run(
                [
                    self.initdb_exe,
                    "-D",
                    self.data_dir,
                    "-U",
                    Config.POSTGRES_USER,
                    "--encoding=UTF8",
                    "--locale=C",
                ],
                check=True,
            )

            # パスワード設定用のSQLファイルを作成
            with open(os.path.join(self.base_dir, "set_password.sql"), "w") as f:
                f.write(
                    f"ALTER USER {Config.POSTGRES_USER} WITH PASSWORD '{Config.POSTGRES_PASSWORD}';"
                )

            # 軽量化設定を適用
            self._apply_lightweight_config()

            print("PostgreSQL データディレクトリが初期化されました")
        else:
            print("PostgreSQL データディレクトリは既に初期化されています")

    def _apply_lightweight_config(self):
        """軽量化設定をpostgresql.confに適用"""
        config_file = os.path.join(self.data_dir, "postgresql.conf")
        
        # 軽量化設定
        lightweight_settings = {
            # メモリ設定
            "shared_buffers": "32MB",
            "work_mem": "1MB",
            "maintenance_work_mem": "16MB",
            "wal_buffers": "1MB",
            "effective_cache_size": "256MB",
            # WAL設定
            "max_wal_size": "200MB",
            "min_wal_size": "50MB",
            "checkpoint_timeout": "15min",
            "checkpoint_completion_target": "0.5",
            # 接続設定
            "max_connections": "10",
            # ログ設定
            "logging_collector": "off",
            "log_min_messages": "error",
            "log_checkpoints": "off",
            # 自動バキューム設定
            "autovacuum_max_workers": "1",
            "autovacuum_naptime": "5min",
        }
        
        # 設定ファイルを読み込み
        with open(config_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        # 適用済みの設定を記録
        applied_settings = set()
        
        # 設定を更新
        for i, line in enumerate(lines):
            for key, value in lightweight_settings.items():
                # コメントアウトされた設定を探して上書き
                if line.strip().startswith(f"#{key}") or line.strip().startswith(f"{key}"):
                    lines[i] = f"{key} = {value}\n"
                    applied_settings.add(key)
                    break
        
        # まだ適用されていない設定を末尾に追加
        remaining_settings = {k: v for k, v in lightweight_settings.items() if k not in applied_settings}
        if remaining_settings:
            lines.append("\n# 軽量化設定\n")
            for key, value in remaining_settings.items():
                lines.append(f"{key} = {value}\n")
        
        # 設定ファイルを書き込み
        with open(config_file, "w", encoding="utf-8") as f:
            f.writelines(lines)
        
        print("軽量化設定を適用しました")


class PostgresServerManager:
    def __init__(self, pg_ctl_exe, psql_exe, data_dir, log_file, base_dir):
        self.pg_ctl_exe = pg_ctl_exe
        self.psql_exe = psql_exe
        self.data_dir = data_dir
        self.log_file = log_file
        self.base_dir = base_dir
        self.postgres_pid = None  # 起動したPostgreSQLのPIDを記録

    def start_server(self):
        """PostgreSQLサーバーを起動"""
        print("PostgreSQLサーバーを起動中...")
        try:
            subprocess.run(
                [
                    self.pg_ctl_exe,
                    "start",
                    "-D",
                    self.data_dir,
                    "-l",
                    self.log_file,
                    "-o",
                    f'"-p {Config.POSTGRES_PORT}"',
                    "-w",  # 起動完了まで待機
                ],
                check=True,
            )

            # 数秒待機してサーバーが起動するのを待つ
            time.sleep(3)
            
            # postmaster.pidファイルからPIDを取得
            try:
                pid_file = os.path.join(self.data_dir, "postmaster.pid")
                if os.path.exists(pid_file):
                    with open(pid_file, 'r') as f:
                        self.postgres_pid = int(f.readline().strip())
                        print(f"PostgreSQL プロセスID: {self.postgres_pid}")
            except Exception as e:
                print(f"PID取得エラー: {e}")

            # パスワードを設定
            if os.path.exists(os.path.join(self.base_dir, "set_password.sql")):
                subprocess.run(
                    [
                        self.psql_exe,
                        "-p",
                        Config.POSTGRES_PORT,
                        "-U",
                        Config.POSTGRES_USER,
                        "-f",
                        os.path.join(self.base_dir, "set_password.sql"),
                    ]
                )
                # SQLファイルを削除
                os.remove(os.path.join(self.base_dir, "set_password.sql"))

            print("PostgreSQLサーバーが起動しました")
            return True
        except Exception as e:
            print(f"サーバー起動中にエラーが発生しました: {e}")
            return False

    def stop_server(self):
        """PostgreSQLサーバーを停止"""
        try:
            status = subprocess.run(
                [self.pg_ctl_exe, "status", "-D", self.data_dir],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            if status.returncode != 0:
                print("PostgreSQLサーバーは既に停止しているか実行されていません")
                # 念のため残存プロセスをチェック
                self._kill_remaining_postgres_processes()
                return True

            # まず正常停止を試みる
            result = subprocess.run(
                [self.pg_ctl_exe, "stop", "-D", self.data_dir, "-m", "fast"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=10  # 10秒でタイムアウト
            )
            
            if result.returncode == 0:
                print("PostgreSQLサーバーを正常に停止しました")
            else:
                print("正常停止に失敗しました。強制停止を試みます...")
                subprocess.run(
                    [self.pg_ctl_exe, "stop", "-D", self.data_dir, "-m", "immediate"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=5
                )
                
            # 念のため残存プロセスをチェック
            self._kill_remaining_postgres_processes()
            return True

        except subprocess.TimeoutExpired:
            print("PostgreSQLサーバーの停止がタイムアウトしました。プロセスを強制終了します...")
            self._kill_remaining_postgres_processes()
            return True
        except Exception as e:
            print(f"サーバー停止中にエラーが発生しました: {e}")
            self._kill_remaining_postgres_processes()
            return True
    
    def _kill_remaining_postgres_processes(self):
        """残存するPostgreSQLプロセスを強制終了（自分が起動したもののみ）"""
        if sys.platform == "win32":
            try:
                # Windowsでpostgres.exeプロセスを検索して終了
                import psutil
                
                # 自分が起動したプロセスのPIDがある場合
                if self.postgres_pid:
                    try:
                        parent_proc = psutil.Process(self.postgres_pid)
                        # 親プロセスとその子プロセスを取得
                        children = parent_proc.children(recursive=True)
                        children.append(parent_proc)
                        
                        for proc in children:
                            if proc.is_running() and proc.name() == 'postgres.exe':
                                print(f"PostgreSQLプロセス (PID: {proc.pid}) を終了します")
                                proc.terminate()
                                proc.wait(timeout=5)
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                        pass
                else:
                    # PIDが不明な場合は、データディレクトリで判別
                    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                        try:
                            if proc.info['name'] == 'postgres.exe':
                                # コマンドラインにデータディレクトリが含まれているか確認
                                cmdline = ' '.join(proc.info.get('cmdline', []))
                                if self.data_dir in cmdline:
                                    print(f"残存PostgreSQLプロセス (PID: {proc.info['pid']}) を終了します")
                                    proc.terminate()
                                    proc.wait(timeout=5)
                        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                            continue
            except ImportError:
                # psutilがない場合は、pg_ctlコマンドのみに依存
                print("psutilが利用できないため、追加のプロセスクリーンアップは実行されません")


class PostgresManager:
    def __init__(self, base_dir=None, port=None):
        """PostgreSQLサーバーを管理するクラス
        
        Args:
            base_dir: ベースディレクトリ
            port: PostgreSQLのポート番号
        """
        if base_dir is None:
            # 実行ファイルのディレクトリを取得
            if getattr(sys, "frozen", False):
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
        
        # ポート設定の更新
        if port:
            Config.POSTGRES_PORT = str(port)

        self.initializer = PostgresInitializer(
            self.base_dir, self.initdb_exe, self.data_dir, self.log_dir
        )
        self.server_manager = PostgresServerManager(
            self.pg_ctl_exe, self.psql_exe, self.data_dir, self.log_file, self.base_dir
        )

    def initialize_db(self):
        """データベースを初期化"""
        self.initializer.initialize_db()

    def start_server(self):
        """PostgreSQLサーバーを起動"""
        if not self.initializer.is_initialized():
            self.initialize_db()
        return self.server_manager.start_server()

    def stop_server(self):
        """PostgreSQLサーバーを停止"""
        return self.server_manager.stop_server()
