#!/bin/bash

# SmartTokenCompressor 构建脚本

set -e

echo "🚀 开始构建 SmartTokenCompressor..."

# 检查Python版本
echo "📋 检查Python版本..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python版本: $python_version"

# 创建虚拟环境
echo "🌟 创建虚拟环境..."
python3 -m venv venv
source venv/bin/activate

# 安装依赖
echo "📦 安装依赖..."
pip install --upgrade pip
pip install -r requirements.txt

# 安装项目
echo "🔧 安装项目..."
pip install -e .

# 运行测试
echo "🧪 运行测试..."
pytest tests/ -v --tb=short

# 构建Docker镜像
echo "🐳 构建Docker镜像..."
docker build -t smart-token-compressor:latest .

echo "✅ 构建完成!"
echo ""
echo "使用方法:"
echo "  本地运行: python -m uvicorn src.api.server:app --host 0.0.0.0 --port 8000"
echo "  Docker运行: docker run -p 8000:8000 smart-token-compressor:latest"
echo "  CLI使用: stc --help"
