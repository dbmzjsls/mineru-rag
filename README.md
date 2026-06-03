# MinerU RAG

基于 MinerU 结构化解析 + FAISS 向量检索 + 阿里云百炼大模型的 RAG 问答系统，面向中文 PDF 文档。

## 工作流程

1. **PDF 解析** — 使用阿里巴巴 MinerU 将 PDF 转为结构化 JSON（文本/表格/图片/公式）
2. **语义切块** — 表格、图片、公式保留为独立块，文本按 1024 字符合并
3. **向量化** — 使用 `paraphrase-multilingual-MiniLM-L12-v2` 计算 Embedding，存入 FAISS
4. **检索问答** — 结合检索到的上下文，通过阿里云百炼 `glm-5` 模型生成回答

## 环境要求

- Python >= 3.10
- [uv](https://docs.astral.sh/uv/) 包管理器

## 快速开始

```bash
# 安装依赖
uv sync

# 将 PDF 文件放入 data/raw/ 目录

# 单次问答
uv run python main.py "Modular RAG.pdf" "你的问题"

# 交互模式（连续提问）
uv run python main.py "Modular RAG.pdf"

# 复用已有索引，跳过解析和向量化
uv run python main.py "Modular RAG.pdf" "你的问题" --no-rebuild
```

## 配置

在 `.env` 文件中设置 API Key：

```env
DASHSCOPE_API_KEY=your_key_here
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
```

## 项目结构

```
mineru-rag/
├── main.py              # 入口：串联完整 RAG 流水线
├── src/
│   ├── config.py        # 全局配置（路径、模型参数、API Key）
│   ├── parser.py        # MinerU PDF 解析器
│   ├── chunker.py       # 结构化 JSON → Document 切块
│   ├── vector_db.py     # FAISS 向量数据库管理
│   └── rag.py           # RAG 检索问答管道
├── data/
│   ├── raw/             # 待解析的 PDF 文件
│   ├── output/          # MinerU 解析输出的 JSON
│   └── faiss_db/        # FAISS 向量索引持久化
└── pyproject.toml
```
