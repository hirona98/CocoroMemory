"""postgres_manager.py のテスト"""

import os
import sys
import tempfile
from unittest.mock import Mock, patch

from postgres_manager import (
    Config,
    PostgresInitializer,
    PostgresManager,
    PostgresServerManager,
    get_short_path_name,
)


class TestGetShortPathName:
    """get_short_path_name 関数のテスト"""

    def test_get_short_path_name_non_windows(self):
        """Windows以外のプラットフォームでは元のパスが返されることをテスト"""
        with patch("sys.platform", "linux"):
            path = "/long/path/name"
            result = get_short_path_name(path)
            assert result == path

    @patch("sys.platform", "win32")
    def test_get_short_path_name_windows_success(self):
        """Windowsで短いパス名が正常に取得されることをテスト"""
        with patch("ctypes.windll.kernel32.GetShortPathNameW") as mock_func:
            mock_func.side_effect = [5, 5]  # 最初の呼び出しで長さを返し、次の呼び出しでも5を返す

            with patch("ctypes.create_unicode_buffer") as mock_buffer:
                mock_output = Mock()
                mock_output.value = "C:\\SHORT~1"
                mock_buffer.return_value = mock_output

                result = get_short_path_name("C:\\LongPathName")
                assert result == "C:\\SHORT~1"

    @patch("sys.platform", "win32")
    def test_get_short_path_name_windows_failure(self):
        """Windowsで短いパス名の取得に失敗した場合、元のパスが返されることをテスト"""
        with patch("ctypes.windll.kernel32.GetShortPathNameW") as mock_func:
            mock_func.side_effect = Exception("Error")

            path = "C:\\LongPathName"
            result = get_short_path_name(path)
            assert result == path


class TestConfig:
    """Config クラスのテスト"""

    def test_config_defaults(self):
        """デフォルト設定値をテスト"""
        assert Config.POSTGRES_PORT == "5432"
        assert Config.POSTGRES_USER == "postgres"
        assert Config.POSTGRES_PASSWORD == "postgres"

    def test_config_environment_variables(self):
        """環境変数からの設定値読み込みをテスト"""
        with patch.dict(os.environ, {"POSTGRES_USER": "testuser", "POSTGRES_PASSWORD": "testpass"}):
            # クラスを再インポートして環境変数を反映
            from importlib import reload

            import postgres_manager

            reload(postgres_manager)

            # 新しい設定値を確認
            assert postgres_manager.Config.POSTGRES_USER == "testuser"
            assert postgres_manager.Config.POSTGRES_PASSWORD == "testpass"


class TestPostgresInitializer:
    """PostgresInitializer クラスのテスト"""

    def setup_method(self):
        """各テストメソッドの前に実行されるセットアップ"""
        self.temp_dir = tempfile.mkdtemp()
        self.base_dir = self.temp_dir
        self.initdb_exe = "/path/to/initdb.exe"
        self.data_dir = os.path.join(self.temp_dir, "data")
        self.log_dir = os.path.join(self.temp_dir, "logs")

        self.initializer = PostgresInitializer(
            self.base_dir, self.initdb_exe, self.data_dir, self.log_dir
        )

    def test_is_initialized_false(self):
        """データディレクトリが初期化されていない場合のテスト"""
        assert not self.initializer.is_initialized()

    def test_is_initialized_true(self):
        """データディレクトリが初期化されている場合のテスト"""
        os.makedirs(self.data_dir, exist_ok=True)
        with open(os.path.join(self.data_dir, "PG_VERSION"), "w") as f:
            f.write("15")

        assert self.initializer.is_initialized()

    @patch("subprocess.run")
    @patch("postgres_manager.get_short_path_name")
    def test_initialize_db_success(self, mock_get_short_path, mock_subprocess):
        """データベース初期化が成功することをテスト"""
        mock_get_short_path.return_value = self.data_dir
        mock_subprocess.return_value = Mock()

        # postgresql.confファイルを事前に作成
        os.makedirs(self.data_dir, exist_ok=True)
        config_file = os.path.join(self.data_dir, "postgresql.conf")
        with open(config_file, "w", encoding="utf-8") as f:
            f.write("# PostgreSQL configuration\nmax_connections = 100\n")

        # _apply_lightweight_configをモックして実際の設定適用をスキップ
        with patch.object(self.initializer, "_apply_lightweight_config"):
            self.initializer.initialize_db()

        # ディレクトリが作成されることを確認
        assert os.path.exists(self.data_dir)
        assert os.path.exists(self.log_dir)

        # initdbコマンドが呼ばれることを確認
        mock_subprocess.assert_called()

    @patch("subprocess.run")
    def test_initialize_db_already_initialized(self, mock_subprocess):
        """既に初期化されている場合のテスト"""
        os.makedirs(self.data_dir, exist_ok=True)
        with open(os.path.join(self.data_dir, "PG_VERSION"), "w") as f:
            f.write("15")

        self.initializer.initialize_db()

        # initdbコマンドが呼ばれないことを確認
        mock_subprocess.assert_not_called()

    def test_apply_lightweight_config(self):
        """軽量化設定の適用をテスト"""
        # データディレクトリとpostgresql.confファイルを作成
        os.makedirs(self.data_dir, exist_ok=True)
        config_file = os.path.join(self.data_dir, "postgresql.conf")

        # 初期設定ファイルを作成
        initial_config = """# PostgreSQL configuration
#shared_buffers = 128MB
#work_mem = 4MB
max_connections = 100
"""
        with open(config_file, "w", encoding="utf-8") as f:
            f.write(initial_config)

        # 軽量化設定を適用
        self.initializer._apply_lightweight_config()

        # 設定ファイルが更新されたことを確認
        with open(config_file, "r", encoding="utf-8") as f:
            content = f.read()

        assert "shared_buffers = 32MB" in content
        assert "work_mem = 1MB" in content


