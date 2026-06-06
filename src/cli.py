"""
命令行接口模块
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Optional, List

import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.text import Text

from core.tokenizer import TokenCounter, get_token_counter
from core.analyzer import ContentAnalyzer
from compressors.hybrid import HybridCompressor, CompressionConfig, CompressionStrategy


console = Console()


@click.group()
@click.version_option(version="1.0.0", prog_name="stc")
def main():
    """🚀 SmartTokenCompressor - 高性能智能Token压缩引擎"""
    pass


@main.command()
@click.argument('input_text', required=False)
@click.option('--file', '-f', type=click.Path(exists=True), help='输入文件路径')
@click.option('--strategy', '-s', 
              type=click.Choice(['semantic', 'summarization', 'keyword', 'hybrid', 'adaptive']),
              default='hybrid', help='压缩策略')
@click.option('--ratio', '-r', type=float, default=0.5, help='目标压缩比 (0.1-0.9)')
@click.option('--model', '-m', 
              type=click.Choice(['gpt-4', 'gpt-3.5', 'claude', 'llama', 'gemini', 'general']),
              default='general', help='模型类型')
@click.option('--output', '-o', type=click.Path(), help='输出文件路径')
@click.option('--json', 'json_output', is_flag=True, help='JSON格式输出')
def compress(input_text: Optional[str], file: Optional[str], strategy: str, 
             ratio: float, model: str, output: Optional[str], json_output: bool):
    """
    压缩文本
    
    示例:
        stc compress "这是一段很长的文本..."
        stc compress -f input.txt -s hybrid -r 0.5
        stc compress -f input.txt -o output.txt
    """
    # 获取输入文本
    if file:
        with open(file, 'r', encoding='utf-8') as f:
            text = f.read()
    elif input_text:
        text = input_text
    else:
        # 从标准输入读取
        if not sys.stdin.isatty():
            text = sys.stdin.read()
        else:
            click.echo("错误: 请提供输入文本或使用 -f 指定文件")
            sys.exit(1)
    
    if not text.strip():
        click.echo("错误: 输入文本为空")
        sys.exit(1)
    
    # 解析策略
    strategy_map = {
        'semantic': CompressionStrategy.SEMANTIC,
        'summarization': CompressionStrategy.SUMMARIZATION,
        'keyword': CompressionStrategy.KEYWORD,
        'hybrid': CompressionStrategy.HYBRID,
        'adaptive': CompressionStrategy.ADAPTIVE,
    }
    compress_strategy = strategy_map[strategy]
    
    # 创建压缩器
    config = CompressionConfig(
        strategy=compress_strategy,
        target_ratio=ratio,
    )
    compressor = HybridCompressor(config)
    
    # 显示进度
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("正在压缩...", total=None)
        
        # 执行压缩
        start_time = time.time()
        result = compressor.compress(text, compress_strategy, ratio)
        processing_time = time.time() - start_time
        
        progress.update(task, completed=True)
    
    # 计算token
    tokenizer = get_token_counter(model)
    original_tokens = tokenizer.count_tokens(text)
    compressed_tokens = tokenizer.count_tokens(result["text"])
    tokens_saved = original_tokens - compressed_tokens
    savings_percentage = (tokens_saved / original_tokens * 100) if original_tokens > 0 else 0
    
    # 输出结果
    if json_output:
        output_data = {
            "success": True,
            "original_text": text[:1000] + "..." if len(text) > 1000 else text,
            "compressed_text": result["text"][:1000] + "..." if len(result["text"]) > 1000 else result["text"],
            "original_tokens": original_tokens,
            "compressed_tokens": compressed_tokens,
            "tokens_saved": tokens_saved,
            "savings_percentage": round(savings_percentage, 2),
            "compression_ratio": round(result["compression_ratio"], 4),
            "strategy": result["strategy"],
            "processing_time": round(processing_time, 4),
            "stages": result.get("stages", []),
        }
        
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            click.echo(f"结果已保存到: {output}")
        else:
            click.echo(json.dumps(output_data, ensure_ascii=False, indent=2))
    else:
        # 富文本输出
        console.print(Panel(
            f"[bold green]✅ 压缩完成[/bold green]\n\n"
            f"[bold]策略:[/bold] {result['strategy']}\n"
            f"[bold]处理时间:[/bold] {processing_time:.4f}s\n"
            f"[bold]原始Token:[/bold] {original_tokens}\n"
            f"[bold]压缩后Token:[/bold] {compressed_tokens}\n"
            f"[bold]节省Token:[/bold] [green]{tokens_saved}[/green] ([green]{savings_percentage:.1f}%[/green])\n"
            f"[bold]压缩比:[/bold] {result['compression_ratio']:.4f}",
            title="SmartTokenCompressor",
            border_style="blue",
        ))
        
        # 显示阶段信息
        if result.get("stages"):
            table = Table(title="压缩阶段")
            table.add_column("阶段", style="cyan")
            table.add_column("信息", style="green")
            
            for stage in result["stages"]:
                stage_name = stage.get("stage", "unknown")
                info = json.dumps({k: v for k, v in stage.items() if k != "stage"}, ensure_ascii=False)
                table.add_row(stage_name, info)
            
            console.print(table)
        
        # 显示压缩结果
        console.print(Panel(
            result["text"][:2000] + ("..." if len(result["text"]) > 2000 else ""),
            title="压缩结果",
            border_style="green",
        ))
        
        # 保存到文件
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(result["text"])
            console.print(f"[green]结果已保存到: {output}[/green]")


@main.command()
@click.argument('input_text', required=False)
@click.option('--file', '-f', type=click.Path(exists=True), help='输入文件路径')
@click.option('--model', '-m', 
              type=click.Choice(['gpt-4', 'gpt-3.5', 'claude', 'llama', 'gemini', 'general']),
              default='general', help='模型类型')
@click.option('--json', 'json_output', is_flag=True, help='JSON格式输出')
def count(input_text: Optional[str], file: Optional[str], model: str, json_output: bool):
    """
    计算Token数量
    
    示例:
        stc count "这是一段文本"
        stc count -f input.txt -m gpt-4
    """
    # 获取输入文本
    if file:
        with open(file, 'r', encoding='utf-8') as f:
            text = f.read()
    elif input_text:
        text = input_text
    else:
        if not sys.stdin.isatty():
            text = sys.stdin.read()
        else:
            click.echo("错误: 请提供输入文本或使用 -f 指定文件")
            sys.exit(1)
    
    # 计算token
    counter = get_token_counter(model)
    stats = counter.get_stats(text)
    
    if json_output:
        click.echo(json.dumps(stats, ensure_ascii=False, indent=2))
    else:
        table = Table(title="Token统计")
        table.add_column("指标", style="cyan")
        table.add_column("数值", style="green")
        
        table.add_row("Token数量", str(stats["tokens"]))
        table.add_row("字符数量", str(stats["characters"]))
        table.add_row("单词数量", str(stats["words"]))
        table.add_row("Token/字符比", str(stats["tokens_per_char"]))
        table.add_row("模型", stats["model"])
        
        console.print(table)


@main.command()
@click.argument('input_text', required=False)
@click.option('--file', '-f', type=click.Path(exists=True), help='输入文件路径')
@click.option('--json', 'json_output', is_flag=True, help='JSON格式输出')
def analyze(input_text: Optional[str], file: Optional[str], json_output: bool):
    """
    分析文本结构
    
    示例:
        stc analyze "这是一段文本"
        stc analyze -f input.txt
    """
    # 获取输入文本
    if file:
        with open(file, 'r', encoding='utf-8') as f:
            text = f.read()
    elif input_text:
        text = input_text
    else:
        if not sys.stdin.isatty():
            text = sys.stdin.read()
        else:
            click.echo("错误: 请提供输入文本或使用 -f 指定文件")
            sys.exit(1)
    
    # 分析文本
    analyzer = ContentAnalyzer()
    result = analyzer.analyze_structure(text)
    
    if json_output:
        click.echo(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        table = Table(title="文本结构分析")
        table.add_column("属性", style="cyan")
        table.add_column("值", style="green")
        
        table.add_row("内容类型", result["content_type"])
        table.add_row("总长度", str(result["total_length"]))
        table.add_row("片段数量", str(result["total_segments"]))
        table.add_row("句子数量", str(result["total_sentences"]))
        table.add_row("段落数量", str(result["total_paragraphs"]))
        table.add_row("包含代码", "是" if result["has_code"] else "否")
        table.add_row("包含Markdown", "是" if result["has_markdown"] else "否")
        table.add_row("包含JSON", "是" if result["has_json"] else "否")
        
        console.print(table)
        
        # 显示片段信息
        if result.get("segments"):
            seg_table = Table(title="片段详情")
            seg_table.add_column("类型", style="cyan")
            seg_table.add_column("长度", style="green")
            seg_table.add_column("重要性", style="yellow")
            
            for seg in result["segments"][:10]:  # 最多显示10个
                seg_table.add_row(
                    seg["type"],
                    str(seg["length"]),
                    str(seg.get("importance", "N/A")),
                )
            
            console.print(seg_table)


@main.command()
@click.option('--host', default='0.0.0.0', help='主机地址')
@click.option('--port', '-p', default=8000, help='端口号')
@click.option('--reload', is_flag=True, help='启用热重载')
def serve(host: str, port: int, reload: bool):
    """
    启动API服务
    
    示例:
        stc serve
        stc serve -p 8080
        stc serve --host 127.0.0.1
    """
    import uvicorn
    
    console.print(Panel(
        f"[bold green]🚀 启动 SmartTokenCompressor API 服务[/bold green]\n\n"
        f"[bold]地址:[/bold] http://{host}:{port}\n"
        f"[bold]文档:[/bold] http://{host}:{port}/docs\n"
        f"[bold]热重载:[/bold] {'启用' if reload else '禁用'}",
        title="API服务",
        border_style="blue",
    ))
    
    uvicorn.run(
        "api.server:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info",
    )


@main.command()
def demo():
    """
    运行演示
    
    展示各种压缩策略的效果
    """
    # 演示文本
    demo_text = """
    SmartTokenCompressor 是一个高性能的智能Token压缩引擎，专为LLM应用设计。
    
    它可以帮助你节省60-95%的API成本，同时保持语义完整性。
    
    主要特性包括：
    - 多策略压缩：支持语义去重、智能摘要、关键词提取等多种压缩策略
    - 实时流式处理：支持SSE流式压缩，无需等待完整输入
    - 智能上下文感知：保留关键信息，确保压缩后语义完整
    - Token精确计数：支持GPT-4/Claude/Llama等主流模型
    - Web UI + API：提供可视化界面和REST API
    - 多格式支持：文本、Markdown、JSON、代码块
    
    使用场景：
    1. 长文档压缩：将长篇文档压缩为适合LLM处理的短文本
    2. 日志分析：压缩大量日志，保留关键信息
    3. 代码审查：压缩代码，保留核心逻辑
    4. 对话历史：压缩对话历史，保留上下文
    
    技术栈：
    - 后端：Python 3.10+, FastAPI, transformers, torch
    - 前端：HTML5, Vanilla JS, Tailwind CSS
    - 算法：BERT语义相似度、TextRank摘要、TF-IDF关键词
    - 部署：Docker, Gunicorn, Uvicorn
    """
    
    console.print(Panel(
        "[bold blue]🚀 SmartTokenCompressor 演示[/bold blue]",
        title="演示",
        border_style="blue",
    ))
    
    console.print(f"\n[bold]原始文本:[/bold]\n{demo_text[:500]}...")
    console.print(f"\n[bold]原始长度:[/bold] {len(demo_text)} 字符")
    
    # 计算原始token
    tokenizer = TokenCounter()
    original_tokens = tokenizer.count_tokens(demo_text)
    console.print(f"[bold]原始Token:[/bold] {original_tokens}")
    
    # 测试各种策略
    strategies = [
        ("语义去重", CompressionStrategy.SEMANTIC),
        ("智能摘要", CompressionStrategy.SUMMARIZATION),
        ("关键词提取", CompressionStrategy.KEYWORD),
        ("混合策略", CompressionStrategy.HYBRID),
        ("自适应", CompressionStrategy.ADAPTIVE),
    ]
    
    table = Table(title="压缩效果对比")
    table.add_column("策略", style="cyan")
    table.add_column("压缩后Token", style="green")
    table.add_column("节省Token", style="yellow")
    table.add_column("节省比例", style="red")
    table.add_column("压缩比", style="blue")
    
    for name, strategy in strategies:
        compressor = HybridCompressor()
        result = compressor.compress(demo_text, strategy, 0.5)
        
        compressed_tokens = tokenizer.count_tokens(result["text"])
        tokens_saved = original_tokens - compressed_tokens
        savings_percentage = (tokens_saved / original_tokens * 100) if original_tokens > 0 else 0
        
        table.add_row(
            name,
            str(compressed_tokens),
            str(tokens_saved),
            f"{savings_percentage:.1f}%",
            f"{result['compression_ratio']:.4f}",
        )
    
    console.print(table)
    
    # 显示混合策略的详细结果
    console.print("\n[bold green]混合策略压缩结果:[/bold green]")
    compressor = HybridCompressor()
    result = compressor.compress(demo_text, CompressionStrategy.HYBRID, 0.5)
    console.print(Panel(
        result["text"][:1000] + ("..." if len(result["text"]) > 1000 else ""),
        title="压缩结果",
        border_style="green",
    ))


if __name__ == '__main__':
    main()
