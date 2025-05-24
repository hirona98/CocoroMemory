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
            # 埋め込みモデルを使用
            response = await litellm.aembedding(
                model=self.embedded_model,
                input=text,
                api_key=self.embedded_api_key,  # APIキーを直接指定
            )

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
                
                if current_dim != target_dim:
                    print(f"Embedding dimension mismatch: got {current_dim}, expected {target_dim}")
                    if current_dim < target_dim:
                        # パディング（0で埋める）
                        embedding = embedding + [0.0] * (target_dim - current_dim)
                    else:
                        # トリミング
                        embedding = embedding[:target_dim]
                        
                return embedding
            else:
                raise ValueError("No embedding found in response")
        except Exception as e:
            print(f"Embedding error: {e}")
            print(f"Model: {self.embedded_model}")
            print(f"API Key: {self.embedded_api_key[:10]}...") 
            # response変数が定義されている場合のみ出力
            if 'response' in locals():
                print(f"Response type: {type(response)}")
                print(f"Response: {response}")
            raise
