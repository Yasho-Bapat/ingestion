from utils.file_mapper import file_mapper
import os
import json
import logging
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
from example import example
from langchain_chroma import Chroma
from langchain_openai.embeddings import AzureOpenAIEmbeddings
from langchain_openai import AzureChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain_community.callbacks import get_openai_callback
from langchain_core.utils.function_calling import convert_to_openai_function

from outputs import Identification, ToxicologicalInfo, MaterialComposition

load_dotenv()


class DocumentProcessor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(filename="retrieval.log", level=logging.INFO)

        # Initialize AzureOpenAIEmbeddings and AzureChatOpenAI
        self.embedding_function = AzureOpenAIEmbeddings(deployment=os.getenv("EMBEDDING_DEPLOYMENT"))
        self.llm = AzureChatOpenAI(deployment_name=os.getenv("LLM_DEPLOYMENT"))


        self.db = None # init is later
        # Convert Pydantic models to OpenAI-compatible functions
        self.id_function = [convert_to_openai_function(Identification)]
        self.toxicological_function = [convert_to_openai_function(ToxicologicalInfo)]
        self.materialcomposition_function = [convert_to_openai_function(MaterialComposition)]

        # Bind models to language models
        self.id_model = self.llm.bind_functions(functions=self.id_function, function_call={"name": "Identification"})
        self.toxicological_model = self.llm.bind_functions(functions=self.toxicological_function, function_call={"name": "ToxicologicalInfo"})
        self.materialcomposition_model = self.llm.bind_functions(functions=self.materialcomposition_function, function_call={"name": "MaterialComposition"})

        # Define a chat prompt template
        # self.template = """
        # You will be given selected chunks from a safety datasheet of a material. Your job is to find whatever is
        # requested by the user. Use only information from the context given to generate answers.
        # If identification information is not available in the document, mention as "No Data".
        # For fields other than material_info, if there is no information about a field, then you may use external knowledge to
        # generate an appropriate answer for that field.
        # Return the answer in JSON format.
        # Example output: {example}
        # """

        # self.template = """
        # Persona: You are a knowledgeable material scientist and chemistry expert specializing in extracting and analysing information of chemicals and materials.
        #
        # Context: You will be given selected chunks from a safety datasheet of a material. Your job is to find
        # whatever is requested by the user. Use only information from the context given to generate answers. For fields other than
        # material_info, if there is no information about fields named 'details', then you may use external knowledge to generate an
        # appropriate answer for that field. Return the answer in JSON format.
        #
        # Input: Chunks from Material Safety Data Sheets along with a query.
        #
        # Task: Extract the requested information from the provided safety datasheet chunks.
        #
        # Guidelines:
        # Use only information from the given context to generate answers.
        # For fields other than material_info, if there is no information about fields named 'details', then use external knowledge to generate an appropriate answer.
        # Return the answer in JSON format.
        #
        # Example output: {example}
        # """

        self.template = """

        Context: You will receive selected chunks from a safety datasheet of a material. Your task is to find the requested information based solely on the provided context. Use the following guidelines:
        
        1. Information Extraction:
           - For material_info, use only the given context to generate answers.
           - For chemical_level_toxicity, if specific information for that chemical is not available in the document provided, look up information about that chemical and generate an appropriate answer.
           - For fields related to toxicity, if information is not available in the context, answer the query by referring to external knowledge.
        
        2. Format:
           - Return the answer in JSON format.
        
        Expected Output:{example}
        
        Note: Ensure accuracy and conciseness in the extracted information.
        """

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self.template),
            ("human", "context: {docs}, query: {query}")
        ])

        self.parser = JsonOutputFunctionsParser()

    @staticmethod
    def reorder_keys(results):
        order = [
            "document_name",
            "identification",
            "material_composition",
            "toxicological_information",
            "total_tokens",
            "total_cost"
        ]
        ordered_results = {key: results[key] for key in order if key in results}
        return ordered_results

    @staticmethod
    def rerank_documents(self, documents, query):
        results = self.reranking_model.rerank(query=query, documents=documents, top_n=5, model="rerank-multilingual-v2.0")
        final_results = []
        for r in results:
            final_results.append(documents[r.index])
        return final_results

    def process_query(self, chain, query):
        docs = self.db.similarity_search(query)
        doc_contents = [doc.page_content for doc in docs]

        with get_openai_callback() as cb:
            result = chain.invoke({"docs": doc_contents, "query": query, "example": example})
            return result, cb.total_cost, cb.total_tokens

    def run(self, document_name):
        filename = file_mapper(document_name)
        self.db = Chroma(persist_directory="./test_chroma_db", collection_name=f"semantic_{filename}", embedding_function=self.embedding_function)
        queries = [
            ("identification", self.prompt | self.id_model | self.parser, "Return material identification information and last date of revision."
                                                                          "Check section 1 and 16."),
            ("material_composition", self.prompt | self.materialcomposition_model | self.parser, "Return the chemical composition of the material provided."
                                                                                                 "Check section 3 or 2."),
            ("toxicological_information", self.prompt | self.toxicological_model | self.parser, "Return toxicological information."
                                                                                    "Check section 11. "),
        ]

        results = dict()
        results["document_name"] = document_name
        total_cost = int()
        total_tokens = int()

        with ThreadPoolExecutor() as executor:
            future_to_query = {executor.submit(self.process_query, chain, query): name for name, chain, query in queries}
            self.logger.info("Task submitted successfully.")
            for future in as_completed(future_to_query):
                name = future_to_query[future]
                try:
                    result, cost, tokens = future.result()
                    results[name] = result
                    total_tokens += tokens
                    total_cost += cost
                    self.logger.info(f"{name} processed successfully.")
                except Exception as e:
                    self.logger.error(f"Error processing {name}: {e}")
        results["total_cost"] = total_cost
        results["total_tokens"] = total_tokens
        return self.reorder_keys(results)

    def store_results(self, results):
        filename = "json_dump/test_from_excel(wrong_ones_that_had_missing_chemicals).json"
        try:
            with open(filename, 'r') as file:
                data = json.load(file)
            self.logger.info("Cumulative result stored successfully in cumulative_result.json")
        except FileNotFoundError as fnf:
            self.logger.info(f"{fnf}; CREATING NEW FILE")
            data = []
        data.append(results)

        try:
            with open(filename, 'w') as file:
                json.dump(data, file, indent=4)
            self.logger.info("Stored results successfully.")
            return "Stored results successfully."
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            return f"Unexpected error occured: {e}"


if __name__ == "__main__":
    processor = DocumentProcessor()
    directory_path = "test_docs"
    files = os.listdir(directory_path)
    files = [f for f in files if os.path.isfile(os.path.join(directory_path, f))]

    for file in files:
        if file == "5.1 11001-5 SDS.pdf":
            print(f"Processing {file}...")
            processor.logger.info(f"Submitting {file} for processing...")
            results = processor.run(file)
            store_results = processor.store_results(results)
            print(store_results)
