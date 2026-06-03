from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from src.config import Config


class VectorDBManager:
    def __init__(self):
        self.db_path = Config.DB_DIR
        self.vector_store = None
        self.embeddings = HuggingFaceEmbeddings(
            model_name=Config.EMBEDDING_MODEL,
            model_kwargs=Config.MODEL_KWARGS
        )

    def build_from_documents(self, document):
        """将切块后的文档向量化存入 FAISS """
        print("[VectorDB] 正在计算 Embedding 并构建 Faiss 索引")
        self.vector_store = FAISS.from_documents(document,self.embeddings)
        self.vector_store.save_local(str(self.db_path))
        print(f"[VectorDB] 索引构建并持久化完成： {self.db_path}")
        return self.vector_store

    def load_db(self):
        """加载已存在的 FAISS 索引"""
        print("[VectorDB] 正在加载本地 FAISS 索引")
        self.vector_store = FAISS.load_local(
            str(self.db_path),
            self.embeddings,
            allow_dangerous_deserialization=True
        )
        print("[VectorDB] 本地索引加载成功")
        return self.vector_store