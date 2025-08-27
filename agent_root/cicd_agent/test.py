RAG_PATTERNS_CORPUS_ID = "projects/haroonc-exp/locations/us-east4/ragCorpora/7205759403792793600"
RAG_KNOWLEDGE_CORPUS_ID = "projects/haroonc-exp/locations/us-east4/ragCorpora/rag-cicd-knowledge"
TARGET_FOLDER_PATH = os.environ.get('WORKING_DIR', '/data')
vertexai.init(project="haroonc-exp", location="us-east4")

rag_retrieval_config = rag.RagRetrievalConfig(
    top_k=3,  # Optional
    filter=rag.Filter(vector_distance_threshold=0.5),  # Optional
)
response = rag.retrieval_query(
    rag_resources=[
        rag.RagResource(
            rag_corpus=RAG_PATTERNS_CORPUS_ID,
            # Optional: supply IDs from `rag.list_files()`.
            # rag_file_ids=["rag-file-1", "rag-file-2", ...],
        )
    ],
    text=keywords,
    rag_retrieval_config=rag_retrieval_config,
)
print(response)