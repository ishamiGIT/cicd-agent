import vertexai
from vertexai import rag

RAG_PATTERNS_CORPUS_ID = "projects/haroonc-exp/locations/us-east4/ragCorpora/5476377146882523136"
RAG_KNOWLEDGE_CORPUS_ID = "projects/haroonc-exp/locations/us-east4/ragCorpora/rag-cicd-knowledge"
vertexai.init(project="haroonc-exp", location="us-east4")

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
    text="cicd pipeline for vibe coding, quick iteration, fast feedback",
    rag_retrieval_config=rag_retrieval_config,
)
patterns = ""

for i, context in enumerate(response.contexts.contexts):
    patterns += f'Pattern {i}: {context.text} \n\n'

print(patterns)