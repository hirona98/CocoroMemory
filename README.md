# CocoroMemory

CocoroMemory は、会話履歴を管理するための組み込み PostgreSQL データベースを含む AI アシスタントアプリケーションです。

## パッケージの内容

このパッケージには以下のコンポーネントが含まれています：

- CocoroMemory API サーバー
- 組み込み PostgreSQL データベース
- 設定ファイルおよびスクリプト

## インストールと実行

### 動作環境

- Windows 10/11
- 最低 4GB のメモリ
- 約 300MB のディスク容量

### 使用方法

1. ダウンロードしたパッケージを任意の場所に展開します
2. `CocoroMemory.exe` を実行します
   - 初回実行時には PostgreSQL データベースが自動的に初期化されます
   - 起動時に PostgreSQL サーバーが自動的に起動します
3. ブラウザで `http://localhost:8000/docs` にアクセスして API ドキュメントを参照できます

### .env ファイルの設定

アプリケーションのルートディレクトリに `.env` ファイルを作成し、以下の内容を設定してください：

```
OPENAI_API_KEY=your_api_key_here
```

## PostgreSQL のデータベース情報

- データベース名: postgres
- ユーザー名: postgres
- パスワード: postgres
- ホスト: 127.0.0.1
- ポート: 5433

## 手動でのデータベース操作

必要に応じて、以下のスクリプトでデータベースを手動操作できます：

- `Scripts\initdb.bat`: データベースの初期化
- `Scripts\start_postgres.bat`: PostgreSQL サーバーの手動起動
- `Scripts\stop_postgres.bat`: PostgreSQL サーバーの手動停止

データベースファイルは `Data` ディレクトリに保存されます。

## トラブルシューティング

問題が発生した場合は、以下を確認してください：

1. `Logs` ディレクトリ内のログファイルでエラーを確認
2. `.env` ファイルが正しく設定されているか確認
3. ポート 5433 と 8000 が他のアプリケーションで使用されていないか確認

## ライセンス

Copyright (c) 2024-2025 CocoroAI

このソフトウェアは、PostgreSQL のライセンスに準拠して利用しています。
詳細は PostgreSQL のライセンス (https://www.postgresql.org/about/licence/) を参照してください。
 
