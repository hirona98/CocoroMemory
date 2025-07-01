"""config_loader.py のテスト"""

import json
import os
import sys
import tempfile
from unittest.mock import patch

from config_loader import load_config, parse_args


class TestParseArgs:
    """parse_args 関数のテスト"""

    def test_parse_args_default(self):
        """引数なしでのデフォルト動作をテスト"""
        with patch("sys.argv", ["test"]):
            args = parse_args()
            assert args.config_dir is None

    def test_parse_args_with_config_dir(self):
        """--config-dir引数が正しく解析されることをテスト"""
        with patch("sys.argv", ["test", "--config-dir", "/test/path"]):
            args = parse_args()
            assert args.config_dir == "/test/path"

    def test_parse_args_short_option(self):
        """-c短縮オプションが正しく解析されることをテスト"""
        with patch("sys.argv", ["test", "-c", "/test/path"]):
            args = parse_args()
            assert args.config_dir == "/test/path"


class TestLoadConfig:
    """load_config 関数のテスト"""

    def test_load_config_with_valid_file(self):
        """有効な設定ファイルが正しく読み込まれることをテスト"""
        test_config = {
            "characterList": ["test_character"],
            "currentCharacterIndex": 0,
            "cocoroMemoryPort": 55602,
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = os.path.join(temp_dir, "setting.json")
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(test_config, f, ensure_ascii=False)

            result = load_config(temp_dir)
            assert result == test_config

    def test_load_config_with_nonexistent_file(self):
        """存在しない設定ファイルの場合、空の辞書が返されることをテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = load_config(temp_dir)
            assert result == {}

    def test_load_config_with_invalid_json(self):
        """不正なJSONファイルの場合、空の辞書が返されることをテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = os.path.join(temp_dir, "setting.json")
            with open(config_file, "w", encoding="utf-8") as f:
                f.write("{ invalid json }")

            result = load_config(temp_dir)
            assert result == {}

    def test_load_config_with_empty_file(self):
        """空の設定ファイルの場合、空の辞書が返されることをテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = os.path.join(temp_dir, "setting.json")
            with open(config_file, "w", encoding="utf-8") as f:
                f.write("")

            result = load_config(temp_dir)
            assert result == {}

    def test_load_config_with_frozen_executable(self):
        """PyInstallerで固められた実行ファイルのパス解決をテスト"""
        test_config = {"test": "value"}

        with tempfile.TemporaryDirectory() as temp_dir:
            # 設定ファイルを作成
            userdata_dir = os.path.join(temp_dir, "UserData")
            os.makedirs(userdata_dir)
            config_file = os.path.join(userdata_dir, "setting.json")
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(test_config, f, ensure_ascii=False)

            # sys.frozen と sys.executable をモック
            with (
                patch.object(sys, "frozen", True, create=True),
                patch.object(sys, "executable", os.path.join(temp_dir, "test.exe")),
            ):
                result = load_config()
                assert result == test_config

    def test_load_config_fallback_paths(self):
        """設定ファイルが複数の場所で探索されることをテスト"""
        test_config = {"fallback": "test"}

        with tempfile.TemporaryDirectory() as temp_dir:
            # 深い階層に設定ファイルを配置
            grandparent_dir = temp_dir
            parent_dir = os.path.join(grandparent_dir, "parent")
            src_dir = os.path.join(parent_dir, "src")
            os.makedirs(src_dir)

            userdata_dir = os.path.join(grandparent_dir, "UserData")
            os.makedirs(userdata_dir)
            config_file = os.path.join(userdata_dir, "setting.json")
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(test_config, f, ensure_ascii=False)

            # __file__ をモック
            with patch("config_loader.__file__", os.path.join(src_dir, "config_loader.py")):
                result = load_config()
                assert result == test_config

    def test_load_config_no_permission(self):
        """ファイルの読み込み権限がない場合のテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = os.path.join(temp_dir, "setting.json")
            with open(config_file, "w", encoding="utf-8") as f:
                f.write('{"test": "value"}')

            # ファイルの読み込み権限を削除
            if os.name != "nt":  # Windowsでない場合のみ権限テストを実行
                os.chmod(config_file, 0o000)

                result = load_config(temp_dir)
                assert result == {}

                # 権限を復元
                os.chmod(config_file, 0o644)
