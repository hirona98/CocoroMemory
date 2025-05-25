# CocoroMemory

CocoroMemory は、CocoroAI の長期記憶機能です

## コマンドライン引数

設定ディレクトリを指定して起動することが可能です：

```bash
CocoroMemory.exe --config-dir C:\path\to\config
# または
CocoroMemory.exe C:\path\to\config
```

## PostgreSQL のデータベース情報

- データベース名: postgres
- ユーザー名: postgres
- パスワード: postgres
- ホスト: 127.0.0.1
- ポート: 設定ファイルより読み込み（無い時は5433）

## 手動でのデータベース操作

必要に応じて、以下のスクリプトでデータベースを手動操作できます：

- `Data`ディレクトリの削除: データベースの削除
- `Scripts\initdb.bat`: データベースの初期化
- `Scripts\start_postgres.bat`: PostgreSQL サーバーの手動起動
- `Scripts\stop_postgres.bat`: PostgreSQL サーバーの手動停止

データベースファイルは起動時に自動生成されます。
