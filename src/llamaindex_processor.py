# --- START OF FILE src/llamaindex_processor.py ---
import os
import json
from typing import List, Dict

from llama_index.core import VectorStoreIndex, Settings
from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.llms.gemini import Gemini  # CORRECTED
from llama_index.embeddings.gemini import GeminiEmbedding # CORRECTED
from llama_index.core.readers.base import BaseReader
from llama_index.core.schema import Document
from .config import GEMINI_MODEL_NAME

class HfDatasetReader(BaseReader):
    """A custom LlamaIndex reader to load files from an in-memory dict."""
    def __init__(self, file_contents: Dict[str, str]):
        """
        Initializes the reader with a dictionary of file contents.
        Args:
            file_contents (Dict[str, str]): A dictionary where keys are file paths (e.g., in HF repo)
                                             and values are the string content of the files.
        """
        self.file_contents = file_contents

    def load_data(self) -> List[Document]:
        """Loads data from the file_contents dictionary into LlamaIndex Document objects."""
        documents = []
        for file_path, content in self.file_contents.items():
            # The file_path here is the key, e.g., the path in the HF repo, used as a unique ID.
            documents.append(Document(text=content, id_=file_path, metadata={"file_path": file_path}))
        return documents

def create_semantic_index(
    api_key: str,
    markdown_content_map: Dict[str, str],
    json_content_map: Dict[str, List[Dict]]
) -> VectorStoreIndex:
    """
    Creates a LlamaIndex VectorStoreIndex from the markdown content,
    enhanced with metadata from the JSON files.
    """
    print("LlamaIndex: Initializing models and settings...")
    # Initialize LlamaIndex components with the provided API key
    Settings.llm = Gemini(model_name=f"models/{GEMINI_MODEL_NAME}", api_key=api_key)
    Settings.embed_model = GeminiEmbedding(model_name="models/embedding-001", api_key=api_key)
    
    print("LlamaIndex: Loading documents with custom in-memory reader...")
    # Load documents from the in-memory dictionary of markdown content
    reader = HfDatasetReader(markdown_content_map)
    documents = reader.load_data()
    
    print(f"LlamaIndex: Loaded {len(documents)} markdown documents.")

    # Initialize the node parser with semantic splitting configuration
    # Breakpoint threshold of 85 means it will be quite precise about splitting, good for financial docs.
    splitter = SemanticSplitterNodeParser(
        buffer_size=2,  # Number of sentences to buffer around a split.
        breakpoint_percentile_threshold=85,
        embed_model=Settings.embed_model,
    )
    
    print("LlamaIndex: Parsing documents into nodes (chunks)...")
    nodes = splitter.get_nodes_from_documents(documents)
    print(f"LlamaIndex: Created {len(nodes)} semantic nodes.")

    print("LlamaIndex: Enhancing nodes with structured JSON metadata...")
    # Enhance nodes with metadata from the corresponding JSON files
    for node in nodes:
        original_filepath = node.metadata.get("file_path", "")
        # We only enhance nodes that came from a tables markdown file
        if "_tables.md" in original_filepath:
            # Construct the corresponding json metadata key
            json_key = original_filepath.replace("_tables.md", "_tables_metadata.json")
            if json_key in json_content_map:
                tables_in_doc = json_content_map[json_key]
                # Find the specific table mentioned in this node's text
                for table_meta in tables_in_doc:
                    # A simple text match to link the node to its structured table data
                    if table_meta['title'].lower() in node.get_content().lower():
                        # Add the structured data to the node's metadata dictionary.
                        # This makes the structured data available during retrieval.
                        node.metadata["structured_table_data"] = table_meta
                        # Add a flag for easier filtering later if needed
                        node.metadata["contains_table"] = True
                        # Found the table for this node, no need to check others in this doc
                        break

    print("LlamaIndex: Building the vector store index from nodes...")
    # Create the index from the (now metadata-enhanced) nodes
    index = VectorStoreIndex(nodes)
    
    print("LlamaIndex: Index creation complete.")
    return index

def query_top_chunks(index: VectorStoreIndex, query_str: str, top_k: int = 10) -> List:
    """Queries the index and returns the top_k most relevant nodes/chunks."""
    print(f"LlamaIndex: Querying for '{query_str[:50]}...' (top {top_k})")
    # as_retriever is the standard way to get nodes from the index
    retriever = index.as_retriever(similarity_top_k=top_k)
    nodes = retriever.retrieve(query_str)
    print(f"LlamaIndex: Retrieved {len(nodes)} nodes.")
    return nodes

def combine_all_markdown(markdown_content_map: Dict[str, str]) -> str:
    """Combines all markdown file contents into a single string for the critique context."""
    full_content = []
    # Sort by filename to ensure a consistent order
    for filepath, content in sorted(markdown_content_map.items()):
        header = f"\n\n--- START OF DOCUMENT: {os.path.basename(filepath)} ---\n\n"
        full_content.append(header)
        full_content.append(content)
    return "".join(full_content)
# --- END OF FILE src/llamaindex_processor.py ---