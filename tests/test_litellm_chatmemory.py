"""LiteLLMChatMemoryクラスのテスト"""

from typing import Any, Dict, List
from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.litellm_chatmemory import LiteLLMChatMemory


@pytest.fixture
def mock_chatmemory_init():
    """ChatMemoryの初期化をモックするフィクスチャ"""
    with patch("src.litellm_chatmemory.ChatMemory.__init__", return_value=None):
        yield


class TestLiteLLMChatMemoryInitialization:
    """LiteLLMChatMemoryの初期化テスト"""

    def test_init_with_default_parameters(self, mock_chatmemory_init):
        """デフォルトパラメータでの初期化テスト"""
        chat_memory = LiteLLMChatMemory()

        assert chat_memory.api_key == ""
        assert chat_memory.embedded_api_key == ""
        assert chat_memory.embedded_model == "openai/text-embedding-3-small"
        assert chat_memory.llm_model == "openai/gpt-4o-mini"

    def test_init_with_api_key(self, mock_chatmemory_init):
        """APIキー指定での初期化テスト"""
        api_key = "test-api-key"
        chat_memory = LiteLLMChatMemory(api_key=api_key)

        assert chat_memory.api_key == api_key
        assert chat_memory.embedded_api_key == api_key  # embedded_api_keyが未指定の場合api_keyを使用

    def test_init_with_separate_api_keys(self, mock_chatmemory_init):
        """別々のAPIキー指定での初期化テスト"""
        api_key = "test-api-key"
        embedded_api_key = "test-embedded-api-key"

        chat_memory = LiteLLMChatMemory(api_key=api_key, embedded_api_key=embedded_api_key)

        assert chat_memory.api_key == api_key
        assert chat_memory.embedded_api_key == embedded_api_key

    def test_init_with_custom_models(self, mock_chatmemory_init):
        """カスタムモデル指定での初期化テスト"""
        llm_model = "anthropic/claude-3-haiku-20240307"
        embedded_model = "openai/text-embedding-ada-002"

        chat_memory = LiteLLMChatMemory(llm_model=llm_model, embedded_model=embedded_model)

        assert chat_memory.llm_model == llm_model
        assert chat_memory.embedded_model == embedded_model

    @patch("src.litellm_chatmemory.ChatMemory.__init__")
    def test_init_calls_super_with_correct_parameters(self, mock_super_init):
        """親クラスの初期化が正しいパラメータで呼ばれることを確認"""
        mock_super_init.return_value = None

        api_key = "test-api-key"
        llm_model = "openai/gpt-4o-mini"
        embedded_model = "openai/text-embedding-3-small"

        LiteLLMChatMemory(api_key=api_key, llm_model=llm_model, embedded_model=embedded_model)

        mock_super_init.assert_called_once_with(openai_api_key=api_key, llm_model=llm_model, embedding_model=embedded_model)


