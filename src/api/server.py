"""
FastAPI服务模块 - 提供REST API接口
"""

import os
import sys
import asyncio
from typing import Optional, List, Dict
from dataclasses import dataclass
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File, Form
from fastapi.responses import StreamingResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.tokenizer import TokenCounter, ModelType
from core.analyzer import ContentAnalyzer
from core.pipeline import ProcessingPipeline, PipelineResult
from compressors.hybrid import HybridCompressor, CompressionConfig, CompressionStrategy


# ============== 数据模型 ==============

class CompressRequest(BaseModel):
    """压缩请求"""
    text: str = Field(..., min_length=1, max_length=1000000, description="要压缩的文本")
    strategy: str = Field(default="hybrid", description="压缩策略: semantic, summarization, keyword, hybrid, adaptive")
    target_ratio: float = Field(default=0.5, ge=0.1, le=0.9, description="目标压缩比")
    model: str = Field(default="general", description="模型类型: gpt-4, gpt-3.5, claude, llama, gemini, general")
    preserve_structure: bool = Field(default=True, description="是否保留结构")


class CompressResponse(BaseModel):
    """压缩响应"""
    success: bool
    original_text: str
    compressed_text: str
    original_tokens: int
    compressed_tokens: int
    tokens_saved: int
    savings_percentage: float
    compression_ratio: float
    strategy: str
    processing_time: float
    stages: List[Dict]


class BatchCompressRequest(BaseModel):
    """批量压缩请求"""
    texts: List[str] = Field(..., min_items=1, max_items=100)
    strategy: str = Field(default="hybrid")
    target_ratio: float = Field(default=0.5, ge=0.1, le=0.9)
    model: str = Field(default="general")


class BatchCompressResponse(BaseModel):
    """批量压缩响应"""
    success: bool
    results: List[CompressResponse]
    total_original_tokens: int
    total_compressed_tokens: int
    total_tokens_saved: int
    avg_savings_percentage: float


class TokenCountRequest(BaseModel):
    """Token计数请求"""
    text: str = Field(..., min_length=1)
    model: str = Field(default="general")


class TokenCountResponse(BaseModel):
    """Token计数响应"""
    tokens: int
    characters: int
    words: int
    tokens_per_char: float
    model: str


class AnalyzeRequest(BaseModel):
    """分析请求"""
    text: str = Field(..., min_length=1)


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str
    version: str
    uptime: float


# ============== 全局状态 ==============

@dataclass
class AppState:
    """应用状态"""
    start_time: float
    compressor: HybridCompressor
    tokenizer: TokenCounter
    analyzer: ContentAnalyzer
    request_count: int = 0
    total_tokens_processed: int = 0


# ============== 生命周期管理 ==============

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    import time
    
    # 启动时初始化
    app.state.app_state = AppState(
        start_time=time.time(),
        compressor=HybridCompressor(),
        tokenizer=TokenCounter(),
        analyzer=ContentAnalyzer(),
    )
    
    print("🚀 SmartTokenCompressor API 已启动")
    
    yield
    
    # 关闭时清理
    print("👋 SmartTokenCompressor API 已关闭")


# ============== 创建应用 ==============

