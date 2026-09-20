from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        results = self.store.search(question, top_k=top_k)

        if not results:
            return self.llm_fn(f"Question: {question}\n\nNo relevant context found.")

        context = "\n\n".join(
            f"[Context {index + 1}] {result['content']}"
            for index, result in enumerate(results)
        )

        prompt = (
            "You are a helpful assistant. Use the context below to answer the user's question.\n"
            "If the answer is not in the provided context, say that it is not available in the retrieved context.\n\n"
            f"Context:\n{context}\n\nQuestion:\n{question}"
        )

        return self.llm_fn(prompt)
