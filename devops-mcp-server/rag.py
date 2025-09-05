from app import mcp
from vertexai import rag
import os
from typing import Dict, Any

RAG_PATTERNS_CORPUS_ID = os.environ.get("RAG_PATTERNS_CORPUS_ID", "projects/haroonc-exp/locations/us-east4/ragCorpora/5476377146882523136")
RAG_KNOWLEDGE_CORPUS_ID = os.environ.get("RAG_KNOWLEDGE_CORPUS_ID", "projects/haroonc-exp/locations/us-east4/ragCorpora/2017612633061982208")

@mcp.tool
def query_knowledge(query: str) -> str:
    """Queries the knowledge base for information on how to build and manage CI/CD pipelines.

    Args:
        query: The query to search for in the knowledge base.

    Returns:
        The response from the retrieval query.
    """
    try:
        rag_retrieval_config = rag.RagRetrievalConfig(
            top_k=3,  # Optional
            filter=rag.Filter(vector_distance_threshold=0.5),  # Optional
        )
        response = rag.retrieval_query(
            rag_resources=[
                rag.RagResource(
                    rag_corpus=RAG_KNOWLEDGE_CORPUS_ID,
                )
            ],
            text=query,
            rag_retrieval_config=rag_retrieval_config,
        )
        knowledge = ""

        for i, context in enumerate(response.contexts.contexts):
            knowledge += f'knowledge {i}: {context.text} \n\n'

        return knowledge
    except Exception as e:
        return {"error": str(e)}

@mcp.tool
def search_common_cicd_patterns(keywords: str) -> str:
    """Searches for common CI/CD patterns and best practices.

    Args:
        keywords: The keywords to search for in the CI/CD patterns.

    Returns:
        The response from the retrieval query.
    """
    try:
        rag_retrieval_config = rag.RagRetrievalConfig(
            top_k=2,  # Optional
            filter=rag.Filter(vector_distance_threshold=0.5),  # Optional
        )
        response = rag.retrieval_query(
            rag_resources=[
                rag.RagResource(
                    rag_corpus=RAG_PATTERNS_CORPUS_ID,
                )
            ],
            text=keywords,
            rag_retrieval_config=rag_retrieval_config,
        )
        patterns = ""

        for i, context in enumerate(response.contexts.contexts):
            patterns += f'Pattern {i}: {context.text} \n\n'

        return patterns
    except Exception as e:
        return {"error": str(e)}

