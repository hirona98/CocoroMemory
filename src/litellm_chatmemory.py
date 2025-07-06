"""LiteLLM対応のChatMemoryクラス"""

from typing import List

import litellm
from chatmemory import ChatMemory


class LiteLLMChatMemory(ChatMemory):
    """LiteLLMを使用するChatMemoryクラス"""

    def __init__(
        self,
        llm_model: str = "openai/gpt-4o-mini",
        api_key: str | None = None,
        embedded_api_key: str | None = None,
        embedded_model: str = "openai/text-embedding-3-small",
        **kwargs,
    ):
        """初期化

        Args:
        ----
            llm_model: 使用するLLMモデル名（LiteLLM形式）
            api_key: APIキー
            embedded_api_key: 埋め込み用APIキー（指定しない場合はapi_keyを使用）
            embedded_model: 埋め込みモデル名
            **kwargs: ChatMemoryクラスの他のパラメータ

        """
        # APIキーを保存
        self.api_key = api_key or ""
        self.embedded_api_key = embedded_api_key or api_key or ""
        self.embedded_model = embedded_model

        # ChatMemoryの初期化（OpenAI APIキーとモデルを設定）
        super().__init__(
            openai_api_key=api_key or "",
            llm_model=llm_model,
            embedding_model=embedded_model,
            **kwargs,
        )

    async def llm(self, system_prompt: str, user_prompt: str) -> str:
        """LiteLLMを使用してLLM応答を生成

        Args:
        ----
            system_prompt: システムプロンプト
            user_prompt: ユーザープロンプト

        Returns:
        -------
            str: LLMの応答

        """
        response = await litellm.acompletion(
            model=self.llm_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
            api_key=self.api_key,  # APIキーを直接指定
        )
        # LiteLLMのレスポンスを処理
        return response.choices[0].message.content  # type: ignore

    async def embed(self, text: str) -> List[float]:
        """テキストの埋め込みベクトルを生成

        Args:
        ----
            text: 埋め込むテキスト

        Returns:
        -------
            List[float]: 埋め込みベクトル

        """
        try:
            # text-embedding-3シリーズの場合はdimensionsパラメータを使用
            embedding_params = {
                "model": self.embedded_model,
                "input": text,
                "api_key": self.embedded_api_key,
            }

            # text-embedding-3シリーズの場合はdimensions=1536を指定
            if "text-embedding-3" in self.embedded_model:
                embedding_params["dimensions"] = 1536  # type: ignore

            response = await litellm.aembedding(**embedding_params)

            # レスポンスの型を確認してデバッグ
            embedding = None
            if isinstance(response, dict):
                # 辞書型の場合
                if "data" in response and len(response["data"]) > 0:
                    embedding = response["data"][0]["embedding"]
                else:
                    raise ValueError(f"Unexpected response format: {response}")
            else:
                # オブジェクト型の場合
                if hasattr(response, "data") and len(response.data) > 0:
                    # response.data[0]がオブジェクトの場合
                    if hasattr(response.data[0], "embedding"):
                        embedding = response.data[0].embedding
                    # response.data[0]が辞書の場合
                    elif isinstance(response.data[0], dict) and "embedding" in response.data[0]:
                        embedding = response.data[0]["embedding"]
                    else:
                        raise ValueError(f"Unexpected data format: {response.data[0]}")
                else:
                    raise ValueError(f"Unexpected response format: {response}")

            # ベクトルのサイズを確認し、必要に応じて調整
            if embedding:
                current_dim = len(embedding)
                target_dim = 1536  # ChatMemoryが期待する次元数

                # text-embedding-3シリーズでdimensionsパラメータを使用した場合は調整不要
                if "text-embedding-3" in self.embedded_model and current_dim == target_dim:
                    return embedding

                # その他のモデルの場合は従来通り調整
                if current_dim != target_dim:
                    print(f"Embedding dimension mismatch: got {current_dim}, expected {target_dim}")
                    if current_dim < target_dim:
                        # パディング（0で埋める）
                        msg = f"Warning: Padding embedding vector from {current_dim} to "
                        msg += f"{target_dim} dimensions"
                        print(msg)
                        embedding = embedding + [0.0] * (target_dim - current_dim)
                    else:
                        # トリミング
                        msg = f"Warning: Trimming embedding vector from {current_dim} to "
                        msg += f"{target_dim} dimensions"
                        print(msg)
                        embedding = embedding[:target_dim]

                return embedding
            else:
                raise ValueError("No embedding found in response")
        except Exception as e:
            print(f"Embedding error: {e}")
            print(f"Model: {self.embedded_model}")
            print(f"API Key: {self.embedded_api_key[:10]}...")
            # response変数が定義されている場合のみ出力
            if "response" in locals():
                print(f"Response type: {type(response)}")
                print(f"Response: {response}")
            raise

    async def search_image_associations(self, user_id: str, query: str, top_k: int = 3) -> str:
        """画像関連の連想記憶を検索"""
        try:
            # 画像関連の記憶を検索
            image_query = f"画像の記憶 {query}"

            # 記憶検索を実行
            search_result = await self.search_async(
                user_id=user_id,
                query=image_query,
                top_k=top_k,
                search_content=True,
                include_retrieved_data=False,
            )

            if search_result and "answer" in search_result:
                return search_result["answer"]
            else:
                return ""

        except Exception as e:
            print(f"画像記憶検索エラー: {e}")
            return ""

    async def search_async(
        self,
        user_id: str,
        query: str,
        top_k: int = 5,
        search_content: bool = False,
        include_retrieved_data: bool = False,
    ):
        """非同期版の記憶検索"""
        try:
            # 要約と知識の検索
            summary_results = await self._search_summaries(user_id, query, top_k)
            knowledge_results = await self._search_knowledge(user_id, query, top_k)

            # 結果をマージ
            all_results = summary_results + knowledge_results

            if not all_results:
                return {"answer": "関連する記憶が見つかりませんでした。"}

            # スコア順にソート
            all_results.sort(key=lambda x: x.get("similarity", 0), reverse=True)
            top_results = all_results[:top_k]

            # LLMで回答を生成
            context = "\n".join([result["content"] for result in top_results])

            system_prompt = (
                "あなたは記憶情報の統合専門家です。\n"
                "検索された複数の記憶を、客観的で正確な情報として整理してください。\n\n"
                "重要な指針：\n"
                "- 矛盾する情報がある場合は明記してください\n"
                "- 推測や創作は絶対に行わないでください\n"
                "- 中立的で事実ベースの文体を使用してください\n"
                "- 感情表現や個性的な口調は使用しないでください\n"
                "- 記憶に含まれる事実のみを整理して報告してください"
            )

            user_prompt = (
                f"質問: {query}\n\n"
                f"関連する記憶:\n"
                f"{context}\n\n"
                "上記の記憶情報を整理して、質問に関連する事実を客観的にまとめてください。"
            )

            answer = await self.llm(system_prompt, user_prompt)

            result = {"answer": answer}
            if include_retrieved_data:
                result["retrieved_data"] = context

            return result

        except Exception as e:
            print(f"記憶検索エラー: {e}")
            return {"answer": "記憶の検索中にエラーが発生しました。"}

    async def _search_summaries(self, user_id: str, query: str, top_k: int):
        """要約テーブルの検索"""
        # 実装は既存のsearch機能の要約検索部分を使用
        # ここでは簡略化
        return []

    async def _search_knowledge(self, user_id: str, query: str, top_k: int):
        """知識テーブルの検索"""
        # 実装は既存のsearch機能の知識検索部分を使用
        # ここでは簡略化
        return []
