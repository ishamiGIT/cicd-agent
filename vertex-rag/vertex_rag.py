import os
import logging
import vertexai
from vertexai import rag
from vertexai.generative_models import GenerativeModel, Tool

_vertexai_initialized = False

def initialize_vertexai_if_needed():
    global _vertexai_initialized
    if not _vertexai_initialized:
        vertexai.init(project="haroonc-exp", location="us-east4")
        _vertexai_initialized = True
        logging.info("Vertex AI SDK initialized.")
    else:
        logging.info("Vertex AI SDK already initialized.")

def _upload_file_to_rag(file_path: str, file_name:str, rag_corpus_id: str):
    rag_file = rag.upload_file(
        corpus_name=rag_corpus_id,
        path=file_path,
        display_name=file_name,
        description=file_name,
    )
    logging.info("Uploaded %s to RAG ", rag_file.name)
    return rag_file

def upload_dir_to_rag(parent_dir:str, dir_list:list, rag_corpus_id: str):
    initialize_vertexai_if_needed()
    logging.info(f"Loading files in {parent_dir} that are in dirs {dir_list}")
    for curr_dir in dir_list:
        for root, _, files in os.walk(os.path.join(parent_dir,curr_dir)):
            for file in files:
                file_path=os.path.join(root, file)
                file_name = os.path.join(root, file).replace(parent_dir, "")
                _upload_file_to_rag(file_path, file_name, rag_corpus_id)



def rag_search_function(query: str) -> str:
    initialize_vertexai_if_needed()
    """Performs a RAG search using the Gemini model and returns the response."""
    rag_retrieval_tool = Tool.from_retrieval(
        retrieval=rag.Retrieval(
            source=rag.VertexRagStore(
                rag_resources=[rag.RagResource(rag_corpus=RAG_CORPUS_ID)]
            )
        )
    )
    # The generative model is instantiated inside the function to be a new instance on each call
    rag_model = GenerativeModel(
        model_name="gemini-1.5-flash-latest",
        tools=[rag_retrieval_tool],
        generation_config={"temperature": 0}
    )
    
    response = rag_model.generate_content(query)
    return response.text

if __name__ == "__main__": 
    # Direct context retrieval
    rag_retrieval_config = rag.RagRetrievalConfig(
        top_k=3,  # Optional
        filter=rag.Filter(vector_distance_threshold=0.5),  # Optional
    )
    response = rag.retrieval_query(
        rag_resources=[
            rag.RagResource(
                rag_corpus=RAG_CORPUS_ID,
                # Optional: supply IDs from `rag.list_files()`.
                # rag_file_ids=["rag-file-1", "rag-file-2", ...],
            )
        ],
        text="How to clone a git repository in cloud build?",
        rag_retrieval_config=rag_retrieval_config,
    )
    print(response)