class TestPostgresServerManager:
    """PostgresServerManager クラスのテスト"""

    def setup_method(self):
        """各テストメソッドの前に実行されるセットアップ"""
        self.temp_dir = tempfile.mkdtemp()
        self.pg_ctl_exe = "/path/to/pg_ctl.exe"
        self.psql_exe = "/path/to/psql.exe"
        self.data_dir = os.path.join(self.temp_dir, "data")
        self.log_file = os.path.join(self.temp_dir, "postgresql.log")
        self.base_dir = self.temp_dir

        self.server_manager = PostgresServerManager(
            self.pg_ctl_exe, self.psql_exe, self.data_dir, self.log_file, self.base_dir
        )

    @patch("subprocess.run")
    @patch("time.sleep")
    @patch("postgres_manager.get_short_path_name")
    def test_start_server_success(self, mock_get_short_path, mock_sleep, mock_subprocess):
        """サーバー起動が成功することをテスト"""
        mock_get_short_path.side_effect = lambda x: x
        mock_subprocess.return_value = Mock()

        # postmaster.pidファイルを作成
        os.makedirs(self.data_dir, exist_ok=True)
        with open(os.path.join(self.data_dir, "postmaster.pid"), "w") as f:
            f.write("12345\n")

        result = self.server_manager.start_server()

        assert result is True
        assert self.server_manager.postgres_pid == 12345
        mock_subprocess.assert_called()

    @patch("subprocess.run")
    def test_start_server_failure(self, mock_subprocess):
        """サーバー起動が失敗することをテスト"""
        mock_subprocess.side_effect = Exception("Start failed")

        result = self.server_manager.start_server()

        assert result is False

    @patch("subprocess.run")
    def test_stop_server_success(self, mock_subprocess):
        """サーバー停止が成功することをテスト"""
        # statusコマンドが0を返す（実行中）
        # stopコマンドが0を返す（成功）
        mock_subprocess.side_effect = [
            Mock(returncode=0),  # status
            Mock(returncode=0),  # stop
        ]

        result = self.server_manager.stop_server()

        assert result is True

    @patch("subprocess.run")
    def test_stop_server_not_running(self, mock_subprocess):
        """サーバーが実行されていない場合のテスト"""
        # statusコマンドが非0を返す（実行されていない）
        mock_subprocess.return_value = Mock(returncode=1)

        result = self.server_manager.stop_server()

        assert result is True

    @patch("subprocess.run")
    def test_stop_server_timeout(self, mock_subprocess):
        """サーバー停止がタイムアウトした場合のテスト"""
        from subprocess import TimeoutExpired

        mock_subprocess.side_effect = [
            Mock(returncode=0),  # status
            TimeoutExpired("cmd", 10),  # stop timeout
        ]

        result = self.server_manager.stop_server()

        assert result is True


