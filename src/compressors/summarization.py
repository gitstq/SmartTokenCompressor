"""
摘要压缩模块 - 基于TextRank和关键句提取
"""

import re
import math
from typing import List, Dict, Tuple
from collections import defaultdict
import numpy as np


class TextRankCompressor:
    """基于TextRank的压缩器"""
    
    def __init__(self, damping: float = 0.85, max_iterations: int = 100, 
                 convergence_threshold: float = 0.0001):
        """
        初始化TextRank压缩器
        
        Args:
            damping: 阻尼系数
            max_iterations: 最大迭代次数
            convergence_threshold: 收敛阈值
        """
        self.damping = damping
        self.max_iterations = max_iterations
        self.convergence_threshold = convergence_threshold
    
    def _tokenize(self, text: str) -> List[str]:
        """
        分词
        
        Args:
            text: 输入文本
            
        Returns:
            词列表
        """
        # 简单的分词（按非字母数字字符分割）
        words = re.findall(r'[a-zA-Z]+|[\u4e00-\u9fff]', text.lower())
        return words
    
    def _split_sentences(self, text: str) -> List[str]:
        """
        分割句子
        
        Args:
            text: 输入文本
            
        Returns:
            句子列表
        """
        sentences = re.split(r'(?<=[.!?。！？])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _calculate_similarity(self, sent1: str, sent2: str) -> float:
        """
        计算句子相似度
        
        Args:
            sent1: 句子1
            sent2: 句子2
            
        Returns:
            相似度分数
        """
        words1 = set(self._tokenize(sent1))
        words2 = set(self._tokenize(sent2))
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union) if union else 0.0
    
    def _build_similarity_matrix(self, sentences: List[str]) -> np.ndarray:
        """
        构建相似度矩阵
        
        Args:
            sentences: 句子列表
            
        Returns:
            相似度矩阵
        """
        n = len(sentences)
        matrix = np.zeros((n, n))
        
        for i in range(n):
            for j in range(n):
                if i != j:
                    matrix[i][j] = self._calculate_similarity(sentences[i], sentences[j])
        
        return matrix
    
    def _textrank(self, similarity_matrix: np.ndarray) -> np.ndarray:
        """
        TextRank算法
        
        Args:
            similarity_matrix: 相似度矩阵
            
        Returns:
            句子权重
        """
        n = similarity_matrix.shape[0]
        
        # 归一化相似度矩阵
        row_sums = similarity_matrix.sum(axis=1, keepdims=True)
        normalized_matrix = similarity_matrix / (row_sums + 1e-8)
        
        # 初始化权重
        scores = np.ones(n) / n
        
        # 迭代计算
        for _ in range(self.max_iterations):
            new_scores = (1 - self.damping) / n + self.damping * np.dot(normalized_matrix.T, scores)
            
            # 检查收敛
            if np.sum(np.abs(new_scores - scores)) < self.convergence_threshold:
                break
            
            scores = new_scores
        
        return scores
    
    def compress(self, text: str, target_ratio: float = 0.3) -> Dict:
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
                "summary_sentences": [],
                "compression_ratio": 1.0,
                "sentence_scores": [],
            }
        
        # 分割句子
        sentences = self._split_sentences(text)
        if len(sentences) <= 2:
            return {
                "text": text,
                "summary_sentences": sentences,
                "compression_ratio": 1.0,
                "sentence_scores": [(s, 1.0) for s in sentences],
            }
        
        # 构建相似度矩阵
        similarity_matrix = self._build_similarity_matrix(sentences)
        
        # 计算TextRank分数
        scores = self._textrank(similarity_matrix)
        
        # 选择top句子
        n = len(sentences)
        target_count = max(1, int(n * target_ratio))
        
        # 按分数排序
        scored_sentences = [(i, scores[i], sentences[i]) for i in range(n)]
        scored_sentences.sort(key=lambda x: x[1], reverse=True)
        
        # 选择top句子并按原文顺序排列
        top_indices = sorted([x[0] for x in scored_sentences[:target_count]])
        summary_sentences = [sentences[i] for i in top_indices]
        
        # 构建摘要
        compressed_text = ' '.join(summary_sentences)
        
        # 计算压缩比
        compression_ratio = len(compressed_text) / len(text) if text else 1.0
        
        return {
            "text": compressed_text,
            "summary_sentences": summary_sentences,
            "compression_ratio": compression_ratio,
            "sentence_scores": [(sentences[i], float(scores[i])) for i in range(n)],
        }
    
    def compress_batch(self, texts: List[str], target_ratio: float = 0.3) -> List[Dict]:
        """
        批量压缩
        
        Args:
            texts: 文本列表
            target_ratio: 目标压缩比
            
        Returns:
            压缩结果列表
        """
        return [self.compress(text, target_ratio) for text in texts]


