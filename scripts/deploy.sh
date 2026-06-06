#!/bin/bash

# SmartTokenCompressor 部署脚本

set -e

echo "🚀 开始部署 SmartTokenCompressor..."

# 检查Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装"
    exit 1
fi

# 构建镜像
echo "🐳 构建Docker镜像..."
docker build -t smart-token-compressor:latest .

# 停止旧容器
echo "🛑 停止旧容器..."
docker stop smart-token-compressor 2>/dev/null || true
docker rm smart-token-compressor 2>/dev/null || true

# 启动新容器
echo "▶️  启动新容器..."
docker run -d \
    --name smart-token-compressor \
    -p 8000:8000 \
    --restart unless-stopped \
    -e TZ=Asia/Shanghai \
    smart-token-compressor:latest

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 5

# 健康检查
echo "🏥 健康检查..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ 部署成功!"
    echo ""
    echo "服务地址: http://localhost:8000"
    echo "API文档: http://localhost:8000/docs"
else
    echo "❌ 部署失败，服务未响应"
    docker logs smart-token-compressor
    exit 1
fi
