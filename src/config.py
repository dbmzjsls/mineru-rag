import os
from pathlib import Path
from dotenv import load_dotenv

class Config:
    #加载环境变量
    load_dotenv()

    # 路径管理
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATA_RAW_DIR = BASE_DIR / "data"/"raw"
    DATA_OUT_DIR = BASE_DIR / "data"/"output"
    DB_DIR = BASE_DIR / "data"/"faiss_db"

    # RAG 配置
    EMBEDDING_MODEL: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    RERANK_MODEL: str = "BAAI/bge-reranker-base"
    MODEL_KWARGS = {'device': 'cpu'}
    CHUNK_SIZE: int = 1024
    CHUNK_OVERLAP: int = 128
    RETRIEVER_K: int = 5
    TOP_N: int = 2

    # 模型配置
    LLM_MODEL:str = "glm-5"
    DASHSCOPE_API_KEY:str = os.environ.get("DASHSCOPE_API_KEY")
    DASHSCOPE_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    LLM_TEMPERATURE: float = 0.2

    # MinerU 配置
    MINERU_FORMAT = "json"
    @classmethod
    def ensure_dirs(cls):
        """确保所有必要的目录都已经创建"""
        directories = [cls.DATA_RAW_DIR, cls.DATA_OUT_DIR, cls.DB_DIR]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    @classmethod
    def validate(cls):
        """检查核心配置是否存在"""
        if not cls.DASHSCOPE_API_KEY:
            raise ValueError("未找到 DASHSCOPE_API_KEY 。请检查根目录下的.env文件")

# 自动检查
Config.ensure_dirs()
Config.validate()