class TestPostgresManager:
    """PostgresManager クラスのテスト"""

    def setup_method(self):
        """各テストメソッドの前に実行されるセットアップ"""
        self.temp_dir = tempfile.mkdtemp()

    def test_init_with_base_dir(self):
        """base_dirを指定してのインスタンス化をテスト"""
        manager = PostgresManager(base_dir=self.temp_dir)

        assert manager.base_dir == self.temp_dir
        assert manager.data_dir == os.path.join(self.temp_dir, "Data")
        assert manager.log_dir == os.path.join(self.temp_dir, "Logs")

    def test_init_with_port(self):
        """ポート番号を指定してのインスタンス化をテスト"""
        # テスト前にポートをリセット
        original_port = Config.POSTGRES_PORT
        try:
            PostgresManager(base_dir=self.temp_dir, port=5432)
            assert Config.POSTGRES_PORT == "5432"
        finally:
            # テスト後に元の値に戻す
            Config.POSTGRES_PORT = original_port

    @patch.object(sys, "frozen", True, create=True)
    @patch.object(sys, "executable", "/path/to/executable.exe")
    def test_init_frozen_executable(self):
        """PyInstallerで固められた実行ファイルでのインスタンス化をテスト"""
        manager = PostgresManager()

        assert manager.base_dir == "/path/to"

    def test_bin_dir_internal_priority(self):
        """_internal/pgsql/binが優先されることをテスト"""
        # _internal/pgsql/binディレクトリを作成
        internal_bin_dir = os.path.join(self.temp_dir, "_internal", "pgsql", "bin")
        os.makedirs(internal_bin_dir)

        # 通常のpgsql/binディレクトリも作成
        normal_bin_dir = os.path.join(self.temp_dir, "pgsql", "bin")
        os.makedirs(normal_bin_dir)

        manager = PostgresManager(base_dir=self.temp_dir)

        assert manager.bin_dir == internal_bin_dir

    def test_bin_dir_fallback(self):
        """_internal/pgsql/binがない場合のフォールバックをテスト"""
        # 通常のpgsql/binディレクトリのみ作成
        normal_bin_dir = os.path.join(self.temp_dir, "pgsql", "bin")
        os.makedirs(normal_bin_dir)

        manager = PostgresManager(base_dir=self.temp_dir)

        assert manager.bin_dir == normal_bin_dir

    @patch("postgres_manager.PostgresInitializer")
    @patch("postgres_manager.PostgresServerManager")
    def test_initialize_db(self, mock_server_manager, mock_initializer):
        """initialize_db メソッドのテスト"""
        mock_initializer_instance = Mock()
        mock_initializer.return_value = mock_initializer_instance

        manager = PostgresManager(base_dir=self.temp_dir)
        manager.initialize_db()

        mock_initializer_instance.initialize_db.assert_called_once()

    @patch("postgres_manager.PostgresInitializer")
    @patch("postgres_manager.PostgresServerManager")
    def test_start_server(self, mock_server_manager_class, mock_initializer_class):
        """start_server メソッドのテスト"""
        mock_initializer = Mock()
        mock_initializer.is_initialized.return_value = True
        mock_initializer_class.return_value = mock_initializer

        mock_server_manager = Mock()
        mock_server_manager.start_server.return_value = True
        mock_server_manager_class.return_value = mock_server_manager

        manager = PostgresManager(base_dir=self.temp_dir)
        result = manager.start_server()

        assert result is True
        mock_server_manager.start_server.assert_called_once()

    @patch("postgres_manager.PostgresInitializer")
    @patch("postgres_manager.PostgresServerManager")
    def test_start_server_with_initialization(
        self, mock_server_manager_class, mock_initializer_class
    ):
        """初期化が必要な場合のstart_serverメソッドのテスト"""
        mock_initializer = Mock()
        mock_initializer.is_initialized.return_value = False
        mock_initializer_class.return_value = mock_initializer

        mock_server_manager = Mock()
        mock_server_manager.start_server.return_value = True
        mock_server_manager_class.return_value = mock_server_manager

        manager = PostgresManager(base_dir=self.temp_dir)
        result = manager.start_server()

        assert result is True
        mock_initializer.initialize_db.assert_called_once()
        mock_server_manager.start_server.assert_called_once()

    @patch("postgres_manager.PostgresInitializer")
    @patch("postgres_manager.PostgresServerManager")
    def test_stop_server(self, mock_server_manager_class, mock_initializer_class):
        """stop_server メソッドのテスト"""
        mock_server_manager = Mock()
        mock_server_manager.stop_server.return_value = True
        mock_server_manager_class.return_value = mock_server_manager

        manager = PostgresManager(base_dir=self.temp_dir)
        result = manager.stop_server()

        assert result is True
        mock_server_manager.stop_server.assert_called_once()
