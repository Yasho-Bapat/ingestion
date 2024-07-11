import os
import logging
from time import perf_counter, time
from concurrent.futures import ThreadPoolExecutor, as_completed

import chromadb
from langchain_chroma import Chroma
from langchain_openai import AzureChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.callbacks import get_openai_callback
from langchain_openai.embeddings import AzureOpenAIEmbeddings
from langchain_experimental.text_splitter import SemanticChunker
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.utils.function_calling import convert_to_openai_function
from langchain_core.output_parsers.openai_functions import JsonOutputFunctionsParser

from constants import Constants
from utils.file_mapper import file_mapper
from utils.dict_reorderer import reorder_keys
from models import Identification, ToxicologicalInfo, MaterialComposition


class DocumentProcessor:
    def __init__(self, documents_directory: str, persist_directory: str, log_file: str, chunking_method: str):
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(filename=log_file, level=logging.INFO)

        # Initialize Experiment Constants
        self.constants = Constants

        # Initialize AzureOpenAIEmbeddings and AzureChatOpenAI
        self.embedding_function = AzureOpenAIEmbeddings(deployment=self.constants.embedding_deployment, api_key=self.constants.azure_openai_api_key, azure_endpoint=self.constants.endpoint)
        self.llm = AzureChatOpenAI(deployment_name=self.constants.llm_deployment, api_key=self.constants.azure_openai_api_key, azure_endpoint=self.constants.endpoint)

        # Initialize Documents Directory
        self.documents_directory = documents_directory

        # Initialize Chroma
        self.db = None  # init later
        self.persist_directory = persist_directory
        self.chunking_method = chunking_method
        self.persistent_client = chromadb.PersistentClient(path=persist_directory)
        self.collections = [collection.name for collection in self.persistent_client.list_collections()]

        # Set up text splitters
        self.splitters = {
            "semantic": SemanticChunker(embeddings=self.embedding_function, breakpoint_threshold_type=self.constants.breakpoint_threshold_type, breakpoint_threshold_amount=self.constants.breakpoint_threshold_amount),
            "recursive": RecursiveCharacterTextSplitter(chunk_size=self.constants.chunk_size, chunk_overlap=self.constants.chunk_overlap)
        }

        # Convert Pydantic models to OpenAI-compatible functions
        self.id_function = [convert_to_openai_function(Identification)]
        self.toxicological_function = [convert_to_openai_function(ToxicologicalInfo)]
        self.material_composition_function = [convert_to_openai_function(MaterialComposition)]

        # Bind models to language models
        self.id_model = self.llm.bind_functions(functions=self.id_function, function_call={"name": "Identification"})
        self.toxicological_model = self.llm.bind_functions(functions=self.toxicological_function, function_call={"name": "ToxicologicalInfo"})
        self.material_composition_model = self.llm.bind_functions(functions=self.material_composition_function, function_call={"name": "MaterialComposition"})

        # Set up prompt
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self.constants.template),
            ("human", self.constants.human_query)
        ])

        # Set up parser
        self.parser = JsonOutputFunctionsParser()

        # Set up sections to extract
        self.sections = [
            ("identification", self.prompt | self.id_model | self.parser, self.constants.identification_prompt),
            ("material_composition", self.prompt | self.material_composition_model | self.parser,
             self.constants.chemical_composition_prompt),
            ("toxicological_information", self.prompt | self.toxicological_model | self.parser,
             self.constants.toxicological_info_prompt),
        ]

    def parse_and_store(self, filename, collection_name):
        """

        :param filename: name of the file being processed
        :param collection_name: name of the collection where chunks of the document will be stored
        :return: None

        This method extracts the text in the given document, performs chunking based on the selected chunking strategy
        (recursive/semantic) and then stores those chunks in Chroma's vector database.
        """
        # update current collections list
        self.collections = [collection.name for collection in self.persistent_client.list_collections()]

        start = perf_counter()

        # if the collection corresponding to this document already exists, skip chunking and storing
        if collection_name in self.collections:
            self.logger.info(f"Collection: {collection_name} for Document: {filename} already exists. Completed in {perf_counter() - start :.2f} seconds. Skipping Ingestion...")
            print(f"File already exists: {filename} in collection: {collection_name}, skipping...")
            self.db = Chroma(embedding_function=self.embedding_function, persist_directory=self.persist_directory, collection_name=collection_name)
        else:
            print(f"Ingesting File: {filename}")
            documents = []

            # Load Documents
            loader = PyPDFLoader(file_path=f"{self.documents_directory}/{filename}")
            document = loader.load()  # extract text from document using PyPDF
            self.logger.info(f"Loaded {filename}")
            documents.extend(document)

            # call splitter (recursive or semantic, both as given default by Langchain)
            split_doc = self.splitters[self.chunking_method].split_documents(documents)

            self.logger.info(f"Splitted documents for {self.chunking_method} into {len(split_doc)} splits")

            print(f"collection name: {collection_name}")
            print(self.persist_directory, f"{collection_name}")

            # update db with new collection
            self.db = Chroma.from_documents(documents=documents, embedding=self.embedding_function, persist_directory=self.persist_directory, collection_name=f"{collection_name}")

            self.logger.info(f"{self.chunking_method} split ingestion of {filename}(collection name - {collection_name}) completed in {perf_counter() - start :.2f} seconds")

    def process_query(self, chain, query):
        """

        :param chain: the chain that will be executed
        :param query: query to be submitted to LLM
        :return: result, total cost, total tokens used

        This is the function that each thread will be running.
        This method involves retrieving the relevant chunks, and sending it to the LLM as context along with
        the actual query.
        """
        # retrieve relevant documents based on query by performing similarity search
        docs = self.db.similarity_search(query)
        doc_contents = [doc.page_content for doc in docs]

        # using openai callbacks for tracking tokens and cost
        with get_openai_callback() as cb:
            # run the chain
            result = chain.invoke({"docs": doc_contents, "query": query, "example": self.constants.example})
            return result, cb.total_cost, cb.total_tokens

    def run(self, document_name):
        """

        :param document_name: Name of document to be processed
        :return: final JSON output

        This method calls other methods defined above and executes the whole program as threads. Each thread runs the
        process_query method.

        """
        filename = file_mapper(document_name)

        # adding contents of document to database
        self.parse_and_store(filename=document_name, collection_name=f"{self.chunking_method}_{filename}")

        results = dict()
        results["document_name"] = document_name
        total_cost = int()
        total_tokens = int()

        self.logger.info("Extracting information...")
        with ThreadPoolExecutor() as executor:
            # create a dictionary of Future objects with the name as its key
            future_to_query = {executor.submit(self.process_query, chain, section): name for name, chain, section in self.sections}
            self.logger.info("Task submitted successfully.")
            for future in as_completed(future_to_query):  # iterate over objects as the threads complete their execution
                name = future_to_query[future]  # find the correct object using name
                try:
                    result, cost, tokens = future.result()  # return values of self.process_query (it returns a 3-tuple of (result, cost, tokens)
                    results[name] = result
                    total_tokens += tokens
                    total_cost += cost
                    self.logger.info(f"{name} processed successfully.")
                except Exception as e:
                    self.logger.error(f"Error processing {name}: {e}")
        results["total_cost"] = total_cost
        results["total_tokens"] = total_tokens
        return reorder_keys(results)