class ExtractiveCompressor:
    """提取式压缩器"""
    
    def __init__(self):
        self._stopwords = self._load_stopwords()
    
    def _load_stopwords(self) -> set:
        """加载停用词"""
        # 基础停用词
        stopwords = {
            'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
            'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'could', 'should', 'may', 'might', 'must', 'shall',
            'can', 'need', 'dare', 'ought', 'used', 'to', 'of', 'in',
            'for', 'on', 'with', 'at', 'by', 'from', 'as', 'into',
            'through', 'during', 'before', 'after', 'above', 'below',
            'between', 'under', 'again', 'further', 'then', 'once',
            'here', 'there', 'when', 'where', 'why', 'how', 'all',
            'each', 'few', 'more', 'most', 'other', 'some', 'such',
            'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than',
            'too', 'very', 'just', 'and', 'but', 'if', 'or', 'because',
            'until', 'while', 'this', 'that', 'these', 'those', 'i',
            'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves',
            'you', 'your', 'yours', 'yourself', 'yourselves', 'he',
            'him', 'his', 'himself', 'she', 'her', 'hers', 'herself',
            'it', 'its', 'itself', 'they', 'them', 'their', 'theirs',
            'themselves', 'what', 'which', 'who', 'whom', 'whose',
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人',
            '都', '一', '一个', '上', '也', '很', '到', '说', '要',
            '去', '你', '会', '着', '没有', '看', '好', '自己', '这',
        }
        return stopwords
    
    def _extract_keywords(self, text: str, top_k: int = 10) -> List[Tuple[str, float]]:
        """
        提取关键词
        
        Args:
            text: 输入文本
            top_k: 返回关键词数量
            
        Returns:
            关键词列表
        """
        words = re.findall(r'[a-zA-Z]+|[\u4e00-\u9fff]', text.lower())
        
        # 过滤停用词和短词
        filtered_words = [w for w in words if w not in self._stopwords and len(w) > 1]
        
        # 统计词频
        word_freq = defaultdict(int)
        for word in filtered_words:
            word_freq[word] += 1
        
        # 计算TF-IDF（简化版）
        total_words = len(filtered_words)
        keywords = []
        for word, freq in word_freq.items():
            tf = freq / total_words
            # 使用词频作为权重
            keywords.append((word, tf))
        
        # 排序并返回top_k
        keywords.sort(key=lambda x: x[1], reverse=True)
        return keywords[:top_k]
    
    def compress(self, text: str, target_ratio: float = 0.3) -> Dict:
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
                "key_sentences": [],
                "keywords": [],
                "compression_ratio": 1.0,
            }
        
        # 提取关键词
        keywords = self._extract_keywords(text)
        keyword_set = set(k[0] for k in keywords)
        
        # 分割句子
        sentences = re.split(r'(?<=[.!?。！？])\s+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) <= 2:
            return {
                "text": text,
                "key_sentences": sentences,
                "keywords": keywords,
                "compression_ratio": 1.0,
            }
        
        # 计算句子得分（基于关键词覆盖）
        sentence_scores = []
        for sentence in sentences:
            words = re.findall(r'[a-zA-Z]+|[\u4e00-\u9fff]', sentence.lower())
            keyword_count = sum(1 for w in words if w in keyword_set)
            score = keyword_count / max(len(words), 1)
            sentence_scores.append((sentence, score))
        
        # 选择高分句子
        target_count = max(1, int(len(sentences) * target_ratio))
        sentence_scores.sort(key=lambda x: x[1], reverse=True)
        
        # 按原文顺序排列选中的句子
        selected_sentences = [s[0] for s in sentence_scores[:target_count]]
        selected_indices = [sentences.index(s) for s in selected_sentences]
        selected_indices.sort()
        
        key_sentences = [sentences[i] for i in selected_indices]
        compressed_text = ' '.join(key_sentences)
        
        compression_ratio = len(compressed_text) / len(text) if text else 1.0
        
        return {
            "text": compressed_text,
            "key_sentences": key_sentences,
            "keywords": keywords,
            "compression_ratio": compression_ratio,
        }
