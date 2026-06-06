"""
Token计数器测试
"""

import pytest
from core.tokenizer import TokenCounter, ModelType, get_token_counter


class TestTokenCounter:
    """TokenCounter测试类"""
    
    def test_count_tokens_empty(self):
        """测试空文本"""
        counter = TokenCounter()
        assert counter.count_tokens("") == 0
    
    def test_count_tokens_simple(self):
        """测试简单文本"""
        counter = TokenCounter()
        text = "Hello world"
        tokens = counter.count_tokens(text)
        assert tokens > 0
    
    def test_count_tokens_chinese(self):
        """测试中文文本"""
        counter = TokenCounter()
        text = "这是一个中文测试"
        tokens = counter.count_tokens(text)
        assert tokens > 0
    
    def test_count_tokens_batch(self):
        """测试批量计算"""
        counter = TokenCounter()
        texts = ["Hello", "World", "Test"]
        results = counter.count_tokens_batch(texts)
        assert len(results) == 3
        assert all(r > 0 for r in results)
    
    def test_get_stats(self):
        """测试统计信息"""
        counter = TokenCounter()
        text = "Hello world, this is a test."
        stats = counter.get_stats(text)
        
        assert "tokens" in stats
        assert "characters" in stats
        assert "words" in stats
        assert "tokens_per_char" in stats
        assert "model" in stats
        
        assert stats["characters"] == len(text)
        assert stats["words"] == 6
    
    def test_different_models(self):
        """测试不同模型"""
        text = "Hello world"
        
        for model_type in ModelType:
            counter = TokenCounter(model_type)
            tokens = counter.count_tokens(text)
            assert tokens > 0
    
    def test_get_token_counter(self):
        """测试获取计数器"""
        counter = get_token_counter("gpt-4")
        assert counter.model_type == ModelType.GPT4
        
        counter = get_token_counter("general")
        assert counter.model_type == ModelType.GENERAL


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