app = FastAPI(
    title="SmartTokenCompressor API",
    description="🚀 高性能智能Token压缩引擎 - 为LLM应用节省60-95% API成本",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件
static_dir = os.path.join(os.path.dirname(__file__), '..', 'web', 'static')
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


# ============== API路由 ==============

@app.get("/", response_class=HTMLResponse)
async def root():
    """根路径 - 返回Web UI"""
    html_path = os.path.join(os.path.dirname(__file__), '..', 'web', 'templates', 'index.html')
    if os.path.exists(html_path):
        with open(html_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    # 如果没有HTML文件，返回API信息
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head>
        <title>SmartTokenCompressor</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            h1 { color: #333; }
            .endpoint { background: #f5f5f5; padding: 10px; margin: 10px 0; border-radius: 5px; }
            code { background: #e0e0e0; padding: 2px 5px; border-radius: 3px; }
        </style>
    </head>
    <body>
        <h1>🚀 SmartTokenCompressor API</h1>
        <p>高性能智能Token压缩引擎</p>
        <h2>API端点</h2>
        <div class="endpoint">
            <code>POST /api/v1/compress</code> - 压缩文本
        </div>
        <div class="endpoint">
            <code>POST /api/v1/compress/batch</code> - 批量压缩
        </div>
        <div class="endpoint">
            <code>POST /api/v1/tokens/count</code> - 计算Token数量
        </div>
        <div class="endpoint">
            <code>POST /api/v1/analyze</code> - 分析文本结构
        </div>
        <div class="endpoint">
            <code>GET /health</code> - 健康检查
        </div>
        <p>查看API文档: <a href="/docs">/docs</a></p>
    </body>
    </html>
    """)


@app.post("/api/v1/compress", response_model=CompressResponse)
async def compress(request: CompressRequest):
    """
    压缩文本
    
    - **text**: 要压缩的文本
    - **strategy**: 压缩策略 (semantic, summarization, keyword, hybrid, adaptive)
    - **target_ratio**: 目标压缩比 (0.1-0.9)
    - **model**: 模型类型
    - **preserve_structure**: 是否保留结构
    """
    try:
        state = app.state.app_state
        state.request_count += 1
        
        # 解析策略
        strategy_map = {
            "semantic": CompressionStrategy.SEMANTIC,
            "summarization": CompressionStrategy.SUMMARIZATION,
            "keyword": CompressionStrategy.KEYWORD,
            "hybrid": CompressionStrategy.HYBRID,
            "adaptive": CompressionStrategy.ADAPTIVE,
        }
        strategy = strategy_map.get(request.strategy.lower(), CompressionStrategy.HYBRID)
        
        # 创建配置
        config = CompressionConfig(
            strategy=strategy,
            target_ratio=request.target_ratio,
        )
        
        # 创建压缩器
        compressor = HybridCompressor(config)
        
        # 执行压缩
        import time
        start_time = time.time()
        result = compressor.compress(request.text, strategy, request.target_ratio)
        processing_time = time.time() - start_time
        
        # 计算token
        tokenizer = TokenCounter()
        original_tokens = tokenizer.count_tokens(request.text)
        compressed_tokens = tokenizer.count_tokens(result["text"])
        tokens_saved = original_tokens - compressed_tokens
        savings_percentage = (tokens_saved / original_tokens * 100) if original_tokens > 0 else 0
        
        # 更新统计
        state.total_tokens_processed += original_tokens
        
        return CompressResponse(
            success=True,
            original_text=request.text[:500] + "..." if len(request.text) > 500 else request.text,
            compressed_text=result["text"][:500] + "..." if len(result["text"]) > 500 else result["text"],
            original_tokens=original_tokens,
            compressed_tokens=compressed_tokens,
            tokens_saved=tokens_saved,
            savings_percentage=round(savings_percentage, 2),
            compression_ratio=round(result["compression_ratio"], 4),
            strategy=result["strategy"],
            processing_time=round(processing_time, 4),
            stages=result.get("stages", []),
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"压缩失败: {str(e)}")


@app.post("/api/v1/compress/batch", response_model=BatchCompressResponse)
async def compress_batch(request: BatchCompressRequest):
    """
    批量压缩文本
    
    - **texts**: 要压缩的文本列表
    - **strategy**: 压缩策略
    - **target_ratio**: 目标压缩比
    - **model**: 模型类型
    """
    try:
        state = app.state.app_state
        
        # 解析策略
        strategy_map = {
            "semantic": CompressionStrategy.SEMANTIC,
            "summarization": CompressionStrategy.SUMMARIZATION,
            "keyword": CompressionStrategy.KEYWORD,
            "hybrid": CompressionStrategy.HYBRID,
            "adaptive": CompressionStrategy.ADAPTIVE,
        }
        strategy = strategy_map.get(request.strategy.lower(), CompressionStrategy.HYBRID)
        
        # 批量压缩
        compressor = HybridCompressor()
        results = compressor.compress_batch(request.texts, strategy, request.target_ratio)
        
        # 构建响应
        compress_responses = []
        total_original = 0
        total_compressed = 0
        
        tokenizer = TokenCounter()
        
        for i, result in enumerate(results):
            original_tokens = tokenizer.count_tokens(request.texts[i])
            compressed_tokens = tokenizer.count_tokens(result["text"])
            tokens_saved = original_tokens - compressed_tokens
            savings_percentage = (tokens_saved / original_tokens * 100) if original_tokens > 0 else 0
            
            total_original += original_tokens
            total_compressed += compressed_tokens
            
            compress_responses.append(CompressResponse(
                success=True,
                original_text=request.texts[i][:200] + "..." if len(request.texts[i]) > 200 else request.texts[i],
                compressed_text=result["text"][:200] + "..." if len(result["text"]) > 200 else result["text"],
                original_tokens=original_tokens,
                compressed_tokens=compressed_tokens,
                tokens_saved=tokens_saved,
                savings_percentage=round(savings_percentage, 2),
                compression_ratio=round(result["compression_ratio"], 4),
                strategy=result["strategy"],
                processing_time=0.0,
                stages=result.get("stages", []),
            ))
        
        total_saved = total_original - total_compressed
        avg_savings = (total_saved / total_original * 100) if total_original > 0 else 0
        
        return BatchCompressResponse(
            success=True,
            results=compress_responses,
            total_original_tokens=total_original,
            total_compressed_tokens=total_compressed,
            total_tokens_saved=total_saved,
            avg_savings_percentage=round(avg_savings, 2),
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量压缩失败: {str(e)}")


@app.post("/api/v1/tokens/count", response_model=TokenCountResponse)
async def count_tokens(request: TokenCountRequest):
    """
    计算Token数量
    
    - **text**: 要计算的文本
    - **model**: 模型类型
    """
    try:
        from core.tokenizer import get_token_counter
        
        counter = get_token_counter(request.model)
        stats = counter.get_stats(request.text)
        
        return TokenCountResponse(
            tokens=stats["tokens"],
            characters=stats["characters"],
            words=stats["words"],
            tokens_per_char=stats["tokens_per_char"],
            model=stats["model"],
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"计算失败: {str(e)}")


@app.post("/api/v1/analyze")
async def analyze(request: AnalyzeRequest):
    """
    分析文本结构
    
    - **text**: 要分析的文本
    """
    try:
        state = app.state.app_state
        result = state.analyzer.analyze_structure(request.text)
        
        return {
            "success": True,
            "analysis": result,
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")


@app.get("/health", response_model=HealthResponse)
async def health():
    """健康检查"""
    import time
    
    state = app.state.app_state
    uptime = time.time() - state.start_time
    
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        uptime=round(uptime, 2),
    )


@app.get("/api/v1/stats")
async def stats():
    """获取服务统计信息"""
    import time
    
    state = app.state.app_state
    uptime = time.time() - state.start_time
    
    return {
        "success": True,
        "uptime_seconds": round(uptime, 2),
        "request_count": state.request_count,
        "total_tokens_processed": state.total_tokens_processed,
        "version": "1.0.0",
    }


# ============== 流式压缩 ==============

@app.post("/api/v1/compress/stream")
async def compress_stream(request: CompressRequest):
    """
    流式压缩（SSE）
    
    - **text**: 要压缩的文本
    - **strategy**: 压缩策略
    - **target_ratio**: 目标压缩比
    """
    async def event_generator():
        try:
            # 解析策略
            strategy_map = {
                "semantic": CompressionStrategy.SEMANTIC,
                "summarization": CompressionStrategy.SUMMARIZATION,
                "keyword": CompressionStrategy.KEYWORD,
                "hybrid": CompressionStrategy.HYBRID,
                "adaptive": CompressionStrategy.ADAPTIVE,
            }
            strategy = strategy_map.get(request.strategy.lower(), CompressionStrategy.HYBRID)
            
            # 发送开始事件
            yield f"data: {json.dumps({'event': 'start', 'message': '开始压缩'})}\n\n"
            
            # 分块处理
            chunk_size = 2000
            text = request.text
            chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
            
            compressor = HybridCompressor()
            
            for i, chunk in enumerate(chunks):
                result = compressor.compress(chunk, strategy, request.target_ratio)
                
                yield f"data: {json.dumps({
                    'event': 'progress',
                    'chunk': i + 1,
                    'total': len(chunks),
                    'compressed_text': result['text'],
                    'compression_ratio': result['compression_ratio'],
                })}\n\n"
            
            # 发送完成事件
            yield f"data: {json.dumps({'event': 'complete', 'message': '压缩完成'})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'event': 'error', 'message': str(e)})}\n\n"
    
    import json
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
    )


# ============== 主函数 ==============

def main():
    """主函数"""
    import uvicorn
    
    uvicorn.run(
        "api.server:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info",
    )


if __name__ == "__main__":
    main()
