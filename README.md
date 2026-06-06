# 🚀 SmartTokenCompressor

> 高性能智能Token压缩引擎 - 为LLM应用节省60-95% API成本

## 🌍 语言切换

- [简体中文](#-smarttokencompressor-zh)
- [繁體中文](#-smarttokencompressor-tw)
- [English](#-smarttokencompressor-en)

---

<a name="smarttokencompressor-zh"></a>
## 🚀 SmartTokenCompressor (简体中文)

### 🎉 项目介绍

SmartTokenCompressor 是一个高性能的智能Token压缩引擎，专为LLM（大语言模型）应用设计。它通过多种智能压缩策略，帮助开发者在保持语义完整性的同时，显著减少API调用成本。

**灵感来源**：本项目灵感来源于GitHub Trending项目 [headroom](https://github.com/chopratejas/headroom)，我们在其基础上进行了深度自研优化，增加了更多压缩策略、实时流式处理、Web UI等差异化功能。

**解决痛点**：
- LLM API调用成本高昂，长文本处理费用惊人
- 大量冗余信息浪费token配额
- 现有工具压缩效果不佳或速度太慢
- 缺乏可视化的压缩效果对比

**自研差异化亮点**：
- ✅ 5种压缩策略（语义去重、智能摘要、关键词提取、混合策略、自适应）
- ✅ 实时流式压缩，无需等待完整输入
- ✅ 智能上下文感知，保留关键信息
- ✅ 多模型Token精确计数（GPT-4/Claude/Llama等）
- ✅ 内置Web UI和REST API双模式
- ✅ 支持代码、日志、JSON等特殊格式压缩

### ✨ 核心特性

| 特性 | 描述 | 状态 |
|------|------|------|
| 🧠 **语义去重** | 基于BERT语义相似度，智能识别冗余内容 | ✅ |
| 📋 **智能摘要** | TextRank算法提取关键句子 | ✅ |
| 🔑 **关键词提取** | TF-IDF算法保留信息密度最高内容 | ✅ |
| 🔄 **混合策略** | 多阶段压缩流水线，最佳效果 | ✅ |
| 🎯 **自适应压缩** | 根据内容类型自动选择策略 | ✅ |
| ⚡ **实时流式** | SSE流式压缩，实时返回 | ✅ |
| 🌐 **Web UI** | 可视化操作界面 | ✅ |
| 🔌 **REST API** | 完整的API接口 | ✅ |
| 📊 **Token计数** | 多模型精确计数 | ✅ |
| 🐳 **Docker部署** | 一键容器化部署 | ✅ |

### 🚀 快速开始

#### 环境要求

- Python 3.10+
- 4GB+ RAM（推荐8GB）
- 支持的操作系统：Linux, macOS, Windows

#### 安装步骤

```bash
# 克隆仓库
git clone https://github.com/yourusername/SmartTokenCompressor.git
cd SmartTokenCompressor

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 安装项目
pip install -e .
```

#### 本地启动

```bash
# 启动API服务
stc serve

# 或直接使用Python
python -m uvicorn src.api.server:app --host 0.0.0.0 --port 8000
```

访问 http://localhost:8000 查看Web UI

#### CLI使用

```bash
# 压缩文本
stc compress "这是一段很长的文本..." -s hybrid -r 0.5

# 压缩文件
stc compress -f input.txt -o output.txt

# 计算Token
stc count "Hello world" -m gpt-4

# 分析文本结构
stc analyze -f document.txt

# 运行演示
stc demo
```

### 📖 详细使用指南

#### API接口

**压缩文本**
```bash
curl -X POST "http://localhost:8000/api/v1/compress" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "要压缩的文本...",
    "strategy": "hybrid",
    "target_ratio": 0.5,
    "model": "gpt-4"
  }'
```

**批量压缩**
```bash
curl -X POST "http://localhost:8000/api/v1/compress/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "texts": ["文本1", "文本2", "文本3"],
    "strategy": "hybrid",
    "target_ratio": 0.5
  }'
```

**Token计数**
```bash
curl -X POST "http://localhost:8000/api/v1/tokens/count" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello world",
    "model": "gpt-4"
  }'
```

#### 压缩策略说明

| 策略 | 适用场景 | 压缩效果 |
|------|----------|----------|
| semantic | 重复内容多的文本 | 去除冗余，保留语义 |
| summarization | 长文档 | 提取关键句子 |
| keyword | 信息密度高的文本 | 保留关键词密集部分 |
| hybrid | 通用场景 | 多阶段最佳效果 |
| adaptive | 未知类型 | 自动选择策略 |

### 💡 设计思路与迭代规划

#### 技术选型原因

- **Python 3.10+**：丰富的AI/ML生态，开发效率高
- **FastAPI**：高性能异步Web框架，自动生成API文档
- **sentence-transformers**：轻量级语义相似度计算
- **scikit-learn**：成熟的机器学习算法库
- **Tailwind CSS**：现代化CSS框架，快速构建UI

#### 后续功能迭代计划

- [ ] 支持更多语言（日语、韩语、德语等）
- [ ] 增加GPU加速支持
- [ ] 添加更多压缩算法（基于LLM的压缩）
- [ ] 支持自定义压缩规则
- [ ] 添加压缩质量评估指标
- [ ] 支持插件扩展机制

#### 社区贡献方向

- 优化现有算法性能
- 增加新的压缩策略
- 改进Web UI体验
- 完善文档和示例
- 修复bug和兼容性问题

### 📦 打包与部署指南

#### Docker部署

```bash
# 构建镜像
docker build -t smart-token-compressor .

# 运行容器
docker run -d -p 8000:8000 --name stc smart-token-compressor
```

#### 生产环境部署

```bash
# 使用Gunicorn
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker src.api.server:app

# 使用Docker Compose
docker-compose up -d
```

### 🤝 贡献指南

#### PR提交规范

1. Fork本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: Add some AmazingFeature'`)
4. 推送分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

#### Issue反馈规则

- 使用清晰的标题描述问题
- 提供复现步骤和环境信息
- 附上相关日志和截图
- 标注问题类型（bug/feature/question）

### 📄 开源协议

本项目采用 [MIT License](LICENSE) 开源协议。

---

<a name="smarttokencompressor-tw"></a>
## 🚀 SmartTokenCompressor (繁體中文)

### 🎉 專案介紹

SmartTokenCompressor 是一個高效能的智慧Token壓縮引擎，專為LLM（大語言模型）應用設計。它透過多種智慧壓縮策略，幫助開發者在保持語意完整性的同時，顯著減少API呼叫成本。

**靈感來源**：本專案靈感來源於GitHub Trending專案 headroom，我們在其基礎上進行了深度自研優化，增加了更多壓縮策略、即時串流處理、Web UI等差異化功能。

**解決痛點**：
- LLM API呼叫成本高昂，長文本處理費用驚人
- 大量冗餘資訊浪費token配額
- 現有工具壓縮效果不佳或速度太慢
- 缺乏可視化的壓縮效果對比

**自研差異化亮點**：
- ✅ 5種壓縮策略（語意去重、智慧摘要、關鍵詞提取、混合策略、自適應）
- ✅ 即時串流壓縮，無需等待完整輸入
- ✅ 智慧上下文感知，保留關鍵資訊
- ✅ 多模型Token精確計數（GPT-4/Claude/Llama等）
- ✅ 內建Web UI和REST API雙模式
- ✅ 支援程式碼、日誌、JSON等特殊格式壓縮

### ✨ 核心特性

| 特性 | 描述 | 狀態 |
|------|------|------|
| 🧠 **語意去重** | 基於BERT語意相似度，智慧識別冗餘內容 | ✅ |
| 📋 **智慧摘要** | TextRank演算法提取關鍵句子 | ✅ |
| 🔑 **關鍵詞提取** | TF-IDF演算法保留資訊密度最高內容 | ✅ |
| 🔄 **混合策略** | 多階段壓縮流水線，最佳效果 | ✅ |
| 🎯 **自適應壓縮** | 根據內容類型自動選擇策略 | ✅ |
| ⚡ **即時串流** | SSE串流壓縮，即時返回 | ✅ |
| 🌐 **Web UI** | 可視化操作介面 | ✅ |
| 🔌 **REST API** | 完整的API介面 | ✅ |
| 📊 **Token計數** | 多模型精確計數 | ✅ |
| 🐳 **Docker部署** | 一鍵容器化部署 | ✅ |

### 🚀 快速開始

#### 環境要求

- Python 3.10+
- 4GB+ RAM（推薦8GB）
- 支援的作業系統：Linux, macOS, Windows

#### 安裝步驟

```bash
# 克隆倉庫
git clone https://github.com/yourusername/SmartTokenCompressor.git
cd SmartTokenCompressor

# 建立虛擬環境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安裝依賴
pip install -r requirements.txt

# 安裝專案
pip install -e .
```

#### 本地啟動

```bash
# 啟動API服務
stc serve

# 或直接使用Python
python -m uvicorn src.api.server:app --host 0.0.0.0 --port 8000
```

訪問 http://localhost:8000 查看Web UI

#### CLI使用

```bash
# 壓縮文本
stc compress "這是一段很長的文本..." -s hybrid -r 0.5

# 壓縮檔案
stc compress -f input.txt -o output.txt

# 計算Token
stc count "Hello world" -m gpt-4

# 分析文本結構
stc analyze -f document.txt

# 執行演示
stc demo
```

### 📖 詳細使用指南

#### API介面

**壓縮文本**
```bash
curl -X POST "http://localhost:8000/api/v1/compress" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "要壓縮的文本...",
    "strategy": "hybrid",
    "target_ratio": 0.5,
    "model": "gpt-4"
  }'
```

**批量壓縮**
```bash
curl -X POST "http://localhost:8000/api/v1/compress/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "texts": ["文本1", "文本2", "文本3"],
    "strategy": "hybrid",
    "target_ratio": 0.5
  }'
```

**Token計數**
```bash
curl -X POST "http://localhost:8000/api/v1/tokens/count" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello world",
    "model": "gpt-4"
  }'
```

#### 壓縮策略說明

| 策略 | 適用場景 | 壓縮效果 |
|------|----------|----------|
| semantic | 重複內容多的文本 | 去除冗餘，保留語意 |
| summarization | 長文件 | 提取關鍵句子 |
| keyword | 資訊密度高的文本 | 保留關鍵詞密集部分 |
| hybrid | 通用場景 | 多階段最佳效果 |
| adaptive | 未知類型 | 自動選擇策略 |

### 💡 設計思路與迭代規劃

#### 技術選型原因

- **Python 3.10+**：豐富的AI/ML生態，開發效率高
- **FastAPI**：高效能非同步Web框架，自動生成API文件
- **sentence-transformers**：輕量級語意相似度計算
- **scikit-learn**：成熟的機器學習演算法庫
- **Tailwind CSS**：現代化CSS框架，快速建構UI

#### 後續功能迭代計劃

- [ ] 支援更多語言（日語、韓語、德語等）
- [ ] 增加GPU加速支援
- [ ] 添加更多壓縮演算法（基於LLM的壓縮）
- [ ] 支援自定義壓縮規則
- [ ] 添加壓縮品質評估指標
- [ ] 支援外掛擴充套件機制

#### 社群貢獻方向

- 最佳化現有演算法效能
- 增加新的壓縮策略
- 改進Web UI體驗
- 完善文件和範例
- 修復bug和相容性問題

### 📦 打包與部署指南

#### Docker部署

```bash
# 構建映象
docker build -t smart-token-compressor .

# 執行容器
docker run -d -p 8000:8000 --name stc smart-token-compressor
```

#### 生產環境部署

```bash
# 使用Gunicorn
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker src.api.server:app

# 使用Docker Compose
docker-compose up -d
```

### 🤝 貢獻指南

#### PR提交規範

1. Fork本倉庫
2. 建立特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: Add some AmazingFeature'`)
4. 推送分支 (`git push origin feature/AmazingFeature`)
5. 建立Pull Request

#### Issue反饋規則

- 使用清晰的標題描述問題
- 提供復現步驟和環境資訊
- 附上相關日誌和截圖
- 標註問題類型（bug/feature/question）

### 📄 開源協議

本專案採用 [MIT License](LICENSE) 開源協議。

---

<a name="smarttokencompressor-en"></a>
## 🚀 SmartTokenCompressor (English)

### 🎉 Project Introduction

SmartTokenCompressor is a high-performance intelligent token compression engine designed specifically for LLM (Large Language Model) applications. It helps developers significantly reduce API call costs while maintaining semantic integrity through multiple intelligent compression strategies.

**Inspiration**: This project is inspired by the GitHub Trending project [headroom](https://github.com/chopratejas/headroom). We have built upon it with deep independent research and optimization, adding more compression strategies, real-time streaming processing, Web UI, and other differentiated features.

**Pain Points Solved**:
- High LLM API call costs, especially for long text processing
- Wasted token quotas due to redundant information
- Existing tools with poor compression or slow speed
- Lack of visual compression effect comparison

**Independent Research Differentiation**:
- ✅ 5 compression strategies (semantic deduplication, smart summarization, keyword extraction, hybrid, adaptive)
- ✅ Real-time streaming compression without waiting for complete input
- ✅ Intelligent context awareness to preserve key information
- ✅ Multi-model token precise counting (GPT-4/Claude/Llama, etc.)
- ✅ Built-in Web UI and REST API dual mode
- ✅ Support for special format compression like code, logs, JSON

### ✨ Core Features

| Feature | Description | Status |
|---------|-------------|--------|
| 🧠 **Semantic Deduplication** | Smart redundancy identification based on BERT semantic similarity | ✅ |
| 📋 **Smart Summarization** | Key sentence extraction using TextRank algorithm | ✅ |
| 🔑 **Keyword Extraction** | TF-IDF algorithm to preserve highest information density content | ✅ |
| 🔄 **Hybrid Strategy** | Multi-stage compression pipeline for optimal results | ✅ |
| 🎯 **Adaptive Compression** | Automatic strategy selection based on content type | ✅ |
| ⚡ **Real-time Streaming** | SSE streaming compression with instant returns | ✅ |
| 🌐 **Web UI** | Visual operation interface | ✅ |
| 🔌 **REST API** | Complete API interface | ✅ |
| 📊 **Token Counting** | Precise multi-model counting | ✅ |
| 🐳 **Docker Deployment** | One-click containerized deployment | ✅ |

### 🚀 Quick Start

#### Requirements

- Python 3.10+
- 4GB+ RAM (8GB recommended)
- Supported OS: Linux, macOS, Windows

#### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/SmartTokenCompressor.git
cd SmartTokenCompressor

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install project
pip install -e .
```

#### Local Development

```bash
# Start API server
stc serve

# Or use Python directly
python -m uvicorn src.api.server:app --host 0.0.0.0 --port 8000
```

Visit http://localhost:8000 for Web UI

#### CLI Usage

```bash
# Compress text
stc compress "This is a long text..." -s hybrid -r 0.5

# Compress file
stc compress -f input.txt -o output.txt

# Count tokens
stc count "Hello world" -m gpt-4

# Analyze text structure
stc analyze -f document.txt

# Run demo
stc demo
```

### 📖 Detailed Usage Guide

#### API Endpoints

**Compress Text**
```bash
curl -X POST "http://localhost:8000/api/v1/compress" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Text to compress...",
    "strategy": "hybrid",
    "target_ratio": 0.5,
    "model": "gpt-4"
  }'
```

**Batch Compression**
```bash
curl -X POST "http://localhost:8000/api/v1/compress/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "texts": ["Text 1", "Text 2", "Text 3"],
    "strategy": "hybrid",
    "target_ratio": 0.5
  }'
```

**Token Counting**
```bash
curl -X POST "http://localhost:8000/api/v1/tokens/count" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello world",
    "model": "gpt-4"
  }'
```

#### Compression Strategy Guide

| Strategy | Use Case | Effect |
|----------|----------|--------|
| semantic | Text with much repetition | Remove redundancy, preserve semantics |
| summarization | Long documents | Extract key sentences |
| keyword | High information density text | Preserve keyword-dense parts |
| hybrid | General purpose | Multi-stage optimal results |
| adaptive | Unknown type | Auto-select strategy |

### 💡 Design Philosophy & Roadmap

#### Technology Choices

- **Python 3.10+**: Rich AI/ML ecosystem, high development efficiency
- **FastAPI**: High-performance async web framework with auto API docs
- **sentence-transformers**: Lightweight semantic similarity computation
- **scikit-learn**: Mature machine learning algorithm library
- **Tailwind CSS**: Modern CSS framework for rapid UI building

#### Future Iteration Plans

- [ ] Support for more languages (Japanese, Korean, German, etc.)
- [ ] GPU acceleration support
- [ ] More compression algorithms (LLM-based compression)
- [ ] Custom compression rules support
- [ ] Compression quality evaluation metrics
- [ ] Plugin extension mechanism

#### Community Contribution Directions

- Optimize existing algorithm performance
- Add new compression strategies
- Improve Web UI experience
- Complete documentation and examples
- Fix bugs and compatibility issues

### 📦 Packaging & Deployment Guide

#### Docker Deployment

```bash
# Build image
docker build -t smart-token-compressor .

# Run container
docker run -d -p 8000:8000 --name stc smart-token-compressor
```

#### Production Deployment

```bash
# Using Gunicorn
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker src.api.server:app

# Using Docker Compose
docker-compose up -d
```

### 🤝 Contribution Guide

#### PR Submission Guidelines

1. Fork this repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'feat: Add some AmazingFeature'`)
4. Push branch (`git push origin feature/AmazingFeature`)
5. Create Pull Request

#### Issue Feedback Rules

- Use clear titles to describe issues
- Provide reproduction steps and environment info
- Attach relevant logs and screenshots
- Label issue type (bug/feature/question)

### 📄 License

This project is licensed under the [MIT License](LICENSE).
