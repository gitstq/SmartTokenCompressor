"""
处理流水线模块 - 管理压缩流程
"""

import asyncio
from typing import List, Dict, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
import time


class CompressionStage(Enum):
    """压缩阶段"""
    ANALYZE = "analyze"
    PREPROCESS = "preprocess"
    COMPRESS = "compress"
    POSTPROCESS = "postprocess"
    VALIDATE = "validate"


@dataclass
class PipelineResult:
    """流水线处理结果"""
    original_text: str
    compressed_text: str
    original_tokens: int
    compressed_tokens: int
    compression_ratio: float
    stage_results: Dict[str, Any] = field(default_factory=dict)
    processing_time: float = 0.0
    strategy_used: str = ""
    quality_score: float = 0.0
    
    @property
    def tokens_saved(self) -> int:
        """节省的token数量"""
        return self.original_tokens - self.compressed_tokens
    
    @property
    def savings_percentage(self) -> float:
        """节省百分比"""
        if self.original_tokens > 0:
            return (self.tokens_saved / self.original_tokens) * 100
        return 0.0


class ProcessingPipeline:
    """处理流水线"""
    
    def __init__(self, stages: Optional[List[CompressionStage]] = None):
        self.stages = stages or [
            CompressionStage.ANALYZE,
            CompressionStage.PREPROCESS,
            CompressionStage.COMPRESS,
            CompressionStage.POSTPROCESS,
            CompressionStage.VALIDATE,
        ]
        self._stage_handlers: Dict[CompressionStage, Callable] = {}
        self._middleware: List[Callable] = []
    
    def register_stage(self, stage: CompressionStage, handler: Callable):
        """
        注册阶段处理器
        
        Args:
            stage: 阶段
            handler: 处理函数
        """
        self._stage_handlers[stage] = handler
    
    def add_middleware(self, middleware: Callable):
        """
        添加中间件
        
        Args:
            middleware: 中间件函数
        """
        self._middleware.append(middleware)
    
    async def process(self, text: str, **kwargs) -> PipelineResult:
        """
        处理文本
        
        Args:
            text: 输入文本
            **kwargs: 额外参数
            
        Returns:
            处理结果
        """
        start_time = time.time()
        stage_results = {}
        current_text = text
        
        # 执行各阶段
        for stage in self.stages:
            if stage in self._stage_handlers:
                handler = self._stage_handlers[stage]
                
                # 执行中间件（前置）
                for middleware in self._middleware:
                    if asyncio.iscoroutinefunction(middleware):
                        await middleware(stage, current_text, "before")
                    else:
                        middleware(stage, current_text, "before")
                
                # 执行阶段处理
                if asyncio.iscoroutinefunction(handler):
                    result = await handler(current_text, **kwargs)
                else:
                    result = handler(current_text, **kwargs)
                
                stage_results[stage.value] = result
                
                # 更新当前文本
                if isinstance(result, dict) and "text" in result:
                    current_text = result["text"]
                elif isinstance(result, str):
                    current_text = result
                
                # 执行中间件（后置）
                for middleware in self._middleware:
                    if asyncio.iscoroutinefunction(middleware):
                        await middleware(stage, current_text, "after")
                    else:
                        middleware(stage, current_text, "after")
        
        processing_time = time.time() - start_time
        
        # 计算token数量
        from .tokenizer import TokenCounter
        counter = TokenCounter()
        original_tokens = counter.count_tokens(text)
        compressed_tokens = counter.count_tokens(current_text)
        
        # 计算压缩比
        compression_ratio = compressed_tokens / original_tokens if original_tokens > 0 else 1.0
        
        return PipelineResult(
            original_text=text,
            compressed_text=current_text,
            original_tokens=original_tokens,
            compressed_tokens=compressed_tokens,
            compression_ratio=compression_ratio,
            stage_results=stage_results,
            processing_time=processing_time,
            strategy_used=kwargs.get("strategy", "unknown"),
            quality_score=kwargs.get("quality_score", 0.8),
        )
    
    def process_sync(self, text: str, **kwargs) -> PipelineResult:
        """
        同步处理文本
        
        Args:
            text: 输入文本
            **kwargs: 额外参数
            
        Returns:
            处理结果
        """
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # 如果事件循环已在运行，创建新任务
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self.process(text, **kwargs))
                    return future.result()
            else:
                return loop.run_until_complete(self.process(text, **kwargs))
        except RuntimeError:
            # 没有事件循环，创建新的
            return asyncio.run(self.process(text, **kwargs))


class StreamingPipeline:
    """流式处理流水线"""
    
    def __init__(self, chunk_size: int = 1000, overlap: int = 100):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self._buffer = ""
        self._callbacks: List[Callable] = []
    
    def on_chunk(self, callback: Callable):
        """
        注册块处理回调
        
        Args:
            callback: 回调函数
        """
        self._callbacks.append(callback)
    
    async def feed(self, text: str, pipeline: ProcessingPipeline, **kwargs):
        """
        流式输入文本
        
        Args:
            text: 输入文本
            pipeline: 处理流水线
            **kwargs: 额外参数
        """
        self._buffer += text
        
        # 当缓冲区足够大时，处理一个块
        while len(self._buffer) >= self.chunk_size:
            chunk = self._buffer[:self.chunk_size]
            self._buffer = self._buffer[self.chunk_size - self.overlap:]
            
            # 处理块
            result = await pipeline.process(chunk, **kwargs)
            
            # 触发回调
            for callback in self._callbacks:
                if asyncio.iscoroutinefunction(callback):
                    await callback(result)
                else:
                    callback(result)
    
    async def flush(self, pipeline: ProcessingPipeline, **kwargs):
        """
        刷新剩余缓冲区
        
        Args:
            pipeline: 处理流水线
            **kwargs: 额外参数
        """
        if self._buffer:
            result = await pipeline.process(self._buffer, **kwargs)
            
            for callback in self._callbacks:
                if asyncio.iscoroutinefunction(callback):
                    await callback(result)
                else:
                    callback(result)
            
            self._buffer = ""
