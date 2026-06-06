/**
 * SmartTokenCompressor Web UI Application
 */

class SmartTokenCompressor {
    constructor() {
        this.apiBaseUrl = window.location.origin;
        this.initializeEventListeners();
        this.loadDemoText();
    }

    initializeEventListeners() {
        // Strategy selection
        const strategySelect = document.getElementById('strategy');
        if (strategySelect) {
            strategySelect.addEventListener('change', (e) => {
                this.updateStrategyInfo(e.target.value);
            });
        }

        // Target ratio slider
        const targetRatio = document.getElementById('targetRatio');
        const ratioValue = document.getElementById('ratioValue');
        if (targetRatio && ratioValue) {
            targetRatio.addEventListener('input', (e) => {
                ratioValue.textContent = e.target.value + '%';
            });
        }

        // Compress button
        const compressBtn = document.getElementById('compressBtn');
        if (compressBtn) {
            compressBtn.addEventListener('click', () => this.compress());
        }

        // Clear button
        const clearBtn = document.getElementById('clearBtn');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => this.clear());
        }

        // Copy button
        const copyBtn = document.getElementById('copyBtn');
        if (copyBtn) {
            copyBtn.addEventListener('click', () => this.copyResult());
        }

        // Auto-resize textarea
        const inputText = document.getElementById('inputText');
        if (inputText) {
            inputText.addEventListener('input', function() {
                this.style.height = 'auto';
                this.style.height = Math.max(this.scrollHeight, 300) + 'px';
            });
        }
    }

    updateStrategyInfo(strategy) {
        const infoMap = {
            'semantic': '🧠 语义去重 - 基于BERT相似度去除冗余',
            'summarization': '📋 智能摘要 - TextRank提取关键句',
            'keyword': '🔑 关键词提取 - TF-IDF保留核心信息',
            'hybrid': '🔄 混合策略 - 多阶段最佳压缩',
            'adaptive': '🎯 自适应 - 根据内容自动选择'
        };
        
        const infoElement = document.getElementById('strategyInfo');
        if (infoElement) {
            infoElement.textContent = infoMap[strategy] || '';
        }
    }

    async compress() {
        const inputText = document.getElementById('inputText');
        const strategy = document.getElementById('strategy');
        const targetRatio = document.getElementById('targetRatio');
        const model = document.getElementById('model');
        const compressBtn = document.getElementById('compressBtn');

        const text = inputText.value.trim();
        if (!text) {
            this.showNotification('请输入要压缩的文本', 'warning');
            return;
        }

        // Update button state
        compressBtn.disabled = true;
        compressBtn.innerHTML = '<span class="loading-spinner"></span> 压缩中...';

        try {
            const response = await fetch(`${this.apiBaseUrl}/api/v1/compress`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: text,
                    strategy: strategy.value,
                    target_ratio: parseInt(targetRatio.value) / 100,
                    model: model.value,
                    preserve_structure: true,
                }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            this.displayResult(data);
            this.showNotification('压缩成功！', 'success');

        } catch (error) {
            console.error('Compression error:', error);
            this.showNotification('压缩失败: ' + error.message, 'error');
        } finally {
            compressBtn.disabled = false;
            compressBtn.innerHTML = '<span>🚀</span> 开始压缩';
        }
    }

    displayResult(data) {
        // Update output text
        const outputText = document.getElementById('outputText');
        if (outputText) {
            outputText.value = data.compressed_text || '';
        }

        // Update stats
        this.updateStat('originalTokens', data.original_tokens);
        this.updateStat('compressedTokens', data.compressed_tokens);
        this.updateStat('tokensSaved', data.tokens_saved);
        this.updateStat('savingsPercentage', data.savings_percentage + '%');

        // Update compression ratio
        const compressionRatio = document.getElementById('compressionRatio');
        if (compressionRatio) {
            compressionRatio.textContent = `压缩比: ${data.compression_ratio}`;
        }

        // Update progress bar
        const progressBar = document.getElementById('progressBar');
        if (progressBar) {
            const progress = Math.min(data.savings_percentage, 100);
            progressBar.style.width = progress + '%';
        }

        // Update stages info
        this.displayStages(data.stages);
    }

    updateStat(elementId, value) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = value.toLocaleString();
        }
    }

    displayStages(stages) {
        const stagesContainer = document.getElementById('stagesContainer');
        if (!stagesContainer || !stages) return;

        stagesContainer.innerHTML = '';
        stages.forEach((stage, index) => {
            const stageElement = document.createElement('div');
            stageElement.className = 'flex items-center gap-3 p-3 bg-gray-50 rounded-lg';
            stageElement.innerHTML = `
                <div class="w-8 h-8 bg-purple-100 text-purple-600 rounded-full flex items-center justify-center font-bold text-sm">
                    ${index + 1}
                </div>
                <div class="flex-1">
                    <div class="font-medium text-gray-800">${stage.stage || '未知阶段'}</div>
                    <div class="text-sm text-gray-500">${JSON.stringify(stage)}</div>
                </div>
            `;
            stagesContainer.appendChild(stageElement);
        });
    }

    clear() {
        const inputText = document.getElementById('inputText');
        const outputText = document.getElementById('outputText');
        
        if (inputText) inputText.value = '';
        if (outputText) outputText.value = '';
        
        this.resetStats();
    }

    resetStats() {
        this.updateStat('originalTokens', '0');
        this.updateStat('compressedTokens', '0');
        this.updateStat('tokensSaved', '0');
        this.updateStat('savingsPercentage', '0%');
        
        const compressionRatio = document.getElementById('compressionRatio');
        if (compressionRatio) {
            compressionRatio.textContent = '压缩比: 1.0000';
        }
        
        const progressBar = document.getElementById('progressBar');
        if (progressBar) {
            progressBar.style.width = '0%';
        }
    }

    copyResult() {
        const outputText = document.getElementById('outputText');
        const copyBtn = document.getElementById('copyBtn');
        
        if (outputText && outputText.value) {
            outputText.select();
            document.execCommand('copy');
            
            if (copyBtn) {
                copyBtn.innerHTML = '<span>✅</span> 已复制';
                setTimeout(() => {
                    copyBtn.innerHTML = '<span>📋</span> 复制结果';
                }, 2000);
            }
            
            this.showNotification('已复制到剪贴板', 'success');
        }
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        const colors = {
            success: 'bg-green-500',
            error: 'bg-red-500',
            warning: 'bg-yellow-500',
            info: 'bg-blue-500'
        };
        
        notification.className = `fixed top-4 right-4 ${colors[type]} text-white px-6 py-3 rounded-lg shadow-lg z-50 animate-fade-in`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    loadDemoText() {
        const inputText = document.getElementById('inputText');
        if (inputText && !inputText.value) {
            inputText.value = `SmartTokenCompressor 是一个高性能的智能Token压缩引擎，专为LLM应用设计。

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
4. 对话历史：压缩对话历史，保留上下文`;
        }
    }
}

// Initialize application
document.addEventListener('DOMContentLoaded', () => {
    window.app = new SmartTokenCompressor();
});