class TestLiteLLMChatMemoryLLMMethod:
    """LiteLLMChatMemoryのLLMメソッドテスト"""

    @pytest.mark.asyncio
    @patch("src.litellm_chatmemory.litellm.acompletion")
    async def test_llm_successful_response(self, mock_acompletion, mock_chatmemory_init):
        """LLMメソッドの正常応答テスト"""
        # モックレスポンスを設定
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "テスト応答"
        mock_acompletion.return_value = mock_response

        chat_memory = LiteLLMChatMemory(api_key="test-api-key")

        system_prompt = "あなたは親切なアシスタントです。"
        user_prompt = "こんにちは"

        result = await chat_memory.llm(system_prompt, user_prompt)

        assert result == "テスト応答"
        mock_acompletion.assert_called_once_with(
            model="openai/gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
            api_key="test-api-key",
        )

    @pytest.mark.asyncio
    @patch("src.litellm_chatmemory.litellm.acompletion")
    async def test_llm_with_custom_model(self, mock_acompletion, mock_chatmemory_init):
        """カスタムモデルでのLLMメソッドテスト"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "カスタムモデル応答"
        mock_acompletion.return_value = mock_response

        custom_model = "anthropic/claude-3-haiku-20240307"
        chat_memory = LiteLLMChatMemory(llm_model=custom_model, api_key="test-api-key")

        result = await chat_memory.llm("システム", "ユーザー")

        assert result == "カスタムモデル応答"
        mock_acompletion.assert_called_once_with(
            model=custom_model,
            messages=[
                {"role": "system", "content": "システム"},
                {"role": "user", "content": "ユーザー"},
            ],
            temperature=0.7,
            api_key="test-api-key",
        )

    @pytest.mark.asyncio
    @patch("src.litellm_chatmemory.litellm.acompletion")
    async def test_llm_exception_handling(self, mock_acompletion, mock_chatmemory_init):
        """LLMメソッドの例外処理テスト"""
        mock_acompletion.side_effect = Exception("API エラー")

        chat_memory = LiteLLMChatMemory(api_key="test-api-key")

        with pytest.raises(Exception) as exc_info:
            await chat_memory.llm("システム", "ユーザー")

        assert "API エラー" in str(exc_info.value)


class TestLiteLLMChatMemoryEmbedMethod:
    """LiteLLMChatMemoryの埋め込みメソッドテスト"""

    @pytest.mark.asyncio
    @patch("src.litellm_chatmemory.litellm.aembedding")
    async def test_embed_successful_response_dict_format(self, mock_aembedding, mock_chatmemory_init):
        """埋め込みメソッドの正常応答テスト（辞書形式）"""
        # 1536次元のテストベクトル
        test_embedding = [0.1] * 1536
        mock_response = {"data": [{"embedding": test_embedding}]}
        mock_aembedding.return_value = mock_response

        chat_memory = LiteLLMChatMemory(embedded_api_key="test-embedded-key")

        result = await chat_memory.embed("テストテキスト")

        assert result == test_embedding
        mock_aembedding.assert_called_once_with(model="openai/text-embedding-3-small", input="テストテキスト", api_key="test-embedded-key", dimensions=1536)

    @pytest.mark.asyncio
    @patch("src.litellm_chatmemory.litellm.aembedding")
    async def test_embed_successful_response_object_format(self, mock_aembedding, mock_chatmemory_init):
        """埋め込みメソッドの正常応答テスト（オブジェクト形式）"""
        test_embedding = [0.2] * 1536

        # オブジェクト形式のモックレスポンス
        mock_data_item = Mock()
        mock_data_item.embedding = test_embedding

        mock_response = Mock()
        mock_response.data = [mock_data_item]
        mock_aembedding.return_value = mock_response

        chat_memory = LiteLLMChatMemory(embedded_api_key="test-embedded-key")

        result = await chat_memory.embed("テストテキスト")

        assert result == test_embedding

    @pytest.mark.asyncio
    @patch("src.litellm_chatmemory.litellm.aembedding")
    async def test_embed_with_non_text_embedding_3_model(self, mock_aembedding, mock_chatmemory_init):
        """text-embedding-3以外のモデルでの埋め込みテスト"""
        test_embedding = [0.3] * 1536
        mock_response = {"data": [{"embedding": test_embedding}]}
        mock_aembedding.return_value = mock_response

        chat_memory = LiteLLMChatMemory(embedded_model="openai/text-embedding-ada-002", embedded_api_key="test-embedded-key")

        result = await chat_memory.embed("テストテキスト")

        assert result == test_embedding
        # text-embedding-3以外の場合はdimensionsパラメータが含まれない
        mock_aembedding.assert_called_once_with(model="openai/text-embedding-ada-002", input="テストテキスト", api_key="test-embedded-key")

    @pytest.mark.asyncio
    @patch("src.litellm_chatmemory.litellm.aembedding")
    async def test_embed_dimension_padding(self, mock_aembedding, mock_chatmemory_init):
        """次元数パディングテスト"""
        # 1000次元のベクトル（1536より小さい）
        small_embedding = [0.1] * 1000
        mock_response = {"data": [{"embedding": small_embedding}]}
        mock_aembedding.return_value = mock_response

        chat_memory = LiteLLMChatMemory(embedded_model="openai/text-embedding-ada-002", embedded_api_key="test-embedded-key")

        with patch("builtins.print") as mock_print:
            result = await chat_memory.embed("テストテキスト")

        # 1536次元にパディングされていることを確認
        assert len(result) == 1536
        # 最初の1000要素は元の値
        assert result[:1000] == small_embedding
        # 残りの536要素は0.0
        assert result[1000:] == [0.0] * 536

        # パディングの警告が出力されていることを確認
        mock_print.assert_any_call("Embedding dimension mismatch: got 1000, expected 1536")
        mock_print.assert_any_call("Warning: Padding embedding vector from 1000 to 1536 dimensions")

    @pytest.mark.asyncio
    @patch("src.litellm_chatmemory.litellm.aembedding")
    async def test_embed_dimension_trimming(self, mock_aembedding, mock_chatmemory_init):
        """次元数トリミングテスト"""
        # 2000次元のベクトル（1536より大きい）
        large_embedding = [0.1] * 2000
        mock_response = {"data": [{"embedding": large_embedding}]}
        mock_aembedding.return_value = mock_response

        chat_memory = LiteLLMChatMemory(embedded_model="openai/text-embedding-ada-002", embedded_api_key="test-embedded-key")

        with patch("builtins.print") as mock_print:
            result = await chat_memory.embed("テストテキスト")

        # 1536次元にトリミングされていることを確認
        assert len(result) == 1536
        # 最初の1536要素が保持されていることを確認
        assert result == large_embedding[:1536]

        # トリミングの警告が出力されていることを確認
        mock_print.assert_any_call("Embedding dimension mismatch: got 2000, expected 1536")
        mock_print.assert_any_call("Warning: Trimming embedding vector from 2000 to 1536 dimensions")

    @pytest.mark.asyncio
    @patch("src.litellm_chatmemory.litellm.aembedding")
    async def test_embed_text_embedding_3_no_adjustment(self, mock_aembedding, mock_chatmemory_init):
        """text-embedding-3モデルで正確な次元数の場合の調整なしテスト"""
        test_embedding = [0.1] * 1536
        mock_response = {"data": [{"embedding": test_embedding}]}
        mock_aembedding.return_value = mock_response

        chat_memory = LiteLLMChatMemory(embedded_model="openai/text-embedding-3-small", embedded_api_key="test-embedded-key")

        with patch("builtins.print") as mock_print:
            result = await chat_memory.embed("テストテキスト")

        # 調整なしで返される
        assert result == test_embedding
        # 次元数不一致の警告が出力されていないことを確認
        mock_print.assert_not_called()

    @pytest.mark.asyncio
    @patch("src.litellm_chatmemory.litellm.aembedding")
    async def test_embed_empty_response_data(self, mock_aembedding, mock_chatmemory_init):
        """空の応答データでの例外処理テスト"""
        mock_response = {"data": []}
        mock_aembedding.return_value = mock_response

        chat_memory = LiteLLMChatMemory(embedded_api_key="test-embedded-key")

        with pytest.raises(ValueError) as exc_info:
            await chat_memory.embed("テストテキスト")

        assert "Unexpected response format" in str(exc_info.value)

    @pytest.mark.asyncio
    @patch("src.litellm_chatmemory.litellm.aembedding")
    async def test_embed_missing_embedding_key(self, mock_aembedding, mock_chatmemory_init):
        """embedding キーが存在しない場合の例外処理テスト"""
        mock_response = {"data": [{"no_embedding": [0.1, 0.2]}]}
        mock_aembedding.return_value = mock_response

        chat_memory = LiteLLMChatMemory(embedded_api_key="test-embedded-key")

        with pytest.raises(ValueError) as exc_info:
            await chat_memory.embed("テストテキスト")

        assert "Unexpected response format" in str(exc_info.value)

    @pytest.mark.asyncio
    @patch("src.litellm_chatmemory.litellm.aembedding")
    async def test_embed_api_exception_handling(self, mock_aembedding, mock_chatmemory_init):
        """API例外の処理テスト"""
        mock_aembedding.side_effect = Exception("API エラー")

        chat_memory = LiteLLMChatMemory(embedded_api_key="test-embedded-key")

        with patch("builtins.print") as mock_print:
            with pytest.raises(Exception) as exc_info:
                await chat_memory.embed("テストテキスト")

        assert "API エラー" in str(exc_info.value)
        # エラー詳細が出力されていることを確認
        mock_print.assert_any_call("Embedding error: API エラー")
        mock_print.assert_any_call("Model: openai/text-embedding-3-small")
        mock_print.assert_any_call("API Key: test-embed...")

    @pytest.mark.asyncio
    @patch("src.litellm_chatmemory.litellm.aembedding")
    async def test_embed_object_format_with_dict_data(self, mock_aembedding, mock_chatmemory_init):
        """オブジェクト形式だがdata[0]が辞書の場合のテスト"""
        test_embedding = [0.4] * 1536

        mock_response = Mock()
        mock_response.data = [{"embedding": test_embedding}]
        mock_aembedding.return_value = mock_response

        chat_memory = LiteLLMChatMemory(embedded_api_key="test-embedded-key")

        result = await chat_memory.embed("テストテキスト")

        assert result == test_embedding

    @pytest.mark.asyncio
    @patch("src.litellm_chatmemory.litellm.aembedding")
    async def test_embed_object_format_unexpected_data_structure(self, mock_aembedding, mock_chatmemory_init):
        """オブジェクト形式で予期しないデータ構造の場合のテスト"""
        mock_response = Mock()
        mock_response.data = [{"unexpected": "data"}]
        mock_aembedding.return_value = mock_response

        chat_memory = LiteLLMChatMemory(embedded_api_key="test-embedded-key")

        with pytest.raises(ValueError) as exc_info:
            await chat_memory.embed("テストテキスト")

        assert "Unexpected data format" in str(exc_info.value)


class TestLiteLLMChatMemoryIntegration:
    """LiteLLMChatMemoryの統合テスト"""

    @pytest.mark.asyncio
    @patch("src.litellm_chatmemory.litellm.acompletion")
    @patch("src.litellm_chatmemory.litellm.aembedding")
    async def test_llm_and_embed_integration(self, mock_aembedding, mock_acompletion, mock_chatmemory_init):
        """LLMと埋め込みメソッドの統合テスト"""
        # LLMモックレスポンス
        mock_llm_response = Mock()
        mock_llm_response.choices = [Mock()]
        mock_llm_response.choices[0].message.content = "統合テスト応答"
        mock_acompletion.return_value = mock_llm_response

        # 埋め込みモックレスポンス
        test_embedding = [0.5] * 1536
        mock_embed_response = {"data": [{"embedding": test_embedding}]}
        mock_aembedding.return_value = mock_embed_response

        chat_memory = LiteLLMChatMemory(api_key="test-api-key", embedded_api_key="test-embedded-key")

        # LLMメソッドのテスト
        llm_result = await chat_memory.llm("システム", "ユーザー")
        assert llm_result == "統合テスト応答"

        # 埋め込みメソッドのテスト
        embed_result = await chat_memory.embed("テストテキスト")
        assert embed_result == test_embedding

        # 両方のAPIが呼ばれたことを確認
        mock_acompletion.assert_called_once()
        mock_aembedding.assert_called_once()

    def test_api_key_inheritance(self, mock_chatmemory_init):
        """APIキーの継承テスト"""
        # api_keyのみ指定
        chat_memory1 = LiteLLMChatMemory(api_key="shared-key")
        assert chat_memory1.api_key == "shared-key"
        assert chat_memory1.embedded_api_key == "shared-key"

        # 別々のキーを指定
        chat_memory2 = LiteLLMChatMemory(api_key="llm-key", embedded_api_key="embed-key")
        assert chat_memory2.api_key == "llm-key"
        assert chat_memory2.embedded_api_key == "embed-key"

        # embedded_api_keyのみ指定
        chat_memory3 = LiteLLMChatMemory(embedded_api_key="embed-only-key")
        assert chat_memory3.api_key == ""
        assert chat_memory3.embedded_api_key == "embed-only-key"

    @pytest.mark.asyncio
    @patch("src.litellm_chatmemory.litellm.aembedding")
    async def test_different_embedding_models(self, mock_aembedding, mock_chatmemory_init):
        """異なる埋め込みモデルでのテスト"""
        test_embedding = [0.6] * 1536
        mock_response = {"data": [{"embedding": test_embedding}]}
        mock_aembedding.return_value = mock_response

        models_to_test = ["openai/text-embedding-3-small", "openai/text-embedding-3-large", "openai/text-embedding-ada-002"]

        for model in models_to_test:
            chat_memory = LiteLLMChatMemory(embedded_model=model, embedded_api_key="test-key")

            result = await chat_memory.embed("テストテキスト")
            assert result == test_embedding

            # text-embedding-3シリーズの場合はdimensionsパラメータが含まれる
            if "text-embedding-3" in model:
                expected_call = {"model": model, "input": "テストテキスト", "api_key": "test-key", "dimensions": 1536}
            else:
                expected_call = {"model": model, "input": "テストテキスト", "api_key": "test-key"}

            mock_aembedding.assert_called_with(**expected_call)
            mock_aembedding.reset_mock()


# エラーケースの詳細テスト
class TestLiteLLMChatMemoryErrorCases:
    """エラーケースの詳細テスト"""

    @pytest.mark.asyncio
    @patch("src.litellm_chatmemory.litellm.aembedding")
    async def test_embed_no_data_key(self, mock_aembedding, mock_chatmemory_init):
        """dataキーが存在しない場合のテスト"""
        mock_response = {"no_data": []}
        mock_aembedding.return_value = mock_response

        chat_memory = LiteLLMChatMemory(embedded_api_key="test-key")

        with pytest.raises(ValueError) as exc_info:
            await chat_memory.embed("テストテキスト")

        assert "Unexpected response format" in str(exc_info.value)

    @pytest.mark.asyncio
    @patch("src.litellm_chatmemory.litellm.aembedding")
    async def test_embed_object_response_no_data_attribute(self, mock_aembedding, mock_chatmemory_init):
        """オブジェクトレスポンスでdataアトリビュートが存在しない場合のテスト"""
        mock_response = Mock()
        # dataアトリビュートを持たないオブジェクト
        mock_response.no_data = []
        # dataアトリビュートを削除してhasattr(response, "data")がFalseになるようにする
        if hasattr(mock_response, "data"):
            delattr(mock_response, "data")
        mock_aembedding.return_value = mock_response

        chat_memory = LiteLLMChatMemory(embedded_api_key="test-key")

        with pytest.raises(ValueError) as exc_info:
            await chat_memory.embed("テストテキスト")

        assert "Unexpected response format" in str(exc_info.value)

    @pytest.mark.asyncio
    @patch("src.litellm_chatmemory.litellm.aembedding")
    async def test_embed_object_response_empty_data(self, mock_aembedding, mock_chatmemory_init):
        """オブジェクトレスポンスでdataが空の場合のテスト"""
        mock_response = Mock()
        mock_response.data = []
        mock_aembedding.return_value = mock_response

        chat_memory = LiteLLMChatMemory(embedded_api_key="test-key")

        with pytest.raises(ValueError) as exc_info:
            await chat_memory.embed("テストテキスト")

        assert "Unexpected response format" in str(exc_info.value)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
