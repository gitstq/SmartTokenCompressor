"""
内容分析器模块 - 分析文本结构和语义
"""

import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class ContentType(Enum):
    """内容类型"""
    TEXT = "text"
    CODE = "code"
    MARKDOWN = "markdown"
    JSON = "json"
    HTML = "html"
    LOG = "log"


@dataclass
class TextSegment:
    """文本片段"""
    content: str
    segment_type: ContentType
    importance: float = 1.0
    start_pos: int = 0
    end_pos: int = 0


class ContentAnalyzer:
    """内容分析器"""
    
    # 代码块标记
    CODE_PATTERNS = [
        (r'```[\s\S]*?```', ContentType.CODE),
        (r'`[^`]+`', ContentType.CODE),
        (r'<code>[\s\S]*?</code>', ContentType.CODE),
    ]
    
    # Markdown标记
    MD_PATTERNS = [
        (r'^#{1,6}\s+.+$', ContentType.MARKDOWN),
        (r'^\s*[-*+]\s+', ContentType.MARKDOWN),
        (r'^\s*\d+\.\s+', ContentType.MARKDOWN),
        (r'\[.+?\]\(.+?\)', ContentType.MARKDOWN),
        (r'\*\*.+?\*\*', ContentType.MARKDOWN),
        (r'__.+?__', ContentType.MARKDOWN),
    ]
    
    # JSON标记
    JSON_PATTERN = r'^\s*[\{\[]'
    
    # HTML标记
    HTML_PATTERN = r'<[^>]+>'
    
    # 日志标记
    LOG_PATTERNS = [
        r'\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}',
        r'\[\w+\]\s+\w+',
        r'(INFO|DEBUG|WARN|ERROR|FATAL)',
    ]
    
    def __init__(self):
        self._sentence_split_pattern = re.compile(r'(?<=[.!?。！？])\s+')
        self._paragraph_split_pattern = re.compile(r'\n\s*\n')
    
    def detect_content_type(self, text: str) -> ContentType:
        """
        检测内容类型
        
        Args:
            text: 输入文本
            
        Returns:
            内容类型
        """
        # 检查JSON
        if re.match(self.JSON_PATTERN, text.strip()):
            try:
                import json
                json.loads(text)
                return ContentType.JSON
            except:
                pass
        
        # 检查HTML
        if re.search(self.HTML_PATTERN, text):
            return ContentType.HTML
        
        # 检查日志
        log_matches = sum(1 for p in self.LOG_PATTERNS if re.search(p, text))
        if log_matches >= 2:
            return ContentType.LOG
        
        # 检查代码
        code_blocks = len(re.findall(r'```', text))
        if code_blocks >= 2:
            return ContentType.CODE
        
        # 检查Markdown
        md_matches = sum(1 for p, _ in self.MD_PATTERNS if re.search(p, text, re.MULTILINE))
        if md_matches >= 3:
            return ContentType.MARKDOWN
        
        return ContentType.TEXT
    
    def split_sentences(self, text: str) -> List[str]:
        """
        将文本分割为句子
        
        Args:
            text: 输入文本
            
        Returns:
            句子列表
        """
        # 保留中英文分隔符
        sentences = re.split(r'(?<=[.!?。！？])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def split_paragraphs(self, text: str) -> List[str]:
        """
        将文本分割为段落
        
        Args:
            text: 输入文本
            
        Returns:
            段落列表
        """
        paragraphs = self._paragraph_split_pattern.split(text)
        return [p.strip() for p in paragraphs if p.strip()]
    
    def extract_segments(self, text: str) -> List[TextSegment]:
        """
        提取文本片段（按类型分割）
        
        Args:
            text: 输入文本
            
        Returns:
            文本片段列表
        """
        segments = []
        current_pos = 0
        
        # 查找代码块
        for pattern, seg_type in self.CODE_PATTERNS:
            for match in re.finditer(pattern, text):
                # 添加代码块前的文本
                if match.start() > current_pos:
                    pre_text = text[current_pos:match.start()]
                    if pre_text.strip():
                        segments.append(TextSegment(
                            content=pre_text,
                            segment_type=ContentType.TEXT,
                            start_pos=current_pos,
                            end_pos=match.start()
                        ))
                
                # 添加代码块
                segments.append(TextSegment(
                    content=match.group(),
                    segment_type=seg_type,
                    importance=1.2,  # 代码块重要性更高
                    start_pos=match.start(),
                    end_pos=match.end()
                ))
                
                current_pos = match.end()
        
        # 添加剩余文本
        if current_pos < len(text):
            remaining = text[current_pos:]
            if remaining.strip():
                segments.append(TextSegment(
                    content=remaining,
                    segment_type=ContentType.TEXT,
                    start_pos=current_pos,
                    end_pos=len(text)
                ))
        
        # 如果没有找到任何片段，返回整个文本
        if not segments:
            segments.append(TextSegment(
                content=text,
                segment_type=self.detect_content_type(text),
                start_pos=0,
                end_pos=len(text)
            ))
        
        return segments
    
    def calculate_importance(self, text: str) -> float:
        """
        计算文本片段的重要性
        
        Args:
            text: 输入文本
            
        Returns:
            重要性分数 (0-1)
        """
        score = 0.5
        
        # 包含关键信息加分
        if re.search(r'(错误|异常|失败|error|exception|fail)', text, re.I):
            score += 0.2
        
        if re.search(r'(重要|关键|注意|important|critical|warning)', text, re.I):
            score += 0.15
        
        # 包含具体数据加分
        if re.search(r'\d+', text):
            score += 0.1
        
        # 长度过短减分
        if len(text) < 20:
            score -= 0.1
        
        # 包含URL或路径加分
        if re.search(r'(https?://|/\w+)', text):
            score += 0.1
        
        return max(0.0, min(1.0, score))
    
    def analyze_structure(self, text: str) -> Dict:
        """
        分析文本结构
        
        Args:
            text: 输入文本
            
        Returns:
            结构分析结果
        """
        content_type = self.detect_content_type(text)
        segments = self.extract_segments(text)
        sentences = self.split_sentences(text)
        paragraphs = self.split_paragraphs(text)
        
        return {
            "content_type": content_type.value,
            "total_length": len(text),
            "total_segments": len(segments),
            "total_sentences": len(sentences),
            "total_paragraphs": len(paragraphs),
            "segments": [
                {
                    "type": seg.segment_type.value,
                    "length": len(seg.content),
                    "importance": seg.importance,
                }
                for seg in segments
            ],
            "has_code": any(seg.segment_type == ContentType.CODE for seg in segments),
            "has_markdown": content_type == ContentType.MARKDOWN,
            "has_json": content_type == ContentType.JSON,
        }
