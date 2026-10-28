from langchain_core.documents import Document
import os
from app.rag.vector_store import vector_store
async def load_docs(docs_path: str):
    docs = []
    ids = []
    for file in os.listdir(docs_path):
        if not file.endswith(".md"):
            continue
        file_path = os.path.join(docs_path, file)
        if not os.path.isfile(file_path):
            continue
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            content = content.strip()
        if len(content) < 10:
            continue
        docs.append(Document(page_content=content, metadata={"source": file}))
        ids.append(file)
    if len(docs) > 0:
        await vector_store.aadd_documents(documents=docs, ids=ids)
