import subprocess
from langchain_core.language_models import LLM
from langchain.chains import RetrievalQA
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.embeddings import Embeddings
import numpy as np

# 1. Dummy embedding class to satisfy FAISS
class DummyEmbedding(Embeddings):
    def embed_documents(self, documents):
        return [np.zeros(384).tolist() for _ in documents]  # FAISS-compatible dimension

    def embed_query(self, query):
        return np.zeros(384).tolist()

# 2. Custom LLM class for Ollama
class OllamaLLM(LLM):
    def _call(self, prompt: str, **kwargs) -> str:
        result = subprocess.run(
        ["ollama", "run", "llama3:latest"],
        input=prompt,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",  # 👈 This is the fix
        errors="ignore"    # 👈 Optional: skip over bad characters
    )
        if result.returncode != 0:
            raise RuntimeError(f"Ollama failed: {result.stderr}")
        return result.stdout.strip()


    @property
    def _llm_type(self) -> str:
        return "ollama-custom"

# 3. Build QA pipeline using Ollama + dummy embedding
def build_qa_pipeline(text: str):
    splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = splitter.create_documents([text])

    embeddings = DummyEmbedding()
    vectorstore = FAISS.from_documents(docs, embeddings)
    retriever = vectorstore.as_retriever()

    ollama_llm = OllamaLLM()
    qa_chain = RetrievalQA.from_chain_type(llm=ollama_llm, retriever=retriever)

    return qa_chain
