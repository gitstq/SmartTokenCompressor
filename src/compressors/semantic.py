"""
语义去重压缩模块 - 基于语义相似度去除冗余内容
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import re


@dataclass
class SentenceEmbedding:
    """句子嵌入"""
    sentence: str
    embedding: np.ndarray
    importance: float = 1.0


class SemanticCompressor:
    """语义压缩器"""
    
    def __init__(self, similarity_threshold: float = 0.85, model_name: str = "all-MiniLM-L6-v2"):
        """
        初始化语义压缩器
        
        Args:
            similarity_threshold: 相似度阈值，超过此值视为重复
            model_name: 句子嵌入模型名称
        """
        self.similarity_threshold = similarity_threshold
        self.model_name = model_name
        self._model = None
        self._initialized = False
    
    def _init_model(self):
        """初始化模型"""
        if not self._initialized:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.model_name)
                self._initialized = True
            except ImportError:
                raise ImportError("sentence-transformers is required for semantic compression")
    
    def _split_sentences(self, text: str) -> List[str]:
        """
        分割句子
        
        Args:
            text: 输入文本
            
        Returns:
            句子列表
        """
        # 支持中英文分隔符
        sentences = re.split(r'(?<=[.!?。！？])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _get_embeddings(self, sentences: List[str]) -> np.ndarray:
        """
        获取句子嵌入
        
        Args:
            sentences: 句子列表
            
        Returns:
            嵌入向量
        """
        self._init_model()
        return self._model.encode(sentences, convert_to_numpy=True)
    
    def _calculate_similarity_matrix(self, embeddings: np.ndarray) -> np.ndarray:
        """
        计算相似度矩阵
        
        Args:
            embeddings: 嵌入向量
            
        Returns:
            相似度矩阵
        """
        # 归一化
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        normalized = embeddings / (norms + 1e-8)
        
        # 计算余弦相似度
        similarity_matrix = np.dot(normalized, normalized.T)
        return similarity_matrix
    
    def compress(self, text: str, target_ratio: float = 0.5) -> Dict:
        """
        压缩文本
        
        Args:
            text: 输入文本
            target_ratio: 目标压缩比
            
        Returns:
            压缩结果
        """
        if not text or len(text) < 100:
            return {
                "text": text,
                "removed_sentences": [],
                "kept_sentences": [text],
                "compression_ratio": 1.0,
            }
        
        # 分割句子
        sentences = self._split_sentences(text)
        if len(sentences) <= 1:
            return {
                "text": text,
                "removed_sentences": [],
                "kept_sentences": sentences,
                "compression_ratio": 1.0,
            }
        
        try:
            # 获取嵌入
            embeddings = self._get_embeddings(sentences)
            
            # 计算相似度矩阵
            similarity_matrix = self._calculate_similarity_matrix(embeddings)
            
            # 选择保留的句子
            kept_indices = self._select_sentences(sentences, similarity_matrix, target_ratio)
            
            # 构建结果
            kept_sentences = [sentences[i] for i in sorted(kept_indices)]
            removed_sentences = [sentences[i] for i in range(len(sentences)) if i not in kept_indices]
            
            compressed_text = ' '.join(kept_sentences)
            
            # 计算实际压缩比
            compression_ratio = len(compressed_text) / len(text) if text else 1.0
            
            return {
                "text": compressed_text,
                "removed_sentences": removed_sentences,
                "kept_sentences": kept_sentences,
                "compression_ratio": compression_ratio,
                "similarity_matrix": similarity_matrix.tolist(),
            }
            
        except Exception as e:
            # 如果模型加载失败，回退到简单去重
            return self._fallback_compress(text)
    
    def _select_sentences(self, sentences: List[str], similarity_matrix: np.ndarray, 
                         target_ratio: float) -> set:
        """
        选择要保留的句子
        
        Args:
            sentences: 句子列表
            similarity_matrix: 相似度矩阵
            target_ratio: 目标压缩比
            
        Returns:
            保留的句子索引
        """
        n = len(sentences)
        target_count = max(1, int(n * target_ratio))
        
        # 计算每个句子的重要性
        importances = []
        for i in range(n):
            # 与其他句子的平均相似度（越低越独特）
            avg_sim = np.mean([similarity_matrix[i][j] for j in range(n) if i != j])
            # 句子长度权重
            length_weight = min(len(sentences[i]) / 100, 1.0)
            importance = (1 - avg_sim) * 0.7 + length_weight * 0.3
            importances.append((i, importance))
        
        # 按重要性排序
        importances.sort(key=lambda x: x[1], reverse=True)
        
        # 选择句子，同时避免过于相似的句子
        kept = set()
        for idx, _ in importances:
            if len(kept) >= target_count:
                break
            
            # 检查是否与已选句子过于相似
            should_keep = True
            for kept_idx in kept:
                if similarity_matrix[idx][kept_idx] > self.similarity_threshold:
                    should_keep = False
                    break
            
            if should_keep:
                kept.add(idx)
        
        # 确保至少保留一个句子
        if not kept and sentences:
            kept.add(0)
        
        return kept
    
    def _fallback_compress(self, text: str) -> Dict:
        """
        回退压缩方法（基于规则）
        
        Args:
            text: 输入文本
            
        Returns:
            压缩结果
        """
        sentences = self._split_sentences(text)
        
        # 简单的重复检测
        seen = set()
        kept = []
        removed = []
        
        for sentence in sentences:
            # 归一化用于比较
            normalized = re.sub(r'\s+', ' ', sentence.lower().strip())
            
            if normalized in seen:
                removed.append(sentence)
            else:
                seen.add(normalized)
                kept.append(sentence)
        
        compressed_text = ' '.join(kept)
        compression_ratio = len(compressed_text) / len(text) if text else 1.0
        
        return {
            "text": compressed_text,
            "removed_sentences": removed,
            "kept_sentences": kept,
            "compression_ratio": compression_ratio,
        }
    
    def compress_batch(self, texts: List[str], target_ratio: float = 0.5) -> List[Dict]:
        """
        批量压缩
        
        Args:
            texts: 文本列表
            target_ratio: 目标压缩比
            
        Returns:
            压缩结果列表
        """
        return [self.compress(text, target_ratio) for text in texts]
