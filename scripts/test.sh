#!/bin/bash

# SmartTokenCompressor 测试脚本

set -e

echo "🧪 开始运行测试..."

# 检查是否在虚拟环境中
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  未检测到虚拟环境，尝试激活..."
    if [ -d "venv" ]; then
        source venv/bin/activate
    else
        echo "❌ 虚拟环境不存在，请先运行 build.sh"
        exit 1
    fi
fi

# 运行单元测试
echo "📋 运行单元测试..."
pytest tests/ -v --tb=short --cov=src --cov-report=html --cov-report=term

# 运行类型检查
echo "🔍 运行类型检查..."
if command -v mypy &> /dev/null; then
    mypy src/ --ignore-missing-imports
else
    echo "⚠️  mypy 未安装，跳过类型检查"
fi

# 运行代码风格检查
echo "🎨 运行代码风格检查..."
if command -v flake8 &> /dev/null; then
    flake8 src/ --max-line-length=120 --extend-ignore=E203,W503
else
    echo "⚠️  flake8 未安装，跳过风格检查"
fi

echo "✅ 测试完成!"
