from langchain_core.documents import Document


class JSONChunker:
    def __init__(self, max_chunk_size=1024):
        self.max_chunk_size = max_chunk_size

    def chunk(self, json_data:list) ->list[Document]:
        """
        基于结构化 JSON 进行切块
        保留表格和图片为独立 chunk 不会被打断。连续文本合并至最大限制
        """
        print("正在结构化语义切块...")
        documents = []
        current_text = ""

        # 遍历 MinerU 提取结构化节点
        for node in json_data:
            node_type = node.get("type","text")
            content = node.get("text","") or node.get("html","") or node.get("markdown","")

            if not content:
                continue

            # 遇到表格或者图片等独立元素就直接保存之前文本
            if node_type in ["table", "image", "equation"]:
                if current_text:
                    documents.append(Document(page_content=current_text.strip(),metadata={"type":"text"}))
                    current_text = ""
                # 表格或者图片作为独立的 Document
                documents.append(Document(page_content=content.strip(),metadata={"type":node_type}))
            else:
                # 普通文本则累加
                if len(current_text) + len(content) > self.max_chunk_size:
                    documents.append(Document(page_content=current_text.strip(),metadata={"type":"text"}))
                    current_text = content + "\n"
                else:
                    current_text += content + "\n"

        # 处理文本末尾
        if current_text.strip():
            documents.append(Document(page_content=current_text.strip(),metadata={"type":"text"}))

        print(f"[Chunker] 切块完成，共生成{len(documents)} 个 Chunk。")
        return documents
