"""
压缩器测试
"""

import pytest
from compressors.semantic import SemanticCompressor
from compressors.summarization import TextRankCompressor, ExtractiveCompressor
from compressors.keyword import KeywordCompressor, KeywordDensityCompressor
from compressors.hybrid import HybridCompressor, CompressionConfig, CompressionStrategy


class TestSemanticCompressor:
    """语义压缩器测试"""
    
    def test_compress_empty(self):
        """测试空文本"""
        compressor = SemanticCompressor()
        result = compressor.compress("")
        assert result["text"] == ""
        assert result["compression_ratio"] == 1.0
    
    def test_compress_short(self):
        """测试短文本"""
        compressor = SemanticCompressor()
        text = "Hello world"
        result = compressor.compress(text)
        assert result["text"] == text
    
    def test_compress_long(self):
        """测试长文本"""
        compressor = SemanticCompressor()
        text = "This is a test. " * 50
        result = compressor.compress(text, target_ratio=0.5)
        assert result["compression_ratio"] <= 1.0
        assert len(result["text"]) <= len(text)
    
    def test_compress_batch(self):
        """测试批量压缩"""
        compressor = SemanticCompressor()
        texts = ["Text one", "Text two", "Text three"]
        results = compressor.compress_batch(texts)
        assert len(results) == 3


class TestTextRankCompressor:
    """TextRank压缩器测试"""
    
    def test_compress_empty(self):
        """测试空文本"""
        compressor = TextRankCompressor()
        result = compressor.compress("")
        assert result["text"] == ""
    
    def test_compress_text(self):
        """测试文本压缩"""
        compressor = TextRankCompressor()
        text = "This is sentence one. This is sentence two. This is sentence three. " * 10
        result = compressor.compress(text, target_ratio=0.5)
        assert len(result["text"]) <= len(text)
        assert result["compression_ratio"] <= 1.0
    
    def test_sentence_scores(self):
        """测试句子分数"""
        compressor = TextRankCompressor()
        text = "First sentence. Second sentence. Third sentence."
        result = compressor.compress(text)
        assert "sentence_scores" in result
        assert len(result["sentence_scores"]) == 3


class TestKeywordCompressor:
    """关键词压缩器测试"""
    
    def test_extract_keywords(self):
        """测试关键词提取"""
        compressor = KeywordCompressor()
        text = "Python is great. Python is easy. Python is powerful."
        keywords = compressor.extract_keywords(text)
        assert len(keywords) > 0
        assert any(k[0] == "python" for k in keywords)
    
    def test_compress(self):
        """测试压缩"""
        compressor = KeywordCompressor()
        text = "This is a test about Python programming. Python is great. " * 20
        result = compressor.compress(text, target_ratio=0.5)
        assert len(result["text"]) <= len(text)
        assert "keywords" in result


class TestHybridCompressor:
    """混合压缩器测试"""
    
    def test_compress_semantic(self):
        """测试语义压缩策略"""
        compressor = HybridCompressor()
        text = "This is a test. " * 50
        result = compressor.compress(text, CompressionStrategy.SEMANTIC, 0.5)
        assert result["strategy"] == "semantic"
        assert len(result["text"]) <= len(text)
    
    def test_compress_summarization(self):
        """测试摘要压缩策略"""
        compressor = HybridCompressor()
        text = "First sentence. Second sentence. Third sentence. " * 20
        result = compressor.compress(text, CompressionStrategy.SUMMARIZATION, 0.5)
        assert result["strategy"] == "summarization"
    
    def test_compress_keyword(self):
        """测试关键词压缩策略"""
        compressor = HybridCompressor()
        text = "Python is great. " * 30
        result = compressor.compress(text, CompressionStrategy.KEYWORD, 0.5)
        assert result["strategy"] == "keyword"
    
    def test_compress_hybrid(self):
        """测试混合压缩策略"""
        compressor = HybridCompressor()
        text = "This is a long text. " * 100
        result = compressor.compress(text, CompressionStrategy.HYBRID, 0.5)
        assert result["strategy"] == "hybrid"
        assert "stages" in result
    
    def test_compress_adaptive(self):
        """测试自适应压缩策略"""
        compressor = HybridCompressor()
        text = "This is a test. " * 50
        result = compressor.compress(text, CompressionStrategy.ADAPTIVE, 0.5)
        assert "strategy" in result
    
    def test_compress_batch(self):
        """测试批量压缩"""
        compressor = HybridCompressor()
        texts = ["Text one", "Text two", "Text three"]
        results = compressor.compress_batch(texts)
        assert len(results) == 3
    
    def test_get_compression_stats(self):
        """测试统计信息"""
        compressor = HybridCompressor()
        results = [
            {"compression_ratio": 0.5, "strategy": "hybrid"},
            {"compression_ratio": 0.6, "strategy": "semantic"},
        ]
        stats = compressor.get_compression_stats(results)
        assert "avg_compression_ratio" in stats
        assert stats["avg_compression_ratio"] == 0.55


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
