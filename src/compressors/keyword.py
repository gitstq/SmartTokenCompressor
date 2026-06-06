"""
关键词提取压缩模块 - 基于TF-IDF和关键词密度
"""

import re
import math
from typing import List, Dict, Tuple, Set
from collections import defaultdict, Counter
import numpy as np


class KeywordCompressor:
    """关键词压缩器"""
    
    def __init__(self, top_k: int = 20, min_keyword_length: int = 2):
        """
        初始化关键词压缩器
        
        Args:
            top_k: 保留的关键词数量
            min_keyword_length: 最小关键词长度
        """
        self.top_k = top_k
        self.min_keyword_length = min_keyword_length
        self._idf_cache = {}
        self._stopwords = self._load_stopwords()
    
    def _load_stopwords(self) -> Set[str]:
        """加载停用词"""
        return {
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
            'until', 'while', 'this', 'that', 'these', 'those',
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人',
            '都', '一', '一个', '上', '也', '很', '到', '说', '要',
            '去', '你', '会', '着', '没有', '看', '好', '自己', '这',
        }
    
    def _tokenize(self, text: str) -> List[str]:
        """
        分词
        
        Args:
            text: 输入文本
            
        Returns:
            词列表
        """
        # 英文单词和中文汉字
        words = re.findall(r'[a-zA-Z]+|[\u4e00-\u9fff]', text.lower())
        return [w for w in words if len(w) >= self.min_keyword_length and w not in self._stopwords]
    
    def _calculate_tf(self, words: List[str]) -> Dict[str, float]:
        """
        计算词频(TF)
        
        Args:
            words: 词列表
            
        Returns:
            词频字典
        """
        word_count = Counter(words)
        total = len(words)
        return {word: count / total for word, count in word_count.items()}
    
    def _calculate_idf(self, documents: List[List[str]]) -> Dict[str, float]:
        """
        计算逆文档频率(IDF)
        
        Args:
            documents: 文档列表（每个文档是一个词列表）
            
        Returns:
            IDF字典
        """
        idf = {}
        total_docs = len(documents)
        
        # 统计包含每个词的文档数
        word_docs = defaultdict(int)
        for doc in documents:
            unique_words = set(doc)
            for word in unique_words:
                word_docs[word] += 1
        
        # 计算IDF
        for word, doc_count in word_docs.items():
            idf[word] = math.log(total_docs / (doc_count + 1)) + 1
        
        return idf
    
    def _calculate_tfidf(self, tf: Dict[str, float], idf: Dict[str, float]) -> Dict[str, float]:
        """
        计算TF-IDF
        
        Args:
            tf: 词频
            idf: 逆文档频率
            
        Returns:
            TF-IDF字典
        """
        return {word: tf[word] * idf.get(word, 0) for word in tf}
    
    def extract_keywords(self, text: str, context: List[str] = None) -> List[Tuple[str, float]]:
        """
        提取关键词
        
        Args:
            text: 输入文本
            context: 上下文文档列表
            
        Returns:
            关键词列表
        """
        words = self._tokenize(text)
        
        if not words:
            return []
        
        # 计算TF
        tf = self._calculate_tf(words)
        
        # 如果有上下文，计算IDF
        if context:
            context_words = [self._tokenize(doc) for doc in context]
            idf = self._calculate_idf(context_words + [words])
        else:
            # 使用简单的IDF（基于当前文本）
            idf = {word: 1.0 for word in tf}
        
        # 计算TF-IDF
        tfidf = self._calculate_tfidf(tf, idf)
        
        # 排序并返回top_k
        keywords = sorted(tfidf.items(), key=lambda x: x[1], reverse=True)
        return keywords[:self.top_k]
    
    def compress(self, text: str, target_ratio: float = 0.4, context: List[str] = None) -> Dict:
        """
        压缩文本（保留关键词密集的句子）
        
        Args:
            text: 输入文本
            target_ratio: 目标压缩比
            context: 上下文文档
            
        Returns:
            压缩结果
        """
        if not text or len(text) < 100:
            return {
                "text": text,
                "keywords": [],
                "key_sentences": [],
                "compression_ratio": 1.0,
            }
        
        # 提取关键词
        keywords = self.extract_keywords(text, context)
        keyword_dict = {k: v for k, v in keywords}
        
        # 分割句子
        sentences = re.split(r'(?<=[.!?。！？])\s+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) <= 2:
            return {
                "text": text,
                "keywords": keywords,
                "key_sentences": sentences,
                "compression_ratio": 1.0,
            }
        
        # 计算每个句子的关键词密度
        sentence_scores = []
        for sentence in sentences:
            words = self._tokenize(sentence)
            if not words:
                sentence_scores.append((sentence, 0.0))
                continue
            
            # 计算关键词覆盖度
            keyword_score = sum(keyword_dict.get(word, 0) for word in words)
            density = keyword_score / len(words)
            
            # 考虑句子长度（避免过短）
            length_bonus = min(len(sentence) / 100, 0.2)
            
            score = density + length_bonus
            sentence_scores.append((sentence, score))
        
        # 选择高分句子
        target_count = max(1, int(len(sentences) * target_ratio))
        sentence_scores.sort(key=lambda x: x[1], reverse=True)
        
        # 按原文顺序排列
        selected = [s[0] for s in sentence_scores[:target_count]]
        selected_indices = sorted([sentences.index(s) for s in selected])
        key_sentences = [sentences[i] for i in selected_indices]
        
        compressed_text = ' '.join(key_sentences)
        compression_ratio = len(compressed_text) / len(text) if text else 1.0
        
        return {
            "text": compressed_text,
            "keywords": keywords,
            "key_sentences": key_sentences,
            "compression_ratio": compression_ratio,
        }
    
    def compress_batch(self, texts: List[str], target_ratio: float = 0.4) -> List[Dict]:
        """
        批量压缩
        
        Args:
            texts: 文本列表
            target_ratio: 目标压缩比
            
        Returns:
            压缩结果列表
        """
        # 使用所有文本作为上下文
        results = []
        for i, text in enumerate(texts):
            context = texts[:i] + texts[i+1:]
            results.append(self.compress(text, target_ratio, context))
        return results


class KeywordDensityCompressor:
    """基于关键词密度的压缩器"""
    
    def __init__(self, density_threshold: float = 0.3):
        """
        初始化
        
        Args:
            density_threshold: 密度阈值
        """
        self.density_threshold = density_threshold
        self._stopwords = {
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
            'until', 'while', 'this', 'that', 'these', 'those',
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人',
            '都', '一', '一个', '上', '也', '很', '到', '说', '要',
            '去', '你', '会', '着', '没有', '看', '好', '自己', '这',
        }
    
    def compress(self, text: str, target_ratio: float = 0.5) -> Dict:
        """
        压缩文本（去除低密度段落）
        
        Args:
            text: 输入文本
            target_ratio: 目标压缩比
            
        Returns:
            压缩结果
        """
        if not text or len(text) < 100:
            return {
                "text": text,
                "paragraphs": [],
                "compression_ratio": 1.0,
            }
        
        # 分割段落
        paragraphs = re.split(r'\n\s*\n', text)
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        if len(paragraphs) <= 1:
            return {
                "text": text,
                "paragraphs": paragraphs,
                "compression_ratio": 1.0,
            }
        
        # 提取全局关键词
        all_words = re.findall(r'[a-zA-Z]+|[\u4e00-\u9fff]', text.lower())
        all_words = [w for w in all_words if w not in self._stopwords and len(w) > 1]
        word_freq = Counter(all_words)
        top_words = set(word for word, _ in word_freq.most_common(20))
        
        # 计算每个段落的关键词密度
        paragraph_scores = []
        for para in paragraphs:
            words = re.findall(r'[a-zA-Z]+|[\u4e00-\u9fff]', para.lower())
            words = [w for w in words if w not in self._stopwords]
            
            if not words:
                paragraph_scores.append((para, 0.0))
                continue
            
            keyword_count = sum(1 for w in words if w in top_words)
            density = keyword_count / len(words)
            paragraph_scores.append((para, density))
        
        # 选择高密度段落
        target_count = max(1, int(len(paragraphs) * target_ratio))
        paragraph_scores.sort(key=lambda x: x[1], reverse=True)
        
        # 按原文顺序排列
        selected = [p[0] for p in paragraph_scores[:target_count]]
        selected_indices = sorted([paragraphs.index(p) for p in selected])
        kept_paragraphs = [paragraphs[i] for i in selected_indices]
        
        compressed_text = '\n\n'.join(kept_paragraphs)
        compression_ratio = len(compressed_text) / len(text) if text else 1.0
        
        return {
            "text": compressed_text,
            "paragraphs": kept_paragraphs,
            "compression_ratio": compression_ratio,
            "paragraph_scores": [(p, float(s)) for p, s in paragraph_scores],
        }
