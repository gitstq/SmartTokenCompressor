"""
混合策略压缩模块 - 结合多种压缩算法
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum

from .semantic import SemanticCompressor
from .summarization import TextRankCompressor, ExtractiveCompressor
from .keyword import KeywordCompressor, KeywordDensityCompressor


class CompressionStrategy(Enum):
    """压缩策略"""
    SEMANTIC = "semantic"
    SUMMARIZATION = "summarization"
    KEYWORD = "keyword"
    HYBRID = "hybrid"
    ADAPTIVE = "adaptive"


@dataclass
class CompressionConfig:
    """压缩配置"""
    strategy: CompressionStrategy = CompressionStrategy.HYBRID
    target_ratio: float = 0.5
    semantic_threshold: float = 0.85
    summarization_ratio: float = 0.3
    keyword_ratio: float = 0.4
    quality_threshold: float = 0.7
    preserve_code: bool = True
    preserve_tables: bool = True
    preserve_urls: bool = True


class HybridCompressor:
    """混合压缩器"""
    
    def __init__(self, config: Optional[CompressionConfig] = None):
        """
        初始化混合压缩器
        
        Args:
            config: 压缩配置
        """
        self.config = config or CompressionConfig()
        
        # 初始化各压缩器
        self._semantic = SemanticCompressor(
            similarity_threshold=self.config.semantic_threshold
        )
        self._summarization = TextRankCompressor()
        self._extractive = ExtractiveCompressor()
        self._keyword = KeywordCompressor()
        self._density = KeywordDensityCompressor()
    
    def compress(self, text: str, strategy: Optional[CompressionStrategy] = None,
                 target_ratio: Optional[float] = None) -> Dict:
        """
        压缩文本
        
        Args:
            text: 输入文本
            strategy: 压缩策略（覆盖配置）
            target_ratio: 目标压缩比（覆盖配置）
            
        Returns:
            压缩结果
        """
        strategy = strategy or self.config.strategy
        target_ratio = target_ratio or self.config.target_ratio
        
        if not text or len(text) < 100:
            return {
                "text": text,
                "strategy": strategy.value,
                "compression_ratio": 1.0,
                "stages": [],
            }
        
        # 根据策略选择压缩方法
        if strategy == CompressionStrategy.SEMANTIC:
            return self._semantic_compress(text, target_ratio)
        elif strategy == CompressionStrategy.SUMMARIZATION:
            return self._summarization_compress(text, target_ratio)
        elif strategy == CompressionStrategy.KEYWORD:
            return self._keyword_compress(text, target_ratio)
        elif strategy == CompressionStrategy.ADAPTIVE:
            return self._adaptive_compress(text, target_ratio)
        else:
            return self._hybrid_compress(text, target_ratio)
    
    def _semantic_compress(self, text: str, target_ratio: float) -> Dict:
        """语义压缩"""
        result = self._semantic.compress(text, target_ratio)
        result["strategy"] = CompressionStrategy.SEMANTIC.value
        result["stages"] = ["semantic_deduplication"]
        return result
    
    def _summarization_compress(self, text: str, target_ratio: float) -> Dict:
        """摘要压缩"""
        result = self._summarization.compress(text, target_ratio)
        result["strategy"] = CompressionStrategy.SUMMARIZATION.value
        result["stages"] = ["textrank_summarization"]
        return result
    
    def _keyword_compress(self, text: str, target_ratio: float) -> Dict:
        """关键词压缩"""
        result = self._keyword.compress(text, target_ratio)
        result["strategy"] = CompressionStrategy.KEYWORD.value
        result["stages"] = ["keyword_extraction"]
        return result
    
    def _hybrid_compress(self, text: str, target_ratio: float) -> Dict:
        """
        混合压缩（多阶段）
        
        阶段1: 语义去重
        阶段2: 关键词提取
        阶段3: 摘要生成
        """
        stages = []
        current_text = text
        
        # 阶段1: 语义去重（去除30%冗余）
        stage1_ratio = min(0.7, 1 / target_ratio * 0.7) if target_ratio < 1 else 0.7
        result1 = self._semantic.compress(current_text, stage1_ratio)
        current_text = result1["text"]
        stages.append({
            "stage": "semantic_deduplication",
            "compression_ratio": result1["compression_ratio"],
            "removed_sentences": len(result1.get("removed_sentences", [])),
        })
        
        # 阶段2: 关键词压缩（进一步压缩）
        stage2_ratio = min(0.8, target_ratio / result1["compression_ratio"]) if result1["compression_ratio"] > 0 else 0.8
        result2 = self._keyword.compress(current_text, stage2_ratio)
        current_text = result2["text"]
        stages.append({
            "stage": "keyword_extraction",
            "compression_ratio": result2["compression_ratio"],
            "keywords": [k[0] for k in result2.get("keywords", [])[:5]],
        })
        
        # 阶段3: 如果还需要进一步压缩，使用摘要
        current_ratio = len(current_text) / len(text) if text else 1.0
        if current_ratio > target_ratio and len(current_text) > 100:
            stage3_ratio = target_ratio / current_ratio if current_ratio > 0 else 0.5
            result3 = self._summarization.compress(current_text, stage3_ratio)
            current_text = result3["text"]
            stages.append({
                "stage": "summarization",
                "compression_ratio": result3["compression_ratio"],
                "summary_sentences": len(result3.get("summary_sentences", [])),
            })
        
        # 计算总体压缩比
        final_ratio = len(current_text) / len(text) if text else 1.0
        
        return {
            "text": current_text,
            "strategy": CompressionStrategy.HYBRID.value,
            "compression_ratio": final_ratio,
            "stages": stages,
            "original_length": len(text),
            "compressed_length": len(current_text),
        }
    
    def _adaptive_compress(self, text: str, target_ratio: float) -> Dict:
        """
        自适应压缩（根据内容类型选择策略）
        """
        from ..core.analyzer import ContentAnalyzer
        
        analyzer = ContentAnalyzer()
        content_type = analyzer.detect_content_type(text)
        
        # 根据内容类型选择策略
        if content_type.value == "code":
            # 代码：保留结构，去除注释和空行
            return self._compress_code(text, target_ratio)
        elif content_type.value == "log":
            # 日志：去除重复和无关信息
            return self._compress_log(text, target_ratio)
        elif content_type.value == "json":
            # JSON：去除空白和默认值
            return self._compress_json(text, target_ratio)
        else:
            # 默认使用混合策略
            return self._hybrid_compress(text, target_ratio)
    
    def _compress_code(self, text: str, target_ratio: float) -> Dict:
        """压缩代码"""
        import re
        
        # 去除注释
        text = re.sub(r'#.*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'//.*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
        
        # 去除多余空行
        text = re.sub(r'\n\s*\n', '\n', text)
        
        # 去除行尾空格
        text = re.sub(r'[ \t]+$', '', text, flags=re.MULTILINE)
        
        compression_ratio = len(text) / len(text) if text else 1.0
        
        return {
            "text": text,
            "strategy": "adaptive_code",
            "compression_ratio": compression_ratio,
            "stages": ["remove_comments", "remove_empty_lines", "trim_whitespace"],
        }
    
    def _compress_log(self, text: str, target_ratio: float) -> Dict:
        """压缩日志"""
        import re
        
        lines = text.split('\n')
        
        # 去除重复日志
        seen_patterns = set()
        unique_lines = []
        
        for line in lines:
            # 提取日志模式（去除时间戳和具体值）
            pattern = re.sub(r'\d{4}-\d{2}-\d{2}[\sT]\d{2}:\d{2}:\d{2}', '<TIME>', line)
            pattern = re.sub(r'\d+', '<NUM>', pattern)
            
            if pattern not in seen_patterns:
                seen_patterns.add(pattern)
                unique_lines.append(line)
        
        compressed_text = '\n'.join(unique_lines)
        compression_ratio = len(compressed_text) / len(text) if text else 1.0
        
        return {
            "text": compressed_text,
            "strategy": "adaptive_log",
            "compression_ratio": compression_ratio,
            "stages": ["deduplicate_patterns"],
            "removed_lines": len(lines) - len(unique_lines),
        }
    
    def _compress_json(self, text: str, target_ratio: float) -> Dict:
        """压缩JSON"""
        import json
        
        try:
            data = json.loads(text)
            # 压缩JSON（去除空白）
            compressed = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
            
            compression_ratio = len(compressed) / len(text) if text else 1.0
            
            return {
                "text": compressed,
                "strategy": "adaptive_json",
                "compression_ratio": compression_ratio,
                "stages": ["remove_whitespace"],
            }
        except json.JSONDecodeError:
            # 如果不是有效JSON，使用默认策略
            return self._hybrid_compress(text, target_ratio)
    
    def compress_batch(self, texts: List[str], strategy: Optional[CompressionStrategy] = None,
                      target_ratio: Optional[float] = None) -> List[Dict]:
        """
        批量压缩
        
        Args:
            texts: 文本列表
            strategy: 压缩策略
            target_ratio: 目标压缩比
            
        Returns:
            压缩结果列表
        """
        return [self.compress(text, strategy, target_ratio) for text in texts]
    
    def get_compression_stats(self, results: List[Dict]) -> Dict:
        """
        获取压缩统计信息
        
        Args:
            results: 压缩结果列表
            
        Returns:
            统计信息
        """
        if not results:
            return {}
        
        ratios = [r["compression_ratio"] for r in results]
        
        return {
            "total_documents": len(results),
            "avg_compression_ratio": sum(ratios) / len(ratios),
            "min_compression_ratio": min(ratios),
            "max_compression_ratio": max(ratios),
            "strategies_used": list(set(r["strategy"] for r in results)),
        }
