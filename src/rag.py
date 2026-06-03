from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from src.config import Config

class RAGPipeline:
    def __init__(self, vector_store):
        self.llm = ChatOpenAI(
            model=Config.LLM_MODEL,
            api_key=SecretStr(Config.DASHSCOPE_API_KEY),
            base_url=Config.DASHSCOPE_BASE_URL,
            temperature=Config.LLM_TEMPERATURE
        )
        # 设置返回的相关结果
        self.retriever = vector_store.as_retriever(search_kwargs={"k":Config.RETRIEVER_K})

    def _format_docs(self, docs):
        """格式化召回的文档，便于大模型阅读"""
        formatted = []
        for d in docs:
            doc_type = d.metadata.get('type','text')
            formatted.append(f"--- [类型：{doc_type}] ---\n{d.page_content}")
        return "\n\n".join(formatted)

    def query(self, question:str) -> str:
        """执行 RAG 检索问答"""
        prompt = ChatPromptTemplate.from_template(
            """
            你是一个严谨的 AI 数据分析助手。 请基于以下提供的参考资料回答问题。
            参考资料中可能包含文本和复杂的表格数据。
            如果资料中没有答案，请说"在已知上下文中没有符合的内容"
            【参考资料】：
            {context}
            【问题】：
            {question}
            """
        )
        # 构造 Langchain LCEL 链
        rag_chain = (
            {"context":self.retriever | self._format_docs, "question":RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )

        print(f"\n [RAG] 思考中：{question} ...")
        return rag_chain.invoke(question)