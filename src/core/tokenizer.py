"""
Token计数器模块 - 支持多种LLM模型的Token计算
"""

import re
from typing import List, Optional, Dict
from enum import Enum


class ModelType(Enum):
    """支持的模型类型"""
    GPT4 = "gpt-4"
    GPT35 = "gpt-3.5-turbo"
    CLAUDE = "claude"
    LLAMA = "llama"
    GEMINI = "gemini"
    GENERAL = "general"


class TokenCounter:
    """Token计数器"""
    
    # 各模型的平均token/字符比率
    TOKEN_RATIOS = {
        ModelType.GPT4: 0.25,
        ModelType.GPT35: 0.25,
        ModelType.CLAUDE: 0.24,
        ModelType.LLAMA: 0.20,
        ModelType.GEMINI: 0.22,
        ModelType.GENERAL: 0.23,
    }
    
    def __init__(self, model_type: ModelType = ModelType.GENERAL):
        self.model_type = model_type
        self._tiktoken_encoder = None
        
        # 尝试加载tiktoken
        try:
            import tiktoken
            if model_type in [ModelType.GPT4, ModelType.GPT35]:
                self._tiktoken_encoder = tiktoken.encoding_for_model("gpt-4")
        except (ImportError, Exception):
            self._tiktoken_encoder = None
    
    def count_tokens(self, text: str) -> int:
        """
        计算文本的token数量
        
        Args:
            text: 输入文本
            
        Returns:
            Token数量
        """
        if not text:
            return 0
            
        # 优先使用tiktoken
        if self._tiktoken_encoder:
            try:
                return len(self._tiktoken_encoder.encode(text))
            except Exception:
                pass
        
        # 回退到估算方法
        return self._estimate_tokens(text)
    
    def _estimate_tokens(self, text: str) -> int:
        """
        估算token数量（基于字符比率）
        
        Args:
            text: 输入文本
            
        Returns:
            估算的token数量
        """
        ratio = self.TOKEN_RATIOS.get(self.model_type, 0.23)
        
        # 中文字符按1.5个token计算
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        other_chars = len(text) - chinese_chars
        
        estimated = int((chinese_chars * 1.5 + other_chars) * ratio)
        return max(1, estimated)
    
    def count_tokens_batch(self, texts: List[str]) -> List[int]:
        """
        批量计算token数量
        
        Args:
            texts: 文本列表
            
        Returns:
            Token数量列表
        """
        return [self.count_tokens(text) for text in texts]
    
    def get_stats(self, text: str) -> Dict:
        """
        获取文本的token统计信息
        
        Args:
            text: 输入文本
            
        Returns:
            统计信息字典
        """
        tokens = self.count_tokens(text)
        chars = len(text)
        words = len(text.split())
        
        return {
            "tokens": tokens,
            "characters": chars,
            "words": words,
            "tokens_per_char": round(tokens / chars, 4) if chars > 0 else 0,
            "model": self.model_type.value,
        }


def get_token_counter(model_name: str = "general") -> TokenCounter:
    """
    获取指定模型的Token计数器
    
    Args:
        model_name: 模型名称
        
    Returns:
        TokenCounter实例
    """
    model_map = {
        "gpt-4": ModelType.GPT4,
        "gpt-3.5": ModelType.GPT35,
        "claude": ModelType.CLAUDE,
        "llama": ModelType.LLAMA,
        "gemini": ModelType.GEMINI,
    }
    
    model_type = model_map.get(model_name.lower(), ModelType.GENERAL)
    return TokenCounter(model_type)
