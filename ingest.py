from langchain_community.document_loaders import PyPDFLoader
from langchain_experimental.text_splitter import SemanticChunker
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
import chromadb
from chromadb.config import Settings
import logging
import time
from langchain_openai import AzureOpenAIEmbeddings

logger = logging.getLogger(__name__)
logging.basicConfig(filename="ingestion.log", level=logging.INFO)

start = time.perf_counter()
documents = []
filename = "docs/4.1 SDS Norton wheel 3.032 X .375 X 1-14 66253249782.pdf"
loader = PyPDFLoader(file_path=filename)
document = loader.load()
logger.info(f"Loaded {filename}")
documents.extend(document)

persistent_client = chromadb.PersistentClient(path="chroma_db/", settings=Settings(anonymized_telemetry=False))
ENDPOINT = os.getenv("ENDPOINT")
OPENAI_API_VERSION = os.getenv("OPENAI_API_VERSION")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")

embedding_function = AzureOpenAIEmbeddings(deployment="langchain-splitting-test1", api_key=AZURE_OPENAI_API_KEY,
                                           azure_endpoint=ENDPOINT)

splitters = {"semantic": SemanticChunker(embeddings=embedding_function, breakpoint_threshold_type="interquartile",
                                         breakpoint_threshold_amount=1.5),
             "recursive": RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=600)}

for key, splitter in splitters.items():
    split_doc = splitter.split_documents(documents)
    logger.info(f"Splitted documents for {key} into {len(split_doc)} splits")

    db = Chroma.from_documents(documents, embedding=embedding_function, persist_directory="./chroma_db", collection_name=key)

    logger.info(f"{key} split ingestion completed in {time.perf_counter() - start :.2f} seconds")
