"""LiteLLM対応のChatMemoryクラス"""

import os
from typing import List

import litellm
from chatmemory import ChatMemory


class LiteLLMChatMemory(ChatMemory):
    """LiteLLMを使用するChatMemoryクラス"""

    def __init__(self, llm_model: str = "openai/gpt-4o-mini", api_key: str | None = None, **kwargs):
        """初期化

        Args:
        ----
            llm_model: 使用するLLMモデル名（LiteLLM形式）
            api_key: APIキー
            **kwargs: ChatMemoryクラスの他のパラメータ

        """
        # ChatMemoryの初期化（OpenAI APIキーとモデルを設定）
        super().__init__(
            openai_api_key=api_key or os.getenv("OPENAI_API_KEY") or "",
            llm_model=llm_model,
            embedding_model="text-embedding-3-small",
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
        )
        return response.choices[0].message.content

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
            # 常にOpenAIの埋め込みモデルを使用
            response = await litellm.aembedding(
                model=self.embedding_model,
                input=text,
            )

            # レスポンスの型を確認してデバッグ
            if isinstance(response, dict):
                # 辞書型の場合
                if "data" in response and len(response["data"]) > 0:
                    return response["data"][0]["embedding"]
                else:
                    raise ValueError(f"Unexpected response format: {response}")
            else:
                # オブジェクト型の場合
                if hasattr(response, "data") and len(response.data) > 0:
                    # response.data[0]がオブジェクトの場合
                    if hasattr(response.data[0], "embedding"):
                        return response.data[0].embedding
                    # response.data[0]が辞書の場合
                    elif isinstance(response.data[0], dict) and "embedding" in response.data[0]:
                        return response.data[0]["embedding"]
                    else:
                        raise ValueError(f"Unexpected data format: {response.data[0]}")
                else:
                    raise ValueError(f"Unexpected response format: {response}")
        except Exception as e:
            print(f"Embedding error: {e}")
            print(f"Response type: {type(response)}")
            print(f"Response: {response}")
            raise
