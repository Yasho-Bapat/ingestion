import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_experimental.text_splitter import SemanticChunker
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
import chromadb
from chromadb.config import Settings
import logging
import time
from langchain_openai import AzureOpenAIEmbeddings
from dotenv import load_dotenv

from utils.file_mapper import file_mapper

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(filename="ingestion.log", level=logging.INFO)

start = time.perf_counter()

directory_path = "test_docs"
files = os.listdir(directory_path)
files = [f for f in files if os.path.isfile(os.path.join(directory_path, f))]
print(files)
for filename in files:
    if filename == "5.1 11001-5 SDS.pdf":
        print(f"Ingesting File: {filename}")
        documents = []
        loader = PyPDFLoader(file_path=f"test_docs/{filename}")
        document = loader.load()
        logger.info(f"Loaded {filename}")
        documents.extend(document)

        persistent_client = chromadb.PersistentClient(path="test_chroma_db/", settings=Settings(anonymized_telemetry=False))
        ENDPOINT = os.getenv("ENDPOINT")
        OPENAI_API_VERSION = os.getenv("OPENAI_API_VERSION")
        AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")

        embedding_function = AzureOpenAIEmbeddings(deployment="langchain-splitting-test1", api_key=AZURE_OPENAI_API_KEY,
                                                   azure_endpoint=ENDPOINT)

        splitters = {"semantic": SemanticChunker(embeddings=embedding_function, breakpoint_threshold_type="interquartile",breakpoint_threshold_amount=1.5),
                     "recursive": RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=600)}

        for key, splitter in splitters.items():
            split_doc = splitter.split_documents(documents)
            logger.info(f"Splitted documents for {key} into {len(split_doc)} splits")

            collection_name = file_mapper(filename=f"{filename}")
            print(f"collection name: {key}_{collection_name}")
            db = Chroma.from_documents(documents, embedding=embedding_function, persist_directory="./test_chroma_db", collection_name=f"{key}_{collection_name}")

            logger.info(f"{key} split ingestion of {filename} completed in {time.perf_counter() - start :.2f} seconds")
