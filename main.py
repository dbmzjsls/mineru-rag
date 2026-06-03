import argparse
from src.chunker import JSONChunker
from src.config import Config
from src.parser import MinerUParser
from src.rag import RAGPipeline
from src.vector_db import VectorDBManager


def run_pipeline(pdf_filename: str, user_question: str, rebuild_db: bool = True):
    """RAG 系统核心调度逻辑"""
    pdf_path = Config.DATA_RAW_DIR / pdf_filename
    if not pdf_path.exists():
        print(f"在 {Config.DATA_RAW_DIR} 没有找到文件 {pdf_filename}")
        return

    db_manager = VectorDBManager()

    index_exists = (Config.DB_DIR / "faiss_index").exists()
    if rebuild_db or not index_exists:
        print("正在执行完整流水线: 解析 -> 切块 -> 向量化...")
        parser = MinerUParser(str(pdf_path))
        parser.parse_pdf()
        json_data = parser.load_json()

        chunker = JSONChunker(max_chunk_size=Config.CHUNK_SIZE)
        docs = chunker.chunk(json_data)

        vector_store = db_manager.build_from_documents(docs)
    else:
        vector_store = db_manager.load_db()

    rag = RAGPipeline(vector_store)
    answer = rag.query(user_question)

    print("\n" + "=" * 50)
    print("回答:")
    print(answer)
    print("=" * 50 + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MinerU RAG - 面向中文 PDF 的检索增强问答系统")
    parser.add_argument("pdf", help="PDF 文件名 (位于 data/raw/ 目录下)")
    parser.add_argument("question", nargs="?", default=None, help="要提问的问题 (不填则进入交互模式)")
    parser.add_argument("--no-rebuild", action="store_true", help="不重建索引, 优先使用已有向量库")

    args = parser.parse_args()

    if args.question:
        run_pipeline(args.pdf, args.question, rebuild_db=not args.no_rebuild)
    else:
        rebuild = not args.no_rebuild
        print(f"\n已加载 PDF: {args.pdf}")
        print("输入问题开始提问, 输入 quit 退出\n")

        vector_store = None
        db_manager = VectorDBManager()

        while True:
            try:
                question = input(">>> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n再见!")
                break

            if not question:
                continue
            if question.lower() == "quit":
                break

            if rebuild or vector_store is None:
                pdf_path = Config.DATA_RAW_DIR / args.pdf
                if not (Config.DB_DIR / "faiss_index").exists() or rebuild:
                    print("正在构建索引...")
                    mineru = MinerUParser(str(pdf_path))
                    mineru.parse_pdf()
                    json_data = mineru.load_json()
                    chunker = JSONChunker(max_chunk_size=Config.CHUNK_SIZE)
                    docs = chunker.chunk(json_data)
                    vector_store = db_manager.build_from_documents(docs)
                    rebuild = False
                else:
                    vector_store = db_manager.load_db()

            rag = RAGPipeline(vector_store)
            answer = rag.query(question)
            print("\n" + "=" * 50)
            print("回答:")
            print(answer)
            print("=" * 50 + "\n")
