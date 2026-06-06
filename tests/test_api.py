"""
API测试
"""

import pytest
from fastapi.testclient import TestClient

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from api.server import app


client = TestClient(app)


class TestAPI:
    """API测试类"""
    
    def test_health(self):
        """测试健康检查"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
    
    def test_compress(self):
        """测试压缩接口"""
        response = client.post("/api/v1/compress", json={
            "text": "This is a test. " * 50,
            "strategy": "hybrid",
            "target_ratio": 0.5,
            "model": "general",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "compressed_text" in data
        assert "original_tokens" in data
        assert "compressed_tokens" in data
        assert "tokens_saved" in data
    
    def test_compress_empty(self):
        """测试空文本压缩"""
        response = client.post("/api/v1/compress", json={
            "text": "",
            "strategy": "hybrid",
        })
        assert response.status_code == 422  # 验证错误
    
    def test_compress_batch(self):
        """测试批量压缩"""
        response = client.post("/api/v1/compress/batch", json={
            "texts": ["Text one", "Text two", "Text three"],
            "strategy": "hybrid",
            "target_ratio": 0.5,
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["results"]) == 3
    
    def test_count_tokens(self):
        """测试Token计数"""
        response = client.post("/api/v1/tokens/count", json={
            "text": "Hello world",
            "model": "general",
        })
        assert response.status_code == 200
        data = response.json()
        assert "tokens" in data
        assert "characters" in data
        assert "words" in data
    
    def test_analyze(self):
        """测试文本分析"""
        response = client.post("/api/v1/analyze", json={
            "text": "This is a test.\n\nAnother paragraph.",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "analysis" in data
    
    def test_stats(self):
        """测试统计信息"""
        response = client.get("/api/v1/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "uptime_seconds" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
